# Agents

Governing parent: [BRAIN.md](../../BRAIN.md)

Read this guide when choosing an agent to delegate to, or when creating or changing an agent definition. Definitions here are workers, agents that work for a lead or an operation; the leads the owner works with directly are guidance: see [Work as a lead](../../guidance/README.md#work-as-a-lead). The shared framework supplies this guide; actual definitions belong to the personal brain. Repository-owned agents keep their repository as their home.

## Definitions

Keep each definition at `agent/agents/<name>.md` in Claude Code's agent format: frontmatter with name, description, and any model or tool settings, followed by the prompt. Runtime sync generates other runtimes' formats from it. The description says when to use the agent; BRAIN's delegation habit and a situation page's **Who** section choose agents by it.

A definition says who an actor is: its role, the evidence it must return, and its boundary. Procedures belong in skills and rules in situation pages; link them rather than copying them in. State the boundary in every definition. By default a worker reads the brain but does not write to it, address the user, or delegate further; the lead relays its evidence and owns the brain's records. Add fields such as permitted action classes, escalation, or revocation only when an operation needs them.

A team or operation adopts a definition by reference, recording its source and version, and may evolve its own copy from there.

A definition from outside the brain is adopted by copying only the definitions needed into `agent/agents/<name>.md`, never a whole collection. The copy records where it came from and which revision in its frontmatter, as `source:` and `revision:`: the commit or version, or the date copied when the source has neither. Updates are taken from that source.

## Discovery

[Runtime sync](../operations/skill-discovery.md#runtime-sync) links or generates each runtime's copy of these definitions, so edits here take effect everywhere. A runtime it does not cover can still be given a definition's path and description.
