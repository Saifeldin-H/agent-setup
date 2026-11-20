---
name: ship-pr
description: File reviewed work and hand back a verified READY pull request. Run only when the user types /ship-pr.
disable-model-invocation: true
---

# Ship PR

Start after the CLAUDE.md pipeline has a cross-vendor APPROVE, or when the user asks to ship existing reviewed work. Keep the review ledger with the filing and watch evidence.

The user's `/ship-pr` invocation or direct request to open the PR authorizes opening it. The coordinator records `AUTHORIZED BY: user, <date>, /ship-pr <what>` in its own notes and copies it into the PR owner's spec. For a direct request, record the requested action in `<what>`. Use the recorded authorization without asking again. Record permission to push only when the user explicitly granted it. Stop and report before opening or pushing if the action lacks authorization.

Before drafting any GitHub text, read the target repo's `CLAUDE.md`, `AGENTS.md`, and `.claude/rules/*.md` that exist. This applies to PR titles and bodies, comments, review replies, and commit messages. Omit AI attribution and all AI or model mentions by default. Add attribution or a cross-vendor review block only if the repo rules explicitly allow it and the user or spec asks for it.

1. The coordinator follows `file-pr` at `~/.agents/stack/skills/file-pr/SKILL.md`. Record the PR URL, number, repository, and current head SHA.
2. The coordinator starts one Codex worker with `orca orchestration worker-start --worktree new-child --name <short>`. Use `ROLE: implementer` and `PR: own` and the watcher settings `roles.implementer.watch.codex` in `~/.agents/roster.json` (`--agent codex --model gpt-6.1-terra --effort medium`). Include the expected SHA, PR and base branches, target repositories, editable paths, reply and push permissions, and the user's authorization. Copy the exact checkout, rebase, verification, and push commands from the **Check out the PR branch** and **Rebase and push** sections of `babysit-pr` at `~/.agents/stack/skills/babysit-pr/SKILL.md` into the spec. Tell the worker to use the existing PR branch and never create a new remote branch. If the branch is checked out in a clean worktree devoted to this task, release it by detaching that worktree at its current head before dispatch. If another task or the user owns that worktree, or it has local changes, stop and report. Delegate through Orca. The worker watches the PR. The coordinator ends the turn and waits for Orca to wake it.
3. When the worker asks for review of a fix range, the coordinator dispatches a delta review by the other vendor. Count it toward the two-round limit. Record the result in the ledger and reply to the worker through Orca. If anyone posts on the PR, use `leaving-pr-comments` at `~/.agents/stack/skills/leaving-pr-comments/SKILL.md`.
4. On a successful `worker_done`, the coordinator reruns `~/.agents/stack/skills/babysit-pr/scripts/ready-check <o/r> <n> <expected_sha>` against the worker's reviewed head. Report READY only if the classifier confirms it. Give the PR link, review ledger, and evidence for the head and checks. Report any failed worker result or non-READY classification with its evidence.

Never merge the PR, enable auto-merge, or bypass branch protection. Leave the PR open for the user.
