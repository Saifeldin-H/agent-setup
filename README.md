# agent-setup

A shared setup for running **Claude Code** and **Codex** as one team of coding agents.

Claude does the high-level work: research, planning, architecture and review. Codex does the implementation. Each vendor reviews the other's work. Every role, model choice and rule is defined once here. A sync script then generates the files each tool reads.

## What's in the repo

| Path | Installs to | What it is |
|---|---|---|
| `agents/` | `~/.agents/` | The cross-tool layer: roles, roster, spec and result formats, the sync script and the shared skill stack. See [agents/README.md](agents/README.md). |
| `agents/roles/*.md` | | What each role does: `researcher`, `planner`, `architect`, `plan-checker`, `implementer`, `adversarial-reviewer`, `worker`, `manual-tester`. |
| `agents/roster.json` | | Which vendor, model and effort each role uses, plus limits and cross-review policy. Model choices live only here. |
| `agents/common.md` | | Rules added to every role. |
| `agents/spec-template.md`, `agents/result-schema.md` | | The format for task specs sent to workers and for the reports they send back. |
| `agents/bin/sync-agents` | | Generates `~/.claude/agents/*.md` from the roles and roster, links the stack skills into both tools, and makes `~/.codex/AGENTS.md` a symlink to `~/.claude/CLAUDE.md`. `--check` reports drift without writing anything. |
| `agents/stack/` | | Engineering principles (`principles.md`) and shared workflow skills: `file-pr`, `ship-pr`, `babysit-pr`, `leaving-pr-comments`, `blast-radius`, `ste`. `stack.json` says which tools get each skill. |
| `agents/stack/bin/check-stack`, `agents/stack/tests/` | | A validator that checks the stack's cross-references, and tests for the scripts. |
| `agents/stack/upstream/` | | Pinned, read-only copies of [tstack](https://github.com/t3dotgg/tstack) and [pstack](https://github.com/backnotprop/pstack), both MIT. [UPSTREAM.md](agents/stack/UPSTREAM.md) records what was adopted and what was changed. |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Global instructions shared by Claude Code and Codex: how to triage work, delegate it, review it across vendors and hand off PRs. |
| `claude/skills/pr-review-master/` | `~/.claude/skills/` | A Claude skill that reviews PRs with a Claude worker and a Codex worker in parallel, then merges their reports. |
| `install.sh` | | Installs everything above into `$HOME`. |

## How the work flows

Work is first sorted into one of three tiers, and each tier gets more review:

- **Trivial:** done directly, or sent to a Codex implementer.
- **Standard:** researcher → planner → plan-checker → implementer → adversarial-reviewer.
- **High-risk** (migrations, auth, money, signing, infra, public APIs): both vendors must approve the plan, both review the diff, and a human approves at each gate.

Delegated work runs as Orca workers. The full rules are in [claude/CLAUDE.md](claude/CLAUDE.md).

## Install

```sh
./install.sh
```

The script:

1. Copies `agents/` into `~/.agents/`. It leaves Orca's own `skills/` and `.orca-skill-digests/` alone.
2. Copies `claude/CLAUDE.md` and the Claude skills into `~/.claude/`. If `~/.agents/local/CLAUDE.local.md` exists, it appends that file to the installed `CLAUDE.md`. Put machine-specific rules there that must not be in the repo.
3. Runs `sync-agents`, then `sync-agents --check`.

Before overwriting anything, it moves the existing file to `~/.agent-stack-backup-<timestamp>/`.

You need to install Orca separately. It provides the `orca-*` and `orchestration` skills.

## Making changes

Edit the files in this repo, not the generated ones:

- **Never hand-edit:** `~/.claude/agents/*.md` and `~/.codex/AGENTS.md`, because `sync-agents` regenerates them.
- **After an edit:** run `./install.sh` again, or copy the changed files into `~/.agents/` and run `~/.agents/bin/sync-agents`.
- **To check for drift:** run `~/.agents/bin/sync-agents --check`. It fails if the installed setup no longer matches the sources.
- **To validate the stack:** run `~/.agents/stack/bin/check-stack`.

## Tests

```sh
agents/stack/tests/check-stack/run.sh   # validator fixtures
agents/stack/tests/pr-wait/run.sh       # pr-wait script, against a fake gh
agents/stack/tests/sync/run.sh          # sync-agents, in throwaway $HOME directories
```

The `sync` tests need two things on your machine: an installed `~/.agents/bin/sync-agents`, and a reference backup at `~/Documents/ai-documents/agent-setup/agent-stack/backups/2026-11-19-agents`.
