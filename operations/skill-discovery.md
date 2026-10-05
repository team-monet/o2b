# Skill discovery setup

Governing parent: [Operations guide](README.md).

Read before configuring or migrating an agent's personal skill discovery root. The [Skills guide](../skills/README.md) owns maintained skill storage and its format standard. This procedure changes discovery paths, not skill authority or publication.

Point each participating agent's personal discovery folder to the brain's maintained skills folder. For a brain installed at `~/.o2b`, the arrangement is:

```text
~/.o2b/skills/                 maintained skills and the entry guide
~/.agents/skills -> ~/.o2b/skills
~/.claude/skills -> ~/.o2b/skills
```

These are aliases of one directory. Creating, editing, renaming, or deleting a skill through any alias changes the same files. A new skill requires no individual link or synchronization job. Git saving and publication remain separate actions.

Inspect existing discovery folders before setup. Consolidate user-maintained skills with their supporting files, resolve name conflicts, and retain a recoverable source before replacing an existing folder. Leave runtime-managed directories with their runtime. Create a whole-root link only after verifying the maintained content. For absent destinations:

```sh
mkdir -p "$HOME/.agents" "$HOME/.claude"
ln -s "$HOME/.o2b/skills" "$HOME/.agents/skills"
ln -s "$HOME/.o2b/skills" "$HOME/.claude/skills"
```

Use the actual brain path and the discovery locations supported by the installed agents. An existing project discovery folder may also point to this root when the owner wants skills authored there to enter the same personal collection. Its contents then have the same visibility as the personal collection; project descriptions and guidance establish applicability.

Verify that every configured root resolves to this directory, supporting files remain accessible, and each installed agent discovers the skills without duplicate legacy registrations. Verify creation and editing through the aliases as well. Agents may cache discovery; check a refreshed catalog or a fresh session before claiming a new skill is available.

On another machine, retrieve the personal brain, provision its declared dependencies, and recreate the root links. Record host paths, recovery instructions, and observed discovery in personal operation records. A filesystem link check establishes shared files; it does not establish agent selection or successful skill execution.
