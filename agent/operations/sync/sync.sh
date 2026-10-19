#!/bin/sh
# Commit, merge, and push a live brain checkout. See ../sync.md.
set -u

root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel) || exit 1
cd "$root" || exit 1

log() { printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"; }
alert() {
	log "ATTENTION: $*"
	if command -v osascript >/dev/null 2>&1; then
		osascript -e 'on run argv' -e 'display notification (item 1 of argv) with title "O2B sync"' -e 'end run' "$*" >/dev/null 2>&1
	fi
	return 0
}

# Only a live brain has an upstream remote. A development checkout must never auto-publish the framework.
if ! git remote get-url upstream >/dev/null 2>&1; then
	log "refusing: $root has no upstream remote, so it is not a live brain"
	exit 2
fi

branch=$(git symbolic-ref --quiet --short HEAD) || { log "skip: detached HEAD"; exit 0; }
git_dir=$(git rev-parse --absolute-git-dir) || exit 1
host=$(hostname -s)
notice="agent/work/sync-conflict-$host.md"
for f in index.lock MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
	if [ -e "$git_dir/$f" ]; then
		log "skip: git busy ($f)"
		exit 0
	fi
done

# Common credential formats only; this is a tripwire, not a secret scanner.
secrets='(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'

if [ -n "$(git status --porcelain)" ]; then
	git add -A || exit 1
	hits=$(git diff --cached -U0 --no-color --no-ext-diff |
		awk '/^\+\+\+ /{f=substr($0,7); next} /^\+/{print f "\t" $0}' |
		grep -E "$secrets" | cut -f1 | sort -u | tr '\n' ' ')
	if [ -n "$hits" ]; then
		git reset -q
		alert "Possible credential in: $hits- nothing committed until it is removed"
		exit 1
	fi
	git commit -q -m "sync: $host" || exit 1
	log "committed $(git rev-parse --short HEAD)"
fi

# The text depends only on the host, the checkout and the conflicting files, so every run that
# meets the same conflict writes the same blob.
notice_text() {
	for_you=$(printf 'Brain sync on %s stopped at a merge conflict - merge origin/%s by hand in %s there' \
		"$host" "$branch" "$root" | sed "s/'/''/g")
	files=$(printf '%s\n' "$1" | sed 's/.*/- `&`/')
	cat <<EOF
---
for_you: '$for_you'
---
# Sync conflict on $host

**Governing parent:** [Auto-sync](../operations/sync.md).

Auto-sync on \`$host\` cannot merge \`origin/$branch\` into \`$root\`, so edits made there reach no other machine. Merge it by hand on that machine:

    cd '$root' && git merge origin/$branch

These files conflicted:

$files

The first sync there that merges cleanly removes this file.
EOF
}

# A machine that cannot merge cannot push its own commits, but it can still add one file on top of
# origin: a notice whose for_you puts the conflict on the owner's snapshot on every machine. It is
# committed locally too, with the same content, so the eventual merge takes it without a conflict.
publish_notice() {
	blob=$(notice_text "$1" | git hash-object -w --stdin) || return 1
	if [ "$(git rev-parse -q --verify "HEAD:$notice")" != "$blob" ]; then
		mkdir -p "$(dirname "$notice")" && git cat-file blob "$blob" >"$notice" &&
			git add -- "$notice" && git commit -q -m "sync: $host" -- "$notice" || return 1
	fi
	[ "$(git rev-parse -q --verify "$remote:$notice")" = "$blob" ] && return 0
	index="$git_dir/o2b-sync-notice-index"
	rm -f "$index" "$index.lock"
	tree=$(GIT_INDEX_FILE=$index git read-tree "$remote" &&
		GIT_INDEX_FILE=$index git update-index --add --cacheinfo "100644,$blob,$notice" &&
		GIT_INDEX_FILE=$index git write-tree)
	built=$?
	rm -f "$index" "$index.lock"
	[ $built -eq 0 ] || return 1
	commit=$(git commit-tree -p "$remote" -m "sync: $host cannot merge" "$tree") || return 1
	# Never forced: if origin moved since the fetch, the push fails and the next run retries.
	git push -q origin "$commit:refs/heads/$branch" || return 1
	remote=$commit
	log "published $notice"
}

git fetch -q origin "$branch" || { log "fetch failed; retrying next run"; exit 1; }
remote=$(git rev-parse FETCH_HEAD)

if ! git merge-base --is-ancestor "$remote" HEAD; then
	if ! git merge -q --no-edit "$remote"; then
		if [ -e "$git_dir/MERGE_HEAD" ]; then
			conflicts=$(git -c core.quotePath=false diff --name-only --diff-filter=U)
			git merge --abort
			publish_notice "$conflicts" || log "conflict notice not published; retrying next run"
			# Alert once per remote revision rather than on every run.
			if [ "$(cat "$git_dir/o2b-sync-conflict" 2>/dev/null)" != "$remote" ]; then
				echo "$remote" >"$git_dir/o2b-sync-conflict"
				alert "Merge conflict with origin/$branch in $root - merge it by hand"
			fi
		else
			log "merge deferred: files changed during sync"
		fi
		exit 1
	fi
	rm -f "$git_dir/o2b-sync-conflict"
	log "merged $(git rev-parse --short "$remote")"
fi

# Merged, so this machine's conflict notice no longer holds.
if git cat-file -e "HEAD:$notice" 2>/dev/null; then
	git rm -q -f -- "$notice" && git commit -q -m "sync: $host" -- "$notice" && log "removed $notice"
	rm -f "$git_dir/o2b-sync-conflict"
fi

if [ -n "$(git rev-list -1 "$remote..HEAD")" ]; then
	git push -q origin "HEAD:$branch" || { log "push failed; retrying next run"; exit 1; }
	log "pushed $(git rev-parse --short HEAD)"
fi

# Keep this machine's agent runtimes in step with the brain's skills and agent definitions. See ../skill-discovery.md.
runtime_sync="$root/agent/operations/runtime-sync/runtime_sync.py"
if [ -f "$runtime_sync" ]; then
	if command -v python3 >/dev/null 2>&1; then
		rm -f "$git_dir/o2b-runtime-sync-no-python"
		python3 "$runtime_sync" --brain "$root" --state "$git_dir/o2b-runtime-sync" ||
			alert "Agent runtimes on $host need attention - see the sync log"
	elif [ ! -e "$git_dir/o2b-runtime-sync-no-python" ]; then
		touch "$git_dir/o2b-runtime-sync-no-python"
		alert "Runtime sync needs python3, which this sync cannot find; agent runtimes are not being updated"
	fi
fi
