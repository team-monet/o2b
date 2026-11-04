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
# Each clone stands for its own machine, so each run sees the clone's name as its host name.
run() {
	mkdir -p "$tmp/host-$1"
	printf '#!/bin/sh\necho %s\n' "$1" >"$tmp/host-$1/hostname"
	chmod +x "$tmp/host-$1/hostname"
	PATH="$tmp/host-$1:$PATH" sh "$tmp/$1/agent/operations/sync/sync.sh" >>"$tmp/log" 2>&1
}
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
touch "$tmp/b/.git/o2b-sync-notice-index.lock"  # left by an interrupted run; must not block the notice
run b
status=$?
notice=agent/work/sync-conflict-b.md
check "conflict exits nonzero" '[ $status -ne 0 ]'
check "conflict leaves no merge in progress" '[ ! -e "$tmp/b/.git/MERGE_HEAD" ] && [ "$(cat "$tmp/b/note.md")" = "b version" ]'
check "conflict pushes only its notice, on top of origin" '[ "$(git -C "$tmp/remote.git" rev-parse main^)" = "$pushed" ] && [ "$(git -C "$tmp/remote.git" diff --name-only "$pushed" main)" = "$notice" ]'
check "conflicting commits stay local" '[ "$(git -C "$tmp/remote.git" rev-list --no-walk --parents main | wc -w | tr -d " ")" = 2 ] && [ "$(git -C "$tmp/remote.git" show main:note.md)" = "a version" ]'
check "notice asks the owner to merge, naming host, place and files" 'git -C "$tmp/remote.git" show "main:$notice" >"$tmp/notice" && grep -q "^for_you: .*sync on b .*merge origin/main by hand in $(git -C "$tmp/b" rev-parse --show-toplevel) there" "$tmp/notice" && grep -q "^- \`note.md\`$" "$tmp/notice"'
check "conflicting clone holds the same notice, committed" '[ "$(git -C "$tmp/b" rev-parse "HEAD:$notice")" = "$(git -C "$tmp/remote.git" rev-parse "main:$notice")" ] && [ -z "$(git -C "$tmp/b" status --porcelain)" ]'
check "conflict alerts once" '[ "$(alerts)" = 1 ]'
published=$(remote_head)
run b
check "repeated conflict neither alerts nor publishes again" '[ "$(alerts)" = 1 ] && [ "$(remote_head)" = "$published" ]'
run a
check "other clone receives the notice" '[ -f "$tmp/a/$notice" ] && [ "$(head_of a)" = "$(remote_head)" ]'
printf 'more from a\n' >"$tmp/a/more.md"
run a
moved=$(remote_head)
run b
check "origin moving on alerts again but publishes no second notice" '[ "$(alerts)" = 2 ] && [ "$(remote_head)" = "$moved" ]'
original=$(git -C "$tmp/remote.git" rev-parse "main:$notice")
printf 'edited elsewhere\n' >>"$tmp/a/$notice"
run a
run b
run b
check "notice edited elsewhere is restored while the conflict stands" '[ "$(git -C "$tmp/remote.git" rev-parse "main:$notice")" = "$original" ]'

# The owner merges by hand; only their own edits conflict, not the notice both sides carry.
git -C "$tmp/b" merge -q --no-edit origin/main >/dev/null 2>&1
check "hand merge conflicts only in the edited file, keeping the notice" '[ "$(git -C "$tmp/b" diff --name-only --diff-filter=U)" = "note.md" ] && [ -f "$tmp/b/$notice" ]'
printf 'merged\n' >"$tmp/b/note.md"
git -C "$tmp/b" add note.md && git -C "$tmp/b" commit -q --no-edit
run b
check "clean sync after the merge removes the notice and pushes" '[ ! -e "$tmp/b/$notice" ] && ! git -C "$tmp/remote.git" cat-file -e "main:$notice" 2>/dev/null && [ "$(head_of b)" = "$(remote_head)" ]'
run a
check "other clone loses the notice" '[ ! -e "$tmp/a/$notice" ] && [ "$(head_of a)" = "$(remote_head)" ]'

# The notice push is never forced: a commit that reaches origin between the fetch and that push
# survives, and the next run publishes the same notice on top of it. The conflict is in a file whose
# name is not ASCII, which the notice lists as written.
printf 'a again\n' >"$tmp/a/노트.md"
printf 'b again\n' >"$tmp/b/노트.md"
run a
printf 'racing\n' >"$tmp/a/race.md"
git -C "$tmp/a" add race.md && git -C "$tmp/a" commit -q -m race
raced=$(head_of a)
real_git=$(command -v git)
mkdir "$tmp/race"
cat >"$tmp/race/git" <<EOF
#!/bin/sh
# Clone a pushes its commit just before the first push of the run.
if [ "\$1" = push ] && [ -e "$tmp/race/armed" ]; then
	rm "$tmp/race/armed"
	"$real_git" -C "$tmp/a" push -q origin main
