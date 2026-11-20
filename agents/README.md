# ~/.agents: the cross-tool agent layer

This directory holds the tool-neutral definitions that every coding agent (Claude Code and Codex) is built from.

| Path | Owner | Purpose |
|---|---|---|
| `skills/`, `.orca-skill-digests/` | **Orca** | Orca-managed skills. Do not edit. |
| `roles/<role>.md` | you | Canonical role behaviour (researcher, planner, architect, plan-checker, implementer, adversarial-reviewer, worker, manual-tester) |
| `common.md` | you | Rules appended to every role |
| `roster.json` | you | role → per-tool model/effort/enabled, plus limits. This is the only place model choices live. |
| `spec-template.md` | you | Task spec format for Agent prompts and `orca orchestration task-create --spec-file` |
| `result-schema.md` | you | Final report / `worker_done` body format, the same for every tool |
| `bin/sync-agents` | you | Generates `~/.claude/agents/*.md` and keeps `~/.codex/AGENTS.md` a symlink to `~/.claude/CLAUDE.md` (one shared global instruction file). Run it after any edit. `--check` detects drift. |
| `stack/principles.md`, `stack/skills/` | you | Engineering principles and shared workflow skills. |
| `stack/stack.json`, `stack/.installed.json` | you | Skill manifest and link ledger used by `bin/sync-agents`. |
| `stack/bin/check-stack`, `stack/tests/` | you | Stack validator and offline fixtures. |
| `stack/UPSTREAM.md`, `stack/upstream/` | you | Source notes and pinned, read-only upstream copies. |

## Claude + Codex

Both vendors are enabled. `roster.json` decides who does what:

- **Claude for high-level work:** research (Sonnet 5.5), planning and architecture (Opus 5.5), adversarial review of Codex code (Opus 5.5).
- **Codex for implementation:** implementer (`gpt-6.2-sol`; `gpt-6.2-astra`/high for `risk: high` steps), worker (`gpt-6-luna`), manual-tester and PR watchers started by `/ship-pr` (`gpt-6.1-terra`/medium), plan-checker (`gpt-6.2-sol`/medium), review of Claude-written code (`gpt-6.2-astra`/medium; high for high-risk).
- **Cross-review:** the reviewer is always the other vendor from the author. High-risk work gets both vendors in parallel: Claude Opus 5.5 + Codex `gpt-6.2-astra` for architecture and review. Rules are in `policy` in `roster.json`.

Orca: `--agent claude --model <claude.orcaModel>` or `--agent codex --model <codex.model> --effort <codex.effort>`. Read-only for Codex is enforced by the role text only, not by a sandbox flag.
