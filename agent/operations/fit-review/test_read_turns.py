"""Tests for read_turns.py against throwaway transcripts, thread stores and brains.

Usage: python3 test_read_turns.py   (touches nothing outside a temporary directory)
"""

import io
import json
import os
import sqlite3
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

import read_turns

SINCE = "2026-10-18T00:00:00Z"
UNTIL = "2026-10-20T00:00:00Z"
LEADS = """# Leads

| Lead | For |
|---|---|
| [Ada](leads/ada.md) | improving products in use |
| [Remy](leads/remy.md) | shaping new products |
"""


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = read_turns.main(list(argv), out=out, err=err)
    records = [json.loads(line) for line in out.getvalue().splitlines()]
    return code, records, err.getvalue()


def texts(records):
    return [turn["text"] for record in records for turn in record["turns"]]


def human(uuid, at, text, session="s1", cwd="/work", **extra):
    record = {
        "type": "user",
        "uuid": uuid,
        "sessionId": session,
        "cwd": cwd,
        "timestamp": at,
        "origin": {"kind": "human"},
        "message": {"role": "user", "content": [{"type": "text", "text": text}]},
    }
    record.update(extra)
    return record


def prompt(uuid, at, text, session="s1", kind=None):
    record = {"type": "user", "uuid": uuid, "sessionId": session, "timestamp": at,
              "message": {"role": "user", "content": text}}
    if kind:
        record["origin"] = {"kind": kind}
    return record


def agent(uuid, at, text, session="s1", box=None):
    content = [{"type": "thinking", "thinking": "hidden"}, {"type": "text", "text": text}] if text else []
    if box is not None:
        content.append({"type": "tool_use", "name": "mcp__app__wrap_up", "input": box})
    return {"type": "assistant", "uuid": uuid, "sessionId": session, "timestamp": at,
            "message": {"role": "assistant", "content": content}}


