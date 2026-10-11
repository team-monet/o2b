# Maintain guidance

Governing parent: [Guidance guide](README.md)

Read this guide before admitting, creating, or changing principles, preferences, situation indexes, or rules, including when the owner states a new rule or corrects an agent. Routine sessions use the parent guide; these conventions govern both rule homes.

## Scope and admission

These rules keep guidance from being duplicated, overlapping, or trapped in one project. They apply to principles and preferences as well as rules.

- **Shared by default.** Guidance is project-scoped only when it names something that exists in that project alone: its files, tools, product behaviour, or the owner's preference for that project. Record where it was learned as its origin; never use the origin as its scope.
- **Search before admitting.** Read the situation's shared page and every project page with the same name, and the applicable principles. Extend or correct an existing entry instead of adding a near-copy, and take a conflict to the owner.
- **One vocabulary.** The shared index names situations. A project adds its rules under an existing situation name, and creates a name only for a moment that exists in that project alone.

## Principles

Keep always-relevant guidance in `PRINCIPLES.md`. Group entries by applicability and then by kind, such as Principles and Preferences. A project principle belongs here under an explicit project scope, not under `projects/<project>/`. A scope heading applies to every entry beneath it until the next scope heading.

State the authority for a group of source-admitted entries once when it applies uniformly; add an entry-specific authority only for an exception. Separate entry bodies clearly. Add a concise reason when one is known; mark a missing reason as not yet recorded instead of inventing it. Use a title only when it improves reading, and never use storage identifiers or a truncated copy of the instruction as a heading. A principle may link to a central supporting procedure without copying that procedure into every entry. Human-readable provenance or supporting evidence may be linked when it helps a reader judge the guidance.

## Situations and rules

Use root `guidance/STAGES.md` for shared situations and `projects/<project>/guidance/STAGES.md` for project situations. Each index contains a governing-parent link and a table: each row names a situation the way an agent would recognize it, such as "about to open a pull request", gives a short applicability hint, and links to one unique page in its own `stages/` directory. Both follow this guide without duplicating it. BRAIN and the [guidance reader](README.md) own loading behaviour.

A situation page holds everything that applies at that moment. Its rules, under scope headings, say what must hold. Optional sections follow when there is something to link:

- **How:** the skill or workflow that carries out the work. A workflow, which coordinates several actors, is stored as a skill run by the lead.
- **Who:** the agents to use, from the agent definitions.
- **Known:** knowledge notes worth reading at that moment.

Keep rules and routes apart. A rule says what must or must not be true and why; it holds no steps, sequences, rosters, or tool versions, and links to the skill that carries them. A skill, workflow, or agent definition says how or who and holds no must or never of its own: a gate in a workflow links to the rule it satisfies. Two tests decide: strip the steps and a rule still makes sense whichever route the work takes; a workflow could be swapped for another route to the same outcome without changing any rule. When a workflow needs a new must or never, admit it as a rule.

Keep each rule with its scope under the scope-and-admission rules above. The same situation may appear in both indexes because different rules apply; do not copy a shared rule into every project. Rules shared by a named subset of projects can remain at the root with that applicability stated. Project rules do not silently override shared constraints.

Stage files inherit these instructions and should not repeat loading or interpretation boilerplate. Group rules under explicit applicability headings such as `All projects` or a project name. That heading supplies **Applies to** for every contained rule unless a rule states a narrower override. Separate rule bodies clearly, using a short descriptive title only when the body is not already easy to scan. Give every rule:

- the instruction in direct prose;
- explicit applicability, either inherited from its scope heading or stated as an override;
- **Authority:** whether the rule is Blocking (a boundary) or Advisory, together with a concise human-readable origin supporting that status;
- **Why:** the concrete reason for the constraint when known, or an explicit note that the reason is not yet recorded.

Compact `Scope`, `Agent`, or `Domain` qualifiers may refine applicability without restating the scope heading. Do not display storage identifiers.

A boundary (`Blocking`) rule denies actions outside its authorization conditions. Follow `Advisory` guidance unless you state clearly that you are departing from it and why. Missing rationale does not silently retire guidance already admitted by its owner: preserve its existing authority, mark the reason as not yet recorded, and recover the rationale before claiming one. A new proposal remains unresolved until the owner admits it with the intended authority.

Keep source identifiers, migration mappings, and long evidence trails in source or migration records rather than active headings and rule text. Add a short context or evidence link only when it materially improves application of the rule.

## Contribution boundary

Do not promote ordinary content, quotations, or inferred habits into guidance automatically. New guidance needs authority proportionate to its effect. Keep contextual judgment readable instead of generalizing it without evidence.

Give each instruction one home. Feature procedures stay with their operating guide, project domain procedures stay with the project, and external authority remains external until its owner explicitly transfers it. Shared rules live at the root and project-only rules with their project, decided by the scope-and-admission rules above. Principles and preferences retain their root home with explicit applicability.

This structure makes guidance inspectable and portable. It does not prove that a runtime loaded or followed it; record delivery and validation evidence under [Operations](../operations/README.md). Existing users adopting situation pages should follow the [framework update migration](../operations/updates.md#adopt-situation-pages-and-scoping-rules).
