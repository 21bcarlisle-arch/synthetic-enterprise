**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** the arm's product gate

# The product gate refuses cap segments, not decisions — and every decision that existed was decided

**Filed:** 2026-09-19 · **Claim id:**
`measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach`
**Measured with:** `tools/svt_refusal_census.py` (landed with this finding, so the counts below
are re-derivable rather than quoted) and the live feed `site/data/value_arms.json`.
**Direction, not an atom.** No exit test was written for it; DONE is this finding.

---

## 0. The answer, before the counts

**The product gate is not the ceiling on the method's reach, and relaxing it would buy nothing.**

The funnel's `product_not_upliftable = 2490` is not 2,490 household decisions the company is
blind to. It is 2,490 **published cap periods**, sitting inside far fewer household boundaries,
at none of which this supplier struck a rate. On the world's own schedules the same refusal is
4,578 segments inside **986 stints** — 4.64 funnel rows per spell on the default tariff.

And the decisive arithmetic is one line of the live feed:

```
  2,824 offered  −  2,490 product_not_upliftable  −  227 acquisition_term  =  107
  decisions_that_existed = 107   priced = 104   declined = 3
```

**Every single term that cleared the gate and the acquisition-term rule became a decision.**
Zero stopped at `no_locked_rate`, zero at `not_the_arms_commodity`, zero at
`no_observed_history`. The arm's conversion of its reachable surface is 107 of 107. A gate that
refuses nothing its writer could have acted on is not a ceiling; it is the boundary of the
subject.

`docs/staging/done/SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md`
§3 **stands**. This measurement does not refute it — it supplies the count that was missing.

---

## 1. The premise, re-measured before the work started

The item's `check FIRST` was that the census answers in the guard's own unit — the TERM — and
that `2f436602b` is the repair. `git merge-base --is-ancestor 2f436602b origin/main` returns
true: the repair is landed, so the precondition holds and the item is **not** spent. The counts
it cites were re-established on the live feed before being used, and all four hold exactly:
2,824 offered / 2,490 refused (all `'svt'`) / 227 acquisition / 107 decisions.

**One of the item's figures needed splitting, not correcting.** It says "54 that were scored".
The live page carries **two** discrimination readings on **two** populations and the item cited
one of them:

| block | population | reading |
|---|---|---|
| `inference_claim` | **54** decisions | 0.482 against a 0.407–0.591 null |
| `decisions.discrimination_auc` | **104** scored decisions, 65 accounts | 0.557 against a 0.39–0.61 null |

Both are live, both are inside their own null, and neither is wrong. Stated here because a later
reader differencing them would be differencing two censuses.

---

## 1a. A rival lane built the other side of this subject while I measured it — and its commit is stranded

Found by `ps` before landing, not after: PID 1011655 was inside `tools.surgical_land` on claim
`the-svt-household-has-no-route-back-to-a-fixed-term`, touching
`simulation/renewal_engagement.py`, `simulation/renewals.py` and `simulation/run_phase2b.py` —
the three modules this census instruments. **No path in this commit is contested** (all three
files here are new), so the two land independently.

**Which tree these counts describe, measured rather than assumed.** Their land reported
`rc=0 … landed f0bc1e057`, and it is **not in `main`**: its parent is `f10e6c643`, which
`aeb8a4970` has since superseded, so the commit sits off an older parent and
`git merge-base --is-ancestor f0bc1e057 origin/main` is false. The shared working tree is clean
against HEAD on all four simulation modules (`git diff --stat HEAD` empty), so **every count
below is HEAD's world — `aeb8a4970`, with their change absent.** Filed as a separate
observation; it is their lane's live repair and is not touched here.

*(`rc=0` from `surgical_land` means the commit was created, not that `main` reached it. The
origin-moved race is the known shape and the remedy is theirs.)*

**Their work does not move any count below, and they measured that themselves.** Their commit
message states the baseline world's output is byte-identical, because every live
`ELEC_CUSTOMERS` record carries `tariff_type: None` → `"fixed"`, so the record-door arrival
branch they repaired is unreachable today. **This census confirms it independently from the
other side: `arrival_origin_stints` = 0.** Two lanes, two methods, one answer.

