---
name: herdr-lab
description: 'Router for the herdr-lab workflow family. Use when the user mentions Herdr, asks to delegate to another coding agent, run parallel agents / batches, run sudo or another privileged/secret-entry command safely in a managed pane, check another agent''s quota/usage, or brainstorm/debate with other agents (bidirectional critique rounds, devil''s advocate, second opinion). Also use to introduce or refresh a harness. Reads the intent and routes to the matching sub-skill: delegation/SKILL.md (herdr-lab-delegation), brainstorm/SKILL.md (herdr-lab-brainstorm), induction/SKILL.md (herdr-lab-induction), desktop/SKILL.md (herdr-lab-desktop: Herdr desktop app via hc + herdr-app), or desktop-mods/SKILL.md (herdr-lab-desktop-mods: customize the desktop window). Each sub-skill carries its own frontmatter and is independently symlinkable; docs-corpus and bin are shared at the herdr-lab root and reached via per-sub-skill relative symlinks.'
version: 0.29.1
updated: "2026-11-09"
triggers:
  - user mentions Herdr by name
requires:
  - either the old CLI edition (herdr >= 0.8.0, pi-herdr plugin, HERDR_ENV=1, HERDR_PANE_ID set) or the desktop edition (hc >= 0.1.18, herdr-app >= 0.1.13, HC_TERMINAL_SOCKET set)
---

# herdr-lab — router (master)

This file routes; it does not perform. The workflow is split into five independently triggerable sub-skills, each with its own frontmatter and trigger set:

| User intent | Sub-skill | What it covers |
| --- | --- | --- |
| "delegate this to claude / codex / opencode", "run these agents in parallel", "batch of N agents", "which model should I use", "how many agents should I run", "check another agent's quota/usage", "run sudo in a managed pane" | `delegation/SKILL.md` — **herdr-lab-delegation** | §1 delegation sequence (topology → dispatch → prompt → verify), §1.5 worktree merge-back, §1.6 batch ledger (`bin/herdr-batch.py`), §2 verification & completion rules, §3 interrupt/error recovery, §4 model discovery + quota pre-flight, §4.5 permission modes, §4.6 provider preflight + task tiers (T0-T3), §4.7 fleet composition (how many harnesses, which harness per seat, which model per seat), §5 privileged / secret-entry command pattern |
| "brainstorm with other agents", "debate these two designs", "devil's advocate against my approach", "cross-examine / stress-test my plan", "have the agents argue it out and converge", "second opinion *with critique*" | `brainstorm/SKILL.md` — **herdr-lab-brainstorm** | R0 independent draft → R1 anonymized cross-critique relay → R2 decision round (only if disagreement remains) → synthesis with a Dissent section; response contract, sub-mode table (divergent / convergent / synthesis), round barrier & blocked-seat handling, anti-sycophancy rules |
| "introduce / onboard this harness", "add a new harness", "refresh the docs-corpus for codex", "does this harness work through herdr" | `induction/SKILL.md` — **herdr-lab-induction** | Capture `--help` + version, ingest official docs, fill a harness card, prove it with one live interactive seat |
| "delegate / run agents in parallel / sudo" **in the Herdr desktop app** (`HC_TERMINAL_ID` set, `hc` + `herdr-app`) | `desktop/SKILL.md` — **herdr-lab-desktop** | edition detection, CLI→desktop command map, `hc` delegation sequence, batch wait, recovery, sudo pattern, ledger mapping, brainstorm/induction transport |
| "customize / restyle the Herdr app", "write or install a herdr-app mod or layout", "port usagebar to the desktop" | `desktop-mods/SKILL.md` — **herdr-lab-desktop-mods** | clone-before-edit, `check` → `status` → `shot` loop, community layout/mod install rules, porting CLI plugins to mods |

## Dispatch rules

1. **Read exactly one sub-skill — the one the intent maps to.** The table above is the mapping. Do not read both, and never inline either sub-skill's content back into this router. When the request involves *how many* agents to run or *which* models they should use, that decision lives in the delegation sub-skill §4.7 (fleet composition) — not in this router, and not in the sub-skill's §4.6 (which covers a single seat).
2. **One-shot question vs. critique exchange.** "Ask another agent what X" with no exchange signal is **plain delegation** (`delegation/SKILL.md` §1). A critique / exchange / "have them respond to each other" signal is **brainstorming** (`brainstorm/SKILL.md`). Plain "ask another agent" is never an excuse to run the full R0→R1→R2 protocol.
3. **Brainstorm also needs delegation.** `brainstorm/SKILL.md` references "delegation §N" for topology (§1), verification (§2), recovery (§3), the ledger (§1.6), and seat tiers (§4.6) — so when the brainstorm sub-skill is selected, read `delegation/SKILL.md` as its reference companion. The induction sub-skill's live test needs the same companion. Delegation alone needs no second file.
4. **Bare "use herdr" / "delegate this"** → `delegation/SKILL.md`. The delegation sequence is the core path; brainstorm is the opt-in elaboration.
5. **Mixed request ("brainstorm, then have the best one implement it")** → run the brainstorm round first (it ends in a decision + Dissent), then run the delegation sequence for the implementation. Do not collapse them into one session of agents.
6. **Shared assets live once at the root.** `docs-corpus/` (offline `--help` captures + online docs for herdr and 7 harnesses) and `bin/herdr-batch.py` live at the herdr-lab root and are reached from each sub-skill directory through the relative symlinks `docs-corpus -> ../docs-corpus` and `bin -> ../bin`. Paths therefore resolve identically whether a sub-skill is loaded through this router or symlinked standalone.
7. **Standalone use.** All five sub-skills carry their own frontmatter, so each can be symlinked on its own (`herdr-lab-delegation`, `herdr-lab-brainstorm`, `herdr-lab-induction`) and will trigger without this router.
8. **Tool schemas are the source of truth.** This skill never restates `herdr_layout` / `herdr_pane` / `herdr_agent` parameters, and never invents a herdr CLI flag that is not captured in `docs-corpus/`. Anything the sub-skill asks for that the corpus does not document must be checked against the live `--help` output, not guessed.
9. **Availability is machine-local, and only a probe knows it.** The docs-corpus says what a harness *supports*; it is a snapshot of another machine's CLIs, not an inventory of this one. When the request depends on which harnesses or models exist, the delegation sub-skill runs its local probe (`bin/herdr-capabilities.py`, §4.6 step 2) on the machine it is running on — never a remembered list, never another box's corpus capture.
10. **Edition first.** Two Herdr generations can be installed side by side and share nothing but `~/.config/herdr`: the old `herdr` TUI CLI (`HERDR_ENV=1`, `HERDR_PANE_ID`) and the desktop app (`HC_TERMINAL_ID`, programs `hc` and `herdr-app`). Check `env | grep -E '^(HC_TERMINAL_ID|HERDR_ENV|HERDR_PANE_ID)='` before routing. Old CLI → `delegation/`; desktop → `desktop/`. Brainstorm and induction are edition-independent in protocol; on desktop read them together with `desktop/SKILL.md` §5 for the transport. Never give `herdr agent/pane ...` commands to the desktop or `hc ...` to the old CLI.

## Versioning

The master router and all five sub-skills share one version number (currently 0.29.1). Bump all six together whenever the family changes, and keep `README.md` in sync with the same release.
