#!/usr/bin/env python3
"""Print what the owner typed to their agents in a window of time, for the fit review.

See ../fit-review.md. For one runtime, prints one JSON line per session that has owner turns
in the window, oldest first: each turn's words, with the end of the agent reply it answered,
and the lines of the agent's first reply that name one of the brain's leads. A summary goes to
stderr. The window is `--since` (exclusive) to `--until` (inclusive, by default ten minutes ago),
both in whole seconds:

    python3 read_turns.py claude --since 2026-10-18T11:00:00Z [--root ~/.claude/projects]
    python3 read_turns.py codex  --since 2026-10-18T11:00:00Z [--home ~/.codex]
    python3 read_turns.py hermes --since 2026-10-18T11:00:00Z --user ID [--label NAME] [--db ~/.hermes/state.db]

Exit 0 when the runtime was read, even with no turns; exit 2 when it could not be read. Only
exit 0 lets the caller advance that runtime's last-read time. Python 3.9 standard library only,
so macOS's /usr/bin/python3 can run it.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve()
# Context a runtime or app adds to the owner's message; none of it is their words.
INJECTED = re.compile(
    r"<(system-reminder|in-app-browser-context|artifact-view-context|ide_selection|ide_opened_file)\b[^>]*>.*?</\1>", re.S
)
PASTED = re.compile(r"<pasted_content\b[^>]*>(.*?)</pasted_content>", re.S)
COMMAND_OUTPUT = re.compile(r"<(bash-stdout|bash-stderr)>(.*?)</\1>", re.S)
LEAD_LINK = re.compile(r"\[([^\]]+)\]\((?:\./)?leads/([^)\s/]+)\.md\)")
SETTLE_MINUTES = 10  # a turn still being written is left to the next window
LEAD_LINES = 3
BOX_LIMIT = 400
COPY_ATTEMPTS = 3


class Unreadable(Exception):
    """The runtime's records could not be read; nothing about its turns is known."""


# Time


def parse_time(value):
    """An aware UTC datetime from ISO 8601; a value without an offset is taken as UTC."""
    if not isinstance(value, str):
        raise ValueError("not a time: %r" % (value,))
    moment = datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=datetime.timezone.utc)
    return moment.astimezone(datetime.timezone.utc)


def from_epoch(seconds):
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


# Text


def clean(text):
    """The owner's words without injected context, with pasted text and command output shortened."""
    text = INJECTED.sub("", text or "")
    text = PASTED.sub(lambda match: "[pasted, %d characters: %s]" % (len(match.group(1)), head(match.group(1).strip(), 200)), text)
    text = COMMAND_OUTPUT.sub(lambda match: "[command output, %d characters]" % len(match.group(2)), text)
    return text.strip()


def head(text, limit):
    return text if len(text) <= limit else text[:limit].rstrip() + " …[cut]"


def tail(text, limit):
    return text if len(text) <= limit else "…" + text[-limit:].lstrip()


def lead_names(brain):
    """Names that identify each lead in the brain's index: its link text and its page's name."""
    index = brain / "guidance" / "LEADS.md"
    if not index.is_file():
        return []
    names = set()
    for text, stem in LEAD_LINK.findall(index.read_text(encoding="utf-8")):
        names.update(name for name in (text.strip(), stem) if name)
    return sorted(names, key=str.lower)


def lead_lines(text, names):
    """Lines of an agent's first reply that name a lead, as it says which one it works as."""
    if not names:
        return []
    pattern = re.compile(r"\b(?:%s)\b" % "|".join(map(re.escape, names)), re.I)
    lines = [line.strip() for line in text.splitlines() if pattern.search(line)]
    return [head(line, 200) for line in lines[:LEAD_LINES]]


