# Guidance

Governing parent: [BRAIN.md](../BRAIN.md)

`BRAIN.md` carries what every session needs at the start. Read this guide when what a rule covers, or changing lead, is in question. Guidance is anchored to situations: the moments, such as opening a pull request or handing work to another session, where something must hold or a known route helps. Shared situations live under root `guidance/`; project-only situations live under `projects/<project>/guidance/`. This guide governs both.

The personal brain may contain:

- `PRINCIPLES.md`: shared and explicitly scoped principles and preferences, always on, apart from those that belong to particular leads.
- `LEADS.md`: the index of leads, the agents the owner works with directly, linking each to its page.
- `leads/<lead>.md`: one lead's page.
- `principles/<set>.md`: principles that belong to several leads, read by the leads whose pages name the set.
- `STAGES.md`: the index of shared situations, linking each to its page.
- `stages/<situation>.md`: the page for one situation.
- `projects/<project>/guidance/STAGES.md` and `stages/<situation>.md`: that project's situations, or its additions to shared ones. A company's live at the same paths under `companies/<company>/`.

The framework supplies conventions, not populated personal guidance. If an optional file is absent, do not infer its contents.

## Apply guidance

Apply only guidance whose project, actor, domain, and action scope matches the task. A lead is an actor: the principles its page holds or names apply only while working as it, a rule that names leads applies only to them, and a rule that names none applies to every lead. A scope heading governs the entries beneath it until the next scope heading; entry qualifiers may narrow it. Match situations by the meaning of the moment, not exact wording, and follow BRAIN's read-before-action instruction.

Load the shared index at startup and a project's index on entering that project. Before acting in a situation, read its page from both indexes. A page's rules, under their scope headings, say what must hold and carry its authority; agent definitions, like the skills and workflows a page links, carry none of their own. Project rules supplement shared rules; surface conflicting instructions rather than silently overriding either. Reassess applicability when the project changes.

`BRAIN.md` says how **Blocking** and **Advisory** rules bind. A missing rationale does not retire admitted guidance or change its authority.

<a id="work-as-a-lead"></a>

## Work as a lead

`BRAIN.md` says how a session chooses its lead at the start. When the owner corrects how you work as a lead, or your sessions show something your page lacks, propose the change as [Fit a lead to its owner](authoring.md#fit-a-lead-to-its-owner) describes.

When the work turns into what another lead is for, say so and hand it to a new session working as that lead, recording the handoff as the [Work guide](../agent/work/README.md#handoffs) describes, so the new session starts without this lead's principles and context. When the owner asks to continue here instead, when the Work guide gives the work no brief home, as for cross-project work, or when the owner names another lead at any point, read that lead's page and every file it names for reading at session start, and work as it from then on.

## Maintain guidance

Before admitting, creating, or changing guidance, read [Maintain guidance](authoring.md). Its authoring, scoping, and migration instructions are not part of routine startup reading.
