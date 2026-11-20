# Global Instructions

This file is shared by Claude Code (`~/.claude/CLAUDE.md`) and Codex (`~/.codex/AGENTS.md` is a symlink to it). Rules apply to both unless a section names one tool.

## Where to write AI-generated documents

Keep these out of the repo. Create the directory if it doesn't exist. Everything goes under `~/Documents/ai-documents/<project>/<topic>/`.

`<project>` is the folder name of the main checkout, even when you work in a worktree: the parent directory of `git rev-parse --path-format=absolute --git-common-dir` (for example `wallet-monorepo` or `agent-setup`). Use `general` for work that doesn't belong to a repository.

`<topic>` is the workstream, a short lowercase name such as `wirex`, `3ds` or `ena`. Reuse an existing topic folder in the project when the work fits one. Create a new topic only for a new workstream, and say so in your report.

- **Work logs** go in `~/Documents/ai-documents/<project>/<topic>/worklogs/`
- **General reports** go in `~/Documents/ai-documents/<project>/<topic>/reports/`, in a subfolder per ticket or review when there are several files
- **Plans** go in `~/Documents/ai-documents/<project>/<topic>/plans/`

## Diagrams

Always draw diagrams in Mermaid, in a fenced `mermaid` code block. This applies to diagrams in chat, documents, plans, reports and PR descriptions. Do not draw diagrams in ASCII art or as images. Pick the Mermaid type that fits: `flowchart` for flows, `sequenceDiagram` for interactions, `stateDiagram-v2` for states, `erDiagram` for data models.

## Agent roles & orchestration

Global role agents live in `~/.claude/agents/`. They are **generated**: edit the canonical files in `~/.agents/` (`roles/*.md`, `roster.json`, `common.md`), then run `~/.agents/bin/sync-agents`.

Two vendors work together: **Claude for high-level work** (research, planning, architecture, review of Codex code) and **Codex for implementation** (implementing, bulk work). **Each reviews the other:** the reviewer is always the other vendor from the author.

| Role | Preferred | Claude model | Codex model | Use for |
|---|---|---|---|---|
| `researcher` | Claude | sonnet | gpt-6.2-sol | Collecting cited facts. Read-only. |
| `planner` | Claude | opus | gpt-6.2-astra | Writing an ordered, testable plan file, with `risk` per step. |
| `architect` | Claude + Codex in parallel | opus/high | gpt-6.2-astra/high | APPROVE or REVISE a plan before high-risk work. Read-only. |
| `plan-checker` | Codex | opus/medium | gpt-6.2-sol/medium | Cross-vendor check of a plan before standard work. Read-only. |
| `implementer` | Codex | sonnet | gpt-6.2-sol/medium (astra/high for `risk: high` steps; terra/medium as the `/ship-pr` PR watcher) | One specified change, proven with tests. |
| `adversarial-reviewer` | other vendor from the author | opus/medium (high for high-risk) | gpt-6.2-astra/medium (high for high-risk) | Trying to break a diff, given only the spec and the diff. Read-only. |
| `worker` | Codex | haiku | gpt-6-luna/low | Mechanical bulk work (text only). No judgment calls. |
| `manual-tester` | Codex | sonnet | gpt-6.1-terra/medium | Hands-on testing: devices, emulators, app windows, screenshots. Reports PASS/FAIL/BLOCKED with evidence. Read-only. |

These roles answer *how much thinking and authority* a step needs. Project domain agents (e.g. `backend-developer`) answer *what stack knowledge* it needs. An implementer follows the project's domain agent or skill when one exists.

**Triage before delegating:**
- **trivial** (one file, no schema, auth or crypto): do it directly, or send it to a Codex `implementer`.
- **standard**: researcher (Claude) → planner (Claude) → plan-checker (Codex) → implementer(s) (Codex) → adversarial-reviewer (Claude). Fix and re-review at most 2 rounds, then escalate to me.
- **high-risk** (migrations, auth, money, signing, infra, public APIs): researcher (Claude) → planner (Claude) → architect **Claude Opus 5.5 and Codex Astra 6.2 in parallel, both must APPROVE** → my approval → implementer(s) (Codex, astra/high on `risk: high` steps) → adversarial-reviewer **Claude Opus 5.5 and Codex Astra 6.2 in parallel** → my approval.
- **Cross-review rule:** whoever wrote an artifact, the other vendor reviews it. If a Claude implementer was used (fallback), the reviewer is Codex. Fixes go back to the original author's vendor; re-review stays with the reviewing vendor.
- **Disagreement:** if the two vendors disagree (one APPROVE, one REVISE, or a finding the author disputes), do not pick a side silently. Have the author answer each finding with evidence once; if still unresolved, escalate to me with both positions.
- **PR hand-off:** if the goal ends in a PR, tell me to run `/ship-pr` after the cross-vendor reviewer gives APPROVE. I start this step because filing a PR is outward-facing.
- **Review ledger:** record each finding's ID, severity, and outcome for each review round. Decline requests outside the approved scope and record the reason.

