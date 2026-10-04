# Framework Updates

**Governing parent:** [Operations guide](README.md).
**Scope:** Repositories with shared framework history and independent personal content. This is a procedure, not authorization to commit or publish.

## Ownership

The framework repository owns BRAIN.md, MASTER-PLAN.md, the root README.md, feature README.md guides, and this procedure. The personal repository owns populated principles, stage indexes and rules, project indexes and content, notes, the inbox, source agreements, and runtime records. Framework contributions must not introduce files at personal-content paths. A structural change that moves personal content needs an explicit migration instruction; Git merges text, not meaning.

The development checkout's `origin` is the framework repository. The live checkout's `origin` is the independent private personal repository, and its `upstream` is the framework repository. Both repositories share their initial framework history. A GitHub fork relationship is unnecessary.

Use a local push-disabled `upstream` remote in personal and review checkouts to reduce accidental publication of personal history. This is a convenience guard, not access control: someone with credentials can change it or push to another URL.

## Prepare a framework update

1. In development, inspect the change and its migration impact. Commit and publish the framework change when authorized. Keep actual personal content out of the framework commit.
2. Before updating the live brain, inspect its working tree and compare its branch with personal `origin/main`. Preserve any uncommitted or unpushed work explicitly; do not auto-stash, reset, discard, or bypass it. If another session is writing to the live brain, coordinate a pause before the final update.
3. Clone the personal repository into a disposable review directory outside the live brain. Add the framework repository as `upstream` there and fetch it. A clone does not inherit remote definitions from the live checkout.
4. Merge the chosen upstream revision into the review checkout. For the current upstream main, the relevant commands in that checkout are:

   ```sh
   git fetch upstream
   git merge --no-edit upstream/main
   ```

   Stop and resolve conflicts in the review checkout. Do not expose an unfinished merge to live sessions.
5. Compare the merge against the personal revision before the merge. Check changed guides and links, any required personal-content migration, and that principles, rules, notes, and work are preserved. Apply migration steps in the review checkout and commit them when authorized. A clean merge alone is not semantic validation.
6. Publish the reviewed result to the personal repository's main branch when authorized. If personal main has advanced, fetch, reconcile, and recheck before retrying. Do not force-push.
7. In the live checkout, verify it is still clean, on main, and has no unpushed work. Then adopt the published result:

   ```sh
   git pull --ff-only origin main
   ```

   A divergent history must be reconciled in a review checkout; do not bypass the fast-forward requirement. Recheck the live revision and changed guidance after updating. Active agents may retain earlier guidance in context; have them refresh it, and use a fresh session for startup-delivery checks.

## First installation

Create an empty independent private personal repository. Clone the framework history to the live location, rename its original remote to `upstream`, add the personal repository as `origin`, and push the shared main branch to personal origin. Configure the live main branch to track `origin/main`. Keep upstream fetching enabled but set its push URL to a deliberately invalid local path. Add personal content only after this separation is in place.

Do not initialize both repositories with separate root commits: that would lose the shared ancestry used by ordinary merges. Do not mirror-push a personal repository to the framework.

## Recovery and evidence

Git history preserves committed revisions; it does not back up uncommitted files or establish a complete recovery system. Prefer a reviewed corrective commit or revert over rewriting shared history. Record real installation details and validation results in personal operation records, rather than adding user paths or live state to this shared procedure.
