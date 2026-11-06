# opencode — harness card

Written by the herdr-lab induction sub-skill. `TODO` means not yet established.

| Field | Value |
|:------|:------|
| Kind / executable | `opencode` / `opencode` |
| Version captured | 1.19.3 (2026-11-06) |
| herdr integration | not installed (screen detection only) |
| Live test | `fail-no-settle` (2026-11-06, model `Big Pickle`, opencode's default) |
| List models | `opencode models [provider]` |
| Model flag | `-m provider/model` |
| Permission: intermediate | none in `--help` |
| Permission: full auto | `--auto` |
| Permission: read-only | none in `--help` |
| Quota surface | TODO |
| Login check | `opencode auth list` (read-only) |
| Transcript reader (herdr-convo) | TODO (not tested) |
| Online docs source | `opencode.ai/docs/<page>.md`; last ingested 2026-09-02, not refreshed by this run |

## Live-test notes

- Seat started and accepted the prompt, and the exact token came back.
- The seat then stayed `working` past 3.5 minutes, repeating compaction at about 297K tokens (149%), so it was interrupted and closed. herdr's `working` state was correct.
- Its own compaction summary quoted a "continue if there are next steps" directive that the test did not send.
- At test time: 0 stored credentials, 10 models listed, all `opencode/*` free models and no `ollama` provider. This says nothing about `opencode+ollama-cloud`.

## Open questions

- Why context reached 149% on a one-line prompt in an empty directory. Suspected, unverified: tool definitions from the `mcp` block in `opencode.jsonc`. Compare with a run using `--pure`, or with that block removed.
- Where the "continue" directive came from. No `plugin` or `instructions` key is set in `opencode.jsonc`, so it may be opencode's own post-compaction message. Unverified.
- `--auto` is new since the 2026-09-02 capture, and delegation §4.5 still lists opencode as config-driven only. The corpus says `opencode.json` `permission` settings cover the other modes; recheck against current docs.
- Online docs were not refreshed: `curl` to `opencode.ai` was denied at the permission prompt twice.
