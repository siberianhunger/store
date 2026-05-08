---
name: plan-review
description: Use when the user asks Codex to review one or more plan markdown files as an architect against the current project. Reads the relevant code, removes overbuilt or awkward decisions, improves the plan in place, and reports what changed.
---

# Plan Review

Use this skill when the user wants architectural review of existing plan files before implementation.

## Workflow

1. Locate plan files. Prefer `codex_tasks/codex_plans/*.md` unless the user names specific files.
2. Read every target plan completely.
3. For each major planned point, inspect the related current code:
   - config and environment handling
   - database/schema/model boundaries
   - route/service/provider boundaries
   - templates/CSS/frontend patterns
   - tests and existing verification style
4. Review as a pragmatic architect for a small production internet store:
   - remove overbuilt admin/platform ideas unless they are directly needed
   - remove vague or duplicate config flags
   - prefer explicit safe flows for payment, stock, privacy, and credentials
   - keep operator workflows simple and auditable
   - keep frontend changes consistent with the existing design system
5. Edit the plan files in place. Keep the original feature scope, but improve the path.
6. Do not add unrelated features just because they would be nice later.
7. After editing, audit that each explicit user request is still covered.

## What To Challenge

- New services where a simple route/script/provider is enough.
- Fake integrations that accidentally bypass real business logic.
- Plans that expose private customer data, raw access keys, exact stock counts, or credentials.
- Telegram/payment/webhook flows without authorization, idempotency, or clear failure behavior.
- Frontend plans that create marketing pages instead of usable store screens.
- Large schemas or event tables before the first version needs history.
- Tests that only assert files exist instead of behavior.

## What To Preserve

- The user's intended feature.
- Existing repo patterns and naming where they are sound.
- Small-store operational reality: simple checkout, protected tracking, clear owner notifications, safe payment state transitions.
- Current test/coverage discipline.

## Output

Final response should include:

- which plan files were reviewed
- high-signal list of changes made
- overall opinion on plan quality and remaining risks
- verification performed, such as files read or grep checks
