# PB1 DISCOVER — how big the world should be, and the price the probe can and cannot quote

**Atom:** `PB1_population_target_and_its_price` (`docs/design/maturity_map.yaml`, lane
`W2_customer_generator`, epoch 2, `loop_stage: idle`, `provenance: director_ruling`, dial 3).
**Source ruling:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`
(deliverable 1). **Mint receipt:** `docs/staging/done/PLANNER_MINTED_population_and_book_growth_2026-08-11.md`.
**Sibling pass, read first:** `docs/design/PB2_OPENING_BOOK_DISCOVER.md`.

**This is a LANE-3 DISCOVER/FRAME pass. No BUILD.** The atom is `idle`, which parks it for BUILD
only (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1). `level_current` stays **0**, `loop_stage` stays
`idle`, no `file_scope` path was touched, no curriculum value moved (R13 — the population target is
the director's to buy; this document proposes it and prices it, and flips nothing).

Every cost figure below is **read from `docs/observability/scale_probe_10k/report.json`** (AO12 run
`20260812T013154Z`) by the script in §3, printed verbatim. No cost is re-derived and none is
asserted from memory. The two places the evidence runs out are labelled UNKNOWN and treated as
unknown, never as zero.

---

## 0. The answer, up front

| | |
|---|---|
| **Proposed premise-population target** | **4,000 premises** — derived, §1 |
| **What it is derived from** | the shipped composition control's own resolution floor (`tests/simulation/test_premise_population.py:37`, `BIG_N = 4_000`), which is the smallest N at which that control can fail; it also clears PB2's funnel floor at any book the probe can price |
| **Today's research draw** | **200** (`docs/observability/coupled_gap_ledger.json:52`, `n=200, population_seed=17`). 4,000 is **20×** it |
| **Cost of drawing 4,000 premises** | **UNKNOWN.** AO12 has **no stage whose subject is `simulation.premise_population`** — §2. This is the pass's main finding |
| **Affordability verdict** | **NOT BUYABLE YET, both ways round.** Un-joined: UNDECIDED (unpriced) *and* purposeless. Joined to the acquisition path, which is what the ruling asks for: **DOES_NOT_FIT** — 8.6× the probe's MEASURED `ceiling_death` at 465 customer-years |
| **Prerequisites, in the order they bind** | (1) one new AO12 stage over `premise_population` — the missing measurement; (2) PB2's **unwon remainder**, without which growing the world *grants* the book; (3) the queryable-projections/storage work (`DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10`, partly landed as `G12`) for the persisted side |
| **Interim, buyable now in principle** | the largest N whose join completes a green full shipped run, found by bisection, with **465 the fail-closed cap** until that run exists |
| **Structural finding for the director** | there are **two populations in this world and they are disjoint** — §4 — so "the company acquires a subset of the population" is false twice over, not once |

Recommendation, and I am not asking which: **adopt 4,000 as the target and do not buy it yet.**
Land the missing probe stage and PB2's remainder first, in that order; they are cheap and they are
what makes the number mean anything. Nothing here needs a decision from the director except the
eventual R13 curriculum act, and that is not owed until the price exists.

---

## 1. The proposed target, and why it is 4,000 rather than a number I liked

The ruling's requirement is "materially above today's research draw". *Material* has to come from a
constraint or it is taste, so here are the two constraints this repo already carries. Both are
floors; the target is the larger of them.

**Floor 1 — the instrument's own resolution.** `simulation/premise_population.py` guarantees that
"for a large enough N, the drawn population reproduces the three published marginals it was raked
to *within binomial sampling error*". The shipped control on that guarantee
(`tests/simulation/test_premise_population.py`) sets `MARGINAL_TOLERANCE_PP = 0.03` and draws
`BIG_N = 4_000`, with its reason written in the source: *"Large enough that binomial noise on the
smallest judged share is well inside the tolerance, so a FAILURE means a biased draw rather than a
small sample."* That constant is R15-proven both ways — line 85's falsifier asserts the tolerance
**can** be exceeded, with the comment *"the control cannot fail and is worth nothing"* if it cannot.

Computed (§3): on the largest published share (44.8%) the binomial sd is 0.0079 at N=4,000, so the
3pp tolerance sits **3.82 sd** out — a real test. At today's N=200 the sd is 0.0352 and the same
tolerance is **0.85 sd** out. **Today's published research draw is below the resolution of its own
control**: at n=200 a biased draw and an unbiased one are not distinguishable at the tolerance the
repo has chosen, so every composition claim made on that draw rests on an instrument that could not
have said otherwise. That is the strongest reason to raise the population and it is independent of
the book entirely.

**Floor 2 — the funnel, from PB2 §4.** Every quote must be issued to a premise that exists:
`N_pop ≥ ⌈5.8324 × N_book⌉`. Inverted, N=4,000 premises supports a book of **686** won accounts —
above the 465 the probe measured as reachable (§3[b]). So at 4,000 **the world is not the binding
constraint**, which is exactly the property the ruling wants ("the company cannot plausibly acquire
from a stock that isn't there") and is the reason not to go higher yet: a target above 686 buys
headroom for a book nothing can currently price.

**4,000 = max(4,000 from Floor 1, 2,712 from Floor 2 at the 465 cap).** Floor 1 binds. The number is
therefore the smallest population at which the world's own composition guarantee is *testable* and
the funnel has somewhere to lose — and it is 20× today's draw, which settles "materially above".

---

## 2. The finding: the probe never priced this object

The atom's exit (b) says the cost must be **read from AO12's own report artefact**. So the first
thing this pass did was look up which stage prices a premise. There isn't one.

AO12's five stages are `population_draw`, `settlement_build`, `run_output_serialization`,
`site_publish`, `git_transport`. The stage named `population_draw` records its own subject in its
own `detail` field:

> `drew 10258 customers via simulation.population_draw in 41 batches of lambda=250 (the generator saturates above ~745)`

and `tools/scale_probe_10k.py:27` labels that stage in its own header as **"the book itself"**. It
measures `simulation/population_draw.py` — the *customer acquisition* draw — not
`simulation/premise_population.py`, the *premise stock* this atom is about. They are different
modules producing different objects (§4). **The 860 bytes/unit and 0.20 s in that row are the price
of a drawn customer, and there is no measured price for a drawn premise anywhere in the report.**

Exit (d) governs what follows: *a stage the probe never reached is an UNKNOWN cost, not a zero.* A
stage it never *aimed at* is the same thing. So the premise-population draw's cost is **UNKNOWN**,
its affordability is **UNDECIDED**, and this pass does not measure it — measuring it here would be
the re-derivation exit (b) forbids, and would put the price in a document instead of in the
instrument that exists to hold prices.

**Queued finding, not fixed here** (SELF_INTERRUPT_DISCIPLINE): PB2 §4 prices 18,756 premises at
"~16 MB to draw" using the 860 B/customer constant, and its record repeats it as "a drawn premise
costs ~860 bytes RSS". That is a **subject substitution** — the customer draw's per-unit constant
read onto premises — and it is the fail-open shape in R15's own vocabulary (wrong subject). PB2's
*count* floors are unaffected; only its cost sentence is. It is recorded here rather than edited
into PB2's doc because that doc belongs to another draw and is in flight.

---

## 3. The price list, read from the record

Run against `docs/observability/scale_probe_10k/report.json` at this commit; output pasted verbatim.

```python
import json, math
r = json.load(open("docs/observability/scale_probe_10k/report.json"))
S = {s["stage"]: s for s in r["stages"]}
N, H = 4000, 10
premise = [k for k, s in S.items() if "premise_population" in (s.get("detail") or "")]
# ... prints each stage's peak RSS / wall / output straight off the record, then the verdict
```

```
report stages                    : ['population_draw', 'settlement_build', 'run_output_serialization', 'site_publish', 'git_transport']
stages whose SUBJECT is premise_population : NONE
population_draw's own subject    : drew 10258 customers via simulation.population_draw in 41 batche...