def tool_result(uuid, at, session="s1"):
    return {"type": "user", "uuid": uuid, "sessionId": session, "timestamp": at,
            "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.brain = self.dir / "brain"
        (self.brain / "guidance").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def with_leads(self):
        (self.brain / "guidance" / "LEADS.md").write_text(LEADS, encoding="utf-8")


class ClaudeCode(Base):
    def setUp(self):
        super().setUp()
        self.root = self.dir / "projects"

    def transcript(self, folder, name, records, raw_tail=""):
        path = self.root / folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
        path.write_text(body + raw_tail, encoding="utf-8")
        return path

    def read(self, *extra, since=SINCE, until=UNTIL):
        return run("claude", "--since", since, "--until", until, "--root", str(self.root),
                   "--brain", str(self.brain), *extra)

    def test_reads_only_the_owners_typed_turns(self):
        self.transcript("-work", "s1.jsonl", [
            prompt("p1", "2026-10-18T01:00:00Z", "Started by another session", kind=None),
            agent("a1", "2026-10-18T01:01:00Z", "First reply."),
            tool_result("t1", "2026-10-18T01:02:00Z"),
            prompt("p2", "2026-10-18T01:03:00Z", "A background task finished", kind="task-notification"),
            human("h1", "2026-10-18T01:04:00Z", "No, check the café page as a visitor sees it"),
        ])
        code, records, err = self.read()
        self.assertEqual(code, 0)
        self.assertEqual(texts(records), ["No, check the café page as a visitor sees it"])
        self.assertIn("1 turns in 1 sessions", err)

    def test_window_excludes_since_and_includes_until(self):
        self.transcript("-work", "s1.jsonl", [
            human("h0", "2026-10-17T23:59:59Z", "before the window"),
            human("h1", "2026-10-18T00:00:00Z", "exactly at since"),
            human("h2", "2026-10-18T00:00:01Z", "just after since"),
            human("h3", "2026-10-20T00:00:00Z", "exactly at until"),
            human("h4", "2026-10-20T00:00:01Z", "after until"),
        ])
        _, records, _ = self.read()
        self.assertEqual(texts(records), ["just after since", "exactly at until"])

    def test_until_is_whole_seconds_so_the_next_window_does_not_read_a_turn_again(self):
        self.transcript("-work", "s1.jsonl", [human("h1", "2026-10-19T12:00:00.500Z", "half a second in")])
        _, first, err = self.read(until="2026-10-19T12:00:00.750Z")
        self.assertIn("through 2026-10-19T12:00:00Z", err)
        _, second, _ = self.read(since="2026-10-19T12:00:00Z")
        self.assertEqual(texts(first) + texts(second), ["half a second in"])

    def test_a_resumed_session_copying_history_counts_each_turn_once(self):
        original = [human("h1", "2026-10-18T02:00:00Z", "first ask"),
                    agent("a1", "2026-10-18T02:01:00Z", "Done.")]
        self.transcript("-work", "s1.jsonl", original)
        copied = [dict(record, sessionId="s2") for record in original]
        self.transcript("-work", "s2.jsonl", copied + [
            human("h2", "2026-10-18T03:00:00Z", "second ask", session="s2")])
        _, records, err = self.read()
        self.assertEqual(sorted(texts(records)), ["first ask", "second ask"])
        self.assertIn("2 turns", err)

    def test_strips_injected_context_and_skips_turns_left_empty(self):
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "<system-reminder>\nLinked sessions now\n</system-reminder>"),
            {**human("h2", "2026-10-18T01:01:00Z", ""), "message": {"role": "user", "content": [
                {"type": "text", "text": "<system-reminder> status </system-reminder>"},
                {"type": "text", "text": "<ide_selection path='a.py'>line 3</ide_selection>Let us take them one by one"}]}},
        ])
        _, records, _ = self.read()
        self.assertEqual(texts(records), ["Let us take them one by one"])

    def test_pasted_text_and_command_output_are_shortened(self):
        pasted = "<pasted_content id='p1'>" + "agent output " * 40 + "</pasted_content>"
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "Look at this: " + pasted + " Why?"),
            human("h2", "2026-10-18T01:01:00Z", "<bash-input>ls</bash-input><bash-stdout>a\nb\n</bash-stdout><bash-stderr></bash-stderr>"),
        ])
        _, records, _ = self.read()
        first, second = texts(records)
        self.assertTrue(first.startswith("Look at this: [pasted, 520 characters: agent output"))
        self.assertTrue(first.endswith(" Why?"))
        self.assertLess(len(first), 260)
        self.assertEqual(second, "<bash-input>ls</bash-input>[command output, 4 characters][command output, 0 characters]")

    def test_before_is_the_end_of_the_agent_reply_answered(self):
        long_reply = "x" * 900 + " Which option should we take?"
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "start"),
            agent("a1", "2026-10-18T01:01:00Z", "An earlier part of the reply."),
            tool_result("t1", "2026-10-18T01:01:30Z"),
            agent("a2", "2026-10-18T01:02:00Z", long_reply),
            human("h2", "2026-10-18T01:04:00Z", "the second"),
        ])
        _, records, _ = self.read("--context", "100")
        first, second = records[0]["turns"]
        self.assertEqual(first["before"], "")
        self.assertTrue(second["before"].startswith("…"))
        self.assertTrue(second["before"].endswith("Which option should we take?"))
        self.assertLessEqual(len(second["before"]), 101)
        _, records, _ = self.read("--context", "2000")
        self.assertTrue(records[0]["turns"][1]["before"].startswith("An earlier part of the reply.\n\nxxx"))

    def test_a_next_step_box_is_part_of_before_and_its_buttons_are_marked(self):
        box = {"recap": "Two fixes are in.", "ask": "Merge it now?",
               "actions": [{"label": "Merge", "message": "Yes, merge it"}, {"label": "Not yet"}]}
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "fix it"),
            agent("a1", "2026-10-18T01:01:00Z", "", box=box),
            tool_result("t1", "2026-10-18T01:01:01Z"),
            agent("a2", "2026-10-18T01:01:02Z", "Both fixes pass."),
            human("h2", "2026-10-18T01:02:00Z", "Yes, merge it"),
            agent("a3", "2026-10-18T01:03:00Z", "", box=dict(box, actions=json.dumps(box["actions"]))),
            human("h3", "2026-10-18T01:04:00Z", "Wait, the live page is still wrong"),
            agent("a4", "2026-10-18T01:05:00Z", "Looking."),
            human("h4", "2026-10-18T01:06:00Z", "Not yet"),
        ])
        _, records, _ = self.read()
        _, clicked, typed, later = records[0]["turns"]
        self.assertEqual(clicked["before"],
                         "Both fixes pass.\n[next-step box] Merge it now? Buttons: Merge (Yes, merge it) / Not yet")
        self.assertTrue(clicked.get("button"))
        self.assertEqual(typed["before"], "[next-step box] Merge it now? Buttons: Merge (Yes, merge it) / Not yet")
        self.assertNotIn("button", typed)
        self.assertEqual(later["before"], "Looking.")
        self.assertNotIn("button", later)  # a box answered earlier no longer applies

    def test_long_turns_are_cut_and_marked(self):
        self.transcript("-work", "s1.jsonl", [human("h1", "2026-10-18T01:00:00Z", "y" * 50)])
        _, records, _ = self.read("--limit", "10")
        self.assertEqual(texts(records), ["y" * 10 + " …[cut]"])

    def test_lead_lines_come_from_the_first_reply_only(self):
        self.with_leads()
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "plan the release"),
            agent("a1", "2026-10-18T01:01:00Z", "Reading the brain first."),
            agent("a2", "2026-10-18T01:02:00Z", "Working as Ada.\nThe release needs two fixes."),
            human("h2", "2026-10-18T01:03:00Z", "go"),
            agent("a3", "2026-10-18T01:04:00Z", "This is Remy's question now."),
            human("h3", "2026-10-18T01:05:00Z", "ok"),
        ])
        _, records, _ = self.read()
        self.assertEqual(records[0]["leads"], ["Working as Ada."])

    def test_no_leads_index_gives_no_lead_lines(self):
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "hi"),
            agent("a1", "2026-10-18T01:01:00Z", "Working as Ada."),
            human("h2", "2026-10-18T01:02:00Z", "go")])
        _, records, _ = self.read()
        self.assertEqual(records[0]["leads"], [])

    def test_skips_sidechains_subagent_files_bad_stamps_and_a_line_being_written(self):
        self.transcript("-work", "s1.jsonl", [
            human("h1", "2026-10-18T01:00:00Z", "kept"),
            human("h2", "2026-10-18T01:01:00Z", "sidechain", isSidechain=True),
            human("h5", None, "no stamp"),
            human("h6", "yesterday", "bad stamp"),
        ], raw_tail='{"type": "user", "uuid": "h3", "orig')
        self.transcript("-work", "s1/subagents/agent-1.jsonl", [human("h4", "2026-10-18T01:02:00Z", "subagent")])
        code, records, _ = self.read()
        self.assertEqual(code, 0)
        self.assertEqual(texts(records), ["kept"])

    def test_a_file_untouched_since_the_window_opened_is_not_read(self):
        path = self.transcript("-work", "s1.jsonl", [human("h1", "2026-10-18T01:00:00Z", "old file, odd stamp")])
        stamp = time.mktime(time.strptime("2026-10-17", "%Y-%m-%d"))
        os.utime(path, (stamp, stamp))
        _, records, _ = self.read()
        self.assertEqual(records, [])

    def test_sessions_are_ordered_by_their_first_turn(self):
        self.transcript("-a", "late.jsonl", [human("h1", "2026-10-19T05:00:00Z", "later", session="late")])
        self.transcript("-b", "early.jsonl", [human("h2", "2026-10-18T05:00:00Z", "earlier", session="early")])
        _, records, _ = self.read()
        self.assertEqual([record["session"] for record in records], ["early", "late"])
        self.assertEqual(records[0]["cwd"], "/work")

    @unittest.skipUnless(hasattr(os.stat_result, "st_birthtime"), "needs file creation times")
    def test_a_copied_turn_stays_with_the_session_it_was_typed_in(self):
        original = [human("h1", "2026-10-18T02:00:00Z", "No, the other file", session="orig"),
                    agent("a1", "2026-10-18T02:01:00Z", "Fixed.", session="orig")]
        self.transcript("-work", "z-orig.jsonl", original)
        time.sleep(0.05)
        copied = [dict(record, sessionId="fork") for record in original]
        self.transcript("-work", "a-fork.jsonl", copied + [
            human("h2", "2026-10-18T03:00:00Z", "No, the other file", session="fork")])
        _, records, _ = self.read()
        self.assertEqual([(record["session"], texts([record])) for record in records],
                         [("orig", ["No, the other file"]), ("fork", ["No, the other file"])])

    def test_a_missing_projects_folder_is_unreadable_not_empty(self):
        code, records, err = run("claude", "--since", SINCE, "--until", UNTIL, "--root", str(self.dir / "none"))
        self.assertEqual(code, 2)
        self.assertEqual(records, [])
        self.assertIn("last-read time stays", err)


