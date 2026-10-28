# herdr-lab-delegation

**Skill name**: `herdr-lab-delegation` · **Version**: 0.26.0 · **Type**: agent skill (workflow-only)

The delegation core of the [herdr-lab](https://github.com/cheahhl814/herdr-lab) family: delegate a task to another coding agent through [herdr](https://github.com/ogulcancelik/herdr) panes, run parallel batches, verify completion, recover stalls, and pick the fleet (how many harnesses, which harness, which model) before any of it starts.

> This is a **sub-skill**. It has its own frontmatter, its own trigger set, and can be symlinked on its own — it does not need the `herdr-lab` router to be loaded. The router is a thin dispatcher; the workflow lives here.

**Workflow-only** — `herdr_layout` / `herdr_pane` / `herdr_agent` tool schemas are the source of truth for parameters. This skill orders calls, defines checkpoints, and lists recovery paths; it never restates tool parameters and never invents a CLI flag that is not captured in `docs-corpus/`.

## When it fires

Triggers (from the SKILL.md frontmatter):

```text
- user mentions Herdr by name
- delegate a task to another coding agent
- run agents in parallel / multiple agents at once
- run sudo or another privileged command safely
- check another agent's quota/usage
```

Plain "ask another agent X" is a **one-shot delegation** (§1). A critique / exchange request ("have them respond to each other", "devil's advocate") belongs to the sibling sub-skill [`herdr-lab-brainstorm`](../brainstorm/README.md).

## What it covers

| Section | Topic |
|:--------|:------|
| **§1** | Delegation sequence: topology → pane check → `herdr_agent start` → prompt + wait → read & verify. Tab-first topology for 2+ agents; concurrent-write isolation via worktrees. |
| **§1.5** | Worktree merge-back after a multi-writer batch (gate on verification, merge one at a time). |
| **§1.6** | Batch ledger — `bin/herdr-batch.py`, interruption-survivable state that outlives context compaction. |
| **§2** | Verification & completion rules — a settled state is not a finished task. |
| **§3** | Interrupt & error recovery — blocked agents, false settlements, lost agents. |
| **§4** | Launch configuration: model discovery + quota pre-flight (per-harness list commands, quota probe recipe, `herdr-agent-quota` plugin). |
| **§4.5** | Permission / auto-approval modes at launch, and the unattended-yolo rule. |
| **§4.6** | Provider preflight & task-tier matching (T0–T3) — **including the local fleet probe**: what *this* machine has installed, authenticated, and model-equipped. |
| **§4.7** | **Fleet composition** — how many harnesses to involve, which harness per seat, which model per seat, the cross-seat budget, the ask-user gate, and the fleet-plan artifact. |
| **§5** | Privileged & secret-entry commands (the sudo pattern) — dedicated pane, never the calling pane, never a secret in chat. |

## The fleet probe — knowing what this machine has

The docs-corpus says what a harness **supports**; it is a snapshot of the CLIs on the capture host, not an inventory of the machine you are running on. §4.6 step 2 answers availability locally:

```bash
python3 bin/herdr-capabilities.py              # fleet table
python3 bin/herdr-capabilities.py --json       # machine-readable
python3 bin/herdr-capabilities.py --no-models  # fast pass, no model listing
```

| Signal | Source |
|:-------|:-------|
| Startable kinds (live enum — 0.8.0 = 21 kinds, 0.9.0 = 23) | `herdr agent start --help` |
| Installed on PATH | `command -v <executable>` |
| Integration state (`current` / `outdated` / `not installed`) + hook path | `herdr integration status` |
| Models per installed harness | `pi --list-models`, `opencode models`, `ollama list`; harnesses without a CLI list pick the model in-TUI (`/model`) and report quota in-TUI (`/usage`, `/status`) |

Run it once per session and reuse the result. A missing binary is a fact to report, not a gap to paper over.

## Install

```bash
git clone https://github.com/cheahhl814/herdr-lab.git
mkdir -p ~/.pi/agent/skills
# keep the symlink name == the skill's frontmatter name
ln -sf "$(pwd)/herdr-lab/delegation" ~/.pi/agent/skills/herdr-lab-delegation
```

If your harness reads `~/.agents/skills/` instead, symlink there instead — same link, same name. The router (`herdr-lab`) and the sibling (`herdr-lab-brainstorm`) are separate links; each works alone.

**Requires**: `herdr >= 0.8.0`, the `pi-herdr` plugin installed and active (`HERDR_PANE_ID` set), `HERDR_ENV=1`, and `docs-corpus/` reachable through the sibling symlink.

## Layout

```text
delegation/
├── SKILL.md             # this sub-skill — the whole workflow
├── docs-corpus -> ../docs-corpus   # shared: herdr CLI + 7 harness captures
└── bin -> ../bin                   # shared: herdr-batch.py, herdr-capabilities.py
```

`docs-corpus/` and `bin/` live once at the repo root; the relative symlinks keep every path inside this file resolving whether the sub-skill is loaded through the router or symlinked standalone.

## Hard guarantees

- **Workflow-only, no tool redefinition** — tool parameters are never restated here; a drift rule at the bottom of SKILL.md deletes any section that starts doing so.
- **Schema-grounded tool usage** — a recommended herdr flag must be present in `docs-corpus/herdr/`; otherwise check the live `--help` instead of guessing.
- **Verified, not assumed** — a settled agent state is never treated as a completed task (§2).
- **Push-UIs over poll loops** — checkpoints use `ask_user_question` as a blocking gate; `bash sleep` + `herdr_pane read` polling loops are forbidden.
- **Fleet decisions are recorded** — the fleet plan and the ledger rows (`tier`, `harness`, `model`) outlive the context that produced them.

## License

MIT — see [LICENSE](../LICENSE). Upstream: <https://github.com/cheahhl814/herdr-lab>.
