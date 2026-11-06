#!/usr/bin/env python3
"""Self-check for herdr-induct.py: python3 bin/test_herdr_induct.py"""
import importlib.util
import os
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("induct", os.path.join(here, "herdr-induct.py"))
induct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(induct)

# Scrub: escapes and identity go; a word merely containing the user stays.
out = induct.scrub("\x1b[90m/home/ann/x\x1b[0m ann@box joanne", "/home/ann", "ann", "box")
assert out == "$HOME/x $USER@$HOSTNAME joanne", out

assert induct.harness_output("/no/such/exe", "--help", 5) is None

with tempfile.TemporaryDirectory() as tmp:
    stub = os.path.join(tmp, "stub")
    for body, expected in (("exit 0", None),  # empty output is a failure
                           ("echo hi; exit 1", None),
                           ("echo hi", "hi")):
        with open(stub, "w") as fh:
            fh.write(f"#!/bin/sh\n{body}\n")
        os.chmod(stub, 0o755)
        assert induct.harness_output(stub, "--help", 5) == expected, body

    args =("demo", "demo", "1.2.3", "usage: demo", "current (v1)", tmp)
    help_path, card_path, new_card = induct.write_capture(*args, "2026-01-01")
    assert new_card
    assert induct.previous_version(help_path) == "1.2.3"

    with open(card_path, "a") as fh:
        fh.write("hand edit\n")
    _, _, new_card = induct.write_capture(*args, "2026-01-02")
    assert not new_card
    with open(card_path) as fh:
        assert "hand edit" in fh.read()  # a re-run never overwrites a card

    legacy = os.path.join(tmp, "legacy.md")
    with open(legacy, "w") as fh:
        fh.write("# Verbatim capture — 2026-09-02 — do not edit; regenerate: x\n")
    assert induct.previous_version(legacy) is None
print("ok")
