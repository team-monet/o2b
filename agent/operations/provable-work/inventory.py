#!/usr/bin/env python3
"""List the items a project's evals must cover (skills, scripts, CI jobs), and
compare them with the rows of its inventory file.

Usage:
  inventory.py <inventory.md>            print the items that exist now
  inventory.py <inventory.md> --check    also compare with the inventory; exit 1 on drift

The inventory's frontmatter names what it covers:

  source: brain                  the brain the inventory file is in
  source: github:<owner>/<repo>  a repository, read with `gh`
  exclude:                       optional path prefixes that are out of scope
    - autopilot/other/

Exit 0 when nothing drifted, 1 on drift, 2 when the inventory or its items cannot
be read.
"""
import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# A row whose item opens with a scheme, such as `cron:nightly` or `file:~/x.py`, is
# kept by hand (unattended jobs, files outside the brain), so it is never reported as gone.
HAND_KEPT = re.compile(r"^[a-z][a-z0-9.-]*:")
CODE = re.compile(r"\.(py|sh|bash|zsh|mjs|cjs|js|ts|mts)$")
ROW = re.compile(r"^\|\s*`([^`]+)`")
REPO = re.compile(r"^github:([\w.-]+/[\w.-]+)$")
SKIP = {"__pycache__", "node_modules", ".venv", "venv"}  # installed or generated code is not an item


class Unavailable(Exception):
    pass


def is_test(rel):
    """Tests are not items of their own: `test_x.py`, `test.sh`, `x_test.py`, `x.test.ts`,
    `x.spec.js`, or anything under a `tests/` folder."""
    name = rel.rsplit("/", 1)[-1]
    return bool(re.match(r"^test[_.]", name) or re.search(r"(_test|\.test|\.spec)\.[^.]+$", name)) or "/tests/" in f"/{rel}"


def is_script(path, rel):
    """Code by its extension, or an executable file without one."""
    if is_test(rel):
        return False
    return bool(CODE.search(path.name)) or ("." not in path.name and os.access(path, os.X_OK))


def workflow_jobs(path, text):
    """Job ids under `jobs:` in a GitHub workflow, as `<path>#<job>`. Handles comments, quoted
    keys and any indentation; the first key under `jobs:` sets the job indentation."""
    jobs, inside, indent = [], False, None
    for line in text.splitlines():
        bare = re.sub(r"\s+#.*$", "", line).rstrip()
        if not bare.strip() or bare.lstrip().startswith("#"):
            continue
        if re.match(r"^jobs:$", bare):
            inside, indent = True, None
        elif inside and re.match(r"^\S", bare):
            inside = False
        elif inside:
            match = re.match(r"^(\s+)[\"']?([A-Za-z0-9_-]+)[\"']?:(\s.*)?$", bare)
            if match and (indent is None or len(match.group(1)) == indent):
                indent = len(match.group(1))
                jobs.append(f"{path}#{match.group(2)}")
    return jobs


def brain_items(root):
    """Skills; the scripts under `agent/skills`, `agent/operations` and each autopilot
    operation's `tools/`, in any subfolder; and the brain's CI jobs."""
    items = [str(skill.parent.relative_to(root)) for skill in sorted((root / "agent" / "skills").rglob("SKILL.md"))]
    bases = [root / "agent" / "skills", root / "agent" / "operations", *sorted(root.glob("autopilot/*/tools"))]
    for base in bases:
        for path in sorted(base.rglob("*")):
            rel = str(path.relative_to(root))
            if path.is_file() and not SKIP.intersection(path.relative_to(base).parts) and is_script(path, rel):
                items.append(rel)
    for workflow in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        items += workflow_jobs(str(workflow.relative_to(root)), workflow.read_text())
    return items


def gh_path():
    """`gh` from PATH, else its usual Homebrew places: a non-interactive shell may lack them."""
    override = os.environ.get("INVENTORY_GH")
    if override:
        return override if Path(override).exists() else None
    return shutil.which("gh") or next((p for p in ("/opt/homebrew/bin/gh", "/usr/local/bin/gh") if Path(p).exists()), None)


