"""Tests for gate_hook.py against throwaway brains, repositories and settings files.

Usage: python3 test_gate_hook.py   (touches nothing outside a temporary directory)
"""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import gate_hook

COMMIT = """---
before: [git commit]
---
# Commit changes

Stage only the paths you changed.
"""

PUSH = """---
before:
  - git push
  - "gh pr create"
---
# Publish

Ask before anything leaves the machine.
"""

FORCE = """---
before: git push --force   # the lease variant is allowed
---
# Git force push

Never force-push.
"""

PLAIN = "# Write a design\n\nSettle every question.\n"

UNCLOSED = "---\nbefore: [git commit]\n# Broken\n\nNo closing line.\n"

PROJECT_COMMIT = """---
before: [git commit]
---
# Commit changes

Alpha commits carry a ticket number.
"""

BETA_MERGE = """---
before: [gh pr merge]
---
# Merge a pull request

Beta merges wait for the release window.
"""


class GateHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name).resolve()
        self.root = root
        self.brain = root / "brain"
        self.state = root / "state"
        stages = self.brain / "guidance" / "stages"
        stages.mkdir(parents=True)
        (self.brain / "BRAIN.md").write_text("# BRAIN\n")
        for name, text in {"commit-changes": COMMIT, "publish": PUSH, "git-force-push": FORCE,
                           "write-a-design": PLAIN, "broken": UNCLOSED, "unlisted": COMMIT}.items():
            (stages / f"{name}.md").write_text(text)
        (self.brain / "guidance" / "STAGES.md").write_text(
            "# Shared stages\n\n**Governing parent:** [Guide](README.md).\n\n"
            "| Moment | Applicability |\n|---|---|\n"
            "| [commit changes](stages/commit-changes.md) | All projects |\n"
            "| [publish](stages/publish.md) | All projects |\n"
            "| [git force push](stages/git-force-push.md) | All projects |\n"
            "| [write a design](stages/write-a-design.md) | All projects |\n"
            "| [broken](stages/broken.md) | All projects |\n"
        )
        self.alpha_dir = root / "work" / "alpha"
        (self.alpha_dir / "src").mkdir(parents=True)
        self.beta_repo = root / "repos" / "beta"
        self.beta_repo.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.beta_repo)], check=True)
        subprocess.run(["git", "-C", str(self.beta_repo), "remote", "add", "origin", "git@github.com:Acme/beta.git"], check=True)
        projects = self.brain / "projects"
        for name, page, text in (("alpha", "commit-changes", PROJECT_COMMIT), ("beta", "merge-a-pull-request", BETA_MERGE)):
            (projects / name / "guidance" / "stages").mkdir(parents=True)
            (projects / name / "README.md").write_text(f"# {name}\n")
            (projects / name / "guidance" / "stages" / f"{page}.md").write_text(text)
            (projects / name / "guidance" / "STAGES.md").write_text(
                f"# Project stages\n\n| Moment | Applicability |\n|---|---|\n| [{page}](stages/{page}.md) | {name} |\n"
            )
        (projects / "INDEX.md").write_text(
            "# Projects Index\n\n"
            "| Project | Names | Remote | Path | Guide |\n|---|---|---|---|---|\n"
            f"| Alpha | alpha | | {self.alpha_dir}; ~/nowhere (other machine) | [Open](alpha/README.md) |\n"
            "| Beta | beta | github.com/acme/beta | | [Open](beta/README.md) |\n"
        )
        self.elsewhere = root / "elsewhere"
        self.elsewhere.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, command, cwd=None, session="s1", agent=None, state=None):
        payload = {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": "Bash",
                   "tool_input": {"command": command}, "cwd": str(cwd or self.elsewhere)}
        if agent:
            payload["agent_id"] = agent
        out = io.StringIO()
        stdin = io.StringIO(json.dumps(payload))
        with contextlib.redirect_stdout(out), unittest.mock.patch("sys.stdin", stdin):
            code = gate_hook.main(["--brain", str(self.brain), "--state-dir", str(state or self.state)])
        self.assertEqual(code, 0)
        text = out.getvalue().strip()
        return json.loads(text) if text else None

    def pages(self, output):
        """The page paths a refusal carries, in order."""
        self.assertIsNotNone(output, "expected the command to be stopped")
        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        reason = decision["permissionDecisionReason"]
        return [line.split(" (before")[0][4:] for line in reason.splitlines() if line.startswith("=== ")]

    def shared(self, name):
        return str(self.brain / "guidance" / "stages" / f"{name}.md")

    def test_first_commit_is_stopped_with_the_page_and_the_retry_passes(self):
        output = self.run_hook('git commit -m "Add the gate hook"')
        self.assertEqual(self.pages(output), [self.shared("commit-changes")])
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("Stage only the paths you changed.", reason)
        self.assertIn("(before `git commit`)", reason)
        self.assertIn("stage page for it reaches you", reason)
        self.assertNotIn("before: [git commit]", reason, "frontmatter is not part of the delivered page")
        self.assertIsNone(self.run_hook('git commit -m "Add the gate hook"'))
        self.assertIsNone(self.run_hook("git commit --amend --no-edit"))

    def test_each_session_and_each_subagent_gets_the_page_once(self):
        self.pages(self.run_hook("git commit -m x"))
        self.assertEqual(self.pages(self.run_hook("git commit -m x", session="s2")), [self.shared("commit-changes")])
        self.assertEqual(self.pages(self.run_hook("git commit -m x", agent="a1")), [self.shared("commit-changes")])
        self.assertIsNone(self.run_hook("git commit -m x", agent="a1"))

    def test_a_changed_page_is_delivered_again(self):
        self.pages(self.run_hook("git commit -m x"))
        page = self.brain / "guidance" / "stages" / "commit-changes.md"
        page.write_text(COMMIT + "\nNever commit secrets.\n")
        output = self.run_hook("git commit -m x")
        self.assertIn("Never commit secrets.", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_one_command_line_can_need_several_pages(self):
        output = self.run_hook("git add a.md && git commit -m x && git push origin HEAD --force")
        self.assertEqual(self.pages(output), [self.shared("commit-changes"), self.shared("publish"), self.shared("git-force-push")])
        self.assertIn("stage pages for it reach you", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_only_the_undelivered_pages_stop_a_later_command(self):
        self.pages(self.run_hook("git commit -m x"))
        self.assertEqual(self.pages(self.run_hook("git commit -m y; git push")), [self.shared("publish")])

    def test_command_forms_that_run_the_gated_command(self):
        forms = [
            "cd /tmp && git -C /some/repo commit -m x",
            "git -c user.name=x --no-pager commit -m x",
            "FOO=1 GIT_EDITOR=true git commit",
            "env FOO=1 /usr/bin/git commit -m x",
            "bash -lc 'git commit -m x'",
            "echo $(git commit -m x)",
            "git status\ngit commit -m x",
            "git status \\\n  && git commit -m x",
            "cat > notes.txt <<'EOF'\nit's here\nEOF\ngit commit -m x",
            'git commit -m "$(cat <<\'EOF\'\nDon\'t stop.\nEOF\n)"',
            "echo it's\ngit commit -m x",
            "grep x <<< hello\ngit commit -m x",
        ]
        for i, command in enumerate(forms):
            with self.subTest(command=command):
                self.assertEqual(self.pages(self.run_hook(command, session=f"form{i}")), [self.shared("commit-changes")])

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
            "git push --force-with-lease origin main && git status --porcelain",
        ]
        for i, command in enumerate(forms):
            with self.subTest(command=command):
                output = self.run_hook(command, session=f"none{i}")
                if command.startswith("git push"):
                    self.assertEqual(self.pages(output), [self.shared("publish")], "the lease variant is not --force")
                else:
                    self.assertIsNone(output)

    def test_a_list_item_in_quotes_is_a_command(self):
        self.assertEqual(self.pages(self.run_hook("gh pr create --fill")), [self.shared("publish")])

    def test_a_project_adds_its_pages_inside_its_path(self):
        output = self.run_hook("git commit -m x", cwd=self.alpha_dir / "src")
        alpha = str(self.brain / "projects" / "alpha" / "guidance" / "stages" / "commit-changes.md")
        self.assertEqual(self.pages(output), [self.shared("commit-changes"), alpha])
        self.assertIn("ticket number", output["hookSpecificOutput"]["permissionDecisionReason"])

    def test_a_project_matched_by_its_repository_remote(self):
        output = self.run_hook("gh pr merge 12 --squash", cwd=self.beta_repo)
        beta = str(self.brain / "projects" / "beta" / "guidance" / "stages" / "merge-a-pull-request.md")
        self.assertEqual(self.pages(output), [beta])

    def test_another_projects_pages_stay_out(self):
        self.assertIsNone(self.run_hook("gh pr merge 12 --squash", cwd=self.alpha_dir))
        self.assertEqual(self.pages(self.run_hook("git commit -m x", cwd=self.beta_repo)), [self.shared("commit-changes")])

    def test_pages_outside_the_index_or_without_closed_frontmatter_are_ignored(self):
        output = self.run_hook("git commit -m x")
        paths = self.pages(output)
        self.assertNotIn(self.shared("unlisted"), paths)
        self.assertNotIn(self.shared("broken"), paths)

    def test_other_links_in_an_index_are_not_pages(self):
        (self.brain / "guidance" / "OPERATING.md").write_text(COMMIT)
        index = self.brain / "guidance" / "STAGES.md"
        index.write_text(index.read_text() + "\nSee also [operating conventions](OPERATING.md).\n")
        self.assertEqual(self.pages(self.run_hook("git commit -m x")), [self.shared("commit-changes")])

    def test_an_option_in_a_gate_matches_its_value_form(self):
        (self.brain / "guidance" / "stages" / "lease.md").write_text("---\nbefore: [git push --force-with-lease]\n---\n# Lease\n")
        index = self.brain / "guidance" / "STAGES.md"
        index.write_text(index.read_text() + "| [lease](stages/lease.md) | All projects |\n")
        output = self.run_hook("git push --force-with-lease=main:abc123 origin main")
        self.assertEqual(self.pages(output), [self.shared("publish"), self.shared("lease")])

    def test_a_brain_without_pages_that_name_commands_stops_nothing(self):
        for page in (self.brain / "guidance" / "stages").glob("*.md"):
            page.write_text(PLAIN)
        self.assertIsNone(self.run_hook("git commit -m x && git push --force"))

    def test_an_unwritable_state_hands_the_pages_over_without_stopping(self):
        blocker = self.root / "not-a-folder"
        blocker.write_text("")
        for attempt in range(2):
            output = self.run_hook("git commit -m x", state=blocker / "state")
            self.assertNotIn("permissionDecision", output["hookSpecificOutput"])
            self.assertIn("Stage only the paths you changed.", output["hookSpecificOutput"]["additionalContext"])
            self.assertIn("could not record", output["systemMessage"])
            self.assertIn("arrives after it ran", output["hookSpecificOutput"]["additionalContext"])

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
        output = io.StringIO()
        payload = json.dumps({"session_id": "s1", "tool_input": {"command": "git commit"}, "cwd": "/"})
        with contextlib.redirect_stdout(output), unittest.mock.patch("sys.stdin", io.StringIO(payload)):
            gate_hook.main(["--brain", str(self.root / "gone"), "--state-dir", str(self.state)])
        self.assertIn("is not a brain", json.loads(output.getvalue())["systemMessage"])

    def test_explain_lists_pages_without_remembering_a_delivery(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            gate_hook.main(["--brain", str(self.brain), "--explain", "git commit -m x", "--cwd", str(self.alpha_dir)])
        self.assertIn(str(self.brain / "projects" / "alpha"), out.getvalue())
        self.assertIn(self.shared("commit-changes") + "  (before `git commit`)", out.getvalue())
        self.assertFalse(self.state.exists())


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = Path(self.tmp.name) / ".claude" / "settings.json"

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, *flags):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = gate_hook.main([*flags, "--settings", str(self.settings)])
        return code, out.getvalue()

    def entries(self):
        groups = json.loads(self.settings.read_text())["hooks"]["PreToolUse"]
        return [h for g in groups for h in g["hooks"] if gate_hook.runs_this(h)]

    def test_install_keeps_existing_settings_and_hooks(self):
        self.settings.parent.mkdir(parents=True)
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

    def test_install_twice_adds_one_entry_and_no_second_backup(self):
        self.call("--install")
        code, out = self.call("--install")
        self.assertIn("already runs", out)
        self.assertEqual(len(self.entries()), 1)
        self.assertEqual(list(self.settings.parent.glob("*.bak-o2b-*")), [])

    def test_uninstall_removes_only_this_hook(self):
        self.settings.parent.mkdir(parents=True)
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "audit"}, {"type": "command", "command": gate_hook.entry_command()}]},
        ]}}))
        code, out = self.call("--uninstall")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(self.settings.read_text()), {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "audit"}]}]}})
        self.call("--install")
        self.call("--uninstall")
        self.assertEqual(self.entries(), [])

    def test_uninstall_of_the_only_hook_leaves_no_empty_hooks(self):
        self.call("--install")
        self.call("--uninstall")
        self.assertEqual(json.loads(self.settings.read_text()), {})

    def test_unreadable_settings_are_left_alone(self):
        self.settings.parent.mkdir(parents=True)
        for text in ("{not json", '{"hooks": []}', '{"hooks": {"PreToolUse": {}}}', "[]"):
            with self.subTest(text=text):
                self.settings.write_text(text)
                code, out = self.call("--install")
                self.assertEqual(code, 1)
                self.assertIn("nothing was changed", out)
                self.assertEqual(self.settings.read_text(), text)
                self.assertEqual(list(self.settings.parent.glob("*.bak-o2b-*")), [])


if __name__ == "__main__":
    unittest.main()
