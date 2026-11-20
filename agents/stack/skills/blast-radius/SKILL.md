---
name: blast-radius
description: Find what a change could break beyond its diff and prove the fact that makes it safe. Use for adversarial reviews, high-risk design reviews, or questions about what a change could break.
---

# Blast radius

Read the diff and trace changed behavior through its callers and dependencies. Check pinned versions and local patches. Follow data and execution across boundaries a symbol search misses, such as stored records, wire formats, feature flags, and teardown.

Find the one fact it's safe because of. For example, a cache cleanup may be safe because every entry it removes has already expired. Test that fact with the smallest check that runs the same code or pinned dependency the app uses.

## Proof ladder

Use the strongest practical proof. Report the level reached for each safety claim.

1. State the claim. This level has no evidence.
2. Cite the relevant `file:line` in the implementation or dependency.
3. Trace the failure case and show where the code prevents it.
4. Run a test or script against the real code. Make it fail if the claim is wrong.
5. Reproduce the case in the running app and observe the result.

For a large change or one that crosses several components, ask the coordinator for a second-vendor review through Orca.

## Report

Describe what changed. State the safety fact, show the proof and its level, and mark the fact unproven if evidence is missing. For each risk, give the failure path, a source location, its likelihood and impact, and the cheapest check. Record which suspected risks you ruled out and why. Write the report with `ste` and remove private details from material approved for public sharing.
