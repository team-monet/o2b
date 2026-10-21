# Framework Updates

**Governing parent:** [Operations guide](README.md).
**Scope:** Repositories with shared framework history and independent personal content. This is a procedure, not authorization to commit or publish.

## Ownership

The framework repository owns `BRAIN.md`, the [master plan](../MASTER-PLAN.md), `.github/README.md`, feature guides, generic examples and validation scenarios, operational tools such as [auto-sync](sync.md), and this procedure. The personal repository owns populated principles, leads, shared and project stage indexes and rules, project indexes and content, autopilot operations, the snapshot, notes, workstreams, inboxes, agent definitions, skills, personal-life content under `personal/` apart from its guide, source agreements, and runtime records. Framework contributions must not introduce files at personal-content paths. A structural change that moves personal content needs an explicit migration instruction; Git merges text, not meaning.

Principles remain under root `guidance/PRINCIPLES.md` with explicit applicability, except those that apply only while working as particular leads, which live in their pages under `guidance/leads/` or in principle sets under `guidance/principles/`. Shared stage rules and their index live under root `guidance/`; project-specific rules and their index live under `projects/<project>/guidance/`. Project READMEs link to their indexes, and the common loading and authoring guides remain at the root. Populated skills belong to the personal brain or their owning project repository; the framework owns only the skills guide.

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

