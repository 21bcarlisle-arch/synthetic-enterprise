**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/provenance state, not domain understanding.

# The 09-10 pair move is landed, and the only three controls it reddened were all keyed to yesterday's artefact

Closes the Lane 0 item *"pair-move the 20260910 run and its floor"*
(claim `pair-move-20260910-after-the-floor-lands`), open across four turns because the floor did
not exist.

---

## 1. The premise was LIVE, and the floor had arrived

Re-measured at the start of this turn, as the item instructs. Both halves checked, because
"the premise is spent" and "the blocker has cleared" look identical from the claim store:

| | state |
|---|---|
| worktree vs `origin/main` | `rev-list --count HEAD..origin/main` = **0** — on the tip, `dfcb46996` |
| canonical `…_three_arm.json` | md5 `bd0936be…`-**not**; it was `0c478778…`, i.e. still the **09-09c** run |
| canonical `…_noise_floor.json` | still `24da1d28…`, the **09-09b** floor |
| the floor the item waits on | **PRESENT**, `…_noise_floor_20260910.json`, 8,638 bytes, `generated_at 2026-09-10T23:03:18Z` |
| its producer | **gone** — no `run_value_cycle_ab` process alive |

So: nothing had landed by another route, and the thing three previous turns were blocked on was on
disk. The prior turn's estimate of ~23:05Z was right to within two minutes — the first of the four
arrival estimates on this run that did not have to be revised.

**Completeness was checked rather than assumed**: 9 seed rows, `11111…99999`, the same seed family
as the floor it replaces, and `world_identity.digest 39a192ce04c1eda8` — the same world as the run
it bounds. The rival `…_20260910b.json` floor was NOT used, per the item.

## 2. What landed

The four paths of the item, in one commit, from a worktree on `origin/main`, plus the three control
repairs section 4 explains:

- `docs/observability/value_cycle_ab_s1_noise_floor_20260910.json` (the dated floor, newly tracked)
- `docs/observability/value_cycle_ab_s1_noise_floor.json` (canonical ← the dated floor)
- `docs/observability/value_cycle_ab_s1_three_arm.json` (canonical ← the dated 09-10 run)
- `site/data/value_arms.json` (regenerated)
- `tests/tools/test_generate_value_arms_data.py` (three controls re-keyed)

Every copy was checksummed against its source before the generator ran.

## 3. What the page gained, and the one thing it LOST

The gains are the ones the item and its pre-registration predicted, and they are graded in
`docs/staging/records/SEAT_PREREG_WHAT_THE_REAL_20260910_FLOORS_ROWS_MOVE_ON_THE_PAGE_2026-09-11.md`
— six of seven predictions held, one refuted. Headline: `contrast_bounds` restored to 7 keys and 3
contrasts on the new run, both `is_it_available_today` flags `false` → `true`, `staleness_caveat`
still clear.

**One gain nobody asked for.** `floor_admission.rule` moved `stamp_proxy` → **`declared_book`**, and
`contrast_bounds.admitted_by` with it. The 09-10 floor is the **first floor on disk to carry a
`book_identity` block**, so the bound under every directional claim on that page stops being
admitted by *two timestamps standing in for the question* and starts being admitted on the book
itself. `run_value_cycle_ab.floor_book_identity` has had a reader for days and no artefact to read;
now it has one.

**And one real LOSS, which the item does not mention and I did not predict.**
`departure_term_rerun.objective_difference.established` went **`true` → `false`**.

The block compares a baseline run against a re-run whose renewal objective was changed to price
departures, and its baseline pointer *is* `THREE_ARM_PATH`. Moving that pointer moved the baseline
onto `9cf9d16ed` — a tree that **already prices departures**. So the pair stopped being a
one-thing-changed experiment, and the producer says so in its own words:

> The two trees could not be shown to differ in the objective: the baseline tree reads True and the
> re-run's reads True. Nothing below is stated as an effect OF the departure term.

