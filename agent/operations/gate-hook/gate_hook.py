#!/usr/bin/env python3
"""Hand an agent the stage pages for a command before the command runs.

See ../gate-hook.md. Claude Code runs this as a PreToolUse hook on Bash. When a command matches
a `before:` entry in the frontmatter of a stage page that applies here, the first such call in a
session is refused and the refusal carries the page, so the agent has it before the command
runs. Set it up once per machine, check it, and ask what a command would get:

    python3 gate_hook.py --install
    python3 gate_hook.py --check
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
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve()
LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
HEREDOC = re.compile(r"<<(-?)[ \t]*((?:[^\s'\"\\<>|&;()]|\\.|'[^'\n]*'|\"[^\"\n]*\")+)")
QUOTING = re.compile(r"\\(.)|'([^']*)'|\"([^\"]*)\"")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
PUNCTUATION = "();<>|&\n"
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
WRAPPERS = {"env", "command", "exec", "nohup", "sudo", "time", "timeout", "nice", "xargs", "stdbuf"}
SHELLS = {"sh", "bash", "zsh"}
STATE_DAYS = 7
STATE_NAME = re.compile(r"[0-9a-f]{32}\.json")
REASON_LIMIT = 9000  # Claude Code moves hook text over 10,000 characters to a file; stay under it


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
        urls = {normal_remote(u.split()[1]) for u in git(here, "remote", "-v").splitlines() if u.endswith("(fetch)")}
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


def backquote_end(text, i):
    """Where the backquote opened at i closes."""
    end = i + 1
    while end < len(text) and text[end] != "`":
        end += 2 if text[end] == "\\" else 1
    return end


def expansions(body):
    """The `$( )` and backquote texts that bash runs in a here-document body whose delimiter is unquoted."""
    found, i, n = [], 0, len(body)
    while i < n:
        if body[i] == "\\":
            i += 2
        elif body.startswith("$(", i):
            _, _, end = read_shell(body, i + 2, nested=True)
            found.append(body[i + 2:end - 1])
            i = end
        elif body[i] == "`":
            end = backquote_end(body, i)
            found.append(body[i + 1:end])
            i = end + 1
        else:
            i += 1
    return found


def read_shell(text, i=0, nested=False):
    """Read shell text the way bash quotes it.

    Returns (kept, substitutions, end): the text without comments, here-document bodies and
    command substitutions; the text inside each `$( )` or backquote pair that bash would run,
    which is read in turn; and, for a nested read, where its closing `)` ends. Single quotes and
    here-document bodies are input, so nothing in them counts, except the substitutions bash
    runs in a body whose delimiter is unquoted.
    """
    kept, found, pending, quote, depth, n = [], [], [], None, 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and quote != "'":
            kept.append(text[i:i + 2])
            i += 2
            continue
        if quote == "'":
            quote = None if c == "'" else quote
            kept.append(c)
            i += 1
            continue
        if text.startswith("$(", i):
            _, _, end = read_shell(text, i + 2, nested=True)
            found.append(text[i + 2:end - 1])
            kept.append(" ")
            i = end
            continue
        if c == "`":
            end = backquote_end(text, i)
            found.append(text[i + 1:end])
            kept.append(" ")
            i = end + 1
            continue
        if quote == '"':
            quote = None if c == '"' else quote
            kept.append(c)
            i += 1
            continue
        if c in "'\"":
            quote = c
        elif c == "#" and (i == 0 or text[i - 1] in " \t\n;&|()"):
            end = text.find("\n", i)
            i = n if end == -1 else end
            continue
        elif c == "\n" and pending:
            kept.append(c)
            i += 1
            for tag, expands, tabs in pending:
                body = []
                while i < n:
                    end = text.find("\n", i)
                    end = n if end == -1 else end
                    line, i = text[i:end], end + 1
                    if (line.lstrip("\t") if tabs else line) == tag:
                        break
                    body.append(line)
                if expands:
                    found += expansions("\n".join(body))
            pending = []
            continue
        elif text.startswith("<<", i) and not text.startswith("<<<", i) and text[i - 1:i] != "<":
            match = HEREDOC.match(text, i)
            word = match.group(2) if match else ""
            if word and not (word[0].isdigit() and word.isalnum()):
                # The delimiter is the word after quote removal; any quoting keeps the body unexpanded.
                tag = QUOTING.sub(lambda m: next(g for g in m.groups() if g is not None), word)
                pending.append((tag, tag == word, bool(match.group(1))))
                kept.append(match.group(0))
                i = match.end()
                continue
        elif nested and c == "(":
            depth += 1
        elif nested and c == ")":
            if depth == 0:
                return "".join(kept), found, i + 1
            depth -= 1
        kept.append(c)
        i += 1
    return "".join(kept), found, n + 1 if nested else n


def tokens(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    return list(lex)


def simple_commands(command, depth=0):
    """Each simple command in a shell command line, as a token list."""
    kept, substituted, _ = read_shell(command.replace("\\\n", " "))
    # A `#` inside a word is text, not a comment, but shlex would start a comment there.
    lexable = re.sub(r"(?<=[^\s;&|()<>])#", r"\\#", kept)
    try:
        words = tokens(lexable)
    except ValueError:
        words = []
        for line in lexable.split("\n"):
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
        while words and (ASSIGNMENT.match(words[0]) or words[0] in KEYWORDS):
            words = words[1:]
        if not words:
            continue
        commands.append(words)
        shell = words
        if os.path.basename(words[0]) in WRAPPERS:
            shell = next((unwrapped(words, s) for s in SHELLS if unwrapped(words, s)), [])
        if shell and os.path.basename(shell[0]) in SHELLS and depth < 3:
            for i, word in enumerate(shell[1:-1], 1):
                if re.fullmatch(r"-[a-z]*c[a-z]*", word):
                    commands += simple_commands(shell[i + 1], depth + 1)
                    break
    if depth < 3:
        for inner in substituted:
            commands += simple_commands(inner, depth + 1)
    return commands


def has_option(tokens, word):
    """Whether `word`, an option, is among the tokens: as itself, as `--option=value`, or inside `-abc`."""
    for token in tokens:
        if token == word or token.startswith(word + "="):
            return True
        if re.fullmatch(r"-[A-Za-z]", word) and re.fullmatch(r"-[A-Za-z]+", token) and word[1] in token[1:]:
            return True
    return False


def unwrapped(words, program):
    """The command a wrapper runs: what follows its options, their values, counts, and other wrappers."""
    value_next = False
    for i, word in enumerate(words[1:], 1):
        if os.path.basename(word) == program:
            return words[i:]
        if word.startswith("-"):
            value_next = "=" not in word and (word.startswith("--") or len(word) == 2)
        elif value_next or ASSIGNMENT.match(word) or re.fullmatch(r"\d+(\.\d+)?[smhd]?", word) or os.path.basename(word) in WRAPPERS:
            value_next = False
        else:
            return []
    return []


def matches(words, gate):
    """Whether a simple command runs `gate`, such as `git commit` or `git push --force`.

    Options and their values may sit between the gate's words (`git -C dir commit`); any other
    word breaks the match (`git stash push` is not `git push`). A gate word that is itself an
    option may appear anywhere after the words before it. A wrapper such as `sudo` or `timeout`
    runs the gate's program wherever it follows.
    """
    gate = gate.split()
    if words and os.path.basename(words[0]) in WRAPPERS:
        words = unwrapped(words, gate[0])
    if not words or os.path.basename(words[0]) != gate[0]:
        return False
    rest, i = words[1:], 0
    for word in gate[1:]:
        if word.startswith("-"):
            if not has_option(rest[i:], word):
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

    A command that never names a gated program is not parsed, and the project is looked up only
    when a project page matches, so most commands cost little.
    """
    pages = stage_pages(brain)
    if not any(gate.split()[0] in command for _, gates, _, _ in pages for gate in gates):
        return []
    runs = simple_commands(command)
    hits = []
    for page, gates, body, folder in pages:
        gate = next((g for g in gates if any(matches(words, g) for words in runs)), None)
        if gate:
            hits.append((page, gate, body, folder))
    if any(folder for *_, folder in hits):
        here = project_folders(brain, cwd)
        hits = [hit for hit in hits if hit[3] is None or hit[3] in here]
    return [hit[:3] for hit in hits]