class Session:
    """One session's owner turns in the window, with what the agent said around them."""

    def __init__(self, runtime, ident, cwd=""):
        self.runtime, self.ident, self.cwd = runtime, ident, cwd or ""
        self.prompts = 0  # messages the agent was given, from anyone
        self.first_reply = []  # agent text before the second prompt
        self.reply_parts = []  # agent text since the latest prompt
        self.box = None  # the next-step box the agent left since then: (question, [(label, message)])
        self.answered = ("", None)  # the reply and box the latest prompt answered
        self.turns = []

    def prompt(self):
        self.answered = ("\n\n".join(self.reply_parts), self.box)
        self.reply_parts, self.box = [], None
        self.prompts += 1

    def reply(self, text):
        if not text:
            return
        if self.prompts <= 1:
            self.first_reply.append(text)
        self.reply_parts.append(text)

    def next_step(self, question, actions):
        if question or actions:
            self.box = (question, actions)

    def turn(self, moment, text, limit, context):
        """Record an owner turn that answered the latest reply; call after prompt()."""
        said, box = self.answered
        turn = {"at": moment, "before": tail(said, context), "text": head(text, limit)}
        if box:
            question, actions = box
            buttons = " / ".join(label if message in ("", label) else "%s (%s)" % (label, message) for label, message in actions)
            shown = "[next-step box] %s%s" % (question, " Buttons: " + buttons if buttons else "")
            turn["before"] = (turn["before"] + "\n" + head(shown, BOX_LIMIT)).strip()
            if text.strip() in {part.strip() for pair in actions for part in pair if part.strip()}:
                turn["button"] = True
        self.turns.append(turn)

    def record(self, names):
        turns = sorted(self.turns, key=lambda turn: turn["at"])
        return {
            "runtime": self.runtime,
            "session": self.ident,
            "cwd": self.cwd,
            "leads": lead_lines("\n".join(self.first_reply), names),
            "turns": [dict(turn, at=iso(turn["at"])) for turn in turns],
        }


# Claude Code


def claude_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def tool_results_only(content):
    return isinstance(content, list) and bool(content) and all(
        isinstance(block, dict) and block.get("type") == "tool_result" for block in content
    )


def next_step_box(content):
    """The desktop app's next-step box in an agent message: its question and buttons, or None."""
    for block in content if isinstance(content, list) else []:
        if not (isinstance(block, dict) and block.get("type") == "tool_use" and str(block.get("name", "")).endswith("wrap_up")):
            continue
        given = block.get("input") if isinstance(block.get("input"), dict) else {}
        actions = given.get("actions") or []
        if isinstance(actions, str):
            try:
                actions = json.loads(actions)
            except ValueError:
                actions = []
        pairs = [
            (str(action.get("label") or "").strip(), str(action.get("message") or "").strip())
            for action in actions if isinstance(action, dict)
        ]
        return str(given.get("ask") or "").strip(), [pair for pair in pairs if any(pair)]
    return None


def read_claude(root, since, until, limit, context):
    """Owner turns from Claude Code transcripts: `origin.kind` "human", deduplicated by `uuid`."""
    if not root.is_dir():
        raise Unreadable("no Claude Code projects folder at %s" % root)
    sessions, seen, paths = {}, set(), []
    # Top-level transcripts only: subagents write theirs below the session's own folder.
    for path in root.glob("*/*.jsonl"):
        try:
            stat = path.stat()
        except OSError as error:
            raise Unreadable("cannot read %s: %s" % (path, error))
        if from_epoch(stat.st_mtime) > since:  # otherwise nothing in it was written after the window opened
            paths.append((getattr(stat, "st_birthtime", 0), str(path), path))
    # A forked or resumed session copies earlier turns under its own id, so read the oldest
    # transcript first and each turn stays with the session it was typed in.
    for _, _, path in sorted(paths):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as error:
            raise Unreadable("cannot read %s: %s" % (path, error))
        local = {}
        for line in lines:
            try:
                record = json.loads(line)
            except ValueError:
                continue  # a line still being written
            if not isinstance(record, dict) or record.get("isSidechain"):
                continue
            kind, ident = record.get("type"), record.get("sessionId") or path.stem
            if kind not in ("user", "assistant"):
                continue
            session = local.get(ident)
            if session is None:
                session = local[ident] = Session("claude", ident, record.get("cwd"))
            message = record.get("message") or {}
            content = message.get("content") if isinstance(message, dict) else None
            if kind == "assistant":
                session.reply(claude_text(content).strip())
                box = next_step_box(content)
                if box:
                    session.next_step(*box)
                continue
            if tool_results_only(content):
                continue
            session.prompt()
            origin = record.get("origin")
            if not (isinstance(origin, dict) and origin.get("kind") == "human"):
                continue
            uuid = record.get("uuid")
            if uuid is not None and uuid in seen:
                continue  # a resumed or forked session copies earlier records
            try:
                moment = parse_time(record.get("timestamp"))
            except ValueError:
                continue
            if not since < moment <= until:
                continue
            text = clean(claude_text(content))
            if text:
                if uuid is not None:
                    seen.add(uuid)
                session.turn(moment, text, limit, context)
        for ident, session in local.items():
            if session.turns:
                if ident in sessions:
                    sessions[ident].turns.extend(session.turns)
                else:
                    sessions[ident] = session
    return list(sessions.values())


