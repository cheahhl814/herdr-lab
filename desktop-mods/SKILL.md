---
name: herdr-lab-desktop-mods
description: herdr-lab desktop mods and layouts — change the Herdr desktop app's own interface (herdr-app) by editing files under ~/.config/herdr-app: write or clone a mod (gpui-kit JavaScript panel), clone a layout, rebind keys, add a program entry, install a community layout/mod from herdr.dev, or port an old herdr-CLI plugin idea (usage/quota meters, status widgets) to a mod. Enforces the check → status → shot verification loop and the clone-before-edit rule. Use when the user asks to customize, restyle or extend the Herdr app window; not for delegating agents (herdr-lab-desktop).
version: 0.29.0
updated: "2026-11-09"
triggers:
  - customize / restyle / extend the Herdr desktop app
  - write, clone, check or install a herdr-app mod or layout
  - port a herdr CLI plugin (usagebar, agent-quota) to the desktop app
requires:
  - herdr-app >= 0.1.13 with a running window (for status and shot)
  - ~/.config/herdr-app/AGENTS.md and herdr.d.ts (the app rewrites them on every start; they are the truth)
  - docs-corpus/herdr-desktop/ present (via the docs-corpus symlink)
---

# herdr-lab desktop mods

The app's whole interface is files in `~/.config/herdr-app` (`HERDR_APP_HOME` overrides). Edits apply live. Full guide: the installed `AGENTS.md`; offline copy `docs-corpus/herdr-desktop/installed-AGENTS.md` (may be older than the install, so prefer the live file). API types: `herdr.d.ts` (offline copy in the corpus). Never edit either, the app rewrites them. This file only orders the steps.

## Procedure

1. **Read first.** Live `~/.config/herdr-app/AGENTS.md` and `herdr.d.ts`; `herdr-app commands` for command arguments. Look at the closest shipped mod in `mods/` as the example.
2. **Do not edit shipped files.** Clone, then edit the clone (shipped layouts/mods are replaced on every start; an edited one is moved to `<name>-edited`):

   ```sh
   herdr-app do mod.clone '{"name":"workspace-status","as":"my-status"}'
   herdr-app do layout.clone '{"name":"main","as":"my-layout"}'   # also switches to it
   ```

   A cloned layout still points at the old mod: change its `content.mod` to the clone.
3. **Write the smallest mod that does the thing.** `mods/<name>/main.js` (default-exported `View` class) + `mod.json` (`{"place":"none"}` unless it should dock). Hard rules from the guide: no HTML/CSS/DOM/Node/`setTimeout`; never keep a `cx` past its callback; poll only for data, with `cx.timer.every`; animate with `.frames`/`.loop`/`.spin`, not redraw timers; use `theme()` colors; keep top-level side effects out of the module.
4. **Verify, every time:**

   ```sh
   herdr-app check ~/.config/herdr-app/mods/<name>   # exits nonzero with the exact error
   herdr-app status                                  # errors[] must be empty
   herdr-app shot /tmp/<name>.png                    # then LOOK at the picture
   ```

   `check` renders once; it does not run later async states. A working screen is not proof the edit worked (a broken save keeps the old version). Do not claim a visual check you did not make.
5. **Change only what was asked.** No edits to other mods, settings or keys.
6. **Escape hatch to tell the user about:** `ctrl-alt-shift-escape` resets layout and keys to the default.
7. **Do not automate the real display** with pointer/key tools.

## Installing someone else's layout or mod

(`herdr.dev/layouts/<owner>/<name>`, `herdr.dev/mods/<owner>/<name>`, or a GitHub folder.) Follow the guide's six steps. Agent-relevant parts:

- Read `RECIPE.md` and **every file** before copying anything. These are trusted JavaScript with command and network access.
- Tell the user up front if the mod reaches the network, runs programs (`exec`, `hc`) or reads files outside its folder, and wait for a go.
- Copy layout → `layouts/`, mods → `mods/`; leave `RECIPE.md`/`preview.png` out; never overwrite (rename on clash, including the `mod` names inside the layout).
- Merge a mod's `keys.json`; ask before replacing a key the user already uses.
- `herdr-app check` each mod; for a layout, `layout.switch {name}`. `ctrl-shift-l` switches back; deleting the files removes it.

## Porting an old CLI plugin (usagebar / agent-quota)

Checked 2026-11-09: no shipped desktop mod shows provider quota or context meters; the desktop does not load `~/.config/herdr/plugins` (manifests, `[[startup]]`, `[[events]]`, `herdr server reload-config` do not exist there). A port is a **new mod**:

- Data source: reuse what the old plugin already caches (its Go binary or cache files) and read it with `exec`/`readTextFile`, or call the provider API with `fetch`. Do not reimplement parsing the old plugin already does.
- Placement: a clone of `workspace-status` (status bar) or the `pane` header mod (per-pane meter). Per-agent identity comes from `agents()`/`panes()`; match meters to terminals by `terminal` address.
- Poll gently (`cx.timer.every` ≥ 30 s for quota); never poll live Herdr data, `render` already re-runs on it.
- Before building, search herdr.dev/gallery (`?type=mods`) and the `herdr-mod` GitHub topic for an existing one, then follow the install rules above.

## Sharing a mod

Public GitHub repo with the folder, a `RECIPE.md` written from the real files (regions, behaviour per agent status, built-from, watch-out, done-when), a `preview.png`, and the topic `herdr-mod` / `herdr-layout`. Only on the user's request.

Drift rule: do not restate the gpui-kit or `herdr` module API here; point to the `.d.ts` files.
