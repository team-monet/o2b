# Fit review

Governing parent: [Operations guide](README.md).

Read before setting up or running the fit review, or relying on its reader.

[Review fit across sessions](../../guidance/authoring.md#review-fit-across-sessions), in Maintain guidance, says what the review reads, looks for, may change, and proposes. This page sets it up and documents the [reader](fit-review/read_turns.py), which picks the owner's turns out of each runtime's session records.

## Set it up

Run the review as an [autopilot operation](../../autopilot/README.md), with the owner's go. As for any operation, its front page names its project and the folder joins that project's row in `projects/INDEX.md`.

- **Mission and Boundaries.** The owner states the Mission, such as keeping their leads and principles fitted to them without their having to notice what is wrong. Its Boundaries are the review section in Maintain guidance, which keeps every change to behaviour on the owner's word, and the owner's settings: the runtimes they agreed to have read and on which machines, and the two numbers that section leaves to them. Keep the settings on a situation page that the front page links, so that they change only through guidance. The schedule the owner sets stays with the scheduler, and the front page names its job.
- **Who runs it.** The owner chooses: a scheduled run of an agent that can read the sessions, reach the owner with each proposal where they can answer it, and edit the brain. Read a runtime on the machine that keeps its sessions; for another machine, run the reader there, for example over SSH from that machine's brain checkout.
- **First run.** Each last-read time starts where the owner says, such as the day the review starts. A past the owner wants read is a separate read they agree to.

The operation keeps, under its `records/`:

- a last-read time for each runtime on each machine, overwritten when it advances;
- each finding not yet entered: its occurrences, each with its runtime, session and time, so that a window read twice adds nothing twice, and the owner's words; how many runs have passed since it last occurred; and whether it awaits an answer, was declined, or was noted with open work;
- each change the review proposed that entered: what it changed, the correction it targets, when it entered, how many runs it has stayed away, and when it last recurred.

A run keeps nothing else: the owner's turns stay in each runtime's own records, and Git keeps what a record said before. A record quotes the owner's words, never a secret that appears in a turn.

## Each run

The operation's own procedure carries these out.

- Read each runtime on each machine from its last-read time with the reader, and advance that time to the `--until` its summary prints only when the reader exited 0 and those turns have been reviewed and recorded. Any other exit leaves the time where it was and is named to the owner. The reader reads only after that time, so a window passed over is never read.
- Add a finding's new occurrences to those already recorded, so that a correction made twice a week reaches the owner's number in the weeks it takes.
- Before proposing a change, read the guidance it would touch as it stands now, its home under [Maintain guidance](../../guidance/authoring.md), and the owner's open work on the subject.

## The reader

```sh
python3 read_turns.py claude --since 2026-10-18T11:00:00Z [--until …] [--root ~/.claude/projects]
python3 read_turns.py codex  --since 2026-10-18T11:00:00Z [--until …] [--home ~/.codex]
python3 read_turns.py hermes --since 2026-10-18T11:00:00Z [--until …] --user <owner's chat user id> [--label <owner's name>] [--db ~/.hermes/state.db]
```

It prints one JSON line per session with owner turns after `--since` and up to `--until`, oldest first: `runtime`, `session`, `cwd`, `leads`, and `turns`. Each turn has `at`; `text`, the owner's words (`--limit` characters); `before`, the end of the agent's reply it answered (`--context` characters), followed by the question and buttons of a next-step box the agent left; and `button: true` when the text is one of those buttons. `leads` holds the lines of the agent's first reply that name a lead linked from the `guidance/LEADS.md` of `--brain`, by default the brain the script sits in. A summary goes to stderr. Exit 0 means the runtime was read, even with no turns; 2 means it could not be, since a missing folder or store is unknown, not empty; anything else is a failure.

How it finds the owner's turns:

- **Claude Code:** `<root>/*/*.jsonl`, user records whose `origin.kind` is `human`, outside subagent sidechains. Each counts once by `uuid`, because a resumed or forked session copies earlier records into its new file under its own id; transcripts are read oldest first by creation time, where the system keeps one, so a turn stays with the session it was typed in. Context the app injects, such as `<system-reminder>`, is removed, and pasted text and command output are shortened to a marker. The desktop app's next-step box is a `wrap_up` tool call; a button the owner clicks arrives as a turn carrying the button's text.
- **Codex:** its thread store, `state_5.sqlite` and `thread_history_1.sqlite`, which Codex builds from its rollout files. User messages count in threads whose source is neither `exec` nor a subagent or reviewer (a JSON source). Voice turns arrive inside Codex's delegation tags.
- **Hermes:** `state.db`, user messages in sessions whose `user_id` is one given with `--user`, or that have no user and come from a local terminal source (`--local`, default `cli,tui` when `--user` is given). Cron and subagent sessions never count, even under the owner's id. Hermes stores its own notes as user messages too: rows opening with the scaffolding prefixes its context compressor and title generator list, such as `[CONTEXT COMPACTION` or `[IMPORTANT:`, and internal notifications are dropped, and a routing note, system note or steer marker around the owner's words is removed. In a shared channel a row starts with its speaker's label: with `--label`, outside direct messages, the owner's label is removed and rows labelled with another name are dropped; without it, labels stay in the text. A compressed session's continuation copies earlier rows, so a row counts once by its platform message id, or by its text and time.

## Check

- `python3 test_read_turns.py`, beside the script, exercises the reader against throwaway transcripts, thread stores and brains.
- Neither shows that the review works. Run it once on a past window where a correction is known to recur, writing no records, and check that it proposes that correction with its occurrences.

## Limits

- `--until` is cut to whole seconds and is ten minutes before now by default, so a turn still being written falls in the next window. A turn written to disk later than that after its own time is missed; resumed sessions copy earlier turns this way, and those are counted already. Whether Codex's store can lag its rollout files that long is not known.
- A store that cannot be opened read-only in place, as under some sandboxes, is read from a temporary copy of it and its journal, removed afterwards. The copy is kept only if neither file changed while it was made; a store that keeps changing is unreadable.
- A session is counted for the lead its first reply names, even if it later works as another; `before` shows the change.
- A reply the owner typed in Hermes that opens like its scaffolding, such as `[IMPORTANT: …]`, is dropped with it. With `--label`, a row in a shared Hermes session that opens with another bracketed word, such as `[WIP]`, is taken for someone else's and dropped.
- The formats are each runtime's own and change without notice; the tests pin the shapes the reader expects. Checked on 2026-10-21 against Claude Code 2.1.228, the Codex desktop app's 0.162 thread store, and Hermes 0.21.5.
