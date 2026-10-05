# O2B

O2B separates a shared Markdown framework from a live personal brain while preserving common Git history.

| Repository | Role |
|---|---|
| `team-monet/o2b` | Shared structure and operating guides |
| A private personal repository | Installed framework plus private guidance, projects, knowledge, and work |

The personal repository is independent rather than a GitHub fork. Its `origin` is the private repository and its `upstream` is `team-monet/o2b`. Creating it from the framework history preserves common ancestry, so framework changes can be reviewed and merged normally.

## Initialize a personal repository

Create an empty private repository, choose a live path, then start from the shared history:

```sh
live_path="/path/to/live-o2b"
personal_remote="git@github.com:account/o2b.git"
git clone git@github.com:team-monet/o2b.git "$live_path"
git -C "$live_path" remote rename origin upstream
git -C "$live_path" remote set-url --push upstream /dev/null/o2b-push-disabled
git -C "$live_path" remote add origin "$personal_remote"
git -C "$live_path" push -u origin main
```

The framework supplies `BRAIN.md`, `MASTER-PLAN.md`, and operating guides. The personal repository supplies populated `guidance/PRINCIPLES.md`, `guidance/STAGES.md`, central `guidance/stages/` rule files, `projects/INDEX.md`, project folders, knowledge notes, source records, and `work/INBOX.md`. Project folders contain no separate behavioural guidance trees. The framework must not publish populated personal files.

## Review a shared update

Adopt updates explicitly; there is no automatic sync or update script. Fetch `upstream` in a disposable checkout of the personal repository, inspect and merge a selected upstream revision there, then validate the combined personal result. Publish the reviewed personal `main` only after conflicts and content migrations are settled. Fast-forward the live checkout from personal `origin/main` only when it is clean and has no unpushed work.

The update sequence, safeguards, recovery boundary, and migration from project-local guidance are owned by [operations/updates.md](operations/updates.md). A framework release that changes personal file locations must include an explicit migration; Git cannot infer meaning.

Begin everyday use at [BRAIN.md](BRAIN.md). Framework changes follow the [master plan](MASTER-PLAN.md).
