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
	git commit -q -m "sync: $(hostname -s)" || exit 1
	log "committed $(git rev-parse --short HEAD)"
fi

git fetch -q origin "$branch" || { log "fetch failed; retrying next run"; exit 1; }
remote=$(git rev-parse FETCH_HEAD)

if ! git merge-base --is-ancestor "$remote" HEAD; then
	if ! git merge -q --no-edit "$remote"; then
		if [ -e "$git_dir/MERGE_HEAD" ]; then
			git merge --abort
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

if [ -n "$(git rev-list -1 "$remote..HEAD")" ]; then
	git push -q origin "HEAD:$branch" || { log "push failed; retrying next run"; exit 1; }
	log "pushed $(git rev-parse --short HEAD)"
fi
