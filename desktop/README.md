# herdr-lab-desktop

**Skill name**: `herdr-lab-desktop` · **Version**: 0.29.1 · **Type**: agent skill (workflow-only)

Delegation, parallel batches, waiting, recovery and sudo/secret entry for the Herdr desktop app, using `hc` to run agents and `herdr-app` to arrange the window. Includes the old-CLI-to-desktop command map and how brainstorm and induction transport onto `hc`.

> This is a **sub-skill** of [herdr-lab](https://github.com/cheahhl814/herdr-lab). It has its own frontmatter and can be symlinked on its own. It targets the **Herdr desktop app** (`herdr-app` + `herdr-core`/`hc`), not the older `herdr` TUI CLI; those are covered by [`herdr-lab-delegation`](../delegation/README.md).

## When it fires

```text
- user mentions Herdr desktop, herdr-app, herdr-core or hc
- delegate to another coding agent while HC_TERMINAL_ID is set
- run agents in parallel through hc
- run sudo or another secret-entry command safely under the desktop app
```

## Sources

Offline copies live in `docs-corpus/herdr-desktop/` (see its provenance table in [docs-corpus/README.md](../docs-corpus/README.md)). Live manuals: `hc --skill`, `herdr-app --skill`, `herdr-app commands`, `~/.config/herdr-app/AGENTS.md`.

## Install

```bash
ln -sf "$(pwd)/herdr-lab/desktop" ~/.agents/skills/herdr-lab-desktop
```

## License

MIT, see [LICENSE](../LICENSE).
