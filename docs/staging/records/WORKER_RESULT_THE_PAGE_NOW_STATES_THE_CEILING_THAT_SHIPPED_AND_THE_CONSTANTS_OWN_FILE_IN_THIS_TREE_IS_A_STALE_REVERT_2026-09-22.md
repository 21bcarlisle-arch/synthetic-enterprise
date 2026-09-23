**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the page states the ceiling that actually shipped, and the constant's own file in this tree is a stale revert carrying nothing unique

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-ceilings-downstream-still-fits-a-value-that-never-shipped`.

## 0. The premise, re-measured before the work — and the tree was the thing that was wrong

The item said the downstream was fitted to 1,330 while a live lane was shipping 1,250. Both halves
held, and there was a third fact the item could not have known: **this tree was nine commits behind
`origin/main`, and the value the item told me to go and read had already landed there.**

| oracle | `SETTLEMENT_CUSTOMER_YEAR_BUDGET` |
|---|---|
| `origin/main` (f31e3b1cd) | **1250.0** |
| local `HEAD` before this turn | 1200.0 |
| `simulation/net_new_acquisition.py` **working copy** | 1200.0 |

Merged `origin/main` first (`4902ccbea`, via `surgical_land --merge`), because a downstream
reconciled against a stale base reconciles to the wrong number. Nothing else in the turn was
started until that landed.

## 1. THE FINDING THAT IS NOT ABOUT THE CEILING: the working copy of the constant is a pure stale revert

`simulation/net_new_acquisition.py` has an mtime of 2026-09-21 16:41 and is `M` against HEAD.
**The direction of that diff is the whole point: 7 insertions, 148 deletions.** It does not add work
— it *removes* the landed curve note and reverts the constant to 1200.0.

The item's own thesis flagged this file as untouchable. **This turn establishes the stronger and
more useful fact: it is not untouchable, it is empty.** Every one of the 7 inserted lines is
superseded prose, listed here in full so the next reader does not have to re-derive it:

```
+#: 3. THE SECOND POINT WAS CONTAMINATED AND THE PROBE NOW SAYS SO. A slope needs two clean
+#:    points and there is one, so this number stays where it is until the run specified in §6 of
+#:    that document is taken with the producer stood down. "I cannot yet say" is the result.
+#: takes it; the clean-slope run is `docs/observability/settlement_ceiling_slope_20260829.json`,
+#: deliberately NOT `settlement_ceiling_probe.json`, whose 2,000 row is the contaminated one.
+#: commerce, and that what ceiling the basis supports is not yet known. The zero-requirement
+SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0
```

All seven are the pre-curve era, and `settlement_ceiling_slope_20260829.json` is in **no commit at
all** (checked against both `HEAD` and `origin/main`) — so the paragraph citing it was already the
comparator-artefact failure this repo has met before.

**Why it matters to every lane and not just this one:** any lane that commits that path by bare
pathspec silently reverts the measurement *and* the fifty-nine-line derivation with it, and the
commit will look like a one-line constant change in the subject line. It has been sitting in the
shared tree since 16:41 yesterday.

**Not discarded here, and the reason is a rule rather than caution:** `git checkout <path>` is
forbidden in this repo and there is no sanctioned discard. It did not need discarding for this
turn's work — `surgical_land` gates *the tree the commit would create*, which is HEAD plus the
named paths, so the stale copy was never in the gated tree. **That is the general remedy and it is
worth naming: a stale working copy is harmless to anyone landing through the sanctioned door, and
dangerous only to a bare pathspec commit.**

## 2. What shipped

`tools/generate_book_growth_data.py::engine_bound_basis` was carrying a ceiling of **1,331**
customer-years, fitted from a 3.73 MB/cy secant against the probe's peak RSS. **No constant ever
held it.** Three things were wrong with it at once and only the first was known when the item was
written:

1. **The number was a fit nobody shipped.** The constant went 1200.0 → 1250.0.
2. **The slope was the wrong one of three admissible fits.** The landed derivation takes the
   curve's own clean secant, **4.3402 MB/cy** — the steepest, therefore the narrowest ceiling,
   which is the direction to take when three fits of one quantity disagree. 3.73 is the
   1,200→2,000 secant.
3. **The anchor was one child process.** The probe's peak is `ru_maxrss` of the single
   `run_annual_report` it spawns. What has to fit the box is the **cgroup** — systemd's
   `MemoryPeak` for `sim-runner.service`, **5,734.4 MB** across 8 runs
   (`resource_headroom.weight_drift("sim_run")`), which is 227.0 MB higher because it counts the
   `sim_runner.py` parent the probe never spawns.

The page now states 4.34 MB/cy, the **1,263** the curve supports against a 25% guest share, and the
**1,250** the constant ships that floored to — and says why a child-anchored **1,312** was never
admissible: it puts the cgroup 227 MB *over* the memory budget it was derived to respect.

**The ceiling was NOT re-derived here.** A lane owns it; its arithmetic stays in the constant's own
note. One home for a derivation is the point.

## 3. The second defect, which the item did not name and which outlives this number

**`(today 1,200)` was a lie by tense, and it would have re-broken this page on the next move.**
That figure is read from `book_growth_campaign.json` — the campaign record of the run *behind* the
page. It therefore lags the constant by one publish cycle **every time the constant moves**, which
is precisely how a reader ends up citing a superseded ceiling as the current one. The item
described `site/data/book_growth.json` as "one producer cycle stale by construction and needs
nothing but a note saying so". **A note would have been spent in a week.** The clause now names
which run it belongs to and says that it lags:

> *"(the run behind this page was given 1,200; a change to the constant reaches this figure one
> publish cycle later)"*

`site/data/book_growth.json` was regenerated rather than annotated, because the stale sentence was
reader-facing on the live page right now. The regeneration moved exactly two fields — the basis and
`generated_at` — verified by a sorted-key diff against the working copy before landing.

## 4. The control: kept keyed to the property, and proven to fail on THIS sentence

`test_the_page_publishes_no_ceiling_it_cannot_name_the_measurement_for` was re-keyed off the pinned
literal `"NOT YET KNOWN"` on 2026-09-21. **It is unchanged here, and deliberately: the new literal
1,250 is not pinned anywhere.** The property is that the basis either says the ceiling is unknown,
or states one AND cites an artefact that is in a commit.

A control inherited across a rewrite is a control nobody has re-proven, so both legs were mutated
against the *new* sentence, each on the defect it was written for:

| mutation | leg that fired | verdict |
|---|---|---|
| cite `settlement_ceiling_slope_NEVER_LANDED.json`, keep the ceiling | the in-a-commit leg | **red**, naming the path |
| drop the citation entirely, keep the ceiling | the names-a-measurement leg | **red** |

Each mutation was reverted immediately and the file compared byte-for-byte against its pre-mutation
bytes (`True` both times), so no mutation was left in the shared tree.

## 5. Owed, and NOT done here — with the reason, because "not done" without one is a gap

**`tools/generate_value_arms_data.py` and `simulation/premise_population.py` still carry the stale
prose** — *"The RSS ceiling is 1,312 customer-years against the budget's 1,200: slack of 1.09x"*,
and *"the next 112 customer-years are the last ones this guest can hold"* (112 = 1,312 − 1,200; at
the landed values it is 13).

The item asked for these. **They were left, and this is not deferral — it is a collision.** A live
lane is re-anchoring `premise_population.load_whole_run_rss_curve` onto the cgroup *in those exact
two files*, running now (pid 2414325, claim
`confirm-the-producer-runs-at-1250-without-an-episode-and-anchor-the-published-ceiling-on-the-cgroup`).
That re-anchor is what moves 1,312 → 1,263, so any prose I wrote there would be superseded by the
same lane within the hour, and the file-level collision is real: `generate_value_arms_data.py` is
865 KB and dirty. **A second writer there buys nothing**, which is the same judgement the 2026-09-22
22:04 result doc made about the same two files, still true for the same reason.

**What this turn adds to that judgement rather than repeating it:** the stale sentences are now
enumerated with line numbers (`tools/generate_value_arms_data.py:10289,10301,10304`), so whoever
lands the re-anchor has the prose list and does not have to find it. **If that lane lands the code
and leaves the docstring, the estate still says 1,312/1,200 and this item is not finished.** That is
the single check the next invocation should run first.

## 6. What "nothing on the estate still says 1,200 or 1,330 as current" means, precisely

The item's FINISHED clause cannot be read as "the strings 1,200 and 1,330 appear nowhere". They
appear, correctly, in a dozen places as **history** — the curve's own 1,200 row, the superseded
paragraphs kept beside their corrections, this file. The clause that can actually be checked is
**"nothing states them as CURRENT"**, and against that:

| surface | before | after |
|---|---|---|
| `engine_bound_basis` (the generator) | 1,331 ceiling, 3.73 MB/cy | 1,263 / 1,250, 4.34 MB/cy, cgroup |
| `site/data/book_growth.json` (published) | 1,331, `today 1,200` | regenerated, run-relative |
| A46 §6 (director-facing) | "leaving it at 1,200" | superseded in place, dated, original kept |
| `generate_value_arms_data.py` docstring | 1,312 / 1,200 / 1.09x | **UNCHANGED — §5** |
| `simulation/net_new_acquisition.py` **working copy** | 1200.0 | **UNCHANGED — §1, stale revert** |

Two rows of that table are still red and both are named above with the reason. **The item is not
released.**
