---
name: planning
description: Use when the user wants to turn rough feature ideas into actionable project plan files, especially after a /planning-style prompt. Creates or updates concise implementation plans in the repo, grounded in the current codebase, without implementing the feature.
---

# Planning

Use this skill when the user gives rough feature ideas and wants Codex to produce one or more implementation plans.

## Workflow

1. Inspect the current project structure and the code areas related to the requested feature.
2. Identify the target plan directory. Prefer `codex_tasks/codex_plans/` when it exists; otherwise create it.
3. Create one focused `.md` plan per coherent feature area. Do not mix unrelated work into one plan.
4. Ground the plan in the existing architecture:
   - name the relevant files/modules already present
   - point out current behavior
   - specify the safest implementation path
   - include data/schema changes if needed
   - include route/UI/config/test changes if needed
5. Include tests and verification commands. Coverage should not regress when the plan is later implemented.
6. Keep the plan practical for the size of the project. Avoid enterprise/admin/platform features unless the user asked for them.
7. After writing, summarize what plan files were created and what each one covers.

## Plan Shape

Use this structure unless the repo already has a stronger convention:

```markdown
# Short Plan Title

Goal: ...

## Current Situation

## Desired Flow

## Implementation Details

## Tests And Verification

## Implementation Order

## Acceptance Criteria
```

## Quality Rules

- Read code before planning; do not invent architecture that conflicts with the repo.
- Prefer small, testable increments.
- Call out security/privacy/payment/stock risks explicitly when relevant.
- Do not put secrets or real credentials in plans.
- Do not implement code while using this skill unless the user explicitly asks for implementation.
- If the user asks for "history" or "completed" plans, keep current work in `codex_tasks/codex_plans/` and move done plans to `codex_tasks/completed_tasks/`.

## Output

Final response should be short:

- list created/updated plan files
- one sentence per plan
- mention any important tradeoff or assumption
