#!/usr/bin/env bash
# Install this agent stack into $HOME.
# Existing files are moved to ~/.agent-stack-backup-<timestamp> first.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
BACKUP="$HOME/.agent-stack-backup-$(date +%Y%m%d-%H%M%S)"

backup() {
  if [ -e "$1" ] || [ -L "$1" ]; then
    mkdir -p "$BACKUP/$(dirname "${1#$HOME/}")"
    mv "$1" "$BACKUP/${1#$HOME/}"
    echo "backed up $1"
  fi
}

mkdir -p "$HOME/.claude/skills" "$HOME/.codex"

# 1. ~/.agents: replace managed files, keep Orca-owned skills/ and .orca-skill-digests/
mkdir -p "$HOME/.agents"
for item in "$SRC"/agents/* "$SRC"/agents/.[!.]*; do
  [ -e "$item" ] || continue
  name="$(basename "$item")"
  ledger=""
  if [ "$name" = stack ] && [ -f "$HOME/.agents/stack/.installed.json" ]; then
    ledger="$(mktemp)"; cp "$HOME/.agents/stack/.installed.json" "$ledger"
  fi
  backup "$HOME/.agents/$name"
  cp -R "$item" "$HOME/.agents/$name"
  # keep the link ledger so sync-agents still owns links it made before
  [ -n "$ledger" ] && mv "$ledger" "$HOME/.agents/stack/.installed.json"
done
mkdir -p "$HOME/.agents/skills"
chmod +x "$HOME/.agents/bin/sync-agents" "$HOME/.agents/stack/bin/check-stack"

# 2. Global instructions and personal skills
backup "$HOME/.claude/CLAUDE.md"
cp "$SRC/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
# Machine-specific rules that must not be in the repo are appended from a local file.
LOCAL_RULES="$HOME/.agents/local/CLAUDE.local.md"
if [ -f "$LOCAL_RULES" ]; then
  printf '\n' >> "$HOME/.claude/CLAUDE.md"
  cat "$LOCAL_RULES" >> "$HOME/.claude/CLAUDE.md"
  echo "appended $LOCAL_RULES"
fi
for skill in "$SRC"/claude/skills/*; do
  name="$(basename "$skill")"
  backup "$HOME/.claude/skills/$name"
  cp -R "$skill" "$HOME/.claude/skills/$name"
done

# 3. ~/.codex/AGENTS.md is recreated as a symlink by sync-agents
if [ -e "$HOME/.codex/AGENTS.md" ] && [ ! -L "$HOME/.codex/AGENTS.md" ]; then
  backup "$HOME/.codex/AGENTS.md"
fi

# 4. Generate ~/.claude/agents, skill links and the Codex symlink
"$HOME/.agents/bin/sync-agents"
"$HOME/.agents/bin/sync-agents" --check

[ -d "$BACKUP" ] && echo "Backups are in $BACKUP"
echo "Done. Install Orca separately; it provides the orca-* and orchestration skills."