[a] premise draw at N=4000       : UNDECIDED -- UNKNOWN cost, no stage measured this subject
[b] settlement_build             : ceiling_death at 465 customer-years (peak RSS 3026 MiB, wall 7.05s, output_bytes None)
    report affordability         : DOES_NOT_FIT (projection 59.5 GiB vs budget 7.99 GiB)
[c] run_output_serialization     : peak RSS 582 MiB, wall 0.73s, output 126214554 B for 507993 records
    report affordability         : DOES_NOT_FIT; 248.46 B/record x 17517 records/customer-yr = 4.35 MB/customer-yr RAW; THE REDUCTION IS UNMEASURED
[d] site_publish                : peak RSS 22 MiB, wall 1.34s, output 1854553833 B, subject_kind=replica, affordability=UNDECIDED, 1 UNMEASURED note(s)
[d] git_transport               : peak RSS 27 MiB, wall 3.63s, output 1420425 B, subject_kind=replica, affordability=UNDECIDED, 2 UNMEASURED note(s)

PATH A -- raise the research draw alone (premise_population only):
  cost   : UNKNOWN (no probe stage has this subject) -> UNDECIDED, fail-closed
  purpose: UNSERVED -- simulation/population_draw.py does not import premise_population,
           so the stock the company acquires from is still not this stock