fi
exec "$real_git" "\$@"
EOF
chmod +x "$tmp/race/git"
touch "$tmp/race/armed"
(PATH="$tmp/race:$PATH"; run b)
check "a commit that reaches origin first is not overwritten" '[ ! -e "$tmp/race/armed" ] && [ "$(remote_head)" = "$raced" ] && git -C "$tmp/b" cat-file -e "HEAD:$notice"'
waiting=$(git -C "$tmp/b" rev-parse "HEAD:$notice")
run b
check "next run publishes the same notice on top of it" '[ "$(git -C "$tmp/remote.git" rev-parse main^)" = "$raced" ] && [ "$(git -C "$tmp/remote.git" rev-parse "main:$notice")" = "$waiting" ]'
check "notice lists a non-ASCII path as written" 'git -C "$tmp/remote.git" show "main:$notice" | grep -q "^- \`노트.md\`$"'
git -C "$tmp/b" merge -q --no-edit origin/main >/dev/null 2>&1
printf 'merged again\n' >"$tmp/b/노트.md"
git -C "$tmp/b" add 노트.md && git -C "$tmp/b" commit -q --no-edit
run b && run a
check "second conflict clears the same way" '[ ! -e "$tmp/a/$notice" ] && [ ! -e "$tmp/b/$notice" ] && [ "$(head_of a)" = "$(head_of b)" ] && [ "$(head_of a)" = "$(remote_head)" ]'

# companies/.gitignore keeps a company's files out of Git, through sync's own add as well.
mkdir -p "$tmp/a/companies/acme/knowledge"
cp "$(dirname "$sync_src")/../../../companies/.gitignore" "$tmp/a/companies/.gitignore"
printf 'note\n' >"$tmp/a/companies/acme/knowledge/note.md"
printf 'scan\n' >"$tmp/a/companies/acme/knowledge/scan.pdf"
run a
check "company Markdown reaches the remote" 'git -C "$tmp/remote.git" cat-file -e main:companies/acme/knowledge/note.md'
check "a company's other files stay out of Git" '! git -C "$tmp/remote.git" cat-file -e main:companies/acme/knowledge/scan.pdf 2>/dev/null && [ -f "$tmp/a/companies/acme/knowledge/scan.pdf" ]'

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

# A slug after sk- is short words joined by hyphens, so it passes wherever it sits, while keys in the
# usual places are still caught. Each case syncs one line in a file of its own. Key-shaped text is
# assembled here, so that this file does not trip the check it tests.
case_n=0
sync_line() {
	case_n=$((case_n + 1))
	printf '%s\n' "$1" >"$tmp/a/case-$case_n.md"
	case_before=$(head_of a)
	run a
}
committed() { sync_line "$1"; [ "$(head_of a)" != "$case_before" ]; }
blocked() {
	sync_line "$1"
	[ "$(head_of a)" = "$case_before" ] && tail -1 "$tmp/alerts" | grep -qF "case-$case_n.md"
	held=$?
	rm -f "$tmp/a/case-$case_n.md"
	return $held
}
sk=sk
alnum=aB3dE5gH7k
key48="${sk}-$alnum$alnum$alnum$alnum${alnum%??}"
mixed="${alnum}_${alnum}-${alnum}_${alnum}-$alnum"
url="https://news.example.com/2026/10/15/${sk}-acme-third-quarter-profit-cloud-demand.html"
check "URL whose path starts with sk- is committed" 'committed "$url"'
check "that URL in a Markdown link is committed" 'committed "[Acme posts record third-quarter profit]($url)"'
check "that URL in a sentence is committed" 'committed "Acme beat estimates on cloud demand, Example News reported at $url on Thursday."'
check "word ending in sk before a hyphenated slug is committed" 'committed "Compare the ri${sk}-adjusted-return-on-capital-model with last year."'
note="${sk}-acme-pricing-outlook.md"
check "relative link to a note whose name starts with sk- is committed" 'committed "[notes]($note)"'
check "that file name in prose is committed" 'committed "See $note for the numbers."'
check "heading anchor starting with sk- is committed" 'committed "[Q3](#${sk}-acme-third-quarter-results)"'
check "search query value starting with sk- is committed" 'committed "https://www.google.com/search?q=${sk}-acme-third-quarter-results"'
check "sk- key at line start is blocked" 'blocked "$key48"'
check "sk- key after a space is blocked" 'blocked "token $key48"'
check "sk- key after = is blocked" 'blocked "OPENAI_API_KEY=$key48"'
check "sk- key in double quotes is blocked" 'blocked "{\"api_key\": \"$key48\"}"'
check "sk- key as a URL query value is blocked" 'blocked "https://api.example.com/v1/models?api_key=$key48"'
check "sk- key after an encoded space is blocked" 'blocked "https://example.com/?auth=Bearer%20$key48"'
check "sk- key after an escaped newline in a JSON string is blocked" 'blocked "{\"text\": \"line one\\n$key48\"}"'
check "Anthropic API key is blocked" 'blocked "ANTHROPIC_API_KEY=${sk}-ant-api03-$mixed"'
check "Anthropic Admin API key is blocked" 'blocked "${sk}-ant-admin01-$mixed"'
check "OpenAI project key is blocked" 'blocked "export OPENAI_API_KEY=${sk}-proj-$mixed"'
check "OpenAI service account key is blocked" 'blocked "key: ${sk}-svcacct-$mixed"'
check "OpenAI admin key is blocked" 'blocked "\"${sk}-admin-$mixed\""'
gh=github aws=AKIA slack=xoxb dashes=-----
check "GitHub fine-grained token is blocked" 'blocked "${gh}_pat_${alnum}_${alnum}_$alnum"'
check "AWS access key ID is blocked" 'blocked "aws_access_key_id = ${aws}Z3X5C7V9B2N4M6L8"'
check "Slack token is blocked" 'blocked "${slack}-123456789012-$alnum$alnum"'
check "private key header is blocked" 'blocked "${dashes}BEGIN OPENSSH PRIVATE KEY$dashes"'

