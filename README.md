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

The framework supplies `BRAIN.md`, `MASTER-PLAN.md`, and operating guides. The personal repository supplies populated principles, shared and project stage indexes and rules, project indexes and content, knowledge notes, source records, workstreams, inbox entries, and capability bundles. Shared rules live under root `guidance/`; project-specific rules live under `projects/<project>/guidance/`. The framework must not publish populated personal files.

## Build your brain

Begin with [BRAIN.md](BRAIN.md), then add only what you actually need:

- Put your admitted principles and stage rules under [Guidance](guidance/README.md).
- Give an actual project a README and add it to your personal `projects/INDEX.md`, following [Projects](projects/README.md).
- Retain useful knowledge and source relationships through [Knowledge](knowledge/README.md) and [Sources](sources/README.md).
- Use [Work](work/README.md) for durable workstreams and an agent inbox. The guide includes copyable formats; create personal files on first use, not empty registries in advance.
- Maintain your agent skills under [Skills](skills/README.md), including personal project workflows, and link participating agents' whole discovery roots there. Skills do not require stage bindings.
- Preserve reusable bundles, scripts, and dependencies through [Capabilities](capabilities/README.md). Keep externally maintained project tools and team-owned skills with their projects.

Configure each participating agent's native startup instructions to read the absolute path to your live `BRAIN.md` and follow its guidance-loading instructions. If the entry cannot be read, the agent must report that rather than assume its guidance. O2B does not install this pointer for you. Observe a fresh session before claiming the runtime loads it; record your configuration and evidence under [Operations](operations/README.md).

A rule that names a skill or script also requires access to that capability and its dependencies. Cloning this framework does not install your personal skills, project scripts, credentials, or runtime dependencies. Follow the [capability guide](capabilities/README.md) to locate and verify them before claiming the rule is usable on a new machine.

## Review a shared update

Adopt updates explicitly; there is no automatic sync or update script. Fetch `upstream` in a disposable checkout of the personal repository, inspect and merge a selected upstream revision there, then validate the combined personal result. Publish the reviewed personal `main` only after conflicts and content migrations are settled. Fast-forward the live checkout from personal `origin/main` only when it is clean and has no unpushed work.

The update sequence, safeguards, recovery boundary, and migration from project-local guidance are owned by [operations/updates.md](operations/updates.md). A framework release that changes personal file locations must include an explicit migration; Git cannot infer meaning.

Begin everyday use at [BRAIN.md](BRAIN.md). Framework changes follow the [master plan](MASTER-PLAN.md).
