# Week 8 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Eason** \
This assignment took me about **TODO** hours to do.

## Task 1: Add more endpoints and validations

a. Links to relevant commits/issues
> PR: [#6](https://github.com/Eason1114/week8/pull/6) (branch `task1-endpoints-validation`)
> Commits: [6677fb0](https://github.com/Eason1114/week8/commit/6677fb0) "Add DELETE/GET endpoints and tighten input validation", [547e890](https://github.com/Eason1114/week8/commit/547e890) "Ignore backend/.DS_Store as well"

b. PR Description
> `notes`/`action-items` had inconsistent CRUD coverage (no DELETE, no GET-by-id for action items) and weak validation: empty-string fields were accepted, `title` had no length cap despite the DB column being `String(200)`, PATCH silently no-op'd on an empty payload, and the `sort` query param used `hasattr(Model, field)`, which allows sorting on any attribute name on the SQLAlchemy model (not just real columns) and can 500 on a bad-but-plausible value.
>
> Added `DELETE /notes/{id}`, `GET /action-items/{id}`, and `DELETE /action-items/{id}` for CRUD symmetry; added Pydantic `Field` constraints (non-empty, 200-char title cap); PATCH now returns `400` on an empty update payload; extracted a shared `resolve_sort()` helper backed by an explicit allow-list of real columns per router, so an invalid sort field returns `400` instead of a silent fallback or a 500.
>
> Testing: `PYTHONPATH=. python3 -m pytest -q backend/tests` — 13 passed (7 pre-existing + 6 new, covering validation errors, PATCH-with-no-fields, GET/DELETE incl. 404s, and invalid vs. valid sort fields). `ruff check backend` clean.

c. Graphite Diamond generated code review
> TODO — run Graphite's AI review on PR #6 (Graphite must be installed/authorized on this repo first — see "Get Started with Graphite" in `assignment.md`) and paste the review comments/summary here.

## Task 2: Extend extraction logic

a. Links to relevant commits/issues
> PR: [#7](https://github.com/Eason1114/week8/pull/7) (branch `task2-extraction-logic`)
> Commit: [a7b61cc](https://github.com/Eason1114/week8/commit/a7b61cc) "Extend action-item extraction with more patterns and metadata"

b. PR Description
> `extract_action_items` only recognized `todo:`/`action:` prefixes and lines ending in `!`, and used `line.strip("- ")`, which strips *any* leading/trailing `-`/space characters rather than just a bullet marker — a latent content-mangling bug.
>
> Added `FIXME:`/`FOLLOW-UP:` keyword recognition (case-insensitive, colon optional), markdown checkbox support (`- [ ] task` / `- [x] task`, with checked-off items excluded from open action items), replaced the buggy strip with a proper bullet/number-marker regex, and added de-duplication. Added `extract_action_items_detailed()`, a dataclass-based variant exposing `keyword`/`urgent`/`already_completed` per item for callers that want more than a flat string list; `extract_action_items()` is now a thin wrapper over it, so existing behavior/signature is unchanged.
>
> Testing: `PYTHONPATH=. python3 -m pytest -q backend/tests` — 9 passed (the original test unmodified, plus 5 new covering keywords, checkboxes, case-insensitivity, dedup, and the detailed-metadata variant). `ruff check` clean.

c. Graphite Diamond generated code review
> TODO — run Graphite's AI review on PR #7 and paste the review comments/summary here.

## Task 3: Try adding a new model and relationships

a. Links to relevant commits/issues
> PR: [#8](https://github.com/Eason1114/week8/pull/8) (branch `task3-tag-model`)
> Commit: [b0e6c3f](https://github.com/Eason1114/week8/commit/b0e6c3f) "Add Tag model with a many-to-many relationship to Note"

b. PR Description
> The app had two unrelated models (`Note`, `ActionItem`) with no relationships between anything.
>
> Added a `Tag` model (id, unique name, timestamps) and a `note_tags` association table for a many-to-many relationship with `Note` (`Note.tags` / `Tag.notes`). Enabled `PRAGMA foreign_keys=ON` on every SQLite connection so the `ON DELETE CASCADE` on `note_tags` is actually enforced (SQLite ignores FK constraints by default). Added `backend/app/routers/tags.py` (CRUD + attach/detach endpoints, duplicate names → `409`, attach/detach idempotent), added `tags` to `NoteRead`, added an optional `?tag=<name>` filter to `GET /notes/`, and updated `data/seed.sql` to stay consistent with the new schema.
>
> Testing: `PYTHONPATH=. python3 -m pytest -q backend/tests` — 10 passed (2 pre-existing + a new `test_tags.py` covering tag CRUD, duplicate-name conflict, empty-name validation, attach/detach incl. idempotency and 404s, and the notes `?tag=` filter). `ruff check` clean.

c. Graphite Diamond generated code review
> TODO — run Graphite's AI review on PR #8 and paste the review comments/summary here.

## Task 4: Improve tests for pagination and sorting

a. Links to relevant commits/issues
> PR: [#9](https://github.com/Eason1114/week8/pull/9) (branch `task4-pagination-sorting-tests`)
> Commit: [1cc057e](https://github.com/Eason1114/week8/commit/1cc057e) "Add real coverage for pagination and sorting"

b. PR Description
> Existing tests passed `skip`/`limit`/`sort` params without ever asserting they changed the result set or its order — a broken pagination or sort implementation would have passed just as well.
>
> Added `backend/tests/test_pagination_and_sorting.py` covering, for both `/notes/` and `/action-items/`: that `sort=<field>`/`-<field>` actually reorders results (scoped to records the test itself created, so it doesn't depend on seed data or run order); that an invalid sort field falls back instead of erroring; that `skip`/`limit` pages partition the full result set with no gaps or duplicates (walking `skip` in `limit`-sized steps and comparing the concatenation to a single unpaginated fetch); that `skip` past the end returns `[]`; that `limit` above the documented cap of 200 returns `422`; and that action items' `completed` filter composes correctly with `sort`.
>
> Testing: `PYTHONPATH=. python3 -m pytest -q backend/tests` — 13 passed (6 pre-existing + 7 new). `ruff check` clean.

c. Graphite Diamond generated code review
> TODO — run Graphite's AI review on PR #9 and paste the review comments/summary here.

## Brief Reflection

a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> TODO — after pasting in the Graphite reviews above, summarize the kinds of issues you (as the human reviewer) flagged across the four PRs — e.g., correctness edge cases (empty checkboxes, ties in sort order, cascade-delete enforcement on SQLite), API shape decisions (409 vs 400, idempotent attach/detach, `exclude_unset` for PATCH), test-coverage gaps, and tradeoffs called out explicitly in each PR description.

b. A comparison of **your** comments vs. **Graphite's** AI-generated comments for each PR.
> TODO — fill in once the Graphite reviews are available. For each PR, note where Graphite's comments overlapped with issues already caught during the manual pass vs. where it raised something new.

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO — cite specific Graphite comments (quote or link them) and say whether each one was a true positive, a false positive/noise, or something your manual review missed.

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> TODO
