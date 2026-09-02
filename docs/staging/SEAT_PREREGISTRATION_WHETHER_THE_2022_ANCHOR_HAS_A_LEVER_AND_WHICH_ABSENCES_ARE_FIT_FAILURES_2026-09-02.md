**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — does the 2022 level anchor have a lever, and are the three absent years absent for the same reason?

**Filed 2026-09-02, delivery seat, Lane 0, in the isolated worktree `/var/tmp/se-seat-executor`, at
`b6a0701e6`. Written and landed BEFORE running any of the measurements below and before reading any
of their output.** The collision this decides is
`docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` and the CORRECTION appended to
`docs/staging/done/WORKER_FINDING_THE_LEVEL_ANCHOR_GUARD_IS_GREEN_AT_HEAD_AND_RED_IN_THE_TREE_THE_WORLD_ACTUALLY_RUNS_FROM_2026-09-01.md`.

## Why this is pre-registered rather than just run

The collision — *does an in-record year the whole-book fit cannot identify REFUSE or FALL BACK?* —
has been posed as a binary for three orientations. I believe the binary is malformed and that the
three absent years are absent for three different reasons. **That belief flatters the answer I am
about to give**, so the discriminating measurements are written down first, with the move each one
must show, and each is graded beside this text afterwards whether it goes my way or not.

## What is already DERIVED and is therefore not a prediction

These are read off committed code, not measured, and I state them so that nothing below gets credit
for "predicting" them:

* `simulation/renewal_engagement.py:62` — `CRISIS_PASSIVE_YEARS = frozenset({"2022"})`, and
  `rolls_active_renewal` returns `False` unconditionally for a 2022 term start.
* `simulation/departure_risks.py:408` — `CAUSE_SVT_INERTIA: _clip_hazard(svt_inertia * action_propensity)`.
  `level_anchor` is **not** on that line, while it *is* on the three renewal-route hazard lines
  (`:338`, `:344`, `:352`).
* `simulation/departure_level_anchor.py` at HEAD holds all ten record years, and
  `_published_departure_rates()` is exactly 2016–2025 — so **HEAD's fail-closed refusal branch is
  structurally unreachable**: the set difference is empty. Measured this orientation, not assumed.

From those three, the 2022 no-lever claim *follows*. The predictions below are what could refute the
derivation.

## Predictions, each with the move it must show

**P1 — the positive control, and it is the null rung this ladder needs.** Sweeping
`YEAR_LEVEL_ANCHOR[2020]` from 0.1x to 10x its fitted value and rebuilding hazards for a 2020
renewal-route term start **moves** the summed renewal-route departure hazard, monotonically
increasing, by **at least a factor of 20** across that sweep. *Refuted by:* any move smaller than
2x, or a non-monotone response. If P1 is refuted the apparatus is broken and P2 says nothing.

**P2 — the subject.** The same sweep on `YEAR_LEVEL_ANCHOR[2022]`, for a 2022 term start routed by
the world's own `rolls_active_renewal`, moves the realised 2022 departure probability by **exactly
zero** (|Δ| < 1e-12). *Refuted by:* any nonzero move. **I am predicting a null and I am naming in
advance why that is not an unfalsifiable prediction: P1 is the same apparatus on a year where the
move must appear.** A null in P2 with a null in P1 is a broken harness, not a result.

**P3 — c3's 2022 rows are not a counter-example, they are a pre-C1b artefact.**
`docs/reports/c3_shown_price_departure_factors.json` carries 2022 rows (the CORRECTION says 53).
I predict those rows carry `departure_cause` values drawn from the **renewal-route** causes and
**none** from `svt_inertia`, and that their `sim_level_anchor` is `1.524110` (the ten-year block's
2022 entry) rather than `3.053619`. That would establish they were captured before C1b routed the
crisis year to the SVT table — i.e. the capture, not the world, is what carries 2022 renewal
decisions. *Refuted by:* any `svt_inertia` cause among them, or a `sim_level_anchor` of `3.053619`,
either of which would mean c3 is post-C1b and the no-lever claim is capture-scoped after all —
**which is the answer that would sink my proposed disposition and I would report it.**

**P4 — `population_anchor` publishes a measured zero and its own insufficiency flag cannot see it.**
Calling `tools/population_anchor._crisis_churn_direction` with a `churn_by_year` that omits 2022
entirely returns `2022_sim_rate_pct == 0.0` with `insufficient_data == False` and
`absolute_diverges == False`. *Refuted by:* `insufficient_data` coming back `True`, which would mean
the fail-open is already disclosed and only the published field needs repair. **Predicted move after
the repair:** `2022_sim_rate_pct` becomes `None` and `insufficient_data` becomes `True` on the same
input — a change in the verdict, not only in the label.

## The constraint this run must not violate

**No constant is pasted, edited or deleted in `YEAR_LEVEL_ANCHOR` by the measurement itself.** Every
sweep above is done by `monkeypatch`/local dict in a scratch process, never by writing the module.
This is discharged by **reading the artefact** — `git status --porcelain simulation/departure_level_anchor.py`
pasted into the grading — and not by recalling my own behaviour, per the catalogued class.

## What I will decide on the answers

* P1 holds and P2 shows zero, and P3 holds ⇒ 2022's absence is **not** a fit failure the anchor can
  repair, and refusing it crashes the run over a value that provably cannot change the run. The
  disposition becomes three-way, keyed to *why* the year is absent, not *whether* it is.
* P2 shows any nonzero move ⇒ 2022 **does** have a lever, the whole-book fit's refusal is a fit
  failure after all, and refusing is the right answer. I would drop the three-way proposal.
* P3 refuted ⇒ the no-lever claim is capture-scoped, and the honest answer is that **neither table
  can be justified until a re-capture runs**, which I would file as the result.
