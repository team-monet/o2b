# Agents

Governing parent: [BRAIN.md](../../BRAIN.md)

Read this guide when choosing an agent to delegate to, or when creating or changing an agent definition. The shared framework supplies this guide; actual definitions belong to the personal brain. Repository-owned agents keep their repository as their home.

## Definitions

Keep each definition at `agent/agents/<name>.md` in the format its runtime reads: frontmatter such as name, description, and model or tool settings, followed by the prompt. The description says when to use the agent; BRAIN's delegation habit and a situation page's **Who** section choose agents by it.

A definition says who an actor is: its role, the evidence it must return, and its boundary. Procedures belong in skills and rules in situation pages; link them rather than copying them in. State the boundary in every definition. By default a worker reads the brain but does not write to it, address the user, or delegate further; the lead relays its evidence and owns the brain's records. Add fields such as permitted action classes, escalation, or revocation only when an operation needs them.

A team or operation adopts a definition by reference, recording its source and version, and may evolve its own copy from there.

## Discovery

Link each runtime's agent folder to this one so that edits here take effect everywhere; [skill discovery setup](../operations/skill-discovery.md#agent-definitions) describes the links. A runtime that cannot read the format can still be given a definition's path and description.
