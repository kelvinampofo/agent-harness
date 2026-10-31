---
name: type-discipline
description: Make the TypeScript compiler reject invalid states and mismatched values. Use after writing or changing TypeScript, and when designing data models, changing signatures, parsing external input, or fixing type errors. Also use for type-safety passes on existing code, including "make this type-safe", legacy cleanup, and casts or suppressions that silence the compiler.
---

# Type discipline

Make the compiler reject impossible states, mismatched values, and unhandled variants. Prefer a design that removes a failure case over code that handles it.

## After changing code

1. Run `npx tsc -b --noEmit` from the directory holding the nearest `tsconfig.json`, usually the repository root.
2. Fix the cause of each error, then run it again until it passes.
3. Review the types in your diff against the rules below. Fix what your change introduced, and report older problems outside it.

Stop when the types prevent a specific bug. Keep exported signatures stable unless the task covers their callers.

## Rules

- Reuse existing types and the project's schema library. When a schema, migration, or OpenAPI spec owns a shape, derive the type from that file.
- Model states as a discriminated union, with only the fields valid in each state.
- Check exhaustiveness with `satisfies never`, so a new variant breaks every site that needs a decision.
- Brand values when swapping them is a plausible bug, such as IDs, units, and validated strings. Keep the `as` inside one validating constructor.
- Parse external input where it enters the program: requests, JSON, files, environment variables, command-line arguments, and database rows. Accept `unknown`, then trust the parsed type from there on.

## Improving existing code

1. Run the type check. Fix existing errors first, or record them as the baseline.
2. Find the escapes: `as any`, `as unknown as`, `: any`, `@ts-ignore`, `@ts-nocheck`, and `@ts-expect-error`. Check each one before removing it, because some mark verified tool limitations.
3. Read the effective settings with `npx tsc -p tsconfig.json --showConfig`.
4. Measure a stricter setting before enabling it: `npx tsc -p tsconfig.json --noEmit --noUncheckedIndexedAccess`.
5. Start with external input and shared types, because fixing them corrects the code that uses them.
6. Fix one module or error class per change, keeping behaviour the same. Report any bug the types expose.
7. Enable a setting in `tsconfig.json` once its errors are gone.

## Gotchas

- `tsc --noEmit` checks nothing and exits 0 when `tsconfig.json` has `"files": []` and `references`. Use `tsc -b --noEmit`, which follows them.
- `tsc -b` rejects most compiler flags. In a solution project, pass `-p tsconfig.app.json` to measure a setting.
- Next.js generates route types such as `LayoutProps`. Run `npx next typegen` first on a clean checkout.
- A pass proves only what the settings enforce. `strict` leaves indexed access unchecked without `noUncheckedIndexedAccess`.
- `JSON.parse` and `response.json()` return `any`, which disables checking wherever it flows. Assign the result to `unknown` first.
- A type predicate such as `value is User` is an unchecked claim. A wrong predicate is as unsafe as `as`.
- `Partial<T>` and `Pick<T, K>` on a union lose the link between its fields. Write the variants out.
- Prefer `@ts-expect-error` with a reason to `@ts-ignore`. It fails once the error disappears.

## Delivery

Be brief. Name the states and mistakes the compiler now rejects. Show the type check result, and report any cast or suppression you kept.
