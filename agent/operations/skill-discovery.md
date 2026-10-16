# Skill discovery setup

Governing parent: [Operations guide](README.md).

Read before setting up a machine's agent runtimes or changing how they find the brain's skills and agent definitions. The [Skills guide](../skills/README.md) owns maintained skills and their format, and the [Agents guide](../agents/README.md) owns agent definitions. This procedure changes discovery paths, not skill authority or publication.

<a id="agent-definitions"></a>

## Runtime sync

[`runtime-sync/runtime_sync.py`](runtime-sync/runtime_sync.py) keeps every agent runtime installed on the machine in step with the brain. [Auto-sync](sync.md) runs it at the end of each sync that completes, so a sync that fails or is skipped leaves runtimes as they were until the next one. Run it by hand after setting up a machine, with `--dry-run` first to see what it would change:

```sh
python3 ~/.o2b/agent/operations/runtime-sync/runtime_sync.py --dry-run
```

| Runtime, installed when its folder exists | Skills | Agent definitions | Startup pointer it checks |
|---|---|---|---|
| Claude Code, `~/.claude` | one link per skill in `~/.claude/skills`, since Claude Code keeps its own synced skills in that folder | `~/.claude/agents` linked to `agent/agents` | `~/.claude/CLAUDE.md` |
| Codex, `~/.codex` | `~/.agents/skills` linked to `agent/skills` | generated as `~/.codex/agents/<name>.toml` | `~/.codex/AGENTS.override.md` when present, else `~/.codex/AGENTS.md` |
| opencode, `~/.config/opencode` | reads the two folders above, including subfolders | generated as `~/.config/opencode/agents/<name>.md` | `~/.config/opencode/AGENTS.md` when present, else `~/.claude/CLAUDE.md`, which opencode falls back to |
| Hermes, `~/.hermes` | its own configuration | none | `~/.hermes/SOUL.md` |

A definition is generated only when its frontmatter has a `name` of lowercase letters, digits and hyphens matching its file name, as Claude Code expects, and a `description`, followed by a prompt, and when Claude Code could load its frontmatter. Frontmatter Claude Code refuses, such as an unclosed quote, a line that is not `key: value`, an indented line that belongs to no key, or a `name` or `description` that is not text, is reported with the line at fault; what Claude Code tolerates by re-quoting, such as a `: ` inside a value or an unclosed `[`, is generated as written. A generated definition carries the description and prompt but no model, so each runtime uses its own default, and its first lines name the source to edit. The tool rewrites only files it generated from this brain and links that point into the brain, removes a generated file only once its source file is gone, and leaves alone any runtime folder that resolves inside the brain; a same-named file it did not generate is first renamed `<name>.<suffix>.bak-o2b-<date>`. It links only skills kept directly under `agent/skills/`. It reports, and leaves alone, a real folder where a whole-folder link belongs, and a runtime whose global instructions do not name this brain's `BRAIN.md`: O2B does not write those instructions for you. For the same reason it reports, and does not change, Claude Code user settings that do not run the brain's [gate hook](gate-hook.md) or run one whose script is gone.

## A new machine

Retrieve the personal brain and provision its declared dependencies. For every agent runtime installed there, set its startup pointer to the brain's `BRAIN.md`, move any skills or agent definitions it already holds into the brain, and run the tool. Then check each runtime in a fresh session: it reads `BRAIN.md`, lists the skills, and lists the agents. A change to these links or formats applies on every machine, not only the one where it was made. Record host paths, recovery instructions, and what each runtime showed in personal operation records.

Agents may cache discovery, so check a fresh session before claiming a new skill or agent is available. A filesystem check establishes shared files; it does not establish agent selection or successful skill execution. A project's own discovery folder may also point to the skills folder when the owner wants skills authored there to join the personal collection; project descriptions and guidance establish applicability.
