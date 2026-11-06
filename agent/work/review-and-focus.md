# Review and focus

Governing parent: [Work guide](README.md).

Read this guide when the owner asks to sort what they have captured, review their open work, choose or change their focus, or get help with it, and when you settle the step the focus's next-action line names. It applies two methods, David Allen's *Getting Things Done* to keep open work trustworthy and Gary Keller's *The ONE Thing* to choose what matters most, through the homes the Work guide already defines. It is optional and runs when the owner asks: no schedule, reminder, or second task list comes with it.

## Who does what

The owner decides what they commit to and what matters most. Agents make those decisions cheap and carry out what is committed.

| Moment | The owner | An agent |
|---|---|---|
| Capture | Says or writes the thought | Puts it in the right inbox, with no commitment |
| Clarify | Accepts or declines each proposed commitment | Proposes a home and who moves it, with a recommendation |
| Review | Judges what is still worth doing | Checks records against trackers and finds what is finished, stuck, or stale |
| Focus | Chooses the one outcome | Offers candidates with what each would make easier or unnecessary, and records the choice |
| Engage | Takes the `(you)` steps | Takes the `(agent)` steps when asked, and prepares each `(you)` step so it costs the owner as little as it can |

## Capture

Anything the owner wants off their mind becomes a dated line in the inbox of the scope it belongs to, as the [inbox shape](README.md#inbox) shows, with `owner` as its source. Several thoughts become several lines, each in its own scope; a thought with no clear scope goes to `personal/INBOX.md`. A capture commits no one, starts no work, and does not touch the focus. It stays unsorted, however tentative or urgent it sounds: whether it is `someday:` is the owner's decision when clarifying.

## Clarify

Take the captures the owner wants sorted, and propose what each one is:

| It is | Its home |
|---|---|
| An outcome that takes several steps | A workstream whose objective states it and whose first step is the next action |
| One action | A step in the workstream it serves, or a short workstream of its own; done on the spot instead if an agent can finish it now and the owner agrees |
| Already tracked elsewhere | A link to the tracker where the work needs it, never a copy of its state |
| Waiting on someone else | A step tagged `(waiting: <who>, since <date>)` |
| A hard date | `due:` on its workstream, and the owner's calendar if they keep one |
| Not now, perhaps later | The same inbox line, marked `someday:` |
| Worth keeping, nothing to do | A knowledge note |
| Nothing | Removed |

A proposal creates nothing. An item becomes a commitment only when the owner accepts it, and until they decide it stays in its inbox. Verify the destination before removing an entry, as the [inbox section](README.md#inbox) requires.

## Review

Agree the scope first: named projects, or everything. Start with what changes most for the owner, stop where the rest changes too little to be worth their attention, and say what was left.

Look for:

- captures still to clarify, leaving `someday:` lines alone unless the owner asks about them;
- active workstreams with no concrete next step, or whose steps do not say who moves them;
- steps grown into logs, whose results belong where they are used, leaving only what is next;
- `(waiting: …)` steps that have gone quiet, with how long and a suggested nudge;
- work linked to a tracker, compared with the tracker's current state where access allows, naming anything that could not be checked rather than treating it as fine;
- finished items and workstreams to retire, with the evidence that they are finished;
- `for_you` items that no longer meet the test in `BRAIN.md`'s habit "Hand things to the owner": work that cannot move, or a cost that keeps running while it waits. That habit lets any agent take them out.

Do without asking what existing rules already allow, such as adding a tag a step's own words settle or taking out such a `for_you` item, and say what you did. Bring the rest one item at a time; when several belong together, use a table with a recommendation on every row. End by asking whether the focus still holds, or whether to choose one.

## Focus

The focus is the one outcome that matters most for the horizon the owner chooses, by default this week: the one whose completion would make the rest easier or unnecessary. It lives in the `Current focus` section of `SNAPSHOT.md`, links to the record that owns the work, and names its next action. It is not the only active work: everything else stays open in its own record, and what waits on the owner stays in For you.

- **Only the owner's explicit choice changes the outcome.** Saying "go with your recommendation" is a choice; silence is not. An agent that thinks the focus should change says so when the owner plans or reviews, and does not edit it.
- **It is not `for_you`, and not a deliverable.** `for_you` means something is waiting on the owner now and says nothing about importance. A session's deliverable is what that session delivers, which may have nothing to do with the focus. Neither one sets, changes, or stands in for the focus.
- **Candidates come from outcomes the owner already holds.** Offer two or three, each with what it would make easier or unnecessary, plus your recommendation and what it turns on. A new outcome may be proposed, but it must be labelled as new.
- **The next action comes from the record and speaks only for this outcome.** Show the outcome's next `(you)` step. When there is none, show an `(agent)` step the owner can ask for, because it does not start unasked: "Next for you: ask for the announcement draft (step-02)." Failing that, show what they are waiting on: "Next for you: nothing on this outcome until Acme replies (step-03)." Name an untagged step as unknown rather than counting it as not theirs. When the record has no concrete next action, propose one and label it as proposed until the owner accepts it. Whoever settles the step this line names moves the line.
- **Changing it costs one line.** The owner can say so in any session; a review is not required. The agent replaces the section in place with the new date, because Git keeps the old one. A focus past its horizon still stands until the owner says otherwise.
- **Ending it is the owner's call too.** When the owner says the outcome is finished, the section says so with the date, and nothing takes its place until they choose. When its last step settles and the outcome is plainly not reached, the record stays and you propose its next step, labelled as proposed. When the outcome looks reached, when you cannot tell, or when its record is already gone, keep the outcome's text without a link to any removed record, and make the next action asking the owner whether it is finished.

## Engage

`BRAIN.md`'s habit "Keep the owner's focus" says what to show when the owner plans. The other obligations it means are things like `for_you` items and near due dates.

Asked to help with the focus, take the `(agent)` steps in its record and prepare the next `(you)` step: gather the facts, lay out the options with a recommendation, write the draft, or find the exact command. New ideas that come up meanwhile are captured, not followed.

## Example

This works in plain Markdown, without a view plugin, calendar, or scheduler:

```markdown
<!-- personal/INBOX.md -->
- 2026-11-02: someday: a family trip to Japan (owner)

<!-- projects/beta/workstreams/launch.md -->
**Objective:** First ten paying customers on the beta.

## Open steps
- step-01 (you): Choose the launch date; the options and a recommendation are in launch-options.md.
- step-02 (agent): Draft the announcement.
- step-03 (waiting: Acme, since 2026-11-03): Their signed quote.

<!-- SNAPSHOT.md -->
## Current focus

_Chosen 2026-11-02, for this week._ [First ten paying customers](projects/beta/workstreams/launch.md), because it settles whether the other two products are worth continuing.

**Next for you:** choose the launch date (step-01).
```
