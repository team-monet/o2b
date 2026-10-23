#!/usr/bin/env python3
"""Tests for inventory.py: items are found wherever they sit, tests and installed code
are not items, the inventory's frontmatter sets source and scope, a repository is read
through `gh`, and drift fails.

Usage: python3 -I test_inventory.py   (touches nothing outside a temporary directory)
"""
import base64
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "inventory.py"
sys.path.insert(0, str(TOOL.parent))
import inventory  # noqa: E402

FRONTMATTER = "---\nsource: brain\n---\n"
HEADER = "| Item | Kind | Eval | Eval of eval | Checked | Finding |\n|---|---|---|---|---|---|\n"
WORKFLOW = "name: CI\non: push\njobs:\n  build:\n    runs-on: x\n  test:\n    runs-on: x\n"
TREE = [
    ".claude/skills/ship/SKILL.md", ".agents/skills/plan/SKILL.md", "docs/skills/notes/SKILL.md",
    "scripts/harvest.mjs", "scripts/deploy", "scripts/test_deploy.py", "scripts/data.json",
    "scripts/lib/util.py", ".github/workflows/ci.yml", "src/app.ts",
]
REPO_ITEMS = [".agents/skills/plan", ".claude/skills/ship", ".github/workflows/ci.yml#build",
              ".github/workflows/ci.yml#test", "scripts/deploy", "scripts/harvest.mjs"]
# A stand-in for `gh api`, answering from TREE and WORKFLOW; GH_STUB_MODE picks a failure.
GH_STUB = """#!{python}
import base64, json, os, sys
mode, path = os.environ.get("GH_STUB_MODE", "ok"), sys.argv[2]
if mode == "fail":
    sys.stderr.write("HTTP 404: Not Found\\n")
    sys.exit(1)
if mode == "garbage":
    print("<html>rate limited</html>")
elif path.startswith("repos/owner/repo/git/trees/"):
    tree = [{{"path": p, "type": "blob"}} for p in {tree!r}] + [{{"path": "scripts", "type": "tree"}}]
    print(json.dumps({{"truncated": mode == "truncated", "tree": tree}}))
elif path == "repos/owner/repo/contents/.github/workflows/ci.yml":
    print(json.dumps({{"content": base64.b64encode({workflow!r}.encode()).decode()}}))
else:
    sys.stderr.write("HTTP 404: Not Found\\n")
    sys.exit(1)
"""


def write(root, rel, text="", executable=False):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip())
    if executable:
        path.chmod(0o755)
    return path


