# O2B Framework — Master Plan

Governing parent: [BRAIN.md](BRAIN.md)

Read this plan before adding a framework capability, changing shared structure, or planning maintenance and validation. The framework is deliberately small: readable Markdown and explicit ownership come first; machinery enters only when observed use justifies it.

## Boundaries

The shared repository owns structure and operating guides. A personal repository built from its history owns populated principles, stage rules, projects, knowledge, work, and source records. Shared updates must not embed or overwrite personal content.

The framework must be usable by someone starting their own brain without the maintainer's private files, accounts, installed skills, or previous conversations. Feature guides supply enough instructions and generic examples to establish a personal instance. Actual workstreams, inbox entries, capability migration inventories, and runtime evidence belong to that instance.

All behavioural guidance is centralized under root `guidance/`, including rules and principles that apply only to one project. Project folders own domain material and procedures without creating another guidance hierarchy.

Existing project trackers and external sources retain authority until their owners explicitly transfer it. Links preserve that boundary; copying changing state does not.

## Design constraints

- Give each instruction, fact, and work item one authoritative home.
- Keep the route from `BRAIN.md` to the applicable guide shallow and explicit.
- Let user intent choose the starting context: a clear task uses relevant knowledge directly; continuation starts from open work and then seeks the needed knowledge. Keep maintenance instructions off the routine startup path.
- Centralize principles and stage-triggered rules while preserving explicit applicability for project and actor scopes.
- Use readable files and existing tools before adding schemas, indexes, adapters, or services.
- Keep guidance, knowledge, and work state distinct. Content does not become an instruction merely because an agent retrieves it.
- Make active guidance understandable: readable separation, explicit authority and applicability, and known reasons rather than source IDs or copied storage labels. Preserve admitted guidance whose reason is not yet recorded without inventing one.
- Preserve current source instructions and version context so external sources can keep operating over time.
- Treat privacy, recovery, concurrent editing, and runtime delivery as operational claims requiring tested mechanisms.
- Prefer the smallest coherent change that improves the human or agent experience. A directory alone does not implement a capability.

## Current areas

| Area | Owns |
|---|---|
| [Projects](projects/README.md) | Project-specific domain knowledge, procedures, decisions, evidence, and continuation context |
| [Knowledge](knowledge/README.md) | Reusable knowledge beyond one project |
| [Guidance](guidance/README.md) | Central principles and stage-triggered rules across shared and project scopes |
| [Work](work/README.md) | Workstream and agent-inbox conventions, work ownership, and handoffs; populated records stay personal |
| [Sources](sources/README.md) | Relationships with external knowledge systems and source ownership changes |
| [Operations](operations/README.md) | Installation, updates, runtime delivery, access, recovery, concurrency, and derived tools |

These areas are starting responsibilities, not a promise of a fixed taxonomy or future feature set.

## Change process

1. Identify the concrete task or observed failure and the owner of the affected material.
2. Read the governing chain and current sources. Decide whether an existing area already owns the need.
3. Make the smallest coherent change. Preserve personal content and compatibility, or state the required migration clearly.
4. Update the owning guide and its discovery links together. When guidance scope changes, update the central principle or stage entry and each affected rule's direct or inherited applicability; do not add a project-local guidance branch.
5. Validate at the level of the claim: inspect links and ownership for documentation, exercise behaviour for guidance delivery, and test real mechanisms for operational protection.

Keep untested claims visible as unvalidated. Record detailed execution work in its project or tracker rather than turning this plan into a work log.
