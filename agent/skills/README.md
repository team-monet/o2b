# Skills

Governing parent: [BRAIN.md](../../BRAIN.md).

Read this guide when creating, changing, installing, or moving agent skills. The shared framework supplies this guide; actual skills belong to the personal brain.

Follow the [Agent Skills specification](https://agentskills.io/specification). Keep each maintained skill directly at `agent/skills/<skill-name>/SKILL.md` for shared discovery, with its scripts, configuration, and other supporting files inside that folder. The entry names what the skill needs beyond its folder, such as tools, runtime packages, or access, and how to obtain it; for a credential, it names where the credential is kept, never its value. Personal skills may be project-scoped and need no stage binding. A workflow, which coordinates several actors toward an outcome, is a skill run by the lead. Like any skill it holds no must or never of its own: a gate in it links to the situation rule it satisfies, and situation pages link it from their **How** section.

Code that is not a personal skill stays with its owner: a repository-owned skill or tool in its repository, linked from its project README with the entry path, and an autopilot operation's code in its `tools/`. Do not keep a second maintained copy in the brain. A skill from an external collection is adopted by copying only the skills needed into `agent/skills/<skill-name>/`, never the whole collection, with its source recorded in the copy (the repository and the commit or version copied, or the date copied when the source has neither) so updates are taken from that source.

Copying or linking a skill's folder does not install what it depends on. Before relying on a skill on another machine, check its prerequisites on that host. When configuring an agent's discovery root or installing on another machine, read [skill discovery setup](../operations/skill-discovery.md).
