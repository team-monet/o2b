"""Tests for gate_hook.py against throwaway brains, repositories and settings files.

Usage: python3 test_gate_hook.py   (touches nothing outside a temporary directory)
"""

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

import gate_hook

COMMITTING = """---
before: [git commit]
---
# Committing

Commit only what the task changed.
"""

PUBLISHING = """---
before:
  - git push
  - "gh pr create"
---
# Publishing

Ask before anything leaves the machine.
"""

REWRITING = """---
before: git push --force   # the lease variant is allowed
---
# Rewriting history

Do not rewrite shared history.
"""

PLAIN = "# Designing\n\nAnswer every open question.\n"

UNCLOSED = "---\nbefore: [git commit]\n# Broken\n\nNo closing line.\n"

ALPHA_COMMITTING = """---
before: [git commit]
---
# Committing

Alpha commits carry a ticket number.
"""

BETA_MERGING = """---
before: [gh pr merge]
---
# Merging

Beta merges wait for the release window.
"""


def git(*args):
    subprocess.run(["git", *args], check=True, capture_output=True)


class Brain(unittest.TestCase):
    """A throwaway brain with shared pages, two projects, and a repository for one of them."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name).resolve()
        self.root = root
        self.brain = root / "brain"
        self.state = root / "state"
        stages = self.brain / "guidance" / "stages"
        stages.mkdir(parents=True)
        (self.brain / "BRAIN.md").write_text("# BRAIN\n")
        for name, text in {"committing": COMMITTING, "publishing": PUBLISHING, "rewriting": REWRITING,
                           "designing": PLAIN, "broken": UNCLOSED, "unlisted": COMMITTING}.items():
            (stages / f"{name}.md").write_text(text)
        self.index = self.brain / "guidance" / "STAGES.md"
        self.index.write_text(
            "# Shared stages\n\n**Governing parent:** [Guide](README.md).\n\n"
            "| Moment | Applicability |\n|---|---|\n"
            "| [committing](stages/committing.md) | All projects |\n"
            "| [publishing](stages/publishing.md) | All projects |\n"
            "| [rewriting history](stages/rewriting.md) | All projects |\n"
            "| [designing](stages/designing.md) | All projects |\n"
            "| [broken](stages/broken.md) | All projects |\n"
        )
        self.alpha_dir = root / "work" / "alpha"
        (self.alpha_dir / "src").mkdir(parents=True)
        self.beta_repo = root / "repos" / "beta"
        self.beta_repo.mkdir(parents=True)
        git("init", "-q", str(self.beta_repo))
        git("-C", str(self.beta_repo), "remote", "add", "origin", "git@github.com:Acme/beta.git")
        self.projects = self.brain / "projects"
        self.add_project("alpha", "committing", ALPHA_COMMITTING)
        self.add_project("beta", "merging", BETA_MERGING)
        self.rows = [f"| Alpha | alpha | | {self.alpha_dir}; ~/nowhere (other machine) | [Open](alpha/README.md) |",
                     "| Beta | beta | github.com/acme/beta | | [Open](beta/README.md) |"]
        self.write_rows()
        self.elsewhere = root / "elsewhere"
        self.elsewhere.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def add_project(self, name, page, text):
        stages = self.projects / name / "guidance" / "stages"
        stages.mkdir(parents=True)
        (self.projects / name / "README.md").write_text(f"# {name}\n")
        (stages / f"{page}.md").write_text(text)
        (self.projects / name / "guidance" / "STAGES.md").write_text(
            f"# Project stages\n\n| Moment | Applicability |\n|---|---|\n| [{page}](stages/{page}.md) | {name} |\n"
        )

    def write_rows(self):
        (self.projects / "INDEX.md").write_text(
            "# Projects Index\n\n| Project | Names | Remote | Path | Guide |\n|---|---|---|---|---|\n" + "\n".join(self.rows) + "\n"
        )

    def run_hook(self, command, cwd=None, session="s1", agent=None, state=None):
        payload = {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": "Bash",
                   "tool_input": {"command": command}, "cwd": str(cwd or self.elsewhere)}
        if agent:
            payload["agent_id"] = agent
        out = io.StringIO()
        with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", io.StringIO(json.dumps(payload))):
            code = gate_hook.main(["--brain", str(self.brain), "--state-dir", str(state or self.state)])
        self.assertEqual(code, 0)
        text = out.getvalue().strip()
        return json.loads(text) if text else None

    def pages(self, output):
        """The page paths a refusal carries, in order."""
        self.assertIsNotNone(output, "expected the command to be held")
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        reason = decision["permissionDecisionReason"]
        return [line.split(" (before")[0][4:] for line in reason.splitlines() if line.startswith("=== ")]

    def shared(self, name):
        return str(self.brain / "guidance" / "stages" / f"{name}.md")

    def project(self, name, page):
        return str(self.projects / name / "guidance" / "stages" / f"{page}.md")


class DeliveryTest(Brain):
    def test_first_commit_is_held_with_the_page_and_the_retry_passes(self):
        output = self.run_hook('git commit -m "Add the gate hook"')
        self.assertEqual(self.pages(output), [self.shared("committing")])
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("Commit only what the task changed.", reason)
        self.assertIn("(before `git commit`)", reason)
        self.assertIn("stage page for it reaches you", reason)
        self.assertNotIn("before: [git commit]", reason, "frontmatter is not part of the delivered page")
        self.assertIsNone(self.run_hook('git commit -m "Add the gate hook"'))
        self.assertIsNone(self.run_hook("git commit --amend --no-edit"))

    def test_each_session_and_each_subagent_gets_the_page_once(self):
        self.pages(self.run_hook("git commit -m x"))
        self.assertEqual(self.pages(self.run_hook("git commit -m x", session="s2")), [self.shared("committing")])
        self.assertEqual(self.pages(self.run_hook("git commit -m x", agent="a1")), [self.shared("committing")])
        self.assertIsNone(self.run_hook("git commit -m x", agent="a1"))

    def test_a_changed_page_is_delivered_again(self):
        self.pages(self.run_hook("git commit -m x"))
        (self.brain / "guidance" / "stages" / "committing.md").write_text(COMMITTING + "\nNever commit secrets.\n")
        output = self.run_hook("git commit -m x")
        self.assertIn("Never commit secrets.", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_one_command_line_can_need_several_pages(self):
        output = self.run_hook("git add a.md && git commit -m x && git push origin HEAD --force")
        self.assertEqual(self.pages(output), [self.shared("committing"), self.shared("publishing"), self.shared("rewriting")])
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("stage pages for it reach you", reason)
        self.assertNotIn("More pages", reason)

    def test_only_the_undelivered_pages_hold_a_later_command(self):
        self.pages(self.run_hook("git commit -m x"))
        self.assertEqual(self.pages(self.run_hook("git commit -m y; git push")), [self.shared("publishing")])

    def test_a_command_added_to_a_delivered_page_delivers_it_again(self):
        page = self.brain / "guidance" / "stages" / "committing.md"
        self.pages(self.run_hook("git commit -m x"))
        page.write_text(COMMITTING.replace("before: [git commit]", "before: [git commit, git tag]"))
        self.assertEqual(self.pages(self.run_hook("git tag v1")), [self.shared("committing")])

    def test_pages_too_long_for_one_message_come_over_several_attempts(self):
        filler = "A rule that takes room. " * 160  # about 3,800 characters
        for name in ("committing", "publishing", "rewriting"):
            page = self.brain / "guidance" / "stages" / f"{name}.md"
            page.write_text(page.read_text() + filler)
        command = "git commit -m x && git push --force"
        first = self.run_hook(command)
        self.assertEqual(self.pages(first), [self.shared("committing"), self.shared("publishing")])
        self.assertLess(len(first["hookSpecificOutput"]["permissionDecisionReason"]), 10000)
        self.assertIn("More pages for this command come on the next attempt.", first["hookSpecificOutput"]["permissionDecisionReason"])
        second = self.run_hook(command)
        self.assertEqual(self.pages(second), [self.shared("rewriting")])
        self.assertNotIn("More pages", second["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIsNone(self.run_hook(command))

    def test_a_page_too_long_alone_is_cut_and_still_delivered_once(self):
        page = self.brain / "guidance" / "stages" / "committing.md"
        page.write_text(COMMITTING + "A rule that takes room. " * 600)
        output = self.run_hook("git commit -m x")
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertLess(len(reason), 10000)
        self.assertIn("Commit only what the task changed.", reason)
        self.assertIn(f"The page continues; read the rest at {self.shared('committing')}.", reason)
        self.assertIsNone(self.run_hook("git commit -m x"))

    def test_text_outside_ascii_is_budgeted_as_it_is_sent(self):
        page = self.brain / "guidance" / "stages" / "committing.md"
        page.write_text(COMMITTING + "\u65e5\u672c\u8a9e\u306e\u898f\u5247\u3002\n" * 1300)  # about 10,400 characters
        payload = json.dumps({"session_id": "utf", "tool_input": {"command": "git commit -m x"}, "cwd": str(self.elsewhere)})
        command = gate_hook.entry_command() + f" --brain '{self.brain}' --state-dir '{self.state}'"
        result = subprocess.run(["sh", "-c", command], input=payload.encode(), capture_output=True, env=dict(os.environ, LC_ALL="en_US.ISO8859-1", LANG="en_US.ISO8859-1"))
        self.assertEqual(result.returncode, 0, result.stderr)
        reason = json.loads(result.stdout.decode("utf-8"))["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("\u65e5\u672c\u8a9e", result.stdout.decode("utf-8"), "sent as UTF-8, not escaped")
        self.assertLess(len(json.dumps(reason, ensure_ascii=False)), 10000)
        self.assertTrue("The page continues" in reason, "a page over the limit is cut")
        self.assertGreater(len(json.dumps(reason, ensure_ascii=False)), gate_hook.REASON_LIMIT - 1500, "the cut keeps most of the room")

    def test_an_unwritable_state_hands_the_pages_over_without_holding(self):
        blocker = self.root / "not-a-folder"
        blocker.write_text("")
        other = self.root / "someone-elses"
        other.mkdir()
        link = self.root / "linked-state"
        link.symlink_to(other)
        for state in (blocker / "state", link):
            for attempt in range(2):
                with self.subTest(state=state.name, attempt=attempt):
                    output = self.run_hook("git commit -m x", state=state)
                    self.assertNotIn("permissionDecision", output["hookSpecificOutput"])
                    self.assertIn("Commit only what the task changed.", output["hookSpecificOutput"]["additionalContext"])
                    self.assertIn("arrives after it ran", output["hookSpecificOutput"]["additionalContext"])
                    self.assertIn("could not record", output["systemMessage"])
        self.assertEqual(list(other.iterdir()), [], "nothing is written through a linked state folder")

    def test_old_state_is_pruned_and_nothing_else(self):
        self.pages(self.run_hook("git commit -m x", session="old"))
        old = next(self.state.glob("*.json"))
        keep = self.state / "package.json"
        keep.write_text("{}")
        long_ago = time.time() - 30 * 86400
        for path in (old, keep):
            os.utime(path, (long_ago, long_ago))
        self.pages(self.run_hook("git commit -m x", session="new"))
        self.assertFalse(old.exists())
        self.assertTrue(keep.exists())

    def test_unreadable_input_says_so_instead_of_staying_silent(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", io.StringIO("not json")):
            gate_hook.main(["--brain", str(self.brain), "--state-dir", str(self.state)])
        self.assertIn("could not read its input", json.loads(out.getvalue())["systemMessage"])

    def test_a_call_without_a_command_passes(self):
        out = io.StringIO()
        payload = json.dumps({"session_id": "s1", "tool_name": "Read", "tool_input": {"file_path": "/x"}})
        with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", io.StringIO(payload)):
            gate_hook.main(["--brain", str(self.brain), "--state-dir", str(self.state)])
        self.assertEqual(out.getvalue(), "")

    def test_a_missing_brain_says_so(self):
        out = io.StringIO()
        payload = json.dumps({"session_id": "s1", "tool_input": {"command": "git commit"}, "cwd": "/"})
        with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", io.StringIO(payload)):
            gate_hook.main(["--brain", str(self.root / "gone"), "--state-dir", str(self.state)])
        self.assertIn("is not a brain", json.loads(out.getvalue())["systemMessage"])

    def test_run_as_claude_code_runs_it(self):
        payload = json.dumps({"session_id": "proc", "tool_input": {"command": "git commit -m x"}, "cwd": str(self.elsewhere)})
        command = gate_hook.entry_command() + f" --brain '{self.brain}' --state-dir '{self.state}'"
        result = subprocess.run(["sh", "-c", command], input=payload, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.pages(json.loads(result.stdout)), [self.shared("committing")])

    def test_an_installed_command_whose_script_is_gone_does_not_refuse(self):
        gone = gate_hook.entry_command(self.root / "removed" / "agent" / "operations" / "gate-hook" / "gate_hook.py")
        result = subprocess.run(["sh", "-c", gone], input="{}", capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 2, "exit 2 makes Claude Code refuse every Bash call")
        self.assertEqual(result.returncode, 1)

    def test_explain_lists_pages_without_remembering_a_delivery(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            gate_hook.main(["--brain", str(self.brain), "--explain", "git commit -m x", "--cwd", str(self.alpha_dir)])
        self.assertIn(str(self.projects / "alpha"), out.getvalue())
        self.assertIn(self.shared("committing") + "  (before `git commit`)", out.getvalue())
        self.assertFalse(self.state.exists())


class MatchingTest(Brain):
    def test_command_forms_that_run_the_gated_command(self):
        forms = [
            "cd /tmp && git -C /some/repo commit -m x",
            "git -c user.name=x --no-pager commit -m x",
            "FOO=1 GIT_EDITOR=true git commit",
            "env FOO=1 /usr/bin/git commit -m x",
            "env -u FOO git commit -m x",
            "sudo -u bob git commit -m x",
            "timeout 120 git commit -m x",
            "nice -n 5 git commit -m x",
            "echo a | xargs git commit -m",
            "bash -lc 'git commit -m x'",
            "sudo bash -c 'git commit -m x'",
            "env FOO=1 bash -c 'git commit -m x'",
            "echo $(git commit -m x)",
            'echo "Made: $(git commit -m x)"',
            "echo `git commit -m x`",
            "if git diff --quiet; then echo clean; else git commit -am wip; fi",
            "{ git commit -m x; }",
            "! git commit -m x",
            "for f in a; do git commit -m x; done",
            "curl -s https://x.example/#frag && git commit -m x",
            "git status\ngit commit -m x",
            "git status \\\n  && git commit -m x",
            "cat > notes.txt <<'EOF'\nit's here\nEOF\ngit commit -m x",
            'git commit -m "$(cat <<\'EOF\'\nDon\'t stop (1) here.\nEOF\n)"',
            "git status -m 'use <<EOF in scripts'\ngit commit -m x",
            "echo it's\ngit commit -m x",
            "grep x <<< hello\ngit commit -m x",
            "# it's done\necho \"$(git commit -m x)\"",
        ]
        for i, command in enumerate(forms):
            with self.subTest(command=command):
                self.assertEqual(self.pages(self.run_hook(command, session=f"form{i}")), [self.shared("committing")])

    def test_command_forms_that_do_not_run_it(self):
        forms = [
            "git status",
            "git log --grep commit",
            "git log --oneline commit",
            "git stash push -m wip",
            "git commit-tree HEAD^{tree}",
            "echo 'git commit -m x'",
            'grep -r "git commit" .',
            "gitk commit",
            "cat <<EOF\ngit commit -m x\nEOF",
            "grep x <<< hello\ngit status",
            "echo it's\ngit status",
            "git status # then git commit",
            "echo done # git commit; git push",
            "sudo ls git-commit",
            "echo '$(git commit -m x)'",
            "rg '`git commit`' docs/",
            "printf '%s\\n' '`git commit -m x`'",
            "python3 -c 'print(\"`git commit`\")'",
            "awk '{print $(NF)}' f && git status",
            "echo $((1+2)) && git status",
            "timeout 5 echo git commit",
            "xargs -n1 echo git commit < list",
            "cat > x.sh <<EOF\necho $(git commit -m x)\nEOF",
            "# see $(git commit) in the docs\ngit status",
        ]
        for i, command in enumerate(forms):
            with self.subTest(command=command):
                self.assertIsNone(self.run_hook(command, session=f"none{i}"))

    def test_commands_quoted_in_a_message_are_text(self):
        bodies = {
            "gh pr create --title x --body \"$(cat <<'EOF'\n## Summary\nRefuses `git push --force` and `git commit`.\nEOF\n)\"": [self.shared("publishing")],
            "git commit -m \"$(cat <<'EOF'\nGate `git push` behind (1) the page\nEOF\n)\"": [self.shared("committing")],
            "git commit -m 'Explain `git push --force` in docs'": [self.shared("committing")],
            "git commit -m 'docs: mention $(git push) usage'": [self.shared("committing")],
            "git commit -m \"$(git push)\"": [self.shared("committing"), self.shared("publishing")],
        }
        for i, (command, expected) in enumerate(bodies.items()):
            with self.subTest(command=command):
                self.assertEqual(self.pages(self.run_hook(command, session=f"msg{i}")), expected)

    def test_option_words_in_a_gate(self):
        cases = {
            "git push --force-with-lease origin main": [self.shared("publishing")],
            "git push origin main --force": [self.shared("publishing"), self.shared("rewriting")],
            "git push --force=yes": [self.shared("publishing"), self.shared("rewriting")],
        }
        for i, (command, expected) in enumerate(cases.items()):
            with self.subTest(command=command):
                self.assertEqual(self.pages(self.run_hook(command, session=f"opt{i}")), expected)

    def test_a_short_option_inside_a_cluster(self):
        page = self.brain / "guidance" / "stages" / "rewriting.md"
        page.write_text(REWRITING.replace("before: git push --force", "before: [git push --force, git push -f]"))
        self.assertEqual(self.pages(self.run_hook("git push -uf origin main")), [self.shared("publishing"), self.shared("rewriting")])
        self.assertEqual(self.pages(self.run_hook("git push -u origin main", session="s2")), [self.shared("publishing")])

    def test_an_option_in_a_gate_matches_its_value_form(self):
        (self.brain / "guidance" / "stages" / "lease.md").write_text("---\nbefore: [git push --force-with-lease]\n---\n# Lease\n")
        self.index.write_text(self.index.read_text() + "| [lease](stages/lease.md) | All projects |\n")
        output = self.run_hook("git push --force-with-lease=main:abc123 origin main")
        self.assertEqual(self.pages(output), [self.shared("publishing"), self.shared("lease")])

    def test_a_list_item_in_quotes_is_a_command(self):
        self.assertEqual(self.pages(self.run_hook("gh pr create --fill")), [self.shared("publishing")])

    def test_a_command_that_names_no_gated_program_is_not_parsed(self):
        with unittest.mock.patch.object(gate_hook, "simple_commands", side_effect=AssertionError("parsed")):
            self.assertIsNone(self.run_hook("ls -la && echo 'it's"))


class PagesTest(Brain):
    def test_a_project_adds_its_pages_inside_its_path(self):
        output = self.run_hook("git commit -m x", cwd=self.alpha_dir / "src")
        self.assertEqual(self.pages(output), [self.shared("committing"), self.project("alpha", "committing")])
        self.assertIn("ticket number", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_a_project_matched_by_its_repository_remote(self):
        self.assertEqual(self.pages(self.run_hook("gh pr merge 12 --squash", cwd=self.beta_repo)), [self.project("beta", "merging")])

    def test_a_push_url_is_not_the_projects_remote(self):
        git("-C", str(self.beta_repo), "remote", "set-url", "--push", "origin", "git@github.com:acme/gamma.git")
        self.add_project("gamma", "merging", BETA_MERGING.replace("Beta", "Gamma"))
        self.rows.append("| Gamma | gamma | github.com/acme/gamma | | [Open](gamma/README.md) |")
        self.write_rows()
        self.assertEqual(self.pages(self.run_hook("gh pr merge 1", cwd=self.beta_repo)), [self.project("beta", "merging")])

    def test_another_projects_pages_stay_out(self):
        self.assertIsNone(self.run_hook("gh pr merge 12 --squash", cwd=self.alpha_dir))
        self.assertEqual(self.pages(self.run_hook("git commit -m x", cwd=self.beta_repo)), [self.shared("committing")])

    def test_the_closest_row_wins(self):
        (self.beta_repo / "tools").mkdir()
        self.add_project("gamma", "merging", BETA_MERGING.replace("Beta", "Gamma"))
        self.add_project("outer", "merging", BETA_MERGING.replace("Beta", "Outer"))
        self.rows += [f"| Gamma | gamma | | {self.beta_repo / 'tools'} | [Open](gamma/README.md) |",
                      f"| Outer | outer | | {self.root / 'repos'} | [Open](outer/README.md) |"]
        self.write_rows()
        cases = {
            self.beta_repo / "tools": "gamma",  # a path inside the repository beats its remote
            self.beta_repo: "beta",  # the repository's remote beats a path above it
            self.root / "repos": "outer",
        }
        for i, (cwd, name) in enumerate(cases.items()):
            with self.subTest(cwd=cwd):
                self.assertEqual(self.pages(self.run_hook("gh pr merge 1", cwd=cwd, session=f"row{i}")), [self.project(name, "merging")])

    def test_pages_outside_the_index_or_without_closed_frontmatter_are_ignored(self):
        paths = self.pages(self.run_hook("git commit -m x"))
        self.assertNotIn(self.shared("unlisted"), paths)
        self.assertNotIn(self.shared("broken"), paths)

    def test_other_links_in_an_index_are_not_pages(self):
        (self.brain / "guidance" / "OPERATING.md").write_text(COMMITTING)
        self.index.write_text(self.index.read_text() + "\nSee also [operating conventions](OPERATING.md).\n")
        self.assertEqual(self.pages(self.run_hook("git commit -m x")), [self.shared("committing")])

    def test_a_brain_without_pages_that_name_commands_holds_nothing(self):
        for page in (self.brain / "guidance" / "stages").glob("*.md"):
            page.write_text(PLAIN)
        for page in self.projects.glob("*/guidance/stages/*.md"):
            page.write_text(PLAIN)
        self.assertIsNone(self.run_hook("git commit -m x && git push --force"))


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.settings = self.root / ".claude" / "settings.json"
        self.settings.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, *flags):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = gate_hook.main([*flags, "--settings", str(self.settings)])
        return code, out.getvalue()

    def entries(self):
        settings = json.loads(self.settings.read_text())
        return [h for _, h in gate_hook.handlers(settings) if gate_hook.gate_scripts(h.get("command"))]

    def test_install_keeps_existing_settings_and_hooks(self):
        original = {"model": "opus", "hooks": {"PreToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "lint"}]}],
                                                "Stop": [{"hooks": [{"type": "command", "command": "notify"}]}]}}
        self.settings.write_text(json.dumps(original))
        code, out = self.call("--install")
        self.assertEqual(code, 0, out)
        settings = json.loads(self.settings.read_text())
        self.assertEqual(settings["model"], "opus")
        self.assertEqual(settings["hooks"]["Stop"], original["hooks"]["Stop"])
        self.assertEqual(settings["hooks"]["PreToolUse"][0], original["hooks"]["PreToolUse"][0])
        self.assertEqual(settings["hooks"]["PreToolUse"][1], {"matcher": "Bash", "hooks": [{"type": "command", "command": gate_hook.entry_command()}]})
        backups = list(self.settings.parent.glob("settings.json.bak-o2b-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), original)
        self.assertEqual(self.call("--check"), (0, ""))

    def test_install_twice_adds_one_entry_and_no_second_backup(self):
        self.call("--install")
        code, out = self.call("--install")
        self.assertIn("already runs", out)
        self.assertEqual(len(self.entries()), 1)
        self.assertEqual(list(self.settings.parent.glob("*.bak-o2b-*")), [])

    def test_an_entry_under_another_matcher_is_not_installed(self):
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Edit", "hooks": [{"type": "command", "command": gate_hook.entry_command()}]}]}}))
        code, out = self.call("--check")
        self.assertEqual(code, 1)
        self.assertIn("does not run", out)
        self.call("--install")
        self.assertEqual(self.call("--check"), (0, ""))
        for matcher in ("Bash|Edit", "*", "", "Edit, Bash"):
            with self.subTest(matcher=matcher):
                self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
                    {"matcher": matcher, "hooks": [{"type": "command", "command": gate_hook.entry_command()}]}]}}))
                self.assertEqual(self.call("--check"), (0, ""))

    def test_check_names_a_gate_hook_whose_script_is_gone(self):
        gone = self.root / "removed-worktree" / "agent" / "operations" / "gate-hook" / "gate_hook.py"
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": f"python3 {gone}"}]}]}}))
        code, out = self.call("--check")
        self.assertEqual(code, 1)
        self.assertIn(f"runs {gone}, which does not exist", out)
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": gate_hook.entry_command(gone)}]}]}}))
        code, out = self.call("--check")
        self.assertEqual(out.count("which does not exist"), 1, "one problem per entry, though the entry names the script twice")
        self.assertIn("does not run", out)
        self.call("--uninstall")
        self.assertEqual(json.loads(self.settings.read_text()), {})

    def test_check_reads_home_relative_spellings(self):
        home = Path(os.path.expanduser("~"))
        if not str(gate_hook.SCRIPT).startswith(str(home) + os.sep):
            self.skipTest("the script is not under the home folder")
        relative = os.path.relpath(gate_hook.SCRIPT, home)
        for spelling in (f"~/{relative}", f"$HOME/{relative}", f"${{HOME}}/{relative}"):
            with self.subTest(spelling=spelling):
                self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": f"python3 {spelling}"}]}]}}))
                self.assertEqual(self.call("--check"), (0, ""))

    def test_uninstall_removes_only_this_hook(self):
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "audit"}, {"type": "command", "command": gate_hook.entry_command()}]},
        ]}}))
        code, out = self.call("--uninstall")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(self.settings.read_text()), {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "audit"}]}]}})
        self.call("--install")
        self.call("--uninstall")
        self.assertEqual(self.entries(), [])

    def test_uninstall_leaves_another_live_brains_hook(self):
        other = self.root / "other-brain" / "agent" / "operations" / "gate-hook" / "gate_hook.py"
        other.parent.mkdir(parents=True)
        other.write_text("")
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": gate_hook.entry_command(other)}]}]}}))
        self.call("--uninstall")
        self.assertEqual(len(self.entries()), 1)

    def test_uninstall_of_the_only_hook_leaves_no_empty_hooks(self):
        self.call("--install")
        self.call("--uninstall")
        self.assertEqual(json.loads(self.settings.read_text()), {})

    def test_a_linked_settings_file_is_written_through_with_its_mode(self):
        real = self.root / "dotfiles" / "settings.json"
        real.parent.mkdir()
        real.write_text('{"model": "opus"}')
        os.chmod(real, 0o600)
        self.settings.symlink_to(real)
        self.call("--install")
        self.assertTrue(self.settings.is_symlink())
        self.assertIn("PreToolUse", json.loads(real.read_text())["hooks"])
        self.assertEqual(stat.S_IMODE(real.stat().st_mode), 0o600)
        backups = list(real.parent.glob("settings.json.bak-o2b-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode), 0o600)

    def test_a_new_settings_file_is_private(self):
        self.call("--install")
        self.assertEqual(stat.S_IMODE(self.settings.stat().st_mode), 0o600)

    def test_unreadable_settings_are_left_alone(self):
        for text in ("{not json", '{"hooks": []}', '{"hooks": {"PreToolUse": {}}}', "[]"):
            with self.subTest(text=text):
                self.settings.write_text(text)
                code, out = self.call("--install")
                self.assertEqual(code, 1)
                self.assertIn("nothing was changed", out)
                self.assertEqual(self.settings.read_text(), text)
                self.assertEqual(list(self.settings.parent.glob("*.bak-o2b-*")), [])
                code, out = self.call("--check")
                self.assertEqual(code, 1)
                self.assertIn("cannot be read", out)


if __name__ == "__main__":
    unittest.main()
