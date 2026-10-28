#!/usr/bin/env python3
"""herdr-capabilities.py — machine-local fleet probe for herdr-lab §4.6 / §4.7.

The skill's docs-corpus says what a harness *supports*. It cannot say what
*this* machine has installed, authenticated, and model-equipped. This probe
answers that question locally, so the seat-count and model decisions in §4.7
are made against reality instead of against another box's documentation.

Four signals, in order:

  1. herdr agent start --help   -> the LIVE kind enum (what herdr can start
                                   here). Never hardcoded: the enum drifts
                                   (0.8.0 = 21 kinds, 0.9.0 = 23).
  2. herdr integration status   -> per-agent integration hook state
                                   (current / outdated / not installed).
                                   "not installed" = screen-manifest detection
                                   only, i.e. the §4.7.3 flake risk.
  3. command -v <executable>    -> what is actually installed on PATH.
  4. per-harness model listing  -> what models each installed harness can
                                   use (pi --list-models, opencode models,
                                   ollama list). Harnesses with no CLI list
                                   (claude/codex/copilot/agy/gemini) report
                                   their in-TUI probe instead.

Usage:
  python3 bin/herdr-capabilities.py              # human table
  python3 bin/herdr-capabilities.py --json       # machine-readable
  python3 bin/herdr-capabilities.py --no-models  # skip model listing (fast)
  python3 bin/herdr-capabilities.py --timeout 20 # per-command timeout, seconds

Standard library only. Python >= 3.8. Never prints secrets, tokens, or
credential values — only executable paths, hook paths, and model names.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# Canonical executable per herdr kind, with fallback candidates. The kind
# name is usually the executable; these are the observed exceptions.
EXE_CANDIDATES = {
    "qodercli": ["qodercli", "qoder"],
    "agy": ["agy", "antigravity-cli"],
    "kimi": ["kimi", "kimi-code"],
    "droid": ["droid", "factory"],
    "cursor": ["cursor", "cursor-agent"],
    "muse": ["muse"],
}

# herdr integration status uses its own names; map them back to kinds.
INTEGRATION_ALIASES = {
    "antigravity-cli": "agy",
    "qoder": "qodercli",
}

# How to list models per harness. `cmd` is run as a subprocess; `parse` shapes
# the output. `None` means the harness has no CLI model list — the model is
# chosen in-TUI, so the probe reports the in-TUI command to use instead.
MODEL_SOURCES = {
    "pi": {
        "cmd": ["pi", "--list-models"],
        "mode": "table",
        "note": "provider-qualified; `--provider` + `--model` at launch",
    },
    "opencode": {
        "cmd": ["opencode", "models"],
        "mode": "lines",
        "note": "provider/model lines; `-m <name>` at launch",
    },
}

# Model listing for harnesses whose provider is Ollama (not a harness itself).
OLLAMA_CMD = ["ollama", "list"]

IN_TUI_MODEL_PROBE = {
    "claude": ("/model (choose), /usage or /status (quota)", "in-tui"),
    "codex": ("/model (choose), /status (quota)", "in-tui"),
    "copilot": ("/model (default `auto`)", "in-tui"),
    "agy": ("/usage or /status (quota)", "in-tui"),
    "gemini": ("/model (choose), /usage (quota)", "in-tui"),
    "cursor": ("/model (choose)", "in-tui"),
    "devin": ("/model (choose)", "in-tui"),
    "cline": ("/model (choose)", "in-tui"),
    "omp": ("/model (choose)", "in-tui"),
    "mastracode": ("/model (choose)", "in-tui"),
    "kimi": ("/model (choose)", "in-tui"),
    "kiro": ("/model (choose)", "in-tui"),
    "droid": ("/model (choose)", "in-tui"),
    "amp": ("/model (choose)", "in-tui"),
    "grok": ("/model (choose)", "in-tui"),
    "hermes": ("/model (choose)", "in-tui"),
    "kilo": ("/model (choose)", "in-tui"),
    "qodercli": ("/model (choose)", "in-tui"),
    "qwen": ("/model (choose)", "in-tui"),
    "maki": ("/model (choose)", "in-tui"),
    "muse": ("/model (choose)", "in-tui"),
}

KIND_RE = re.compile(r"\[possible values:\s*([^\]]+)\]")
INTEGRATION_RE = re.compile(r"^(?P<name>[^:]+):\s+(?P<rest>.+)$")
PAREN_RE = re.compile(r"\(([^)]*)\)")
VERSION_RE = re.compile(r"herdr\s+(\S+)")


def run(cmd, timeout):
    """Run a command, returning (ok, stdout, stderr). Never raises."""
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return False, "", "command not found"
    except subprocess.TimeoutExpired:
        return False, "", f"timeout after {timeout}s"
    except OSError as exc:
        return False, "", str(exc)
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    return proc.returncode == 0, out, err


def live_kinds(timeout):
    """The kind enum this herdr binary accepts (never hardcoded)."""
    ok, out, err = run(["herdr", "agent", "start", "--help"], timeout)
    if not ok:
        return [], err.strip()
    match = KIND_RE.search(out)
    if not match:
        return [], "could not parse [possible values] from herdr agent start --help"
    kinds = [k.strip() for k in match.group(1).split(",") if k.strip()]
    return kinds, None


def herdr_version(timeout):
    ok, out, _ = run(["herdr", "--version"], timeout)
    if not ok:
        return None
    match = VERSION_RE.search(out)
    return match.group(1) if match else out.strip().splitlines()[0] if out.strip() else None


def integration_status(timeout):
    """Parse `herdr integration status` into {name: {status, path}}."""
    ok, out, _ = run(["herdr", "integration", "status"], timeout)
    if not ok:
        return {}, "herdr integration status unavailable"
    table = {}
    for line in out.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        match = INTEGRATION_RE.match(line)
        if not match:
            continue
        name = match.group("name").strip()
        rest = match.group("rest").strip()
        parens = PAREN_RE.findall(rest)
        # "pi: current (v8) (/path)" -> status "current", version "v8", path "/path"
        # "agy: not installed (/path)"   -> status "not installed", path "/path"
        version = None
        path = ""
        if parens:
            path = parens[-1].strip()
            if len(parens) > 1:
                version = parens[0].strip()
        status = PAREN_RE.sub("", rest).strip()
        if version:
            status = f"{status} {version.replace(' ', '')}"
        table[name] = {"status": status, "hook_path": path}
    return table, None


def normalize_integration(status_text):
    """Kept for callers that already hold a raw status; identity by design."""
    return status_text.strip()


def find_executable(kind):
    for candidate in EXE_CANDIDATES.get(kind, [kind]):
        path = shutil.which(candidate)
        if path:
            return path, candidate
    return None, None


def parse_pi_models(text):
    models = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for line in lines[1:]:  # drop the header row
        parts = line.split()
        if len(parts) >= 2:
            models.append(f"{parts[0]}:{parts[1]}")
    return models


def parse_lines(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def parse_ollama(text):
    models = []
    for line in parse_lines(text)[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])
    return models


def model_source_for(kind, timeout, with_models):
    """Return (mode, models_or_note, error)."""
    source = MODEL_SOURCES.get(kind)
    if source is None:
        note, mode = IN_TUI_MODEL_PROBE.get(kind, ("/model (choose)", "in-tui"))
        return mode, note, None
    if not with_models:
        return "cli-list", "skipped (--no-models)", None
    ok, out, err = run(source["cmd"], timeout)
    if not ok:
        return "cli-list", None, err.strip() or "listing failed"
    models = parse_pi_models(out) if source["mode"] == "table" else parse_lines(out)
    return "cli-list", models, None


def distinct_families(models):
    """Heuristic family key = leading alpha token of the model name.

    Deliberately coarse: it is a diversity *hint* for §4.7.3, not a taxonomy.
    "gemma4:31b-cloud" -> "gemma"; "tev1:0.8b" -> "tev"; "d3:2b" -> "d".
    """
    keys = set()
    noise = {"latest", "cloud", "free", "preview", "beta", "auto", "default"}
    for model in models:
        name = model.split(":", 1)[-1]
        name = name.split("/")[-1]
        name = name.replace(":cloud", "")
        token = name.split(":")[0].split("-")[0]
        token = re.sub(r"[^A-Za-z].*$", "", token)
        if token and token.lower() not in noise:
            keys.add(token.lower())
    return sorted(keys)


def probe(timeout, with_models):
    report = {
        "herdr_version": herdr_version(timeout),
        "errors": [],
        "harnesses": [],
    }

    kinds, kinds_err = live_kinds(timeout)
    if kinds_err:
        report["errors"].append(f"kind enum: {kinds_err}")
    report["kinds_startable"] = kinds

    integ, integ_err = integration_status(timeout)
    if integ_err:
        report["errors"].append(f"integration status: {integ_err}")

    all_models = []
    for kind in kinds:
        path, exe = find_executable(kind)
        entry = {
            "kind": kind,
            "executable": exe,
            "path": path,
            "installed": bool(path),
            "integration": None,
            "integration_hook": None,
            "model_source": None,
            "models": None,
            "model_note": None,
            "error": None,
        }

        raw = integ.get(kind)
        if raw is None:
            for alias, target in INTEGRATION_ALIASES.items():
                if target == kind and alias in integ:
                    raw = integ[alias]
                    break
        if raw:
            entry["integration"] = normalize_integration(raw["status"])
            entry["integration_hook"] = raw["hook_path"]

        if not entry["installed"]:
            # Not on PATH: no model listing, no in-TUI probe — nothing to say.
            report["harnesses"].append(entry)
            continue

        mode, payload, err = model_source_for(kind, timeout, with_models)
        entry["model_source"] = mode
        if err:
            entry["error"] = err
        elif isinstance(payload, list):
            entry["models"] = payload
            all_models.extend(payload)
        else:
            entry["model_note"] = payload

        report["harnesses"].append(entry)

    report["installed_kinds"] = [h["kind"] for h in report["harnesses"] if h["installed"]]
    report["current_integration_kinds"] = [
        h["kind"] for h in report["harnesses"]
        if (h["integration"] or "").startswith("current")
    ]
    report["outdated_integration_kinds"] = [
        h["kind"] for h in report["harnesses"]
        if (h["integration"] or "").startswith("outdated")
    ]

    ollama_models = []
    if with_models and shutil.which(OLLAMA_CMD[0]):
        ok, out, err = run(OLLAMA_CMD, timeout)
        if ok:
            ollama_models = parse_ollama(out)
        else:
            report["errors"].append(f"ollama list: {err.strip()}")
    report["ollama_models"] = ollama_models

    families = distinct_families(all_models + ollama_models)
    report["distinct_model_families_heuristic"] = families
    report["distinct_model_family_count_heuristic"] = len(families)
    return report


def print_table(report):
    version = report.get("herdr_version") or "unknown"
    print(f"herdr {version} | startable kinds: {len(report.get('kinds_startable', []))}")
    print()
    header = f"{'KIND':<12} {'INSTALLED':<10} {'INTEGRATION':<18} {'MODELS':<10} NOTE"
    print(header)
    print("-" * len(header))
    for h in report["harnesses"]:
        installed = "yes" if h["installed"] else "no"
        integ = h["integration"] or "-"
        if not h["installed"]:
            models = "-"
        elif h["model_source"] == "cli-list" and h["models"] is not None:
            models = f"{len(h['models'])} listed"
        elif h["model_source"] == "cli-list" and (h["model_note"] or "").startswith("skipped"):
            models = "skipped"
        elif h["model_source"] == "cli-list":
            models = "err"
        else:
            models = h["model_source"] or "-"
        note = h["model_note"] or h["error"] or (h["path"] or "")
        if not h["installed"]:
            note = h["integration_hook"] or ""
        print(f"{h['kind']:<12} {installed:<10} {integ:<18} {models:<10} {note}")
    print()
    print(f"installed here: {', '.join(report.get('installed_kinds', [])) or 'none'}")
    print(f"lifecycle integration current: {', '.join(report.get('current_integration_kinds', [])) or 'none'}")
    print(f"lifecycle integration outdated: {', '.join(report.get('outdated_integration_kinds', [])) or 'none'}")
    if report.get("ollama_models"):
        print(f"ollama models: {len(report['ollama_models'])} "
              f"(e.g. {', '.join(report['ollama_models'][:3])})")
    count = report.get("distinct_model_family_count_heuristic", 0)
    print(f"distinct model families (heuristic): {count}")
    if report.get("errors"):
        print()
        print("errors:")
        for err in report["errors"]:
            print(f"  - {err}")


def main():
    parser = argparse.ArgumentParser(
        description="Probe this machine's herdr harness + model fleet (§4.6 / §4.7)."
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--no-models", action="store_true",
                        help="skip per-harness model listing (fast)")
    parser.add_argument("--timeout", type=float, default=20.0,
                        help="per-command timeout in seconds (default 20)")
    args = parser.parse_args()

    if shutil.which("herdr") is None:
        print("error: herdr is not on PATH — this probe needs the herdr CLI",
              file=sys.stderr)
        return 2

    report = probe(args.timeout, not args.no_models)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_table(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
