# gitignore

A curated repo that merges official templates from [github/gitignore](https://github.com/github/gitignore). Current combination: **Python + Unity + User**.

## Files

| File | Description |
|---|---|
| `.gitignore` | The repo's output: merged `Section 1: Python` / `Section 2: Unity` / `Section 3: User`; upstream banners carry a `?raw=true` source link; grab it directly for your own projects |
| `user.gitignore` | Repo-local hand-maintained personal ignores, embedded as `Section 3: User`; edits here survive upstream sync |
| `scripts/merge_gitignores.py` | Merge script: fetches the official Python / Unity templates from `main`, appends the local `user.gitignore`, and regenerates `.gitignore` |
| `.github/workflows/sync-upstream.yml` | GitHub Action that keeps `.gitignore` in sync (daily cron + fork-sync push trigger) |

## Auto sync

- **Triggers**: `schedule` once a day (21:17 UTC) + manual `workflow_dispatch`
- **Flow**: fetch official `Python.gitignore` / `Unity.gitignore` → run the merge script (appends the repo-local `user.gitignore`) → compare against the committed file
- Change detection is content-based: upstream commits that do not touch these two files produce no empty commit; any real change is committed and pushed as `agent`
- The cron pulls upstream content directly via raw.githubusercontent.com, so it works regardless of fork sync; this fork's `master` shares no history with upstream, so GitHub "Sync fork" cannot update it anyway
- Scheduled workflows only run from the repository's **default branch**: keep `master` as default in Settings → Branches, or the cron will silently stop

## Run manually

```bash
python scripts/merge_gitignores.py          # regenerate .gitignore
python scripts/merge_gitignores.py --check  # check only, exit 1 on difference
```

## Notes

- GitHub disables scheduled workflows after 60 days of repository inactivity; re-enable manually if that happens
- The workflow declares `permissions: contents: write`; if org/repo policy restricts workflows to read-only, allow read/write under Settings → Actions → General → Workflow permissions
