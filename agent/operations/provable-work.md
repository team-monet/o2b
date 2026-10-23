# Provable work

Governing parent: [Operations guide](README.md).

Read before setting up or running a provable-work operation, or relying on the [brain check](provable-work/check_brain.py) or the [inventory](provable-work/inventory.py).

Agent work can be trusted only as far as it can be proven. A provable-work operation keeps that proof current in a loop that does not end: every skill, script, CI check and unattended job gets an eval; every eval is itself evaluated; each finding is fixed by an agent or decided by the owner; then the loop runs again. The method is adapted from pstack's eval playbook (`cursor/plugins`, `pstack/`).

## Set it up

Run it as an [autopilot operation](../../autopilot/README.md), with the owner's go.

- **Mission and Boundaries.** The owner states the Mission, such as making agent work in their projects provable so that it needs less of their supervision. Its Boundaries, on situation pages the front page links, say in which repositories it may open pull requests and that those change only proof (checks, CI, scripts, verification skills); which brain files, if any, it may change directly; what it may spend, a judge included; and who merges.
- **Scope.** The owner names the projects in scope. Each gets an inventory and a record, below.
- **Direction first.** An eval needs a target. Each project's home states what the project is for, where it is heading, what working means as behaviour a user can observe, and what is out of scope. Agents draft it; the owner confirms it.
- **Who runs it.** A scheduled run of an agent that can run the tools, start other agents and reach the owner. Whoever builds or decides something does not verify it; a different agent checks.

## Each item's eval

