# Changelog

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
