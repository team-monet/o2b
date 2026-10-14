# Work

Governing parent: [BRAIN.md](../../BRAIN.md)

Read this guide when creating a workstream, inbox, brief, or the snapshot, or changing how one is kept. BRAIN.md carries the everyday habits: noticing open work at the start, capturing findings, recording handoffs, handing things to the owner, and settling before reporting done.

## Where work lives

| Owner | Workstreams | Inbox | Briefs |
|---|---|---|---|
| A project | `projects/<project>/workstreams/<name>.md` | `projects/<project>/INBOX.md` | `projects/<project>/briefs/<slug>.md` |
| The owner's personal life | `personal/workstreams/<name>.md` | `personal/INBOX.md` | `personal/briefs/<slug>.md` |
| Cross-project work | `agent/work/workstreams/<name>.md` | `agent/work/INBOX.md` | — |

Project work never goes in `agent/work/`; when a project has no home yet, create one as the [projects guide](../../projects/README.md) describes. Create each file or folder when its first item arrives. The folders are the index: agents find open work by listing them, so no README needs to link it. Keep existing plans and external trackers authoritative; do not copy their changing work into another record. The framework supplies conventions and examples; actual records belong to each personal brain.

## Workstreams

Open a workstream when work is handed to another session, worktree, or agent, or when something will still be open at the end of a session and no tracker owns it. Small tasks need none, fine-grained tasks stay in the host's task state, and work a pull request or issue already tracks stays with that tracker.

A workstream holds its objective, open questions, open steps, and links. Rationale, evidence, and design content go to their own home: the repository when the project has one, otherwise a document in the project folder linked from its README. Once content has landed there, remove the workstream's copy.

On a continuation request, start with the relevant workstream or owning tracker. If the target is ambiguous, list the candidates and ask which one. Read open questions before steps, then search or follow links for the knowledge needed to continue, and verify current sources.

Give items labels unique among the file's current items and address them by file and label; do not renumber. Settle an item by putting its result where it is used — the repository, a tracker, a knowledge note, a project document, or guidance — and then removing the item. Keep a dropped item's reason only as a knowledge note, when it would stop the item being proposed again. Filing transfers work: verify the destination before removing the item. Remove a workstream once nothing in it is open. Git keeps the past.

Status is a frontmatter property so views such as Obsidian Bases can list open work: `active`, or `paused` when explicitly held. Copy this shape, replacing placeholders and removing unused sample items. `../README.md` reaches the project, personal, or Work guide from each workstream home above:

```markdown
---
status: active
---
# <Title>

**Governing parent:** [Project or work guide](../README.md).
**Objective:** <Outcome.>

## Open questions
- question-01: <Question.>

## Open steps
- step-01: <Next action.>
```

<a id="handoffs"></a>

## Handoffs

A brief gives another session, worktree, or agent what it needs to do a piece of work without the original conversation. That includes a session's next piece of work when a fresh session will take it up, not only work delegated to an agent. Write it at `projects/<project>/briefs/<slug>.md` and link it from the workstream step that tracks the handoff; start the receiving session with the brief's path. A brief names its goal, the sources to read, the decisions and rules that bind the work, what is out of scope, what the receiver may and may not do, and what done means. It also carries the understanding the conversation built: what the owner said that shaped the work, in their words where the wording matters, and what was considered and dropped, and why. A receiving session that works with the owner opens by saying that understanding and the deliverable back in a few lines, and starts once the owner confirms. Remove the brief when its step settles.

<a id="inbox"></a>

## Agent inbox

One inbox per scope serves humans and agents. Capture a finding as one dated line, `- <date>: <finding> (<source>)`, and continue the current task; mark a knowledge placeholder with `learned:` after the date. Entries carry no labels: refer to them by date and wording. Avoid duplicates and preserve existing entries. Capture creates no commitment or new workstream.

Disposition belongs to the owner: keep, act when authorized, drop, or file to its appropriate home. An agent resolves an entry its own authorized task finished, and turns a `learned:` line into a knowledge note when settling; the next session that settles in the project may file a line its writer left behind. Resolve an entry by removing it once its result is where it is used; verify a filing destination first.

Copy this shape; `README.md` reaches the project, personal, or Work guide from each inbox home:

```markdown
# Inbox

**Governing parent:** [Project or work guide](README.md).

- <date>: <Finding.> (<source>)
```

<a id="snapshot"></a>

## Snapshot

`SNAPSHOT.md` at the brain root is the one page the owner reads each morning to see what needs them. Keep it short: an owner flooded with items stops reading. It holds live views and, if the owner wants them, a few written sections such as current focus; it links instead of copying.

A file appears under For you while its frontmatter carries `for_you: <what it needs from the owner>`, such as `for_you: decide whether paper trading moves to real money`. It belongs only on something waiting on the owner now, never on routine output, as `BRAIN.md`'s habit "Hand things to the owner" says. Leave the file with its owner, and remove the file when nothing else needs it. Running lists autopilot operations by their front page; Open loops lists personal workstreams with their status and due date.

The views are Obsidian Bases. An agent that cannot render them reads the same frontmatter and folders instead. Any agent may update a written section in place, with its date, when its task changes what the section shows; sections are added or removed only when the owner asks. A briefing sent to the owner is built from this page and, where connected, their calendar and email; it is a message, not a page, and is not kept in the brain.

Create the page from this skeleton:

````markdown
# Snapshot

**Governing parent:** [Work guide](agent/work/README.md#snapshot).

## For you

```base
filters:
  and:
    - file.hasProperty("for_you")
views:
  - type: table
    name: For you
    order:
      - file.name
      - note.for_you
```

## Running

```base
filters:
  and:
    - file.inFolder("autopilot")
    - 'file.basename == "README"'
    - file.hasProperty("status")
views:
  - type: table
    name: Running
    order:
      - file.folder
      - note.status
```

## Open loops

```base
filters:
  and:
    - file.inFolder("personal/workstreams")
views:
  - type: table
    name: Open loops
    order:
      - file.name
      - note.status
      - note.due
```
````

## Before finishing

Leave unfinished work with an honest status and a concrete next step. The record and linked artifacts should support continuation without the original chat.

Coordinate one writer per affected file, reread before editing, and inspect the result. Preserve conflicting contributions for resolution. After interrupted filing, check the existing destination before retrying. These files supply no locking, atomic transactions, or scheduling; those mechanisms belong to [Operations](../operations/README.md). See [validation scenarios](validation.md) when evaluating actual use.