def gh(*args):
    path = gh_path()
    if path is None:
        raise Unavailable("gh not found")
    result = subprocess.run([path, "api", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise Unavailable(f"gh api {args[0]} failed: {(result.stderr.strip().splitlines() or ['no message'])[0]}")
    return result.stdout


def repo_items(repo):
    """Agent skills, the direct children of top-level `scripts/`, and CI jobs of a
    repository's default branch."""
    try:
        listing = json.loads(gh(f"repos/{repo}/git/trees/HEAD?recursive=1"))
        if listing.get("truncated"):
            raise Unavailable(f"the tree of {repo} is truncated")
        paths = [entry["path"] for entry in listing["tree"] if entry["type"] == "blob"]
        items = [p.rsplit("/", 1)[0] for p in paths if re.match(r"^\.(claude|cursor|agents)/skills/[^/]+/SKILL\.md$", p)]
        items += [p for p in paths if re.match(r"^scripts/[^/]+$", p) and not is_test(p)
                  and (CODE.search(p) or "." not in p.rsplit("/", 1)[-1])]
        for path in paths:
            if re.match(r"^\.github/workflows/[^/]+\.ya?ml$", path):
                content = json.loads(gh(f"repos/{repo}/contents/{path}"))["content"]
                items += workflow_jobs(path, base64.b64decode(content).decode())
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise Unavailable(f"unexpected answer from gh api for {repo}: {error!r}")
    return sorted(items)


def scalar(value):
    """A frontmatter value without its trailing comment, quotes, or leading `./`."""
    value = re.sub(r"\s+#.*$", "", value).strip().strip("\"'")
    return value[2:] if value.startswith("./") else value


def frontmatter(text):
    """Top-level scalars and lists (`- item` lines, or `[a, b]`) of a frontmatter block;
    {} when there is none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields, key = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        item = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if item and key and isinstance(fields[key], list):
            fields[key].append(scalar(item.group(1)))
            continue
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if match:
            key, value = match.group(1), re.sub(r"(^|\s+)#.*$", "", match.group(2)).strip()
            if value.startswith("[") and value.endswith("]"):
                fields[key] = [scalar(v) for v in value[1:-1].split(",") if scalar(v)]
            else:
                fields[key] = scalar(value) if value else []
    return {}


def brain_root(path):
    """The brain an inventory file is in: the nearest folder above it holding BRAIN.md."""
    for folder in path.resolve().parents:
        if (folder / "BRAIN.md").is_file():
            return folder
    return None


def table_lines(text):
    """Lines outside fenced code, where an example table is no inventory row. A fence closes
    only on a bare run of its own character at least as long as the one that opened it."""
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                yield line
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
            fence = None


def excluded(item, prefixes):
    return any(item == p.rstrip("/") or item.startswith(p.rstrip("/") + "/") for p in prefixes)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inventory", type=Path, help="the project's inventory file")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, help="brain root for `source: brain` (default: the brain the file is in)")
    args = parser.parse_args()
    name = args.inventory.stem
    try:
        text = args.inventory.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        print(f"inventory {name}: unavailable (cannot read {args.inventory}: {error.__class__.__name__})")
        return 2
    fields = frontmatter(text)
    source = fields.get("source")
    exclude = fields.get("exclude") or []
    if isinstance(exclude, str):
        exclude = [exclude]
    try:
        if source == "brain":
            root = args.root or brain_root(args.inventory)
            if root is None:
                raise Unavailable("no BRAIN.md above the file; pass --root")
            if not (root / "BRAIN.md").is_file():
                raise Unavailable(f"no BRAIN.md in {root}")
            try:
                items = brain_items(root)
            except (OSError, UnicodeDecodeError) as error:
                raise Unavailable(f"cannot read the brain: {error!r}")
        elif isinstance(source, str) and REPO.match(source):
            items = repo_items(REPO.match(source).group(1))
        else:
            raise Unavailable("its frontmatter needs `source: brain` or `source: github:<owner>/<repo>`")
    except Unavailable as error:
        print(f"inventory {name}: unavailable ({error})")
        return 2
    items = [item for item in items if not excluded(item, exclude)]
    if not args.check:
        print("\n".join(items))
        return 0
    rows = [m.group(1) for m in map(ROW.match, table_lines(text)) if m]
    tracked = [row for row in rows if not HAND_KEPT.match(row)]
    missing, gone = sorted(set(items) - set(tracked)), sorted(set(tracked) - set(items))
    for item in missing:
        print(f"not in inventory: {item}")
    for item in gone:
        print(f"in inventory but gone: {item}")
    print(f"inventory {name}: {len(items)} items, {len(missing)} missing, {len(gone)} gone")
    return 1 if missing or gone else 0


if __name__ == "__main__":
    sys.exit(main())
