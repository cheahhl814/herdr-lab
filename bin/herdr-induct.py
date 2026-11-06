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
    """Remove terminal escapes and machine identity from captured output."""
    home = home or os.path.expanduser("~")
    user = user or getpass.getuser()
    host = host or socket.gethostname()
    text = ANSI_RE.sub("", text).replace(home, "$HOME")
    text = re.sub(rf"\b{re.escape(user)}\b", "$USER", text)
    return re.sub(rf"\b{re.escape(host)}\b", "$HOSTNAME", text)


def harness_output(exe, flag, timeout):
    """Run `exe flag` with stdin closed. Returns text, or None on failure."""
    try:
        proc = subprocess.run(
            [exe, flag], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = proc.stdout.decode("utf-8", "replace").strip()
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
