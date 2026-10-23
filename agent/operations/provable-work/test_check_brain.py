#!/usr/bin/env python3
"""Tests for check_brain.py: a clean brain passes, and each planted defect fails.

Usage: python3 -I test_check_brain.py
"""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_brain.py"
REAL_SYNC = Path(__file__).resolve().parents[3] / "agent" / "operations" / "sync" / "sync.sh"
SECRET_SHAPED = "gh" + "p_" + "A" * 36  # assembled so this file holds no match itself


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


class CheckBrainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "BRAIN.md", """
            # Brain
            See [guide](guidance/README.md#apply-the-for_you-test), [quoted](guidance/README.md#quoted-heading),
            [explicit](guidance/README.md#kept-anchor), [skill](agent/skills/demo/SKILL.md) and [web](https://example.com).
            A link in code is ignored: `[x](missing.md)`.
            """)
        write(self.root, "guidance/README.md", """
            # Guide
            ## Apply the `for_you` test
            > ## Quoted heading
            <a id="kept-anchor"></a>
            ```
            ## Heading in code
            ```
            """)
        write(self.root, "guidance/STAGES.md", "| [a moment](stages/a-moment.md) | All |\n")
        write(self.root, "guidance/stages/a-moment.md", "# A moment\n")
        write(self.root, "agent/skills/demo/SKILL.md", """
            ---
            name: demo
            description: A demo skill.
            ---
            # Demo
            """)
        pattern = next(l for l in REAL_SYNC.read_text().splitlines() if l.startswith("secrets='"))
        write(self.root, "agent/operations/sync/sync.sh", pattern + "\n")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root)],
                                capture_output=True, text=True)
        return result.returncode, result.stdout

    def assert_fails_with(self, expected):
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn(expected, out)

    def test_clean_brain_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("0 problem(s)", out)

    def test_broken_link(self):
        write(self.root, "notes.md", "[gone](nowhere.md)\n")
        self.assert_fails_with("notes.md:1: broken link -> nowhere.md")

    def test_wrong_case_link_is_broken(self):
        # The CI runner (ubuntu) is case-sensitive: a wrong-case path is broken there.
        # macOS is not, so the target must be resolved component by component, not by exists().
        write(self.root, "notes.md", "[right](guidance/README.md)\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)  # the correctly-cased link keeps its verdict
        write(self.root, "notes.md", "[wrong](Guidance/README.md)\n")
        self.assert_fails_with("notes.md:1: broken link -> Guidance/README.md")
        write(self.root, "notes.md", "[gone](guidance/nope.md)\n")
        self.assert_fails_with("notes.md:1: broken link -> guidance/nope.md")

    def test_missing_anchor(self):
        write(self.root, "notes.md", "[stale](guidance/README.md#old-heading)\n")
        self.assert_fails_with("missing anchor -> guidance/README.md#old-heading")

    def test_heading_inside_code_is_not_an_anchor(self):
        write(self.root, "notes.md", "[code](guidance/README.md#heading-in-code)\n")
        self.assert_fails_with("missing anchor -> guidance/README.md#heading-in-code")

    def test_skill_name_must_match_folder(self):
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: other\ndescription: x\n---\n")
        self.assert_fails_with("name 'other' does not match folder 'demo'")

    def test_skill_needs_description(self):
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: demo\n---\n")
        self.assert_fails_with("agent/skills/demo/SKILL.md: no description")

    def test_unclosed_frontmatter_is_no_frontmatter(self):
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: demo\ndescription: x\n# Demo\n")
        self.assert_fails_with("agent/skills/demo/SKILL.md: no frontmatter")

    def test_stage_page_missing_from_index(self):
        write(self.root, "guidance/stages/orphan.md", "# Orphan\n")
        self.assert_fails_with("stage page not in index -> guidance/stages/orphan.md")

    def test_stage_page_listed_only_in_a_comment_or_fence_is_missing(self):
        write(self.root, "guidance/stages/hidden.md", "# Hidden\n")
        write(self.root, "guidance/stages/fenced.md", "# Fenced\n")
        write(self.root, "guidance/STAGES.md", """
            | [a moment](stages/a-moment.md) | All |
            <!-- | [hidden](stages/hidden.md) | All | -->
            ```
            | [fenced](stages/fenced.md) | All |
            ```
            """)
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("stage page not in index -> guidance/stages/hidden.md", out)
        self.assertIn("stage page not in index -> guidance/stages/fenced.md", out)
        self.assertNotIn("guidance/stages/a-moment.md", out)

    def test_a_fence_inside_a_longer_fence_stays_code(self):
        write(self.root, "notes.md", """
            ````markdown
            ```sh
            [inner](gone-inner.md)
            ```
            ## Heading in an example
            ````
            [after](gone-after.md) [anchor](#heading-in-an-example)
            """)
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertNotIn("gone-inner.md", out)
        self.assertIn("notes.md:7: broken link -> gone-after.md", out)
        self.assertIn("notes.md:7: missing anchor -> #heading-in-an-example", out)

    def test_a_fence_closes_only_on_its_own_character_and_length(self):
        write(self.root, "notes.md", "```\n~~~\n[a](gone-a.md)\n```sh\n[b](gone-b.md)\n````\n[c](gone-c.md)\n")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertNotIn("gone-a.md", out)
        self.assertNotIn("gone-b.md", out)
        self.assertIn("notes.md:7: broken link -> gone-c.md", out)

    def test_secret_format_in_tracked_file(self):
        write(self.root, "notes.md", f"token {SECRET_SHAPED}\n")
        subprocess.run(["git", "-C", str(self.root), "add", "notes.md"], check=True)
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("notes.md:1: secret-format match (value not printed)", out)
        self.assertNotIn(SECRET_SHAPED, out)

    def test_parentheses_in_a_path_and_single_quoted_titles(self):
        write(self.root, "notes/foo_(bar).md", "# Foo\n")
        write(self.root, "notes/index.md", "[p](foo_(bar).md) and [t](../BRAIN.md 'Title')\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        write(self.root, "notes/index.md", "[p](gone_(bar).md)\n")
        self.assert_fails_with("broken link -> gone_(bar).md")

    def test_broken_image(self):
        write(self.root, "notes.md", "![chart](missing.png)\n")
        self.assert_fails_with("notes.md:1: broken link -> missing.png")

    def test_links_in_html_comments_are_ignored(self):
        write(self.root, "notes.md", "<!-- [x](gone.md) -->\n<!--\n[y](gone.md)\n-->\nText\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_a_closed_comment_does_not_hide_the_rest_of_the_file(self):
        write(self.root, "notes.md", "<!-- note --> text\n\n[later](gone.md)\n")
        self.assert_fails_with("notes.md:3: broken link -> gone.md")

    def test_inline_html_in_a_heading(self):
        write(self.root, "notes.md", "## Setup <span>now</span>\n[s](#setup-now)\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_hyphenated_slug_trips_neither_check(self):
        slug = "s" + "k-hynix-reports-record-profit-on-ai-memory"  # assembled: an older tripwire flagged it
        write(self.root, "notes.md", f"See example.com/2026/10/15/{slug}.html\n\n{slug} in prose\n")  # untracked: still scanned
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_long_run_in_a_url_path_trips_auto_sync_but_is_no_secret(self):
        token = "s" + "k-" + "a" * 24  # assembled so this file holds no match itself
        write(self.root, "notes.md", f"See example.com/files/{token}.html\n")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertNotIn("secret-format", out)
        self.assertIn("notes.md:1: matches auto-sync's credential tripwire", out)
        self.assertNotIn(token, out)

    def test_keys_with_and_without_hyphens_are_secrets(self):
        for key in ("s" + "k-" + "Ab1" * 10, "s" + "k-proj-" + "Ab1" * 10):
            write(self.root, "notes.md", f"key {key}\n")
            self.assert_fails_with("notes.md:1: secret-format match")

    def test_missing_sync_pattern_is_reported(self):
        (self.root / "agent/operations/sync/sync.sh").write_text("# no pattern\n")
        self.assert_fails_with("auto-sync's pattern not found")

    def test_heading_ending_in_html(self):
        write(self.root, "notes.md", '## Setup <a id="x"></a>\n[s](#setup) and [x](#x)\n')
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_comment_opener_in_inline_code_hides_nothing(self):
        write(self.root, "notes.md", "Use `<!--` to open a comment.\n\n[later](gone.md)\n")
        self.assert_fails_with("notes.md:3: broken link -> gone.md")

    def test_setext_headings_are_anchors(self):
        write(self.root, "notes.md", "---\ntitle: x\n---\nTitle here\n==========\n\n- item\n---\n[t](#title-here) [i](#item)\n")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("missing anchor -> #item", out)
        self.assertNotIn("#title-here", out)

    def test_angle_bracket_targets(self):
        write(self.root, "notes/my file.md", "# Mine\n")
        write(self.root, "notes/index.md", "[a](<my file.md>)\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        write(self.root, "notes/index.md", "[a](<gone file.md>)\n")
        self.assert_fails_with("broken link -> gone file.md")

    def test_block_scalar_description(self):
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: demo\ndescription: |\n  A demo skill\n  over two lines.\n---\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        write(self.root, "agent/skills/demo/SKILL.md", "---\nname: demo\ndescription: >\n---\n")
        self.assert_fails_with("agent/skills/demo/SKILL.md: no description")

    def test_only_top_level_worktrees_is_skipped(self):
        write(self.root, "worktrees/copy/notes.md", "[gone](nowhere.md)\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        write(self.root, "notes/worktrees/plan.md", "[gone](nowhere.md)\n")
        self.assert_fails_with("notes/worktrees/plan.md:1: broken link -> nowhere.md")


if __name__ == "__main__":
    unittest.main()
