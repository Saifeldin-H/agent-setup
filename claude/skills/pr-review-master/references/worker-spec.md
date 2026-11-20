# Worker spec template

Fill `{PR}`, `{REPO}`, `{TICKET}` (or "none"), `{SUBAGENT_MODEL}` (`sonnet`, or `opus` for a high-risk PR), `{RULE_FILES}` (the repo's instruction files for the changed paths) and replace `{TESTING}` with the block(s) for the PR type, using the repo's real commands.

```text
ROLE: read-only PR reviewer (this spec overrides ~/.agents/roles/adversarial-reviewer.md: reviewer subagents run on {SUBAGENT_MODEL})
GOAL: Review PR #{PR} ({TICKET}) end to end and report findings and test evidence.
TARGET: your own worktree (rev-{PR}).
EDITABLE PATHS: none. Local throwaway tests or harness files are allowed; leave them uncommitted, delete them at the end, and list them in the report.
NON-ZERO EXIT: a failed build or test is a finding to report, not a task failure. Fail the task only if you could not review at all.

HARD RULES
- Never push, commit to the PR branch, comment on GitHub, approve, request changes, merge, or write to the ticket tracker.
- Never use production systems, shared deployed environments, or prod secrets. Local stack only.
- Follow {RULE_FILES}, including the project's attribution rules.

SETUP
1. Fetch over HTTPS:
   git fetch https://github.com/{REPO}.git pull/{PR}/head:pr-{PR} && git checkout pr-{PR}
   Confirm HEAD equals `gh pr view {PR} --repo {REPO} --json headRefOid`.
2. orca worktree set --worktree path:$(pwd) --pr {PR} --workspace-status in-review   (add --linear-issue {TICKET} for a Linear ticket)
3. Read: gh pr view {PR}, gh pr diff {PR}, review comments (gh api repos/{REPO}/pulls/{PR}/comments, gh pr view {PR} --comments), gh pr checks {PR}, and the ticket + comments (read-only) for the acceptance criteria. No ticket: use the PR description.

STEP 1 — ADVERSARIAL REVIEW
Start THREE subagents in one message, each with model "{SUBAGENT_MODEL}". Give each the PR number, the diff command and the acceptance criteria. Tell each one to read the surrounding code, not only the diff, and to return file:line, severity (blocker/major/minor/nit), a concrete failure scenario and a fix:
- security: authn/authz, secret or PII leaks (logs, analytics, crash reports), injection, deep links/intents, token handling, new deps, CI permissions, pinned actions.
- bugs: logic, races, lifecycle/state, null and edge cases, error paths, regressions in callers, gaps against the acceptance criteria, weak or missing tests.
- cleanliness: repo conventions ({RULE_FILES}, .claude/skills), duplication, dead code, stale comments/docs, naming, test quality.
Then verify every finding against the code yourself. Drop false positives. Mark each kept finding CONFIRMED or PLAUSIBLE.

STEP 2 — FUNCTIONAL TEST
{TESTING}

REPORT (worker_done) — short and factual:
- PR #{PR} {TICKET}, head sha, verdict: APPROVE / APPROVE WITH NITS / REQUEST CHANGES / BLOCKED
- Each acceptance criterion: MET / NOT MET / UNTESTED, with evidence
- Findings ranked: severity, CONFIRMED/PLAUSIBLE, file:line, scenario, fix
- Testing done: commands and pass/fail, device flows, absolute screenshot paths
- Gaps and why
- Local leftovers (uncommitted files, stacks, containers, volumes, downloaded tools)
```

## {TESTING} blocks

Replace `<...>` with the repo's commands and skills from the Project settings.

### backend
```text
- Follow the backend instruction file and domain skill, if any. Run typecheck, lint and the unit tests of the touched modules: <commands>.
- Run their integration tests on a local stack if they exist: <local stack command>. Use the repo's normal migration command, never a destructive schema push.
- List behaviours, branches and error paths in the changed code that no test covers. Where cheap, write a local test that proves a gap or a bug, run it, report it, then delete it.
- Check new env vars, secrets, deploy config and .env.example files. Check that schema changes are backward compatible (expand/contract) and report rollout risk.
- If an end-to-end run against a stubbed external service is possible, do it. Never call real external services.
- Tear down any stack you start and remove its volumes.
```

### web
```text
- Run typecheck, lint and tests for the changed app: <commands>.
- Run the app against a local stack, open the changed pages in Orca's browser, drive the changed flow, and take a screenshot per acceptance criterion.
- Check the changed screens against the hard rules in `~/.agents/stack/skills/refactoring-ui/SKILL.md` and the symptoms in its `references/diagnose.md`, in light and dark mode. Report each violation with the rule, the element, and the measured value.
```

### android
```text
- Build and unit tests first: <assemble debug + unit test commands, with any JAVA_HOME / ANDROID_HOME / JVM memory flags the repo needs>.
- DEVICE GATE: do NOT boot, create or attach any emulator yourself. When the build and unit tests are done, run `orca orchestration ask` with subject "device" and end your turn. The coordinator sends the device brief.
```

### ios
```text
- Build and run the related unit tests: <commands>.
- DEVICE GATE: do NOT boot or create a simulator yourself. When the build and unit tests are done, run `orca orchestration ask` with subject "device" and end your turn. The coordinator sends the device brief.
```

### contracts
```text
- Build and test the touched contracts: <commands, e.g. forge build / forge test>. Focus the security reviewer on access control, reentrancy, upgrade/storage layout, and value flows.
```

### ci-infra
```text
- Run actionlint on changed workflows and shellcheck on changed scripts. Run the repo's own CI checks and any spec tests for the scripts: <commands>.
- Review triggers, required approvals/environments, branch guards, permissions blocks, secret exposure to forks, pull_request_target, pinned action SHAs, concurrency, idempotency and rollback.
- Dry-run what runs without real credentials. Never call real store or cloud APIs.
- Check the docs/runbook against what the workflows do.
- If the PR also changes app code, add the matching app block.
```

## Device brief (coordinator sends with `send`)

```text
DEVICE GRANTED: you have exclusive use of <device serial / simulator name> until you report. Others wait, so aim for under 30 minutes.
1. Attach through Orca: orca emulator attach "<device name>" --worktree path:$(pwd) --focus --json. Target only this device. Do not kill, wipe or cold-boot it. Do not uninstall other apps.
2. Install your debug build. If the flow needs backend data, use a local stack. If you cannot reach the state, simulate it (intent / deep link, seeded row, throwaway test harness) and say exactly what you simulated.
3. Drive the changed flow through the pane (orca emulator ax → tap/gesture), 1–2 s per screen.
4. Run the instrumented / UI tests the PR adds or changes, one at a time.
5. Take a screenshot per acceptance criterion into your scratchpad; list absolute paths.
6. At the end: stop the app, uninstall test builds, reset any device setting you changed (font scale, dark mode, locale), tear down stacks and remove their volumes, delete harness files, leave the device booted. Then report worker_done with per-criterion device evidence and any new findings.
<PR-specific: the flow to drive and what to confirm>
```
