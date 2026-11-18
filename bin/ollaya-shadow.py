#!/usr/bin/env python3
"""ollaya-shadow.py — shadow-mode decision-model tier+effort suggestions for herdr-lab delegations.

Option (b) of the ollaya-decisions plan: NEVER route. For each row of a
herdr-batch.py ledger it asks the local Ollaya daemon (TypeSafe /v1/systemone
wire format, port 11435, default model laya:en) TWO typed questions about the
seat's task — which §4.6 task tier it fits AND which per-seat thinking/effort
level (§4.7.4) to run the seat at — and records the suggestions in a sidecar
file `<ledger>.shadow.json`, next to the real `tier` the orchestrating agent
actually chose. `report` later prints agreement/divergence.

Division of labour (deliberate, see ollaya-shadow decision-model policy):
  ollaya (decision model)  -> suggested_tier, suggested_effort  (its own calls)
  §4.7.4 table             -> fallback ONLY, when the daemon is unreachable
  the skill's §4.6/§4.7    -> harness, seat model, quota, family diversity
                              (the decision model never picks a harness or a
                              model string — availability probes stay with §4.6)

Fallback: on machines without ollaya, `suggest` does not hard-fail. It writes
`effort_source: "table-fallback"` entries derived from the row's actual
`tier` by the documented §4.7.4 table (T0 off–low, T1 low–medium, T2
medium–high, T3 low) so delegation effort guidance still works offline. Pass
`--no-fallback` to make an unreachable daemon an error instead.

Why shadow: the measured verdict in the wiki (decision-model-no-home-rule,
2026-10-28) is that inline delegation routing is a downgrade — volume is
1–5 seats per session and the orchestrating LLM is free and better. The
sidecar accumulates labelled data instead: after enough batches, compare
`suggested_tier` against the human/LLM `tier` before ever letting the
decision model influence a real launch.

Standard library only. Python >= 3.8.

Subcommands:
  suggest  LEDGER [--agent NAME] [--base URL] [--model ID] [--dry-run]
                  [--no-fallback]
           ask ollaya tier+effort per row (skips rows already suggested or
           rows without a task); writes <ledger>.shadow.json
  report   LEDGER
           print suggestion vs actual tier + effort-source table
  show     LEDGER
           print the raw sidecar

Examples:
  python3 bin/ollaya-shadow.py suggest .herdr-batch/batch-x.json
  python3 bin/ollaya-shadow.py report .herdr-batch/batch-x.json
"""

import argparse
import datetime
import json
import pathlib
import sys
import urllib.request

TIERS = ("T0", "T1", "T2", "T3")
EFFORT_LEVELS = ("off", "low", "medium", "high")

# §4.6 table criteria, verbatim task shapes (the decision model needs the
# same labels the skill uses so agreement/divergence measures the right
# boundary).
TIER_QUESTION = {
    "type": "choice",
    "instructions": (
        "Which herdr task tier does the task in `task` fit? "
        "T0 = trivial/bulk (lint fixes, mechanical renames, batch small edits); "
        "T1 = standard dev (single/few-file features, bugfixes, tests); "
        "T2 = heavy agentic (multi-file refactor, cross-cutting changes, long planning); "
        "T3 = read-only/review (code review, analysis, research, quota probes)."
    ),
    "criteria": {
        "T0": "Trivial or bulk work: lint fixes, mechanical renames, batch small edits",
        "T1": "Standard development: single or few-file features, bugfixes, tests",
        "T2": "Heavy agentic work: multi-file refactor, cross-cutting changes, long planning",
        "T3": "Read-only work: code review, analysis, research, quota probes",
    },
}

# §4.7.4: "Effort / thinking follows the tier, not habit" and "Never `max`
# across a fleet". The decision model picks one level; `off` suits T0 bulk
# work where input dominates, `high` only pays where a planning failure
# costs a re-dispatch.
EFFORT_QUESTION = {
    "type": "choice",
    "instructions": (
        "Which per-seat thinking/effort level should a delegated coding agent run at for the task in `task`? "
        "The seat is one herdr pane in a batch; never pick `max`."
    ),
    "criteria": {
        "off": "Trivial or bulk work where input dominates; thinking tokens are ~noise",
        "low": "Standard single-file work or read-only reviews",
        "medium": "Standard dev work where some planning helps (features, tests)",
        "high": "Heavy agentic work where a planning failure costs a re-dispatch (multi-file refactor, cross-cutting changes)",
    },
}

