#!/bin/sh
# Exercise sync.sh against throwaway repositories: two live clones of one remote, plus a development clone.
# Usage: test.sh   (needs git; touches nothing outside a temporary directory)
set -u

sync_src=$(cd "$(dirname "$0")" && pwd -P)/sync.sh
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
failed=0
check() {
	if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; failed=1; fi
}

# Record alerts instead of showing notifications.
mkdir "$tmp/bin"
printf '#!/bin/sh\nfor a; do last=$a; done\necho "$last" >>"%s/alerts"\n' "$tmp" >"$tmp/bin/osascript"
chmod +x "$tmp/bin/osascript"
PATH="$tmp/bin:$PATH"
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.invalid GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.invalid
alerts() { cat "$tmp/alerts" 2>/dev/null | wc -l | tr -d ' '; }

git init -q --bare -b main "$tmp/remote.git"
git init -q --bare -b main "$tmp/framework.git"
git clone -q "$tmp/remote.git" "$tmp/a" 2>/dev/null
mkdir -p "$tmp/a/agent/operations/sync"
cp "$sync_src" "$tmp/a/agent/operations/sync/sync.sh"
printf 'line\n' >"$tmp/a/note.md"
git -C "$tmp/a" add -A && git -C "$tmp/a" commit -q -m init && git -C "$tmp/a" push -q origin main
git clone -q "$tmp/remote.git" "$tmp/b"
git clone -q "$tmp/remote.git" "$tmp/dev"
git -C "$tmp/a" remote add upstream "$tmp/framework.git"
git -C "$tmp/b" remote add upstream "$tmp/framework.git"
run() { sh "$tmp/$1/agent/operations/sync/sync.sh" >>"$tmp/log" 2>&1; }
head_of() { git -C "$tmp/$1" rev-parse "${2:-HEAD}"; }
remote_head() { git -C "$tmp/remote.git" rev-parse main; }

before=$(head_of a)
run a
check "idle run changes nothing" '[ "$(head_of a)" = "$before" ]'

printf 'from a\n' >"$tmp/a/a.md"
run a
check "local change is committed and pushed" '[ "$(remote_head)" = "$(head_of a)" ] && [ "$(head_of a)" != "$before" ]'

run b
check "other clone pulls it" '[ -f "$tmp/b/a.md" ] && [ "$(head_of b)" = "$(remote_head)" ]'

printf 'x\n' >"$tmp/a/x.md"
printf 'y\n' >"$tmp/b/y.md"
run a && run b && run a
check "different files on both sides merge and converge" '[ -f "$tmp/a/y.md" ] && [ -f "$tmp/b/x.md" ] && [ "$(head_of a)" = "$(head_of b)" ] && [ "$(head_of a)" = "$(remote_head)" ]'

printf 'a version\n' >"$tmp/a/note.md"
printf 'b version\n' >"$tmp/b/note.md"
run a
pushed=$(remote_head)
run b
status=$?
check "conflict exits nonzero" '[ $status -ne 0 ]'
check "conflict leaves no merge in progress" '[ ! -e "$tmp/b/.git/MERGE_HEAD" ] && [ "$(cat "$tmp/b/note.md")" = "b version" ]'
check "conflict pushes nothing" '[ "$(remote_head)" = "$pushed" ]'
check "conflict alerts once" '[ "$(alerts)" = 1 ]'
run b
check "repeated conflict does not alert again" '[ "$(alerts)" = 1 ]'

before=$(head_of a)
token="ghp_$(printf '%036d' 0 | tr 0 a)"
printf 'key: %s\n' "$token" >"$tmp/a/leak.md"
run a
check "possible credential blocks the commit" '[ "$(head_of a)" = "$before" ] && [ -f "$tmp/a/leak.md" ] && [ -z "$(git -C "$tmp/a" diff --cached --name-only)" ]'
check "possible credential alerts with the file name" 'tail -1 "$tmp/alerts" | grep -q leak.md'
rm "$tmp/a/leak.md"

printf 'busy\n' >"$tmp/a/busy.md"
touch "$tmp/a/.git/index.lock"
run a
check "busy git skips the run" '[ "$(head_of a)" = "$before" ]'
rm "$tmp/a/.git/index.lock" "$tmp/a/busy.md"

printf 'dev\n' >"$tmp/dev/dev.md"
dev_before=$(head_of dev)
run dev
status=$?
check "development checkout without upstream is refused" '[ $status -eq 2 ] && [ "$(head_of dev)" = "$dev_before" ]'

if [ "$failed" -ne 0 ]; then
	echo "--- sync log"
	cat "$tmp/log"
	exit 1
fi
echo "all checks passed"
