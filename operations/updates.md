# Framework Updates

**Governing parent:** [Operations guide](README.md).
**Scope:** Repositories with shared framework history and independent personal content. This is a procedure, not authorization to commit or publish.

## Ownership

The framework repository owns `BRAIN.md`, `MASTER-PLAN.md`, the root `README.md`, feature guides, generic examples and validation scenarios, operational tools such as [auto-sync](sync.md), and this procedure. The personal repository owns populated principles, shared and project stage indexes and rules, project indexes and content, notes, workstreams, inboxes, agent definitions, personal-life content under `personal/` apart from its guide, source agreements, and runtime records. Framework contributions must not introduce files at personal-content paths. A structural change that moves personal content needs an explicit migration instruction; Git merges text, not meaning.

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

## Adopt open-work awareness and lean work records

BRAIN now has every session note open work and knowledge at the start and carries the everyday work habits; the [Work guide](../work/README.md) keeps only what is open and adds briefs for handoffs. This supersedes the earlier workstream, inbox, and intent-based startup adoptions. Apply it in the disposable personal review checkout:

1. For each workstream, move its `**Status:**` line into frontmatter as `status: active` or `status: paused`. Check that each resolved item's result is where it is used, then remove the `Resolved` section; remove a workstream whose status was `done`. Keep a dropped item's reason only as a knowledge note when it would stop the item being proposed again.
2. Move project work filed under `work/` into its project's `workstreams/`, creating the project home if needed.
3. In each inbox, keep pending entries as dated lines and drop the `Pending` and `Resolved` headings and the labels. Remove resolved entries once their results are where they are used.
4. Resolve with the owner any personal instruction that conflicts, such as one saying a clear task skips open work or that inboxes keep resolved entries.
5. With a fresh session, exercise the awareness, capture, incremental checkpoint, and completion-and-handoff [validation scenarios](../work/validation.md), and record what was observed.

Publish and install through the reviewed update sequence above.

## Adopt the required project index

Sessions now identify their project from `projects/INDEX.md`, so every project home needs a row an agent can match. In the personal review checkout:

1. Rewrite the index in the [projects guide](../projects/README.md#project-index)'s shape: Names, Remote, and Path columns. Take each remote from the repository's fetch URL and each path from where the project actually lives.
2. Replace any identifier an agent cannot observe, such as a label from an earlier system, with the real remote or path.
3. From each project's directory, check that its row matches by remote or path, and that a task naming the project matches by Names.

Links from a project README to its workstreams and inbox are no longer required; keep or remove them. Publish and install through the reviewed update sequence above.

## Adopt project knowledge folders

Project knowledge now lives in `projects/<project>/knowledge/` in the [Knowledge guide](../knowledge/README.md)'s note shape. In the personal review checkout, move project-specific notes out of root `knowledge/` into their projects. Give an existing note its summary first line and source when it is next touched; no bulk rewrite is needed. Publish and install through the reviewed update sequence above.

## Adopt situation pages and scoping rules

Stage files become situation pages, and the [authoring guide](../guidance/authoring.md) adds scope-and-admission rules. Existing pages stay valid: their scoped rules are what must hold, and How, Who, and Known sections are added when there is something to link. In the personal review checkout, or as ordinary maintenance afterwards, one situation at a time with the owner:

1. Re-scope guidance learned in one project but applying everywhere, and merge near-copies of the same rule across shared and project pages.
2. Move steps, sequences, rosters, and tool versions out of rules into the skills that carry them, and move approval gates out of skills into rules.
3. Rename project situations that duplicate a shared situation under another name.

Publish and install through the reviewed update sequence above.

## Adopt the personal area

Personal-life material now has its own home under the [Personal guide](../personal/README.md). In the personal review checkout, move material about the owner's own life out of project and knowledge homes into `personal/`, one item at a time with the owner; career, investing, and other bodies of work stay or become projects. Create `personal/snapshot.md` when the owner wants it. Publish and install through the reviewed update sequence above.

## Adopt agent definitions

Agent definitions now live in the brain under the [Agents guide](../agents/README.md). Move each personal definition from a runtime's agent folder into `agents/`, keeping a recoverable copy until the move is verified, and rewrite any reference to an earlier memory system or tool. State each definition's boundary. Then link the runtime folder as [skill discovery setup](skill-discovery.md#agent-definitions) describes and check in a fresh session that the runtime lists them. Publish and install through the reviewed update sequence above.

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
