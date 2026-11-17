# herdr-lab-parallel

**Skill name**: `herdr-lab-parallel` · **Version**: 0.32.0 · **Type**: agent skill (workflow-only)

Fan-out mode for the [herdr-lab](https://github.com/cheahhl814/herdr-lab) family: one task split into N independent subtasks, executed by N seats at once behind a single barrier, then merged and verified. Between delegation (heterogeneous deep tasks) and brainstorm (critique rounds).

> This is a **sub-skill**. It has its own frontmatter and can be symlinked on its own; it reads the seat/wait/verify rules from `herdr-lab-delegation` (or `herdr-lab-desktop` on the desktop edition).

## When it fires

```text
- run N agents in parallel / parallel subagents / fan this out
- batch of independent subtasks across seats
- (not for critique → herdr-lab-brainstorm; not for deep one-off tasks → herdr-lab-delegation)
```

## Install

```bash
ln -sf "$(pwd)/herdr-lab/parallel" ~/.agents/skills/herdr-lab-parallel
```

## License

MIT, see [LICENSE](../LICENSE).