# Delivery


def user_id():
    return os.getuid() if hasattr(os, "getuid") else os.environ.get("USERNAME", "user")


def state_file(state_dir, payload):
    key = "{}|{}".format(payload.get("session_id") or "no-session", payload.get("agent_id") or "")
    return state_dir / (hashlib.sha256(key.encode()).hexdigest()[:32] + ".json")


def default_state_dir():
    return Path(tempfile.gettempdir()) / "o2b-gate-hook-{}".format(user_id())


def open_state_dir(state_dir):
    """Create the state folder, refusing one that is a link or belongs to someone else."""
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = os.lstat(state_dir)
    if not stat.S_ISDIR(info.st_mode) or (hasattr(os, "getuid") and info.st_uid != os.getuid()):
        raise OSError("{} is not a folder of this user".format(state_dir))
    cutoff = time.time() - STATE_DAYS * 86400
    for path in state_dir.iterdir():
        try:
            if STATE_NAME.fullmatch(path.name) and path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass


def fingerprint(page):
    """The page and its whole text, frontmatter included, so any change to it is delivered again."""
    try:
        text = page.read_bytes()
    except OSError:
        text = b""
    return "{} {}".format(page, hashlib.sha256(text).hexdigest()[:16])


def output_size(text):
    """Characters `text` takes in the hook's JSON output, escapes included."""
    return len(json.dumps(text, ensure_ascii=False))


