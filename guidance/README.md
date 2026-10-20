# Guidance

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide at session start. Guidance is anchored to situations: the moments, such as opening a pull request or handing work to another session, where something must hold or a known route helps. Shared situations live under root `guidance/`; project-only situations live under `projects/<project>/guidance/`. This guide governs both.

The personal brain may contain:

- `PRINCIPLES.md`: shared and explicitly scoped principles and preferences, always on, apart from those that belong to particular leads.
- `LEADS.md`: the index of leads, the agents the owner works with directly, linking each to its page.
- `leads/<lead>.md`: one lead's page.
- `principles/<set>.md`: principles that belong to several leads, read by the leads whose pages name the set.
- `STAGES.md`: the index of shared situations, linking each to its page.
- `stages/<situation>.md`: the page for one situation.
- `projects/<project>/guidance/STAGES.md` and `stages/<situation>.md`: that project's situations, or its additions to shared ones.

The framework supplies conventions, not populated personal guidance. If an optional file is absent, do not infer its contents.

## Apply guidance

Apply only guidance whose project, actor, domain, and action scope matches the task. A lead is an actor: the principles its page holds or names apply only while working as it, a rule that names leads applies only to them, and a rule that names none applies to every lead. A scope heading governs the entries beneath it until the next scope heading; entry qualifiers may narrow it. Match situations by the meaning of the moment, not exact wording, and follow BRAIN's read-before-action instruction.

Load the shared index at startup and a project's index on entering that project. Before acting in a situation, read its page from both indexes. A page's rules, under their scope headings, say what must hold and carry its authority. Its **How**, **Who**, and **Known** sections, when present, link the skill or workflow to follow, the agents to use, and the notes worth reading. Skills, workflows, and agent definitions carry no authority of their own: when one conflicts with a rule, the rule applies and the conflict is surfaced. Project rules supplement shared rules; surface conflicting instructions rather than silently overriding either. Reassess applicability when the project changes.

A **Blocking** rule is a boundary; do not cross it outside its authorization conditions. Follow **Advisory** guidance unless you state the departure and why. A missing rationale does not retire admitted guidance or change its authority.

<a id="work-as-a-lead"></a>

## Work as a lead

When the brain has `LEADS.md`, a session working with the owner chooses which lead it works as at session start: the one the owner names in the conversation; else the one the brief you start from names; else the one the owner's instructions for that place name; else the one whose index row fits what the work is now, not what it may become. When none fits, work without one. Say in one line of your first reply which lead you are working as, or that none fits, so the owner can redirect you. A worker, an agent working for a lead, works as none, and an autopilot run works as one only when its front page names it. A brain without `LEADS.md` defines no leads, and its sessions do not mention them.

When the work turns into what another lead is for, say so and hand it to a new session working as that lead, recording the handoff as the [Work guide](../agent/work/README.md#handoffs) describes, so the new session starts without this lead's principles and context. When the owner asks to continue here instead, when the Work guide gives the work no brief home, as for cross-project work, or when the owner names another lead at any point, read that lead's page and every file it names for reading at session start, and work as it from then on.

## Maintain guidance

Before admitting, creating, or changing guidance, read [Maintain guidance](authoring.md). Its authoring, scoping, and migration instructions are not part of routine startup reading.