# SQLite stores


def marks(path):
    """Size and modification time of a store and its journal, to tell whether a copy is consistent."""
    found = []
    for suffix in ("", "-wal"):
        try:
            stat = os.stat(str(path) + suffix)
            found.append((stat.st_size, stat.st_mtime_ns))
        except FileNotFoundError:
            found.append(None)
    return found


def connect(path, scratch):
    """A read-only connection; a store whose journal cannot be opened in place is read from a copy."""
    if not path.is_file():
        raise Unreadable("no database at %s" % path)
    try:
        connection = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
        connection.execute("select count(*) from sqlite_master").fetchone()
        return connection
    except sqlite3.Error:
        pass
    copy = Path(scratch) / path.name
    try:
        # The store and its journal are copied one after the other; a write or checkpoint between
        # them leaves a pair that silently lacks rows, so keep a copy only if neither changed.
        for _ in range(COPY_ATTEMPTS):
            before = marks(path)
            for suffix in ("", "-wal"):
                target = Path(str(copy) + suffix)
                if target.exists():
                    target.unlink()
                source = Path(str(path) + suffix)
                if source.is_file():
                    shutil.copyfile(str(source), str(target))
            if marks(path) == before:
                connection = sqlite3.connect(str(copy))
                connection.execute("select count(*) from sqlite_master").fetchone()
                return connection
    except (OSError, sqlite3.Error) as error:
        raise Unreadable("cannot read %s: %s" % (path, error))
    raise Unreadable("%s kept changing while it was copied" % path)


def columns(connection, table):
    return {row[1] for row in connection.execute("pragma table_info(%s)" % table)}


# Codex


def codex_text(item, key):
    if key == "text":
        return item.get("text") or ""
    return "\n".join(
        part.get("text", "") for part in item.get("content") or [] if isinstance(part, dict) and part.get("type") == "text"
    )


def owner_thread(source):
    """Threads the owner typed in: not a subagent or reviewer (a JSON source) and not `codex exec`."""
    source = (source or "").strip()
    return bool(source) and not source.startswith("{") and source != "exec"


def read_codex(home, since, until, limit, context):
    """Owner turns from Codex's thread store (`state_5.sqlite` and `thread_history_1.sqlite`)."""
    with tempfile.TemporaryDirectory(prefix="fit-review-") as scratch:
        try:
            state = connect(home / "state_5.sqlite", scratch)
            history = connect(home / "thread_history_1.sqlite", scratch)
            threads = {ident: (source, cwd) for ident, source, cwd in state.execute("select id, source, cwd from threads")}
            low, high = since.timestamp() * 1000, until.timestamp() * 1000
            active = [
                ident
                for (ident,) in history.execute(
                    "select distinct thread_id from thread_items where item_type = 'userMessage'"
                    " and created_at_ms > ? and created_at_ms <= ?",
                    (low, high),
                )
                if owner_thread(threads.get(ident, ("", ""))[0])
            ]
            sessions = []
            for ident in active:
                session = Session("codex", ident, threads[ident][1])
                rows = history.execute(
                    "select item_type, item_json, created_at_ms from thread_items where thread_id = ?"
                    " and item_type in ('userMessage', 'agentMessage') order by rollout_ordinal",
                    (ident,),
                )
                for kind, raw, created in rows:
                    try:
                        item = json.loads(raw)
                    except (TypeError, ValueError):
                        continue
                    if kind == "agentMessage":
                        session.reply(codex_text(item, "text").strip())
                        continue
                    session.prompt()
                    if isinstance(created, (int, float)) and low < created <= high:
                        text = clean(codex_text(item, "content"))
                        if text:
                            session.turn(from_epoch(created / 1000), text, limit, context)
                if session.turns:
                    sessions.append(session)
            return sessions
        except sqlite3.Error as error:
            raise Unreadable("cannot read Codex threads in %s: %s" % (home, error))


