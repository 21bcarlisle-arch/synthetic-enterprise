**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: a pre-registration refutes nothing on its own. It exists so the measurement
filed beside it can be shown to have been designed before its answer was known.*

# Pre-registration: what the first NATIVE SVT capture must show

**Filed 2026-09-01, delivery seat, Lane 0, AFTER launching `tools/capture_departure_factors.py` and
BEFORE reading a single line of its output.** The run was started against
`/tmp/svtcap/c2_marketterm.json` at the commit below; nothing in this file was written with a result
in view.

---

## Why this run is possible today and was not yesterday

`WORKER_FINDING_THE_SVT_ROUTE_CAN_NOW_SEE_THE_MARKET_AND_THE_NEXT_GATE_IS_A_STALE_CAPTURE_2026-09-01.md`
closed with four owed items and called item 1 **the binding one**:

> **Land the SVT departure route's recorder in `run_phase2b`** so a capture can be regenerated.
> Until then no whole-book anchor can be emitted by the ordinary route. This is the binding item and
> it is in another lane.

**That item is discharged, and I did not discharge it — I found it already done.** `run_phase2b.py`
carries `_svt_decisions` at line 1419, appends at 1656, and returns `"svt_decisions": _svt_decisions`
at 3244. All three are **in `HEAD`**, verified with `git show HEAD:simulation/run_phase2b.py` rather
than by reading the working tree, because this repo has paid for exactly that confusion
(`WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31.md`).
It landed at **`6db30a350`** — *"the SVT belief can finally tell two households apart, and it is
still inside its null"* — a commit whose headline claim is about something else entirely, which is
why the finding one lane over could still call the item outstanding in good faith.

**So this is the first capture in this repo's history whose SVT sibling has a producer in git.**
Every SVT sibling read by any instrument to date is the 1,266-row foreign artefact at `87709c617`,
whose producer is in no commit and whose renewal table is a different run
(`WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`:
144 renewal decisions over 68 accounts against 1,266 SVT decisions over 116 accounts, only 53 shared).

**A stale docstring is filed alongside, not fixed here.** `tools/capture_departure_factors.py`'s
module docstring still asserts *"At this HEAD that is every run: `run_phase2b`'s return dict has 63
keys and `svt_decisions` is not one of them"*. `6db30a350` falsified that sentence and did not edit
it. It is a false statement in a live module, and it is the sentence a reader consults before
deciding whether re-capturing is worth ten minutes — so it is load-bearing, not cosmetic.

**Captured to a stem of its own, deliberately.** `/tmp/svtcap/`, not `docs/reports/`. `emit_svt_sibling`
refuses to leave a stale sibling beside a fresh renewal table because every reader joins the two as
one capture; writing to the live stem would have put a fresh table beside the foreign 1,266-row
sibling and made that refusal my problem instead of a diagnostic.

---

## The predictions

Five, each with a direction and a magnitude, each falsifiable by the run now in flight. **This is
deliberately not an invariance**: an invariance measured on the old code embeds the defect being
removed.

### P1 — a sibling is written, by a producer in git, and it is not a measured zero

`emit_svt_sibling` reads `result.get("svt_decisions")` with **no default**, so the three outcomes are
distinguishable. Predicted: the key is **present** and the list is **non-empty** — a sibling file is
written and neither stderr warning fires.

*Refuted by:* `⚠ NO SVT RECORDER IN THIS RUN` (key absent — `6db30a350` does not reach the return
path I read), or `⚠ THE SVT RECORDER RAN AND RECORDED NOTHING` (present but empty — the product
exists and no roster assigns it, which `test_svt_product.py::test_no_account_is_on_the_svt_product_yet`
asserted as recently as 08-31).

**P1 is the one I am least sure of, and I am saying so before the answer.** The empty case is live:
if no roster assigns the SVT product in a default `run_phase2b`, the recorder runs and records
nothing, and that is a *measured zero* rather than a failure. If P1 lands empty, the finding is that
the route exists in code and carries no accounts — which would make the 61%-of-departures figure a
property of the foreign artefact and not of this world, and that is a bigger finding than the one I
set out to file.

### P2 — the staleness leg goes to exactly zero

`svt_composition_refusal` classifies each row into `unanchored` / `anchored` / `market_blind` /
`neither`, in that order. Predicted: **`market_blind == 0` and `unanchored == total`.**

