---
name: pr-review-master
description: >-
  Master PR review: for every PR the user sends (links, numbers or a screenshot of
  PR links), run two Orca workers per PR: a Claude worker that does a three-way
  adversarial review (security, bugs, cleanliness) on Sonnet (Opus for high-risk PRs) plus a functional test
  by PR type, and an independent Codex (gpt-6.2-sol) adversarial reviewer. Merge
  both reports, and report back in STE. The Claude functional test is by PR type
  (backend tests and gap hunt, web visual check, mobile on a device or simulator, CI dry run). Posts nothing until the user decides; then posts the chosen
  request-changes or a bare approval and cleans up. Use when the user says "review
  these PRs", "master review", "pr-review-master", or sends PR links to review.
---

# PR review master

You are the **coordinator**. You never review code yourself; Orca workers do. You
gather their reports, write one STE report, and act only on the user's decision.

## Project settings

This skill is repo-neutral. Take repo-specific values from the target repo's
`CLAUDE.md` / `AGENTS.md` (and nested ones such as `backend/CLAUDE.md`), its
`.claude/rules/` and `.claude/skills/`. Collect them once in Phase 0:

| Setting | Where to find it | If missing |
|---|---|---|
| Build, lint, typecheck and test commands per component | repo instruction files, `README`, `package.json` / `Makefile` / `justfile` / Gradle / CI workflows | Use the commands the CI workflows run |
| Ticket key pattern and tracker | PR title, branch name, repo instructions | No ticket: take acceptance criteria from the PR description |
| Domain skills per component | `.claude/skills/` | Use none |
| Device / simulator name | repo instructions | Ask the user before any device test |
| Local stack command (Docker etc.) | repo instructions | Skip end-to-end runs and say so |

## Overrides

- **Reviewer models.** This skill overrides the global `adversarial-reviewer` role
  in `~/.agents/roster.json`:
  - Claude side, normal PR: **Sonnet** (`claude-sonnet-5-5` for the Orca worker, `model: "sonnet"` for its subagents).
  - Claude side, **high-risk PR**: **Opus** (`claude-opus-5-5` for the Orca worker, `model: "opus"` for its subagents).
  - Codex side, every PR: **`gpt-6.2-sol`, effort `high`** (not astra).
  A PR is **high-risk** when it touches migrations or schema, auth or access control,
  money or payments, signing or keys, infra or CI release pipelines,
  or public APIs. When unsure, treat it as high-risk.
  Do not take the reviewer models from the roster.
- **Two vendors per PR.** Every PR gets one Claude worker and one Codex worker, in
  parallel, each in its own worktree. Neither sees the other's findings (cross-vendor
  independence). Codex only reviews; Claude does all functional testing (devices,
  local stacks, visual review), because those need Orca emulator control and Claude skills.
- **Orca only.** Do not do review work with in-session subagents in the coordinator.
- **Report language.** Load the `ste` skill before the first report to the user.
  Text posted on GitHub is plain technical English, not STE.

## Constants

| Name | Value |
|---|---|
| Orca CLI | `$ORCA_CLI_COMMAND`, else `orca` |
| Claude worker | `--agent claude --model claude-sonnet-5-5` (high-risk: `claude-opus-5-5`), worktree `rev-<n>` |
| Codex worker | `--agent codex --model gpt-6.2-sol --effort high`, worktree `rev-<n>-cx` |
| Worker limit | 8 workers = 4 PRs at a time; queue the rest |
| GitHub label | `review: in-progress` (see Phase 0) |
| Ticket state | `In Review` (only if the project uses a tracker Orca can reach) |
| Device | from Project settings; one PR at a time per device |
| Scratch | the coordinator scratchpad; specs under `specs/`, notes in `review-log.md` |

## Phase 0 — Intake (coordinator)

1. Find each PR number, repo, head SHA, author, changed files:
   `gh pr view <n> --repo <repo> --json number,title,headRefName,headRefOid,author,files,state,isDraft`.
