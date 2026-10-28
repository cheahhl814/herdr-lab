---
name: herdr-lab-delegation
description: herdr-lab delegation core (§1-§5) — delegate tasks to another coding agent via herdr panes, run parallel batches (tab-first topology, staged dispatch), verify completion signals, recover stalls/false-settlements, discover models+quota pre-flight (pi/opencode/claude/codex/copilot/agy), match providers to task tiers (T0-T3), and run sudo / privileged / secret-entry commands safely in a dedicated pane. Ships the interruption-survivable batch ledger bin/herdr-batch.py and the offline docs-corpus (verbatim --help captures + online docs for herdr + 7 harnesses; never invent a flag not present there). Workflow-only, tool schemas are the source of truth. Use when the user mentions Herdr, asks to delegate to another agent, run agents in parallel, run a privileged/secret-entry command in a managed pane, or check another agent's quota/usage.
version: 0.24.1
updated: "2026-10-28"
triggers:
  - user mentions Herdr by name
  - delegate a task to another coding agent
  - run agents in parallel / multiple agents at once
  - run sudo or another privileged command safely
  - check another agent's model/quota/usage
requires:
  - herdr >= 0.8.0
  - pi-herdr plugin installed and active (HERDR_PANE_ID set)
  - HERDR_ENV=1
  - docs-corpus/ present (reached via the docs-corpus symlink sibling of this file, or alongside the herdr-lab router)
---


Herdr tools are opt-in: only use them when the user explicitly invokes this workflow (see triggers above). Tool descriptions define WHAT each action does and its parameters — this file only orders calls, defines checkpoints, and lists recovery paths.

**docs-corpus**: `docs-corpus/` (sibling of this file) holds verbatim `--help` captures for the `herdr` CLI plus 7 coding-agent harnesses, their **online documentation** ingested via docs-ingest (permission semantics, config files, quotas, sandbox policies — under `docs-corpus/harnesses/<harness>-online-docs/` and `docs-corpus/herdr/online-docs-0.8.2/`), and a curated permission-flag table, plus `docs-corpus/herdr/supported-agents.md` — the full 21-kind cross-reference of agents herdr supports, with per-agent detection limits — and `docs-corpus/providers/` (Ollama online docs + `providers-matrix.md`, the curated harness×provider wiring and task-tier facts behind §4.6). For an unknown flag or an unexplained error, read in this order: `docs-corpus/harnesses/permission-modes.md` → `docs-corpus/harnesses/help-<harness>.md` → `docs-corpus/harnesses/<harness>-online-docs/` (deeper semantics; may differ from the installed version) → `docs-corpus/herdr/` → `docs-corpus/providers/`. Never invent a flag not present in the corpus.

## §1 Delegation sequence (core)

