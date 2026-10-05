# Work

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when continuing previous work, recording or updating durable work, capturing a finding, or settling work before completion. A clear new task needs no startup workstream or inbox scan; follow the [entry point's task route](../BRAIN.md#start-a-session).

## Where work lives

| Owner | Workstreams | Agent inbox |
|---|---|---|
| A project | `projects/<project>/workstreams/<name>.md` | `projects/<project>/INBOX.md` |
| Personal or cross-project work | `work/workstreams/<name>.md` | `work/INBOX.md` |

Create files when needed and link project records from the project README. Keep existing plans and external trackers authoritative; do not copy their changing work into another record. The framework supplies conventions and examples; actual records belong to each personal brain.

## Workstreams

A workstream preserves an objective and questions or steps that may outlive a session. Small tasks need none; fine-grained tasks stay in the host's task state. Keep rationale and evidence in linked artifacts.

On a continuation request, start with the relevant workstream or owning tracker. If the target is ambiguous, inspect titles/status and ask which stream. Read open questions before steps, then search or follow links for the knowledge needed to continue. Verify current sources; read resolved history only when needed.

Update the open set as work changes. Give items stable labels unique within the file, including resolved items. Address them by file and label; preserve untouched items and never renumber or reuse labels. Resolve an item by moving its original text and label to `Resolved`, with a date and one disposition: `done` with a result, `dropped` with a reason, or `filed` with a verified destination. Filing transfers work; it does not complete it.

Status is `active`, `paused` when explicitly held, or `done` only when no open item remains. New follow-up work makes a done stream active unless explicitly held. Resolve inconsistent records before updating them.

Copy this shape, replacing placeholders and removing unused sample items. `../README.md` reaches the project guide or this Work guide from either workstream home above:

```markdown
# <Title>

**Governing parent:** [Project or work guide](../README.md).
**Status:** active
**Objective:** <Outcome.>

## Open questions
- question-01: <Question.>

## Open steps
- step-01: <Next action.>

## Resolved
```

<a id="inbox"></a>

## Agent inbox

One inbox per scope serves humans and agents. Capture an incidental finding in one short Pending bullet with a stable label, date, context, and source when useful. Avoid duplicates, preserve existing entries, and continue the current task. Capture creates no commitment or new workstream.

Disposition belongs to the owner: keep pending, act when authorized, drop with a reason, or file to its appropriate home. Verify the filing destination first. Move resolved entries, preserving text and label, to `Resolved` with a dated result, reason, or destination link. Leave kept items alone unless relevant circumstances change. Existing unlabelled entries can receive labels when next updated or disposed.

Copy this shape; `README.md` reaches the project guide or this guide from either inbox home:

```markdown
# Agent inbox

**Governing parent:** [Project or work guide](README.md).

## Pending
- find-01 — <date>: <Finding.>

## Resolved
```

## Before finishing

Settle addressed work and review the relevant inbox; present items needing owner judgment together. Leave unfinished work with an honest status and a concrete next step. The record and linked artifacts should support continuation without the original chat.

Coordinate one writer per affected file, reread before editing, and inspect the result. Preserve conflicting contributions for resolution. After interrupted filing, check the existing destination before retrying. These files supply no locking, atomic transactions, or scheduling; those mechanisms belong to [Operations](../operations/README.md). See [validation scenarios](validation.md) when evaluating actual use.
