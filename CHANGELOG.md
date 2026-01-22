# Changelog

## [0.0.3] - 2026-01-22
### Added
- Created per-item JSON prototype for Bible under src/content/packs/core/items/
- docs/Advancing.md for discipleship actions + verse list
- docs/puzzles.md with puzzle pattern examples
- Drafted item instance schema and v1 verse list in docs/Advancing.md
- Split core commands into modules under src/server/commands/
- Added command pack file at src/content/packs/core/commands/commands.json
- Added MOVE/GO and QUIT commands; TAKE now supports GET alias
- HELP now shows short list by default and detailed help for specific commands
- HELP tips now mention HELP <command>, and detailed help shows aliases
- Marked HELP listing of GO/QUIT as DONE in docs/TODO.md
- Marked acceptance checks (no hardcoded IDs, modular commands) as DONE in docs/TODO.md
### Changed
- Expanded docs/TODO.md with a step-by-step plan for GH Issue #1
- Marked completed GH Issue #1 steps as DONE in docs/TODO.md
- Marked PRD/MVP JSON schema doc task as DONE in docs/TODO.md
- Bumped version to 0.0.3 in package.json, package-lock.json, and public/meta.txt
- Clarified commit/tag message guidance in docs/TODO.md
- Ignored and removed local player save data from version control
- Updated content manifest to use items/ directory and loader to support per-item files
- Added design notes on item instances, inventory slots, and private tutorial rooms in PRD/MVP
- Updated MVP scope to include a public courtyard room
- Added goal-conveyance guidance and content targets to PRD
- Expanded docs/Advancing.md with discipleship commands, character traits, disciplines, actions, and “put off” list
- Expanded docs/Advancing.md with a structured NT discipleship map (core, ethics, fruit, practices, mission)
- Expanded docs/puzzles.md with cryptic, spatial, logic, meta, and cooperation puzzle types
- Added world.json for start room + initial spawns and removed hardcoded Bible instance
- Moved item instance schema from Advancing.md to PRD.md
- Help output now generated from command module metadata
- Guarded against missing room IDs in saved player state
- Disabled lifespan in dev_server.py and handled SIGQUIT for cleaner shutdowns
- dev_server.py now runs world.start/stop explicitly when lifespan is off
- Fixed circular import so HELP command dispatch works
- Added HELP command metadata so it registers and appears in help output
- Switched command registry to load modules from command packs on content reload
- Added command metadata endpoint and dynamic quick buttons in the UI
- Added modular engine philosophy and reusable command packs guidance to PRD
### Fixed
### Known Issues

## [0.0.2] - 2026-01-20
### Added
- package.json and package-lock.json with Vite/Vitest/ESLint/Prettier/Husky dev deps
- public/favicon.ico sourced from drafts/favicon.ico
### Changed
- Updated package metadata to AGPL-3.0-only and version 0.0.2 (package.json + package-lock.json)
- Added npm build/deploy/dev scripts; deploy now uses .env and requires prebuilt dist/
- Added Vite config to build from src/web into dist/ and include public assets
- Documented production URL and GitHub URL in docs/README; noted version-sync requirement in docs/TODO.md
- Documented Conventional Commits + approval requirement in docs/TODO.md
- Served meta.txt and favicon.ico from the backend; topbar now shows version from meta.txt
- Renamed player display prefix to Disciple@IP
- Reduced shutdown noise by handling CancelledError in world reload and dev server wrapper
### Fixed
### Known Issues

## [0.0.1] - 2026-01-20
### Initial Release
### Added
- Default .gitignore (NOTE: Do not delete or replace the initial .gitignore, only add to it)
- LICENSE.txt - AGPL3
- PRD.md, MVP.md, and README.md fleshed out from docs/ inputs
### Changed
- Marked changelog reminder task as DONE in docs/TODO.md
- Marked the changelog date task as DONE in docs/TODO.md
### Fixed
- Updated CHANGELOG.md date to current date (YYYY-MM-DD date format)
### Known Issues
- [see docs/TODO.md]
