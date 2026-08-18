# DISCOVER — D27: the published side has D27's own defect an order of magnitude worse, and the book constructor forbids ever testing it

**Atom:** `D27_belief_window_saturates_on_this_book` (lane `D_billing_metering`, epoch 3, `loop_stage: idle`)
**Pass:** fourth DISCOVER pass, 2026-08-18, worker tick, DISCOVER/FRAME lane.
**NO BUILD CODE.** The atom is epoch-parked (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1); its
deliverable is a reshape of `tools/couple_w2_11_d5.py`, which is not drawable. This doc is a
measurement, not a change: nothing in the repo was edited to produce any figure below.
**Lead taken:** the third DISCOVER pass
(`D27_RENDER_SITE_POPULATION_DISCOVER.md` §7) left three things named rather than absorbed. The
first was *"`months=6` never varied"*. This pass varies it, and the variation turned out to
reach past the render sweep into D27's own subject.

**Headline (R9: every figure below is `observed-with-evidence`, measured 2026-08-18 against
shipped `LivePaymentTriad.measure_and_write` / `measure_component_render_sites` /
`check_component_render_sites`, with only the book spec and the consumer's window substituted):**

> `_publish_one_book` writes its due dates as `date(2020, m, 28)`, so `months` is capped at **12**
> — `months=13` raises `ValueError: month must be in 1..12`. The longest book this module can
> express therefore spans **335 days**. The published side's belief-window saturation edge is
> **exactly the book's span plus 30 days** (measured at four spans, two customer counts, exact at
> every one), so the largest edge any expressible book can reach is **365**. The live composer
> holds `_RUN_SPANNING_WINDOW_DAYS = 6000`. **5,635 days — 94% — of the memory the published
> artefact is scored against cannot be reached by any book this constructor can build, by
> construction rather than by choice of constant.** And the equality that states it: today's
> published `belief` is bit-identical to the same company built with a window of 60,000 days, so
> the figure on the Proof door **is** the never-forgets company's figure.

---

## 1. The ceiling nobody declared (R9: observed)

`_publish_one_book` (`tools/couple_w2_11_d5.py:6890`) builds every book the artefact-side sweeps
grade:

```python
for m in range(1, int(spec["months"]) + 1):
    triad.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28), ...)
```

The month index is a **calendar month of one hard-coded year**. Measured:

| `months` | outcome |
|---|---|
| 1–12 | a book spanning `date(2020, months, 28) - date(2020, 1, 28)` days |
| 13 | `ValueError: month must be in 1..12, not 13` |

So `months` carries a hard ceiling of 12 and a maximum span of **335 days**. That ceiling is
declared nowhere: not in `_PUBLISHED_BOOK_SPECS`'s type (`Tuple[Dict[str, int], ...]` — an
unbounded int), not in `_publish_one_book`'s docstring (which explains at length *why only the
book is substituted*, and never that the substitution has a range), not in `published_books`, and
not in any test. The one test that passes custom specs
(`tests/tools/test_couple_w2_11_d5.py:6990`) uses `months: 4`, inside the ceiling.

This is the fourth constant in this module found to set an instrument's resolution from outside
every census built to find such constants, and the second field of the same constant — the third
pass found `_PUBLISHED_BOOK_SPECS` invisible twice over (private **and** `AnnAssign`) to the
subject rule proposed to extend the census. `months` is invisible a third way: it is a **dict key
inside** that constant, so even an AST rule that walked `AnnAssign` and dropped the `_` filter
would see one tuple-of-dicts constant and not the two independent levers inside it.

## 2. The saturation edge is the span plus thirty days, exactly

Method: the shipped composer driven end to end, `LivePaymentTriad(dd_failure_window_days=W)` the
only substitution; the five register carriers read exactly as `measure_component_render_sites`
reads them (`PUBLISHED_GAP_CONSUMERS[dim]["carrier"]`). "Edge" = the smallest `W` at which every
larger `W` publishes the baseline, bisected against `W=6000`.

| book | span | **edge** | span + 30 | `belief` at the edge | days of shipped memory unreachable |
|---|---|---|---|---|---|
| 30×3 | 60 | **90** | 90 | 0.1086957 | 5,910 |
| 30×6 | 152 | **182** | 182 | 0.1346154 | 5,818 |
| 150×6 | 152 | **182** | 182 | 0.14705882352941177 | 5,818 |
| 170×6 | 152 | **182** | 182 | 0.14193548387096774 | 5,818 |
| 30×9 | 244 | **274** | 274 | 0.1428571 | 5,726 |
| 30×12 | 335 | **365** | 365 | 0.1333333 | 5,635 |
| 150×12 | 335 | **365** | 365 | 0.14666666666666667 | 5,635 |

Exact at every row, and **independent of customer count** — 150 and 170 give the same edge, which
is what makes this a property of the constructor rather than of a sampling accident. The edge is
the book's span plus the fixed offset between a due date and the failure's value date; nothing in
the module states it, and the relation is what turns the undeclared `months` ceiling into a
statement about the window: `edge ≤ 365` for every book that can be built, against a shipped
window of 6000.

