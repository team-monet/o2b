# Gate hook

Governing parent: [Operations guide](README.md).

Read before installing the gate hook on a machine, naming a command on a stage page, or relying on the hook to deliver a page.

A situation page reaches an agent only when the agent opens it, so a gated command can run before its page is read. The [gate hook](gate-hook/gate_hook.py) closes that gap in Claude Code. Before a Bash command runs, it looks for stage pages whose frontmatter names that command under `before:`, and refuses the first such call in a session with the pages' text as the reason. The agent reads them and runs the command again unless a rule says not to; the same pages do not stop it again in that session unless they change. The hook delivers the page; following it stays with the agent.

A refusal is used because Claude Code shows context a `PreToolUse` hook adds beside the tool result, after the command has run; the reason for a refusal reaches the agent before it.

## Name a command on a page

```yaml
---
before: [git push, gh pr create]
---
```

Write each command as typed, program first, such as `git commit` or `git push --force`; a `- ` list under `before:` works too. An entry matches the command in the usual forms an agent writes: in a list after `&&`, `;` or a newline, inside `if`, `for` or `{ }`, behind environment assignments or a wrapper such as `sudo`, `timeout` or `xargs`, inside `bash -c`, `$( )` or backquotes, and with options between its words, as in `git -C dir commit`. It does not match the same words as text: in quotes, a comment, a here-document, or a single-quoted `$( )`. Nor does it match a different subcommand: `git stash push` is not `git push`. A word that starts with `-` matches that option anywhere after the words before it, as `--option=value`, or inside a cluster such as `-uf`. Matching reads the command line, not the shell, so an alias, a function, or a script that runs the command is not seen.

A page counts only when its index links it. Shared pages always apply; a project's pages apply when the session's working directory belongs to that project by `projects/INDEX.md`'s Path or Remote columns, the closest row winning as in `BRAIN.md`. Which pages name which commands is the owner's guidance; the framework names none.

## Install

Once per machine, with the owner's go, from the live brain rather than a development checkout:

```sh
python3 ~/.o2b/agent/operations/gate-hook/gate_hook.py --install
```

It adds one `PreToolUse` entry for Bash to `~/.claude/settings.json`, keeps the previous file as `settings.json.bak-o2b-<date>` with the same permissions, and changes nothing when the entry is already there. `--uninstall` removes that entry and any gate hook entry whose script no longer exists. Sessions started afterwards use it. `--check` reports what is wrong with the settings, and [runtime sync](skill-discovery.md#runtime-sync) reports the same in the sync log.

## Check

- `--explain "<command>" --cwd <dir>` prints the project matched and the pages the command would get, without refusing or recording anything.
- `python3 test_gate_hook.py`, beside the script, exercises matching, delivery and installation against throwaway brains.
- Neither shows that a session receives a page. In a fresh session, have the agent run a command a page names, in a scratch repository, and check that the refusal carries that page. Record the result and the Claude Code version in personal operation records.

## Limits

- It remembers deliveries per session and subagent in a folder of the user's under the system temporary directory, kept seven days. After the conversation is compacted, a page delivered earlier is not delivered again.
- One refusal carries about 9,000 characters of pages, below the size at which Claude Code moves hook text to a file. Pages beyond that come with the next attempt; a single page longer than that is cut, with its path for the rest.
- When it cannot record a delivery, it lets the command run and hands the pages over beside the result, with a warning to the user, rather than refusing every retry. Unreadable input or a missing brain also warns instead of passing silently. If its script is gone, the installed entry fails without refusing anything, and `--check` names it.
- It reads the indexes and pages on every Bash call, about 40 ms in a brain of 60 pages (2026-10-16). It parses only commands that name a gated program, and runs `git` only when a project page matches.
- It sees only Claude Code's Bash tool. A command run through another tool is not seen. It delivers guidance; it is not access control.
- Other runtimes document a comparable hook, untested here (their documentation, read 2026-10-16): Codex's `PreToolUse` in `~/.codex/hooks.json` takes the same input and refusal and runs once the hook is trusted; opencode plugins can stop a tool in `tool.execute.before`; Hermes plugins can block one in `pre_tool_call`. The framework sets up none of them.
