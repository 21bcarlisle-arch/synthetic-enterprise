# D27 DISCOVER pass 7 — the lift that publishes a limit chose its subject by the last seven characters of a key

**Atom:** `D27_belief_window_saturates_on_this_book` · **Lane:** DISCOVER/FRAME only, **no BUILD code**
(the atom is epoch-parked; `file_scope` is `tools/couple_w2_11_d5.py` + its test, untouched here).
**Date:** 2026-08-19 · **Measured at HEAD** `5e0f964ab`.
**Level:** stays **L0**. This is a DISCOVER record, not a repair.

Everything in §2–§4 is `observed-with-evidence` (R9), reproduced below with the commands that
produced it. §5 is labelled where it reasons rather than observes.

---

## 0. Why this pass exists at all — the pause resumed on its own stated trigger

`145a1490f` (2026-08-18 18:54:21 +0100) paused this atom after six passes and named three resume
triggers, one of which was **"a D29/D30 edge move reopening the origin question"**.

`7466402f6` (2026-08-18 **19:30:49** +0100 — 36 minutes later) is D30 DISCOVER pass 6, and it moved
exactly that: it measured `scored_company_headroom_days` / `scored_company_is_inert` — the two fields
whose only subject is whether D27's origin parameter can move the published belief figure — as
computed off the **invoice** population while the belief edges are read off the **failure**
population, wrong by 91 days and published beside a caveat quoting a different number for the same
company.

The trigger fired, in this atom's own subject, before the pause note was an hour old. This pass takes
it. (Recorded so the resumption is auditable against the pause's own text rather than against a
draw doorbell — R7.)

---

## 1. The question this pass asked

D30 pass 6 found the two published headroom numbers disagreeing. The obvious next question is D30's
(repair the field). The question **D27** owns is one step back:

> `score_triad` fastens D27's whole resolution apparatus to the `belief` dimension under a code
> comment that states, in terms, *why* it is fastened to `components` rather than prose. **Which of
> those components actually reaches a reader of the published artefact?**

The comment being tested is `tools/couple_w2_11_d5.py:11253-11255`:

> *"AND AS COMPONENTS, not only in the prose: the ledger writer, the live wiring and the dashboard
> take `components` and never read `note`, so a limit only the prose carries is one the machine
> strips off (D22)."*

and its D33 sibling at `:11258-11260`:

> *"THIS FIGURE'S OWN FLOOR, as structure and not only prose (atom D33): the ledger writer, the live
> wiring and the dashboard read `components`, so a per-figure resolution the machine strips off is
> one the reader never gets."*

---

## 2. MEASURED — 2 of 22, and 2 of 14

Built a live triad (`background.live_payment_triad.LivePaymentTriad`, 40 accounts × 6 periods,
`income_stress_value="high"`), called `.measure()`, and enumerated what `score_triad` attaches:

| dimension | components attached | reach the published entry |
|---|---|---|
| `belief` | **22** | **2** |
| `belief_population_mix` | **14** | **2** |

The two that arrive, in both cases, are `belief_resolution_caveat` and
`scenario_constant_census_caveat`. The 20 + 12 that do not include every structured field the two
comments above were written to justify:

```
band_owning_constants        belief_window_resolution      book_bound_floor_days
measured_resolution_floor_days   memory_blind_band_days    scored_company_is_inert
scored_company_window_days   tv   n_cases   per_case_disagreement_rate
undercall_rate  overcall_rate  n_undercalled  n_overcalled  mean_undercall_steps  ...
```

**The selector.** `background/live_payment_triad.py:148` sets
`CAVEAT_COMPONENT_SUFFIX = "_caveat"`, and `caveats_by_dimension` (`:188`) lifts
`{k: v for k, v in components.items() if k.endswith(CAVEAT_COMPONENT_SUFFIX)}`. Nothing else in
either belief dimension's `components` is looked at.

---

## 3. MEASURED — the control that guards the lift cannot fail outside the suffix

`check_every_caveat_is_published` (`background/live_payment_triad.py:195`) carries an explicit R15
independence argument in its docstring: *"NOT a tautology -- the expectation is read off the SCORED
dimensions and the subject is the WRITTEN one, which are two different objects"*, and the duplicated
lines below it are described as *"the independence, and are the point"*.

The **values** are independent. The **keyset** is not: both halves compute
`k.endswith("_caveat")`. So the control's subject is chosen by a key's last seven characters, not by
whether a limit reaches the reader.

Run against the shipped module, baseline clean (`violations == []`):