**The producer failed closed exactly as designed**, on a conjunction whose source comment
anticipates this case verbatim: *"`rerun_pays` alone would call a pair of runs a departure
experiment whenever the LATER tree happens to have the term, including when the earlier one had it
too"*. Nothing is published falsely. But the page **has** lost a comparison it was making
yesterday, and that is the honest price of the move rather than a defect in it: a bound restored on
three contrasts, against a departure-term effect withdrawn. **Recording it because the item's own
framing — "a pure DATA move" — is what makes a loss like this easy to land without noticing.** The
route back is a departure-term re-run drawn from a pre-departure tree, and that is a run, not a
repair.

## 4. THE FINDING: all three reds were controls that go red when their subject gets MORE honest

Three tests failed after the move. **All three passed in a clean extract at `HEAD`**, so all three
were caused by the pair move — checked rather than assumed, because "pre-existing at HEAD" is the
flattering answer and it was not the true one here. None of the three was a defect in the data.

| control | what it borrowed | why the move broke it |
|---|---|---|
| `test_EVERY_admission_outcome_IS_REACHABLE_…` | `_load(NOISE_FLOOR)` as its **stamp-proxy** witness | worked only because no floor on disk carried a book. The new one does, so the witness silently moved onto the declared-book branch |
| `test_a_leg_whose_own_redraws_straddle_zero_…` | that the live draw is **positive** while its family's centre is negative | the canonical selection leg moved +£319 → −£333, onto the SAME side as its centre, so the conditional centre clause correctly fell silent |
| `test_the_objective_difference_is_read_from_the_TREES_…` | `THREE_ARM`'s producing commit as its **no-departure** poison witness | the new run was drawn at a tree that prices departures, so the poison round evaporated |

**One shape, three doors.** Each control had keyed a witness to *an accidental property of whichever
artefact was canonical that week*, and each went red at the moment its subject improved: a floor
that finally declares its book, a page whose published draw finally agrees with its own family's
centre, a run drawn from a better objective. CLAUDE.md's *"key a control to the property, not to
today's answer"* names this, and *"a control pinned to the current state goes red when the code
becomes more honest and stays green when the claim rots"* is exactly what happened — **three times
in one commit, through three different doors**, which is the same way the guard-branch trap was
learned.

The repairs give each branch a witness constructed from the property it stands for:
`_floor_without_a_book()` for the proxy branch; a computed **biconditional** (the centre clause is
present exactly when the draw and the centre straddle zero) plus a reflected-draw witness so the
firing branch stays reachable; and a **named immutable commit** for the poison round, with the
poison precondition still asserted so a witness that stops being poisonous fails loudly.

**All five mutations fire** — clause composed unconditionally; clause never composed;
`_objective_pays_for_departures` always `True`; `_floor_admission` never reaching the proxy branch;
and `_floor_without_a_book` returning a book-carrying floor. That last one was run specifically to
answer whether the new witness is load-bearing or merely redundant beside the disagreeing-arms
witness (CLAUDE.md: *a mutation that does not fire is either a missing test or an equivalence —
establish which*). **It fires: the witness is doing work.**

One docstring was carrying a claim that the move falsified —`_floor_declaring` opened with *"No
floor on disk carries a book identity yet — every one of them predates the writer"*. Corrected in
place beside the prediction it was making, which held.

**Suites green:** 401 passed, 1 skipped across
`site/test_the_baseline_comparison_reaches_the_reader.py`,
`tests/tools/test_generate_value_arms_data.py`, `tests/tools/test_value_cycle_ab_noise_floor.py`.

## 5. What is next

- **The departure-term comparison is withdrawn until a re-run is drawn from a pre-departure tree.**
  That is a run, and it is the one piece of this item's subject that landing could not restore.
- `error_bar.distinguishable_from_zero` is now `true` and **renders in no sentence**. The feed
  publishes it, no HTML or JS reads it. Either it should reach the reader or it should not be in
  the payload; today it is a fact with no consumer.