printf 'dev\n' >"$tmp/dev/dev.md"
dev_before=$(head_of dev)
run dev
status=$?
check "development checkout without upstream is refused" '[ $status -eq 2 ] && [ "$(head_of dev)" = "$dev_before" ]'

# Runtime sync runs after a sync, against the home folder it is given. A separate remote keeps
# the tool out of the clones above, whose runs use the real home folder.
git init -q --bare -b main "$tmp/remote2.git"
git clone -q "$tmp/remote2.git" "$tmp/r" 2>/dev/null
mkdir -p "$tmp/r/agent/operations/sync" "$tmp/r/agent/operations/runtime-sync" "$tmp/r/agent/skills/demo" "$tmp/home/.codex"
cp "$sync_src" "$tmp/r/agent/operations/sync/sync.sh"
cp "$(dirname "$sync_src")/../runtime-sync/runtime_sync.py" "$tmp/r/agent/operations/runtime-sync/"
printf '# BRAIN\n' >"$tmp/r/BRAIN.md"
printf -- '---\nname: demo\n---\n' >"$tmp/r/agent/skills/demo/SKILL.md"
git -C "$tmp/r" add -A && git -C "$tmp/r" commit -q -m init && git -C "$tmp/r" push -q origin main
git -C "$tmp/r" remote add upstream "$tmp/framework.git"
alerts_before=$(alerts)
(HOME="$tmp/home"; export HOME; run r)
check "runtime sync links the shared skills folder" '[ -L "$tmp/home/.agents/skills" ]'
check "runtime problem alerts" '[ "$(alerts)" = $((alerts_before + 1)) ]'
(HOME="$tmp/home"; export HOME; run r)
check "same runtime problem does not alert again" '[ "$(alerts)" = $((alerts_before + 1)) ]'

# Without python3 on the PATH, runtime sync is skipped with one alert.
mkdir "$tmp/nopy"
ln -s "$tmp/bin/osascript" "$tmp/nopy/osascript"
for f in /usr/bin/* /bin/* "$(dirname "$(command -v git)")"/*; do
	name=${f##*/}
	case $name in python3*) continue ;; esac
	[ -e "$tmp/nopy/$name" ] || ln -s "$f" "$tmp/nopy/$name"
done
alerts_before=$(alerts)
(HOME="$tmp/home"; PATH="$tmp/nopy"; export HOME PATH; run r; run r)
check "missing python3 alerts once" '[ "$(alerts)" = $((alerts_before + 1)) ] && tail -1 "$tmp/alerts" | grep -q python3'

if [ "$failed" -ne 0 ]; then
	echo "--- sync log"
	cat "$tmp/log"
	exit 1
fi
echo "all checks passed"
