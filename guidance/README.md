# Guidance

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide at session start. `guidance/` is the single home for behavioural guidance across shared and project-specific scopes. Projects may link here but must not maintain separate principles, stage indexes, rule files, or behavioural guidance trees.

The framework defines the following personal paths without supplying populated content:

- `PRINCIPLES.md` — shared principles plus principles explicitly scoped to named projects or other contexts.
- `STAGES.md` — one central index of action moments, applicability hints, and links to stage files.
- `stages/<stage>.md` — one uniquely named document for each action moment, containing all rules associated with that stage.

If one of these files is absent, no personal guidance is recorded there. Do not infer or recreate it from framework text.

## Principles

Keep always-relevant guidance in `PRINCIPLES.md`. Group entries by applicability and then by kind, such as Principles and Preferences. A project principle belongs here under an explicit project scope, not under `projects/<project>/`. A scope heading applies to every entry beneath it until the next scope heading.

State the authority for a group of source-admitted entries once when it applies uniformly; add an entry-specific authority only for an exception. Separate entry bodies clearly. Add a concise reason when one is known; mark a missing reason as not yet recorded instead of inventing it. Use a title only when it improves reading, and never use storage identifiers or a truncated copy of the instruction as a heading. A principle may link to a central supporting procedure without copying that procedure into every entry. Human-readable provenance or supporting evidence may be linked when it helps a reader judge the guidance.

## Stages and rules

`STAGES.md` is the only stage index. Keep it to a governing-parent link and a table: each row identifies a recognizable action moment, gives a short applicability hint, and links to one unique file under `stages/`. BRAIN.md and this guide own the read-before behaviour. Match the moment by meaning rather than exact wording. Several projects may share a stage file when the action moment is the same; applicability within the stage file decides which rules apply.

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

Give each instruction one home. Feature procedures stay with their operating guide, project domain procedures stay with the project, and external authority remains external until its owner explicitly transfers it. Behavioural constraints and preferences belong in this central guidance area even when their applicability is one project.

This structure makes guidance inspectable and portable. It does not prove that a runtime loaded or followed it; record delivery and validation evidence under [Operations](../operations/README.md). Existing users moving project guidance into this layout should follow the [framework update migration](../operations/updates.md#migrate-project-guidance-into-central-guidance).
