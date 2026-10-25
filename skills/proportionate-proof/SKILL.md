---
name: proportionate-proof
description: Use when asked whether a fix works, tests prove useful behaviour, a change is ready to ship, or an improvement has evidence. Includes "how do we know?" and bugs despite passing checks. Match verification to correctness, compatibility, performance, or agent-behaviour claims. Running a specified check or explaining test syntax does not need this workflow.
---

# Proportionate proof

Choose evidence strong enough to prove the claim. Match the effort to the risk and uncertainty. Limit conclusions to what the evidence shows.

## Approach

1. State the claim and what would disprove it. Work out the expected behaviour before trusting tests.
2. Pick the check that matches the claim: a formatter, a type checker, or running the code. Measure performance under relevant conditions. Compare equivalent tasks and environments for agent improvements.
3. Exercise relevant failure, cancellation, and timing paths. Check browser behaviour in supported runtimes.
4. Inspect assertions and results. Fix failures within scope and rerun affected checks. Reuse evidence while inputs and environments remain unchanged.
5. Report what you proved, what you did not test, and which checks were blocked. Narrow claims when decisive evidence is unavailable.

## Gotchas

- Passing tests can encode bugs, such as cancellation completing a destructive gesture.
- DOM typings do not prove browser support. Builds do not prove interactions work.
- Local results apply to production only when relevant conditions match.
- Shorter instructions do not prove better compliance. One run does not prove reliability.
- Test application behaviour without recreating browser-owned features.

## Example

Claim: saving twice creates one record. Submit twice while the first request is pending, then count stored records. A disabled button alone does not prove it.

## Delivery

Connect conclusions to evidence. Distinguish observations, inferred causes, and unmeasured benefits.
