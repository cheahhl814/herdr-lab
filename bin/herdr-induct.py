#!/usr/bin/env python3
"""herdr-induct.py — capture step of the herdr-lab induction sub-skill.

Writes, for one installed harness:

  docs-corpus/harnesses/help-<kind>.md   verbatim --help, scrubbed, stamped
  docs-corpus/harnesses/<kind>-card.md   card skeleton (never overwritten)

Refuses a kind that herdr cannot start or that is not on PATH. It never
installs anything. `--version` and `--help` are the only harness calls it
makes, with stdin closed, so the no-headless rule (delegation §1) holds.

Usage: python3 bin/herdr-induct.py <kind> [--timeout 20]

Standard library only. Python >= 3.8.
"""

import argparse
import datetime
import getpass
import importlib.util
import os
import re
import socket
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
HARNESS_DIR = os.path.join(os.path.dirname(HERE), "docs-corpus", "harnesses")
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
# Allowlist, not denylist: a credential can have any name (DATABASE_URL).
SAFE_ENV_RE = re.compile(r"(PATH|HOME|USER|LOGNAME|SHELL|TERM|TMPDIR|LANG|LC_[A-Z]+)")
# CLIs built on clap print live values as `[env: NAME=value]` in --help. A value
# can contain `]`, so everything to the end of the line goes.
ENV_HINT_RE = re.compile(r"\[env:\s*([A-Za-z_][A-Za-z0-9_]*)=.*$", re.M)
# Greedy to the last `@`: a password can contain `@` or `/`. Over-redacting is safe.
URL_USERINFO_RE = re.compile(r"(://)\S*@")
TOKEN_RE = re.compile(
    r"\bsk-[A-Za-z0-9_-]{16,}|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}"
    r"|\bAKIA[0-9A-Z]{16}\b|\bAIza[0-9A-Za-z_-]{30,}|(?i:\bbearer\s+[A-Za-z0-9._-]{20,})")

_spec = importlib.util.spec_from_file_location(
    "herdr_capabilities", os.path.join(HERE, "herdr-capabilities.py"))
caps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(caps)

CARD = """# {kind} — harness card

Written by the herdr-lab induction sub-skill. `TODO` means not yet established.

| Field | Value |
|:------|:------|
| Kind / executable | `{kind}` / `{exe}` |
| Version captured | {version} ({date}) |
| herdr integration | {integration} |
| Live test | not run |
| List models | TODO |
| Model flag | TODO |
| Permission: intermediate | TODO |
| Permission: full auto | TODO |
| Permission: read-only | TODO |
| Quota surface | TODO |
| Login check | TODO |
| Transcript reader (herdr-convo) | TODO |
| Online docs source | TODO |

## Open questions

- TODO
"""


def scrub(text, home=None, user=None, host=None):
    """Remove terminal escapes, secrets and machine identity from captured output."""
    home = home or os.path.expanduser("~")
    user = user or getpass.getuser()
    hosts = {host} if host else {socket.gethostname(), socket.getfqdn()}
    text = ANSI_RE.sub("", text)
    text = ENV_HINT_RE.sub(r"[env: \1=<redacted>]", text)
    text = URL_USERINFO_RE.sub(r"\1<redacted>@", text)
    text = TOKEN_RE.sub("<redacted>", text).replace(home, "$HOME")
    text = re.sub(rf"\b{re.escape(user)}\b", "$USER", text, flags=re.I)
    # Longest first, so an FQDN isn't left half-replaced by its short name.
    for name in sorted(hosts - {"", "localhost"}, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(name)}\b", "$HOSTNAME", text, flags=re.I)
    return text


def safe_env():
    """Only the variables a CLI needs to print its help."""
    return {k: v for k, v in os.environ.items() if SAFE_ENV_RE.fullmatch(k)}


def harness_output(exe, flag, timeout):
    """Run `exe flag` with stdin closed and an allowlisted environment.

    Returns stdout, or None on failure. stderr is used only when stdout is
    empty: logs and warnings don't belong in a published file, but some CLIs
    (opencode) print --help there.
    """
    try:
        proc = subprocess.run(
            [exe, flag], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=safe_env(), timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (proc.stdout or proc.stderr).decode("utf-8", "replace").strip()
    return text if proc.returncode == 0 and text else None


def previous_version(help_path):
    """Version stamped in an existing capture, or None (e.g. older format)."""
    if not os.path.exists(help_path):
        return None
    with open(help_path, encoding="utf-8") as fh:
        match = re.search(r"— version: (.+?) —", fh.readline())
    return match.group(1) if match else None


def write_capture(kind, exe, version, help_text, integration, harness_dir, today):
    """Write the help capture and a missing card. Returns (help, card, new_card)."""
    os.makedirs(harness_dir, exist_ok=True)
    help_path = os.path.join(harness_dir, f"help-{kind}.md")
    card_path = os.path.join(harness_dir, f"{kind}-card.md")
    with open(help_path, "w", encoding="utf-8") as fh:
        fh.write(f"# Verbatim capture — {today} — version: {version} — "
                 f"do not edit; regenerate: python3 bin/herdr-induct.py {kind}\n")
        fh.write(help_text + "\n")
    new_card = not os.path.exists(card_path)
    if new_card:
        with open(card_path, "w", encoding="utf-8") as fh:
            fh.write(CARD.format(kind=kind, exe=exe, version=version, date=today,
                                 integration=integration))
    return help_path, card_path, new_card


def main():
    parser = argparse.ArgumentParser(description="Capture one harness for induction.")
    parser.add_argument("kind", help="herdr agent kind, e.g. opencode")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    kinds, err = caps.live_kinds(args.timeout)
    if err:
        print(f"error: cannot read herdr kinds: {err}", file=sys.stderr)
        return 2
    if args.kind not in kinds:
        print(f"refused: herdr cannot start kind '{args.kind}'", file=sys.stderr)
        return 1
    path, exe = caps.find_executable(args.kind)
    if not path:
        print(f"refused: '{args.kind}' is not installed; install it first",
              file=sys.stderr)
        return 1

    help_text = harness_output(exe, "--help", args.timeout)
    if help_text is None:
        print(f"error: `{exe} --help` failed", file=sys.stderr)
        return 1
    raw_version = harness_output(exe, "--version", args.timeout)
    version = scrub(raw_version).splitlines()[0] if raw_version else "unknown"

    integ, _ = caps.integration_status(args.timeout)
    names = [args.kind] + [a for a, t in caps.INTEGRATION_ALIASES.items() if t == args.kind]
    integration = next((integ[n]["status"] for n in names if n in integ), "none listed")

    previous = previous_version(os.path.join(HARNESS_DIR, f"help-{args.kind}.md"))
    today = datetime.date.today().isoformat()
    help_path, card_path, new_card = write_capture(
        args.kind, exe, version, scrub(help_text), integration, HARNESS_DIR, today)

    print(f"version: {version} (previous capture: {previous or 'not stamped'})")
    print(f"integration: {integration}")
    print(f"help: {help_path}")
    print(f"card: {card_path} ({'new skeleton' if new_card else 'kept, update by hand'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
