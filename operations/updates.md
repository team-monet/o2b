# Framework Updates

**Governing parent:** [Operations guide](README.md).
**Scope:** Repositories with shared framework history and independent personal content. This is a procedure, not authorization to commit or publish.

## Ownership

The framework repository owns `BRAIN.md`, `MASTER-PLAN.md`, the root `README.md`, feature guides, generic examples and validation scenarios, operational tools such as [auto-sync](sync.md), and this procedure. The personal repository owns populated principles, shared and project stage indexes and rules, project indexes and content, notes, workstreams, inboxes, source agreements, and runtime records. Framework contributions must not introduce files at personal-content paths. A structural change that moves personal content needs an explicit migration instruction; Git merges text, not meaning.

Principles remain under root `guidance/PRINCIPLES.md` with explicit applicability. Shared stage rules and their index live under root `guidance/`; project-specific rules and their index live under `projects/<project>/guidance/`. Project READMEs link to their indexes, and the common loading and authoring guides remain at the root. Populated capability bundles belong to the personal brain or their owning project repository; the framework owns only the capability guide.

The development checkout's `origin` is the framework repository. The live checkout's `origin` is the independent private personal repository, and its `upstream` is the framework repository. Both repositories share their initial framework history. A GitHub fork relationship is unnecessary.

Use a local push-disabled `upstream` remote in personal and review checkouts to reduce accidental publication of personal history. This is a convenience guard, not access control: someone with credentials can change it or push to another URL.

## Prepare a framework update

1. In development, inspect the change and its migration impact. Commit and publish the framework change when authorized. Keep actual personal content out of the framework commit.
2. Before updating the live brain, inspect its working tree and compare its branch with personal `origin/main`. Preserve uncommitted or unpushed work explicitly; do not auto-stash, reset, discard, or bypass it. If another session is writing to the live brain, coordinate a pause before the final update.
3. Clone the personal repository into a disposable review directory outside the live brain. Add the framework repository as `upstream` there and fetch it. A clone does not inherit remote definitions from the live checkout.
4. Merge the chosen upstream revision into the review checkout. For the current upstream main, the relevant commands in that checkout are:

   ```sh
   git fetch upstream
   git merge --no-edit upstream/main
   ```

   Stop and resolve conflicts in the review checkout. Do not expose an unfinished merge to live sessions.
5. Compare the merge against the personal revision before the merge. Check changed guides and links, required personal-content migrations, and preservation of principles, rules, projects, notes, and work. Apply migration steps in the review checkout and commit them when authorized. A clean merge alone is not semantic validation.
6. Publish the reviewed result to the personal repository's main branch when authorized. If personal main has advanced, fetch, reconcile, and recheck before retrying. Do not force-push.
7. In the live checkout, verify it is still clean, on main, and has no unpushed work. Then adopt the published result:

   ```sh
   git pull --ff-only origin main
   ```

   A divergent history must be reconciled in a review checkout; do not bypass the fast-forward requirement. A live checkout running [auto-sync](sync.md) adopts the published result on its next run instead; it merges only when the merge is clean and leaves conflicts to a person. Recheck the live revision and changed guidance after updating. Active agents may retain earlier guidance in context; have them refresh it, and use a fresh session for startup-delivery checks.

## Adopt workstreams and the agent inbox

This is an additive convention; no bulk move of existing plans, trackers, or inbox entries is required. Apply it in the disposable personal review checkout:

1. Read the incoming [Work guide](../work/README.md) and identify the owner of each actual work item. Keep existing project plans and external trackers authoritative; do not copy their changing open sets into new workstreams.
2. Create a workstream only for authorized work whose execution state the brain owns. Use the guide's format and correct project or brain-owned home; link project records from their project README. Preserve prior work records until their owner explicitly settles or transfers them.
3. Retain existing `Pending`/`Resolved` inboxes and all entries. The old `work/README.md#inbox` link still works. Assign a stable label to an unlabelled entry when it is next updated or disposed; do not renumber existing labels. Create a project inbox only when a finding belongs there; leave unrelated findings in their existing scope unless their owner transfers them.
4. Check governing links, status against the open set, item-label uniqueness, and preservation of untouched content. Exercise the relevant [validation scenarios](../work/validation.md) in isolation and record what was actually observed. No simultaneous-writer or automatic-enforcement claim follows from adopting these files.