def first_batch(hits):
    """The pages that fit one message, the rest waiting for the next attempt; a page too long alone is cut."""
    batch, size = [], 600
    for page, gate, body in hits:
        room = REASON_LIMIT - size - output_size(str(page)) - 40
        if output_size(body) > room:
            if batch:
                break
            limit = max(room - 120, 0)
            body = body[:limit]
            while body and output_size(body) > limit:
                body = body[:len(body) - (output_size(body) - limit)]
            body = body.rstrip() + "\n\n[The page continues; read the rest at {}.]".format(page)
        size += output_size(str(page)) + output_size(body) + 40
        batch.append((page, gate, body))
    return batch


def emit(output):
    """Print hook output as UTF-8 JSON, so text outside ASCII keeps its length."""
    print(json.dumps(output, ensure_ascii=False))


def message(hits, held=True, more=False):
    many = len(hits) > 1
    page, it = ("stage pages", "them") if many else ("stage page", "it")
    if held:
        lead = ("O2B held this command once so that the {page} for it reach{s} you before it runs. "
                "Read {it}, apply the rules that match this task, then run the command again unless a rule says not to. "
                "This session is not held again for {these}.").format(
                    page=page, s="" if many else "es", it=it, these="these pages" if many else "this page")
        if more:
            lead += " More pages for this command come on the next attempt."
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
        emit({"systemMessage": "O2B gate hook could not read its input ({}); the command was not checked.".format(error)})
        return 0
    if not isinstance(command, str) or not command.strip():
        return 0
    if not (brain / "BRAIN.md").is_file():
        emit({"systemMessage": "O2B gate hook: {} is not a brain; stage pages were not checked.".format(brain)})
        return 0
    hits = due(brain, command, payload.get("cwd") or os.getcwd())
    if not hits:
        return 0
    path = state_file(state_dir, payload)
    try:
        delivered = set(json.loads(path.read_text(encoding="utf-8"))) if path.is_file() else set()
    except (OSError, ValueError, TypeError):
        delivered = set()
    new = [hit for hit in hits if fingerprint(hit[0]) not in delivered]
    if not new:
        return 0
    batch = first_batch(new)
    try:
        open_state_dir(state_dir)
        temporary = path.with_name(path.name + ".{}.tmp".format(os.getpid()))
        temporary.write_text(json.dumps(sorted(delivered | {fingerprint(p) for p, _, _ in batch})), encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        # Refusing without remembering would refuse every retry, so hand the pages over beside the result instead.
        emit({
            "systemMessage": "O2B gate hook could not record a delivery ({}); the stage pages arrive after the command instead of before it.".format(error),
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": message(batch, held=False)},
        })
        return 0
    emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": message(batch, more=len(batch) < len(new)),
    }})
    return 0


# Setup


def entry_command(script=SCRIPT):
    # A script that is gone must not exit 2: Claude Code reads that as refusing every Bash call.
    quoted = shlex.quote(str(script))
    return "[ -f {0} ] && python3 {0}".format(quoted)


def gate_scripts(command):
    """The gate hook scripts a hook command names, with `~` and `$HOME` expanded."""
    if not isinstance(command, str):
        return []
    try:
        words = shlex.split(command)
    except ValueError:
        words = command.split()
    found = [os.path.expanduser(os.path.expandvars(w)) for w in words if w.endswith("gate-hook/gate_hook.py")]
    return list(dict.fromkeys(found))


def runs_bash(group):
    matcher = group.get("matcher")
    if matcher in (None, "", "*"):
        return True
    if isinstance(matcher, str) and "," in matcher:
        return "Bash" in (part.strip() for part in matcher.split(","))
    try:
        return isinstance(matcher, str) and re.fullmatch(matcher, "Bash") is not None
    except re.error:
        return matcher == "Bash"


def handlers(settings):
    """(group, handler) for each PreToolUse command handler in the settings."""
    for group in settings.get("hooks", {}).get("PreToolUse", []):
        if isinstance(group, dict) and isinstance(group.get("hooks"), list):
            for handler in group["hooks"]:
                if isinstance(handler, dict):
                    yield group, handler


def same_file(a, b):
    return os.path.realpath(a) == os.path.realpath(b)


