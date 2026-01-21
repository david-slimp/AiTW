# TODO

## Next (Do Soon)
- DONE: Install Vite (port 26472, initial app version 0.0.1), Prettier, Husky, ESLint, etc.
- DONE: Locate the root `.env` file and report variables set.
  - DONE: `.env` and `src/scripts/deploy.sh` should use npm and `deploy:prod` to rsync files.
- DONE: Ensure `public/meta.txt` ends up beside `index.html` in the built output.
  - DONE: `npm build` should copy it into `dist/`.
- DONE: Ensure `npm deploy` runs `npm build` first.
- DONE: Configure Prettier to ignore `CHANGELOG.md`.
- DONE: Ensure any `index.html` shows app title + version (e.g., `v0.0.1`) in the UI.

## Later / Pending Info
- Update docs/code/helpers with these as available:
  - GitHub URL: `https://github.com/david-slimp/AiTW`
  - Relative install path on prod server: see `.env`
  - Verify where the GitHub URL is documented (skip for now)
  - Final production URL for live gameplay: https://MinistriesForChrist.net/games/

## Ongoing Reminders
- For large/complex tasks, track progress here and mark completed items as `DONE:` in `docs/TODO.md`, then update `CHANGELOG.md`.
- Use relative paths everywhere (code/docs/helpers).
- Never remove or reduce the initial `.gitignore` (only add).
- Always use Conventional Commits, and show the proposed commit + tag messages for approval before running git commands.

## DONE
- DONE: Remember to update `CHANGELOG.md` after every change, and add this reminder in two places.
- DONE: Choose license (AGPL3) and ensure the file is `LICENSE.txt`.
- DONE: Ensure the `0.0.1` changelog date is current and properly formatted.
- DONE: GitHub URL confirmed in docs (`https://github.com/david-slimp/AiTW`).
- DONE: Production deploy path confirmed in `.env` and gameplay URL documented.

## FINALLY (Completed for v0.0.1)
- After all above, confirm and perform `git init`, commit, and tag `v0.0.1` (tag message should not repeat the version).
- Keep version numbers in sync across `CHANGELOG.md`, `package.json`, `package-lock.json`, and `public/meta.txt`.