PATH B -- join it to the acquisition path, which is what the ruling asks for:
  simulation/live_population.py:161-177 returns list(CUSTOMERS) + drawn, so every drawn
  member IS a book member -> the book-side stages bind at the drawn size
  verdict at N=4000: DOES_NOT_FIT -- 8.60x the MEASURED ceiling_death at 465; raw settlement over 10 yr = 174.1 GB before an UNMEASURED reduction
  verdict at the measured cap 465: the largest book the record can price at all (20.2 GB raw over 10 yr)

FLOOR 1 (funnel, from PB2 §4): 5.8324 quotes/win -> N=4000 supports a book of 686, above the measured cap 465: the world is not the binding constraint
FLOOR 2 (statistical) N=200  : binomial sd on the largest published share 0.0352; the shipped 3pp tolerance is 0.85 sd
FLOOR 2 (statistical) N=4000 : binomial sd on the largest published share 0.0079; the shipped 3pp tolerance is 3.82 sd
```

Four things about that output are worth stating plainly, because each is a place a cheerful reading
was available and the record refuses it:

1. **465 is measured; 1,343 is not.** `settlement_build` has `status: ceiling_death` and its own
   `detail` says the per-unit cost is *under-stated* (baseline taken at the first checkpoint). Its
   projection is labelled a lower bound by the report itself. Fail-closed uses the 465 the stage
   actually completed, as PB2 §2(ii) already concluded on the book side.
2. **`run_output_serialization`'s pressure is a lower bound with an unbounded term in it.** The
   report's own `pressures` entry says so: the REDUCTION is unmeasured, so no smaller persisted
   figure may be claimed from this row, and no larger one is available either.
3. **`site_publish` and `git_transport` are `subject_kind: replica`.** Both are 10,000 replays of a
   handful of real shapes; `git_transport`'s own note says its 1,306× pack ratio biases both size
   and wall time **low by an unknown factor**. They stay UNDECIDED at any N, and a population target
   may not lean on them.
4. **`population_draw` reads FITS, and it is the one row that does not apply here.** It is the
   cheapest row in the report and the tempting one to quote. It is about a different object.

---

## 4. The structural finding: two populations, disjoint

Read the two modules directly:

* `simulation/premise_population.py` — draws `DrawnPremise` records (property type, build era,
  insulation, bedrooms, EPC band) raked onto three published England housing-stock marginals. Used
  by `tools/couple_fabric.py` only. It is a **research instrument**; nothing in a run consumes it.
* `simulation/population_draw.py` — draws `SyntheticCustomer` acquisitions (region, tenure, cohort,
  consumption band). Its imports are `simulation.household_segments` and stdlib; it **does not
  import `premise_population`**. Its output is what `live_population()` appends to the book.

`premise_population`'s own docstring records why they are separate — it was built *because*
`SyntheticCustomer` carries no premise dimensions, so `make_household` defaults every drawn customer
to the same `suburban_semi`, "a population of clones". The two were never joined.

So the ruling's sentence — *"the company cannot plausibly acquire from a stock that isn't there"* —
is satisfied by neither population today. Raising the premise stock does not enlarge what the
company can win, because the company wins out of the *other* draw. And PB2 §5 shows the other draw
is the book itself (`live_population.py:161-177` returns `list(CUSTOMERS) + drawn`, verified in this
pass by reading it). Stacked:

```
premise stock (200, raked, research-only)  ─── no membership relation ───  acquisition draw (2, appended)
                                                                                    ║
                                                                          ══ IS the book ══