| mutation | control |
|---|---|
| **A** — add `memory_blind_band_days_v2 = (-9999, 0)` to `belief.components` | **SILENT** (`[]`) |
| **NULL CONTROL** — delete A, add the *same value* on the *same dimension* as `memory_blind_band_days_v2_caveat` | **FIRES** — 1 violation |
| **B** — corrupt three shipped limits in place: `scored_company_is_inert = False`, `memory_blind_band_days = (0,)`, `book_bound_floor_days = 1` | **SILENT** (`[]`) |
| **C** — delete **every** non-`_caveat` component from both belief dimensions (32 fields) | **SILENT** (`[]`) |

The null control is the whole result: same tuple, same dimension, same writer, same reader — the
verdict flips on the spelling of the key and on nothing else.

Reproduce:

```python
import sys; sys.path.insert(0, '.')
from datetime import date
import background.live_payment_triad as lpt
triad = lpt.LivePaymentTriad()
for i in range(40):
    for m in range(1, 7):
        triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                            amount_gbp=120.0, income_stress_value="high", segment="resi")
res = triad.measure(); head = res["detection"]
head.components["dimension_caveats"] = lpt.caveats_by_dimension(res)
res["belief"].components["memory_blind_band_days_v2"] = (-9999, 0)
print(lpt.check_every_caveat_is_published(res, head))          # []
del res["belief"].components["memory_blind_band_days_v2"]
res["belief"].components["memory_blind_band_days_v2_caveat"] = (-9999, 0)
print(lpt.check_every_caveat_is_published(res, head))          # 1 violation
```

**The repair knew it was generalising and generalised on one axis.** Its own comment
(`:143-147`) says the lift is *"deliberately GENERIC rather than a two-key copy: the defect class is
'a caveat attached to a dimension nobody writes', and naming the two known instances would leave the
next one to be found by an Expert Hour reading the JSON."* That reasoning is right and it worked —
mutation A's *suffixed* twin is caught without anyone naming it. What the suffix does not span is the
other axis of the same class: the class is about **limits that must reach the reader**, and the
selector it built is about **spelling**. A limit named `memory_blind_band_days` is the next instance,
it was already present on 2026-08-18, and it is not found by an Expert Hour reading the JSON because
it is not in the JSON.

---

## 4. MEASURED — which channel actually carries what, on the artefact

Read off the committed `docs/observability/coupled_gap_ledger.json` at HEAD
(`W2_11_payment_behaviour_source`, `measured_at 2026-08-19T00:16:09Z`,
`run_git_commit 5e0f964ab`). The live writer writes the **detection** dimension and splices the other
dimensions in as formatted prose, so there are two channels, and each carries a different subset:

| carried by | contents |
|---|---|
| `note` (prose) | the belief **numbers** — balanced error 0.1818, under-called 0.3636 (4 of 11, mean 2.50 steps), over-called 0.0000, per-case disagreement 0.2105, `belief_population_mix` 0.2105 |
| `components.dimension_caveats` | the **two caveat strings**, and nothing else |
| **neither** | `memory_blind_band_days`, `band_owning_constants`, `scored_company_is_inert`, and the belief dimensions' own structured counts |

Checked directly — none of `RESOLUTION IS THIS BOOK`, `THE BAND IS THE BOOK`, `SATURATED`, `2622`,
`memory_blind`, `band_owning`, `is_inert`, `3378` appears in the published `note`. So the caveats
reach the **machine** only, the numbers reach the **prose** only, and the third bucket reaches
nobody.

**This is the D22 rationale empirically inverted on the only path with a public reader.** D22's
argument is *"the machine reads `components` and never `note`"*. On the live path every belief number
a human gets is in `note`, and `components` is the channel that drops things.

**And the working pattern is twenty keys away in the same dict.** The detection-side band
`recon_saturation_band_days = [-6, 483]` ships **and** carries its provenance:
`recon_saturation_band_measured_on = {'source': 'predicted_from_this_book', 'n_accounts': 19,
'n_cases': 1600, 'n_held_by_dd_channel': 13, 'n_scored': 1482, 'below_closed_form': -6}`. The
belief-side band has neither. Same artefact, same writer, same components dict.

---

## 5. Severity: **LATENT**, and the reason is uncomfortable (inferred from §2–§4)

The strip is currently **protective**. Two of the three fields that reach nobody are fields another
pass has independently measured as wrong on exactly this book:

* `scored_company_is_inert` — D30 pass 6 (`7466402f6`) measured it reading the invoice population
  where the belief edges are read off failures, wrong by 91 days at the step where the two disagree;
* `memory_blind_band_days` — the frozen literal `(-308, -100, -1, 1, 500)` for `belief` and
  `(-309, -308, -100, -1, 1, 500)` for `belief_population_mix`, both `DIMENSION_DRIFT_RESOLUTION`
  constants measured on the **offline** `n=300`, `window=400` scenario. The live book's own bound is
  `book_bound_floor_days` = **2623d** against a **6000d** company (31 observed failures, oldest
  3378d, headroom 2622d). On the 40×6 fixture above the same literal sits against a bound of 5819.
  *(Both literals gained `-307` on 2026-08-22, D27 BUILD pass 4: the never-forgets witness added to
  `book_memory_grid` made the sweep score a drift it had never visited, and it is invisible. The
  band is one member wider on each entry; nothing else in this section moves, and neither component
  is published.)*