1. **Decide the topology BEFORE creating layout.** Count how many secondary agents the task will run concurrently.
   - **1 secondary agent** → `herdr_layout pane_split` — get a pane ID. Default topology: sibling pane, caller's tab + cwd. Use another tab/workspace/cwd only if the user asked for it. For background work the user should not be pulled into, pass `focus: false` on the `herdr_layout` call (the standalone `herdr` CLI's equivalent, if invoked directly rather than through the tool, is `--no-focus`).
   - **2+ secondary agents** → do NOT split a second pane. Every split beyond the first shrinks each pane's share of the screen; at 2+ splits a pane drops to roughly 1/4 width, where agent output is effectively unreadable — both for you when verifying via `herdr_agent read`/`herdr-convo` and for the user watching the TUI. Instead, create **one new tab per agent** (`herdr_layout tab_create`; each new tab comes with its own root pane — no extra split needed) and run steps 2–5 below against each tab's root pane. Tabs keep every agent full-width; the user switches tabs instead of squinting at quarter-panes. Set each tab's `cwd` the same way you would have set the pane's (worktree/scratch dirs per the concurrent-write isolation rule below); pass `focus: false` for background batches the user shouldn't be pulled into.
   
   > **Concurrent-write isolation (decide BEFORE splitting):** if two or more agents will WRITE to the same git repo concurrently, give each writing agent its own worktree — prefer herdr's native command: `herdr worktree create --cwd <repo> --branch <task>-<agent> --label <agent> --no-focus`. It creates the checkout (under the configured worktrees directory when `--path` is omitted), opens it as a workspace **grouped under the parent repo workspace**, and emits `worktree.created` events; point the agent's tab/pane at the returned workspace's cwd so it needs no manual cwd. Cleanup is `herdr worktree remove --workspace <id>` — it runs `git worktree remove`, never deletes the branch, and refuses a dirty checkout without `--force` (never force without asking the user). Fallback for herdr versions without `worktree`: `git worktree add ../<repo>-wt-<agent> -b <branch>` per writing agent, passing that path as the pane's cwd. Either way, integrate via the §1.5 merge-back procedure, where conflicts are visible instead of silently interleaved. Sharing a tree fails silently (index.lock races, contaminated test runs from a neighbor's half-finished edits, clobbered build/cache state), while worktree overhead fails loudly. Worktrees are NOT needed for advisory/brainstorm agents that write only to /tmp briefs, disjoint directories (one agent per subtree, explicit ownership), or serial work (one writer, others idle) — there a worktree is pure ceremony and adds a stale-base problem. Rule of thumb: N writers > 1 → isolate; N readers / 1 writer → share the tree.
2. Verify the pane is at an idle interactive shell prompt (`herdr_pane read`) before starting an agent.
3. `herdr_agent start` with the pane ID.
   - `name` must match `[a-z][a-z0-9_-]{0,31}`; for batches use `<task-slug>-<harness>` so the name doubles as the §1.6 ledger join key (rename later via `herdr_agent rename` if needed).
   - `kind` = the recognized agent to start.
   - `agentArgs` optional — see §4 for model flags.
4. `herdr_agent prompt` with wait enabled (default). Do not skip waiting unless the **user** explicitly asked for fire-and-forget — never choose it yourself for convenience, since it removes the user's only visibility into the secondary agent.
   - **Batch dispatch (2+ agents, tab topology):** a batch is only parallel if all prompts are sent before any wait begins. Round 1 — `herdr_agent prompt` each agent with `until: ["working"]` (returns as soon as the agent accepts the prompt; `--until` requires wait enabled, per `docs-corpus/herdr/online-docs-0.8.2/cli-reference.md`). Round 2 — `herdr_agent wait` on every agent (`--until` `done`/`idle`/`blocked`), servicing `blocked` agents per §3 as they surface. This is NOT fire-and-forget: the batch is finished only when every agent has been waited on and verified per §2, and each agent's result is still relayed individually. Record tab/pane/agent IDs in the §1.6 batch ledger as you go. **Staged dispatch for expensive or hard-to-verify batches:** when the outputs are costly or slow to verify (image/doc generation, long migrations, anything with no cheap pass/fail marker), do NOT dispatch all N at once — send 1 first, verify it per §2 (spot-check a representative case, not an edge case), and only then dispatch the remainder; the un-verified remainder is where a systemic defect multiplies N times.
5. `herdr_agent read` (or **herdr-convo**, below, for claude/codex/opencode/pi) — read and verify per §2 before treating the task as done, then relay the secondary agent's actual output (not just "done") back to the user — they cannot see the pane unless they look at it themselves.

> **zoetrope plugin** (source 3, `docs-corpus/herdr/related-plugins.md`) — if installed, this is the user's own answer to "I can't see what the secondary agent is doing" (§1 step 4's concern): focusing a claude/codex agent pane and pressing `prefix+shift+z` opens a live flow-graph overlay of that session for the **user** to watch directly — it doesn't change what you (the calling agent) do, but mention it exists when delegating so the user knows they have a real-time option beyond waiting for your relay.
> 
> Non-interactive/print-mode invocations (`-p`, `exec`, `--print`, etc., run via `herdr_pane run` instead of `herdr_agent`) have no lifecycle, no §2 states, and none of the §3 recovery paths — a blocked or approval-seeking sub-agent just hangs silently with nothing to read. Reserve this mode for the T3 one-shot case in §4.6 (short, read-only, unlikely to need approval); default to interactive `herdr_agent` delegation for everything else so state and output stay observable.

> CRITICAL: `herdr_agent start` never creates or changes layout. If no pane exists yet, step 1 is mandatory — never call `start` against a pane you have not just split or confirmed idle.

> Pane hygiene: reuse an existing idle-pane shell running (or last running) a compatible harness instead of splitting a new pane per task; keep total panes ≤2 per tab (incl. primary) — a batch of 2+ agents goes into new tabs, not more panes (step 1) — and `herdr_pane close` unused ones once a task's verification completes — panes are a resource, not per-task disposables.
> Herdr panes run fish — `herdr_pane run` commands must be fish-safe (`$status`, not `$?`); a fish parse error aborts the entire line except the error banner.

> Batch labeling (2+ agents): rename each tab to the task slug right after `tab_create` (`herdr tab rename <tab_id> <label>` — syntax per `docs-corpus/herdr/online-docs-0.8.2/cli-reference.md`), and optionally report sidebar tokens per pane: `herdr pane report-metadata <pane_id> --source herdr-lab --token task=<slug> --token tier=<T0-T3>` (omit `--ttl-ms` to keep tokens until the pane closes; `--source` is ≤80 ASCII chars `[A-Za-z0-9:._-]`). At 3+ tabs this is the difference between navigating the batch and guessing which tab holds what.

## §1.5 Worktree merge-back (after a multi-writer batch)

Applies whenever §1's isolation rule produced 2+ worktrees. Never leave this to improvisation — this is where batches with several writing agents fail or leave stray worktrees and branches behind.

1. **Gate on verification**: every writing agent in the batch must have settled AND passed the §2 output check first. Never merge an unverified worktree.
2. **Review each worktree**: `git diff --stat <base>...HEAD` in the worktree, plus run its tests in that worktree's pane (`herdr_pane run` + `herdr_pane wait_output` on a pass/fail marker). Record the result in the §1.6 ledger.
3. **Merge one at a time** into an integration branch, smallest diff first, re-running the test suite after each merge.
4. **Conflicts go back to the owning agent** — never resolve them silently yourself. Send the conflict into the owning agent's pane (it runs `git merge <integration-branch>` inside its own worktree), wait, and re-verify per §2. After 2 failed merge rounds per agent, escalate to the user.
5. **Cleanup**: `herdr worktree remove --workspace <id>` per worktree and `herdr_pane close` per tab. Never delete a branch without asking the user; a dirty worktree removal needs `--force`, which is itself ask-first.

## §1.6 Batch ledger (interruption-survivable state)

For any batch of 2+ agents — and any single long-running delegation you might need to resume after context loss — keep a JSON ledger via `bin/herdr-batch.py` (reached through the `bin/` symlink sibling of this file; stdlib-only, see its `--help`). One row per agent: `{agent_name, task, tier, harness, tab_id, pane_id, worktree, session_id, convo_cursor, state, verified}`. `session_id` comes from `herdr-convo locate <pane>` (claude/codex/opencode/pi); `convo_cursor` from the last `herdr-convo read`.

- **Update the row at every state transition** (start, each §3 recovery, verification, merge-back) — once a batch outgrows a single turn, the ledger, not your context, is the source of truth.
- **Resume after a herdr restart or context compaction**: `herdr_agent list`, match rows by agent name (that is why §1 step 3's `<task-slug>-<harness>` naming matters — it is the join key); herdr auto-resumes supported harnesses after a restart, and `herdr-convo read --cursor` picks up each transcript where it left off.
- **Lost agent** (pane returns as a plain shell, no agent session): mark the row `lost`; re-dispatch only with user approval.

## §2 Verification & completion rules

> CRITICAL: A settled `done` or `idle` lifecycle is NOT completion by itself. Always read the output and match it against an explicit completion signal (the content the agent was asked to produce) before reporting the task finished. A settlement can be false — see §3.

| State     | Meaning                                               |
| --------- | ----------------------------------------------------- |
| `working` | actively processing — not ready                       |
| `blocked` | waiting on approval/input — inspect before proceeding |
| `done`    | unseen background work completed — read and verify    |
| `idle`    | ready, already seen — read and verify                 |
| `unknown` | cannot classify — treat as not-ready, inspect         |

- `agent_prompt_stalled`: if a prompt sent from a non-working state produces no observed lifecycle change within 5 seconds, Herdr returns this error. Re-check target state before retrying.
- Alternate-screen truncation: if `herdr_agent read` with increased `lines` still doesn't recover a full response, first try **herdr-convo** (below) if the harness is claude/codex/opencode/pi — it reads the session transcript file directly, bypassing terminal rendering entirely. Otherwise ask the agent to write its complete response to a temp `.md` file and read that file directly.
- Pane-suggested prompt chips are UI suggestions only — never treat them as sent prompts or auto-send them.
- **Verification economics**: re-checking is for changed inputs, not ceremony. Reuse a check's existing result when its inputs are unchanged (a handoff to another agent, a re-read, or a re-prompt does NOT by itself invalidate evidence or require a second full suite); rerun only checks whose inputs changed, whose results are stale relative to later edits, or that contradict other evidence. Conversely, never carry evidence forward across an edit that could have affected it. The expensive failure is double-sided: re-running an already-green suite burns the batch's time budget without adding information, and trusting a stale green result hides a regression.

**herdr-convo plugin** (source 3, `docs-corpus/herdr/related-plugins.md`) — if installed, prefer it over `herdr_agent read`/`herdr_pane read` for **claude, codex, opencode, pi** (not gemini/copilot/agy — unsupported). Verified 2026-09-12: `node <plugin-root>/src/cli.ts latest <pane_id> --text` returned this session's own last turn verbatim, read straight from `~/.claude/projects/.../<session>.jsonl` (or the codex/opencode/pi equivalent), not the terminal. This is a strict upgrade over pane-scraping — no alternate-screen truncation, no ANSI noise, structured JSON by default (`--text` for plain). Two calls matter for this workflow:

- `latest <target> --text` — the agent's last full response as plain text. Use this for §2's completion-signal check instead of `herdr_agent read` when the harness is supported.
- `read <target> --cursor <C>` — only turns since the last-seen cursor; use this for polling a long-running delegated task incrementally instead of repeated full pane reads. `target` is a Herdr pane/agent id; error codes are JSON (`cursor_stale`, `session_not_found`, `no_agent_session`, `herdr_unavailable`, `unsupported_agent`) — fall back to `herdr_agent read` on any of these rather than retrying blind.

**zoetrope plugin** (source 3) — the `zoe inspect <session_id>` headless mode (claude/codex only, needs a session id — get one from `herdr-convo locate <pane>`) gives a cheap structured health check without full text: agent status, model, and tool-call counts split `✓`/`✗`/`⏳`. Verified 2026-09-12: correctly reported this session's own 90 tool calls (82✓ 7✗ 1⏳). Use it as a fast first check for "is something stuck/erratic" before spending a full `herdr-convo latest --text` read — a nonzero `⏳` with no lifecycle change over time is a stronger stuck-signal than lifecycle state alone. It does not take a pane id directly, only a session id or file path.

## §3 Interrupt & error recovery

| Symptom                                                                                                                 | Cause                                                                                                                                                                           | Fix                                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workspace trust dialog appears (Claude Code)                                                                            | Agent started in an untrusted folder                                                                                                                                            | Cursor defaults to "No, exit". Send `["down","enter"]` to accept trust. **NEVER send bare `["enter"]`** — it kills the agent (confirmed incident).                                                        |
| `herdr_agent read`/`get` returns "agent target not found" right after a settlement                                      | Agent exited and vanished from the registry                                                                                                                                     | Fall back to `herdr_pane read` on the same pane ID.                                                                                                                                                       |
| Lifecycle settled (`done`/`idle`) but output doesn't match the expected result                                          | False settlement                                                                                                                                                                | Re-prompt with "continue" (or equivalent) and require the output to match an explicit completion signal before accepting it.                                                                              |
| Lifecycle is `blocked`                                                                                                  | Agent needs approval, an answer, or is stuck at a dialog                                                                                                                        | Read the pane first to classify, then act: approval request → send the requested approval keys/text; open question → `herdr_agent prompt` with the answer; trust dialog → use the trust-dialog row above. |
| Agent settles as `idle`/`done` but seems to wait for input; or state is erratic (esp. `gemini`, `cline`, amp/kiro/maki) | Detection limits: unknown prompt shapes fall back to `idle` (`default_known_agent_idle_fallback`); gemini/cline are "less thoroughly tested"; amp/kiro/maki have no integration | Trust output reading over lifecycle state (§2). Check detection with `herdr agent explain --agent <kind> --json`; see `docs-corpus/herdr/supported-agents.md` for per-agent detection limits.             |
| First prompt returns an API/auth error (e.g. `Unauthorized`)                                                            | Provider listed but not authenticated/usable — model listing ≠ model usable                                                                                                     | Read the pane to confirm; treat that harness/provider as unavailable; fall back to the next property-matched candidate (§4.6 step 3) — do not retry the same option.                                      |

Symptom not covered above, or a flag/error you don't recognize → consult `docs-corpus/` (see note above) before guessing.

## §4 Launch configuration: model discovery + quota pre-flight

Discover model names and quota state at call time — never hardcode a model name or quota number in a prompt or plan.

| Harness  | List models                   | Model flag (via `herdr_agent start` `agentArgs`)                                | Quota/usage surface                                                                          |
| -------- | ----------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| pi       | `pi --list-models [search]`   | `--provider`, `--model`, `--models` — see `docs-corpus/harnesses/help-pi.md`    | `pi auth <cmd>` (provider readiness); Ollama models are compute-metered, not quota-capped    |
| opencode | `opencode models`             | `-m <name>` or model config                                                     | in-TUI percentage indicator only                                                             |
| claude   | no CLI list — in-TUI `/model` | `--model`, `--fallback-model` — see `docs-corpus/harnesses/help-claude.md`      | **herdr-agent-quota** JSON, if installed (below); else in-TUI `/usage` or `/status`          |
| codex    | no CLI list — in-TUI `/model` | `-m`/`--model`, or `-c model="..."` — see `docs-corpus/harnesses/help-codex.md` | herdr-agent-quota only covers ChatGPT-subscription auth, not API-key auth — in-TUI `/status` |
| copilot  | no CLI list                   | `--model <model>` (default `auto`)                                              | **hard cap** on free tier — no plugin coverage (see below) — re-verify via the probe recipe  |
| agy      | no CLI list surfaced          | none surfaced                                                                   | **herdr-agent-quota** JSON, if installed (below); else undocumented cap, expect HTTP 429     |

Re-verify: exact commands, flag syntax, and any numeric caps drift between CLI versions — cross-check `docs-corpus/harnesses/help-<harness>.md` (or re-capture it) before relying on them; do not carry numbers forward from a prior session.

**Quota probe recipe** (no CLI surface, all harnesses): `herdr_agent start` → `herdr_agent send_keys` the usage slash command (e.g. `/usage`, `/status`) → `herdr_agent read` (`recent-unwrapped`) to record tier/quota — advisory only, format varies by CLI version. Probe before delegating to a hard-cap harness (copilot, agy) or before a parallel batch that could exhaust a shared limit.

**herdr-agent-quota plugin** (source 3, `docs-corpus/herdr/related-plugins.md`) — if installed and configured (`herdr plugin action invoke configure --plugin herdr-agent-quota`, not the raw binary — see below), `claude`/`agy` quota is collected passively by a statusLine/hook the harness itself invokes every turn, not by polling. Read it directly instead of the `refresh`/`dashboard` subcommands (those need pane/session context this skill's ad hoc CLI calls don't have, and return `unavailable` even with real data present):

```
cat ~/.local/state/herdr/plugins/herdr-agent-quota/claude-statusline.observation.json   # claude
cat ~/.local/state/herdr/plugins/herdr-agent-quota/agy-statusline.observation.json      # agy
```

Each file's `snapshot.windows` gives `five_hour`/`weekly` `used_percent`/`remaining_percent` + `resets_at`; absent file = that harness hasn't run a turn since the hook was installed yet. Coverage gaps, verified 2026-09-12 on this machine: no `copilot`/`pi`/`opencode` support at all — still use the scrape recipe for those; `codex` only works with ChatGPT-subscription auth, not API-key auth.

Enabling this for `claude`/`agy` writes `~/.claude/settings.json` / `~/.gemini/antigravity-cli/settings.json` (a `statusLine` block only, verified minimal diff) — a standing-config change: ask the user before enabling it, and never run `configure --apply` yourself if `~/.claude/settings.json` is your own config (Claude Code's self-modification guard blocks that, and the plugin separately refuses the raw binary — must go through `herdr plugin action invoke configure --plugin herdr-agent-quota`). Direct the user to run it in a pane.

## §4.5 Permission / auto-approval modes at launch

Most harnesses block shell commands by default. Pass the flag via `herdr_agent start` `agentArgs`. Flags below are sourced from `docs-corpus/harnesses/permission-modes.md`, verified against the verbatim `help-<harness>.md` captures — do not use a flag not present there. Codex has **no** `--full-auto` flag in this version — do not cite it.

| Harness  | Intermediate (recommended default: edits auto, exec gated) | Full auto-approval (yolo)                                                 | Read-only / plan                                                                |
| -------- | ---------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| claude   | `--permission-mode acceptEdits`                            | `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` | `--permission-mode plan`                                                        |
| codex    | `-s workspace-write -a never` (or `--approve-for-me`)      | `--dangerously-bypass-approvals-and-sandbox`                              | `-s read-only`                                                                  |
| gemini   | `--approval-mode auto_edit`                                | `-y`/`--yolo` or `--approval-mode yolo`                                   | `--approval-mode plan` (newer CLI gates behind `experimental.plan` — re-verify) |
| copilot  | `--allow-all-tools` (paths/URLs still asked)               | `--allow-all` / `--yolo`                                                  | none — use `--allow-tool` granularly                                            |
| agy      | none — single switch only                                  | `--dangerously-skip-permissions`                                          | none                                                                            |
| pi       | none needed — no permission popups by design               | none needed                                                               | none                                                                            |
| opencode | config-driven (`opencode.json` `permission`), no CLI flags | config-driven                                                             | config-driven                                                                   |

**Escalation ladder** (agent blocked on approval in-pane): read the pane to classify the prompt (§3) → single approval: send the confirmation key(s) → repeated approvals for the same action kind: pass the intermediate auto-approval flag on the **next** `herdr_agent start` (never change flags mid-session) → secret/credential prompt: never auto-answer, escalate to the user (§5).

**Unattended-yolo rule** — unattended workers must never stall on permission prompts: if the work is explicitly unattended (the user asked for fire-and-forget, or a long batch they will not be watching), launch with the harness's full-auto-approval (yolo) flag from the table above instead of the intermediate default — a blocked worker nobody is watching is a dead worker, and §3's blocked-handling path presumes someone is present to service it. Scope: only with the user's explicit unattended intent (never choose yolo yourself for convenience — mirrors §1 step 4's fire-and-forget rule), only in repos/dirs the task owns, and state one line in chat that the seat runs with auto-approval and which flag was used. Anything touching secrets, credentials, or paths outside the task's ownership → §5 pattern, never yolo. Interactive/watched sessions keep the intermediate default.

## §4.6 Provider preflight & task-tier matching

Decision procedure — cache discovery in-session per harness/provider after first run:
0. **Routing profile**: read optional `~/.config/herdr/routing.json` (user-owned; skill reads, never writes; schema: per-tier `{harness, provider, model_pattern}` + optional `avoid` list). An exact tier match short-circuits discovery — skip to step 5.

1. Classify the task into a tier (table below).
2. Discover lazily (first use per session, then reuse): harnesses via `herdr agent start --help` + `docs-corpus/herdr/supported-agents.md`; providers per harness (pi `--provider`/`--list-models`; opencode `opencode models`; copilot provider env vars; codex `model_providers` in config.toml; claude/gemini/agy locked — see `docs-corpus/providers/providers-matrix.md`); models per provider (§4 list commands + `ollama list`, note `:cloud` vs local); Ollama pre-flight (daemon via `ollama ps`, model present via `ollama list` — `ollama pull` is a prerequisite, never implicit).
3. Match discovered options against the tier's required properties, never by remembered model name.
4. **Ask-user gate** — fire ONLY when no profile match AND (T2 task, OR a hard-cap harness is near its probed limit, OR ≥2 candidates tie on all required properties, OR a §6 brainstorm with ≥3 seats, any T2 seat, or a round beyond R2). Use the house Evidence + Recommend + Options convention. Never fire for an unambiguous T0/T1 match or a profile hit — auto-pick.
5. State tier + chosen option + one-line reason (profile match / cheapest / fastest / quota constraint) before launching.

Fallback: a herdr-delegated sub-agent with no ask-user tool surfaces its recommendation in pane output and waits; the calling agent reads it and asks the user on its behalf.

| Tier                    | Task shape                                                | Required properties                                                |
| ----------------------- | --------------------------------------------------------- | ------------------------------------------------------------------ |
| **T0** trivial/bulk     | lint fixes, mechanical renames, batch small edits         | cheap, fast, tool-use adequate                                     |
| **T1** standard dev     | single/few-file features, bugfixes, tests                 | solid tool-use reliability, mid context                            |
| **T2** heavy agentic    | multi-file refactor, cross-cutting changes, long planning | large context, strongest reasoning + tool-use, cost-insensitive OK |
| **T3** read-only/review | code review, analysis, research, quota probes             | read-only/plan mode (pair with §4.5)                               |

**T3 note**: for short read-only reviews, prefer a one-shot (`claude -p --permission-mode plan` with file redirect) over an interactive plan-mode session — TUI redraw/truncation makes short answers hard to retrieve via `herdr_agent read`, and settling `idle` while the TUI still shows "Generating…" is a known false-settlement flavor.
**Ollama note**: `:cloud` models proxy to Ollama's hosted service (account + egress required); local models run on-box, offline/private, need VRAM headroom, weaker at T2 work.
**Refusals**: never sum/infer shared quota across harnesses proxying the same provider account — probes are harness-local only. Verify the active provider before trusting a probe/cost estimate. Custom-provider API keys/base-URLs follow §5. Never change a harness's provider config without asking first.

## §5 Privileged & secret-entry commands (sudo pattern)

1. `herdr_layout pane_split` — dedicated pane for the privileged command. Never run it in the calling pane.
2. `herdr_pane run` the sudo (or other privileged) command in that pane.
3. `herdr_pane wait_output` for the password prompt (e.g. `"[sudo] password"`).
4. **Notify the user to type their password directly into the TUI pane.** Do not proceed on their behalf.
5. `herdr_pane wait_output`/`read` for the completion marker.
6. `herdr_pane read` the result.
7. Keep the pane open — sudo credential caching is per-tty, so follow-up privileged commands in the same pane skip re-prompting.

This generalizes to any interactive secret prompt: GPG passphrase, SSH key passphrase, 2FA code, etc.

**Anti-patterns:**

- NEVER `send_keys`/`send_text` a password or secret into a pane.
- NEVER pipe a password, e.g. `echo pw | sudo -S`.
- NEVER ask the user to paste a secret into the agent/chat — only into the TUI pane directly.
- NEVER run sudo (or any privileged/secret-entry command) in the calling pane — always a dedicated split pane.

Drift rule: if any section above starts restating tool parameters or capabilities, delete that section.