```

**Both halves must change before a population target means anything:** the acquisition draw must
sample from the premise stock (so a won account is a real premise), and the stock must retain an
unwon remainder (so the book is a subset rather than the whole). The second is PB2's exit (d), filed
as its blocker. The first is not currently filed anywhere and this pass is where it becomes visible.

**Sequencing consequence, and it inverts the filed edge.** The map has `PB2.depends_on = [PB1]`, and
the ruling says the population grows first. On today's seam, growing the population *is* granting
the book — the one implementation PB2 names as forbidden. So deliverable 1 cannot be *bought* before
deliverable 2's remainder exists, even though it can be *proposed* first (which is what this pass
is). The `depends_on` edge is not wrong for the proposal and would be a cycle if reversed; the
correct reading is that **the buying order is remainder-first**, and it is stated here rather than
mechanised because a cycle in the map is worse than a sentence in the record.

---

## 5. What the record says the prerequisites are

The ruling's governor: *"if the probe says the scale is unaffordable on current storage, that is the
answer, and the queryable-projections/storage work is its prerequisite, not a workaround."* Applied
literally, in binding order:

1. **The missing measurement.** One new AO12 stage whose subject is
   `simulation.premise_population.draw_premise_population`, reporting peak RSS, wall and output like
   every other stage. Until it exists, *any* population target is unpriced and this atom's exit (b)
   is unsatisfiable by construction — not by this pass's choice. It is the cheapest of the three and
   it is what turns UNDECIDED into a number. (Scope note: the probe's own `_draw_book` batches below
   the λ≈745 saturation of the *customer* generator; a premise stage takes `n` directly and inherits
   no such limit, but that is a claim about the shipped signature, not a measurement.)
2. **PB2's unwon remainder** (its exit (d)) — without it, every premise added to the world is an
   account added to the book, which is both the forbidden grant and the reason the verdict above
   reads DOES_NOT_FIT rather than a number.
3. **The persisted side.** `DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md` is still an
   unconsumed mint source in the staging root, so it cannot be a `depends_on` edge and is named
   here instead, as the atom's own exit requires. Its first increment has landed —
   `G12_queryable_projections` (L2) already copies AO12's scale envelope verbatim into a rebuilt
   store — but its own record says the envelope **governs nothing yet** ("recorded state is not a
   control") and the store has no consumer until `G13`. So the storage prerequisite is *begun*, not
   met, and nothing in this pass may be read as clearing it.

---

## 6. What this pass deliberately did not do

* **No BUILD.** No code, no test, no `file_scope` path touched; the atom stays `idle` at level 0.
* **No measurement of the premise draw.** Exit (b) says the cost is read from AO12's report. Taking
  the reading myself would have produced a number with no instrument behind it and would have hidden
  the finding in §2 behind a plausible figure.
* **No curriculum change.** N stays 200, the activation flag and profile stay as the director signed
  them (`docs/design/curriculum/population_draw_activation.json`). R13: the target is proposed here,
  bought elsewhere.
* **No map edit.** `level_current` stays 0, `loop_stage` stays `idle`, `depends_on` untouched (§4).
* **No re-derivation of PB2's figures**, and no edit to its in-flight document; the one defect found
  in it is recorded in §2 and in this atom's own record.
