# [WORKER FINDING] The publish path swallowed 199 generator crashes and served a frozen artefact for four days

**Severity:** BLOCKING · **Lane:** H_harness
**Found:** 2026-08-17 worker tick, at BUILD on `W2_17_dual_fuel_leg_clv_attribution` (not in the finding that minted it)
**Subject:** `background/process_run_complete.py` (the per-generator `except Exception: log(...)` blocks), `tools/generate_customer_sample.py:226-229`
**Discharged:** 2026-08-17 worker tick — `tests/tools/test_generate_customer_sample.py::test_a_null_clv_does_not_crash_the_generator`, `tests/tools/test_generate_customer_sample.py::test_a_null_clv_publishes_null_and_never_the_number_zero`, `tests/background/test_publish_step_ledger.py::test_a_step_that_raises_is_recorded_as_not_refreshed`, `tests/background/test_publish_step_ledger.py::test_a_missing_ledger_raises`, `tests/background/test_publish_step_ledger.py::test_the_five_evidenced_failures_are_all_covered`, `background/publish_step_ledger.py`. Closure items 1 and 3 are LIVE and each was mutation-proven at this HEAD by RUNNING the named falsifier, not by reading a commit — five injected mutations, five reds, tabulated in "How this was discharged" at the foot of this document. Closure item 2 (a control asserting its subject's production stamp) is DELEGATED, not done: the hook it needs is assert_fresh in the module named above, and retro-fitting the existing controls to call it belongs to the sibling finding that owns that subject, `docs/staging/WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15.md`.

## What was found

`process_run_complete.py` wraps each site-data generator in its own
`try / except Exception` and, on failure, calls `log()` and continues:

```python
    try:
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    except Exception as exc:
        log("Customer data generation failed: {}".format(exc))
```

No alarm, no NTFY, no gate, no non-zero exit — and, critically, **no removal of the
artefact the failed step was supposed to refresh**. The previous run's output stays on
the publish path and keeps being served.

`observed-with-evidence` — counted from `docs/observability/sim-runner-log.md`:

| step | total failures logged | `__round__` crashes | first `__round__` crash |
|---|---|---|---|
| Customer data generation | 130 | **99** | 2026-08-13 21:53 UTC |
| Customer sample generation | 131 | **100** | 2026-08-13 21:53 UTC |
| Billing ledger generation | 32 | 0 | — |
| Live portfolio generation | 31 | 0 | — |
| Invoice data generation | 31 | 0 | — |

199 crashes of one shape, on every publish, from 2026-08-13 21:53 to 2026-08-17 10:41 —
**a little under four days**. `site/data/customers/*.json` was last actually written by
the publish path at commit `528c2559e` (2026-08-13 19:21), 2h32m before the first crash.
Everything the customer pages served after that was that frozen snapshot.

## Why nobody saw it

The staleness was invisible from every direction that normally catches it:

* **The artefact existed and parsed.** `_retire_departed_artefacts` only removes accounts
  absent from a run that SUCCEEDED, so a crashed run retires nothing and disturbs nothing.
* **The figures were plausible.** The frozen snapshot carried a full lifetime-value book
  (C1 `clv_gbp` 2840.5, C_IC3 3137524.98). A blank page gets noticed; a stale-but-complete
  one does not.
* **The controls read the frozen file and were satisfied by it.**
  `site/customers/test_wall_exhibit.py`'s vacuity guard asserted the closed household
  carried live forward-looking figures — and it did, because it was reading the 2026-08-13
  snapshot. The control was green *because* publishing was broken. It went red the moment
  the generator was fixed and wrote the current run's real values.
* **R2's shape, on a document.** The fix that produced the crash (`build_clv` returning
  `clv_gbp: null` for accounts no longer supplied) was committed and green; it simply never
  reached the artefact, and nothing checks that it did.

## Root cause of the crash itself

`round(clv_data.get("clv_gbp", 0), 2)` — the `.get(k, 0)` default handles a MISSING key but
not a key PRESENT AND NULL. Once `build_clv` began recording `clv_gbp: null` for the five
no-longer-supplied accounts (C1, C3, C4, C5, C6 — all `still_supplied: false`, which is
correct behaviour), every publish raised `TypeError: type NoneType doesn't define
__round__ method`.

