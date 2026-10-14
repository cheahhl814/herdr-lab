---
name: herdr-lab-brainstorm
description: 'herdr-lab brainstorming mode — bidirectional multi-agent critique rounds over herdr panes, not a one-shot opinion poll. R0 independent draft (orchestrator writes its own first, anti-anchoring), R1 anonymized cross-critique relay (positions shuffled, verbatim seat-written fields, no tallies), R2 decision round only if disagreement remains (rank / vote / evidence-check by sub-mode), synthesis with a Dissent section. Anti-sycophancy countermeasures built in (seat isolation, RELAY FIDELITY self-check, CHANGED: yes must cite a named verified argument, orchestrator never votes). Use when the user wants to brainstorm, debate, cross-examine / stress-test a design, get a devil''s advocate or a second opinion with critique, or have agents argue it out and converge. References herdr-lab-delegation''s sections (§N) for topology, verification, recovery, ledger, and task-tier seating.'
version: 0.24.0
updated: "2026-10-14"
triggers:
  - brainstorm / debate / get a second opinion *with critique* together with other agents (bidirectional critique rounds, not a one-shot opinion poll)
  - cross-examine / stress-test / poke holes in my design or plan using another agent
  - play devil's advocate against my approach
  - get multiple agents to converge on / vote on a design decision
  - which approach is better — have the agents argue it out
  - ask another agent, then let them respond to each other's critiques (multi-agent discussion, critique rounds)
requires:
  - herdr-lab-delegation conventions available (reads its §1-§5 for topology, verification, recovery, ledger, seat tiers)
---

# herdr-lab brainstorming (herdr-lab workflow §6)

## Multi-agent brainstorming protocol

Use when the user asks to brainstorm, debate, or get a second opinion *with critique* — not a one-shot opinion poll (that is plain delegation; see herdr-lab-delegation §1). You (the orchestrator) are both a **participant** and the **only channel** between seats; seats never see each other's panes. That isolation is the anti-sycophancy mechanism (arXiv 2502.19130: agents converge on the first answer they see; staged no-direct-communication visibility is the measured countermeasure) — never break it by pasting raw transcripts across seats.

Setup: seats per delegation §4.6 (a brainstorm is T3 read-only unless the question needs T2; prefer a distinct harness/provider per seat — same-model seats share blind spots); topology per delegation §1 step 1 (no worktrees — advisory agents, see delegation §1's isolation note); one delegation §1.6 ledger row per seat. State the anchor question, the sub-mode (table below), the seat lineup, and the round cap in one line before R0. Artifacts per round go to `<ledger-dir>/<batch>/r<N>-<seat>.md` (the orchestrator writes them; seats stay read-only).

1. **R0 — Independent draft.** Write YOUR draft to `r0-self.md` BEFORE reading any seat — you are a participant, and the first answer you read becomes your anchor. Batch-dispatch the anchor question + response contract to all seats (delegation §1 step 4). Wait for every seat; verify each against the contract (delegation §2). Save each response as `r0-<seat>.md`.
2. **R1 — Cross-critique (anonymized relay).** Build the relay from what seats wrote, copied as written: anchor question verbatim; positions P1..Pn shuffled and unattributed (yours included); settled points in one line; per contested point the seats' own best arguments as written. You only strip names, shuffle, and group — never pick or paraphrase a "strongest" argument. No vote counts, no confidence levels, no quotes (visible majority triggers conformity; verbatim style leaks authorship). Each seat's response also carries `RELAY FIDELITY: ok | misrepresented — <what>`; if a seat flags misrepresentation, re-send its corrected field before using the relay. Ask each seat to attack the strongest opposing point, then answer in the contract. Read responses with herdr-convo `read --cursor` (delegation §2).
3. **Stop or decide.** Stop when the disagreement map is empty, or every `CHANGED: yes` names a verified argument and positions converged, or the split is values-only (more rounds won't help). Verify every cited argument exists in the relay file you sent (one grep); treat a fabricated citation exactly like an unnamed one — discount the change, keep the seat's prior position as its vote. Otherwise run **R2 as a decision round** per the table (rank or vote, no new arguments). Never an R3 without the user's OK — add a seat instead of a round.
4. **Synthesis.** Report: the decision (or ranked ideas), the margin, the strongest losing argument, and a **Dissent** section. Never present an outvoted position as agreed. Close seat tabs (delegation §1 hygiene); mark ledger rows `done`.

**Response contract** (every round, every seat — prompt content, not tool parameters):

```
POSITION: <one sentence>
RECOMMENDATION: <what to do>
TOP-3 RISKS: 1. 2. 3.
CONTRARIAN TAKE: <the best argument against your own position>
CHANGED: no | yes — because <named argument from the relay>
RELAY FIDELITY: ok | misrepresented — <what>
CONFIDENCE: low | medium | high
EVIDENCE: <file:line, command output, citation — or "reasoning only">
```

| Sub-mode | Task signal | R2 protocol | Output |
| --- | --- | --- | --- |
| **Divergent** (ideation) | open-ended, many valid answers | No convergence: each seat ranks the pooled deduplicated ideas top-3 (Borda) | Union of ideas, ranked; dissent column is where the novelty lives |
| **Convergent / reasoning** (design choice, tradeoffs) | judgment call | Plurality vote with ≥3 active seats, ranked tiebreak; **2 seats → stop after R1, user breaks the tie** | Winner + margin + strongest losing argument |
| **Convergent / factual** ("does X support Y") | checkable answer | Evidence-checked consensus: orchestrator verifies each EVIDENCE line (reads the file, runs the command); no counting | Verified answer; unverifiable claims flagged |
| **Synthesis** ("draft/combine") | user wants a doc, not a pick | Orchestrator merges; each position gets a traceable section | Doc + Dissent section |

**Round barrier & blocked seats.** A round is a barrier: never relay before every seat has settled AND passed the contract check. A blocked seat gets one delegation §3 recovery attempt plus a fixed window after the last healthy seat settles (default 5 min); then mark it `excluded-r<N>` in the ledger — its R0 position still appears under Dissent labelled "not critiqued", but it does not vote. Fewer than 2 active seats → ask the user: re-dispatch, continue one-on-one, or abort.

**Decision rule:** the orchestrator never votes (it both debates and would tally), voting requires ≥3 active seats, and the orchestrator states the sub-mode at R0 so the protocol isn't picked after the fact to suit the result.

**Anti-patterns:**

- NEVER read a seat before committing your own R0 draft — the first answer you read becomes the anchor.
- NEVER relay verbatim excerpts, authorship, harness names, or tallies between seats.
- NEVER choose or paraphrase which argument to relay — copy seat-written fields as written; that choice is how orchestrator bias enters the relay.
- NEVER add rounds to force agreement — forced extra rounds lower accuracy; scale seats instead (per delegation §4.6 gate).
- NEVER use approval voting (it mostly ends with no decision) — ranked or plurality voting, or evidence-checked consensus.
- NEVER let the question change mid-brainstorm — restate it verbatim in every relay; a new scope means a new brainstorm.
- NEVER relay a partial round — every seat settles and passes the contract check first (round barrier above).
- NEVER accept `CHANGED: yes` without a verified named argument — that is how sycophancy shows up.

Drift rule: if any section above starts restating tool parameters or capabilities, delete that section.
