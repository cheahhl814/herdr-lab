# herdr-lab-induction

**Skill name**: `herdr-lab-induction` · **Version**: 0.28.2 · **Type**: agent skill (workflow-only)

The onboarding step of the [herdr-lab](https://github.com/cheahhl814/herdr-lab) family: introduces the primary harness to an installed secondary harness, then proves the harness works. Running it again on a known harness refreshes its corpus entry.

> This is a **sub-skill**. It has its own frontmatter and can be symlinked on its own, but its live test follows [`herdr-lab-delegation`](../delegation/README.md) §1-§3.

## When it fires

```text
- introduce / onboard / induct a new harness or coding agent to herdr-lab
- add a new harness to the docs-corpus
- refresh / re-capture the docs-corpus for a harness
- check whether a harness actually works through herdr
```

## What it produces

| Output | Purpose |
|:-------|:--------|
| `docs-corpus/harnesses/help-<kind>.md` | Verbatim `--help`, stamped with date and version, machine details scrubbed |
| `docs-corpus/harnesses/<kind>-online-docs/` | Official docs, via the optional `docs-ingest` skill |
| `docs-corpus/harnesses/<kind>-card.md` | The facts delegation needs: flags, quota surface, login check, live-test verdict |

## Capture script

```bash
python3 bin/herdr-induct.py <kind>   # capture --help and version, create the card skeleton
python3 bin/test_herdr_induct.py     # self-check
```

The script refuses a kind herdr cannot start or that isn't installed, and it never overwrites an existing card.

## Guarantees

- One harness per run, and only one that is already installed.
- The live test is an interactive herdr seat. Only `--help`, `--version` and a read-only login check run non-interactively.
- Permission and model flags on a card must appear in the live `--help`.
- Nothing is committed, and credentials, provider config and `routing.json` are left alone.

## Install

Symlink next to the other sub-skills, keeping the name equal to the frontmatter name:

```bash
ln -sf "$(pwd)/herdr-lab/induction" ~/.agents/skills/herdr-lab-induction
```

`docs-ingest` is optional: https://github.com/cheahhl814/docs-ingest

## License

MIT, see [LICENSE](../LICENSE).
