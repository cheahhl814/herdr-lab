# Seat templates (`herdr-core` / `hc`)

Ready-made seat definitions for the Herdr **desktop** edition
(`hc run --bg --name <seat> <template> "<task>"`), in two tiers:

- **Lean, read-only** — T0/T3 work: search, review, summarize, verify. Minimal context
  injection; the seat cannot (or must not) change anything.
- **Heavy, working** — T1/T2 work: full tools, stronger model or higher thinking.
  Approval posture is *intermediate* (edits auto, shell still gated) — see below.

`hc` reads templates from **one place only**: `~/.config/herdr-core/templates/<name>.md`
(no config flag for another directory). This folder is the *source*; the
`bin/install-templates.sh` installer copies them there. Nothing here is live until it
is installed.

## Install

```sh
# from the repo root (or via the bin/ symlink inside desktop/)
bin/install-templates.sh              # installs all (lean + heavy), skips existing files
bin/install-templates.sh --dry-run    # show what would happen, change nothing
bin/install-templates.sh --only pi-lean,claude-heavy
bin/install-templates.sh --force      # overwrite existing files (use after pulling repo updates)
```

The installer **never overwrites by default**. After install, check with `hc templates`,
then edit the installed copies (not these) if you want a different provider/model.

Or, from a desk session, just ask: "set up the herdr-core templates" — the
`herdr-lab-induction` skill runs a guided setup (probe → questions → install) and is
offered automatically by herdr-lab when `~/.config/herdr-core/templates/` is missing or empty.

## Template format

```markdown
---
name: <name>          # used as: hc run --bg --name x <name> "<task>"
description: ...      # shown by `hc templates`; warn here if the seat is not read-only
command: <argv>       # the harness launch line; approval/permission flags live HERE
---

<body>                # becomes the first message together with your task
```
`hc` prints frontmatter values verbatim — write plain YAML scalars (no surrounding quotes, no `: ` inside unquoted values).

Flags belong in `command`, not on the `hc run` line — flags after the template name are
parsed as the task. A template that can act un-asked must carry its own approval posture
(see `delegation/SKILL.md` §4.5 for the flag table).

## The lean tier (read-only, T0/T3)

| File | Seat | Approval | Notes / what to edit |
|:-----|:-----|:---------|:---------------------|
| `pi-lean.md` | Pi, Ollama `glm-5.3-flash:cloud` | yes (`--tools read,grep,find,ls`) | `--no-mcp` confirmed present (2026-11-17); edit `--provider/--model` for your own Ollama |
| `claude-lean.md` | Claude Code | yes (`--permission-mode plan`) | `--safe-mode` drops skills/MCP/hooks/CLAUDE.md but **keeps** normal auth (unlike `--bare`, which forces API-key-only auth — deliberately not used). Plan mode: seat reports findings, cannot edit |
| `codex-lean.md` | Codex | yes (`-s read-only`) | `--no-daemon` required so codex commands stay under `hc`. No verified lean/context flag exists in the capture — context is NOT reduced |
| `gemini-lean.md` | Gemini CLI | yes (`--approval-mode plan`) | No captured flag disables skills/extensions; they still load. `--allowed-mcp-server-names` can whitelist MCP but not disable all |
| `copilot-lean.md` | Copilot CLI | yes (`--mode plan`) | `--disable-builtin-mcps` kills the built-in GitHub MCP; desktop GitHub login required |
| `opencode-lean.md` | OpenCode | **only if configured** | Env vars kill plugins/external skills/project config/Claude-Code compat. Permissions themselves are `opencode.json`-driven — ship a read-only agent or the seat may edit |
| `agy-lean.md` | Antigravity | yes (`--mode plan`) | `--disable-slash-commands` covers print mode only |

All lean bodies forbid edits, subagents and scope creep, and demand a short
findings-first final reply for `hc read`.

## The heavy tier (working seats, T1/T2)

| File | Seat | Approval posture | Notes / what to edit |
|:-----|:-----|:-----------------|:---------------------|
| `pi-heavy.md` | Pi, Ollama `glm-5.3:cloud`, thinking high | act (pi has no approval prompts) | all built-in tools; skills still off; edit `--model` / `--thinking` freely |
| `claude-heavy.md` | Claude Code, `opus`, effort high | intermediate (`acceptEdits`) | paths stay gated; flip to `--permission-mode bypassPermissions` only for fully unattended fleets (see below) |
| `codex-heavy.md` | Codex, workspace-write | intermediate (`-a never`, fails closed) | `-s workspace-write` keeps writes inside the workspace; add `-m <model>` to pin a model |
| `gemini-heavy.md` | Gemini CLI | intermediate (`--approval-mode auto_edit`) | no captured effort flag; pick a stronger `-m` model instead |
| `copilot-heavy.md` | Copilot CLI | intermediate (`--allow-all-tools`, paths/URLs still gated) | add `--model` to pin; `--allow-all` is the yolo variant |
| `opencode-heavy.md` | OpenCode | config-driven | permissions live in `opencode.json`; set `provider/model` with `-m`; grant `allow` only for unattended runs |
| `agy-heavy.md` | Antigravity | intermediate (`--mode accept-edits`, effort high) | pick a stronger `--model` from `agy models` |

Heavy bodies: scoped edits welcome, worktree/scope respect, no unrequested subagents,
end with a changed-paths + verification report for `hc read`.

**Unattended heavy fleets:** the intermediate posture stalls on shell-approval prompts when no one watches. For fully unattended batches flip each seat to its harness's yolo flag yourself (`claude --permission-mode bypassPermissions`, `codex --dangerously-bypass-approvals-and-sandbox`, `gemini -y`, `copilot --allow-all`, `agy --dangerously-skip-permissions`; pi needs nothing) — the orchestrator then cannot service approvals, so humans out of the loop requires yolo or read-only. Never for secrets/privileged entry (desktop/SKILL.md §3).

## Verified against

Flags checked against `docs-corpus/harnesses/help-*.md` (2026-09-02 captures; pi 2026-09-02,
opencode 2026-11-06; `--no-mcp` confirmed by user 2026-11-17) and `docs-corpus/herdr-desktop/hc-skill.md`.
Captures go stale — if a seat misbehaves after a harness upgrade, diff against a fresh
`--help` before blaming the model (herdr-lab router rule 9).

## Known issues

- **`claude-lean`**: on a first launch in a project dir, Claude Code shows its workspace-trust dialog and `first_message.sent` stays false. Clear it with `hc read <seat>` then `hc keys <seat> down enter`, deliver the task with `hc send <seat> "…"`, and verify with `hc read`. Observed 2026-11-17 (Claude Code 2.1.326). Not specific to this template — any claude seat behaves this way.

## Not in this folder, deliberately

- **Yolo-by-default seats.** Heavy templates ship in the *intermediate* posture; unattended fleets opt into yolo per seat, explicitly. Nothing here approves itself.
- **Claude `--bare`.** Breaks OAuth/keychain auth; `--safe-mode` achieves the leanness without touching auth.
- **Machine-local providers.** `pi-*` pins the author's Ollama setup; edit the `command:` line for yours. Nothing here phones home.

## Adding your own

Copy any file, rename, adjust `name` + `command` + body, then
`bin/install-templates.sh --only <yours>`. Keep read-only as the default posture; if a
template can act unattended-and-unapproved, say so in `description` — `hc templates`
prints it to every delegating agent.