Publish and install the reviewed result through the update sequence above. Personal work records and validation evidence stay out of the shared framework commit.

## Adopt intent-based startup and guidance authoring

The guidance reader remains at `guidance/README.md`; its maintenance instructions move to `guidance/authoring.md`. Existing principles, stages, rules, workstreams, and inbox entries keep their paths and meaning. Adopt BRAIN and both guidance files together so the maintenance route remains available. BRAIN selects relevant knowledge directly for a clear task, or open work followed by knowledge for a continuation request; there is no routine startup scan of old work or inboxes.

In the review checkout, check any personal startup instructions or procedures that require such a scan for a conflict with the new route. Preserve personal authority and resolve conflicts explicitly. Verify links and exercise the clear-task, continuation, and guidance-maintenance cases in the [validation scenarios](../work/validation.md). Record runtime observations separately from static checks, then publish and install through the update sequence above.

## Adopt portable capability conventions

This adds an on-demand [capability guide](../capabilities/README.md); existing personal files remain in place. Adopt the guide and its discovery links together in the personal review checkout. No capability, runtime adapter, or dependency is installed by this framework update.

For each selected personal transfer, establish the current owner and portable source, follow support and setup dependencies, and choose the home described in the guide. Preserve the original source until the selected bundle and incoming references are verified. Keep project repositories authoritative where they own the capability; do not make a second maintained copy in the brain. Update machine-specific references to a verified owning route and recreate host adapters from that source.

Check links and source preservation, then exercise the guide's isolated transfer validation. Keep actual inventories, ownership decisions, and execution evidence personal. A static check does not establish runtime availability; publish and install only through the reviewed update sequence above.

<a id="migrate-project-guidance-into-central-guidance"></a>

## Adopt shared and project stage discovery

This replaces the earlier all-central stage layout. The old migration anchor above remains for existing links; the procedure below governs the current layout. Principles and preferences keep their root home. Apply the change in an isolated personal review checkout:

1. Inventory current rules and stage indexes before moving anything. Record each rule's moment, instruction, applicability, authority, origin, and reason. Keep the source available until preservation is verified.
2. Retain shared rules under root `guidance/stages/`. Move each project-only rule to `projects/<project>/guidance/stages/`, splitting mixed stage files by applicability. A rule shared by a named subset of projects can remain at the root with that scope stated. Preserve rule meaning and support-link destinations; do not copy the shared rule into each project.
3. Rebuild root `guidance/STAGES.md` from shared stages only. Create each affected project's `guidance/STAGES.md` from its local stages. Keep unique destinations within each index, and retain the recognizable moment and applicability. Link each project index from its README and repair active references to moved files.
4. Adopt BRAIN, the common guidance reader/authoring guide, and Projects guide together. Shared stages load at startup; project stages load when that project is entered. Matching shared and local rules both apply; a local file is not permission to override a shared constraint. Resolve outdated personal instructions that still demand a single central index.
5. Compare all rule tuples with the inventory, verify governing and support links, and check every rule file appears in its owning index. Remove the old active copies only after those checks pass. Preserve historical evidence as historical and identify the earlier layout as superseded in current operating records.
6. Exercise discovery in an isolated setup: a shared-only action, a project-only action, an action matching both indexes, and a switch to another project. Observe which indexes and files a fresh actor reads before action. Link checks alone do not establish runtime delivery. Record observed results and limits personally.

Publish and install through the reviewed update sequence above when authorized. A request to commit locally does not authorize publication. For a local-only adoption, commit existing authorized personal work first, merge the framework and migrate in a disposable local clone, then fast-forward the clean tracked live checkout to the validated local result. Preserve unrelated untracked files and do not discard pre-existing work.

## First installation

Create an empty independent private personal repository. Clone the framework history to the live location, rename its original remote to `upstream`, add the personal repository as `origin`, and push the shared main branch to personal origin. Configure the live main branch to track `origin/main`. Keep upstream fetching enabled but set its push URL to a deliberately invalid local path. Add personal content only after this separation is in place.

Do not initialize both repositories with separate root commits: that would lose the shared ancestry used by ordinary merges. Do not mirror-push a personal repository to the framework.

## Recovery and evidence

Git history preserves committed revisions; it does not back up uncommitted files or establish a complete recovery system. Prefer a reviewed corrective commit or revert over rewriting shared history. Record real installation details and validation results in personal operation records rather than adding personal paths or live state to this shared procedure.
