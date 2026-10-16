#!/usr/bin/env python3
"""Hand an agent the stage pages for a command before the command runs.

See ../gate-hook.md. Claude Code runs this as a PreToolUse hook on Bash. When a command matches
a `before:` entry in the frontmatter of a stage page that applies here, the first such call in a
session is refused and the refusal carries the page, so the agent has it before the command
runs. Set it up once per machine, and ask what a command would get:

    python3 gate_hook.py --install
    python3 gate_hook.py --explain "git commit -m x" [--cwd DIR]

Python 3.9 standard library only, so macOS's /usr/bin/python3 can run it.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve()
LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
PUNCTUATION = "();<>|&\n"
WRAPPERS = {"env", "command", "exec", "nohup", "sudo", "time"}
SHELLS = {"sh", "bash", "zsh"}
STATE_DAYS = 7


# Pages


def split_frontmatter(text):
    """(frontmatter lines, body) of a page; no frontmatter gives ([], text)."""
    lines = text.split("\n")
    if lines[0].rstrip() != "---":
        return [], text
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        return [], text
    return lines[1:end], "\n".join(lines[end + 1:]).lstrip("\n")


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def before_commands(frontmatter):
    """The commands a page's `before:` key names: `before: git commit`, `[a, b]`, or a `- ` list."""
    for i, line in enumerate(frontmatter):
        match = re.match(r"before:(.*)$", line)
        if not match:
            continue
        value = re.sub(r"\s+#.*$", "", match.group(1)).strip()
        if value.startswith("[") and value.endswith("]"):
            items = re.findall(r'"[^"]*"|\'[^\']*\'|[^,]+', value[1:-1])
        elif value:
            items = [value]
        else:
            items = []
            for item in frontmatter[i + 1:]:
                if not item.strip():
                    continue
                if not item.lstrip().startswith("- "):
                    break
                items.append(item.lstrip()[2:])
        return [c for c in (" ".join(unquote(item).split()) for item in items) if c]
    return []


def index_pages(index):
    """The pages an index links in its own stages/ folder, in index order."""
    try:
        text = index.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    stages = (index.parent / "stages").resolve()
    pages = []
    for target in LINK.findall(text):
        page = (index.parent / target).resolve()
        if page.parent == stages and page not in pages:
            pages.append(page)
    return pages


def read_page(page):
    """(commands, body) of a stage page; unreadable gives ([], "")."""
    try:
        text = page.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [], ""
    frontmatter, body = split_frontmatter(text)
    return before_commands(frontmatter), body


# Projects


def expand(path):
    path = re.sub(r"\s*\([^)]*\)\s*$", "", path.strip())
    return os.path.realpath(os.path.expanduser(path)) if path.startswith(("/", "~")) else None


def normal_remote(url):
    """`host/owner/repo` for a fetch URL or an index entry, lowercased."""
    url = url.strip()
    url = re.sub(r"^[a-z+]+://", "", url)
    url = re.sub(r"^[^@/]+@", "", url)
    url = re.sub(r"^([^/:]+):(?!\d)", r"\1/", url)
    url = re.sub(r"\.git$", "", url.rstrip("/"))
    return url.lower()


def project_rows(brain):
    """(folder, paths, remotes) for each row of projects/INDEX.md."""
    index = brain / "projects" / "INDEX.md"
    try:
        lines = index.read_text(encoding="utf-8").split("\n")
    except (OSError, UnicodeDecodeError):
        return []
    rows, columns = [], None
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if columns is None:
            columns = {name.lower(): i for i, name in enumerate(cells)}
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue

        def cell(name):
            i = columns.get(name)
            return cells[i] if i is not None and i < len(cells) else ""

        guide = LINK.search(cell("guide"))
        if not guide:
            continue
        folder = (index.parent / guide.group(1)).resolve().parent
        paths = [p for p in (expand(p) for p in cell("path").split(";")) if p]
        remotes = [normal_remote(r) for r in re.split(r"[;,]", cell("remote")) if r.strip()]
        rows.append((folder, paths, remotes))
    return rows


