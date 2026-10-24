# Local GitHub backlog

This folder is the editable source for the planned GitHub milestones, epic issues, and implementation issues. Full issue descriptions live in `epics/` and `issues/`; `backlog.json` assigns each description a stable ID and phase.

## Sync

Run from any directory in the repository:

```bash
scripts/sync-backlog-to-github.sh --dry-run
scripts/sync-backlog-to-github.sh
```

The sync command requires an authenticated GitHub CLI session with permission to read repository issues and create/edit issues, labels, and milestones. It resolves the repository from the current GitHub remote by default. Set `GITHUB_REPOSITORY=owner/name` only when the checked-out repository does not identify the target.

Each generated issue body contains an invisible `backlog-id` marker. The synchronizer uses that marker to update the existing issue on later runs, so repeated syncs do not create duplicates. Epic issues receive generated child checklists after their child issues are present. `--dry-run` reports planned mutations without writing to GitHub.

Edit the Markdown source files, not the generated GitHub copy. Keep IDs stable once synced. If an issue is intentionally retired, mark it as such in the source and close it manually; do not reuse its ID for unrelated work.

## Planning conventions

- Four phases become four GitHub milestones and four `[Epic]` issues.
- Implementation issues represent coherent, reviewable end-to-end capabilities, not isolated cosmetic edits.
- Dependencies are expressed with stable backlog IDs locally and GitHub issue references after sync.
- Local issue documents are written in English to match the repository's current docs; update them with the team as scope changes.
