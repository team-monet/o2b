# O2B

O2B separates a shared Markdown framework from a live personal brain while preserving common Git history.

| Repository | Role |
|---|---|
| `team-monet/o2b` | Shared structure and operating guides; developed in a normal working checkout |
| private `johnonlee/o2b` | Personal brain; its live checkout is `~/.o2b` |

The personal repository is independent rather than a GitHub fork. Its `origin` is the private personal repository and its `upstream` is the shared repository. Creating it from the shared repository preserves common ancestry, so later framework changes can be reviewed and merged normally.

## Initialize the personal repository

Create the empty private `johnonlee/o2b` repository, then start from the shared history:

```sh
git clone git@github.com:team-monet/o2b.git ~/.o2b
git -C ~/.o2b remote rename origin upstream
git -C ~/.o2b remote set-url --push upstream /dev/null/o2b-push-disabled
git -C ~/.o2b remote add origin git@github.com:johnonlee/o2b.git
git -C ~/.o2b push -u origin main
```

The shared repository supplies `BRAIN.md`, `MASTER-PLAN.md`, and the section guides. The personal repository supplies private content such as `guidance/PRINCIPLES.md`, `guidance/STAGES.md`, files under `guidance/stages/`, `projects/INDEX.md`, project folders, knowledge notes, source records, and `work/INBOX.md`. The framework must not publish populated personal files.

## Review a shared update

Adopt updates explicitly; there is no automatic sync or update script. Fetch `upstream` in a disposable checkout of the personal repository, inspect and merge a selected upstream revision there, then validate the combined personal result. Publish the reviewed personal `main` only after conflicts and any content migration are settled. Fast-forward `~/.o2b` from personal `origin/main` only when the live checkout is clean and has no unpushed work.

The update sequence, safeguards, and recovery boundary are owned by [operations/updates.md](operations/updates.md). A framework release that changes personal file locations must include an explicit migration; Git cannot infer the meaning of that change.

Begin everyday use at [BRAIN.md](BRAIN.md). Framework changes follow the [master plan](MASTER-PLAN.md).