**Below the edge the window is not inert — it is the single largest lever on the figure.** On the
shipped first book (150×6), `belief` runs 0.5000000 at `W=1` to 0.1470588 at `W ≥ 182`: a factor
of **3.4**. `belief_population_mix` runs 0.9066667 to 0.2666667, a factor of **3.4**. So this is
not a dimension insensitive to its one company parameter. It is a dimension whose entire dynamic
range sits in `[1, 365]` and which is graded at 6000.

## 3. The equality that states the finding

At `W = 60000` — a memory 164 times longer than any expressible book — 150×6 publishes

```
belief = 0.14705882352941177      belief_population_mix = 0.26666666666666666
```

bit-identical to what the module publishes **today** at `W = 6000`. Today's published belief
figures *are* the figures of a company that never forgets a failed collection. That is the same
sentence D27's FRAME wrote about the scored side ("today's figure IS the never-forgets company's
figure") reproduced on the artefact side with a different constant, a different stated reason, and
a factor of 16 more headroom.

The direction matters and is the one D27 named: a company that never forgets keeps a recovered
customer in collections. The published number cannot distinguish that company from the scored one.

## 4. The docstring's stated claim is TRUE — measured, and it is not cover for the two dimensions it is not about

`background/live_payment_triad.py:66-76` states two things. Both were put on trial and **both
hold** (150×6, `W=1` against `W=6000`):

| dimension | `W=1` | `W=6000` | |
|---|---|---|---|
| `detection` | 0.11818181818181818 | 0.11818181818181818 | **inert** |
| `ageing` | 0.246974 | 0.246974 | **inert** |
| `detection_latency` | 2.135447 | 2.135447 | **inert** |
| `belief` | 0.5 | 0.14705882352941177 | moves |
| `belief_population_mix` | 0.9066666666666666 | 0.26666666666666666 | moves |

The docstring's *"the DETECTION headline … is NOT window-limited, so the headline is
window-independent regardless"* is correct, and so is *"the window only affects
`arrears_risk_belief`, which feeds the companion BELIEF gap"* — exactly two of five move, and they
are the two D27's map note names. Recording a verified claim is the point: the defect is not that
the docstring is wrong.

The defect is what the true claim is doing. Its stated reason — *"over a multi-year live run it
must span the whole run so the belief-severity count is on the SAME all-time basis as the
truth-severity count"* — is a statement about **the live multi-year run**, and it is defensible
there. The artefact-side sweeps do not run a multi-year book; they run six months, and cannot run
more than twelve. Nothing anywhere records that the same choice costs the two belief dimensions
their whole resolution *on the population the control actually grades*. That is D27's class
stated in one line: **a design note stood in for a measurement**, and the note is about a
different population than the one the number is published from.

The docstring even names the parallel itself — *"the offline scorer's own 400-day window covers
its whole 3-period scenario for the identical reason"* — so the two saturations are known to be
the same choice. What was never written is that it is the same *defect*.

## 5. What `months` does to the shipped control (run, not reasoned about)

The shipped pair anchored at `(150, 170)`, `months` swept 1–12, through unmodified
`measure_component_render_sites` + `check_component_render_sites`:

| `months` | sites (ageing / belief / mix / detection / latency) | violations |
|---|---|---|
| 1 | 0 / 1 / 1 / **0** / 1 | **4** |
| 2 | 2 / 1 / 1 / 1 / 1 | **1** |
| 3 | 1 / 1 / 1 / 1 / 1 | 0 |
| 4 | 1 / 1 / 1 / 1 / 1 | 0 |
| 5 | 1 / 1 / 1 / 1 / **0** | **1** |
| **6 (shipped)** | 1 / 1 / 1 / 1 / 1 | **0** |
| 7–12 | 1 / 1 / 1 / 1 / 1 | 0 |

**Three of the twelve expressible values (25%) break a control that is correct and unchanged.**
The failures are the third pass's finding reproduced on the *other* field of the same constant:

- **`months=5`** loses `detection_latency`'s only render site, and the control says *"declares a
  2dp render into `note` that this scoring does not produce — a render site nobody can find cannot
  be what set this figure's epsilon"*. The register is right; the book landed where the figure does
  not render. The message names the register.
- **`months=1`** publishes `detection = 0.0` exactly, quantises both `ageing` and `detection` at
  1dp, and emits four violations — two of them the "digits past that are a decoration" message
  about a register that has not changed.
- **`months=2`** finds `ageing` rendered at 1dp into `note`, undeclared.

So the wrong-side attribution the third pass measured across `n_customers` is not a property of
that field: it is a property of the book-spec constant. Both of its levers can move a correct
register into a debt message, and neither is pinned, censused, or bounded.

