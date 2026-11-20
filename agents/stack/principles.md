# Engineering principles

## Plan

### principle-foundational-thinking

Choose core types and data structures around how the system reads and writes data. Put shared groundwork before features.
Source `pstack/skills/principle-foundational-thinking/SKILL.md`.

### principle-sequence-verifiable-units

Start from a known good state. Make one small change, run its check, and proceed when the check passes.
Source `pstack/skills/principle-sequence-verifiable-units/SKILL.md`.

### principle-subtract-before-you-add

Remove dead code and redundant checks before building. Add only what the observed use and requirements call for.
Source `pstack/skills/principle-subtract-before-you-add/SKILL.md`.

### principle-laziness-protocol

Make each decision in one place and pass along the result. Use the smallest change that solves the problem.
Source `pstack/skills/principle-laziness-protocol/SKILL.md`.

### principle-migrate-callers-then-delete-legacy-apis

When no external caller needs compatibility, move all callers to the new API before deleting the old one. Update tests to check the new contract.
Source `pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`.

### principle-make-operations-idempotent

Read the current state and apply only the changes needed to reach the goal. Check what happens on a retry after each possible interruption.
Source `pstack/skills/principle-make-operations-idempotent/SKILL.md`.

### principle-separate-before-serializing-shared-state

Give each writer its own state when it publishes independent facts. Enforce serialized access when writers must share one target.
Source `pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md`.

## Build

### principle-prove-it-works

Run the feature or inspect the actual artifact against the requirement. Keep a repeatable check when practical.
Source `pstack/skills/principle-prove-it-works/SKILL.md`.

### principle-fix-root-causes

Reproduce the symptom and trace it to the first wrong decision or state. Fix that cause wherever it occurs.
Source `pstack/skills/principle-fix-root-causes/SKILL.md`.

### principle-test-behavior-not-implementation

Test observable results through the public interface. Derive expected values and effects from the requirement.
Source `pstack/skills/principle-test-behavior-not-implementation/SKILL.md`.

### principle-boundary-discipline

Validate and parse external data at the boundary. Pass typed values to business logic that can run without the framework.
Source `pstack/skills/principle-boundary-discipline/SKILL.md`.

### principle-type-system-discipline

Use types that rule out invalid states and distinguish values with different meanings. Handle every variant and derive types from the source schema.
Source `pstack/skills/principle-type-system-discipline/SKILL.md`.

### tdd

If the user requests a test or a cheap local test exists, verify that it fails for the expected reason before fixing the bug. Run the test again after the fix. If a new test is impractical, use the closest executable check.
Source `pstack/skills/tdd/SKILL.md`.

## Review

### principle-attack-the-premise

When two fixes fail the same check and share an assumption, write down the assumption. Test it directly before attempting another fix.
Source `pstack/skills/principle-attack-the-premise/SKILL.md`.

### principle-minimize-reader-load

Remove layers that only forward calls. Keep mutable state close to its users and derive values when you can.
Source `pstack/skills/principle-minimize-reader-load/SKILL.md`.

### principle-explain-the-number

State which result would change the decision. Use profiles or counters to find the limit and rule out skipped work or noise. Report the run count, spread, and limit.
Source `pstack/skills/principle-explain-the-number/SKILL.md`.

### principle-test-behavior-not-implementation

Check that a test would fail if observable behavior broke. Check that it would still pass if the internals changed while behavior stayed the same.
Source `pstack/skills/principle-test-behavior-not-implementation/SKILL.md`.