**One name in §2–§4 changes when their commit reaches `main`, and the substance does not.** They split the
single `rolls_active_renewal` call into two household decisions — *re-fix or roll onto the cap*,
and *stay on the cap or take a fixed deal* (`renewal_engagement.converts_off_the_cap`) — because
the second is an internal switch and the GB record prices the two differently. The boundary this
finding counts is the same boundary; after their commit the decider at a class-(a) boundary is
`converts_off_the_cap` rather than `rolls_active_renewal`. Their own 200-pair sweep shows the
two are an **equivalence while the conversion rate is `None`**, which is why the 850/136/144/706
split below is unchanged by it. **If that rate is ever given a value, this census must be
re-run** — the split is the first thing it would move.

**They reached this finding's conclusion from the world side, independently:** "nothing
company-side is touched: no conversion desk, `UPLIFTABLE_TARIFF_TYPES` unchanged,
`SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07` §3 stands."

---

## 2. What each number counts, said before anything is divided

Three units. The funnel publishes one of them and the other two are invisible from it.

| unit | definition | who produces it |
|---|---|---|
| **SEGMENT** | one row from `build_svt_schedule` — one published cap period. **This is what the funnel counts and what the gate refuses.** | `simulation/svt_product.py` |
| **STINT** | one *call* of `build_svt_schedule` — one unbroken spell on the default tariff, beginning where `rolls_active_renewal` came up passive. | the builder's call boundary |
| **BOUNDARY** | the anniversary that *terminates* a stint, where the loop re-enters and `rolls_active_renewal` decides again. **The only unit at which a household decides anything.** At most one per stint. | `simulation/renewals.py` |

> **The stint is taken from the CALL, not from contiguity, and that is a correction to my own
> first draft.** My first pass scanned for runs of adjacent SVT terms and read **280** stints.
> Two consecutive passive rolls emit contiguous segments, so a contiguity scan merges them: it
> reported stints of 42 segments (eleven years on the cap) and a terminating-roll-passive count
> of **0**, which is impossible in a world where two thirds of the book is on the default
> tariff. The true count is **986**. Kept here beside the answer because the wrong number was
> plausible and self-consistent, and only the impossible zero gave it away.

**Two censuses, and this finding never divides one by the other.**

- **Schedule census** (`tools/svt_refusal_census.py`): what the world *builds*, 226 legs,
  **pre-churn**.
- **Funnel census** (`renewal_funnel`, live feed): what *reached the arm* — already net of two
  world-side `continue`s the chain never sees (a term on an already-churned account; an
  unactivated successor term), and carrying successor legs the schedule census does not.

---

## 3. (a) Of the refused terms, how many have a decision behind them

Schedule census, window ending 2025-06-07:

```
  terms built                      5,097        legs 226
  SVT segments                     4,578   (89.8% of terms)
  SVT stints                         986
  segments per stint                4.643   histogram {1:24, 2:54, 3:13, 4:68, 5:827}
  non-SVT terms at index >= 1        294
  term 0, by tariff type           {fixed: 225}
```

Split by whether the stint's own anniversary falls inside the window — which *is* the builder's
`while term_start <= report_end`, read rather than restated:

| class | stints | segments | share of segments |
|---|---:|---:|---:|
| **(a) a decision follows** — the household is asked again | **850** | **4,212** | 92.0% |
| **(not-a) no decision follows** — the stint outruns the window | **136** | **366** | 8.0% |

**The identity control holds.** A stint with nothing after it can only be a leg's last, so
class (not-a) must equal the legs that end the window on the cap. Both are **136**. Had they
diverged, the class rule would be wrong.

Of the **850** class-(a) boundaries, read at the anniversary itself rather than inferred from
adjacency:

- **144** the roll came up **ACTIVE** — the household took a fixed deal, and **the arm already
  sees that term**. It is in the 2,824.
- **706** the roll came up **PASSIVE** — the household looked at the market and stayed on the
  cap. No rate struck, by its own choice.

**`arrival_origin_stints` = 0.** Every SVT stint in this world is a mid-tenure roll. That is an
independent confirmation of `05684780e`'s claim that no caller mints a default-tariff arrival
today, measured from the other side.

---

## 4. (b) Is there an observable at a class-(a) boundary

**Yes — and the gate already reads it, correctly.**

