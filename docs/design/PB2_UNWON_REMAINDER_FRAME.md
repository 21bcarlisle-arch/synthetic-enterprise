# PB2 FRAME — the unwon remainder: the object exits (b), (c) and (d) all need

**Atom:** `PB2_opening_book_won_not_assigned` (`docs/design/maturity_map.yaml`, lane
`W2_customer_generator`, epoch 2, `loop_stage: idle`, `provenance: director_ruling`).
**Predecessor pass:** `docs/design/PB2_OPENING_BOOK_DISCOVER.md` (2026-08-13, DISCOVER — the size
and its anchor). **Sibling:** `docs/design/PB1_POPULATION_TARGET_DISCOVER.md`.
**Source ruling:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`.

**This is a LANE-3 FRAME pass. No BUILD.** The atom is `idle`, which parks it for BUILD only
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1). `level_current` stays **0**, `loop_stage` stays
`idle`, no `file_scope` path is touched, no curriculum value moves (R13). Everything below is a
design and a set of named preconditions; none of it is wired.

**Why hold the level at 0 when the deliverable is a document.** PB2's `gain` is *"a 13-account book
stops being a stress test of the money machinery and starts being a small supplier"* and its
`level_target` is 3. Exit (a) is proposal-shaped and the DISCOVER pass discharged it; exits (b), (c)
and (d) are properties of a running seam, so no document can move this atom's level. Contrast
D30/EP19, where the register *was* the deliverable. The doc is the input to a build, not the atom.

---

## 0. What this pass adds

The DISCOVER pass ended on a blocker it stated but did not design out:

> Exit (d) is unsatisfiable by construction today. `simulation/live_population.py:161-177` renders,
> appends and registers every drawn `SyntheticCustomer`, so the drawn population **is** the book. A
> subset test today asserts `|book| == |population|` and passes — the tautology R15 names first.

Re-read at this pass's HEAD, unchanged: `live_population()` ends `register_drawn_points(drawn)` then
`return list(CUSTOMERS) + drawn`. Confirmed still true.

This pass contributes four things:

1. **A second structural blocker, new here: there is no join key.** Even once a remainder exists,
   exit (d) — *"the opening book is measured to be a genuine subset of the drawn population"* —
   cannot be evaluated, because the two id grammars share nothing. `simulation/population_draw.py`
   mints `SYN-{year}-{i:03d}`; `simulation/premise_population.py:654` mints `P{i:04d}`; and
   `SyntheticCustomer` (fields listed at its dataclass) carries **no premise field at all**. Subset
   is a relation between sets of the same key. Today it is a relation between two id spaces that
   have never met. §3.
2. **The design of the remainder** — what it is, where it lives, and the inversion that produces it
   (§1–§2).
3. **The subject the existing wall instruments need** for exit (c), and the two mutations exit (d)'s
   control must survive (§4).
4. **A correction to the DISCOVER pass's cost sentence**, which PB1 queued and which belongs to this
   atom's record rather than PB1's (§5).

---

## 1. The inversion: draw the stock, not the winners

Today the SIM draws **winners**. `iter_acquisition_events(base_seed, ..., acquisitions_per_year_lambda)`
draws `Poisson(lambda)` *acquisitions* per year and yields a `SyntheticCustomer` for each — an
account that is already won at the moment it is minted. There is no losing. `lambda` **is** the book
size, in the plainest possible sense: it is the parameter whose value the book equals in
expectation.

That is why the DISCOVER pass named "raise `lambda` on the existing append-the-whole-cohort seam" as
the forbidden implementation (§f). It is forbidden not because the number would be wrong but
because a book that equals a parameter is *assigned*, and the ruling's word is *won*.

**The frame is to move the draw one stage upstream.** The SIM draws the **stock** — the addressable
premises. The company issues **quotes** against that stock. The funnel decides which quotes become
accounts. The book is what comes out.

```
   TODAY                          FRAMED
   ─────                          ──────
   lambda ──> winners             stock ──> prospects ──> quotes ──> funnel ──┬─> WON  ──> book
              (= the book)        (SIM)                   (company spend)     └─> LOST ──┐
                                                                                         │
                                  remainder = stock − book ────────────────────────────────┘
