# Personal

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when a task concerns the owner's own life rather than a project: life direction, family, health, routines, home, travel, and personal finance and administration. Career work, investing, and other bodies of work with their own goals belong in [project homes](../projects/README.md). The shared framework supplies this guide; the area's content belongs to the personal brain.

## Parts

The area uses the same parts as a project home, so BRAIN's habits apply unchanged. Create each part when its first item arrives.

| Part | Holds | Governed by |
|---|---|---|
| `knowledge/` | Notes on the owner's inner life and how they live: direction, health, routines, reflections, plans | [Knowledge](../agent/knowledge/README.md) |
| `household/` | Notes on operations an assistant would carry out: properties, providers, bills and renewals, travel logistics, administrative deadlines | [Knowledge](../agent/knowledge/README.md) note shape |
| `people/` | One page per person in the owner's inner circle, such as family and close friends | This guide |
| `workstreams/`, `INBOX.md`, `briefs/` | Open loops and commitments, findings, and handoffs | [Work](../agent/work/README.md) |
| `guidance/STAGES.md`, `guidance/stages/` | Situations and rules that apply to the owner's personal life alone | [Guidance](../guidance/README.md) |
| Personal documents | Plans and records with no other home, linked from the owner's snapshot | This guide |

Principles for personal life stay in root `guidance/PRINCIPLES.md` under a Personal scope heading, or, when they apply only while working as particular leads, under one where [Maintain guidance](../guidance/authoring.md#leads) places such principles.

When a note could go to `knowledge/` or `household/`, ask whether an assistant would act on it: if so, it is household; if it is reflection or how the owner lives, it is knowledge. Open loops from either stay in `workstreams/`, with a `due:` date when they have one. On entering the area, list `household/` and `people/` alongside `knowledge/`. A `people/` page is named after the person and holds what the owner's own life needs about them, such as the relationship, important dates, and preferences that matter to the owner; facts about the owner's dealings with that person stay in the notes and workstreams they belong to, linked from the page.

## Snapshot

The owner's page is the root `SNAPSHOT.md`, described in the [Work guide](../agent/work/README.md#snapshot); its open-loops view lists `personal/workstreams/`. When a personal task changes a written section of it, update that section in place with its date.

## Boundaries

Personal content is kept out of other tasks' context because only a personal task enters this area, but any actor with file access can read it. Keep secrets, credentials, and government or financial identifiers out of it; record where they are kept instead, in a household note that names the stores, and refer to one as `Kept in: <store>, "<entry>"`. Do not store other people's personal data beyond what the owner's own life requires.