def git(cwd, *args):
    try:
        out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout if out.returncode == 0 else ""


def project_folders(brain, cwd):
    """The project folders whose row is closest to cwd: by path, or by the repository's remotes."""
    rows = project_rows(brain)
    if not rows or not cwd:
        return []
    here = os.path.realpath(cwd)
    best, found = -1, []

    def consider(depth, folder):
        nonlocal best, found
        if depth > best:
            best, found = depth, [folder]
        elif depth == best and folder not in found:
            found.append(folder)

    for folder, paths, _ in rows:
        for path in paths:
            if here == path or here.startswith(path.rstrip(os.sep) + os.sep):
                consider(len(path) + 1, folder)  # a path wins a tie with the repository holding it
    if any(remotes for _, _, remotes in rows):
        top = git(here, "rev-parse", "--show-toplevel").strip()
        urls = {normal_remote(u.split()[1]) for u in git(here, "remote", "-v").splitlines() if len(u.split()) > 1}
        if top and urls:
            for folder, _, remotes in rows:
                if urls & set(remotes):
                    consider(len(os.path.realpath(top)), folder)
    return found


def stage_pages(brain):
    """[(page, commands, body, project folder or None)] for every page that names a command."""
    indexes = [(brain / "guidance" / "STAGES.md", None)]
    indexes += [(folder / "guidance" / "STAGES.md", folder) for folder, _, _ in project_rows(brain)]
    pages = []
    for index, folder in indexes:
        for page in index_pages(index):
            commands, body = read_page(page)
            if commands:
                pages.append((page, commands, body, folder))
    return pages


# Commands


def strip_heredocs(command):
    """Drop here-document bodies, whose text is input rather than commands."""
    lines, out, i = command.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for match in HEREDOC.finditer(line):
            tag = match.group(2)
            while i < len(lines) and lines[i].strip() != tag:
                i += 1
            i += 1
    return "\n".join(out)


