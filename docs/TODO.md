# TODO

## Next (Do Soon)
- GH Issue #1 (MVP modular refactor): step-by-step plan
  1) Define new content layout in `src/content/packs/core/`:
     - DONE: Rooms are per-file already; add 3 more MVP room files.
     - DONE: Create `items/` and move each item to its own JSON file.
     - DONE: Add `world.json` (or similar) for start room + initial item instances.
  2) Update manifest schema:
     - DONE: Replace `items.json` with `items_path: "items"` (directory).
     - DONE: Add optional `world_path` for start room + spawn/instances.
  3) Refactor loaders in `src/server/world.py`:
     - DONE: Load item prototypes from per-file items directory.
     - DONE: Load `world.json` to set start room and initial instances.
     - DONE: Remove hardcoded `start_room_id`, `bible_proto_id`, `bible_instance_id`.
  4) Introduce command modules:
     - DONE: Add `src/server/commands/` and a registry/dispatcher.
     - DONE: Migrate LOOK, INVENTORY, HELP, TAKE, DROP to separate modules.
     - DONE: Add command packs and auto-discovery from content packs.
     - DONE: Add GO and QUIT modules (required for MVP).
  5) Add data-driven gating + visibility:
     - Room JSON supports `description_dark` and `visibility_rules`.
     - Item JSON supports `tags` like `light_source` and inventory slots/weight.
     - Gate rules for Bible-required room (data-driven, not hardcoded).
  6) Update world state flow:
     - Enforce gate checks in GO via data rules.
     - Use visibility rules for LOOK output and item discovery.
  7) Update client UX + help text:
     - DONE: HELP lists GO/QUIT and MVP verbs.
     - DONE: Quick buttons updated from command metadata.
  8) Add MVP content:
     - 4 rooms, 2 items (Bible + Candle).
     - Bible gate + dark room using Candle.
  9) Validate acceptance:
     - DONE: No room/item IDs in code.
     - DONE: Commands modular and extendable.
     - MVP content works via JSON only.
10) Update docs + changelog:
     - DONE: PRD/MVP reflect new JSON schema (per-item files + world config).

## Later / Pending Info
- Update docs/code/helpers with these as available:
  - GitHub URL: `https://github.com/david-slimp/AiTW`
  - Relative install path on prod server: see `.env`
  - Verify where the GitHub URL is documented
  - Final production URL for live gameplay: https://MinistriesForChrist.net/games/

## Ongoing Reminders
- For large/complex tasks, track progress here and mark completed items as `DONE:` in `docs/TODO.md`, then update `CHANGELOG.md`. -- CHANGELOG does not need to mention updating TODO file.
- Use relative paths everywhere (code/docs/helpers).
- Never remove or reduce the initial `.gitignore` (only add).
- Always use Conventional Commits, and show the proposed commit + tag messages for approval before running git commands.
- When changes address a GH Issue, reference the issue in the commit body (Fixes/Refs #N) and keep the subject line specific.
- Commit/tag messages should never say "bump version"; state the substantive change and reference the issue.
- Good commit messages: subject describes the change; body includes `Fixes GH Issue #N (reason)` plus 1–3 bullets of the main changes.
- Keep version numbers in sync across `CHANGELOG.md`, `package.json`, `package-lock.json`, and `public/meta.txt`.
- Remember to update `CHANGELOG.md` and `docs/TODO.md` after every change.
