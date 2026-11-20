# Task spec template

Use this for every delegated task: a Claude `Agent` prompt, or Orca `task-create --spec-file`. A spec has to be self-contained, because the receiving role sees nothing else.

```text
ROLE: <role>  (follow ~/.agents/roles/<role>.md, ~/.agents/common.md and ~/.agents/result-schema.md)
AGENT: <claude|codex>/<model id>   (from ~/.agents/roster.json)
GOAL: <one sentence: the outcome, not the activity>
CONTEXT: <file paths to read: research report, plan, ADR, relevant code. Pointers, not pasted contents>
TARGET: <repo / worktree / directory>
CHANGE: <what to do. For implementer: the exact plan step>
PR: <none | file | own>   (optional)
AUTHORIZED BY: user, <date>, <what>   (required for PR: file or PR: own)
EDITABLE PATHS: <globs the role may modify, or "none (read-only)">
REVIEW PATHS: <adversarial-reviewer only, optional: globs this shard reviews when a large diff is split; omit to review the whole diff>
CONSTRAINTS: <must-not-touch, compatibility, conventions, project rules to honour>
DONE MEANS: <the evidence that proves completion: commands that must exit 0, tests, files that must exist>
NON-ZERO EXIT: <"task failed"  OR  "capturing the failure is the deliverable">
REPORT: ~/.agents/result-schema.md
```

Rules for writing specs:
- **PR work:** use `PR: file` or `PR: own` only with explicit user authorization. Record the date and what the user authorized on the `AUTHORIZED BY: user, <date>, <what>` line.
- **GitHub text:** read the repo's `CLAUDE.md`, `AGENTS.md`, and `.claude/rules/*.md` files first. Do not include AI attribution or mention AI or model names in any GitHub text unless the repo's rules explicitly allow it.
- **Reviewer:** give `adversarial-reviewer` and `plan-checker` only the GOAL, the plan (step(s)) and the diff range. Do not include the author's reasoning or transcript.
- **Large reviews:** if the diff is over ~250 KB (`git diff <base>...<head> | wc -c`), split the review into shards with non-overlapping `REVIEW PATHS`, plus one contracts shard for files that cross shard boundaries (see "Large reviews" in `~/.claude/CLAUDE.md`).
- **Cross-review:** the reviewer must be the other vendor from the author (see `policy.cross_review` in `roster.json`). Codex wrote it → Claude reviews; Claude wrote it → Codex reviews.
- **Codex specs:** Codex workers do not have your context or Claude-only tools (subagents, skills). Write file paths and commands out in full.
- **Worker:** spell out the exact pattern for a `worker`. If you cannot write it out mechanically, the task is not a worker task.
- **Parallel tasks:** give tasks that run in parallel EDITABLE PATHS that do not overlap. If they cannot avoid overlap, run them in separate worktrees (Orca `--worktree new-child`).