def rows(items):
    return "".join(f"| `{i}` | kind | none | — | 2026-10-16 | — |\n" for i in items)


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "BRAIN.md", "# Brain\n")
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: demo\n---\n")
        write(self.root, "agent/skills/group/nested/SKILL.md", "---\nname: nested\n---\n")
        write(self.root, "agent/skills/demo/scripts/run.py", "print(1)\n")
        write(self.root, "agent/skills/demo/scripts/build.mjs")
        write(self.root, "agent/skills/demo/scripts/watch", "#!/bin/sh\n", executable=True)
        write(self.root, "agent/skills/demo/scripts/NOTES", "not code\n")
        write(self.root, "agent/skills/demo/scripts/test_run.py")
        write(self.root, "agent/skills/demo/tests/helpers.py")
        write(self.root, "agent/skills/demo/scripts/cases.json", "{}")
        write(self.root, "agent/operations/sync/sync.sh")
        write(self.root, "agent/operations/sync/test.sh")
        write(self.root, "autopilot/proof/tools/check.py")
        write(self.root, ".github/workflows/ci.yml", """
            name: CI
            on: push
            jobs:
              lint:
                runs-on: ubuntu-latest
                steps:
                  - run: echo hi
              test:
                runs-on: ubuntu-latest
            """)
        self.expected = [
            "agent/skills/demo",
            "agent/skills/group/nested",
            "agent/skills/demo/scripts/run.py",
            "agent/skills/demo/scripts/build.mjs",
            "agent/skills/demo/scripts/watch",
            "agent/operations/sync/sync.sh",
            "autopilot/proof/tools/check.py",
            ".github/workflows/ci.yml#lint",
            ".github/workflows/ci.yml#test",
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def inventory(self, items, frontmatter=FRONTMATTER, rel="autopilot/proof/records/inventory/demo.md"):
        return write(self.root, rel, frontmatter + "\n# Demo\n\n" + HEADER + rows(items))

    def run_tool(self, path, *args, env=None):
        return subprocess.run([sys.executable, "-I", str(TOOL), str(path), *args],
                              capture_output=True, text=True, env=env)

    def gh_stub(self, mode="ok"):
        stub = write(self.root, "bin/gh", GH_STUB.format(python=sys.executable, tree=TREE, workflow=WORKFLOW),
                     executable=True)
        return {"INVENTORY_GH": str(stub), "GH_STUB_MODE": mode, "PATH": "/usr/bin:/bin"}

    def test_finds_skills_scripts_and_jobs_but_not_tests_data_or_plain_files(self):
        self.assertEqual(sorted(inventory.brain_items(self.root)), sorted(self.expected))

    def test_scripts_in_any_operation_folder_are_items(self):
        # Listing scripts only in named folders would hide a new operation's scripts.
        write(self.root, "agent/operations/new-review/reader.py")
        write(self.root, "autopilot/review/tools/notify.py")
        write(self.root, "autopilot/review/tools/jobs/nightly.sh")
        items = inventory.brain_items(self.root)
        for rel in ("agent/operations/new-review/reader.py", "autopilot/review/tools/notify.py",
                    "autopilot/review/tools/jobs/nightly.sh"):
            self.assertIn(rel, items)
        result = self.run_tool(self.inventory(self.expected), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: agent/operations/new-review/reader.py", result.stdout)

    def test_tests_named_by_suffix_are_not_items(self):
        for name in ("worker_test.py", "worker.test.ts", "worker.spec.js", "smoke_test.sh"):
            write(self.root, f"agent/skills/demo/scripts/{name}")
        write(self.root, "agent/skills/demo/scripts/latest.py")
        write(self.root, "agent/skills/demo/scripts/attest.sh")
        expected = self.expected + ["agent/skills/demo/scripts/latest.py", "agent/skills/demo/scripts/attest.sh"]
        self.assertEqual(sorted(inventory.brain_items(self.root)), sorted(expected))

    def test_installed_and_generated_code_is_not_an_item(self):
        write(self.root, "agent/skills/demo/node_modules/pkg/index.js")
        write(self.root, "autopilot/proof/tools/.venv/lib/site.py")
        write(self.root, "autopilot/proof/tools/__pycache__/check.cpython-39.pyc")
        self.assertEqual(sorted(inventory.brain_items(self.root)), sorted(self.expected))

    def test_code_outside_the_scanned_folders_is_not_an_item(self):
        write(self.root, "projects/demo/notes/sketch.py")
        write(self.root, "autopilot/proof/records/compute.py")
        self.assertEqual(sorted(inventory.brain_items(self.root)), sorted(self.expected))

    def test_matching_inventory_passes(self):
        result = self.run_tool(self.inventory(self.expected), "--check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("inventory demo: 9 items, 0 missing, 0 gone", result.stdout)

    def test_new_item_is_drift(self):
        result = self.run_tool(self.inventory(self.expected[1:]), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: agent/skills/demo", result.stdout)

    def test_removed_item_is_drift(self):
        result = self.run_tool(self.inventory(self.expected + ["agent/skills/old"]), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("in inventory but gone: agent/skills/old", result.stdout)

    def test_a_row_inside_fenced_code_is_no_row(self):
        path = self.inventory(self.expected[1:])
        path.write_text(path.read_text() + "\n```markdown\n" + HEADER + rows(["agent/skills/demo"]) + "```\n")
        result = self.run_tool(path, "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: agent/skills/demo", result.stdout)

    def test_a_fence_inside_a_longer_fence_stays_code(self):
        # Toggling on every fence line would end the example at "```text" and read its row.
        path = self.inventory(self.expected[1:])
        example = "````markdown\n```text\n" + rows(["agent/skills/demo"]) + "```\n````\n"
        path.write_text(path.read_text() + "\n" + example)
        result = self.run_tool(path, "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: agent/skills/demo", result.stdout)
        path.write_text(path.read_text() + rows(["agent/skills/demo"]))
        result = self.run_tool(path, "--check")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rows_with_a_scheme_are_kept_by_hand(self):
        kept = self.expected + ["cron:a1", "launchd:local.brain.sync", "file:~/x.py", "agent-runtime:abc123"]
        result = self.run_tool(self.inventory(kept), "--check")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_path_row_is_not_kept_by_hand(self):
        result = self.run_tool(self.inventory(self.expected + ["agent/skills/old:v1"]), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("in inventory but gone: agent/skills/old:v1", result.stdout)

    def test_exclude_in_every_written_shape(self):
        write(self.root, "autopilot/other/tools/scan.py")
        write(self.root, "autopilot/otherwise/tools/keep.py")
        expected = self.expected + ["autopilot/otherwise/tools/keep.py"]
        shapes = (
            "---\nsource: brain\nexclude:\n  - autopilot/other/\n---\n",
            "---\nsource: brain\nexclude:\n- autopilot/other\n---\n",
            "---\nsource: brain\nexclude:\n  - ./autopilot/other/  # out of scope\n---\n",
            "---\nsource: brain\nexclude: [autopilot/other/]\n---\n",
            "---\nsource: brain\nexclude: ['./autopilot/other', agent/nothing/]\n---\n",
            "---\nsource: brain  # this brain\nexclude: \"autopilot/other\"\n---\n",
            "\ufeff---\nsource: brain\nexclude: autopilot/other\n---\n",
        )
        for frontmatter in shapes:
            result = self.run_tool(self.inventory(expected, frontmatter), "--check")
            self.assertEqual(result.returncode, 0, repr(frontmatter) + result.stdout)
        result = self.run_tool(self.inventory(expected, FRONTMATTER), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: autopilot/other/tools/scan.py", result.stdout)

    def test_excluding_a_workflow_file_excludes_its_jobs(self):
        write(self.root, ".github/workflows/other.yml", "jobs:\n  build:\n    runs-on: x\n")
        frontmatter = "---\nsource: brain\nexclude:\n  - .github/workflows/other.yml\n---\n"
        result = self.run_tool(self.inventory(self.expected, frontmatter), "--check")
        self.assertEqual(result.returncode, 0, result.stdout)
        result = self.run_tool(self.inventory(self.expected), "--check")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: .github/workflows/other.yml#build", result.stdout)
        one_job = "---\nsource: brain\nexclude:\n  - .github/workflows/ci.yml#lint\n---\n"
        result = self.run_tool(self.inventory([], one_job))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn(".github/workflows/ci.yml#lint", result.stdout.split())
        self.assertIn(".github/workflows/ci.yml#test", result.stdout.split())

    def test_listing_respects_exclude(self):
        result = self.run_tool(self.inventory([], "---\nsource: brain\nexclude:\n  - agent/skills/\n---\n"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(sorted(result.stdout.split()),
                         sorted(i for i in self.expected if not i.startswith("agent/skills/")))

    def test_without_a_source_it_is_unavailable_and_names_the_fix(self):
        for frontmatter in ("", "---\nexclude: x/\n---\n", "---\nsource: brain\n", "---\nsource: gitlab:a/b\n---\n"):
            result = self.run_tool(self.inventory(self.expected, frontmatter), "--check")
            self.assertEqual(result.returncode, 2, repr(frontmatter) + result.stdout)
            self.assertIn("needs `source: brain` or `source: github:<owner>/<repo>`", result.stdout)

    def test_missing_or_unreadable_inventory_is_unavailable(self):
        result = self.run_tool(self.root / "nowhere.md", "--check")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("inventory nowhere: unavailable", result.stdout)
        path = self.inventory(self.expected)
        path.write_bytes(path.read_bytes() + b"\xff\xfe broken\n")
        result = self.run_tool(path, "--check")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("inventory demo: unavailable", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_brain_is_the_nearest_one_above_the_file(self):
        nested = write(self.root, "projects/demo/BRAIN.md", "# Another brain\n")
        write(nested.parent, "agent/skills/only-here/SKILL.md", "---\nname: only-here\n---\n")
        path = self.inventory(["agent/skills/only-here"], rel="projects/demo/records/demo.md")
        result = self.run_tool(path, "--check")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_no_brain_above_the_file_is_unavailable_unless_root_is_given(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            path = write(Path(elsewhere), "demo.md", FRONTMATTER + HEADER + rows(self.expected))
            result = self.run_tool(path, "--check")
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("no BRAIN.md above the file", result.stdout)
            result = self.run_tool(path, "--check", "--root", str(self.root))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_root_without_a_brain_is_unavailable(self):
        # Hand-kept rows only would otherwise pass against an empty listing.
        path = self.inventory(["cron:nightly"])
        for root in (self.root / "nowhere", self.root / "agent"):
            for args in (("--check",), ()):
                result = self.run_tool(path, *args, "--root", str(root))
                self.assertEqual(result.returncode, 2, f"{root} {args} {result.stdout}")
                self.assertIn(f"no BRAIN.md in {root}", result.stdout)

    def test_an_unreadable_brain_file_is_unavailable(self):
        (self.root / ".github/workflows/bad.yml").write_bytes(b"jobs:\n  \xff:\n")
        for args in (("--check",), ()):
            result = self.run_tool(self.inventory(self.expected), *args)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("inventory demo: unavailable (cannot read the brain", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_repository_items_through_gh(self):
        path = self.inventory(REPO_ITEMS, "---\nsource: github:owner/repo\n---\n")
        result = self.run_tool(path, env=self.gh_stub())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.split(), REPO_ITEMS)
        result = self.run_tool(path, "--check", env=self.gh_stub())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.inventory(REPO_ITEMS[1:], "---\nsource: github:owner/repo\n---\n")
        result = self.run_tool(path, "--check", env=self.gh_stub())
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("not in inventory: .agents/skills/plan", result.stdout)

    def test_repository_that_cannot_be_read_whole_is_unavailable(self):
        path = self.inventory(REPO_ITEMS, "---\nsource: github:owner/repo\n---\n")
        expected = {"truncated": "the tree of owner/repo is truncated",
                    "fail": "gh api repos/owner/repo/git/trees/HEAD?recursive=1 failed: HTTP 404: Not Found",
                    "garbage": "unexpected answer from gh api for owner/repo"}
        for mode, message in expected.items():
            result = self.run_tool(path, "--check", env=self.gh_stub(mode))
            self.assertEqual(result.returncode, 2, mode + result.stdout + result.stderr)
            self.assertIn(message, result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_gh_is_unavailable_not_a_crash(self):
        path = self.inventory([], "---\nsource: github:owner/repo\n---\n")
        result = self.run_tool(path, "--check", env={"INVENTORY_GH": "/nonexistent/gh", "PATH": "/usr/bin:/bin"})
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("inventory demo: unavailable (gh not found)", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_jobs_end_at_the_next_top_level_key(self):
        text = "jobs:\n  a:\n    x: 1\nenv:\n  b:\n"
        self.assertEqual(inventory.workflow_jobs("w.yml", text), ["w.yml#a"])

    def test_workflow_jobs_in_other_valid_shapes(self):
        cases = {
            "jobs: # c\n  build:\n    runs-on: x\n": ["w#build"],
            'jobs:\n  "build":\n    runs-on: x\n': ["w#build"],
            "jobs:\n  build: # c\n    runs-on: x\n": ["w#build"],
            "jobs:\n    build:\n        runs-on: x\n    test:\n        runs-on: x\n": ["w#build", "w#test"],
            "jobs:\n  a:\n    x: 1\n# a comment at column 0\n  b:\n    x: 1\n": ["w#a", "w#b"],
        }
        for text, expected in cases.items():
            self.assertEqual(inventory.workflow_jobs("w", text), expected, text)


if __name__ == "__main__":
    unittest.main()
