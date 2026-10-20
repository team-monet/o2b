# O2B Framework — Master Plan

Governing parent: [BRAIN.md](../BRAIN.md)

Read this plan before adding a framework capability, changing shared structure, or planning maintenance and validation. The framework is deliberately small: readable Markdown and explicit ownership come first; machinery enters only when observed use justifies it.

## Boundaries

The shared repository owns structure and operating guides. A personal repository built from its history owns the snapshot, populated principles, leads, situation pages and their rules, agent definitions, skills, personal-life content, projects, autopilot operations, knowledge, work, and source records. Shared updates must not embed or overwrite personal content.

The framework must be usable by someone starting their own brain without the maintainer's private files, accounts, installed skills, or previous conversations. Feature guides supply enough instructions and generic examples to establish a personal instance. Actual workstreams, inbox entries, migration inventories, and runtime evidence belong to that instance.

Guidance is anchored to situations. Principles remain under root `guidance/PRINCIPLES.md` with explicit applicability, except those that apply only while working as particular leads, which live in their pages under `guidance/leads/` or in principle sets under `guidance/principles/`. Shared situation pages live under root `guidance/`; project-only ones live under `projects/<project>/guidance/`. Each scope owns its index, and BRAIN reads a project's index on entering it. Shared loading and authoring conventions live once in the root guidance guides.

Existing project trackers and external sources retain authority until their owners explicitly transfer it. Links preserve that boundary; copying changing state does not.

## Design constraints

- Hold only what someone will need to read. Git is the brain's history, so no structure may accumulate logs, archives, or replaced versions kept just for the record.
- Give each instruction, fact, and work item one authoritative home.
- Keep the root for what the owner reads or rules on, and put agents' working material under `agent/`. What an agent prepares for the owner stays with its owner and reaches the owner through the snapshot, not through a separate folder.
- Keep the route from `BRAIN.md` to the applicable guide shallow and explicit.
- Minimize the total context needed to find the right information and act correctly. Unnecessary reading consumes limited context; a shorter entry is useful only if it preserves efficient discovery.
- Author READMEs according to the [README principles](#readme-principles).
- Anchor the agent to its situation: principles, the chosen lead's page, and BRAIN's work habits are always on, the situation index is read at startup, and a situation's page is read before acting, linking how, who, and what is known. Every session notes its project's open work and knowledge listings without resuming anything unasked. Keep maintenance instructions off the routine startup path.
- Scope guidance by where it applies, not where it was learned: shared by default, and project-scoped only when it names something that exists in that project alone. Read shared and project pages together when both match.
- Use readable files and existing tools before adding schemas, indexes, adapters, or services.
- Make the habits that keep the brain useful, such as capturing findings, settling work, and writing knowledge, one-step actions tied to a named moment. Add machinery only when such a habit is observed not to happen in real use.
- Keep guidance, knowledge, and work state distinct. Content does not become an instruction merely because an agent retrieves it.
- Make active guidance understandable: readable separation, explicit authority and applicability, and known reasons rather than source IDs or copied storage labels. Preserve admitted guidance whose reason is not yet recorded without inventing one.
- Preserve current source instructions and version context so external sources can keep operating over time.
- Treat privacy, recovery, concurrent editing, and runtime delivery as operational claims requiring tested mechanisms.
- Prefer the smallest coherent change that improves the human or agent experience. A directory alone does not implement a capability.

## README principles

A README helps an agent choose its next source or action. Keep the scope, read trigger, governing parent where applicable, authoritative homes, and local constraints needed to navigate correctly. Give each supporting link a clear task or action cue.

Include a paragraph only if omitting it would change a relevant local decision or make the needed source harder to find. Assume the agent knows general authoring and tool use. Link to an established standard instead of explaining it again; state only local requirements beyond that standard. Do not repeat guidance already supplied by BRAIN or the governing parent.

Setup, installation, migration, and other detailed procedures belong in linked documents read when performing that action. Optional background and historical explanation stay off the entry path. A shorter README must still provide enough context to choose correctly.

## Current areas

| Area | Owns |
|---|---|
| `SNAPSHOT.md` | The owner's page: what needs them now, from any area, built from the skeleton in the [Work guide](work/README.md#snapshot); populated content stays personal |
| [Personal](../personal/README.md) | The owner's own life outside projects: the same parts as a project home plus household notes and inner-circle people pages; populated content stays personal |
| [Projects](../projects/README.md) | Project-specific domain knowledge, procedures, decisions, evidence, and continuation context |
| [Autopilot](../autopilot/README.md) | Operations that run on their own toward a Mission the owner gave, and their progress; populated operations stay personal |
| [Guidance](../guidance/README.md) | Principles, leads, situation pages, and the conventions for scoping and admitting them |
| `agent/` | Agents' working material, below |
| [Agents](agents/README.md) | Agent definition conventions and discovery; populated definitions stay personal |
| [Skills](skills/README.md) | Agent skills with their scripts and dependencies, authoring, and whole-root discovery links; populated skills stay private |
| [Knowledge](knowledge/README.md) | Knowledge note conventions for project and cross-project knowledge |
| [Work](work/README.md) | Workstream, agent-inbox, and handoff conventions, work ownership, and the snapshot skeleton; populated records stay personal |
| [Sources](sources/README.md) | Relationships with external knowledge systems and source ownership changes |
| [Operations](operations/README.md) | Installation, updates, runtime delivery, access, recovery, concurrency, and derived tools |

These areas are starting responsibilities, not a promise of a fixed taxonomy or future feature set.

## Change process

1. Identify the concrete task or observed failure and the owner of the affected material.
2. Read the governing chain and current sources. Decide whether an existing area already owns the need.
3. Make the smallest coherent change. Preserve personal content and compatibility, or state the required migration clearly.
4. Update the owning guide and its discovery links together. When guidance scope changes, update its owning principle or stage entry and each affected rule's direct or inherited applicability. Link project stage indexes from their project README.
5. Validate at the level of the claim: inspect links and ownership for documentation, exercise behaviour for guidance delivery, and test real mechanisms for operational protection.

Keep untested claims visible as unvalidated. Record detailed execution work in its project or tracker rather than turning this plan into a work log.