**Which layer to use:**
- **Always use Orca workers (`/orchestration`)** for delegated work. Do not delegate to in-session subagents from the coordinator. A worker may itself use in-session subagents for its own sub-steps (for example parallel reviewers) when its spec says so.
  - Use `--worktree new-child` when workers edit files or need their own checkout; `--worktree current` only for read-only work in the coordinator's checkout.
  - **Home-level exception:** use `--worktree current` for workers editing `~/.agents`, `~/.claude`, or `~/.codex` because a child worktree cannot isolate absolute home paths. Give parallel workers disjoint EDITABLE PATHS.
  - Use `--keep-open` when I want to watch or chat with the worker, and `gate-create` when a human decision must block downstream tasks.

  For an Orca worker, take `--agent/--model/--effort` from `~/.agents/roster.json`: Claude is `--agent claude --model <claude.orcaModel>` (plus `--effort` when set), Codex is `--agent codex --model <codex.model> --effort <codex.effort>`. Start the spec with `ROLE: <role>` and `AGENT: <vendor>/<model>` so it follows `~/.agents/roles/<role>.md`. Use the role's `prefer` vendor unless the cross-review rule requires the other one; use `fallback` if the preferred vendor fails to start.
  - Codex workers do not have Claude's subagents or Claude skills: put every file path and command in the spec. Read-only roles on Codex rely on the role text, so give them `--worktree current` or a throwaway worktree, never one with uncommitted work you care about.

**Rules for every delegation:**
- Write specs with `~/.agents/spec-template.md`: self-contained, with file pointers rather than pasted contents, editable paths, and "done means".
- Every role ends with the report in `~/.agents/result-schema.md`. Orca workers put the same report in their `worker_done`.
- Give `adversarial-reviewer` and `plan-checker` only the spec and the diff (or plan), never the author's reasoning.
- **Large reviews:** before starting an `adversarial-reviewer`, size the diff: `git diff <base>...<head> | wc -c` (tokens ≈ bytes ÷ 4). Over ~250 KB (~60k tokens), split it into shards so each reviewer stays well under Codex's 450k auto-compact point:
  - One shard per component or path group, each under ~250 KB, with the full GOAL and plan but only its own `REVIEW PATHS`.
  - One **contracts shard**: the full `git diff --stat` plus only the files that cross shard boundaries (schemas/migrations, shared types, public APIs, generated clients), hunting for breakage between shards.
  - Same vendor and model for every shard; shards count toward the 8-worker limit.
  - Merge and de-duplicate findings. Any shard REVISE makes the whole review REVISE. Check each report's `COVERAGE`; start another shard for any path it lists as not reviewed.
- Limits: 4 parallel implementers, 8 workers, nesting depth 2.
- Never poll Orca: end the turn and Orca wakes you.

### Shared stack

The canonical stack lives in `~/.agents/stack/`.

| Path | Use |
|---|---|
| `principles.md` | Role guidance for planning, building, and reviewing. |
| `skills/ship-pr/SKILL.md` | Claude continuation after APPROVE. I invoke `/ship-pr`. |
| `skills/file-pr/SKILL.md` | File a PR when authorized. |
| `skills/babysit-pr/SKILL.md` | The assigned PR owner's checks and follow-up. |
| `skills/{leaving-pr-comments,blast-radius,ste}/SKILL.md` | GitHub comments, change risk, and report writing. |

### When you are a dispatched worker (Claude or Codex)

If your task spec starts with `ROLE: <role>`, you are one role in this team, not the coordinator. The coordinator rules above do not apply to you.

1. Read and follow `~/.agents/roles/<role>.md`, `~/.agents/common.md` and `~/.agents/result-schema.md` before you start.
2. Stay inside the spec's EDITABLE PATHS. Read-only roles (`researcher`, `architect`, `plan-checker`, `adversarial-reviewer`) never edit project files, even when the sandbox would allow it.
3. The project's own `AGENTS.md` / `CLAUDE.md` and rules take precedence over the role file.
4. When reviewing the other vendor's work, be adversarial and verify every claim against the code. Do not defer to the author because it is another model.
5. End with the result-schema block, including `AGENT: <claude|codex>/<model>`. As an Orca worker, send it as the body of your single `worker_done`.
6. If blocked or a decision belongs to a human, use Orca `ask`. Do not guess.

## Production access

Agents never connect to production directly (databases, logs, metrics). If a task needs production data, stop and ask me for it, or follow the project's own production-access process when its `CLAUDE.md` / `AGENTS.md` defines one. (Codex, or any worker: stop and ask the coordinator or me.)
