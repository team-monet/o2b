# O2B

O2B is a starting framework anyone can clone to build their own human-owned Markdown brain. It supplies the fundamentals for humans and replaceable agents to discover guidance, reuse knowledge, and continue work through ordinary files.

The shared framework and each person's live brain remain separate while preserving common Git history. The framework ships operating conventions and examples; each person supplies their own content, authority, and runtime setup.

| Repository | Role |
|---|---|
| `team-monet/o2b` | Shared structure and operating guides |
| A private personal repository | Installed framework plus private guidance, projects, knowledge, and work |

The personal repository is independent rather than a GitHub fork. Its `origin` is the private repository and its `upstream` is `team-monet/o2b`. Creating it from the framework history preserves common ancestry, so framework changes can be reviewed and merged normally.

## Initialize a personal repository

Create an empty private repository, choose a live path, then start from the shared history:

```sh
live_path="/path/to/live-o2b"
personal_remote="git@github.com:account/o2b.git"
git clone git@github.com:team-monet/o2b.git "$live_path"
git -C "$live_path" remote rename origin upstream
git -C "$live_path" remote set-url --push upstream /dev/null/o2b-push-disabled
git -C "$live_path" remote add origin "$personal_remote"
git -C "$live_path" push -u origin main
```

Without an SSH key, clone over HTTPS instead: replace the `git clone` line with `git clone https://github.com/team-monet/o2b.git "$live_path"`.

Scheduled [auto-sync](../agent/operations/sync.md) and [runtime sync](../agent/operations/skill-discovery.md#runtime-sync) are macOS (launchd) only: the installer is a launchd job, and the scripts are tested on macOS and Linux runners but not installed elsewhere. Everything else here is plain Markdown and Git.

The framework supplies `BRAIN.md`, the master plan, and operating guides. The personal repository supplies the snapshot, populated principles, leads, shared and project stage indexes and rules, agent definitions, skills, project indexes and content, autopilot operations, knowledge notes, source records, workstreams, and inbox entries. Shared rules live under root `guidance/`; project-specific rules live under `projects/<project>/guidance/`. The framework must not publish populated personal files.

## Build your brain

The root holds what you read or rule on; agents' working material lives under `agent/`. Begin with [BRAIN.md](../BRAIN.md), then add only what you actually need:

- Create `SNAPSHOT.md` at the root from the skeleton in the [Work guide](../agent/work/README.md#snapshot): the one page you read to see what needs you.
- Put your admitted principles, leads, and situation pages under [Guidance](../guidance/README.md).
- Keep material about your own life outside projects under [Personal](../personal/README.md).
- Keep the running of a company under [Companies](../companies/README.md), apart from its products.
- Give an actual project a README and add it to your personal `projects/INDEX.md`, following [Projects](../projects/README.md).
- Run operations that work on their own toward a Mission you give under [Autopilot](../autopilot/README.md).
- Retain useful knowledge and source relationships through [Knowledge](../agent/knowledge/README.md) and [Sources](../agent/sources/README.md).
- Use [Work](../agent/work/README.md) for durable workstreams and an agent inbox. The guide includes copyable formats; create personal files on first use, not empty registries in advance. When open work outgrows what you can hold in your head, [Review and focus](../agent/work/review-and-focus.md) helps you sort it, review it, and choose the one outcome that matters most.
- Keep agent definitions under [Agents](../agent/agents/README.md), and maintain your agent skills, with their scripts and dependencies, under [Skills](../agent/skills/README.md), including workflows, and link participating agents' whole discovery roots there. Skills do not require stage bindings. Keep externally maintained project tools and team-owned skills with their projects.

Configure each participating agent's native startup instructions to read the absolute path to your live `BRAIN.md` and follow its guidance-loading instructions. If the entry cannot be read, the agent must report that rather than assume its guidance. O2B does not install this pointer for you. Observe a fresh session before claiming the runtime loads it; record your configuration and evidence under [Operations](../agent/operations/README.md). A chat assistant such as ChatGPT or Claude reads the brain from GitHub instead of a local path; [chat assistants](../agent/operations/chat-assistants.md) covers its pointer and limits.

A rule that names a skill or script also requires access to that capability and its dependencies. Cloning this framework does not install your personal skills, project scripts, credentials, or runtime dependencies. Follow the [skills guide](../agent/skills/README.md) to locate and verify them before claiming the rule is usable on a new machine.

## Review a shared update

Adopt updates explicitly; no script merges a framework update for you. [Auto-sync](../agent/operations/sync.md) only commits and pushes your own live checkout, and [runtime sync](../agent/operations/skill-discovery.md#runtime-sync) only links skills and agent definitions into each agent runtime. Both are optional and installed on a schedule on macOS only; elsewhere, run `runtime_sync.py` by hand and push your own changes. Fetch `upstream` in a disposable checkout of the personal repository, inspect and merge a selected upstream revision there, then validate the combined personal result. Publish the reviewed personal `main` only after conflicts and content migrations are settled. Fast-forward the live checkout from personal `origin/main` only when it is clean and has no unpushed work.

The update sequence, safeguards, recovery boundary, and migration from project-local guidance are owned by [agent/operations/updates.md](../agent/operations/updates.md). A framework release that changes personal file locations must include an explicit migration; Git cannot infer meaning.

Begin everyday use at [BRAIN.md](../BRAIN.md). Framework changes follow the [master plan](../agent/MASTER-PLAN.md).