```

Three properties fall out, and each of them is an exit criterion:

- **Book size stops being a parameter anywhere in the tree.** There is no `book_size`, and `lambda`
  no longer names one. What the company chooses is *campaign volume* — how many quotes it issues,
  which is a spend decision it already owns (`saas/growth_mandate.py:82::should_attempt_acquisition`
  is already the awareness/consideration gate, by `simulation/acquisition_funnel.py`'s own top-of-file
  scope statement). Book size becomes a **measurement of what the campaign won**. That is exit (b),
  and it is also the whole precondition for PB3 — a number that is an outcome can be lost.
- **The remainder exists by construction**, because quotes lose. At the shipped funnel's
  `p(win|quote) = 0.171456`, roughly five in six quoted premises stay unwon. Exit (d) becomes a
  measurable claim rather than a tautology.
- **The population target becomes load-bearing** rather than decorative: PB2's derived floor
  `N_pop ≥ ⌈5.8324 × N_book⌉` is the statement that *the funnel must have somewhere to lose*. On
  today's seam that floor means nothing, because nothing is lost.

### 1.1 The stock already exists, and it has the property this needs

`simulation/premise_population.py::draw_premise_population(n, *, base_seed, as_of)` already draws a
premise stock raked onto three published England housing-stock marginals, and its docstring records
the property that matters most here:

> *"Draw `n` premises. Growing `n` APPENDS — `P0007` never changes."*

Each premise is drawn from its own `premise_id`-keyed substream (`_substream(base_seed, f"{premise_id}:cell")`
and siblings), so the draw is **append-stable**: growing the population never re-rolls an existing
member. This is exactly the property a remainder needs — the unwon set must be able to grow without
disturbing the book that was already won out of it, or every book-size measurement is taken against
a different world than the one before it. It is also C-S2 (RNG substream discipline) already
satisfied, not owed.

What the stock does **not** have is a consumer. PB1 established it: `premise_population` is read only
by `tools/couple_fabric.py`, a research instrument no run touches. This frame gives it its first
production consumer, which is the cheapest available way to close PB1's "two populations, disjoint"
finding — it needs no third population.

---

## 2. Where the remainder lives, and where it must not

**The remainder is SIM-side state with no company-side name.** It is not a table the company holds
with a `won` flag set false; a supplier does not have a list of the households it has not signed.
The unwon set is world truth, and the company's only trace of it is the outcome of quotes it
actually issued.

| | SIM (world truth) | Company |
|---|---|---|
| the full stock | **holds it** | never sees the set, never sees its size |
| a premise it has quoted | holds truth | holds its own quote record + the funnel outcome |
| a premise it has won | holds truth | holds the account (`supply_book`) |
| a premise it has never approached | **holds it** | **has no object for it at all** |

The bottom row is the wall. It is also the row that does not exist today, which is why no control
covers it — you cannot leak a set that is empty.

**The registration point is where a grant would sneak back in.** `live_population()` currently ends
with `register_drawn_points(drawn)`, registering the *entire drawn cohort* on the supply book at the
seam. That call was added for a real reason (the home-move path needed `registered_point()` to
resolve a drawn account, per its own inline note), and under this frame it becomes the single most
dangerous line in the file: registering the stock is granting the book. Under the frame,
`company/interfaces/supply_book.py::register_acquired_point` is reached **only on a funnel win**, and
`register_drawn_points` either loses its caller or has its subject narrowed to won accounts. Naming
it here so the build cannot reintroduce the grant by inheriting a line nobody re-read.

### 2.1 What the company may see before it quotes

A supplier does not quote blind, so the prospect seam is not empty — but its contents are a wall
decision and must be argued, not assumed. Proposed observable set at prospect stage, to be checked
against the fidelity oracle before build (it is a regulation-commons question, and this pass does
not settle it):

- **Legitimately observable** — region, commodity, and the meter's read cadence are things a
  supplier learns from the industry systems on switching enquiry; EPC band and property type are on
  a **public register** in reality, which under the regulation-commons doctrine makes them readable
  text rather than a leak. `premise_population` already models EPC coverage as partial
  (`EPC_COVERAGE_SHARE = 0.60`), which is the right shape: the company sees a certificate where one
  exists and nothing where one does not.
- **Never observable** — `Household.nssec`, tenure, and the whole `Cohort` object (green stance,
  price sensitivity, channel preference). These are the segmentation ground truth the canonical wall
  ruling puts entirely behind the wall, and the company's job is to *discover* them from outcomes.

The line to hold: the company may see what a public register or an industry query would tell it,
and must infer everything that determines whether the household will actually say yes.

---

## 3. The join key — the second blocker, and the smallest thing that fixes it

Exit (d) says *"the opening book is measured to be a genuine subset of the drawn population."*
Subset is a relation over a shared key. There is none:

| | id grammar | source |
|---|---|---|
| population (stock) | `P0004` | `simulation/premise_population.py:654`, `f"P{i:04d}"` |
| book (accounts) | `SYN-2016-001` | `simulation/population_draw.py`, `f"SYN-{year}-{i:03d}"` |

`SyntheticCustomer`'s fields are `customer_id, acquisition_date, segment, commodity, payment_method,
consumption_band, eac_kwh, region, tariff_type, data_regime, acquisition_type, cohort` — **no premise
reference**. So even with a remainder in place, a subset control would have nothing to compare, and
the shapes available to a build under pressure are exactly the two R15 names first: compare the
*counts* (`|book| < |population|` — passes for two unrelated sets, wrong subject) or compare the sets
after mapping one grammar onto the other by position (tautology, since position is what generated
both).

**The fix is a supply-point identity, not a new id.** The account an acquisition creates is an
account *at a premise*: the won `SyntheticCustomer` must carry the `premise_id` it was won at, so
`book_premise_ids ⊆ stock_premise_ids` is a set relation over one key. This is also the honest
domain model — a UK supply point is identified by its metering point, which belongs to the property
and survives the customer leaving. It is what makes the home-move path (already built, already
buggy once at this seam) coherent rather than coincidental.

The 13 static `CUSTOMERS` have no premise and predate the stock. They are **out of scope of the
subset claim** and the control must say so explicitly by construction — an exclusion that is
declared and bounded, not an exclusion that quietly makes the verdict green
(the failure shape catalogued in `feedback_an_exclusion_that_makes_your_own_verdict_green`).

---

## 4. The controls: one instrument gets a new subject, one gets a new pair of mutations

### (c) The wall — no third instrument

The DISCOVER pass established this and it stands: `tests/architecture/test_epistemic_wall_ratchet.py`
is the static company↔sim import ratchet, R15 both ways; `tests/simulation/test_live_population_seam.py`
carries the runtime half for hidden ground truth with its own falsifier
(`test_the_company_import_guard_can_fail`). PB2 supplies a **new subject**, not a new instrument —
this repo's characteristic failure is an orphaned control, not an absent one
(`feedback_a_classs_remedy_may_already_exist_unwired`).

The subject is **roster membership**, and the static ratchet cannot see it: the remainder is *data*,
not an import, so a company module that never imports `simulation.premise_population` can still be
handed the unwon set by a caller. The runtime guard is the half that must grow. Its new assertion,
in the shape the existing one already uses for `cohort`:

- a company-side read of the unwon set REDs — and its falsifier, a deliberately leaked remainder,
  must make the guard fire. Both directions, per the ruling's non-negotiable.

### (d) The subset — the two mutations that decide whether the control is worth anything

A subset control passes trivially on a broken world. Two mutations, both required:

1. **Register an unwon premise on the book.** The control must RED. Without this it does not test
   subset at all — it tests that two sets exist.
2. **Mint a book account whose `premise_id` is not in the stock.** The control must RED. This is the
   one that catches the frame collapsing back to today's seam, where accounts are minted rather than
   won.

And one assertion that is not a mutation but a precondition: **`|remainder| > 0`**. A control that
passes when the remainder is empty is the fail-open shape — it would have passed every day of this
atom's life to date, on a world where the property is definitionally false. The remainder being
non-empty is the *first* thing to assert and the thing that distinguishes this from the tautology
the DISCOVER pass found.

---

## 5. Correction to the DISCOVER pass: the 860 bytes is a customer, not a premise

PB1 §(g) queued this against PB2's record and did not edit it (an in-flight document belonging to
another draw). It belongs to this atom, so this pass discharges it.

`docs/design/PB2_OPENING_BOOK_DISCOVER.md` reads the AO12 `population_draw` per-unit cost correctly
once and incorrectly twice:

- line 106 (correct): *"860 bytes RSS/customer"*
- line 113 (wrong): *"The population draw costs ~860 bytes per **premise**"*
- line 198 (wrong): *"at 860 bytes RSS/**premise**, 18,756 premises cost ~16 MB to draw. **The world
  is affordable at the target book's floor**..."*

Read from `docs/observability/scale_probe_10k/report.json`, the stage's own fields are
`"unit": "customer"`, `"units_completed": 10258`, `"per_unit.rss_bytes": 859.6888282316241`, and its
`detail` says *"drew 10258 customers via simulation.population_draw"*. The measured subject is a
`SyntheticCustomer` from `simulation/population_draw.py`. A `DrawnPremise` from
`simulation/premise_population.py` is a **different class with different fields**, and PB1 §(b)
already established that the probe has **no stage for it**: *"there is therefore NO measured price
for a drawn premise anywhere in the report."*

This is R15's wrong-subject shape, and here it is load-bearing rather than cosmetic, because the
sentence it produces is an **affordability verdict**. Corrected:

> The per-premise draw cost is **UNMEASURED**, therefore **UNKNOWN**. PB1 exit (d) governs: an
> unmeasured stage is an unknown cost, not a zero. **"The world is affordable at the target book's
> floor" is withdrawn** — it is not supported by the artefact it cites.

Two things survive the correction, and it is worth being precise about which:

- **The count floors are untouched.** `N_pop ≥ ⌈5.8324 × N_book⌉` = 18,756 at target / 2,712 at the
  interim is funnel arithmetic and never used the byte figure.
- **The reframing survives in KIND but not in number.** "The expensive object is the book, not the
  world" rests on the *stage* the two objects reach: a won premise enters `settlement_build`, the
  stage AO12 measured dying at 465 customer-years; an unwon premise never does. That argument is
  structural and holds. The **~7,400×** multiplier attached to it does not — it divides a settlement
  cost by a customer-draw cost and calls the denominator a premise. The ratio is unknown until the
  premise stage is measured.

**The measurement that closes this is already named and already owed**: PB1 §(f) prerequisite (1),
*"one new AO12 stage whose subject is `premise_population.draw_premise_population`"*. This pass does
not take it — taking it here would produce a number with no instrument behind it, which is precisely
what PB1 refused to do and refused for the right reason.

---

## 6. What a build would need, in binding order

Nothing below is opened; this is the sequence a future BUILD draw inherits.

1. **The join key** (§3) — a premise reference on the won account. Everything else is unmeasurable
   without it, so it is first even though it is the smallest.
2. **The prospect seam** (§2.1) — the observable set, fidelity-oracle-checked before it is coded.
3. **The inversion** (§1) — quotes drawn against the stock, `lambda` re-homed to campaign volume,
   `register_acquired_point` reached only on a win, `register_drawn_points`' subject narrowed (§2).
4. **The controls** (§4) — the runtime wall guard's new subject, and the subset control with both
   mutations and the `|remainder| > 0` precondition.

**Preconditions carried forward from the DISCOVER pass, unchanged and still owed** (they were filed
as findings, not fixed, per `SELF_INTERRUPT_DISCIPLINE`): the draw saturates silently above
`lambda ≈ 745` (batching below saturation is mandatory — visible in the probe's own `detail`, which
records 41 batches of 250 for this reason); the `SYN` key set diverges from the static roster and
cost seven consecutive failed runs on 2026-08-13, so entrypoint hardening is a **precondition** of
any book increase rather than a follow-up; and the curriculum-arms-from-disk / code-arms-at-HEAD
asymmetry is inherited intact by any profile edit.

**And the governor still governs.** The DISCOVER pass's affordability verdict is unchanged by
anything here: 3,217 is 6.9× the measured `settlement_build` ceiling of 465 customer-years, so the
target is not affordable today and the interim — the largest N completing a green full shipped run,
by bisection, with 465 as the fail-closed cap — is what a build would aim at. Note the shape the
frame gives this: under the inversion, the *stock* can be at PB1's target while the *book* sits at
the interim, because the remainder never reaches the expensive stage. The two numbers stop needing
to be the same number. That is the frame's affordability contribution, and it is a structural claim
about which stage each object reaches — **not** a claim that the stock is cheap, which §5 has just
withdrawn.
