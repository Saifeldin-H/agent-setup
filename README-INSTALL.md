# Agent stack: install on a new machine

A generic Claude + Codex orchestration stack: roles, roster, shared skills and global instructions. It contains no project-specific settings.

1. Unzip anywhere: `unzip agent-stack-generic.zip && cd agent-stack`
2. Run `./install.sh`
   - It copies `agents/` to `~/.agents`, plus `claude/CLAUDE.md` and the `pr-review-master` skill to `~/.claude`.
   - It moves existing files to `~/.agent-stack-backup-<timestamp>` first.
   - It runs `~/.agents/bin/sync-agents` to generate `~/.claude/agents/*.md`, the skill links and `~/.codex/AGENTS.md` (a symlink to `~/.claude/CLAUDE.md`).
3. Install Orca separately. It installs the `orca-*` and `orchestration` skills, which this zip does not include.
4. Per project: put build/test commands, device names, ticket rules and production-access rules in the project's own `CLAUDE.md` / `AGENTS.md`. The stack reads them from there.

Requires: bash, python3. Change models, efforts and limits in `~/.agents/roster.json`, then run `~/.agents/bin/sync-agents`.