# Hermes

# Hermes stores its own notes as user messages. These openers are its scaffolding rows, from its
# context compressor, title generator and control frames (Hermes 0.21.5), plus a restated request.
HERMES_SCAFFOLDING = (
    "[System:", "[SYSTEM]", "[CONTEXT", "[PRIOR CONTEXT", "[IMPORTANT:", "[Your active task list",
    "[Planning state preserved", "[ASYNC DELEGATION", "[Runtime note:", "[STILL IN PROGRESS", "Cronjob Response:",
)
HERMES_RUNS = {"cron", "subagent"}  # sessions Hermes starts itself, whoever they belong to
HERMES_ROUTING = re.compile(r"(?:^|\n)\[Triggering message id:[^\n]*\]\n*")  # older rows carry the Discord routing note
HERMES_ORIGIN = re.compile(r"\AGateway message origin \(JSON data[^\n]*\n[^\n]*\n[^\n]*\n\n")
HERMES_SPEAKER = re.compile(r"\A\[([^\]\n:—]{1,40})\]\s+")  # "[Name] " before a message in a shared channel
HERMES_NOTE = re.compile(r"\A\[System note:[^\]]*\]\s*")  # prepended to the owner's next message
HERMES_STEER = re.compile(r"\A\[OUT-OF-BAND USER MESSAGE[^\]]*\]\s*(.*?)\s*(?:\[/OUT-OF-BAND USER MESSAGE\])?\s*\Z", re.S)


def hermes_text(content, labels):
    """The owner's words in a Hermes user row, or "" when the row is Hermes' own or someone else's.

    `labels` are the owner's speaker labels: a row labelled with one loses the label, and with
    labels given, a row labelled with another name is dropped. Without labels, labels stay.
    """
    text = HERMES_ROUTING.sub("\n", clean(content)).strip()
    text = HERMES_ORIGIN.sub("", text).strip()
    for _ in range(2):  # a speaker label can stand before a note
        speaker = HERMES_SPEAKER.match(text)
        if speaker:
            rest = text[speaker.end():]
            if rest.startswith(HERMES_SCAFFOLDING):
                return ""
            if speaker.group(1).strip() in labels:
                text = rest
            elif labels:
                return ""
        text = HERMES_NOTE.sub("", text, count=1).strip()
    steer = HERMES_STEER.match(text)
    if steer:
        text = steer.group(1).strip()
    return "" if text.startswith(HERMES_SCAFFOLDING) else text


def read_hermes(db, users, local, labels, since, until, limit, context):
    """Owner turns from a Hermes state database: the owner's own chat sessions and local terminals."""
    with tempfile.TemporaryDirectory(prefix="fit-review-") as scratch:
        try:
            connection = connect(db, scratch)
            session_fields, message_fields = columns(connection, "sessions"), columns(connection, "messages")
            cwd_column = "cwd" if "cwd" in session_fields else "''"
            chat_column = "chat_type" if "chat_type" in session_fields else "null"
            kind_column = "display_kind" if "display_kind" in message_fields else "''"
            platform_column = "platform_message_id" if "platform_message_id" in message_fields else "null"
            owned = {}
            query = "select id, source, user_id, %s, %s from sessions" % (cwd_column, chat_column)
            for ident, source, user, cwd, chat in connection.execute(query):
                if source in HERMES_RUNS:
                    continue
                if (user is not None and str(user) in users) or (user is None and source in local):
                    owned[ident] = (cwd, chat)
            active = [
                ident
                for (ident,) in connection.execute(
                    "select distinct session_id from messages where role = 'user' and timestamp > ? and timestamp <= ?",
                    (since.timestamp(), until.timestamp()),
                )
                if ident in owned
            ]
            sessions, seen = [], set()
            for ident in active:
                cwd, chat = owned[ident]
                session = Session("hermes", ident, cwd)
                speakers = labels if chat != "dm" else set()  # a direct message has no one else to label
                rows = connection.execute(
                    "select role, content, timestamp, %s, %s from messages where session_id = ?"
                    " and role in ('user', 'assistant') order by id" % (kind_column, platform_column),
                    (ident,),
                )
                for role, content, moment, kind, platform_id in rows:
                    if role == "assistant":
                        session.reply((content or "").strip())
                        continue
                    session.prompt()
                    if not isinstance(moment, (int, float)) or not since.timestamp() < moment <= until.timestamp():
                        continue
                    if kind == "internal_notification":
                        continue
                    text = hermes_text(content, speakers)
                    # A compressed session's continuation copies earlier rows, keeping their time.
                    keys = {("text", text, int(moment))} | ({("platform", platform_id)} if platform_id else set())
                    if text and not keys & seen:
                        seen |= keys
                        session.turn(from_epoch(moment), text, limit, context)
                if session.turns:
                    sessions.append(session)
            return sessions
        except sqlite3.Error as error:
            raise Unreadable("cannot read Hermes sessions in %s: %s" % (db, error))


