---
name: herdr-lab
description: 'Router for the herdr-lab workflow family. Use when the user mentions Herdr, asks to delegate to another coding agent, run parallel agents / batches, run sudo or another privileged/secret-entry command safely in a managed pane, check another agent''s quota/usage, or brainstorm/debate with other agents (bidirectional critique rounds, devil''s advocate, second opinion). Reads the intent and routes to the matching sub-skill: delegation/SKILL.md (herdr-lab-delegation) or brainstorm/SKILL.md (herdr-lab-brainstorm). Each sub-skill carries its own frontmatter and is independently symlinkable; docs-corpus and bin are shared at the herdr-lab root and reached via per-sub-skill relative symlinks.'
version: 0.24.0
updated: "2026-10-14"
triggers:
  - user mentions Herdr by name
requires:
  - herdr >= 0.8.0
  - pi-herdr plugin installed and active (HERDR_PANE_ID set)
  - HERDR_ENV=1
---

# herdr-lab — router (master)

This file routes; it does not perform. The workflow is split into two independently triggerable sub-skills, each with its own frontmatter and trigger set (matching versions 0.24.0 across master + sub-skills):

| User intent | Sub-skill | What it covers |
| 