The `generate_customer_data.py` half is **fixed and landed** by `W2_17` in this same
commit. **`tools/generate_customer_sample.py:226-229` carries the identical defect and is
NOT fixed** — it is outside `W2_17`'s `file_scope`, and it is still crashing on every
publish (100 of the 199). Registered here rather than fixed on sight, per
SELF_INTERRUPT_DISCIPLINE.

## Why this is BLOCKING and not LATENT

The damage is not hypothetical and not internal: `poesys.net` served four days of
per-customer figures that the company's own current run does not produce, under a
present-day data stamp. That is the R11 defect (the published value is not the computed
value) reached through a channel R11's own checks cannot see, because they verify the
rendered value against the published FILE and the file was internally consistent.

The class is wider than these two generators. Nine `except Exception: log(...)` blocks sit
on the publish path; each one converts a publish failure into a silently frozen artefact,
and four of them have fired for other reasons (32 + 31 + 31 + 1 + 1 times).

## What would close it (R10 — the class, not the instance)

1. A publish step that fails must make its own staleness **visible**, not just logged: the
   step's artefacts fail their freshness assertion, or the publish is marked degraded and
   NTFYs on the state transition (R5).
2. A control that reads a published artefact must assert that artefact's **production
   stamp is from the current run** — otherwise, as here, the control's subject is a file
   the publish path stopped maintaining. (Overlaps
   `WORKER_FINDING_THE_PUBLISHED_ARTEFACT_CARRIES_NO_PRODUCTION_STAMP_2026-08-15`.)
3. The `.get(k, 0)`-on-a-nullable-field shape should be swept repo-wide, not patched twice:
   `_round_or_none` in `tools/generate_customer_data.py` is the landed form.

R15 note: the control that *should* have caught this (the wall-exhibit vacuity guard) was
not merely absent — it was **actively green on the frozen file**. A control whose subject
is an artefact that stopped being written passes forever. That is killer pattern 3
(fail-silent) reached through the subject rather than through the checker.

---

## How this was discharged (2026-08-17 worker tick)

Everything below is `observed-with-evidence` (R9): every claim is a command that was run at
this HEAD and the output it produced.

### The instance was still live when this tick opened

`docs/observability/sim-runner-log.md` — the customer-DATA half stopped failing after W2_17
landed (last failure 2026-08-15 17:43 UTC); the SAMPLE half was still crashing on the most
recent publish:

    - [2026-08-17 09:41 UTC] [process_run] Customer sample generation failed:
      type NoneType doesn't define __round__ method

Reproduced directly, before touching anything:

    python3 -c "from tools.generate_customer_sample import generate; generate()"
    -> TypeError: type NoneType doesn't define __round__ method
       tools/generate_customer_sample.py:226

The source book confirms the population it fires on — 5 of 13 billing accounts carry
`clv_gbp: null` and `expected_lifetime_periods: null` in `docs/reports/run_output_latest.json`.

### Closure item 3 — the shape is now landed ONCE, not patched twice

`tools/generate_customer_sample.py` now **imports** `_round_or_none` from
`tools/generate_customer_data.py` rather than re-declaring it, and applies it to the three
forward-looking billing-account fields. The generator runs (19 customers written) and
`site/data/customer_sample.json` now carries `clv_gbp: null` for C1 rather than a stale 2840.5.

**One correction to that last sentence, because the credit is not mine and the difference
matters.** The regeneration above ran at 10:23:43 UTC and left the fixed artefact
UNCOMMITTED in the shared working tree; three minutes later a concurrent lane's publish
commit `1ffe5e219` swept it in. So the artefact was already unfrozen at HEAD before this
tick committed anything, and `git log -1 -- site/data/customer_sample.json` credits that
commit, not this one. Two things follow, and both are the point rather than a footnote:

* The four-day freeze ended as a DATA change carried by an unrelated commit while the CODE
  that froze it was still crashing. That is the `uncommitted_and_orphaned_work` shape, and
  it is why an artefact being correct at HEAD proves nothing about the generator: the very
  next publish on the unfixed code would have re-frozen it, silently, exactly as before.
