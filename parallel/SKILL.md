---
name: herdr-lab-parallel
description: Parallel subagents for the Herdr editions — fan one task out to N independent seats (2-5) running the same shape of work at once, behind one barrier, then merge and verify. For mechanical fan-out (renames, migrations, per-file review, batched search/analysis), not for critique rounds (that is herdr-lab-brainstorm) or heterogeneous deep tasks (that is herdr-lab-delegation). Picks per-seat tier and thinking effort, enforces the independence preconditions and the shared-quota math, uses the lean seat templates where seats are read-only. Use when the user asks to "run N agents in parallel", "fan out", "parallel subagents/seats/workers", or to batch independent subtasks across seats. Edition-aware (old herdr CLI and Herdr desktop).
version: 0.32.0
updated: "2026-11-17"
triggers:
  - parallel subagents / parallel seats / parallel workers
  - fan out this task across agents
  - batch of independent subtasks across agents
  - run these checks/searches/edits in parallel
requires:
  - herdr-lab-delegation conventions available (reads its §1-§5 for seats, waiting, verification, recovery, fleet sizing)
  - either herdr >= 0.8.0 with HERDR_ENV=1 (CLI), or the Herdr desktop app (HC_TERMINAL_ID set)
disable-model-invocation: true
---

# herdr-lab parallel subagents

> **Edition guard.** Edition-independent protocol. On the old `herdr` TUI CLI, seats and waits work exactly as in `delegation/SKILL.md`; on the Herdr desktop app, follow `desktop/SKILL.md` §1 for launch (`hc run --bg`), the visible-by-default rule, and `hc` wait/read. Read the one matching your session: `HC_TERMINAL_ID` set → desktop; `HERDR_ENV=1` + `HERDR_PANE_ID` → CLI.

Fan **one task** out to **N seats that all do the same kind of work** — a batch of independent subtasks — behind a single barrier, then merge. This is the middle mode: `delegation` gives each seat a *different* deep task, `brainstorm` makes seats *critique each other*; parallel does neither. Seats never see each other's output.

## When to use — and when not to

All four must hold:

1. **Independence** — no seat needs another seat's output or the same files. Shared files → partition by directory, or give each writing seat a worktree (delegation §1), or don't parallelize.
2. **Uniform shape** — subtasks are the same kind of work (same tooling, same verification). If one needs a different harness, that's delegation, not parallel.
3. **Independently verifiable** — each subtask has its own acceptance check you will run before merging.
4. **Failure-isolated** — one seat's failure doesn't invalidate the others' work.

Not for: shared-mutable-state tasks, sequential pipelines, critique/decision tasks (brainstorm), or one hard problem (delegation, one strong seat).

## Fleet sizing and model/effort per seat

Hard cap **5 seats** (delegation §4.7.2) — beyond that the user must explicitly ask. Same harness family across seats (batch rule, §4.7.3); spread is for brainstorms, not fan-out. Pick per seat, not per fleet:

| Seat role | Tier (§4.6) | Model class | Effort / thinking |
|:----------|:-------------|:------------|:------------------|
| Mechanical bulk (renames, lint/format sweeps, boilerplate) | T0 | small / flash / local Ollama | off or low |
| Standard subtask (feature slice, test per module, per-file review) | T1 | flash / workhorse (harness default) | low–medium |
| Read-only verify/search/summarize | T3 | small / flash | low |
| **Synthesis / merge (exactly 1, optional)** | T2 | strongest available | medium–high — the only seat worth real effort |

Equivalent per-role guidance lives in delegation §4.7.4 (effort follows tier) and brainstorm (effort on the synthesis/verdict, not the jurors).

Notes:

