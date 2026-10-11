# Autopilot

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when starting an operation, or when a task runs or continues one. An operation runs on its own, usually on a schedule, toward a Mission the owner gave it, and the owner monitors it from the snapshot. The shared framework supplies this guide; operations belong to the personal brain.

## An operation's folder

Each operation lives in `autopilot/<name>/`. Its front page, `README.md`, is the progress document any agent continues from: read it in full before acting. Its frontmatter `status:`, such as `running` or `paused`, is what the snapshot's Running view shows. The front page names the operation's project, which keeps the domain knowledge, and links the guidance that holds its Boundaries. Add the operation's folder to that project's row in `projects/INDEX.md`, so a session working in it identifies the project.

Only the Mission and the Boundaries carry the owner's authority. The Mission is stated on the front page. Boundaries stay in guidance, on the project's or shared situation pages, so they change only through guidance. Everything else, such as the team, rules, scoring, and Objectives, is written by the agents and evolves as the operation learns.

Front-page sections are the operation's own: commonly Mission, Boundaries, Team, Rules, Scoring, Route (how to reach outside state), and Now (a view of open Objectives). Run procedures, such as a scheduled cycle, sit beside the front page and are linked from it. Other parts are created when their first item arrives:

| Part | Holds |
|---|---|
| `team/<member>.md` | A team member adopted from an [agent definition](../agent/agents/README.md), with `source`, `version`, `adopted`, and `status` properties |
| `objectives/<date>-<slug>.md` | One Objective, with `status` (`open`, `waiting`, `done`, `dropped`), `opened`, `closed`, `waiting_on`, and `waiting_since` properties |
| `records/<kind>/` | What the operation keeps track of, in Markdown |
| `reports/<date>-<slug>.md` | A report the owner needs to read, carrying `for_you` |
| `drafts/<date>-<slug>.md` | Something the owner must send, ready to send, carrying `for_you` |
| `tools/` | The operation's code and its tests |

## Writing

Write frequent changes to new files, one writer per file; the front page changes when the operation changes, not on every run. Keep nothing for the record: remove a replaced team member, rule, or score; remove a settled Objective once its result is where it is used; and remove a report or draft once the owner no longer needs it. Do not accumulate daily lines; compute charts from records. Read outside live state fresh from its source rather than copying it in. The scheduler that runs the operation keeps its schedules and message delivery; the front page names those jobs.