* It is also a live instance of CLAUDE.md's concurrent-writers hazard on this one tree — an
  uncommitted file belonging to one lane landing inside another lane's pathspec.

The repo-wide sweep the finding asked for was RUN, not assumed. Census of
`round(<x>.get("<field>", 0), n)` over `tools/ background/ saas/ company/`: 53 sites across 6
files, of which **the two named in this finding were the only ones reading a field that can be
null**. There is no third crash site. Narrow census of every Python read of `clv_gbp` /
`latest_churn_probability` / `expected_lifetime_periods` / `avg_annual_net_margin_gbp`
confirms it: the remaining readers either pass None through (`generate_company_data.py`) or
already guard it (`generate_shadow_html.py`, whose `_gbp`/`_pct` render None as an em-dash).

**What the sweep DID surface, filed rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE):**
seven `or 0` / `or 0.0` sites in `saas/reporting/annual_report.py` (lines 8217-8242) fold a
null CLV into a published median, percentile and sum as the number **0**. That does not crash
— it is the mirror half of this same defect, and it moves a published distribution. Registered
as its own finding rather than swept in here, because it belongs to the
`measurements_that_mirror` class and to a different lane's subject.

### Closure item 1 — a failed publish step now makes its own staleness visible

`background/publish_step_ledger.py` (new). The swallow STAYS — one dead generator must not
cost the other twenty their publish, which is what the bare `except` was reaching for and was
right about. What goes is the silence. Each converted step records whether it refreshed its
named artefacts, and the cycle publishes `site/data/publish_steps.json` carrying
`degraded`, `stale_artefacts`, and per step the run stamp it was **last** real at (carried
forward across cycles, so "stale" can say *since when* instead of being a mood). The
clean↔degraded transition NTFYs exactly once in each direction with the failing step names and
their exceptions as payload (R5).

Wired into `generate_dashboard_json` for eleven steps, including **all five that the evidence
table above proves actually fired**. The remaining ~20 steps further down that function still
carry the bare `except` and are NOT yet converted — stated here rather than left implied,
because a silent cap reads as full coverage, which is this document's own subject. They are
the same mechanical conversion; the ledger takes them without change.

No new commit-list wiring was needed: the `site/data/*.json` glob at
`background/process_run_complete.py` already commits any new generated data file, which is the
2026-07-16 R10 class-closure doing its job.

### R15 — every control here was proven able to fail

Four mutations were injected at this HEAD and the suite re-run each time; each reddened its
intended control and was then reverted (suite green again at 19/19 and 15/15):

| # | mutation | result |
|---|---|---|
| 1 | the swallow records `ok=True` on exception (i.e. the original defect, exactly) | **9 failed** |
| 2 | `read_ledger` returns `{"steps": [], "degraded": False}` instead of raising on a missing file (FAIL-OPEN) | **1 failed** — `test_a_missing_ledger_raises` |
| 3 | the `was_degraded == now_degraded` guard removed (R5, alert every cycle) | **1 failed** — `test_an_unchanged_status_never_repeats` |
| 4 | the sample step's wiring reverted to the bare `try/except` | **2 failed** — both `TestWiredIntoThePublishPath` tests |
| 5 | `_round_or_none` reverted to `round(clv_data.get("clv_gbp", 0), 2)` | **2 failed** in `tests/tools/test_generate_customer_sample.py` |

Mutation 5 is the one that matters most to this finding's own argument: **before this tick,
that mutation was the live state of the tree and the whole existing suite was green on it.**
No test in `tests/tools/test_generate_customer_sample.py` put a populated
`by_billing_account` in front of the generator — every fixture passed `{}` — so the null case
that crashed 100 publishes had no falsifier at all. It has three now, and the third asserts
the *other* direction (a populated CLV must still round), so the fix cannot be "return None
always".

### The R15 note in the original finding is upheld and worth repeating

The control that should have caught this was not absent; it was **green because publishing was
broken**, and went red the moment the generator was fixed. `assert_fresh()` exists so a control
can refuse to be satisfied by a file the publish path stopped maintaining — including refusing
for an artefact no step claims to write at all, since unmeasured must not read as fine. That is
the hook; pointing the existing controls at it is closure item 2, delegated above.
