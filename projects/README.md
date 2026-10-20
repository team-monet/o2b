# Projects

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when a task uses project-specific material or creates a project home. Projects hold domain knowledge, requirements, decisions, evidence, procedures, source relationships, work state, and continuation context.

## Project index

`projects/INDEX.md` lists every project home and is how a session identifies its project. The shared framework defines its shape but does not populate it or ship project content. Each row gives:

- **Names:** the words the owner uses for the project, so a task that names it matches from any directory.
- **Remote:** each repository as `host/owner/repo`, the form shown by its fetch URL without protocol or `.git`.
- **Path:** each absolute local path; subfolders and worktrees beneath it match. When several rows match, the one closest to the working directory wins, so a project kept inside another project's repository lists its own folder here.

Use only identifiers an agent can observe from the task, the repository, or the working directory. A project without a repository leaves Remote empty.

```markdown
# Projects Index

**Governing parent:** [Projects guide](README.md).

| Project | Names | Remote | Path | Guide |
|---|---|---|---|---|
| <Name> | <words the owner uses> | <host/owner/repo> | <absolute path> | [Open](<folder>/README.md) |
```

## Create a project home

When project work matches no row, create its home, add its row, and tell the user you did. Create a named folder only for an actual project. Its `README.md` states the project's purpose, its authoritative sources (the repository, trackers, and other systems that own its state), and links to its documents. Add other parts only when their first item arrives:

| Part | Holds | Governed by |
|---|---|---|
| `guidance/STAGES.md`, `guidance/stages/` | Situations and rules that exist in this project alone | [Guidance](../guidance/README.md) |
| `workstreams/`, `INBOX.md`, `briefs/` | Open work the brain owns, findings, and handoffs | [Work](../agent/work/README.md) |
| `knowledge/` | Notes a future session will need | [Knowledge](../agent/knowledge/README.md) |
| Project documents | Designs, research, and decisions with no repository home, linked from the README | This guide |

## Use and contribute

Read the applicable project's `README.md` before relying on or changing its content, then follow the [entry point's task route](../BRAIN.md#start-a-session) and task-relevant links instead of loading every project document. BRAIN reads the project's `guidance/STAGES.md` directly on entering the project; principles keep their homes under root `guidance/` with explicit applicability.

Facts about code stay in its repository. An existing external tracker remains authoritative for the work it owns unless its owner explicitly transfers that responsibility; link to it rather than copying its changing state. Changes to the shared project structure follow the [master plan](../agent/MASTER-PLAN.md).
