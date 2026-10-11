# Knowledge

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when writing, reorganising, or migrating knowledge notes. BRAIN carries the everyday habits: when a note is worth writing, how to make it findable, and listing notes when entering a project.

## Where notes live

Project knowledge lives in `projects/<project>/knowledge/`; knowledge that clearly applies beyond one project lives in root `knowledge/`. Facts about code stay in its repository. Each folder is created with its first note, and its listing is the index: there is no separate index file.

## Note shape

One topic per note. The filename names the subject in the words a future task would use, such as `drizzle-baselining.md`, and serves as the title. The first line is a one-sentence summary, so a reader can decide from a listing or a search match whether to open the rest.

```markdown
<One-sentence summary of what a reader needs to know.>

<The detail, using the exact names, commands, and error text a search would hit. Keep what was observed apart from what was inferred.>

Source: <where this was observed or read>, <date or version>.
```

Store enough subject, source, version or time scope, and evidence for a later reader to judge whether the note still applies.

## Write and maintain

Before writing, list the folder and search for the subject; update the matching note in place rather than adding another, and merge near-duplicates when you find them. A `learned:` line left in an inbox becomes a note, or part of one, when its session settles. When a note proves wrong or stale, correct it or remove it. Keep a correction's earlier belief in the note only when it would prevent the same mistake again.

## Read

List the note filenames, or search and read the matching notes' first lines, before opening any note in full; open only the notes the task touches. Search results are candidates, not selected context: check a note's source and date before relying on it.

## Migrate from another system

Bring knowledge across one project at a time, never in bulk. For each record, check it against current sources where that is cheap, keep it only if a future session would otherwise rediscover it or ask the owner again, and merge small records into topic notes in the shape above. Records left behind stay in the source system as its history.

Follow the [master plan](../MASTER-PLAN.md) before adding indexes, retrieval tools, or other framework machinery.
