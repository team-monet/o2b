# Auto-sync

**Governing parent:** [Operations guide](README.md).
**Scope:** A live brain written from more than one machine or actor. Installing it is the owner's decision; once installed, the owner has authorized it to commit, pull, and push the live checkout.

## What it does

[sync.sh](sync/sync.sh) runs on a schedule in the live checkout. Each run:

1. Refuses a checkout without an `upstream` remote. A development checkout has none, so the shared framework is never auto-published.
2. Skips while Git is busy (a lock, merge, rebase, or cherry-pick in progress) or HEAD is detached.
3. Commits every change as `sync: <host>`. If an added line matches a common credential format, it unstages, commits nothing, and alerts.
4. Fetches the current branch from `origin` and merges it. It merges rather than rebases so commit IDs recorded in notes stay valid.
5. Pushes when the checkout is ahead.

On a merge conflict it aborts the merge, pushes nothing, and alerts once per remote revision. Local commits wait until a person merges by hand; the next run then pushes the result.

## Install

On macOS, run the installer from the live checkout. The optional argument is the interval in seconds (default 300):

```sh
operations/sync/install-macos.sh
```

It writes the per-user launchd job `local.o2b.sync`, runs it once immediately, uses the installer's `PATH`, and logs to `~/Library/Logs/o2b-sync.log`. Rerun it to change the interval. To remove it:

```sh
launchctl bootout "gui/$(id -u)/local.o2b.sync"
rm ~/Library/LaunchAgents/local.o2b.sync.plist
```

Elsewhere, schedule `sh <live-checkout>/operations/sync/sync.sh` with cron or a systemd timer. Install it on every machine that writes to the brain.

Before relying on it, run [test.sh](sync/test.sh) on the host; it exercises sync against throwaway repositories. Then confirm the first scheduled run in the log, since the scheduler's credentials and `PATH` can differ from an interactive shell.

## Limits

- It commits whatever is on disk, including an actor's unfinished edits; other machines see them within one interval. Actors may still make deliberate commits.
- The credential check matches common token formats only. Keep secrets outside the brain.
- It resolves no conflicts. A clean text merge can still combine contradictory edits in different places, so semantic conflicts need the same review as before.
- Alerts use macOS notifications when available, otherwise the log. Offline and authentication failures are logged and retried silently.
- Run one syncer per checkout. Do not also run an editor's Git plugin on a timer.
- Framework updates are still prepared in a review checkout under [updates.md](updates.md); the sync then brings the published result into the live checkout.
