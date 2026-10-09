#!/bin/sh
# Install a per-user launchd job that runs sync.sh for this live brain. See ../sync.md.
# Usage: install-macos.sh [interval-seconds]   (default 300)
set -eu

here=$(cd "$(dirname "$0")" && pwd -P)
root=$(cd "$here/../.." && pwd -P)
interval=${1:-300}
label=local.o2b.sync
plist="$HOME/Library/LaunchAgents/$label.plist"
logfile="$HOME/Library/Logs/o2b-sync.log"

if ! git -C "$root" remote get-url upstream >/dev/null 2>&1; then
	echo "refusing: $root has no upstream remote, so it is not a live brain" >&2
	exit 2
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat >"$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key><string>$label</string>
	<key>ProgramArguments</key>
	<array><string>/bin/sh</string><string>$here/sync.sh</string></array>
	<key>EnvironmentVariables</key>
	<dict><key>PATH</key><string>$PATH</string></dict>
	<key>StartInterval</key><integer>$interval</integer>
	<key>RunAtLoad</key><true/>
	<key>StandardOutPath</key><string>$logfile</string>
	<key>StandardErrorPath</key><string>$logfile</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$plist"
echo "installed $label: syncs $root every ${interval}s; log $logfile"
