# [DIRECTOR-INSTRUCTION] — Mint queryable projections; the July design finally gets its caller (2026-08-10)

**Type:** [INSTRUCTION — mint, then draw on normal priority after BUILD_THE_BREATHING lands]. The director asked "is this staged, or in a lane?" — the audit answer: no atom exists anywhere on the 250-atom map, while the full design has sat in canon since July: docs (project) DATA_LAKE_OBSERVABILITY.md — "the data can't be queried, filtered, visualised, or explored… a real company would have a data warehouse." A design with no caller, at architecture scale; this instruction is the caller.

**Mint (G_data_learning; ids the registry's):** *queryable projections* — a query store derived from committed truth (run outputs, the event spine, observability ledgers), rebuilt-not-mutated each publish so it can never disagree with its sources for long, and never a second source of truth. v1 scope judged by the worker (the July doc's four layers are the anchor, not a contract; a single-file query database is fine); the AO12 10k probe's measurements set its scale ceiling and graduation trigger (Postgres at product-time stays ruled). Explicit boundary: this is INTERNAL queryability — the external-dataset anchor philosophy (EPC, census as cited artefacts, not ingested lakes) is untouched.

**Three consumers, by design:** (1) the site's derived pages read projections instead of hand-refreshed files — deleting a whole subclass of the derived-artefact-staleness wedge disease; (2) the advisor's lab and the director's exploration get SQL-shaped access to the company's own truth; (3) future dashboards per the July doc's upper layers, drawn in course.

## WORK THIS CREATES (canonical, in-document)
1. The atom(s) minted with the July doc cited as design anchor. 2. v1 built: projections derived, rebuilt per publish, queryable from the repo. 3. At least one site page and one lab query consuming it, as the proof-of-caller.

— Directed 2026-08-10 via the advisor; sequenced behind the breathing, ahead of comfort.