def tokens(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    return list(lex)


def simple_commands(command, depth=0):
    """Each simple command in a shell command line, as a token list."""
    command = strip_heredocs(command.replace("\\\n", " "))
    try:
        words = tokens(command)
    except ValueError:
        words = []
        for line in command.split("\n"):
            try:
                words += tokens(line)
            except ValueError:
                words += line.split()
            words.append("\n")
    found, current = [], []
    for word in words + ["\n"]:
        if word and set(word) <= set(PUNCTUATION):
            if current:
                found.append(current)
            current = []
        else:
            current.append(word)
    commands = []
    for words in found:
        while words and (ASSIGNMENT.match(words[0]) or os.path.basename(words[0]) in WRAPPERS):
            words = words[1:]
            while words and words[0].startswith("-"):
                words = words[1:]
        if not words:
            continue
        commands.append(words)
        if os.path.basename(words[0]) in SHELLS and depth < 3:
            for i, word in enumerate(words[1:-1], 1):
                if re.fullmatch(r"-[a-z]*c[a-z]*", word):
                    commands += simple_commands(words[i + 1], depth + 1)
                    break
    return commands


def matches(words, gate):
    """Whether a simple command runs `gate`, such as `git commit` or `git push --force`.

    Options and their values may sit between the gate's words (`git -C dir commit`); any other
    word breaks the match (`git stash push` is not `git push`). A gate word that is itself an
    option may appear anywhere after the words before it.
    """
    gate = gate.split()
    if not words or os.path.basename(words[0]) != gate[0]:
        return False
    rest, i = words[1:], 0
    for word in gate[1:]:
        if word.startswith("-"):
            if not any(t == word or t.startswith(word + "=") for t in rest[i:]):
                return False
            continue
        value_next = False
        while True:
            if i >= len(rest):
                return False
            token = rest[i]
            i += 1
            if token == word:
                break
            if token.startswith("-"):
                value_next = "=" not in token
            elif value_next:
                value_next = False
            else:
                return False
    return True


def due(brain, command, cwd):
    """[(page, gate, body)] for each shared or this project's page with a gate the command runs.

    The project is looked up only when a project page matches, so most commands cost no git call.
    """
    runs = simple_commands(command)
    hits = []
    for page, gates, body, folder in stage_pages(brain):
        gate = next((g for g in gates if any(matches(words, g) for words in runs)), None)
        if gate:
            hits.append((page, gate, body, folder))
    if any(folder for *_, folder in hits):
        here = project_folders(brain, cwd)
        hits = [hit for hit in hits if hit[3] is None or hit[3] in here]
    return [hit[:3] for hit in hits]


# Delivery


def state_file(state_dir, payload):
    key = "{}|{}".format(payload.get("session_id") or "no-session", payload.get("agent_id") or "")
    return state_dir / (hashlib.sha256(key.encode()).hexdigest()[:32] + ".json")


def default_state_dir():
    return Path(tempfile.gettempdir()) / "o2b-gate-hook-{}".format(os.getuid())


def prune(state_dir):
    cutoff = time.time() - STATE_DAYS * 86400
    for path in state_dir.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass


def fingerprint(page, body):
    return "{} {}".format(page, hashlib.sha256(body.encode()).hexdigest()[:16])


def message(hits, held=True):
    many = len(hits) > 1
    page, it = ("stage pages", "them") if many else ("stage page", "it")
    if held:
        lead = ("O2B held this command once so that the {page} for it reach{s} you before it runs. "
                "Read {it}, apply the rules that match this task, then run the command again unless a rule says not to. "
                "This session is not held again for {these}.").format(
                    page=page, s="" if many else "es", it=it, these="these pages" if many else "this page")
    else:
        lead = ("O2B could not hold this command, so the {page} for it arrive{s} after it ran. "
                "Read {it} and apply the rules that match this task.").format(page=page, s="" if many else "s", it=it)
    lines = [lead]
    for path, gate, body in hits:
        lines += ["", "=== {} (before `{}`) ===".format(path, gate), body.rstrip()]
    return "\n".join(lines)


def hook(brain, state_dir, stdin):
    try:
        payload = json.loads(stdin)
        command = (payload.get("tool_input") or {}).get("command")
    except (ValueError, AttributeError) as error:
        print(json.dumps({"systemMessage": "O2B gate hook could not read its input ({}); the command was not checked.".format(error)}))
        return 0
    if not isinstance(command, str) or not command.strip():
        return 0
    if not (brain / "BRAIN.md").is_file():
        print(json.dumps({"systemMessage": "O2B gate hook: {} is not a brain; stage pages were not checked.".format(brain)}))
        return 0
    hits = due(brain, command, payload.get("cwd") or os.getcwd())
    if not hits:
        return 0
    path = state_file(state_dir, payload)
    try:
        delivered = set(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else set()
    except (OSError, ValueError):
        delivered = set()
    new = [hit for hit in hits if fingerprint(hit[0], hit[2]) not in delivered]
    if not new:
        return 0
    try:
        state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        prune(state_dir)
        path.write_text(json.dumps(sorted(delivered | {fingerprint(p, b) for p, _, b in new})), encoding="utf-8")
    except OSError as error:
        # Refusing without remembering would refuse every retry, so hand the pages over beside the result instead.
        print(json.dumps({
            "systemMessage": "O2B gate hook could not record a delivery ({}); the stage pages arrive after the command instead of before it.".format(error),
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": message(new, held=False)},
        }))
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": message(new),
    }}))
    return 0


# Setup


def entry_command():
    return "python3 " + shlex.quote(str(SCRIPT))


def runs_this(handler, script=SCRIPT):
    command = handler.get("command") if isinstance(handler, dict) else None
    return isinstance(command, str) and (str(script) in command or os.path.realpath(script) in command)