**On the shipped value it does not bite**, and that is stated rather than buried: `months=6` gives
five sites and zero violations, and `months=3,4,7..12` do too.

## 6. Why this is D27's class and not a fix on sight (R12, self-interrupt discipline)

- **No value change is proposed or implied.** 6000 is not criticised as a number and no window is
  recommended; `months=6` is not defended by its output and no other value is proposed. Choosing
  `months` *because* it gives `detection_latency` a site would be selecting the population to
  green the control, which is the defect one level up.
- The remedy is a **recorded measured reason** and a resolution the instrument can state, which is
  the reshape this atom is. Changing either constant moves every published belief figure on this
  pair — a mint, not a fix.
- This is the same boundary as D27, D25 and D26, one population further out: **the published book
  has no event sitting beside the line the live composer reads**, and unlike the scored side it
  *cannot be given one* without changing the constructor, because the ceiling is 335 days and the
  line is at 6000.

## 7. What a BUILD would land, and the mutation that proves each control can fail (R15)

1. **The book spec's range is declared and enforced, not discovered by `ValueError`.**
   `months` carries a stated maximum and `_publish_one_book` refuses an out-of-range spec with a
   message naming the ceiling and its cause (a single hard-coded year).
   *Mutation:* restore the bare `date(2020, m, 28)` and pass `months=13` — the control must fail
   with the ceiling named, not with `month must be in 1..12`. *Fail-open check:* passing
   `months=12` must still succeed, or the control has bought its pass by refusing everything.
2. **The published side owes a MEASURED window-resolution reading, on its own book.** The
   artefact-side sweep records the saturation edge for the book it actually publishes and the
   window the composer actually holds, and states the headroom — the same debt the scored side
   already carries via `measure_belief_window_resolution`, on the population the door reads.
   *Mutation:* substitute a window inside the edge (e.g. 90 on a 6-month book) — the reading must
   move; substitute 60000 — it must not, and the control must say so rather than passing silently.
   *Independence:* the edge is derived from the book's own event dates and the composer's declared
   window, never from any severity threshold (the D20/D21 tautology).
3. **A saturated belief dimension is a VISIBLE state on the published artefact.** A dimension whose
   carrier is bit-identical to the infinite-memory company's is stamped as such where the reader is
   handed the figure, not left to be inferred.
   *Mutation:* build the composer inside the edge — the stamp must clear. A stamp that is always
   present is the fail-open this instrument has produced before.
4. **The "site nobody can find" violation distinguishes an undischarged register from a book that
   does not discriminate.** Same criterion the third pass wrote for `n_customers`, now with a
   second witness: the message must be different for `months=5` (correct register, blind book) than
   for a genuinely stale declaration.
   *Mutation:* stale a declaration deliberately and confirm the two messages differ; run the
   control on `months=5` and confirm it does not name the register.

## 8. What this pass does not settle

- **`n_customers` × `months` jointly.** Only the anchored pair was swept per axis. The third
  pass's 1,830-pair base rate over `n_customers` was at fixed `months=6`; the joint surface is
  unmeasured.
- **The other two open leads from pass 3 are still open**: a third book is unmeasured, and the
  four measurement functions defaulting to `RESOLUTION_SEEDS` are still unswept.
- **The 30-day offset in `edge = span + 30` was measured, not derived.** It is exact on six books
  and its mechanism (the fixed due-date-to-value-date lag) is inferred, not proven.
- **Owners, handed over in writing (unchanged):** D28 keeps the register declarations, D31 the
  undefined-reading witness. D27 owns the census shape and now, on this evidence, the published
  book's span.

## 9. Reproducing the measurement

```python
# All shipped except the book spec and the consumer's window.
import background.live_payment_triad as lpt
from background.live_payment_triad import LivePaymentTriad
import tools.couple_w2_11_d5 as C

# §1 -- the ceiling
LivePaymentTriad().record_period(due_date=date(2020, 13, 28), ...)   # ValueError

# §2/§3 -- the saturation edge, bisected against W=6000 on the shipped carriers
#   triad = LivePaymentTriad(dd_failure_window_days=W); drive record_period over
#   the spec; measure_and_write; read PUBLISHED_GAP_CONSUMERS[dim]["carrier"].
#   -> edge == span + 30 at every book tried; belief(6000) == belief(60000)

# §5 -- the shipped controls over months 1..12 at the (150, 170) anchor
books = [publish(150, m), publish(170, m)]
C.check_component_render_sites(C.measure_component_render_sites(books=books))
```

Runtime: the window bisect is ~11 composer runs per book (~1s each at n=150); the months sweep is
~30s end to end.

## 10. Level

**LEVEL STAYS L0, and that is correct rather than a hold.** L1 is "has been BUILT in any form"
(`MATURITY_MAP.md` §3) and this atom's deliverable is a reshape of `tools/couple_w2_11_d5.py`,
which is epoch-gated. The doc is not this atom's deliverable, so DISCOVER cannot move it.
