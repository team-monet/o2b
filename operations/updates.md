# Framework Updates

**Governing parent:** [Operations guide](README.md).
**Scope:** Repositories with shared framework history and independent personal content. This is a procedure, not authorization to commit or publish.

## Ownership

The framework repository owns `BRAIN.md`, `MASTER-PLAN.md`, the root `README.md`, feature guides, generic examples and validation scenarios, and this procedure. The personal repository owns populated principles, the central stage index and rules, project indexes and content, notes, workstreams, inboxes, source agreements, and runtime records. Framework contributions must not introduce files at personal-content paths. A structural change that moves personal content needs an explicit migration instruction; Git merges text, not meaning.

Behavioural guidance has one personal home under root `guidance/`. A project may own domain procedures and context, but not a separate principles file, stage index, rule set, or guidance tree.

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

   A divergent history must be reconciled in a review checkout; do not bypass the fast-forward requirement. Recheck the live revision and changed guidance after updating. Active agents may retain earlier guidance in context; have them refresh it, and use a fresh session for startup-delivery checks.

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

## Migrate project guidance into central guidance

Perform this migration in the disposable personal review checkout before updating the live brain:

1. Inventory every project-local principles file, stage index, stage file, and README link. Record each item's current instruction, applicability, authority, known reason, and evidence or provenance needed for audit. Do not delete the originals yet.
2. Move project principles into a clearly labelled project-scoped section of `guidance/PRINCIPLES.md`, grouped by Principles and Preferences. Retain scope, authority, and known reasons. State a shared source-admitted authority once when it applies to the whole group. Mark a missing reason as not yet recorded without changing an admitted principle's authority. Remove source IDs and storage labels from the active presentation while preserving needed provenance in a source or migration record.
3. Merge every project action moment into the central `guidance/STAGES.md`. Keep that file to its governing-parent link and a table. Give each row a recognizable moment, an applicability hint, and one unique central stage-file link. When multiple projects share a moment, use one stage file.
4. Move the rules into `guidance/stages/` and group them under explicit applicability headings. A scope heading applies to every contained rule unless a compact `Scope`, `Agent`, or `Domain` qualifier narrows it. Remove identifier and truncated-text headings; use descriptive rule titles only where they help scanning. For each rule, retain the instruction, compact **Authority** with a human-readable origin, and **Why**. Preserve admitted guidance with its existing authority when a reason is missing, mark that reason as not yet recorded, and recover it before claiming a rationale. Do not admit a new proposal without the owner's decision.
5. Remove project README links to local guidance and remove the old project guidance trees only after every item has a verified central destination. Projects keep domain knowledge, procedures, context, and work state.
6. Re-read the central index and principles as a fresh actor would. Check links, unique stage destinations, project applicability, authority, reasons, and absence of leftover active copies in project folders. Record any runtime-delivery test separately; file inspection does not establish startup compliance.

## First installation

Create an empty independent private personal repository. Clone the framework history to the live location, rename its original remote to `upstream`, add the personal repository as `origin`, and push the shared main branch to personal origin. Configure the live main branch to track `origin/main`. Keep upstream fetching enabled but set its push URL to a deliberately invalid local path. Add personal content only after this separation is in place.

Do not initialize both repositories with separate root commits: that would lose the shared ancestry used by ordinary merges. Do not mirror-push a personal repository to the framework.

## Recovery and evidence

Git history preserves committed revisions; it does not back up uncommitted files or establish a complete recovery system. Prefer a reviewed corrective commit or revert over rewriting shared history. Record real installation details and validation results in personal operation records rather than adding personal paths or live state to this shared procedure.