class Codex(Base):
    def setUp(self):
        super().setUp()
        self.home = self.dir / "codex"
        self.home.mkdir()
        state = sqlite3.connect(str(self.home / "state_5.sqlite"))
        state.execute("create table threads (id text primary key, source text, cwd text, thread_source text)")
        state.executemany("insert into threads values (?, ?, ?, ?)", [
            ("t-user", "vscode", "/repo", "user"),
            ("t-cli", "cli", "/cli", "user"),
            ("t-exec", "exec", "/tmp", "user"),
            ("t-sub", '{"subagent":{"thread_spawn":{"parent_thread_id":"t-user"}}}', "/repo", "subagent"),
            ("t-guard", '{"subagent":{"other":"guardian"}}', "/repo", "guardian_review"),
        ])
        state.commit()
        state.close()
        self.history = sqlite3.connect(str(self.home / "thread_history_1.sqlite"))
        self.history.execute("create table thread_items (thread_id text, turn_id text, item_id text,"
                             " rollout_ordinal integer, created_at_ms integer, item_json text, item_type text)")
        self.ordinal = 0

    def tearDown(self):
        self.history.close()
        super().tearDown()

    def item(self, thread, kind, at, text):
        self.ordinal += 1
        body = ({"type": "agentMessage", "text": text} if kind == "agentMessage" else
                {"type": "userMessage", "content": [{"type": "text", "text": text}]})
        millis = int(read_turns.parse_time(at).timestamp() * 1000)
        self.history.execute("insert into thread_items values (?, ?, ?, ?, ?, ?, ?)",
                             (thread, "turn", "i%d" % self.ordinal, self.ordinal, millis, json.dumps(body), kind))
        self.history.commit()

    def read(self):
        return run("codex", "--since", SINCE, "--until", UNTIL, "--home", str(self.home), "--brain", str(self.brain))

    def test_reads_owner_threads_only(self):
        for thread in ("t-user", "t-cli", "t-exec", "t-sub", "t-guard"):
            self.item(thread, "userMessage", "2026-10-18T01:00:00Z", "from " + thread)
        code, records, _ = self.read()
        self.assertEqual(code, 0)
        self.assertEqual(sorted(texts(records)), ["from t-cli", "from t-user"])

    def test_turns_carry_the_agent_reply_before_and_the_first_reply_names_the_lead(self):
        self.with_leads()
        self.item("t-user", "userMessage", "2026-10-17T10:00:00Z", "older ask")
        self.item("t-user", "agentMessage", "2026-10-17T10:01:00Z", "Remy here. Let us shape it.")
        self.item("t-user", "userMessage", "2026-10-18T10:00:00Z",
                  "<in-app-browser-context>tab: docs</in-app-browser-context>That is not what I meant")
        _, records, _ = self.read()
        self.assertEqual(texts(records), ["That is not what I meant"])
        self.assertEqual(records[0]["turns"][0]["before"], "Remy here. Let us shape it.")
        self.assertEqual(records[0]["leads"], ["Remy here. Let us shape it."])
        self.assertEqual(records[0]["cwd"], "/repo")

    def test_window_excludes_since_and_includes_until(self):
        self.item("t-user", "userMessage", SINCE, "exactly at since")
        self.item("t-user", "userMessage", "2026-10-19T00:00:00Z", "inside")
        self.item("t-user", "userMessage", UNTIL, "exactly at until")
        self.item("t-user", "userMessage", "2026-10-20T00:00:01Z", "after until")
        _, records, _ = self.read()
        self.assertEqual(texts(records), ["inside", "exactly at until"])

    def test_a_store_that_cannot_be_opened_in_place_is_read_from_a_copy_with_its_journal(self):
        self.history.execute("pragma journal_mode=wal")
        self.item("t-user", "userMessage", "2026-10-18T01:00:00Z", "still in the journal")
        self.assertTrue((self.home / "thread_history_1.sqlite-wal").stat().st_size > 0)
        connect = sqlite3.connect

        def refuse_in_place(target, *args, **kwargs):
            if kwargs.get("uri"):
                raise sqlite3.OperationalError("unable to open database file")
            return connect(target, *args, **kwargs)

        with unittest.mock.patch.object(read_turns.sqlite3, "connect", refuse_in_place):
            code, records, _ = self.read()
        self.assertEqual(code, 0)
        self.assertEqual(texts(records), ["still in the journal"])

    def refuse_in_place(self):
        connect = sqlite3.connect

        def refuse(target, *args, **kwargs):
            if kwargs.get("uri"):
                raise sqlite3.OperationalError("unable to open database file")
            return connect(target, *args, **kwargs)

        return unittest.mock.patch.object(read_turns.sqlite3, "connect", refuse)

    def test_a_store_written_while_it_is_copied_is_copied_again(self):
        self.item("t-user", "userMessage", "2026-10-18T01:00:00Z", "copied whole")
        copyfile, writes = read_turns.shutil.copyfile, []

        def copy_while_written(source, target):
            copyfile(source, target)
            if source.endswith("thread_history_1.sqlite") and not writes:
                writes.append(source)
                stamp = os.stat(source).st_mtime_ns + 10 ** 9
                os.utime(source, ns=(stamp, stamp))  # a checkpoint lands mid-copy

        with self.refuse_in_place(), unittest.mock.patch.object(read_turns.shutil, "copyfile", copy_while_written):
            code, records, _ = self.read()
        self.assertEqual(code, 0)
        self.assertEqual(writes, [str(self.home / "thread_history_1.sqlite")])
        self.assertEqual(texts(records), ["copied whole"])

    def test_a_store_that_keeps_changing_while_copied_is_unreadable(self):
        self.item("t-user", "userMessage", "2026-10-18T01:00:00Z", "never settles")
        copyfile = read_turns.shutil.copyfile

        def copy_while_written(source, target):
            copyfile(source, target)
            stamp = os.stat(source).st_mtime_ns + 10 ** 9
            os.utime(source, ns=(stamp, stamp))

        with self.refuse_in_place(), unittest.mock.patch.object(read_turns.shutil, "copyfile", copy_while_written):
            code, records, err = self.read()
        self.assertEqual((code, records), (2, []))
        self.assertIn("kept changing", err)

    def test_a_missing_store_is_unreadable(self):
        os.remove(str(self.home / "state_5.sqlite"))
        code, _, err = self.read()
        self.assertEqual(code, 2)
        self.assertIn("no database", err)


