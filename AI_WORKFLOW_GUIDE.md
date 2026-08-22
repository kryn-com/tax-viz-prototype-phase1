# AI Workflow Guide

This repository uses AI most effectively when each session stays narrow, phase-bound, and test-led. `PROJECT_SCOPE.md` and the newest `PHASE_*_HANDOFF.md` are the durable context; do not rebuild prior discussion from chat history.

## Rules

1. Work only on one approved phase at a time.
2. Start a fresh AI chat at each phase boundary.
3. Begin each phase by reading only:
   - `PROJECT_SCOPE.md`
   - the newest `PHASE_*_HANDOFF.md`
   - the specific source files and tests relevant to the approved task
4. Do not inspect the whole repository unless the approved phase truly requires it.
5. Prefer one complete, constrained implementation prompt over many micro-prompts.
6. Reference repository files by name instead of pasting large file contents.
7. Keep responses concise: changed files, tests added, validation results, and blockers only.
8. Use the scope and handoff files as durable context; do not recreate historical discussion.
9. Require focused tests first, then run the full suite before committing.
10. Review `git status --short` before staging, after committing, and after pushing.
11. Keep documentation work separate from implementation when practical.
12. Preserve project boundaries: no tax logic changes, UI, charts, API, serialization, CLI, or federal-state integration unless an approved phase explicitly authorizes them.

## Git discipline

Use small, auditable commits tied to the approved objective. Before any `git add`, check `git status --short`; check it again immediately after commit and again after push so no unintended files drift into the branch.

Recommended rhythm:
1. Read scope, newest handoff, and only the relevant files.
2. Confirm one narrow approved objective before editing code.
3. Make the smallest change set that satisfies that objective.
4. Run focused tests for the touched area first.
5. Run the full test suite before commit.
6. Review `git status --short`, then stage intentionally.
7. Commit with a message tied to the approved objective.
8. Push, then review `git status --short` again.

## Session output format

Ask AI assistants to respond with:
- Files changed.
- Tests added or updated.
- Validation commands and results.
- Blockers or open questions.

Avoid long narrative status reports unless explicitly requested.

## New Session Starter

Read:
- `PROJECT_SCOPE.md`
- the newest `PHASE_*_HANDOFF.md`
- only the repository files and tests directly relevant to the next approved task

Then:
1. Summarize current project status in 10 bullets or fewer.
2. Identify the next unselected phase, but do not select or start it.
3. Ask me to approve one narrow objective before any code changes.
4. After approval, give concise one-step-at-a-time Git guidance.
5. Keep responses brief and repository-specific.
6. Do not inspect the whole repository unless the approved task requires it.
7. Do not propose work outside approved boundaries, including tax logic changes, UI, charts, API, serialization, CLI, or federal-state integration, unless explicitly authorized.