The mechanism: the world now runs the market-factored hazard, and the refusal reconstructs `raw`
with the same factor from each row's own `market_year`, so every row matches the *first* branch.
Note the branches are ordered and mutually exclusive — rows from 2019–20, where `factor ≈ 1.0`,
match `unanchored` before `market_blind` is ever evaluated. So `market_blind == 0` is **not**
evidence that those years are market-blind, and I am recording that here so the count is not
over-read afterwards.

*Refuted by:* any non-zero `market_blind` (the run did not use the term the fit assumes), any
non-zero `anchored` (the world multiplies the level anchor into the SVT route, which would make the
whole-book fit's held-fixed contribution wrong), or any non-zero `neither` (mechanism disagreement).

### P3 — the account-denominator refusal is the coin-flip, and I predict it LIFTS

`account_denominator_refusal` refuses on three properties: rows with no `customer_id`, an account
departing **more than once**, and an account invisible **between** two of its own decisions.
Predicted: **returns `None`.**

The argument for lifting: the foreign sibling failed the *provenance* question, not these three, and
a single coherent run cannot produce the 63-SVT-only / 15-renewal-only split that made the joined
pair incoherent. Both routes now come from one `run_phase2b` over one roster.

**The argument against, which I am filing because it is real:** the prior finding's title is that a
*foreign* sibling is what makes this control **pass**. A native capture puts renewal and SVT
decisions for the *same* account into one union for the first time, and if a household can churn on
the SVT route and also reach a renewal roll that records a departure, `twice` fires. Predicted
`None`, with maybe 65% confidence — and if it refuses on `twice`, **that is a finding about the
world (a departure is not terminal), not about the capture**, and it must not be repaired by
de-duplicating in the reader.

### P4 — a whole-book fit is emitted for the first time

Conditional on P1, P2 and P3. Predicted: `── WHOLE-BOOK FIT ──` prints and per-year anchors are
emitted, replacing the standing `REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture`.

### P5 — 2022 is reachable, and the other nine years are too

Predicted: **2022's SVT floor lands below its 4.30% target**, so the year is `reachable` and the
renewal anchor for it is a positive finite number. Magnitude: floor in **1.5%–3.5%**, straddling the
**2.33%** / **2.34%** the two diagnostic runs recorded, and *not* equal to either — this is a third
population.

Predicted: **2023's renewal anchor is above 1.0** and no longer the **0.03** that made the priceable
route near-extinct. Predicted range 1.5–3.5, widened from the 1.3–2.0 I got wrong last time, on the
same measured evidence (2.4417) rather than on hope.

*Refuted by:* any year printing `NOT FITTED — unreachable: SVT alone expects …`.

**Absolute counts will differ from both prior tables and that is not a result.** The denominator has
moved twice already today (2022: 55 → 52 accounts). Differencing a cell across two populations
measures the population, not the hazard.

---

## What must NOT happen when this is scored

Named in advance so the flattering repair is not available afterwards:

1. **No constant is pasted into `simulation/departure_level_anchor.py`** on the strength of one
   capture, however green. If P4 lands, the fit emitting a block is the result; adopting it is a
   separate decision with its own evidence.
2. **No widened band and no clamp on 2022.**
3. **`population_anchor._churn_by_year` is not repaired by inserting a `sim_churn_rate` of 0.0** for
   2022. That publishes a measured zero-churn crisis year. Its arithmetic consumers fail closed.
4. **If P3 refuses on `twice`, the reader is not de-duplicated.** The refusal is then correct and the
   question moves to the world.

---

# GRADED 2026-09-01, delivery seat, Lane 0

**The text above is untouched. Every miss below is kept where it was filed, not revised.**

## What was actually run

The run that produced this grading is the **fourth** launch. The first three died with the bounded
tick that launched them — the class `a job launched from a bounded tick dies with it` — and the
third's corpse is kept at `/tmp/svtcap/capture.DEAD-run3-1147Z.log`, ending at `2020-10-18 period 2`.
The fourth was launched under `systemd-run --user --unit=svt-native-capture`, which outlives its
launcher, and **ran to completion**: `EXIT_RC=0`, the full window, `OUTCOME: SURVIVED`.

I did not launch it — I found it already in flight at 17:31:18Z and waited on it with
`tools/wait_for.py --pid 2771542 --deadline 1800`, never a hand-rolled `pgrep`. It finished 240s
into that wait. **The run took ~11 minutes of wall-clock, not the hours the direction budgeted**, and
that matters for scheduling the next one: this is a cheap experiment, and three stretches of it being
"too expensive to restart" were mis-costed.

| artefact | sha256 |
|---|---|
| `/tmp/svtcap/c2_marketterm.json` (156 renewal rows) | `bd6ad1da9207a5ff8f7c364bffcf4c546613ded7fd47d2a156e259f7a272fa70` |
| `/tmp/svtcap/c2_marketterm_svt_segment_decisions.json` (1373 SVT decisions, 38 departed) | `4bb04dcd0a1ccd6e64df618860c9d687e009200eca01c89f932544fe690e3e58` |

`/tmp/svtcap/PROVENANCE.txt` records the module sha256s **as run**. Read them: the run executed the
**shared working tree**, not a commit, and three of its five run-relevant modules were dirty against
`origin/main` at launch.

## The five predictions, as filed

### P1 — SPLIT. The falsifiable clause holds; the clause in its own heading is REFUTED.

The heading claims a sibling *"written **by a producer in git**"*. The `Refuted by:` line named only
the two stderr warnings, and **neither fired**: the key is present, the list has 1373 rows, and
`load_svt_decisions` returns no warning. On its own stated refutation criterion, **P1 stands**.

**But its heading is false, and I am grading the heading because the prereg wrote it.** The producer
is in git by half. The *recorder* landed at `6db30a350`, as the prereg says. The **C1b roll** that
puts an account on the SVT product so the recorder has anything to record did **not**:

```
$ git show origin/main:simulation/renewals.py | grep -c 'rolls_active_renewal'
0
```

Zero occurrences, checked against `origin/main` after fetching, not against the working tree. The
roll is ~56 uncommitted lines in the shared checkout. **So whether this tool writes a populated
sibling or an empty one is decided by the working tree, not by the commit** — run it on a clean
checkout of this HEAD and the sibling is empty.

**The prereg said P1 was the one it was least sure of, and it was right to be — but it was wrong
about which half would fail.** It braced for an *empty* sibling and got a full one; what actually
failed was *provenance*, which it had listed as settled. That is the more useful miss, because the
prereg's own cited precedent
(`A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31`) is exactly this
class and the prereg still filed the clause as established.

Another lane reached the same conclusion independently and landed it at `342d72159` — *"the SVT
recorder is in git and the roll that fills it is not, so the native capture is native by half"* —
together with the docstring correction this direction asked for. **I did not redo either.**

### P2 — CONFIRMED, exactly, on the counts and not merely on the verdict.

`svt_composition_refusal` returns `None`. The verdict alone would be a thin grade, so the
classification was re-run row by row:

```
total=1373   unanchored=1373   anchored=0   market_blind=0   neither=0
```

`market_blind == 0` ✓ and `unanchored == total` ✓, both as predicted. The staleness leg goes to
exactly zero and every row reproduces under the market-factored hazard.

**The prereg's own caveat stands and is repeated here so the count is not over-read**: the branches
are ordered and mutually exclusive, so 2019–20 rows where the factor ≈ 1.0 match `unanchored`
*before* `market_blind` is evaluated. `market_blind == 0` is **not** evidence those years are
market-blind. `anchored == 0` is the load-bearing one: the world does not multiply the level anchor
into the SVT route, so the whole-book fit holding the SVT contribution fixed is legitimate.

### P3 — CONFIRMED. The coin-flip landed on the predicted side.

`account_denominator_refusal(renewal_rows, svt_rows)` returns `None`. Sub-properties measured rather
than inferred from the verdict: **0 rows carry no `customer_id`**, and **131 distinct accounts**
across both routes. `twice` did **not** fire.

So the question the prereg raised — whether a household can churn on the SVT route *and* reach a
renewal roll that records a departure — **does not arise in this world**, and constraint 4 is moot.
Filed at ~65% confidence; it paid.

### P4 — CONFIRMED. The first whole-book fit in this repository's history.

`── WHOLE-BOOK FIT: both routes, over the accounts on the book ──` printed, replacing the standing
`REFUSED — no YEAR_LEVEL_ANCHOR block is emitted from this capture`. Seven years carry an anchor;
three are absent with a named cause each.

### P5 — SPLIT. The magnitudes are sharp hits. One clause is REFUTED by a cause the prereg did not put in its refuter list.

| year | accts | nRen | nSVT | record % | SVT floor % | anchor |
|---|---|---|---|---|---|---|
| 2017 | 57 | 20 | 116 | 14.00 | 5.72 | 7.2492 |
| 2018 | 55 | 21 | 144 | 20.00 | 10.20 | 3.2492 |
| 2019 | 45 | 16 | 122 | 21.30 | 10.89 | 5.2532 |
| 2020 | 51 | 18 | 137 | 23.00 | 10.39 | 5.4772 |
| 2021 | 55 | 23 | 153 | 18.40 | 7.87 | 5.2686 |
| **2022** | **55** | **0** | **213** | **4.30** | **2.54** | **—** |
| 2023 | 57 | 20 | 210 | 12.50 | 6.90 | 2.0539 |
| 2024 | 62 | 19 | 181 | 16.10 | 6.83 | 4.1204 |

**CONFIRMED, and sharply:** 2022's SVT floor is **2.54%**. Predicted 1.5–3.5% ✓; below the 4.30%
target ✓; straddling the 2.33%/2.34% the two diagnostic runs recorded and **not equal to either** ✓ —
a third population, as predicted. **CONFIRMED:** 2023's anchor is **2.0539** — above 1.0 ✓, inside
the predicted 1.5–3.5 ✓, no longer the 0.03 that made the priceable route near-extinct.

**CONFIRMED on the stated refuter:** no year printed `NOT FITTED — unreachable: SVT alone expects …`.

**REFUTED:** the clause *"so the year is **reachable** and the renewal anchor for it is a positive
finite number"*. 2022 prints `NOT FITTED — no renewal decisions in this year`. Its anchor is `—`, not
a positive finite number.

**Why this miss is worth keeping.** The prereg treated the SVT floor as the binding constraint on
2022 and predicted that clearing it would make the year fittable. **Clearing it changed nothing**:
the floor came down from 12.09% to 2.54% — comfortably under target — and 2022 is *still* unfitted,
because it holds **zero renewal decisions over 55 accounts**. The anchor multiplies nothing, so no
value of it moves the year by a basis point. `departure_level_anchor`'s own docstring already said
both causes bind; the prereg cited that docstring and still predicted the year would become
reachable. **Two independent causes, and I fixed the one I was looking at.**

## Constraints honoured

1. **No constant pasted into `simulation/departure_level_anchor.py`.** The block above is recorded
   as a *result*, not adopted. Adopting it is a separate decision needing evidence this one capture
   cannot supply — and it should not be taken while the producer is half-uncommitted (P1).
2. **No widened band, no clamp on 2022.** None applied. 2022 stays unfitted with both causes named.
3. **`_churn_by_year` not repaired with a `sim_churn_rate` of 0.0.** Not touched — and this capture
   turns that hazard from hypothetical into live, which is a result in its own right. See below.
4. **Reader not de-duplicated.** Moot: P3 did not refuse on `twice`.

## Two findings this capture produced that were not predicted

**(a) The `= 0.0` default in `population_anchor` now has a real 2022 behind it.**
`_churn_by_year` only creates `by_year[year]` when a `customer_events` entry exists for that year.
This capture establishes 2022 has **zero renewal decisions over 55 accounts** — so the year is
**absent**, `churn_by_year.get(2022, {})` is `{}`, and `tools/population_anchor.py:490`'s
`.get("sim_churn_rate", 0.0)` resolves to **0.0**. That zero then flows into `2022_sim_rate_pct`,
`2022_ratio_vs_ofgem` and the crisis-divergence test — **publishing a measured zero-churn crisis
year for the one year the published record is loudest about.** This is the class
`a default-zero parameter turns an unobservable cause into a published measured zero`. The repair is
to fail those consumers closed, never to insert the zero. **`tools/population_anchor.py` is outside
this stretch's pathspec, so it is recorded here and not touched.**

**(b) The 61%-of-departures figure is a property of the foreign artefact, not of this world.**
This capture: 38 SVT departures and 36 renewal departures over 74 — the SVT route is **51%**, and the
tool reports the renewal route's own share as 49%. The prereg predicted the 61% figure would be
exposed as foreign only *if P1 landed empty*. P1 landed full and **the 61% is foreign anyway**.
Anything downstream still citing 61% is citing the 1,266-row artefact at `87709c617`.

## What is owed next

1. **Land the C1b roll**, or this capture is unreproducible from any commit. Until then the
   whole-book block above cannot be adopted — the fit is real, its producer is not in git.
2. **Fail `population_anchor`'s five 2022 consumers closed** (finding (a)).
3. **Re-run this capture after (1) lands** and confirm the block is byte-stable. It costs ~11
   minutes, not hours.
