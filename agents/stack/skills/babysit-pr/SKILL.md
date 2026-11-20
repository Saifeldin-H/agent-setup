---
name: babysit-pr
description: "Watch a pull request through CI and review as the single Orca worker assigned PR: own."
---

# Babysit PR

One worker owns each PR watch. The coordinator and review workers leave watching to that owner. Record the repo, PR number, expected head SHA, and what the spec authorizes before starting.

Run `gh auth status`, then run `~/.agents/stack/skills/babysit-pr/scripts/ready-check <o/r> <n> <expected_sha> --preflight`. Check that it exited 0 and reported `state=OPEN` with the expected head. If either check fails, report `OUTCOME: blocked` with evidence and ask the coordinator.

## Watch and classify

Use the run mode for your vendor.

- **Codex:** Run one foreground command with the longest command timeout your tool allows, capped at 55 minutes. The Codex foreground timeout limit is unverified. If the tool yields a session before the process exits, keep the same session.
- **Claude:** Start the watcher with Bash `run_in_background: true` and `timeout: 3600000` ms, or with Monitor and `timeout_ms: 3600000`. Let the exit notification wake you.

Use `--until ready` only when the repo uses Greptile or Macroscope. The watcher keeps its own state in `~/.local/state/pr-wait/`.

```sh
~/.agents/stack/skills/babysit-pr/scripts/pr-wait "$pr" --repo "$repo" --until green
```

After every watcher exit, including a timeout, run `~/.agents/stack/skills/babysit-pr/scripts/ready-check "$repo" "$pr" "$expected_sha"`. Save the exit codes and the classifier JSON. Use that JSON to decide what to do. If the watcher exited 2, ask the coordinator about bad input or a competing watcher and make no fixes.

| Class | Action |
|---|---|
| `READY` | Finish when the watcher exited 0. If it exited 1 and the classifier reports READY, ask the coordinator with both outputs. |
| `MERGED`, `CLOSED`, `HEAD_CHANGED`, `AUTO_MERGE_ON`, `IN_MERGE_QUEUE` | Send `worker_done --outcome failed` with the evidence. Make no fixes. |
| `DRAFT` | Report the draft state and stop. Do not change draft status. |
| `CHECK_FAILED` | Verify the check failure and use the fix loop. |
| `BEHIND`, `CONFLICT` | Use the branch setup and rebase steps below if authorized. |
| `UNRESOLVED_THREADS`, `CHANGES_REQUESTED` | Read the feedback and verify it on the current head. Use the fix loop for valid findings. Reply using `leaving-pr-comments` at `~/.agents/stack/skills/leaving-pr-comments/SKILL.md`. |
| `CHECK_PENDING` | On timeout, count an empty run as described below. Otherwise, restart the watcher in the vendor run mode. If the watcher repeatedly reports completion while the same check is pending, report the mismatch and ask the coordinator. |
| `BAD_INPUT` | Ask the coordinator for the correct repo, PR number, and full head SHA. |
| `API_ERROR` | Run `gh api rate_limit` and retry the classifier once. If it still reports an API error, ask the coordinator. |

Count a run as empty if it times out without a watcher event or if it times out and `ready-check` reports `CHECK_PENDING`. Count these runs regardless of duration. Reset the count after any other run. After three consecutive empty runs, use the Orca `ask` command from your dispatch and end the turn.

On timeout, follow the table for actionable results. If the classifier reports `READY` or `CHECK_PENDING` and the empty-run limit has not been reached, rerun the watcher. Do not start a separate watch, poll loop, or sleep loop.

READY requires an open PR that is out of draft and out of the merge queue, with `merged=false`, no auto-merge request, no conflict or behind state, and zero unresolved threads. A reviewer’s latest approval or change request applies across commits. Require green checks on the expected head. When branch policy names required checks, use those checks. Otherwise, use every current check run and status on the head. If none have appeared, the result is `CHECK_PENDING`. Bot review status such as Copilot is reported separately. A truncated thread result cannot prove that all threads are resolved.

## Fix loop and hand-back

Opening a PR or pushing requires explicit user authorization. Verify the spec has `AUTHORIZED BY: user, <date>, <what>` covering the action. Stop and report if it is missing. Before drafting any GitHub text, read the target repo's `CLAUDE.md`, `AGENTS.md`, and `.claude/rules/*.md` that exist. This includes commit messages and review replies. Omit AI attribution and all AI or model mentions by default. Add attribution or a cross-vendor review block only if the repo rules explicitly allow it and the user or spec asks for it.

Verify the check failure or review finding. Keep the fix in scope. Give a written reason for declining a finding and record follow-ups.

### Check out the PR branch

Work in the Orca child worktree. Verify that it is clean and that the fetch and push URLs for `origin` point to the existing PR head repository. Use the PR branch from the spec as `pr_branch`. Run these commands before any edit. Stop and report if any command fails.

```sh
git fetch origin "$pr_branch"
git switch -C "$pr_branch" "origin/$pr_branch"
test "$(git rev-parse HEAD)" = "$expected_sha"
```

Do not bypass Git's checked-out-branch protection. If the PR branch is in use elsewhere, ask the coordinator.

### Rebase and push

Before a rebase, fetch the PR base from `origin` and confirm that `origin/$base` matches the PR base on GitHub. If it does not, stop and report. Save the commit subjects before rebasing. After rebasing, verify that the base is an ancestor and the subjects are unchanged. Run the commands in this order. Stop and report if any command fails.

```sh
git fetch origin "$base"
git log --oneline "origin/$base..HEAD"
before_subjects=$(git log --format=%s "origin/$base..HEAD")
git rebase "origin/$base"
git merge-base --is-ancestor "origin/$base" HEAD
git log --oneline "origin/$base..HEAD"
after_subjects=$(git log --format=%s "origin/$base..HEAD")
test "$before_subjects" = "$after_subjects"
```

Test the fix. Before pushing, verify that the PR is open at the expected SHA. Immediately before the push, confirm that `origin` still advertises that SHA for the PR branch. Stop if the lookup or SHA check fails. Push only to the existing PR branch. Never create a new remote branch.

```sh
advertised_ref=$(git ls-remote --exit-code --refs origin "refs/heads/$pr_branch")
test "$(printf '%s\n' "$advertised_ref" | cut -f1)" = "$expected_sha"
```

For a rebased branch, push with the original expected SHA as the lease.

```sh
git push --force-with-lease="refs/heads/$pr_branch:$expected_sha" origin "HEAD:refs/heads/$pr_branch"
```

For a fix without a rebase, verify that the push is a fast-forward and use a plain push.

```sh
git merge-base --is-ancestor "$expected_sha" HEAD
git push origin "HEAD:refs/heads/$pr_branch"
```

Record the new head as the expected SHA after a successful push. Ask the coordinator for a delta review and give the old and new SHAs. End the turn and wait for the review answer. Resume the watch with the new head after approval.

For READY, send `worker_done` with `PR:` for the URL, head SHA, and state, and `CHECKS:` for the classifier class, check results, bot review, and `merged=false`. Leave the PR open.

Never merge a PR, enable auto-merge, or use `--admin`.
