---
name: explain
description: Explain code, diffs, or PRs in Markdown with background, intuition, and a walkthrough. Use when asked to explain, walk through, catch up on, or understand code. Not for code review.
---

# Explain

Explain inspected code or changes in one Markdown document.

Apply the user's personal writing instructions throughout.

## Scope

Explain the named code. Otherwise use uncommitted changes, then commits on the current branch that are not on the default branch. If neither exists, ask for scope.

Read the diff, callers, implementations, and tests needed to support the explanation. For unchanged code, trace the entry point and main data flow. Say which claims come from tests, which you confirmed by running code, and which you inferred. Say when you did not run the code.

## Sections

### Background

Briefly explain the system and problem.

### Intuition

Explain the core idea with an example traced through the code. Label invented values and assumptions. Omit toy data when unhelpful. Add a diagram when useful.

### Code

Group changes by purpose, or unchanged code by responsibility or execution order. Show the important code beside the explanation. Use focused excerpts for current behaviour and short diffs to explain changes. Explain effects and constraints. Source links support the walkthrough but do not replace code excerpts.

## Format

- Use one `#` title and consecutive heading levels. Add a table of contents only for long documents.
- Use tables for comparisons and language-labelled code fences.
- Link to concrete source files rather than directories, which may not open in Markdown viewers.
- In saved Markdown, use local file paths relative to the document's final location. VS Code may interpret filesystem-absolute paths such as `/Users/...` as workspace-relative. Resolve every local target from the saved document's directory and verify that it is a file.
- In chat, follow the host's file-link format. Do not copy chat-only absolute paths or `path:line` syntax into saved Markdown.
- Place further-reading links at the end of the relevant paragraph, after the explanation. Use specific official API references or Wikipedia articles. Verify the links and omit generic or redundant resources.

## Inline diffs

When explaining changes, use short `diff` blocks to show the relevant before and after. Keep enough context to understand the change and explain its effect beside the block. For mostly new code, show the relevant code directly rather than an all-additions diff.

For example, a simplified control-flow change:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

Label schematic diffs as simplified. Preserve real names and order. Mark whether each diff is pseudocode or a real patch, and explain its effect. Show complete code when mostly new, needed for context, or intended for copying.

## Diagrams

Use `mermaid` for relationships, data flow, and sequences. Prefer `flowchart LR` for component communication. Name nodes clearly and label edges with actions, data, or protocols. Use bidirectional arrows only for two-way communication.

Keep labels short, split crowded diagrams, and inspect rendering where possible.

Explain key relationships. Make diagrams match the code, and mark proposed changes apart from existing behaviour.

## Save and deliver

Check claims, names, links, execution order, and examples against the code, including relevant branches and defaults. Check the prose against the user's writing instructions. Keep small explanations brief.

Save outside the repository under `~/explanations/`, creating it if needed. Prefix the filename with today's date, such as `2026-01-12-interaction-design.md`. Format only that file.

Open with `code <file>`. Report formatting or opening failures and link the file.
