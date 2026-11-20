# Upstream sources

Both pinned snapshots use the MIT license. The snapshots retain their original license and copyright notices and are kept for reference.

| Repository | Pinned revision | License |
|---|---|---|
| [t3dotgg/tstack](https://github.com/t3dotgg/tstack) | `11e37a74d0a6868c121cd0910ab2b3bd9873b92a` | [MIT, Theo Browne](upstream/tstack/LICENSE) |
| [backnotprop/pstack](https://github.com/backnotprop/pstack) | `0d2dc00df47d7686c94324cfe9c3444710d9f16d` | [MIT, Lauren Tan](upstream/pstack/LICENSE) |

## Adopted and folded content

| Upstream source | Kept | Changed |
|---|---|---|
| [tstack file-pr](upstream/tstack/skills/file-pr/SKILL.md) | Existing PR check, local diff review, problem-first description, privacy check, open PR by default, and REST fallback. | Repository title, branch, template, draft, and attribution rules take precedence. The cross-vendor review block is conditional on project policy. |
| [tstack leaving-pr-comments](upstream/tstack/skills/leaving-pr-comments/SKILL.md) | Concise comments, concrete evidence, privacy checks, and confirmation before resolving a thread. | Apply project attribution rules, including a ban on AI mentions where required. Use plain technical English for GitHub comments. |
| [tstack babysit-pr](upstream/tstack/skills/babysit-pr/SKILL.md) and [pr-wait](upstream/tstack/skills/babysit-pr/scripts/pr-wait) | One watcher per PR, the byte-for-byte `pr-wait` script, checks after pushes, and evidence-based review replies. | An Orca worker owns the PR watch. Local `ready-check` classifies the expected head. The coordinator arranges delta review, and the worker hands back a ready PR. |
| [tstack council](upstream/tstack/skills/council/SKILL.md) | Independent review and a guard against scope creep. | Use the existing cross-vendor workflow, its verdicts, and its two-round cap. |
| [tstack sol-loop](upstream/tstack/skills/sol-loop/SKILL.md) | A finding ledger, severity, a round limit, and delta review after fixes. | Use Orca and the project roster for cross-vendor review. Record findings in the shared result schema. |
| [pstack blast-radius](upstream/pstack/skills/blast-radius/SKILL.md) | The five proof levels and the one fact that makes the change safe. | Allow model invocation. Ask the coordinator for a second-vendor review through Orca for wide changes. Use `ste` for the report. |
| [pstack technical-writing](upstream/pstack/skills/technical-writing/SKILL.md) | Simplified Technical English rules for short sentences, direct commands, and conditions before actions. | Condense into `ste` for reports and plans addressed to the user. |
| [pstack unslop](upstream/pstack/skills/unslop/SKILL.md) | Rules 3–33 for direct, specific, readable prose. | Condense into `ste` with the technical-writing rules. |
| [pstack interrogate](upstream/pstack/skills/interrogate/SKILL.md) | Give concrete proof for review findings. | The adversarial-reviewer uses Orca and requires a run or definitive code path for a confirmed finding. |
| [pstack arena](upstream/pstack/skills/arena/SKILL.md) | An independent perspective for a wide review. | A coordinator-arranged second-vendor review takes the place of the upstream fan-out. |

`ship-pr` is a local, user-invoked continuation. It uses the adapted PR filing, comment, and watching skills after cross-vendor approval.

Each principle below comes from pstack. The named rule is kept in [principles.md](principles.md) as short guidance for the relevant roles. Each source skill's standalone instructions are condensed into one entry per relevant section.

| Upstream source | Kept |
|---|---|
| [principle-foundational-thinking](upstream/pstack/skills/principle-foundational-thinking/SKILL.md) | Choose core types around access patterns and do shared groundwork first. |
| [principle-sequence-verifiable-units](upstream/pstack/skills/principle-sequence-verifiable-units/SKILL.md) | Check each small unit before proceeding. |
| [principle-subtract-before-you-add](upstream/pstack/skills/principle-subtract-before-you-add/SKILL.md) | Remove redundant code before building. |
| [principle-laziness-protocol](upstream/pstack/skills/principle-laziness-protocol/SKILL.md) | Decide in one place and minimize the change. |
| [principle-migrate-callers-then-delete-legacy-apis](upstream/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | Migrate internal callers and their contract tests before removing the legacy API. |
| [principle-make-operations-idempotent](upstream/pstack/skills/principle-make-operations-idempotent/SKILL.md) | Reconcile against current state so retries converge. |
| [principle-separate-before-serializing-shared-state](upstream/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md) | Give writers separate state when possible and enforce serialized writes when needed. |
| [principle-prove-it-works](upstream/pstack/skills/principle-prove-it-works/SKILL.md) | Verify the real artifact or behavior. |
| [principle-fix-root-causes](upstream/pstack/skills/principle-fix-root-causes/SKILL.md) | Reproduce the problem and fix the first fault. |
| [principle-test-behavior-not-implementation](upstream/pstack/skills/principle-test-behavior-not-implementation/SKILL.md) | Assert observable behavior through the public interface. |
| [principle-boundary-discipline](upstream/pstack/skills/principle-boundary-discipline/SKILL.md) | Parse at boundaries and keep business logic free of the framework. |
| [principle-type-system-discipline](upstream/pstack/skills/principle-type-system-discipline/SKILL.md) | Use types to exclude impossible states and handle every variant. |
| [tdd](upstream/pstack/skills/tdd/SKILL.md) | Show a regression test failing before a fix and passing after it when practical. |
| [principle-attack-the-premise](upstream/pstack/skills/principle-attack-the-premise/SKILL.md) | Test the shared assumption behind repeated failures. |
| [principle-minimize-reader-load](upstream/pstack/skills/principle-minimize-reader-load/SKILL.md) | Remove pass-through layers and shrink mutable state scope. |
| [principle-explain-the-number](upstream/pstack/skills/principle-explain-the-number/SKILL.md) | Find the measured limit, rule out confounders, and report count and spread. |

## Skills excluded by the plan

| Upstream skills | Reason |
|---|---|
| tstack `full-send` | Merges and force-pushes autonomously. |
| tstack `council`, `sol-loop` | Use a second orchestrator for reviews. `council` also needs a third model provider. The local review workflow uses the ledger, severity, and round limit. |
| pstack `swarm`, `arena`, `interrogate` | Start Cursor or in-session agents outside Orca. The adversarial-reviewer uses the proof standard from `interrogate`. |
| pstack `setup-pstack` | Introduces a second model registry alongside `roster.json`. |
| pstack `poteto-mode`, `automate-me`, `ketchup*`, `bro`, `make-bot-ui`, and standalone `principle-*` skills | Encode personal style or add entries to the skill list. Selected principles are condensed into `principles.md`. |
| tstack `takeover`, `modernize`, and pstack `reflect`, `correct`, `create-verification-skill` | Deferred to phase 2. |
