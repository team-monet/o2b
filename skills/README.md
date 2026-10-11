# Skills

Governing parent: [BRAIN.md](../BRAIN.md).

Read this guide when creating, changing, or installing personal agent skills. The shared framework supplies this guide; actual skills belong to the personal brain. Repository-owned skills retain their repository as the authoritative home.

Follow the [Agent Skills specification](https://agentskills.io/specification). Keep each maintained skill directly at `skills/<skill-name>/SKILL.md` for shared discovery; supporting resources stay within that skill's folder. Personal skills may be project-scoped and need no stage binding. A workflow, which coordinates several actors toward an outcome, is a skill run by the lead. Like any skill it holds no must or never of its own: a gate in it links to the situation rule it satisfies, and situation pages link it from their **How** section.

When configuring an agent's discovery root or installing on another machine, read [skill discovery setup](../operations/skill-discovery.md). For supporting bundles and external dependencies, follow [Capabilities](../capabilities/README.md).
