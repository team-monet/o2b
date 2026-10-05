# O2B Framework — Master Plan

Governing parent: [BRAIN.md](BRAIN.md)

Read this plan before adding a framework capability, changing shared structure, or planning maintenance and validation. The framework is deliberately small: readable Markdown and explicit ownership come first; machinery enters only when observed use justifies it.

## Boundaries

The shared repository owns structure and operating guides. A personal repository built from its history owns populated principles, stage rules, projects, knowledge, work, and source records. Shared updates must not embed or overwrite personal content.

The framework must be usable by someone starting their own brain without the maintainer's private files, accounts, installed skills, or previous conversations. Feature guides supply enough instructions and generic examples to establish a personal instance. Actual workstreams, inbox entries, capability migration inventories, and runtime evidence belong to that instance.

Principles remain under root `guidance/PRINCIPLES.md` with explicit applicability. Shared stage rules live under root `guidance/`; project-specific stage rules live under `projects/<project>/guidance/`. Each scope owns its stage index, and project READMEs provide the discovery links. Shared loading and authoring conventions live once in the root guidance guide.

Existing project trackers and external sources retain authority until their owners explicitly transfer it. Links preserve that boundary; copying changing state does not.

## Design constraints

- Give each instruction, fact, and work item one authoritative home.
- Keep the route from `BRAIN.md` to the applicable guide shallow and explicit.
- Minimize the total context needed to find the right information and act correctly. Unnecessary reading consumes limited context; a shorter entry is useful only if it preserves efficient discovery.
- Author READMEs according to the [README principles](#readme-principles).
- Let user intent choose the starting context: a clear task uses relevant knowledge directly; continuation starts from open work and then seeks the needed knowledge. Keep maintenance instructions off the routine startup path.
- Keep principles and shared stage rules at the root, and project stage rules with their project; preserve applicability and read shared and local rules together when both match.
- Use readable files and existing tools before adding schemas, indexes, adapters, or services.
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
| [Projects](projects/README.md) | Project-specific domain knowledge, procedures, decisions, evidence, and continuation context |
| [Knowledge](knowledge/README.md) | Reusable knowledge beyond one project |
| [Guidance](guidance/README.md) | Principles, shared stage rules, and common discovery/authoring conventions for project stage rules |
| [Work](work/README.md) | Workstream and agent-inbox conventions, work ownership, and handoffs; populated records stay personal |
| [Capabilities](capabilities/README.md) | Reusable capability ownership, discovery, dependency layout, and portable setup; populated bundles stay personal or project-owned |
| [Skills](skills/README.md) | Personal agent-skill storage, authoring, and whole-root discovery links; populated skills stay private |
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