EFFORT_BY_TIER_FALLBACK = {  # §4.7.4 table, used ONLY when ollaya is unreachable
    "T0": "off-low",
    "T1": "low-medium",
    "T2": "medium-high",
    "T3": "low",
}

MODEL = "laya:en"
BASE = "http://127.0.0.1:11435"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_ledger(path: pathlib.Path) -> dict:
    try:
        with path.open() as fh:
            data = json.load(fh)
    except FileNotFoundError:
        sys.exit(f"error: ledger not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: corrupt ledger {path}: {exc}")
    if "rows" not in data or not isinstance(data["rows"], dict):
        sys.exit(f"error: {path} is not a herdr-batch ledger (missing 'rows')")
    return data


def _sidecar_path(ledger: pathlib.Path) -> pathlib.Path:
    return ledger.with_name(ledger.stem + ".shadow.json")


def _load_sidecar(ledger: pathlib.Path) -> dict:
    path = _sidecar_path(ledger)
    if path.exists():
        try:
            with path.open() as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            sys.exit(f"error: corrupt sidecar {path}: {exc}")
    return {"ledger": str(ledger), "rows": {}}


def _save_sidecar(ledger: pathlib.Path, sidecar: dict) -> None:
    path = _sidecar_path(ledger)
    sidecar["updated"] = _now()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def ask_tier_effort(task: str, base: str, model: str) -> dict:
    """One /v1/systemone call with both questions. Returns {error: ...} on any failure."""
    body = json.dumps(
        {
            "model": model,
            "state": {"task": task},
            "questions": {"tier": TIER_QUESTION, "effort": EFFORT_QUESTION},
        }
    ).encode()
    request = urllib.request.Request(
        f"{base.rstrip('/')}/v1/systemone",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except Exception as exc:  # noqa: BLE001 — report every failure as data
        return {"error": f"ollaya request failed: {exc}"}
    if not isinstance(payload, dict) or "answers" not in payload:
        return {"error": f"unexpected response: {json.dumps(payload)[:200]}"}
    return payload


def record_from_answer(answer: dict, field: str, vocabulary: tuple, out: dict, label: str) -> None:
    """Copy a typed choice answer into the record if the label is in vocabulary."""
    probs = answer.get("probabilities", {}) if answer.get("type") == "choice" else {}
    choice = answer.get("choice")
    if choice in vocabulary:
        out.update({field: choice, f"{field}_confidence": answer.get("confidence")})
        if label == "tier":
            out["probabilities"] = probs
    else:
        out[f"{field}_error"] = f"answer out of vocabulary: {choice!r}"


def suggest_row(name: str, row: dict, args) -> dict:
    """Build one sidecar record; never raises."""
    record = {"task": row["task"], "asked_at": _now(), "actual_tier": row.get("tier", "")}
    payload = ask_tier_effort(row["task"], args.base, args.model)
    if "error" in payload:
        if args.no_fallback:
            record["error"] = payload["error"]
            return record
        # Fallback path (§4.7.4 table): effort derived from the ACTUAL tier.
        # No decision-model suggestions are recorded.
        actual = row.get("tier", "")
        if actual in TIERS:
            record["effort_source"] = "table-fallback"
            record["suggested_effort"] = EFFORT_BY_TIER_FALLBACK[actual]
            record["note"] = f"ollaya unavailable ({payload['error'][:120]})"
        else:
            record["error"] = payload["error"]
            record["note"] = "fallback needs the row's actual `tier` set; none found"
        return record

    record["effort_source"] = "model"
    for field, label, vocab in (
        ("suggested_tier", "tier", TIERS),
        ("suggested_effort", "effort", EFFORT_LEVELS),
    ):
        record_from_answer(payload["answers"].get(label, {}), field, vocab, record, label)
    return record


def cmd_suggest(args) -> None:
    ledger_path = pathlib.Path(args.ledger).expanduser()
    ledger = _load_ledger(ledger_path)
    sidecar = _load_sidecar(ledger_path)
    sidecar["model"] = args.model
    sidecar["base"] = args.base

    names = [args.agent] if args.agent else sorted(ledger["rows"])
    pending = [
        name
        for name in names
        if name in ledger["rows"]
        and name not in sidecar["rows"]
        and ledger["rows"][name].get("task")
    ]
    if not pending:
        print("nothing to suggest (no unsuggested rows with a task)")
        return

    errors = 0
    for name in pending:
        row = ledger["rows"][name]
        record = suggest_row(name, row, args)
        sidecar["rows"][name] = record
        if args.dry_run:
            print(f"[dry-run] {name}: {json.dumps(record, sort_keys=True)[:240]}")
            continue
        if record.get("error"):
            errors += 1
            print(f"{name}: ERROR {record['error'][:120]}")
        elif record["effort_source"] == "table-fallback":
            print(f"{name}: effort={record.get('suggested_effort', '?')} "
                  f"[table-fallback from tier {row.get('tier', '?')}] (ollaya unavailable)")
        else:
            print(
                f"{name}: tier={record.get('suggested_tier', '?')} "
                f"(conf={record.get('suggested_tier_confidence', '?')}) "
                f"effort={record.get('suggested_effort', '?')} "
                f"(conf={record.get('suggested_effort_confidence', '?')}) "
                f"actual={row.get('tier', '?') or '(not set yet)'}"
            )

    if args.dry_run:
        return
    _save_sidecar(ledger_path, sidecar)
    print(f"sidecar: {_sidecar_path(ledger_path)}")
    if errors:
        print(f"warning: {errors} row(s) failed — check the ollaya daemon (systemctl status ollaya)", file=sys.stderr)


def cmd_report(args) -> None:
    ledger_path = pathlib.Path(args.ledger).expanduser()
    ledger = _load_ledger(ledger_path)
    sidecar_path = _sidecar_path(ledger_path)
    if not sidecar_path.exists():
        sys.exit(f"error: no sidecar yet: {sidecar_path} (run `suggest` first)")
    with sidecar_path.open() as fh:
        sidecar = json.load(fh)

    headers = ("agent", "actual", "suggested", "match", "tier_conf", "effort", "effort_src", "note")
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join([" --- "] * len(headers)) + "|")
    scored = 0
    matches = 0
    errors = 0
    for name in sorted(sidecar["rows"]):
        record = sidecar["rows"][name]
        actual = ledger.get("rows", {}).get(name, {}).get("tier", "")
        suggested = record.get("suggested_tier", "")
        if record.get("error"):
            match = "—"
            note = f"error: {record['error']}"
            errors += 1
        elif not actual:
            match = "?"
            note = "actual tier not set yet"
        elif not suggested:
            # table-fallback row: effort guidance only, no tier opinion to score
            match = "?"
            note = "table-fallback row (no tier suggestion)"
        else:
            is_match = actual == suggested
            match = "=" if is_match else "≠"
            note = "" if is_match else "DIVERGES"
            scored += 1
            matches += 1 if is_match else 0
        print(
            "| "
            + " | ".join(
                [
                    name,
                    actual or "—",
                    suggested or "—",
                    match,
                    _fmt(record.get("suggested_tier_confidence")),
                    record.get("suggested_effort", ""),
                    record.get("effort_source", ""),
                    note,
                ]
            )
            + " |"
        )
    print(
        f"\nsidecar: {sidecar_path} · model {sidecar.get('model', MODEL)} · "
        f"scored {scored} row(s): agreement {matches}/{scored}"
        + (f" · {errors} error row(s)" if errors else " · 0 errors"),
        file=sys.stderr,
    )


def _fmt(value) -> str:
    return "" if value is None else str(value)


def cmd_show(args) -> None:
    sidecar_path = pathlib.Path(args.ledger).expanduser()
    sidecar_path = _sidecar_path(sidecar_path)
    if not sidecar_path.exists():
        sys.exit(f"error: no sidecar: {sidecar_path}")
    print(sidecar_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("suggest", help="ask ollaya for a tier + effort per ledger row")
    p.add_argument("ledger")
    p.add_argument("--agent", help="only this row (default: every unsuggested row with a task)")
    p.add_argument("--base", default=BASE)
    p.add_argument("--model", default=MODEL)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-fallback", action="store_true",
                   help="an unreachable daemon is an error instead of the §4.7.4 table fallback")
    p.set_defaults(func=cmd_suggest)

    p = sub.add_parser("report", help="suggestion vs actual tier agreement")
    p.add_argument("ledger")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("show", help="raw sidecar JSON")
    p.add_argument("ledger")
    p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