1. Rewrite the index in the [projects guide](../../projects/README.md#project-index)'s shape: Names, Remote, and Path columns. Take each remote from the repository's fetch URL and each path from where the project actually lives.
2. Replace any identifier an agent cannot observe, such as a label from an earlier system, with the real remote or path.
3. From each project's directory, check that its row matches by remote or path, and that a task naming the project matches by Names.

Links from a project README to its workstreams and inbox are no longer required; keep or remove them. Publish and install through the reviewed update sequence above.

## Adopt project knowledge folders

Project knowledge now lives in `projects/<project>/knowledge/` in the [Knowledge guide](../knowledge/README.md)'s note shape. In the personal review checkout, move project-specific notes out of root `knowledge/` into their projects. Give an existing note its summary first line and source when it is next touched; no bulk rewrite is needed. Publish and install through the reviewed update sequence above.

## Adopt situation pages and scoping rules

Stage files become situation pages, and the [authoring guide](../../guidance/authoring.md) adds scope-and-admission rules. Existing pages stay valid: their scoped rules are what must hold, and How, Who, and Known sections are added when there is something to link. In the personal review checkout, or as ordinary maintenance afterwards, one situation at a time with the owner:

1. Re-scope guidance learned in one project but applying everywhere, and merge near-copies of the same rule across shared and project pages.
2. Move steps, sequences, rosters, and tool versions out of rules into the skills that carry them, and move approval gates out of skills into rules.
3. Rename project situations that duplicate a shared situation under another name.

Publish and install through the reviewed update sequence above.

## Adopt the personal area

Personal-life material now has its own home under the [Personal guide](../../personal/README.md). In the personal review checkout, move material about the owner's own life out of project and knowledge homes into `personal/`, one item at a time with the owner; career, investing, and other bodies of work stay or become projects. Publish and install through the reviewed update sequence above.

## Adopt agent definitions

Agent definitions now live in the brain under the [Agents guide](../agents/README.md). Move each personal definition from a runtime's agent folder into `agents/`, keeping a recoverable copy until the move is verified, and rewrite any reference to an earlier memory system or tool. State each definition's boundary. Then run [runtime sync](skill-discovery.md#runtime-sync) and check in a fresh session that the runtime lists them. Publish and install through the reviewed update sequence above.

## Adopt runtime sync

Auto-sync now ends each completed run with [runtime sync](skill-discovery.md#runtime-sync), which links or generates every installed runtime's skills and agent definitions from the brain, so publishing this update changes each machine's runtimes within one sync interval. Before publishing to personal main, preview it on every machine that runs auto-sync: from the review checkout, run `python3 agent/operations/runtime-sync/runtime_sync.py --brain <live brain> --dry-run` and read what it would change. Move skills or agent definitions a runtime holds that are not yet in the brain into it first; a same-named file the tool did not generate is renamed `<name>.<suffix>.bak-o2b-<date>`, not lost. After publishing, read the first run's lines in each machine's sync log and check each runtime in a fresh session. Publish and install through the reviewed update sequence above.

## Adopt the gate hook

The [gate hook](gate-hook.md) hands a stage page to a Claude Code agent before a command the page names in `before:`. It does nothing until pages name commands and a machine installs it, but once the update arrives, runtime sync reports each machine whose Claude Code does not run it. After publishing:

1. With the owner, name the commands on the pages for situations that are commands, such as committing changes or merging a pull request, and check each with `--explain`.
2. On every machine that runs Claude Code, install the hook with the owner's go, and check it in a fresh session as the gate-hook guide describes.

Publish and install through the reviewed update sequence above.

## Adopt the owner's root and the agent folder

The root now holds only what the owner reads or rules on: `SNAPSHOT.md`, `personal/`, `projects/`, `autopilot/`, `guidance/`, and `BRAIN.md`. Agents' working material lives under `agent/`, the capability guide is folded into the [Skills guide](../skills/README.md), the snapshot moves to the root and covers everything that needs the owner, and the framework README moves to `.github/README.md`. Apply it in the personal review checkout:

1. Move `agents/`, `skills/`, `knowledge/`, `operations/`, `sources/`, and `work/`, with their personal content, under `agent/`. Move personal workstreams and inbox entries from there into `personal/workstreams/` and `personal/INBOX.md`; `agent/work/` keeps only cross-project work. Move anything under `capabilities/` into the skill that uses it, or to the project or operation that owns it, and remove the folder.
2. Move autonomous operations kept elsewhere, such as a `missions/` folder, to `autopilot/<name>/`, as the [Autopilot guide](../../autopilot/README.md) describes, and put each operation's path in its project's row in `projects/INDEX.md`.
3. Move `personal/snapshot.md` to `SNAPSHOT.md` and add the views from the [snapshot skeleton](../work/README.md#snapshot), keeping the owner's written sections. Point any briefing at the new page, and set `for_you` on the files that are waiting on the owner now, as `BRAIN.md`'s habit "Hand things to the owner" says.
4. Remove `history/` folders and other copies kept for the record; Git keeps them. Make records that cite them cite the commit instead.
5. Rewrite links, `projects/INDEX.md` paths, and Obsidian Bases folder filters into the moved folders, and any outside reference to an old path, such as scheduled jobs, launchers, and runtime instructions.
6. Auto-sync adopts a published result on its next run, and its installed job names the old script path, so it fails silently once `operations/` moves. Before publishing to personal main, on every machine that runs auto-sync, pause the other writers to the live brain, such as scheduled jobs and agent sessions, let auto-sync commit and push their pending work, then stop it and remove its job (the commands in [sync.md](sync.md#install), or disable the cron or systemd entry) so a login cannot reload it. After publishing, on each machine: confirm the live checkout is clean, run `git pull --ff-only origin main`, re-point the discovery links as [skill discovery setup](skill-discovery.md) describes and the paused writers to the new paths, rerun `agent/operations/sync/install-macos.sh` (or reschedule `agent/operations/sync/sync.sh`), confirm its first run in the log, and resume the writers.

Publish and install through the reviewed update sequence above.

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

## Adopt the narrower `for_you` test

`BRAIN.md`'s habit "Hand things to the owner" now sets `for_you` only while something is waiting on the owner now, and lets any agent take an item that blocks nothing out of a file's `for_you`, keeping it findable through an inbox entry. The update does not re-evaluate flags set under the earlier test, which covered anything the owner needed to read, decide, or act on. Apply it in the disposable personal review checkout:

1. List every file carrying `for_you`. For each item its value names, read the entry or file behind it, and keep the item only if work cannot move, or a cost keeps running, until the owner takes a step only they may take or decide.
2. Take every other item out of its file's `for_you`, and remove the property when no item is left. Leave each item's inbox entry in place; for a file with no entry, such as a report or a design, first add a dated entry linking it to its owner's inbox, chosen as `BRAIN.md`'s habit "Capture findings" chooses one, so a session working on its subject still finds it at startup.
3. Resolve with the owner any personal instruction that still uses the earlier test, such as an operating convention or a skill that flags whatever needs the owner's decision.

Publish and install through the reviewed update sequence above.

## Adopt leads

Leads are optional: a brain without `guidance/LEADS.md` works as before. To adopt them, work with the owner in the disposable personal review checkout, as [Maintain guidance](../../guidance/authoring.md#leads) describes:

1. Find with the owner which leads they need, then write the index and a page for each, fitting each to them as [Fit a lead to its owner](../../guidance/authoring.md#fit-a-lead-to-its-owner) describes.
2. Move each principle that applies only while working as particular leads from `PRINCIPLES.md` to the home Maintain guidance gives it, keeping its wording, authority, origin, and reason. Leave in `PRINCIPLES.md` every principle that workers, autopilot runs, or sessions without a lead also need, such as one scoped to a project or an operation.
3. Name the leads in the applicability of any rule that would be wrong for the others.
4. Move a lead kept in a runtime's own configuration, such as a Claude Code output style, into its page, and leave that configuration pointing at the page.
5. Resolve with the owner any personal instruction that conflicts with working as several leads, such as a single lead defined in an operating convention, or a rule that keeps a change of mode in the same session.
6. Check in fresh sessions that the agent chooses a lead, names it in its first reply, and follows its page; that it hands a change of mode to a new session through a brief; and that a session started from that brief works as the lead it names.

Publish and install through the reviewed update sequence above.

## Adopt the fit review

The [fit review](fit-review.md) is optional: a brain without one works as before, and leads are not required for it. To adopt it, with the owner:

1. Agree which runtimes' sessions it may read and on which machines, who runs it and on what schedule, where its proposals reach them, and the numbers [Review fit across sessions](../../guidance/authoring.md#review-fit-across-sessions) leaves to them.
2. Create the operation as the fit-review guide describes, with the owner's settings on the situation page its Boundaries link and each runtime's first last-read time where the owner says.
3. Run the reader on each runtime and read its summary, then check one run end to end on a past window where a correction is known to recur, writing no records, so that the check counts toward nothing.

Publish and install through the reviewed update sequence above.

## First installation

Create an empty independent private personal repository. Clone the framework history to the live location, rename its original remote to `upstream`, add the personal repository as `origin`, and push the shared main branch to personal origin. Configure the live main branch to track `origin/main`. Keep upstream fetching enabled but set its push URL to a deliberately invalid local path. Add personal content only after this separation is in place.

Do not initialize both repositories with separate root commits: that would lose the shared ancestry used by ordinary merges. Do not mirror-push a personal repository to the framework.

## Recovery and evidence

Git history preserves committed revisions; it does not back up uncommitted files or establish a complete recovery system. Prefer a reviewed corrective commit or revert over rewriting shared history. Record real installation details and validation results in personal operation records rather than adding personal paths or live state to this shared procedure.
