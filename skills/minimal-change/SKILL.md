---
name: minimal-change
description: Use for simplification, cleanup, refactoring, or KISS passes, including when work feels overengineered or the user says "this is doing too much". Choose the smallest complete change preserving behaviour and intent. Fully specified mechanical edits do not need this workflow.
---

# Minimal change

Solve the whole problem with the least unnecessary complexity. Changed-line count is not the goal.

## Approach

1. Define the outcome and the behaviour, contracts, and design choices to preserve.
2. Trace callers and failure paths before judging code redundant.
3. Delete unnecessary work, then simplify. Prefer a larger change when it fixes the cause more cleanly. Explain why it is needed.
4. Stay within scope. Preserve useful surrounding material and intervening edits. Leave sound code alone.
5. Check behaviour and review the diff for accidental removals. Stop once the outcome is achieved.

## Gotchas

- Unused CSS variables and single-caller hooks may have a deliberate role.
- Guards that seem redundant may prevent stale results overwriting newer state.
- Extracting branches can lower complexity scores without clarifying the flow.
- Shortened examples must still teach the intended concept.

## Example

Two screens disagree on a delivery charge. Share the agreed calculation, preserve their layouts, and check both totals.

## Delivery

Explain the change, preserved behaviour, checks, and uncertainty. Measure performance before claiming gains.