# Command line


def arguments(argv):
    parser = argparse.ArgumentParser(description="Print the owner's turns in a window, one JSON line per session.")
    parser.add_argument("runtime", choices=["claude", "codex", "hermes"])
    parser.add_argument("--since", required=True, help="last-read time, ISO 8601; turns after it are read")
    parser.add_argument("--until", help="read through this time; default %d minutes ago" % SETTLE_MINUTES)
    parser.add_argument("--brain", default=str(SCRIPT.parents[3]), help="brain whose leads index names the leads")
    parser.add_argument("--root", default="~/.claude/projects", help="Claude Code projects folder")
    parser.add_argument("--home", default="~/.codex", help="Codex home")
    parser.add_argument("--db", default="~/.hermes/state.db", help="Hermes state database")
    parser.add_argument("--user", action="append", default=[], help="the owner's chat user id in Hermes; repeatable")
    parser.add_argument("--local", help="Hermes sources without a user that are the owner's; default cli,tui with --user")
    parser.add_argument("--label", action="append", default=[], help="the owner's speaker label in Hermes; repeatable")
    parser.add_argument("--limit", type=int, default=4000, help="characters kept of each owner turn")
    parser.add_argument("--context", type=int, default=600, help="characters kept of the agent reply before it")
    return parser.parse_args(argv)


def main(argv=None, out=sys.stdout, err=sys.stderr):
    args = arguments(argv)
    try:
        since = parse_time(args.since)
        until = parse_time(args.until) if args.until else (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=SETTLE_MINUTES)
        )
    except ValueError as error:
        print("read_turns: bad time: %s" % error, file=err)
        return 2
    until = until.replace(microsecond=0)  # the summary prints whole seconds, and the next run starts there
    if until <= since:
        print("read_turns: --until %s is not after --since %s" % (iso(until), iso(since)), file=err)
        return 2
    if args.runtime == "hermes" and not args.user and args.local is None:
        print("read_turns: name the owner's chat user with --user, or only local sources with --local", file=err)
        return 2
    if hasattr(out, "reconfigure"):
        out.reconfigure(encoding="utf-8")

    def expand(value):
        return Path(os.path.expanduser(value))

    try:
        if args.runtime == "claude":
            sessions = read_claude(expand(args.root), since, until, args.limit, args.context)
        elif args.runtime == "codex":
            sessions = read_codex(expand(args.home), since, until, args.limit, args.context)
        else:
            local = args.local if args.local is not None else "cli,tui"
            sources = {source.strip() for source in local.split(",") if source.strip()}
            labels = {label.strip() for label in args.label if label.strip()}
            sessions = read_hermes(expand(args.db), set(args.user), sources, labels, since, until, args.limit, args.context)
    except Unreadable as error:
        print("read_turns: %s: %s; its last-read time stays where it was" % (args.runtime, error), file=err)
        return 2
    names = lead_names(expand(args.brain))
    records = sorted((session.record(names) for session in sessions), key=lambda record: record["turns"][0]["at"])
    for record in records:
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
    turns = sum(len(record["turns"]) for record in records)
    print(
        "read_turns: %s: %d turns in %d sessions after %s through %s"
        % (args.runtime, turns, len(records), iso(since), iso(until)),
        file=err,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
