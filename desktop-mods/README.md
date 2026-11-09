# herdr-lab-desktop-mods

**Skill name**: `herdr-lab-desktop-mods` · **Version**: 0.29.1 · **Type**: agent skill (workflow-only)

Customize the Herdr desktop app by editing files under `~/.config/herdr-app`: write or clone mods and layouts, install community ones, verify with `check` → `status` → `shot`, and port CLI plugin ideas such as usage meters.

> This is a **sub-skill** of [herdr-lab](https://github.com/cheahhl814/herdr-lab). It has its own frontmatter and can be symlinked on its own. It targets the **Herdr desktop app** (`herdr-app` + `herdr-core`/`hc`), not the older `herdr` TUI CLI; those are covered by [`herdr-lab-delegation`](../delegation/README.md).

## When it fires

```text
- customize / restyle / extend the Herdr desktop app
- write, clone, check or install a herdr-app mod or layout
- port a herdr CLI plugin (usagebar, agent-quota) to the desktop app
```

## Sources

Offline copies live in `docs-corpus/herdr-desktop/` (see its provenance table in [docs-corpus/README.md](../docs-corpus/README.md)). Live manuals: `hc --skill`, `herdr-app --skill`, `herdr-app commands`, `~/.config/herdr-app/AGENTS.md`.

## Install

```bash
ln -sf "$(pwd)/herdr-lab/desktop-mods" ~/.agents/skills/herdr-lab-desktop-mods
```

## License

MIT, see [LICENSE](../LICENSE).
