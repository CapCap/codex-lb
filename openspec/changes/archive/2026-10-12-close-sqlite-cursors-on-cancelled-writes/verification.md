# Verification

## Completeness and correctness

- Connection factory covers the existing shared file-backed engine kwargs; actual main and background construction paths are exercised by cancellation regressions.
- Both new scenarios are covered: retained cancellation tracebacks and real terminal transcript timeout persistence (rows_v1 and chunks_v2). Uncommitted inserts disappear, independent writes succeed, settlement fences late appends, and scheduler leader acquisition succeeds.
- Negative controls on current main: removing only the connection factory makes all four lock regressions fail with `database is locked` (main engine, background engine, rows_v1 terminal spool, chunks_v2 terminal spool). No forced garbage collection is used in passing tests.
- 160 focused tests passed: DB session, leader election, connection regression, event batcher, and terminal timeout integration.
- All five new cases also passed under uvloop on SQLAlchemy 2.0.52 and 2.1.4; the event batcher suite passed on 2.1.4 as well.
- `make lint` and `make typecheck` passed in the isolated PR worktree on main `f8ffbac2099a113fba54dfd8d77774f5bca80ffa` with frozen dependencies. All five new cases also passed on Python 3.13.11 with uvloop.
- Proxy architecture, cancellation safety, timing seam, and migration topology checks passed. No Alembic revisions were added.
- Strict change validation passed. All 67 main specs passed normal validation. The installed OpenSpec 1.14.1 reports existing long-requirement warnings in main specs; strict global validation treats those warnings as failures. Existing requirements were not rewritten for this incident fix.

## Coherence

Implementation follows the design: weak cursor tracking, native finalization on the aiosqlite worker, original cancellation propagation, no dependency or schema changes. Cursor close and connection close are idempotent; normal commit/rollback and weak lifetime semantics are covered. Both spec scenarios map to regression tests without mocking the durable repository writes.

## Package smoke test

A wheel built from the patch was loaded through isolated uvx with frozen dependencies. Its cancellation regression passed under uvloop with SQLAlchemy 2.0.52, and the dashboard plus all 17 index-referenced assets returned HTTP 200. This validates the packaged code; it does not substitute for production observation.

## Limits

The exact cursor held in the incident process was not inspected. The tests prove a reachable persistent writer-lock leak and its repair, not the cause of every historical stall in #1682. Sustained production recovery remains to be observed. No new migration or live database repair is part of this patch.