- **Thinking effort does little for T0/T1 seats** — input tokens dominate cost; measured on a flash-class local model, thinking saved ~40–110 output tokens per call. Spend effort on the merge seat or nowhere.
- **Input dominates.** Each seat re-pays the fixed prompt (system + tools + AGENTS/CLAUDE.md). That is what the lean seat templates eliminate; see "Lean seats" below.
- **Shared account, shared quota.** N seats on one provider burn that window N times over. `:cloud` Ollama is plan-capped (Pro/Team ≈ 3–8 concurrent; free ≈ 1); local Ollama serializes on VRAM. Size the fleet to the cap *before* picking models, and never sum quota across harnesses.
- **Discovery is per-machine** (§4.6 step 2): never copy model names from docs or this file; probe, then match by property (cheap+fast for T0/T1).

## Launch

Per edition; on the desktop these are §1 of `desktop/SKILL.md` with extra discipline:

1. **Fleet plan line first** (delegation §4.7.7), one line per seat: role, tier, harness, model, subtask, acceptance check. No plan → no seats.
2. Name seats `<batch-slug>-<n>-<harness>` (ledger join key).
3. **Launch all seats before waiting on any.** Barrier comes after launch, never interleaved.
4. Every unattended seat gets an approval posture that cannot stall it (delegation §4.5; desktop: desktop §1 step 3) — a batch that idles on a permission prompt wastes the whole barrier. Prefer read-only-by-construction seats where the subtask allows.
5. On the desktop, seats are visible by default (`hc label … herdr.space=…`) — keep them visible; the user is watching their machine, not a batch log.
6. Register every seat in the ledger (`bin/herdr-batch.py`, §1.6): tier, harness, model. The ledger, not context, is the source of truth — resume after compaction via `hc ls` + ledger.

**Lean seats.** If a subtask is read-only (review, search, summarize, verify), launch it from a lean template instead of a full harness: `hc run --bg --name <slug>-<n> <template> "<scope>"` with templates from `desktop/templates/` (pi-lean, claude-lean, codex-lean, gemini-lean, copilot-lean, opencode-lean, agy-lean — lean tier; the `-heavy` heavy tier for T1/T2 subtasks). Lean seats skip skill/extension/MCP injection, which is most of a seat's fixed cost, and cannot edit anything — the correct failure mode for a fan-out seat gone wrong.

## Barrier, verify, merge

1. One barrier for the whole batch: `hc wait --children all` (desktop) / per-seat waits (CLI). A 180 s timeout is a check-in, not a failure; wait again.
2. Read every seat (`hc read <t>` / delegation §2). **`done` is not completion** — match the explicit completion signal and the per-subtask acceptance check from the fleet plan.
3. Merge in the subtask order from the plan. Conflicts mean the independence test failed — stop and report; do not improvise a merge policy for the user.
4. Only after merge: aggregate report — per-subtask verdict, evidence, skipped/failed seats, and anything you did not verify.

## Failure handling

- A seat stalls or blocks: one recovery attempt (desktop §2 / delegation §3) or one re-dispatch with a narrower scope. Still stuck → mark that subtask **unfinished** and continue the merge of the rest.
- Never silently drop a seat. The final report lists every planned subtask as done / unfinished.
- ≥⅓ of seats failing the same way means the decomposition was wrong, not the seats — stop, summarize, re-plan with the user.
- A seat that strays out of scope: interrupt, salvage what is usable, report the rest.

## Anti-patterns

- N copies of one vague prompt ("look at the repo") — that's a brainstorm without the protocol, or delegation without a task.
- Parallelizing before the per-seat subtasks are written down; "we'll see" is not a subtask.
- Homogeneous-strong fleets (max effort everywhere) — cost and latency scale with seats; effort belongs on the merge seat.
- Treating peer review as a substitute for the merge step.
- Skipping the ledger because "it's only three seats".

## See also

- `delegation/SKILL.md` §1 (seats), §2 (verification), §3 (recovery), §4.5–§4.7 (flags, tiers, fleet), §1.6 (ledger)
- `desktop/SKILL.md` (desktop edition mechanics) and `desktop/templates/` (lean seats)
- `brainstorm/SKILL.md` (when the seats should argue instead of work)