| Item | Its eval |
|---|---|
| **Skill** | An [instruction test](#instruction-test). |
| **Script** | Tests that run it on a case where it must fail and on one where it must pass. |
| **CI check** | It has been seen red on a defect of the kind it exists for, real or planted in a copy. A job that has never gone red has no eval yet. |
| **Verification skill** | One end-to-end run that drives the real product and captures the evidence, and a map of the features users touch that it covers. |
| **Unattended job** | A check, independent of the job and run by something else, that its output exists and is right. |

An item with no eval is a gap; its eval says `none`, never a guess.

## Eval of eval

Ask these of every eval. It counts only once it has passed those that apply.

1. **Can it fail?** Remove the behaviour it guards, or plant the defect it exists for, confirm the change landed, and see it go red. An eval that cannot fail reads exactly like one that passed. Do it in a copy, never in the live brain or a checked-out branch, where sync would publish the broken copy.
2. **Does it measure like the real consumer?** Compare its verdicts on real inputs with those of whatever actually reads the thing: the renderer, parser, crawler, CI runner or agent runtime.
3. **Can its fixture show the effect?** Test data in which the failure cannot happen proves nothing about that failure.
4. **Does a second judge agree?** On a sample of its verdicts, a model of another family or the owner judges the same outputs. When they disagree, suspect the eval's criteria first.
5. **Did anything escape it?** A miss it should have caught counts against it and sends it back to question 1.

## Improve

- **An agent fixes** what the operation's Boundaries allow. **The owner decides** direction, a new dependency, a repository setting, a guidance or framework change, and more autonomy, through a report carrying `for_you`; their answer is recorded before it is acted on.
- **A mistake seen twice** is fixed at the highest level that works: remove the possibility; a type, script or check whose failure message names the fix; a test of the behaviour; and only for a judgement nothing can check, a written rule.
- **Every fix gets its own eval and eval of eval** before it is relied on.
- **Keep evals cheap.** One too slow or costly to run gets skipped, so note its cost in the inventory.

## Levels

A project's record summarises its standing as a level: 0, direction; 1, checks that fail; 2, proof of behaviour; 3, independent verification; 4, earned autonomy. A level holds only when its items' evals have passed eval of eval. Agents work unattended in a project, by scheduled runs or merges, only as far as the owner approves on the inventory's evidence.

## Records

The operation keeps, under its `records/`:

- **`inventory/<project>.md`**, one row per item, which the [inventory](#the-tools) compares with what exists:

  ```markdown
  ---
  source: brain
  exclude:
    - autopilot/out-of-scope/
  ---
  | Item | Kind | Eval | Eval of eval | Checked | Finding |
  |---|---|---|---|---|---|
  | `agent/operations/provable-work/check_brain.py` | script | 23 tests | fails; consumer; fixture | 2026-10-23 | — |
  | `agent/skills/release-notes` | skill | none | — | 2026-10-23 | no instruction test |
  ```

  `source` is `brain`, the brain the file is in, or `github:<owner>/<repo>`; `exclude` lists path prefixes out of scope; a workflow file's path excludes its jobs. **Eval of eval** names the questions passed (`fails`, `consumer`, `fixture`, `judge`, `no escapes`), or `failed: <question>`. A row whose item opens with a scheme, such as `cron:nightly-brief` or `file:~/bin/backup.sh`, is kept by hand: an unattended job or a file outside the brain.
- **`projects/<project>.md`**, the project's level and the check command and verification skill any session working there runs before calling work done.
- **`misses/<date>-<slug>.md`**, one per miss: agent work that passed its evals but was wrong, found by the owner, a reviewer, CI or production. Its frontmatter gives `project`, `found_by`, and `eval`, the item or eval that should have caught it or `none existed`; the body says what happened, how it was found, and links the change and evidence. The operation records the misses it finds; for other sessions to record theirs, the owner's guidance must route them here, such as through a skill they load. A worker reports a miss to its lead.

## Instruction test

How to tell whether a change to a skill, agent definition or guidance makes agents behave better before anything relies on it. An agent that knows it is being tested behaves differently, so the runs never learn they are one.

1. **Frame.** Name the change and write three to six concrete success criteria. Only the judge sees them.
2. **Task.** Write one task the instruction should handle, in the owner's words. No prompt, path or folder the runs can see says test, eval, judge, rubric, candidate or compare, and no run is asked which instructions it followed.
3. **Runs.** Run the task with the old version and with the new, in the same runtime and model, each in its own throwaway copy of the brain or repository, neither knowing of the other; two or more per side when one could be luck. A run usually loads the live brain through its startup pointer, so the old version can leak into a run meant to test the new one; check what each run actually loaded. Choose a task whose success is an answer, not a write, note each checkout's `HEAD` first, and afterwards check that the live brain and repositories are unchanged with both `git status` and `git log --stat <start>..HEAD`: a run that does not know it is a test may act for real, and sync may already have committed what it wrote.
4. **Judge.** One agent of another model family scores all outputs against the criteria in one pass, under neutral labels, without learning which side is which.
5. **Read it yourself.** Read every output, check which files each run opened, and grade what it did, never what it says. When you disagree with the judge, suspect the criteria.
6. **Decide.** Keep the change if it wins, or ties and is simpler; otherwise revert it.
7. **Record** the change, task, criteria, scores, your reading and the decision in the item's inventory row.

The test is an eval too: run it once more with the instruction removed from the new version, and its score must drop; on at least one test, the owner judges the same outputs.

## The tools

```sh
python3 check_brain.py [--root <brain>]
python3 inventory.py <inventory.md> [--check] [--root <brain>]
```

- **`check_brain.py`** reports broken links and anchors as GitHub renders them, resolving paths case-sensitively as a Linux runner does; skills without frontmatter, without a description or with one over 1024 characters, or whose name differs from their folder; stage pages missing from their index; and lines that match a secret format or [auto-sync](sync.md)'s credential pattern, which it reads from `sync.sh` so the two never drift; the secrets check never prints a matched value. It exits 1 on any problem; with no `--root` it checks the brain it is installed in.
- **`inventory.py`** lists what the inventory's `source` holds. In a brain: each skill, at any depth under `agent/skills/`; each script under `agent/skills/`, `agent/operations/` and every `autopilot/*/tools/`, in any subfolder, where a script is a file with a code extension (`.py`, `.sh`, `.bash`, `.zsh`, `.js`, `.mjs`, `.cjs`, `.ts`, `.mts`) or an executable file without an extension, and tests and installed packages are not; and each job of the brain's CI workflows. In a repository, through `gh`: each skill folder directly under `.claude/skills/`, `.cursor/skills/` or `.agents/skills/`, each script directly in top-level `scripts/`, and each CI job. Rows inside fenced code are examples, not rows. With `--check` it exits 1 when an item has no row or a row has no item, and 2, never a pass, when the inventory, the brain it names or the items cannot be read.

## Check

- `python3 -I test_check_brain.py` and `python3 -I test_inventory.py`, beside the scripts, run against throwaway brains and a stand-in for `gh`.
- On 2026-10-16 the brain check's anchors were compared with GitHub's rendered anchors on 120 files of a live brain. On 2026-10-23, with that brain's out-of-scope operation excluded, the inventory listed a live brain's items as its earlier, brain-specific version did, apart from three scripts in folders that version did not scan, and listed two repositories identically.

## Limits

- The brain check does not read reference-style links, wikilinks or links in raw HTML, and another renderer may form anchors differently from GitHub.
- The inventory does not follow symbolic links to folders inside the folders it scans, counts no code with an extension outside its list, and reads only top-level values and lists from frontmatter. A repository's scripts count only directly in its top-level `scripts/`, and there an extensionless file counts whatever its mode. A repository tree too large for one API answer is unavailable.
- Neither tool runs on its own: the operation's cycle, or a CI job the owner adds, runs them.
