# Result schema (every role, every tool)

Every role ends its final message with this block. An Orca worker uses the same text as the body of its single `worker_done` message (`--outcome succeeded|failed`). Because the shape is fixed, a Claude coordinator can parse a Codex worker's report, and the reverse.

```text
ROLE: <researcher|planner|architect|plan-checker|implementer|adversarial-reviewer|worker|manual-tester>
AGENT: <claude|codex>/<model id>
OUTCOME: succeeded | failed | blocked
SUMMARY: <1–3 sentences: what was done or found>
ARTIFACTS: <paths of files written (plan, report, ADR) or "none">
FILES_CHANGED: <path list, or "none">
EVIDENCE:
- <command> → exit <n> (<short result>)
- <file:line or URL> — <what it shows>
FINDINGS:            # reviewer/architect/researcher; omit if empty
- [CONFIRMED|PLAUSIBLE|INFO] [blocker|should|nit] <file:line> — <issue> — repro: <steps/test>
COVERAGE:            # adversarial-reviewer only
- reviewed: <paths/globs reviewed in full>
- not reviewed: <paths in scope you did not review, and why, or "none">
VERDICT: <APPROVE|REVISE|n/a>    # architect / plan-checker only
PR: <URL, head SHA, state>    # optional
CHECKS: <ready-check class, checks, bot review, merged=false>    # optional
OPEN_QUESTIONS:
- <question needing a human or coordinator decision, or "none">
```

Rules:
- `failed` means the task could not be done. `blocked` means the role needs a decision before it can continue. A review that found bugs is still `succeeded`.
- Only list something under EVIDENCE if you ran it or read it in this session.
- Severity is required for findings in reports produced after the stack is installed. Older reports stay valid.
