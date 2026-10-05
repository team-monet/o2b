# Maintain guidance

Governing parent: [Guidance guide](README.md)

Read this guide before creating or changing principles, preferences, shared or project stage indexes, or rules. Routine sessions use the parent guide; these authoring conventions govern both rule homes.

## Principles

Keep always-relevant guidance in `PRINCIPLES.md`. Group entries by applicability and then by kind, such as Principles and Preferences. A project principle belongs here under an explicit project scope, not under `projects/<project>/`. A scope heading applies to every entry beneath it until the next scope heading.

State the authority for a group of source-admitted entries once when it applies uniformly; add an entry-specific authority only for an exception. Separate entry bodies clearly. Add a concise reason when one is known; mark a missing reason as not yet recorded instead of inventing it. Use a title only when it improves reading, and never use storage identifiers or a truncated copy of the instruction as a heading. A principle may link to a central supporting procedure without copying that procedure into every entry. Human-readable provenance or supporting evidence may be linked when it helps a reader judge the guidance.

## Stages and rules

Use root `guidance/STAGES.md` for shared stages and `projects/<project>/guidance/STAGES.md` for project stages. Each index contains a governing-parent link and a table: each row identifies a recognizable action moment, gives a short applicability hint, and links to one unique file in its own `stages/` directory. A project index links to its project README, which links back to the index. Both follow this guide without duplicating it. BRAIN and the [guidance reader](README.md) own loading behaviour.

Keep each rule with its scope. Split a mixed stage file into shared and project sections at their respective homes, preserving instructions, authority, applicability, and reasons. The same moment may appear in both indexes because different rules apply; do not copy a shared rule into every project. Rules shared by a named subset of projects can remain at the root with that applicability stated. Project rules do not silently override shared constraints.

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

Give each instruction one home. Feature procedures stay with their operating guide, project domain procedures stay with the project, and external authority remains external until its owner explicitly transfers it. Shared stage constraints belong at the root; project stage constraints belong with their project. Principles and preferences retain their root home with explicit applicability.

This structure makes guidance inspectable and portable. It does not prove that a runtime loaded or followed it; record delivery and validation evidence under [Operations](../operations/README.md). Existing users moving rules into this layout should follow the [framework update migration](../operations/updates.md#adopt-shared-and-project-stage-discovery).