class Hermes(Base):
    def setUp(self):
        super().setUp()
        self.db = self.dir / "state.db"
        self.connection = sqlite3.connect(str(self.db))
        self.connection.execute("create table sessions (id text primary key, source text, user_id text,"
                                " started_at real, cwd text)")
        self.connection.execute("create table messages (id integer primary key autoincrement, session_id text,"
                                " role text, content text, timestamp real)")
        self.connection.executemany("insert into sessions values (?, ?, ?, 0, ?)", [
            ("owner-chat", "discord", "111", "/home"),
            ("other-chat", "discord", "222", "/home"),
            ("terminal", "cli", None, "/home"),
            ("cron-run", "cron", None, "/home"),
            ("owner-cron", "cron", "111", "/home"),
            ("delegated", "subagent", "111", "/home"),
        ])
        self.connection.commit()

    def tearDown(self):
        self.connection.close()
        super().tearDown()

    def message(self, session, role, at, content):
        moment = read_turns.parse_time(at).timestamp() if at else None
        self.connection.execute("insert into messages (session_id, role, content, timestamp) values (?, ?, ?, ?)",
                                (session, role, content, moment))
        self.connection.commit()

    def read(self, *owner):
        return run("hermes", "--since", SINCE, "--until", UNTIL, "--db", str(self.db), "--brain", str(self.brain), *owner)

    def test_reads_the_owners_chats_and_local_terminals_only(self):
        for session in ("owner-chat", "other-chat", "terminal", "cron-run", "owner-cron", "delegated"):
            self.message(session, "user", "2026-10-18T01:00:00Z", "from " + session)
        code, records, _ = self.read("--user", "111")
        self.assertEqual(code, 0)
        self.assertEqual(sorted(texts(records)), ["from owner-chat", "from terminal"])

    def test_the_agent_reply_before_skips_tool_rows_and_empty_rows(self):
        self.message("owner-chat", "user", "2026-10-18T01:00:00Z", "Sort my to-dos")
        self.message("owner-chat", "assistant", "2026-10-18T01:00:10Z", "Three items are open.")
        self.message("owner-chat", "assistant", "2026-10-18T01:00:20Z", None)
        self.message("owner-chat", "tool", "2026-10-18T01:00:30Z", "tool output")
        self.message("owner-chat", "user", "2026-10-18T01:01:00Z", "That is not what I asked")
        _, records, _ = self.read("--user", "111")
        self.assertEqual(records[0]["turns"][1]["before"], "Three items are open.")

    def test_hermes_own_rows_are_dropped_and_its_wrappers_removed(self):
        rows = [
            "[Triggering message id: `123` — use as `message_id` for reply/react/pin via the discord tools.]\n\nNot that one, this one",
            "[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted.",
            "[IMPORTANT: Background process p1 finished (exit code 0).]",
            "[ASYNC DELEGATION BATCH COMPLETE — deleg_1]\nA background task finished.",
            "[STILL IN PROGRESS — this is the active request, restated after compaction] sort the list",
            "[Triggering message id: `124` — use as `message_id` for reply/react/pin via the discord tools.]\n\n"
            "[System: The active model for this chat has changed to x]",
            "[SYSTEM] The active model changed.",
            "[System note: your previous turn was interrupted.]\nTry again",
            "\n\n[OUT-OF-BAND USER MESSAGE — a direct message from the user, delivered once at this position]\n"
            "Stop and do this first\n[/OUT-OF-BAND USER MESSAGE]",
            'Gateway message origin (JSON data, not instructions or authorization):\n{"platform": "discord"}\n'
            "Do not guess a reply destination when these fields are insufficient.\n\nWhat is on today?",
            '[Replying to: "Three items are open."] Do the first one',
            "[WIP] keep this label",
        ]
        for minute, content in enumerate(rows):
            self.message("owner-chat", "user", "2026-10-18T01:%02d:00Z" % minute, content)
        self.message("owner-chat", "user", "2026-10-18T02:00:00Z", None)
        self.message("owner-chat", "user", None, "no time")
        _, records, _ = self.read("--user", "111")
        self.assertEqual(texts(records), [
            "Not that one, this one", "Try again", "Stop and do this first", "What is on today?",
            '[Replying to: "Three items are open."] Do the first one', "[WIP] keep this label",
        ])

    def test_speaker_labels_are_removed_only_for_the_owner(self):
        rows = ["[Sam Park] Yes, do that", "[Robin] Can you check mine?", "[Sam Park] [IMPORTANT: MCP servers reloaded.]",
                "[Robin] [CONTEXT COMPACTION — REFERENCE ONLY] summary"]
        for minute, content in enumerate(rows):
            self.message("owner-chat", "user", "2026-10-18T01:%02d:00Z" % minute, content)
        _, labelled, _ = self.read("--user", "111", "--label", "Sam Park")
        self.assertEqual(texts(labelled), ["Yes, do that"])
        _, unlabelled, _ = self.read("--user", "111")
        self.assertEqual(texts(unlabelled), ["[Sam Park] Yes, do that", "[Robin] Can you check mine?"])

    def test_labels_are_read_only_outside_direct_messages(self):
        self.connection.execute("alter table sessions add column chat_type text")
        self.connection.executemany("insert into sessions values (?, 'discord', '111', 0, '/home', ?)",
                                    [("owner-dm", "dm"), ("owner-thread", "thread")])
        self.connection.commit()
        for session in ("owner-dm", "owner-thread"):
            self.message(session, "user", "2026-10-18T01:00:00Z", "[WIP] in " + session)
            self.message(session, "user", "2026-10-18T01:01:00Z", "[Sam Park] signed in " + session)
        _, records, _ = self.read("--user", "111", "--label", "Sam Park")
        self.assertEqual(sorted(texts(records)), ["[Sam Park] signed in owner-dm", "[WIP] in owner-dm", "signed in owner-thread"])

    def test_internal_notifications_are_dropped(self):
        self.connection.execute("alter table messages add column display_kind text")
        self.connection.execute("insert into messages (session_id, role, content, timestamp, display_kind)"
                                " values ('owner-chat', 'user', 'A cron job finished.', ?, 'internal_notification')",
                                (read_turns.parse_time("2026-10-18T01:00:00Z").timestamp(),))
        self.message("owner-chat", "user", "2026-10-18T01:01:00Z", "Why is that?")
        _, records, _ = self.read("--user", "111")
        self.assertEqual(texts(records), ["Why is that?"])

    def test_rows_a_compressed_session_copies_count_once(self):
        self.connection.execute("alter table messages add column platform_message_id text")
        self.connection.execute("insert into sessions values ('owner-chat-2', 'discord', '111', 0, '/home')")
        at = read_turns.parse_time("2026-10-18T01:00:00Z").timestamp()
        insert = "insert into messages (session_id, role, content, timestamp, platform_message_id) values (?, 'user', ?, ?, ?)"
        self.connection.executemany(insert, [
            ("owner-chat", "No, that is not it", at, "d1"),
            ("owner-chat-2", "No, that is not it", at, None),  # copied, same time
            ("owner-chat-2", "[Sam Park] No, that is not it", at + 5, "d1"),  # copied, same platform message
            ("owner-chat-2", "No, that is not it", at + 3600, "d2"),  # said again an hour later
        ])
        self.connection.commit()
        _, records, err = self.read("--user", "111", "--label", "Sam Park")
        self.assertEqual(texts(records), ["No, that is not it", "No, that is not it"])
        self.assertIn("2 turns", err)

    def test_the_owner_must_be_named(self):
        code, _, err = self.read()
        self.assertEqual(code, 2)
        self.assertIn("--user", err)

    def test_local_names_the_terminal_sources_and_can_be_empty(self):
        self.message("owner-chat", "user", "2026-10-18T01:00:00Z", "chat")
        self.message("terminal", "user", "2026-10-18T01:00:00Z", "terminal")
        _, records, _ = self.read("--local", "cli")
        self.assertEqual(texts(records), ["terminal"])
        _, records, _ = self.read("--user", "111", "--local", "")
        self.assertEqual(texts(records), ["chat"])

    def test_an_older_store_without_a_cwd_column_is_read(self):
        self.connection.execute("alter table sessions rename to old")
        self.connection.execute("create table sessions (id text primary key, source text, user_id text)")
        self.connection.execute("insert into sessions select id, source, user_id from old")
        self.connection.commit()
        self.message("owner-chat", "user", "2026-10-18T01:00:00Z", "still read")
        _, records, _ = self.read("--user", "111")
        self.assertEqual(texts(records), ["still read"])
        self.assertEqual(records[0]["cwd"], "")


class Arguments(Base):
    def test_until_must_follow_since(self):
        code, _, err = run("claude", "--since", UNTIL, "--until", SINCE, "--root", str(self.dir))
        self.assertEqual(code, 2)
        self.assertIn("not after", err)

    def test_a_time_without_an_offset_is_utc(self):
        self.assertEqual(read_turns.iso(read_turns.parse_time("2026-10-18T09:00:00")), "2026-10-18T09:00:00Z")
        self.assertEqual(read_turns.iso(read_turns.parse_time("2026-10-18T19:00:00+10:00")), "2026-10-18T09:00:00Z")

    def test_default_until_leaves_turns_being_written_to_the_next_window(self):
        root = self.dir / "projects" / "-work"
        root.mkdir(parents=True)
        now = time.time()

        def stamp(seconds):
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))

        lines = [human("h1", stamp(now - 3600), "an hour ago"), human("h2", stamp(now - 60), "a minute ago")]
        (root / "s1.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
        _, records, err = run("claude", "--since", stamp(now - 7200), "--root", str(self.dir / "projects"))
        self.assertEqual(texts(records), ["an hour ago"])
        self.assertRegex(err, r"through \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


if __name__ == "__main__":
    unittest.main()
