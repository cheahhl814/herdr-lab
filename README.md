# herdr-lab

[![Version](https://img.shields.io/badge/version-0.24.1-blue)](#installation)
[![Type](https://img.shields.io/badge/type-agent%20skill-blueviolet)](#installation)
[![Built with](https://img.shields.io/badge/built%20with-bioinfo--skill--creator-orange)](https://github.com/cheahhl814/bioinfo-skill-creator)

Use when the user mentions Herdr, asks to delegate to another agent, run parallel agents, brainstorm/debate with other agents (cross-examine a design, devil's advocate, second opinion with critique), run sudo (or another privileged/secret-entry command) safely in a managed pane, or check another agent's quota/usage. **Workflow-only** — tool schemas (`herdr_layout`, `herdr_pane`, `herdr_agent`) are the source of truth for parameters. Complements the [official herdr skill](https://github.com/herdr).

**Repository**: https://github.com/cheahhl814/herdr-lab

> [!NOTE]
> Current version: **v0.24.1** (updated 2026-10-28). The workflow is split into a router master + two independently symlinkable sub-skills: `herdr-lab-delegation` (§1-§5) and `herdr-lab-brainstorm`. See [Changelog](#changelog).

## Contents

- [Why this skill exists](#why-this-skill-exists)
- [Installation](#installation)
- [Workflow phases](#workflow-phases)
- [Repo layout](#repo-layout)
- [Update check](#update-check)
- [Hard guarantees](#hard-guarantees)
- [Changelog](#changelog)
- [Provenance & License](#provenance--license)

## Why this skill exists

The official herdr skill ships `herdr_layout` / `herdr_pane` / `herdr_agent` tools and their parameter schemas. This skill **does not redefine those tools** — it defines the workflow around them: when to split a pane, when to delegate to another agent, how to gate a prompt on completion, how to recover from stalls, and — since v0.15.0 — how to run a bidirectional multi-agent brainstorm (critique rounds, not a one-shot opinion poll).

If you are looking for the tool API, read `docs-corpus/herdr/` (offline captures of the herdr CLI flags and supported agents). If you are looking for *workflow* (the order in which to call those tools, the checkpoints, the failure recoveries), read `SKILL.md`.

## Installation

This is an **agent skill**, not a user-facing library. There is no `pixi.toml` and no `pixi install` step — the skill is pure Markdown + a single Python importer.

**Option A — give your agent this prompt (recommended):**

```text
Install the herdr-lab skill from
https://github.com/cheahhl814/herdr-lab —
clone it into your agent's skills directory (the path your agent watches
for skills). Then read SKILL.md (the router) and the sub-skill SKILL.md
you need (delegation/SKILL.md for §1-§5 delegation, brainstorm/SKILL.md
for bidirectional critique rounds). Confirm when the environment is
ready.
```

**Option B — manual install:**

```bash
git clone https://github.com/cheahhl814/herdr-lab.git
# Symlink into your agent's skills directory. On Pi:
mkdir -p ~/.pi/agent/skills
ln -sf "$(pwd)/herdr-lab" ~/.pi/agent/skills/herdr-lab
# Each sub-skill also runs standalone (own frontmatter).
# Keep the symlink name == the sub-skill's frontmatter name, so the
# directory a skill is discovered under and the skill it declares agree:
ln -sf "$(pwd)/herdr-lab/delegation" ~/.pi/agent/skills/herdr-lab-delegation
ln -sf "$(pwd)/herdr-lab/brainstorm" ~/.pi/agent/skills/herdr-lab-brainstorm
```

> [!TIP]
> If your harness reads `~/.agents/skills/` instead of `~/.pi/agent/skills/`, symlink into that directory instead — same three links, same names. Both the router (`herdr-lab`) and the two sub-skills (`herdr-lab-delegation`, `herdr-lab-brainstorm`) are then discovered independently, and each sub-skill's `docs-corpus` / `bin` symlinks still resolve.

The skill does **not** install any third-party Python packages at install time. The one tool it ships (`bin/herdr-batch.py`, the §1.6 batch ledger) is stdlib-only.

## Workflow phases

The skill is a **router master + two sub-skills**. `SKILL.md` routes; the sub-skills do the work. Each sub-skill has its own frontmatter (name, description, version, triggers) and can be symlinked as a standalone skill.

| Path | Skill name | When it is read |
|:-----|:-----------|:----------------|
| `SKILL.md` | `herdr-lab` | Router: detects intent (delegation vs brainstorming) and routes; fires on bare "use herdr" |
| `delegation/SKILL.md` | `herdr-lab-delegation` | "delegate to claude / codex / opencode / …", "run agents in parallel" — §1 sequence + worktree merge-back + §1.6 batch ledger, §2 verification, §3 recovery, §4/§4.5/§4.6 launch config + tiers, §5 sudo pattern |
| `brainstorm/SKILL.md` | `herdr-lab-brainstorm` | "brainstorm with another agent", "debate these two designs", "devil's advocate", "have the agents argue it out and converge" — R0 draft → R1 anonymized cross-critique → R2 decision round → synthesis + Dissent |

`delegation/SKILL.md` and `brainstorm/SKILL.md` are the same §1-§5 / §6 content that previously lived in the single SKILL.md, with brainstorm's §-references rewritten to "delegation §N" so they resolve in the split files.

> [!TIP]
> Every gated decision in §4-§6 surfaces back to the user via `ask_user_question` (Evidence + Recommend + Options) rather than auto-picking. This mirrors how Claude Code and OpenCode surface their permission prompts.

### Natural-language triggers

Trigger phrases (from SKILL.md `triggers:` frontmatter):

```text
- user mentions Herdr by name
- delegate a task to another coding agent
- run agents in parallel / multiple agents at once
- brainstorm / debate / get a second opinion with critique together with other agents (§6)
- cross-examine / stress-test / poke holes in my design or plan using another agent (§6)
- play devil's advocate against my approach (§6)
- get multiple agents to converge on / vote on a design decision (§6)
- run sudo or another privileged command safely
- check another agent's model/quota/usage
```

The §6 brainstorm trigger family (added in v0.15.0/v0.15.1) routes to the bidirectional brainstorm mode, NOT a one-shot §1 opinion poll (plain "ask another agent X" without a critique/exchange signal still routes to plain §1 delegation).

## Repo layout

```text
herdr-lab/
├── SKILL.md                 # Router master: routes to the two sub-skills below
├── delegation/
│   ├── SKILL.md             # herdr-lab-delegation: §1-§5 (independently symlinkable)
│   ├── docs-corpus -> ../docs-corpus
│   └── bin -> ../bin
├── brainstorm/
│   ├── SKILL.md             # herdr-lab-brainstorm: bidirectional critique rounds (independently symlinkable)
│   ├── docs-corpus -> ../docs-corpus
│   └── bin -> ../bin
├── docs-corpus/             # Shared offline snapshots of herdr CLI + 7 coding-agent harnesses
├── bin/
│   └── herdr-batch.py       # §1.6 batch ledger (new/set/show/todo)
├── LICENSE                  # MIT
└── .gitignore
```

There is intentionally **no** `pixi.toml` / `pixi.lock` / `scaffold-render.py` / `skill-update-check.py`. This skill is pure workflow + one Python CLI; dependency management happens upstream (the agent's runtime).

## Update check

```bash
# From a clone of this repo
git fetch origin
git rev-parse --verify HEAD                    # local HEAD
git rev-parse --verify origin/main             # upstream HEAD
```

| Verdict | Meaning |
|:--------|:--------|
| Match | UP-TO-DATE |
| Local ahead | Unpushed local commits; no action needed |
| Upstream ahead | Behind; consider re-pulling — compare against CHANGELOG below |
| `git fetch` failed | Offline / network issue; informational only |

## Hard guarantees

- **Workflow-only, no tool redefinition** — `SKILL.md` never restates `herdr_layout` / `herdr_pane` / `herdr_agent` parameters; it only orders calls and lists recovery paths. Drift rule at the bottom of SKILL.md enforces this. The router `SKILL.md` and both sub-skills each end with that drift rule.
- **Schema-grounded tool usage** — when the skill recommends a herdr CLI flag, the recommendation is grounded in `docs-corpus/herdr/` captures, not the agent's memory.
- **Push-UIs over poll loops** — every checkpoint that would otherwise need polling uses `ask_user_question` as a blocking gate (one tool call, zero LLM tokens while waiting). Polling loops with `bash sleep` + `herdr_pane read` are explicitly forbidden.
- **Shared assets via symlinks** — `docs-corpus/` and `bin/` live once at the root; per-sub-skill relative symlinks keep every path inside the sub-skill SKILL.mds resolving, whether loaded via the router or as a symlinked standalone skill.

## Changelog

### v0.24.1 (2026-10-28)

**Fixed the router body, which shipped truncated in v0.24.0.** The v0.24.0 commit left `SKILL.md` cut off mid-table (the body ended at the table header `| User intent | Sub-skill | What it covers |` with zero rows), so the router had no routing rows, no dispatch rules, and no drift rule — it could not route. The router body is now complete: the intent → sub-skill mapping table (delegation §1-§5 vs. brainstorm R0→R1→R2), eight dispatch rules (one-shot question vs. critique exchange, "brainstorm also needs delegation" because the brainstorm protocol references "delegation §N", mixed request = brainstorm then delegate, shared-assets location, standalone symlink use, tool-schema-is-source-of-truth), and a shared-versioning note. Frontmatter is unchanged apart from the version bump. Master + both sub-skills now carry version **0.24.1** and `updated: "2026-10-28"`. No workflow text in the sub-skills changed.

### v0.24.0 (2026-10-14)

**Split the two modes into independently symlinkable sub-skills (router + sub-skill layout).** `SKILL.md` became a router; `delegation/SKILL.md` (`herdr-lab-delegation`, §1-§5 delegation core) and `brainstorm/SKILL.md` (`herdr-lab-brainstorm`, bidirectional critique rounds) each carry their own frontmatter, trigger set, and version (0.24.0, matching across master + sub-skills). Brainstorm's §1-§5 references were rewritten as "delegation §N" to resolve across the file split; its section header lost the redundant §6. `docs-corpus/` and `bin/` are shared once at the root and reached via relative symlinks inside each sub-skill directory, so paths resolve identically whether a sub-skill is loaded via the router or symlinked standalone (`ln -sf .../herdr-lab/delegation ~/.pi/agent/skills/herdr-lab-delegation`). No workflow text was changed — pure restructure.

### v0.23.0 (2026-10-14)

**Stripped tutorial (§6 old), quiz (§7), companion (§9), and deck-led course (§10) modes; brainstorming renumbered §8 → §6.** Usage showed delegation (§1–§5) and multi-agent brainstorming as the only heavily used modes; the four teaching/companion modes were removed and brainstorming is now §6. Frontmatter description and triggers trimmed to delegation + brainstorming + sudo + quota; the `html-template-pack` optional dependency is gone; the course/quiz machinery (`course.schema.v1.json`, `quiz.schema.v1.json`, `steps.schema.v1.json`, `bin/quiz-import-pdf.py`, `bin/course-vet.py`, `bin/course-deck.py`) was deleted. §1–§5 delegation/core workflow and the batch ledger are unchanged. Historical changelog entries below describe the removed modes as they shipped at the time.

### v0.22.0 (2026-10-01)

**New §10 deck-led course mode.** Lesson content moves out of agent chat into an HTML slide deck (`lessons/<slug>/deck.html`, built once from [html-template-pack](https://github.com/cheahhl814/html-template-pack)'s slide template, referenced by a `deck:` frontmatter key). Starting a course opens the deck in the browser (`xdg-open` / `open` / `wslview`, or `python3 -m http.server` for SSH) and a practice pane beside it. The student picks a drive: **companion** (self-paced, agent silent until "check task s2" or "help", which runs the `steps.json` evidence check) or **trainer** (§6 gates with ≤5-line pointer cards like "Slide 5 · task s2", since the deck carries the content). Practice slides are tagged `data-step`, show the goal rather than the command (except under `drill`), and keep the hint ladder in native `<details>` rungs so self-paced students can unfold hints without the agent. Concept-only lessons (no shell) work too: they use the deck plus the §7 quiz, with no pane. New `bin/course-deck.py` wraps a lesson's slide fragment in the template (drops the reference slides, sets the title, namespaces annotation storage, adds the hint style, writes the `deck:` key). `course-vet.py` now checks the deck exists, has no leftover template slides, and that each `data-step` resolves to a step (unslided steps are a warning). It also warns when a practice slide shows no `accept[]` form verbatim, because `accept[]` is exact-match: a student who copies the slide's command must pass "check task". Decks are **lecture decks for students with no prior knowledge**: taught from the full course source rather than the lesson summary, starting with why, defining every term on first use, and following explain → worked example with real output → practice for every command, ending with a recap and common mistakes (~15–25 slides). Piloted on lesson 01 of `missing-semester-2026` (25 slides) and `pixi-fundamentals` (21 slides).

### v0.21.0 (2026-09-30)

**New §9 companion mode.** The agent attaches to the user's pane (or opens one), replies with one line, and ends its turn: no gates, no polling, zero tokens while the user works. When the user asks for help, it reads the pane, finds the most recent failure or hang, quotes the error line, investigates read-only in its own shell, and gives a fix for the user to run. It types into the user's pane only when asked (with confirmation for destructive commands), redacts secrets, and on detach closes only panes it created.

### v0.20.1 (2026-09-30)

**Card placement now depends on the host.** v0.19.0 put every lesson card inside the ask-user dialog, but Claude Code (and OpenCode / RPC hosts) trim long `question`/`preview` text, so instructions were cut off. Pi still gets the card inside the dialog, since its dialog scrolls and never trims. On other hosts the card goes in chat right before a compact dialog (a one-line question, no lesson preview), so the dialog covers as little chat as possible.

### v0.20.0 (2026-09-30)

**Pedagogy stances for §6/§7.** The default is now `constructivist`: steps give a goal instead of a command, ask the student to predict before running and to interpret after, use a 4-rung hint ladder (the full command is the last rung), and add a Socratic re-ask plus a confidence rating and a one-line "why" on quiz items. `heutagogy` lets the student set the goal and route, choose the quiz objectives, and ends with a reflection. `heuristagogy` (Dr. Victor L. Berardi's framework: heuristics + heutagogy + AI/LLMs, aimed at "good enough" rather than perfect) teaches problem-solving heuristics, treats the AI as a partner whose answers the student must check against the pane, uses a stopping criterion the student sets, and leaves the student a `heuristics.md` toolkit. `drill` keeps the old command-first behaviour when asked for. The gate mechanics, the evidence check, and the retry cap are unchanged. An optional `pedagogy:` key in `course.yaml` sets a course default.

### v0.19.0 (2026-09-30)

**Dashboard-first rendering for §6 tutorial and §7 quiz.** With the side pane open, the ask-user dialog covered half the chat pane and hid the lesson text printed above it. Lesson cards (previous-step explanation or diagnosis, next instruction, command, what to look for) and quiz feedback now go *inside* the push-UI call: the instruction goes in `question`, and the card is a markdown `preview` repeated on every option, folded into `question` when the host or `multiSelect` has no preview. Chat output before a gate is capped at one line. Also corrected the host table: Claude Code's `AskUserQuestion` does render `preview`.

### v0.18.1 (2026-09-29)

**`quiz-import-pdf.py` now scaffolds hlab-course.v1 natively.** Default layout became `lessons/<slug>/` with full frontmatter (`id`/`module`/`title`/`objectives`), a `steps.json` gate skeleton, and `course.yaml` create-or-extend via `--course-name`/`--course-title`/`--module` (rebuilding a repo lesson only appends its slug — multi-lecture imports converge on one manifest). `--legacy-layout` opts out. `course-vet.py` gained the skeleton guard: a lesson whose frontmatter `status:` starts with `skeleton` FAILS vet with a fill-first error, so freshly scaffolded courses cannot pass as teachable by accident; frontmatter YAML parse errors now report verbatim instead of masquerading as "no frontmatter". Fixes: unquoted colon in scaffold status line broke YAML parsing.

### v0.18.0 (2026-09-29)

**Standardized tutorial/quiz course format (hlab-course.v1) + `bin/course-vet.py`.** Goal: consistent §6/§7 performance across hosts, sessions, and models by moving the three judgment-heavy checks onto written data.

- **`course.schema.v1.json`** — schema for the parsed `course.yaml` manifest: `schema: herdr-lab/course.v1`, `name`, `shell` (fish-aware snippet flagging), optional `scratch_setup`, `passing_score` (default 0.8), ordered `modules[].{id,title,lessons[]}`. Kills layout drift between courses (the `week-N-*` vs `lessons/<slug>` split).
- **Lesson frontmatter** — `id` (== dir slug), `module`, `title`, `objectives[]`, plus optional `difficulty`, `est_minutes`, `prerequisites[]`, `quiz`. Replaces prose metadata like "Phase 1 · est. 2–3 h".
- **`steps.schema.v1.json` + optional `steps.json`** — machine-readable §6 step gates: `instruction` (the §6 chat string), `accept[]` (command + genuine variants — the §6 step-(b) "valid variant" check as data), `output_fragment` / `silent: true` (deterministic non-empty proof / buffer-growth check), optional `recorded: <rehearsal transcript>`. The §6 hidden-tab rehearsal stays agent-driven (vet grades the evidence, never runs commands).
- **`quiz.schema.v1.json` v1 extensions** (additive, back-compatible): `items[].objectives[]` (slug tags → vet coverage + §7 closing summary names objectives), `items[].points` (weighted scoring vs `passing_score`), `items[].accepted_synonyms[]` on `short` items (fixed free-text adjudication set instead of per-run judgment).
- **`bin/course-vet.py`** — the vet-first enforcement point (PyYAML required, jsonschema optional with structural fallback): manifest + frontmatter + steps + quiz validation, orphan-lesson detection, and the 2026-09-25 option-position anti-pattern audited across consecutive optioned items. Read-only by design.
- SKILL.md §6 gains the vet-first rule + format contract; §6 step (b) and §7 steps e/summary now consume the new fields. algal-wgs retrofitted as the reference implementation.

### v0.17.0 (2026-09-29)

**Renamed: `herdr-skill+` → `herdr-lab`.** The `+` in the skill/folder name was incompatible with some coding agents (treated as a regex quantifier or rejected by strict `[a-z0-9-]` name parsers). Renamed the skill, folder, symlinks, GitHub repo (`herdr-skill-plus` → `herdr-lab`), schema namespace (`herdr-skill+/quiz.v1` → `herdr-lab/quiz.v1`), and pane metadata tokens (`--source herdr-lab`). Old GitHub URLs keep working via GitHub's automatic redirect. No behavior changes — name only.
### v0.16.0 (2026-09-24)

**Three operational rules adopted from community practice** (research into other herdr orchestration skills and parallel-agent workflows):

- **§2 verification economics.** Re-checking is for changed inputs, not ceremony: reuse a check's result when its inputs are unchanged (a handoff, re-read, or re-prompt does not invalidate evidence or require a second full suite); rerun only checks whose inputs changed, results went stale relative to later edits, or that contradict other evidence. Both failure modes named: redundant re-runs burn time budget; stale green results hide regressions.
- **§1 step 4 — staged dispatch for expensive or hard-to-verify batches.** When batch outputs are costly or slow to verify (image/doc generation, long migrations, no cheap pass/fail marker), send 1 first, verify it per §2 against a representative case, then dispatch the remainder — a systemic defect caught after dispatch is N× the damage.
- **§4.5 — unattended-yolo rule.** Explicitly unattended work (user-requested fire-and-forget, or long unwatched batches) launches with the harness's full-auto-approval flag from the §4.5 table instead of the intermediate default, because a blocked worker nobody is watching is a dead worker. Scoped: explicit user intent only (never chosen for convenience), task-owned paths only, one chat line disclosing the flag; secrets/credentials/outside-owned-paths → §5, never yolo; interactive sessions keep the intermediate default.

### v0.15.0 (2026-09-24)

**New §8 — multi-agent brainstorming mode (bidirectional).** Until now, "brainstorm with another agent" meant one-shot opinion collection (prompt → read → relay). §8 turns it into a real critique exchange, designed via online research (arXiv 2502.19130 *Voting or Consensus?*, Du et al. 2305.14325, arXiv 2502.19559 problem drift, kiloloop/brainstorm protocol) and a live two-round debate with a delegated Claude Code seat — which conceded 4 orchestrator critiques, revising the design mid-flight (the section was dogfooded before it existed):

- **Round structure** R0 independent draft (orchestrator writes its own BEFORE reading any seat — it is a participant; prevents anchoring) → R1 anonymized cross-critique (positions shuffled/unattributed, copied verbatim from seat-written fields, no tallies) → R2 decision round only if real disagreement remains. Hard cap 2 interaction rounds — add seats, not rounds (forced extra rounds reduce accuracy; groupthink).
- **Sycophancy countermeasures**: herdr's seat isolation IS the "no direct communication" channel the research recommends; `CHANGED: yes` must cite a named argument, and the orchestrator greps the saved relay file to verify it (fabricated = discounted); `RELAY FIDELITY` self-check per seat; the orchestrator never picks/paraphrases which arguments to relay (relay-author-bias fix from round 2).
- **Decision protocols by sub-mode**: divergent → Borda rank of pooled ideas (dissent = novelty); convergent/reasoning → plurality vote with ≥3 seats (2-seat ties go to the user; approval voting forbidden — 59% no-decision); convergent/factual → orchestrator verifies each EVIDENCE line; synthesis → merge with a Dissent section. The orchestrator never votes at any seat count.
- **Round barrier + blocked seats**: one §3 recovery attempt + 5-min window, then `excluded-r<N>` in the ledger (R0 position kept in Dissent, labelled "not critiqued", no vote); <2 active seats → ask the user.
- **Wiring**: seats are T3 read-only (§4.5); §4.6 ask-user gate extended (≥3 seats, any T2 seat, round past cap, hard-cap harness); one §1.6 ledger row per seat with a new `round` field; per-round artifacts `<ledger-dir>/<batch>/r<N>-<seat>.md` make a brainstorm resumable after compaction.

### v0.14.0 (2026-09-24)

**Batch execution, merge-back, and resumability** (from a Claude Code feature brainstorm; all flags verified against `docs-corpus/herdr/online-docs-0.8.2/`):

- **§1 step 4 — parallel batch dispatch.** With 2+ agents, a batch is only parallel if all prompts are sent before any wait begins: prompt each agent with `until: ["working"]` (returns on acceptance), then `herdr_agent wait` on every agent, servicing `blocked` first. Explicitly not fire-and-forget — every agent is still waited on and verified per §2.
- **§1 isolation note — native herdr worktrees.** `herdr worktree create --cwd <repo> --branch <task>-<agent> --label <agent> --no-focus` replaces raw `git worktree add` (workspaces grouped under the parent repo, `worktree.created` events, right cwd inherited for free); `herdr worktree remove --workspace <id>` for cleanup (never deletes the branch, `--force` is ask-first). Raw git kept as fallback.
- **New §1.5 worktree merge-back.** Gate on §2 verification → per-worktree diff+tests → merge smallest-diff-first → conflicts sent back to the owning agent (never resolved silently; escalate after 2 failed rounds) → cleanup that never deletes a branch without asking.
- **New §1.6 batch ledger + `bin/herdr-batch.py`.** Interruption-survivable JSON ledger (one row per agent: task, tier, harness, tab/pane IDs, worktree, session_id, convo_cursor, state, verified). Resume after herdr restart or context compaction by matching `herdr_agent list` rows on the `<task-slug>-<harness>` agent naming; lost agents re-dispatch only with user approval. Stdlib-only; `new` / `set` / `show --md` / `todo` subcommands.
- **§1 batch labeling.** Tabs renamed to the task slug (`herdr tab rename`), agents named `<task-slug>-<harness>` (doubles as the ledger join key), optional sidebar tokens via `herdr pane report-metadata`.
- **§6 expected-output precomputation.** Optional hidden-tab rehearsal on a throwaway copy of the scratch dir so lesson gates compare the student's output against *real* recorded output (success and error variants). Deterministic exercises only; the student still types every command.

Also reconciles README version drift again (README still showed v0.12.0 while SKILL.md was at v0.13.1 — the v0.13.x tab-first topology rule: 1 secondary agent → pane_split, 2+ → one new tab per agent, because 2+ splits squeeze panes to ~1/4 width).

### v0.12.0 (2026-09-19)

**§6 step-gate loop hardening** (from an external Claude Code review of SKILL.md):

- **Output-vs-step verification.** On `I did it`, the pane read is now checked against the step before explaining: the instructed command (or a valid variant) must appear as executed, and a command that should produce output must not be empty. Mismatches route to the error branch instead of being confidently narrated as correct. New anti-pattern: narrating unverified output.
- **Hardened `wait_output` fall-back.** The old output-anchored regex could not distinguish a completed silent command (`cd`, `export`, `set`) from a stale prompt. The fall-back now requires buffer growth past a pre-instruction line-count snapshot **plus** a trailing prompt match; residual limit (long-running silent commands) documented with two workarounds (wait on an output fragment, or an explicit `echo step-N-done` marker).
- **Tab-back cue.** With `focus: true` the student is in the side pane and may not think to return; the first instruction now must include one sentence on how to get back to the chat gate, repeated if the gate sits unanswered.
- **Retry cap.** After 3 consecutive `Something went wrong` answers on the same step, the identical gate is no longer re-issued; the loop offers skip / show-expected-result / keep-trying through the gate, and ends honestly if the student prefers. Never forced.

Also reconciles README version drift (README still showed v0.11.1 while SKILL.md was already v0.11.2 — the concurrent-write isolation decision rule shipped in v0.11.2).

### v0.11.2 (2026-09-16)

**Concurrent-write isolation decision rule in delegation step 1.** Added the decide-BEFORE-splitting rule: N writers > 1 → per-agent `git worktree add` with the worktree path as the pane's cwd; worktrees NOT needed for advisory-only agents, disjoint-directory, or serial work. Sharing one tree fails silently (index.lock races, contaminated test runs); worktree overhead fails loudly.

### v0.11.1 (2026-09-15)

**`quiz.schema.v1.json` schema fix.** Lowered `options.minItems` from 2 to 1. The schema's prose already said `short` and `task` items are "optional / forbidden" for `options` (they rely on the host's `Type something.` row at runtime), but the `minItems: 2` constraint made that impossible to express in practice — surfaced during the v0.11.0 cross-host test (item 4 of `/tmp/quiz-test/quiz-herdr-basics.json` is a `short` with no options). Same `quiz.v1` contract, just no longer self-contradictory.

### v0.11.0 (2026-09-15)

**§6 / §7 push-UI question tool is now host-aware.** Replaced every prose reference to `ask_user_question` (the Pi-rpiv-specific tool name) with the generic phrase "the host's push-UI question tool" and added a *Host equivalents* table at the top of §6 with the 5 host variants (Pi: `ask_user_question`; Claude Code: `AskUserQuestion` built-in; OpenCode: `task` permission policy `question`; RPC/ACP: native dialogs; non-interactive: tool removed). The *workflow contract* — one blocking tool call, zero LLM tokens while the student answers, two-option gate on §6 lesson steps, one tool call per §7 quiz item — is identical across hosts. Host-specific features (preview side-by-side, `Submit` review tab, per-question notes) degrade silently when not available. This makes §6 / §7 readable on Claude Code and OpenCode without breaking Pi behavior.

### v0.10.0 (2026-09-15)

**`bin/quiz-import-pdf.py --llm-stdin` LLM-mediated fallback.** User flagged the v0.9.0 importer as too rigid. New stdin mode writes source text to `<lesson>/source.txt`, scaffolds the lesson Markdown + quiz JSON, emits a `FILL_THIS.md` directive for the agent's next turn. CLI stays deterministic (no API key, no model dependency). Schema's `source.type` enum gains `"stdin"`. See `obs-2026-09-15-herdr-skill-plus-v0-10-0-llm-stdin-fallback`.

### v0.9.0 (2026-09-15)

**Markdown is the spine, JSON only at the lesson→quiz boundary.** User correction: course content was invented-as-JSON when the precedent `course-materials/bacterial-genome-pipeline/` already uses plain Markdown. Rewrote importer to emit `<lesson>/{README,exercises}.md` and `<lesson>/quiz-<id>.json`. Removed the buggy multi-lesson splitter. See `obs-2026-09-15-herdr-skill-plus-v0-9-0-markdown-spine-json-quiz-boundary`.

### v0.8.0 (2026-09-15)

**`quiz.schema.v1.json` + importer.** JSON Schema 2020-12 interchange for §7 quiz items (`mcq` / `multi` / `preview` / `short` / `task`); importer stub emits skeleton items the agent fills (never auto-grades). See `obs-2026-09-15-herdr-skill-plus-v0-8-0-quiz-schema-and-importer`.

### v0.7.0 (2026-09-15)

**§7 Quiz mode.** New section, same `ask_user_question` gate primitive as §6, different per-item loop. One `ask_user_question` per item (never batched, so the `Submit` review tab doesn't swallow per-item coaching). See `obs-2026-09-15-herdr-skill-plus-v0-7-0-quiz-mode-design`.

### v0.6.0 (2026-09-15)

**§6 tutorial mode rewrite.** Replaced the `bash sleep` + `herdr_pane read` polling loop (per-iteration LLM-token noise) with one blocking `ask_user_question` per lesson. Live-tested end-to-end with the user (4 lessons completed: `pwd`, `mkdir`+`cd`, `echo` + `> / >>`, `ls -la`). See `obs-2026-09-15-herdr-skill-plus-v0-6-0-tutorial-mode-live-test` and the gate-design note `obs-2026-09-15-herdr-skill-plus-v0-6-0-tutorial-mode-uses-ask-user-question-gate`.

### v0.5.0 → v0.4.x

Earlier versions (model discovery + provider preflight in §4.6, sudo pattern in §5, cross-agent delegation tests). See git log.

## Provenance & License

Built with the [bioinfo-skill-creator](https://github.com/cheahhl814/bioinfo-skill-creator) meta-skill (v1.1.0). The flat workflow-library layout (no preflight → run → qc sub-skill chain) is intentional — herdr-lab is a **single skill for one human conversational workflow**, not a batch pipeline.

Released under the MIT License — see the `LICENSE` file in this repository for details.
