#!/usr/bin/env python3
"""Check an o2b brain's content: links and anchors, skill frontmatter, stage
indexes, and secret formats. Prints each problem and exits 1 if any are found.

Usage: check_brain.py [--root <brain>]   (default: the brain this script is in)

Not checked yet: reference-style links, Obsidian wikilinks and links in raw HTML
(href=).
"""
import argparse
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

SKIP_DIRS = {".git", ".claude", ".obsidian", ".trash", "node_modules"}  # at any depth
SKIP_TOP = {"worktrees"}  # only directly under the brain root
# [text](target) and ![alt](target); a target may hold one level of parentheses and a title
LINK = re.compile(r"\[[^\]]*\]\((?:<([^>]+)>|((?:[^()\s]|\([^()\s]*\))+))(?:\s+(?:\"[^\"]*\"|'[^']*'))?\)")
SETEXT = re.compile(r"^(=+|-+)\s*$")
HTML_COMMENT = re.compile(r"<!--.*?-->")
HTML_TAG = re.compile(r"<[^>]+>")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
EXPLICIT_ANCHOR = re.compile(r"<a\s+(?:id|name)=\"([^\"]+)\"")
# Auto-sync's tripwire formats (agent/operations/sync/sync.sh), except that `sk-` must not
# continue a word or path: the tripwire also matches a long run after `sk-` inside a URL path,
# which check_secrets reports separately as a tripwire match.
SECRET = re.compile(
    r"((?<![A-Za-z0-9/_-])sk-[A-Za-z0-9_-]*[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


def markdown_files(root):
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if not SKIP_DIRS.intersection(parts) and parts[0] not in SKIP_TOP:
            yield path


def prose_lines(text, keep_code=False):
    """Yield (line number, line) outside fenced code and HTML comments; inline code is
    removed unless kept. A fence closes only on a bare run of its own character at least
    as long as the one that opened it, so an example fence inside a longer one stays code."""
    fence, in_comment = None, False
    for number, line in enumerate(text.splitlines(), 1):
        match = None if in_comment else FENCE.match(line)
        if match and fence is None:
            fence = match.group(1)
            continue
        if fence:
            marker = match.group(1) if match else ""
            if marker[:1] == fence[0] and len(marker) >= len(fence) and not match.group(2).strip():
                fence = None
            continue
        if in_comment:
            if "-->" not in line:
                continue
            line, in_comment = line.split("-->", 1)[1], False
        line = HTML_COMMENT.sub("", line)
        if "<!--" in INLINE_CODE.sub("", line):  # a `<!--` inside inline code opens nothing
            line, in_comment = line[:line.index("<!--")], True
        yield number, line if keep_code else INLINE_CODE.sub("", line)


def slug(heading):
    """GitHub's heading anchor: lowercase, drop punctuation (keeping _ and -), spaces to hyphens."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", HTML_TAG.sub("", heading).strip().lower())
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


@lru_cache(maxsize=None)
def anchors(path):
    """Heading anchors as GitHub renders them: ATX and setext headings, headings in quotes,
    and explicit <a id>."""
    found, seen, previous = set(), {}, ""

    def add(heading):
        base = slug(heading)
        n = seen.get(base, 0)
        found.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1

    text = path.read_text(encoding="utf-8", errors="replace")
    skip_until = 0
    if text.startswith("---\n"):  # frontmatter is not prose
        end = text.find("\n---", 4)
        skip_until = text[:end].count("\n") + 2 if end != -1 else 0
    for number, line in prose_lines(text, keep_code=True):
        if number <= skip_until:
            continue
        found.update(a.lower() for a in EXPLICIT_ANCHOR.findall(line))
        bare = re.sub(r"^\s*(>\s?)+", "", line)
        match = HEADING.match(bare)
        if match:
            add(match.group(2))
        elif SETEXT.match(bare) and previous.strip() and not re.match(r"^\s*([#>|*+-]|\d+[.)])", previous):
            add(previous)
        previous = "" if match else bare
    return frozenset(found)


def resolve_target(base, relative):
    """Resolve a link target the way the case-sensitive CI runner does: every path
    component must match a real directory entry's exact spelling, so a wrong-case
    link is reported here as ubuntu reports it. Returns None when it does not exist.
    """
    current = base
    for part in Path(relative).parts:
        if part in (".", ""):
            continue
        if part == "..":
            current = current.parent
            continue
        try:
            names = {entry.name for entry in os.scandir(current)}
        except OSError:
            return None
        if part not in names:
            return None
        current = current / part
    return current


def check_links(root, problems):
    for path in markdown_files(root):
        rel = path.relative_to(root)
        for number, line in prose_lines(path.read_text(encoding="utf-8", errors="replace")):
            for angled, plain in LINK.findall(line):
                target = angled or plain
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, mailto:, app links
                    continue
                file_part, _, anchor = target.partition("#")
                if not file_part:
                    dest = path
                else:
                    dest = resolve_target(path.parent, unquote(file_part))
                    if dest is None:
                        problems.append(f"{rel}:{number}: broken link -> {target}")
                        continue
                if anchor and dest.suffix == ".md" and dest.is_file():
                    if unquote(anchor).lower() not in anchors(dest):
                        problems.append(f"{rel}:{number}: missing anchor -> {target}")


def frontmatter(path):
    """Top-level frontmatter fields; a block scalar (`key: |` or `key: >`) takes its indented lines."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields, block = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if block and (line.startswith((" ", "\t")) or not line.strip()):
            fields[block] = (fields[block] + " " + line.strip()).strip()
            continue
        block = None
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            if re.fullmatch(r"[|>][-+]?", value):
                fields[key], block = "", key
            else:
                fields[key] = value.strip("\"'")
    return None


def check_skills(root, problems):
    for skill in sorted((root / "agent" / "skills").rglob("SKILL.md")):
        rel = skill.relative_to(root)
        fields = frontmatter(skill)
        if fields is None:
            problems.append(f"{rel}: no frontmatter")
            continue
        if fields.get("name") != skill.parent.name:
            problems.append(f"{rel}: name {fields.get('name')!r} does not match folder {skill.parent.name!r}")
        description = fields.get("description", "")
        if not description:
            problems.append(f"{rel}: no description")
        elif len(description) > 1024:
            problems.append(f"{rel}: description longer than 1024 characters")


def check_stage_indexes(root, problems):
    for index in sorted([root / "guidance" / "STAGES.md", *root.glob("projects/*/guidance/STAGES.md")]):
        if not index.exists():
            continue
        rel = index.relative_to(root)
        text = index.read_text(encoding="utf-8", errors="replace")
        links = [link for _, line in prose_lines(text) for link in LINK.findall(line)]  # not commented out or fenced
        listed = {(index.parent / (a or t).partition("#")[0]).resolve() for a, t in links}
        pages = index.parent / "stages"
        for page in sorted(pages.glob("*.md")) if pages.is_dir() else []:
            if page.resolve() not in listed:
                problems.append(f"{rel}: stage page not in index -> {page.relative_to(root)}")


def sync_tripwire(root):
    """Auto-sync's credential pattern, read from its own script so the two never drift."""
    sync = root / "agent" / "operations" / "sync" / "sync.sh"
    match = re.search(r"^secrets='([^']+)'", sync.read_text(), re.M) if sync.exists() else None
    return re.compile(match.group(1)) if match else None


def check_secrets(root, problems):
    try:
        listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        problems.append("secrets: could not list files (not checked)")
        return
    tripwire = sync_tripwire(root)
    if tripwire is None:
        problems.append("secrets: auto-sync's pattern not found in agent/operations/sync/sync.sh (tripwire not checked)")
    for name in sorted(set(filter(None, listed.decode().split("\0")))):
        path = root / name
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if SECRET.search(line):
                problems.append(f"{name}:{number}: secret-format match (value not printed)")
            elif tripwire and tripwire.search(line):
                problems.append(f"{name}:{number}: matches auto-sync's credential tripwire; sync stops on this machine until it changes")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    root = parser.parse_args().root.resolve()
    problems = []
    for check in (check_links, check_skills, check_stage_indexes, check_secrets):
        check(root, problems)
    for problem in problems:
        print(problem)
    print(f"check_brain: {len(problems)} problem(s) in {root}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
