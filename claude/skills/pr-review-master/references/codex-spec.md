# Codex reviewer spec template

Fill `{PR}`, `{REPO}`, `{TICKET}` (or "none"), `{ACCEPTANCE}` (the acceptance criteria,
copied as plain text, because Codex has no tracker access), `{RULE_FILES}` (the repo's
instruction files and domain skills for the changed paths), `{TEST_COMMANDS}` (the repo's
real build/lint/test commands for the changed components), `{FOCUS}` (PR-specific
risk areas, written by the coordinator from the diff file list, not from Claude findings),
and `{REVIEW_PATHS}` ("the whole diff", or this shard's globs when a large PR is split).

```text
ROLE: adversarial-reviewer
AGENT: codex/gpt-6.2-sol (effort high)
Follow ~/.agents/roles/adversarial-reviewer.md, ~/.agents/common.md and ~/.agents/result-schema.md. The project's CLAUDE.md / AGENTS.md and .claude/rules/ take precedence.

GOAL: Find real defects in PR #{PR} ({TICKET}) before merge: security, correctness, and code cleanliness.
TARGET: your own worktree (rev-{PR}-cx). It is a throwaway checkout.
REVIEW PATHS: {REVIEW_PATHS}. Review only these; read other code only as context. If you cannot cover them all, stop with OUTCOME blocked and list what is left.
EDITABLE PATHS: none (read-only). Throwaway repro tests are allowed; delete them before you report and list them under EVIDENCE.
NON-ZERO EXIT: a failing test that proves a defect is evidence, not a task failure. Use OUTCOME failed only if you could not review at all.

HARD RULES
- Never push, commit, comment on GitHub, approve, request changes, merge, or write to the ticket tracker.
- Never use production systems, prod secrets, or real external partner APIs.
- Do not start emulators, simulators or Docker stacks.
- Never print the contents of .env files, keys or tokens.

SETUP (you may switch branches for this task)
1. git fetch https://github.com/{REPO}.git pull/{PR}/head:pr-{PR}-cx
2. git checkout pr-{PR}-cx
3. Confirm HEAD equals: gh pr view {PR} --repo {REPO} --json headRefOid --jq .headRefOid
4. Read the PR: gh pr view {PR} --repo {REPO}
5. Read the diff: gh pr diff {PR} --repo {REPO}
6. Read the repo rules that apply to the changed paths: {RULE_FILES}, plus .claude/rules/*.md.

ACCEPTANCE CRITERIA
{ACCEPTANCE}

REVIEW — read the surrounding code and the callers, not only the diff:
- Security: authn/authz on new routes, service-to-service auth, secret/PII leaks (logs, analytics, crash reports), injection, deep links/intents, token handling, new dependencies, CI permissions and pinned actions.
- Correctness: logic, races and concurrency (double requests, retries, redelivery), idempotency, lifecycle/state, null and edge cases, error paths that swallow failures, regressions in callers, deploy order between services, migrations (expand/contract).
- Acceptance: mark each criterion MET / NOT MET / UNTESTED with evidence.
- Tests: tests that cannot fail, tests that mock away the subject, missing negative cases, test fixtures or DI modules that the change breaks.
- Cleanliness: repo conventions, dead code, duplication, stale comments/docs.
PR-specific focus:
{FOCUS}

TEST COMMANDS (run what applies; record exit codes)
{TEST_COMMANDS}
- CI changes: actionlint <workflows>; shellcheck <scripts>

REPORT: the ~/.agents/result-schema.md block as the body of your single worker_done. In FINDINGS give, for each: [CONFIRMED|PLAUSIBLE] file:line — severity (blocker/major/minor/nit) — issue — failure scenario — fix — repro. Add one line per acceptance criterion under EVIDENCE. Fill COVERAGE (reviewed / not reviewed). Put your overall verdict (APPROVE / APPROVE WITH NITS / REQUEST CHANGES) in SUMMARY.
```