So no published figure is wrong today and no lane is held. **That is an ordering constraint, not a
reprieve:** publishing these components before D30's repair lands would hand a machine reader a
known-wrong inertness verdict and a band from a different book, with a `dimension_caveats` control
that would not notice either. The two repairs are coupled and D30's goes first.

## 6. The class, stated so it is not re-derived

A **suffix used as a class guard** is sound exactly when the suffix names the class. This repo
already relies on that and gets it right one file over: `simplifications_store.is_note_field` uses
`field.endswith("_note")` and defends it as *"what makes this a class guard rather than an instance
list"* — and there the class genuinely **is** "note fields", so the spelling and the membership are
the same question. In `caveats_by_dimension` the class is *"a limit that must reach the reader"* and
the spelling is `_caveat`, so a limit that is a tuple rather than a sentence is out of scope by
construction and its control has no subject.

## 7. Open leads, ranked, none taken here

1. **(D30's, blocking this one)** repair `scored_company_is_inert` / `scored_company_headroom_days`
   onto the failure population. Already filed:
   `WORKER_FINDING_THE_INERTNESS_FLAG_IS_BLIND_TO_THE_POPULATION_ITS_OWN_FUNCTION_NAMES_AS_THE_EDGE_SETTER_2026-08-18`.
2. **(D27's, BUILD, parked)** make `memory_blind_band_days` book-derived with a
   `..._measured_on` provenance stamp, copying the shape `recon_saturation_band_measured_on` already
   ships in the same dict — this is the smallest change that makes the field publishable at all.
3. **(harness)** the lift's declared scope should be *what a dimension publishes as a limit*, not
   *keys ending `_caveat`*; the cheapest honest form is a declared per-dimension publish-set with the
   suffix rule as its default, so the control's subject stops being the spelling. Note this must
   re-measure `PUBLISHED_GAP_CONSUMERS` — `CAVEAT_LIFT_DIMENSIONS`' own comment records that
   publishing `ageing.ordinal_direction_caveat` would move that figure's declared precision, and the
   same hazard applies to any widening.
4. **(unranked, single instance)** the two-channel split itself — `note` for numbers, `components`
   for caveats — is nobody's declared design; it is the residue of a writer that writes one dimension
   and splices the rest. Whether that seam should exist is a bigger question than this atom.

---

## 8. Preserved verbatim: the pause note this pass compacted

The store's note tenant for this atom stood at **32,760 of 32,768 bytes** (8 bytes of headroom) —
measured and filed on 2026-08-18 as
`WORKER_FINDING_AN_ATOMS_NOTE_TENANT_IS_EIGHT_BYTES_FROM_ITS_CAP_AND_ITS_OWN_RESUME_TRIGGERS_HAVE_NOWHERE_TO_LAND_2026-08-18.md`.
That finding recommended, for exactly this situation: *"a new dated DISCOVER doc under `docs/design/`
(unbounded, already this atom's convention for the substance of every pass) with a one-line pointer,
and to buy that pointer's bytes by compacting `discover_pause_note` — the newest note … so no other
pass's record is touched."* That is what this commit does, and the compacted text is reproduced here
**in full** so the honest-history convention loses nothing — it moves from a byte-bounded tenant to
an unbounded committed file:

> PAUSED 2026-08-18 (DISCOVER/FRAME lane; NO BUILD; SELF_INTERRUPT_DISCIPLINE judgment, not a
> finding; terse to fit the note-tenant budget). Six passes over four days DERIVED, not just swept,
> this atom's account: the origin defect (window=400 sits the scored company 308-309d inside its
> blind band; published belief bit-identical to never-forgets, both sides), the repair with four R15
> criteria, a constant-provenance census, the render-site population defect, the book-span ceiling,
> and edge=span+buffer, source-derived and bisection-confirmed. Pass 5's 4 STILL-OPEN items are not a
> next D27 pass: ageing edge is D29's per pass 5's own text; span x buffer and a third book shape are
> confirmation sweeps on an already-derived law; the seed sweep ran one register over, remedy handed
> to D28/D31, and D27's artefacts are source-derived not seed-fit. D28 BUILT today; D29/D30 hold live
> DISCOVER, D30's own_draw_size_axis already the closest population sweep. RESUME ON: BUILD opening,
> a D29/D30 edge move reopening the origin question, or a director/advisor steer. Not a hold. LEVEL
> STAYS L0, deliverable epoch-gated.

**R12:** no published number was tuned, and none moved. What moved is what this atom knows about
where its own apparatus goes.