An SVT segment reaches `decide_renewal_rate` carrying a **non-`None`** `locked_unit_rate`: the
published cap. So `STAGE_NO_LOCKED_RATE` does **not** fire, and the number alone cannot
distinguish *a rate this supplier struck* from *a rate Ofgem set*. The only thing that
distinguishes them is `tariff_type` — and a real UK supplier knows precisely which of its
households sit on its default tariff. `UPLIFTABLE_TARIFF_TYPES` is therefore reading a genuine
observable, and it is the **only** guard in the chain that can tell those two apart. Deleting it
would not widen the method; it would feed `renewal_unit_rate_uplift` a regulated ceiling as
though the supplier had chosen it.

What is absent is not an observable — it is the **writer's argument**.
`renewal_unit_rate_uplift` moves a rate the supplier set. At a cap segment there is none.

What a real supplier decides at that boundary is a **conversion** — whether to serve this
household a fixed deal — which is acquisition-shaped and is a desk this company has not built.
The live feed's own `why` text already says exactly this, and this measurement is the first
evidence for it rather than a restatement of it. Note also that at **706 of the 850** class-(a)
boundaries the household had just declined to take a deal; the conversion desk's subject is a
population that has demonstrably said no.

---

## 5. (c) What the decision count would be if the gate admitted class (a)

Three readings. Each is stated inside **one** census, and they are not added across censuses.

**(c1) — the gate admits class-(a) SEGMENTS.** This is what relaxing `UPLIFTABLE_TARIFF_TYPES`
would literally do, because the guard is per-term. Schedule census: **+4,212 rows**. Funnel
census: up to **+2,490**. **None of them is a decision.** At 4.64 segments per stint this counts
a single household boundary up to five times, and at every one of them the rate is the published
cap. The funnel's `decisions_that_existed` would rise by thousands and the company would not
have made one more decision.

**(c2) — the gate admits ONE decision per class-(a) STINT**, at its terminating anniversary. The
honest unit, and it is not a shape the present guard can express. Schedule census: **850**
boundaries, of which **144** already reach the arm as fixed terms, leaving **706** genuinely
new — against that same census's **294** decision-eligible terms. So the honest ceiling on this
route is real and large: roughly a trebling of the surface. **But all 706 are conversion
decisions, not uplift decisions**, and the arm has no writer for them.

**(c3) — the gate as it stands.** Funnel census: **107** decisions existed and **107** were
decided (104 priced, 3 declined).

---

## 6. What this relocates the constraint to

The item said the constraint was "unlocated" after the tree refuted a world-side diagnosis last
stretch. This narrows it to two things, neither of which is the product gate:

1. **The world's product mix**, which is fidelity and not a defect. ~90% of terms are on the
   default tariff. `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b) is the published
   warrant: a domestic fixed share that is a minority in every year of the window. Growing the
   book scales both sides of `decisions_that_existed / offered` and cannot move it.

2. **Churn truncation, which is larger than the gate and was not on anyone's list.** The
   schedules contain **294** decision-eligible terms across the 226 legs. The funnel saw
   **107**. The difference — *at least* 187 — is terms belonging to accounts that had already
   churned, since successor gating can only *add* to the funnel's count. **Roughly two thirds of
   the decision surface this world builds is destroyed by churn before the arm is ever asked.**
   This is stated as a bound, not an equality: the two counts are from the two censuses named in
   §2, and I have not re-run the arms to measure it inside one.

   **That bound is the next measurement, and it is bigger than the one just taken.** It is not
   taken here because it needs a run, and because this item was explicitly scoped to measure the
   gate and rule nothing.

---

## 7. What I did not do, and why

Per the item, explicitly: **`UPLIFTABLE_TARIFF_TYPES` is unchanged**; no conversion or targeting
desk was built; the arms page was not touched. The census is a diagnostic and carries R12 in its
own docstring — no count in it is a target, and specifically none of them is a cue to relax the
gate so the refused number falls.

**The symmetric error the item named was the live one and it did not fire.** Relaxing a
company-side gate before establishing there is a decision behind it would have added thousands
of cap segments to `decisions_that_existed`, moved every published share, and produced a page
saying the method reached far more households — with not one additional decision behind it.