def read_settings(path):
    settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(settings, dict):
        raise ValueError("it is not a JSON object")
    if not isinstance(settings.get("hooks", {}), dict) or not isinstance(settings.get("hooks", {}).get("PreToolUse", []), list):
        raise ValueError("its `hooks` or `hooks.PreToolUse` is not in the shape Claude Code documents")
    return settings


def write_settings(path, settings):
    if path.exists():
        backup = path.with_name("{}.bak-o2b-{}".format(path.name, datetime.date.today().isoformat()))
        n = 2
        while backup.exists():
            backup = path.with_name("{}.bak-o2b-{}-{}".format(path.name, datetime.date.today().isoformat(), n))
            n += 1
        backup.write_bytes(path.read_bytes())
        print("gate-hook: kept the previous settings as {}".format(backup))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".o2b-tmp")
    temporary.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def install(path):
    try:
        settings = read_settings(path)
    except (OSError, ValueError) as error:
        print("gate-hook: {} cannot be read as settings ({}); nothing was changed".format(path, error))
        return 1
    groups = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any(runs_this(h) for g in groups if isinstance(g, dict) for h in g.get("hooks") or []):
        print("gate-hook: {} already runs {} before Bash commands".format(path, SCRIPT))
        return 0
    groups.append({"matcher": "Bash", "hooks": [{"type": "command", "command": entry_command()}]})
    write_settings(path, settings)
    print("gate-hook: {} now runs {} before Bash commands; start a new session to use it".format(path, SCRIPT))
    return 0


def uninstall(path):
    try:
        settings = read_settings(path)
    except (OSError, ValueError) as error:
        print("gate-hook: {} cannot be read as settings ({}); nothing was changed".format(path, error))
        return 1
    hooks = settings.get("hooks", {})
    groups = hooks.get("PreToolUse", [])
    kept = []
    for group in groups:
        handlers = group.get("hooks") if isinstance(group, dict) and isinstance(group.get("hooks"), list) else None
        if handlers is None:
            kept.append(group)
            continue
        rest = [h for h in handlers if not runs_this(h)]
        if rest:
            kept.append(dict(group, hooks=rest))
    if kept == groups:
        print("gate-hook: {} does not run {}".format(path, SCRIPT))
        return 0
    if kept:
        hooks["PreToolUse"] = kept
    else:
        del hooks["PreToolUse"]
        if not hooks:
            del settings["hooks"]
    write_settings(path, settings)
    print("gate-hook: removed {} from {}".format(SCRIPT, path))
    return 0


def explain(brain, command, cwd):
    folders = project_folders(brain, cwd)
    print("project: " + (", ".join(str(f) for f in folders) if folders else "none matched; shared pages only"))
    hits = due(brain, command, cwd)
    if not hits:
        print("no stage page names this command in `before:`")
    for page, gate, _ in hits:
        print("{}  (before `{}`)".format(page, gate))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hand an agent the stage pages for a command before it runs.")
    parser.add_argument("--brain", help="the live brain (default: the one holding this script)")
    parser.add_argument("--state-dir", help="where deliveries are remembered per session (default: a folder in the temporary directory)")
    parser.add_argument("--explain", metavar="COMMAND", help="list the pages COMMAND would get, without refusing anything")
    parser.add_argument("--cwd", default=os.getcwd(), help="working directory for --explain (default: this one)")
    parser.add_argument("--install", action="store_true", help="add this hook to Claude Code's user settings")
    parser.add_argument("--uninstall", action="store_true", help="remove this hook from Claude Code's user settings")
    parser.add_argument("--settings", default=str(Path.home() / ".claude" / "settings.json"), help="settings file for --install and --uninstall")
    args = parser.parse_args(argv)
    brain = Path(args.brain).expanduser().resolve() if args.brain else SCRIPT.parents[3]
    if args.install:
        return install(Path(args.settings).expanduser())
    if args.uninstall:
        return uninstall(Path(args.settings).expanduser())
    if args.explain is not None:
        return explain(brain, args.explain, args.cwd)
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    return hook(brain, state_dir, sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main())