2. Collect the Project settings above. Find the ticket key in the title or branch, if the project uses one.
3. Sort each PR into one or more types: backend, web, android, ios, contracts, ci-infra, other.
   A PR with several types gets every matching test step.
   Also mark each PR **normal** or **high-risk** (see Overrides) and tell the user which.
4. Add the GitHub label if the repo has it: `gh pr edit <n> --repo <repo> --add-label "review: in-progress"`.
   If the label does not exist, skip this step; do not create labels.
5. If the ticket is in a tracker you can reach (for example Linear through `orca-linear`),
   move it to **In Review**, only if its state is Triage, Backlog, Todo or In Progress.
   Do not move a Done or Canceled ticket.

## Phase 1 — Start workers (coordinator)

6. Load the Orca guide once: `orca skills get orchestration`.
7. Write two specs per PR:
   - Claude: `references/worker-spec.md` (fill `{PR}`, `{REPO}`, `{TICKET}`, `{SUBAGENT_MODEL}` = `sonnet` or `opus` for high-risk, `{RULE_FILES}`, and the `{TESTING}` block for the PR type, with the repo's real commands).
   - Codex: `references/codex-spec.md` (fill `{PR}`, `{REPO}`, `{TICKET}`, `{ACCEPTANCE}` = the acceptance criteria copied as text, `{RULE_FILES}`, `{TEST_COMMANDS}`, and `{FOCUS}` = PR-specific risk areas). Never put Claude findings in it.
8. Start both workers per PR (at most 4 PRs at once):
   `orca orchestration worker-start --spec-file <claude spec> --task-title "Review #<n> <TICKET> (claude)" --worktree new-child --name rev-<n> --agent claude --model <claude-sonnet-5-5 | claude-opus-5-5 for high-risk> --json`
   `orca orchestration worker-start --spec-file <codex spec> --task-title "Review #<n> <TICKET> (codex)" --worktree new-child --name rev-<n>-cx --agent codex --model gpt-6.2-sol --effort high --json`
   If the Codex worker fails to start, report it to the user; do not replace it with a second Claude reviewer without asking.
   **Large PRs:** size the diff first: `gh pr diff <n> --repo <repo> | wc -c`. Over ~250 KB, split the Codex review into shards (the "Large reviews" rule in `~/.claude/CLAUDE.md`): one Codex spec per path group with `{REVIEW_PATHS}` set, plus one contracts shard for files that cross shard boundaries. Name them `rev-<n>-cx-<k>`. Shards count toward the 8-worker limit, so start fewer PRs at once if needed. Under 250 KB, set `{REVIEW_PATHS}` to "the whole diff". Tell the user when a PR was split.
9. Attach each PR to the master workspace:
   `orca reference add <PR url> --worktree path:<master worktree>`.
10. Tell the user the table of PRs and workers, then **end the turn**. Orca wakes you.

## Phase 2–3 — What each worker does

**Codex worker** (`references/codex-spec.md`): fetches the PR over HTTPS, does one
adversarial review covering security, bugs and cleanliness, may run tests and write
throwaway repro tests, and reports in `~/.agents/result-schema.md` shape. No device,
no local stack, no Orca emulator.

**Claude worker** (`references/worker-spec.md`):

- Check out the PR head over HTTPS and link its worktree to the PR (`orca worktree set --pr`, plus `--linear-issue` when there is a Linear ticket).
- Three subagents in parallel (Sonnet; Opus for high-risk): **security**, **bugs/correctness**, **cleanliness**.
  The worker verifies every finding against the code, drops false ones, marks the
  rest CONFIRMED/PLAUSIBLE with severity, `file:line`, failure scenario and fix,
  and marks each acceptance criterion MET / NOT MET / UNTESTED.
- Functional test by type (see the spec blocks).
- Report with `worker_done`.

## Device control (coordinator)

Only one device test runs at a time per device.

- Workers do the review, build and unit tests first, then `ask` for the device and end their turn.
- Before you grant the device, confirm it is free: `adb devices` (Android) or
  `xcrun simctl list devices booted` (iOS), the foreground app is the launcher or the
  app under test, and `orca emulator list` shows no other session.
- If it is free, `send` the worker the device brief (in `references/worker-spec.md`).
  Queue the others; grant the next one when a worker reports.
- If it is not free, not booted, or no device is configured, **tell the user** and wait.
  Do not create AVDs or simulators, and do not boot emulators from a sandboxed shell:
  they can run without hardware acceleration and hang at boot.

## Phase 4 — Report (coordinator)

When a worker reports, write its result in `review-log.md`. Check the Codex report's
`COVERAGE`: start another shard for any path it lists as not reviewed. When all workers
of a PR have settled (every Codex shard counts as the Codex side), merge their reports:

1. Combine findings that describe the same defect. Tag each finding **[Both]**,
   **[Claude]** or **[Codex]**. [Both] findings rank first within a severity.
2. **Disagreement:** a finding one vendor marks CONFIRMED and the other's report or
   evidence contradicts, a severity gap of two levels or more, or different verdicts.
   Send the disputed finding (the claim and its evidence only) once to the other
   vendor's worker with `orchestration send` and ask it to confirm or refute with
   `file:line` evidence. If it is still unresolved, list it under **Disagreements**
   with both positions. Never pick a side silently.
3. A single-vendor finding stays in the report with its own label; the coordinator
   does not drop it without evidence.

When every PR is merged, load `ste` and give one report:

- A summary table: PR, ticket, risk (normal / high-risk), Claude verdict, Codex verdict, combined verdict (APPROVE / APPROVE WITH NITS / REQUEST CHANGES / BLOCKED), tests, device result.
- **Problems to fix before merge** — the blocking or near-blocking findings, each with scenario and fix.
- **Smaller findings** per PR.
- **Disagreements** between the vendors, with both positions.
- Device evidence: screenshot paths.
- **Decisions for you** at the end.

A worker that ends its turn without `worker_done` is usually waiting on a
background job; leave it unless its output shows it is stuck.

## Phase 5 — No action before the decision

Do not push, commit, comment, approve or change the ticket further until the user decides.

## Phase 6 — Act on the decision

- Follow `~/.agents/stack/skills/leaving-pr-comments/SKILL.md` when writing GitHub review comments.
- **Request changes:** one review per PR with the problems the user chose:
  `gh pr review <n> --repo <repo> --request-changes --body-file <file>`.
  Each problem: what is wrong, a concrete failure scenario, the fix, `file:line`.
- **Approve:** `gh pr review <n> --repo <repo> --approve` with no body, unless the user asks for comments.
- Never merge, never enable auto-merge.

## Phase 7 — Cleanup (only when the user says so)

For each PR the user names (both the Claude and the Codex worker):

1. Stop a worker that is still working (`orca orchestration worker-stop --dispatch <id>`), then release every dispatch of that PR (`worker-release`).
2. For both `rev-<n>` and `rev-<n>-cx`: check the worktree has no tracked changes, then `orca worktree rm --worktree path:<wt> --delete-branch`.
3. `git worktree prune`. Delete leftover `pr-<n>`, `pr-<n>-cx`, and `*/rev-<n>` / `*/rev-<n>-cx` branches only if `git log <b> --not --remotes` is empty.
4. Remove Docker containers and volumes the review made (the workers list them under local leftovers). Do not touch containers of other sessions.
5. Stop build daemons (Gradle, Kotlin, etc.) whose cwd belongs to the review (check with `lsof -d cwd`); leave daemons that started after the review.
6. Delete tools or SDKs a worker downloaded only for the review.
7. Delete the scratch folders of the review sessions (the `rev-<n>` workspace folders under the Claude scratch root), screenshots included.
8. Remove the PR references from the master workspace (`orca reference remove <url> --worktree path:<master>`).
9. Leave the device or simulator booted.
