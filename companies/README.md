# Companies

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when a task concerns running a company: its structure, governance, finances, compliance, registrations, or company-wide accounts. Building one of its products is project work. The shared framework supplies this guide and `.gitignore`; each company's content belongs to the personal brain.

## Find a company

Each company has a folder, `companies/<company>/`, named in the words the owner uses for it. The folders are the index, because a company has no remote or working directory to match. If the task is about the owner's company and names none, the only one applies; with several, ask. A task about someone else's company is not company work here. When the owner's company has no folder yet, create `companies/<company>/` with its README and say so. Add an index only when a name in use cannot be matched from a folder name.

## Parts

A company uses the same parts as a project home, so BRAIN's habits apply unchanged. Create each part when its first item arrives.

| Part | Holds | Governed by |
|---|---|---|
| `README.md` | What the company is, a summary of its structure with source and date, its products as links with no status, and a Records section | This guide |
| `workstreams/`, `INBOX.md`, `briefs/` | Open work and deadlines, findings, and handoffs | [Work](../agent/work/README.md) |
| `knowledge/` | Decisions, reasons, and what was learned | [Knowledge](../agent/knowledge/README.md) |
| `guidance/STAGES.md`, `guidance/stages/` | Situations and rules for this company alone | [Guidance](../guidance/README.md) |

A recurring obligation is a workstream whose open step is its next occurrence, with `due:` moved on each time, so it stays open while the obligation exists. A company's stage page is read on entering the company, but the [gate hook](../agent/operations/gate-hook.md) does not hold commands for it; extend the hook when a company rule first needs to stop a command.

## Company, product, or personal

Ask in order:

1. **Is it the company's legal or accounting record?** It is company, even when it concerns one product, such as that product's trademark registration or its revenue in the books, or a director's loan as the company records it.
2. **Is it what this means for the owner's own money or tax?** It stays in [Personal](../personal/README.md).
3. **Would it still be true and needed if that product shut down?** Yes means company, such as an organisation developer account or payout details. No means product, such as an in-app purchase catalogue or store listing.

Split a task that spans two. A product's README links its company with a line such as `**Company:** [Name](../../companies/<company>/README.md)`, and a product reads company facts through that link rather than copying them.

## Where the truth lives

The brain owns open work, deadlines, decisions and their reasons, and what was learned. It points to everything else.

| Record | Authority | In the brain |
|---|---|---|
| Registered details, officers, shareholders | The government register | A summary with its source and date, or marked unverified |
| Signed consents, certificates, receipts | The owner's document store | The folder's path in the Records section |
| Money | The bank and the accounting system | Where they are, never balances |
| Credentials and unpublished identifiers | The owner's password store | `Kept in: <store>, "<entry>"` |
| Anything about one product | That product's project | A link |

The Records section gives a plain folder path per kind of record. It lists no individual files, because they get renamed, and no share links, because anyone holding one can open the file. Check how long each kind of record must be kept in the company's jurisdiction and record the answer here.

## Files and secrets

Files and secrets stay out of the brain: every connected service can read the repository, and what enters Git history stays there. [Sensitive information and binding actions](../agent/operations/sensitive-information.md) sets what an agent may read and do. The `.gitignore` in this folder makes ordinary `git add` stage only Markdown under `companies/`, so a dropped PDF stays out of Git. Such a file sits unsynced with no warning, and the ignore file does not stop a forced add or a secret saved as Markdown.

A document store that syncs a deletion everywhere is not a backup. Confirm that a second copy exists when setting one up.

## Move a company out of `projects/`

A framework update never moves personal content; the owner decides. Check that nothing under the old folder is uncommitted and no session is working on the company, because on a brain written from several machines, a new file under the old path on a machine that has not pulled stops that machine's sync with a conflict. Then, in one commit: `git mv projects/<company> companies/<company>`, remove its row from `projects/INDEX.md`, correct its README's governing parent, and update other references to the old path. Move any tracked non-Markdown file to the document store first, because a tracked file stays tracked despite the ignore file. A stage page with `before:` commands stops being delivered by the gate hook once the row is gone. Afterwards, confirm on each machine that the old folder is gone, since a session still holding the old guidance can recreate it. To undo the move, make a new commit moving the folder back; `git revert` works only until something has been added under the new path.
