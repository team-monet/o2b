# Gate hook

Governing parent: [Operations guide](README.md).

Read before installing the gate hook on a machine, naming a command on a stage page, or relying on the hook to deliver a page.

A situation page reaches an agent only when the agent opens it, so a gated command can run before its page is read. The [gate hook](gate-hook/gate_hook.py) closes that gap in Claude Code. Before a Bash command runs, it looks for stage pages whose frontmatter names that command under `before:`, and refuses the first such call in a session with the pages' text as the reason. The agent reads them and runs the command again if they allow it; the same pages do not stop it again in that session unless they change. The hook delivers the page; following it stays with the agent.

A refusal is used because Claude Code shows context a `PreToolUse` hook adds beside the tool result, after the command has run; the reason for a refusal reaches the agent before it.

## Name a command on a page

```yaml
---
before: [git push, gh pr create]
---
```

Write each command as typed, program first, such as `git commit` or `git push --force`; a `- ` list under `before:` works too. An entry matches wherever the command runs in a command line: after `cd dir &&`, behind environment assignments, inside `bash -c` or `$( )`, and with options between its words, as in `git -C dir commit`. It does not match the same words inside quoted text or a here-document, or a different subcommand: `git stash push` is not `git push`. A word that starts with `-` matches that option anywhere after the words before it, including its `--option=value` form.

A page counts only when its index links it. Shared pages always apply; a project's pages apply when the session's working directory belongs to that project by `projects/INDEX.md`'s Path or Remote columns, the closest row winning as in `BRAIN.md`. Which pages name which commands is the owner's guidance; the framework names none.

## Install

Once per machine, with the owner's go, after the brain is in place:

```sh
python3 ~/.o2b/agent/operations/gate-hook/gate_hook.py --install
```

It adds one `PreToolUse` entry for Bash to `~/.claude/settings.json`, keeps the previous file as `settings.json.bak-o2b-<date>`, and changes nothing when the entry is already there. `--uninstall` removes only that entry. Sessions started afterwards use it. [Runtime sync](skill-discovery.md#runtime-sync) reports a Claude Code whose user settings do not run it.

## Check

- `--explain "<command>" --cwd <dir>` prints the project matched and the pages the command would get, without refusing or recording anything.
- `python3 test_gate_hook.py`, beside the script, exercises matching, delivery and installation against throwaway brains.
- Neither shows that a session receives a page. In a fresh session, have the agent run a command a page names, in a scratch repository, and check that the refusal carries that page. Record the result and the Claude Code version in personal operation records.

## Limits

- It remembers deliveries per session and subagent in a folder under the system temporary directory, kept seven days. After the conversation is compacted, a page delivered earlier is not delivered again.
- When it cannot record a delivery, it lets the command run and hands the pages over beside the result, with a warning to the user, rather than refusing every retry. Unreadable input or a missing brain also warns instead of passing silently.
- It reads the indexes and pages on every Bash call, about 40 ms in a brain of 60 pages (2026-10-16), and runs `git` only when a project page matches.
- It sees only Claude Code's Bash tool. A command run through another tool, a script file, or an alias is not seen. It delivers guidance; it is not access control.
- Other runtimes document a comparable hook, untested here (their documentation, read 2026-10-16): Codex's `PreToolUse` in `~/.codex/hooks.json` takes the same input and refusal and runs once the hook is trusted; opencode plugins can stop a tool in `tool.execute.before`; Hermes plugins can block one in `pre_tool_call`. The framework sets up none of them.
