**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Add two lint rule families, bug patterns and timezone-naive dates, under the existing ratchet

**Type:** STEER, through the advisor channel. Finish what you're doing first, then take this next. It is a small backlog item, ranked in Friday's balance review.

## The director's words (chat, Thu 19 Nov, verbatim)

- 14:03: "Do we or should we have lint rules"
- 14:09: "On the lint? Add the 2 you suggested"

The two the advisor suggested, from a quick count with a newer ruff (0.16.9) than the pinned one, so the figures are rough:

1. **Bug patterns (flake8-bugbear, ruff `B`).** Rules that catch real defects, not style. Examples: a loop variable captured late in a closure (about 65 hits), mutable default arguments, `raise` inside `except` without `from`, and `zip` without `strict`.
2. **Timezone-naive dates (ruff `DTZ`).** Settlement turns on BST and GMT, and this project has had clock-change defects. A naive `datetime` is a defect class, not a style point.

## The problem (the machine owns the design)

- **New code only, through the existing ratchet** (`tests/architecture/test_static_quality_ratchet.py`): no new violations in a changed file, and a shrink-only baseline. No mass clean-up and no bulk `--fix` sweep across lanes.
- **Choose the rules inside each family.** Leave out any that are noise for this codebase, and say why in a line each. Example: `B905` (`zip` strict) has hundreds of hits and may be worth it only where lengths can genuinely differ.
- **The baseline is per ruff version.** Add the families at the pinned version (`requirements.txt`: 0.15.16), and re-freeze the baseline in the same commit.
- **Check whether existing hits are live defects.** The late-binding closures especially: some may already be producing wrong results. Any that change money or a customer outcome are a serious class under the correctness rule. Fix them as a class, not one by one.
- **Do not add style families** (magic numbers, too-many-arguments and the like). The constant-origin test already does the magic-number job better.

## Risk

- **Touches:** `ruff.toml` and the ratchet's frozen baseline.
- **Blast radius:** every lane's commits, through the ratchet.
- **Probable failure mode:** a baseline frozen wrongly, or at the wrong version, reds every lane and names files nobody touched.
- **Mitigation, inline:** freeze and land in one commit at the pinned version. Run the ratchet on a clean worktree of origin before landing. Reverse by reverting the two `select` entries and the baseline.

**Proportionality:** reversible and narrow, so just do it.

## Done

*Delivery seat, 19 Nov 2026.* Both families are now in `ruff.toml` under the existing ratchet, at
the pinned ruff 0.15.16. There was no clean-up and no `--fix`.

**Rules taken: all of B and all of DTZ, except the following.** Each has a reason in `ruff.toml`.
- `B905` (`zip` without `strict=`): 558 hits, and the lengths are equal by construction almost
  everywhere.
- `B007` (unused loop variable): a naming hint, not a defect.
- `B009` and `B010` (`getattr`/`setattr` with a constant): style.
- `DTZ001` in `tests/*` only: 305 of the repo's 310 hits are test fixtures that build calendar
  datetimes. The clock decision is made in the code under test, and that stays covered. `DTZ011`
  (`date.today()`) stays live in tests too, because a test that reads the wall clock passes today
  and fails next year.

**Baseline.** Fourteen new codes, 285 hits in all, were added to `RUFF_BASELINE` as a ceiling.
They were counted on an `origin/main` worktree at 024206bfb, and the shared working tree read the
same counts. The mutation proof that used B008 as a never-natural code now uses `PLR2004`, a
style family deliberately left out. Ratchet results:
- On the origin worktree: 13 passed.
- Mutation check: a new file carrying `def f(x=[])` and `date.today()` reds
  `test_no_changed_file_gains_a_ruff_violation` (B006 0->1, DTZ011 0->1) and the ceiling test.

**Live defects: none that change money or a customer outcome today.** No finding is filed.
- **B023 (late-binding closures, 65 hits).** company/ and saas/ have none. In simulation/:
  - `arrears_engine.py` (14 hits) and `run_phase2b.py` (3 hits): the helpers are defined and
    called within the same loop iteration.
  - `population_draw.py` (2 hits): `_claim_in_year` does escape its iteration through
    `functools.partial`, but its stock and slot are bound as arguments. The late-bound `year`
    and `n` appear only in the text of an error message.
  - The other 46 hits are in tools/, background/ and tests/.
- **DTZ in company/, saas/ and simulation/ (17 hits).**
  - The ones that matter are the ten `date.today()` fallbacks. Each would age a 2016-2025 book
    against the 2026 calendar if a caller left out `as_of`:
    - `collections.py` (2), `contract.py` (2), `switching_recommendation.py`
    - `direct_debit.set_mandate`, `invoice.record_payment`'s `recorded_at`
    - `retention_risk.py`, `service_log.complaint_deadlines`
    - `resentment_ledger.is_at_churn_risk`
  - None is reached from a run. Every non-test caller either passes the simulation date
    (`generate_shadow_html` passes the journey's own date) or does not exist (`is_at_churn_risk`,
    `get_collections_queue`, `switching_recommendation` and `set_mandate` have no production
    caller).
  - The rest are calendar arithmetic, where naive time is harmless, plus two `datetime.min`
    fail-closed sentinels in `recorded_sim_interface.py`.
  - The class is latent. DTZ011 under the ratchet now refuses a new instance in any changed file.

**To reverse:** revert the `select`/`ignore`/per-file lines in `ruff.toml` and the fourteen
baseline entries.

Decision: none -- the families were the advisor's suggestion, not a machine recommendation
