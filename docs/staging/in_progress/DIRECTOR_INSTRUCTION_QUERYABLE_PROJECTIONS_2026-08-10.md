> **[IN PROGRESS — steps 1-2 of 3 DONE, 2026-08-11]** Parked here, not archived, because sub-item 3
> of WORK THIS CREATES is genuinely still open. Do not re-mint.
>
> - **1. Atom(s) minted — DONE** (`79c3ecd2e`): `G12_queryable_projections` (the store) and
>   `G13_projection_consumers` (the proof-of-caller), lane `G_data_learning`, epoch 2, both
>   `loop_stage: build`. G12 is drawable NOW (no `blocked_on`, no `depends_on`); G13 depends on G12.
> - **2. v1 built — DONE** (`400414f02`, level 0→2, `loop_stage: harden`). `tools/build_projections.py`
>   rebuilds `docs/observability/projections.sqlite` (gitignored) from four COMMITTED artefacts via
>   `git cat-file blob HEAD:<path>`: 403 rows from 4 sources in 0.32s, 26 tests, R15 both ways on
>   rebuild-not-mutate, fail-closed, and envelope-is-read. Record and residuals:
>   `docs/design/simplifications/G12_queryable_projections.yaml`.
> - **3. Proof-of-caller — OPEN**, behind G12 by design (`depends_on`). Now DRAWABLE: G12's
>   dependency is satisfied. This is the sub-item that keeps this file parked, and the one that
>   makes the store more than a design with no caller.
>
> **The anchor discrepancy is RESOLVED (2026-08-11), narrow branch taken.** The cited
> `DATA_LAKE_OBSERVABILITY.md` has never existed in this repo, so this instruction's own text is
> the anchor of record. Of the two forks the mint named, G12 took the second: scope stays INTERNAL
> queryability, `SAAS_COVERAGE_MAP.md:71` is left true as written, and its published 22.7% figure
> does not move — nothing in the store feeds a published figure or a site surface. G13 must hold
> that line: a site page reading the store is still not board-grade analytics via a warehouse, but
> if it ever becomes that, the row moves deliberately and the percentage with it. Evidence:
> `docs/staging/WORKER_FINDING_A_MINT_SOURCES_CITED_DESIGN_ANCHOR_HAS_NEVER_EXISTED_2026-08-11.md`.

