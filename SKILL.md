---
name: herdr-lab
description: 'Router for the herdr-lab workflow family. Use when the user mentions Herdr, asks to delegate to another coding agent, run parallel agents / batches, run sudo or another privileged/secret-entry command safely in a managed pane, check another agent''s quota/usage, or brainstorm/debate with other agents (bidirectional critique rounds, devil''s advocate, second opinion). Reads the intent and routes to the matching sub-skill: delegation/SKILL.md (herdr-lab-delegation) or brainstorm/SKILL.md (herdr-lab-brainstorm). Each sub-skill carries its own frontmatter and is independently symlinkable; docs-corpus and bin are shared at the herdr-lab root and reached via per-sub-skill relative symlinks.'
version: 0.24.1
updated: "2026-10-28"
triggers:
  - user mentions Herdr by name
requires:
  - herdr >= 0.8.0
  - pi-herdr plugin installed and active (HERDR_PANE_ID set)
  - HERDR_ENV=1
---

# herdr-lab — router (master)

This file routes; it does not perform. The workflow is split into two independently triggerable sub-skills, each with its own frontmatter and trigger set (matching versions 0.24.1 across master + sub-skills):

| User intent | Sub-skill | What it covers |
| --- | --- | --- |
| "delegate this to claude / codex / opencode", "run these agents in parallel", "batch of N agents", "which model should I use", "check another agent's quota/usage", "run sudo in a managed pane" | `delegation/SKILL.md` — **herdr-lab-delegation** | §1 delegation sequence (topology → dispatch → prompt → verify), §1.5 worktree merge-back, §1.6 batch ledger (`bin/herdr-batch.py`), §2 verification & completion rules, §3 interrupt/error recovery, §4 model discovery + quota pre-flight, §4.5 permission modes, §4.6 provider preflight + task tiers (T0-T3), §5 privileged / secret-entry command pattern |
| "brainstorm with other agents", "debate these two designs", "devil's advocate against my approach", "cross-examine / stress-test my plan", "have the agents argue it out and converge", "second opinion *with critique*" | `brainstorm/SKILL.md` — **herdr-lab-brainstorm** | R0 independent draft → R1 anonymized cross-critique relay → R2 decision round (only if disagreement remains) → synthesis with a Dissent section; response contract, sub-mode table (divergent / convergent / synthesis), round barrier & blocked-seat handling, anti-sycophancy rules |

## Dispatch rules

1. **Read exactly one sub-skill — the one the intent maps to.** The table above is the mapping. Do not read both, and never inline either sub-skill's content back into this router.
2. **One-shot question vs. critique exchange.** "Ask another agent what X" with no exchange signal is **plain delegation** (`delegation/SKILL.md` §1). A critique / exchange / "have them respond to each other" signal is **brainstorming** (`brainstorm/SKILL.md`). Plain "ask another agent" is never an excuse to run the full R0→R1→R2 protocol.
3. **Brainstorm also needs delegation.** `brainstorm/SKILL.md` references "delegation §N" for topology (§1), verification (§2), recovery (§3), the ledger (§1.6), and seat tiers (§4.6) — so when the brainstorm sub-skill is selected, read `delegation/SKILL.md` as its reference companion. Delegation alone needs no second file.
4. **Bare "use herdr" / "delegate this"** → `delegation/SKILL.md`. The delegation sequence is the core path; brainstorm is the opt-in elaboration.
5. **Mixed request ("brainstorm, then have the best one implement it")** → run the brainstorm round first (it ends in a decision + Dissent), then run the delegation sequence for the implementation. Do not collapse them into one session of agents.
6. **Shared assets live once at the root.** `docs-corpus/` (offline `--help` captures + online docs for herdr and 7 harnesses) and `bin/herdr-batch.py` live at the herdr-lab root and are reached from each sub-skill directory through the relative symlinks `docs-corpus -> ../docs-corpus` and `bin -> ../bin`. Paths therefore resolve identically whether a sub-skill is loaded through this router or symlinked standalone.
7. **Standalone use.** Both sub-skills carry their own frontmatter, so either can be symlinked on its own (`herdr-lab-delegation`, `herdr-lab-brainstorm`) and will trigger without this router.
8. **Tool schemas are the source of truth.** This skill never restates `herdr_layout` / `herdr_pane` / `herdr_agent` parameters, and never invents a herdr CLI flag that is not captured in `docs-corpus/`. Anything the sub-skill asks for that the corpus does not document must be checked against the live `--help` output, not guessed.

## Versioning

The master router and both sub-skills share one version number (currently 0.24.1). Bump all three together whenever the family changes, and keep `README.md` in sync with the same release.