def read_settings(path):
    settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(settings, dict):
        raise ValueError("it is not a JSON object")
    if not isinstance(settings.get("hooks", {}), dict) or not isinstance(settings.get("hooks", {}).get("PreToolUse", []), list):
        raise ValueError("its `hooks` or `hooks.PreToolUse` is not in the shape Claude Code documents")
    return settings


def write_settings(path, settings):
    """Write through a link to the real file, keeping its permissions, after copying it aside."""
    target = path.resolve()
    mode = 0o600
    if target.exists():
        mode = stat.S_IMODE(target.stat().st_mode)
        today = datetime.date.today().isoformat()
        backup, n = target.with_name("{}.bak-o2b-{}".format(target.name, today)), 2
        while backup.exists():
            backup, n = target.with_name("{}.bak-o2b-{}-{}".format(target.name, today, n)), n + 1
        backup.write_bytes(target.read_bytes())
        os.chmod(backup, mode)
        print("gate-hook: kept the previous settings as {}".format(backup))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".o2b-tmp")
    temporary.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.chmod(temporary, mode)
    os.replace(temporary, target)


def check(path):
    """Problems with this machine's Claude Code settings for this hook; none when it is installed."""
    try:
        settings = read_settings(path)
    except (OSError, ValueError) as error:
        return ["{} cannot be read as settings ({}), so the gate hook was not checked".format(path, error)]
    problems, installed = [], False
    if settings.get("disableAllHooks") is True:
        problems.append("{} sets `disableAllHooks`, so Claude Code runs no hooks, this one included".format(path))
    for group, handler in handlers(settings):
        for script in gate_scripts(handler.get("command")):
            if not os.path.exists(script):
                problems.append("{} runs {}, which does not exist; remove it with `python3 {} --uninstall`".format(path, script, SCRIPT))
            elif same_file(script, SCRIPT) and runs_bash(group):
                installed = True
    if not installed:
        problems.append("{} does not run {} before Bash commands; add it with `python3 {} --install`".format(path, SCRIPT, SCRIPT))
    return problems


def install(path):
    try:
        settings = read_settings(path)
    except (OSError, ValueError) as error:
        print("gate-hook: {} cannot be read as settings ({}); nothing was changed".format(path, error))
        return 1
    if any(runs_bash(g) and any(same_file(s, SCRIPT) for s in gate_scripts(h.get("command"))) for g, h in handlers(settings)):
        print("gate-hook: {} already runs {} before Bash commands".format(path, SCRIPT))
        return 0
    settings.setdefault("hooks", {}).setdefault("PreToolUse", []).append(
        {"matcher": "Bash", "hooks": [{"type": "command", "command": entry_command()}]})
    write_settings(path, settings)
    print("gate-hook: {} now runs {} before Bash commands; start a new session to use it".format(path, SCRIPT))
    return 0


def uninstall(path):
    """Remove this hook, and any gate hook whose script no longer exists."""
    try:
        settings = read_settings(path)
    except (OSError, ValueError) as error:
        print("gate-hook: {} cannot be read as settings ({}); nothing was changed".format(path, error))
        return 1

    def removable(handler):
        return any(same_file(s, SCRIPT) or not os.path.exists(s) for s in gate_scripts(handler.get("command")))

    hooks = settings.get("hooks", {})
    groups = hooks.get("PreToolUse", [])
    kept = []
    for group in groups:
        if not (isinstance(group, dict) and isinstance(group.get("hooks"), list)):
            kept.append(group)
            continue
        rest = [h for h in group["hooks"] if not (isinstance(h, dict) and removable(h))]
        if rest:
            kept.append(dict(group, hooks=rest))
    if kept == groups:
        print("gate-hook: {} runs no gate hook to remove".format(path))
        return 0
    if kept:
        hooks["PreToolUse"] = kept
    else:
        del hooks["PreToolUse"]
        if not hooks:
            del settings["hooks"]
    write_settings(path, settings)
    print("gate-hook: removed the gate hook from {}".format(path))
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
    parser.add_argument("--uninstall", action="store_true", help="remove this hook, and gate hooks whose script is gone, from those settings")
    parser.add_argument("--check", action="store_true", help="report whether those settings run this hook; exit 1 when they do not")
    parser.add_argument("--settings", default=str(Path.home() / ".claude" / "settings.json"), help="settings file for --install, --uninstall and --check")
    args = parser.parse_args(argv)
    brain = Path(args.brain).expanduser().resolve() if args.brain else SCRIPT.parents[3]
    settings = Path(args.settings).expanduser()
    if args.install:
        return install(settings)
    if args.uninstall:
        return uninstall(settings)
    if args.check:
        problems = check(settings)
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    if args.explain is not None:
        return explain(brain, args.explain, args.cwd)
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    return hook(brain, state_dir, sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main())
