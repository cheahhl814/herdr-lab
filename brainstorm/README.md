# herdr-lab-brainstorm

**Skill name**: `herdr-lab-brainstorm` · **Version**: 0.26.0 · **Type**: agent skill (workflow-only)

The brainstorming mode of the [herdr-lab](https://github.com/cheahhl814/herdr-lab) family: bidirectional multi-agent critique rounds over [herdr](https://github.com/ogulcancelik/herdr) panes — not a one-shot opinion poll. Agents take independent positions, critique each other's arguments in an anonymized relay, and the group converges on a decision with the losing argument preserved.

> This is a **sub-skill**. It has its own frontmatter, its own trigger set, and can be symlinked on its own — it does not need the `herdr-lab` router to be loaded. The router is a thin dispatcher; the workflow lives here.

**Workflow-only** — `herdr_layout` / `herdr_pane` / `herdr_agent` tool schemas are the source of truth for parameters. This skill orders calls, defines the round protocol, and lists anti-patterns; it never restates tool parameters and never invents a CLI flag that is not captured in `docs-corpus/`.

## When it fires

Triggers (from the SKILL.md frontmatter):

```text
- brainstorm / debate / get a second opinion *with critique* together with other agents
- cross-examine / stress-test / poke holes in my design or plan using another agent
- play devil's advocate against my approach
- get multiple agents to converge on / vote on a design decision
- which approach is better — have the agents argue it out
- ask another agent, then let them respond to each other's critiques
```

Plain "ask another agent X" with **no** exchange signal is *not* this skill — that is a one-shot delegation in [`herdr-lab-delegation`](../delegation/README.md) §1. A critique, exchange, or convergence signal is the tell.

## What it covers

| Part | Topic |
|:-----|:------|
| **Setup** | Fleet composition per delegation §4.7: seat count, harness spread, model per seat — all read from the **local probe**, because the corpus describes other machines. |
| **R0** | Independent draft. The orchestrator writes its own draft *before* reading any seat — you are a participant, and the first answer you read becomes your anchor. |
| **R1** | Cross-critique via an anonymized relay: positions shuffled and unattributed, seat-written fields copied verbatim, no quotes, no tallies, no confidence levels. |
| **R2** | Decision round — only if disagreement remains; rank or vote, no new arguments. Never an R3 without the user's OK. |
| **Synthesis** | Decision + margin + strongest losing argument + a **Dissent** section. An outvoted position is never presented as agreed. |
| **Response contract** | The fixed per-seat response fields every round, every seat. |
| **Sub-modes** | Divergent / convergent-reasoning / convergent-factual / synthesis — each with its seat range, R2 protocol, and output shape. |
| **Round barrier** | Never relay before every seat has settled and passed the contract check; blocked seats get one recovery attempt, then are excluded and labelled. |
| **Anti-patterns** | The anti-sycophancy rules (see below). |

## Anti-sycophancy design

The failure mode is agents converging on the first answer they see (arXiv 2502.19130). The countermeasures are structural, not advisory:

- **Seat isolation** — seats never see each other's panes; the orchestrator is the only channel.
- **You are a participant** — your own R0 draft is written first, so you cannot anchor on a seat.
- **The orchestrator never votes** — it both debates and would tally.
- **Verbatim relay** — you strip names and shuffle; you never pick, paraphrase, or rank a "strongest" argument.
- **No quotes, no tallies** — visible majorities trigger conformity; verbatim style leaks authorship.
- **`CHANGED: yes` must name a verified argument** — an unnamed or fabricated citation is discounted and the seat keeps its prior position.
- **Dissent is mandatory** — the strongest losing argument is reported, not dropped.

## The fleet probe — knowing what this machine has

Seat lineup needs harnesses and models that exist *here*. The docs-corpus says what a harness supports; it is a snapshot of another machine's CLIs. The probe answers availability locally:

```bash
python3 bin/herdr-capabilities.py              # fleet table
python3 bin/herdr-capabilities.py --json       # machine-readable
```

Two rules that depend on it: seats must sit on **distinct harnesses and distinct model families** (same-model seats share blind spots), and **the orchestrator's own model family counts as a seat's** — you write the R0 draft, so three seats that all match you are one prior sampled three times.

## Install

```bash
git clone https://github.com/cheahhl814/herdr-lab.git
mkdir -p ~/.pi/agent/skills
# keep the symlink name == the skill's frontmatter name
ln -sf "$(pwd)/herdr-lab/brainstorm" ~/.pi/agent/skills/herdr-lab-brainstorm
```

If your harness reads `~/.agents/skills/` instead, symlink there instead — same link, same name. The router (`herdr-lab`) and the sibling (`herdr-lab-delegation`) are separate links; each works alone.

**Requires**: `herdr >= 0.8.0`, the `pi-herdr` plugin installed and active (`HERDR_PANE_ID` set), `HERDR_ENV=1`, and the `herdr-lab-delegation` conventions (this protocol reads "delegation §N" for topology, verification, recovery, the ledger, and seat tiers).

## Layout

```text
brainstorm/
├── SKILL.md             # this sub-skill — the whole protocol
├── docs-corpus -> ../docs-corpus   # shared: herdr CLI + 7 harness captures
└── bin -> ../bin                   # shared: herdr-batch.py, herdr-capabilities.py
```

`docs-corpus/` and `bin/` live once at the repo root; the relative symlinks keep every path inside this file resolving whether the sub-skill is loaded through the router or symlinked standalone.

## Hard guarantees

- **Workflow-only, no tool redefinition** — tool parameters are never restated here; a drift rule at the bottom of SKILL.md deletes any section that starts doing so.
- **Orchestrator never votes** — a decision needs ≥3 active seats and a stated sub-mode from R0.
- **Rounds are barriers** — no partial relay, no forced extra rounds.
- **Dissent is reported** — synthesis always names the strongest losing argument.
- **The ledger is the source of truth** — seat state, round, and exclusion survive context compaction.

## License

MIT — see [LICENSE](../LICENSE). Upstream: <https://github.com/cheahhl814/herdr-lab>.
