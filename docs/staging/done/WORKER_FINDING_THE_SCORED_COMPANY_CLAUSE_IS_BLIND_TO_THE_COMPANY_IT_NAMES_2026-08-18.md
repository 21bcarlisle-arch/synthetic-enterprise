# WORKER FINDING — the clause that names the scored company's memory is blind to the company it names, and on the live path no belief caveat is published at all

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Raised:** 2026-08-18, worker tick, D30 DISCOVER pass 4 (LANE 3 idle draw). Full evidence and
the sweep tables: `docs/design/simplifications/D30_the_belief_band_is_this_books_length.yaml`,
note 4.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) as well as of D30/D31, so leg 1 is drawable now. Leg 2 additionally needs
`background/live_payment_triad.py`, which is in NO atom's `file_scope` — stated rather than
implied, because that is why nobody has drawn it.
**Intended rank (P-1):** top of `D_billing_metering`, immediately behind the census repair that
landed 2026-08-18 — this is the half of the same register that repair did not reach, and one leg
of it is live on a public door.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE). The draw that found it was
DISCOVER/FRAME only.

## Leg 1 — three fields called `scored_company_*` are read off a harness constant, not off the scored company

`measure_scenario_constant_census` publishes the graded company's place in the belief band:

```python
window = DD_FAILURE_WINDOW_DAYS                                    # line 6551
...
"scored_company_window_days": window,
"scored_company_headroom_days": None if oldest is None else window - oldest,
"scored_company_is_inert": None if oldest is None else window >= oldest,
```

`DD_FAILURE_WINDOW_DAYS` is a module constant (400). The function's signature is
`(records, as_of, census=None)` — **it never receives the consumer**, so it cannot read the
company whose memory those three fields report. `score_triad`, which calls it, holds that
consumer as its second positional argument.

Measured through the DECLARED `organ_failure_window_drift_days` parameter (never a monkeypatch),
n=300, seed 7 — the company's memory moved over a 120× range and the census did not move at all:

| drift | company's actual W | book's oldest age | census `window` | census `headroom` | census `is_inert` | **truth** |
|---|---|---|---|---|---|---|
| 0 | 400 | 92 | 400 | 308 | True | True |
| −320 | **80** | 92 | 400 | 308 | True | **False** |
| −350 | **50** | 92 | 400 | 308 | True | **False** |
| +200 | 600 | 92 | 400 | 308 | True | True |
| +5600 | **6000** | 92 | 400 | 308 | True | True |

Bit-identical on every row. The published sentence is byte-identical too, at W=50 as at W=400:

> AND THE SCORED COMPANY SITS OUTSIDE IT: it holds 400d of memory, 308d past the top of the
> band, so every belief figure here is read at a point where the one company parameter these
> dimensions depend on is inert by construction (reported, never tuned — R12).

**And the figure it rides on falsifies it.** At W=50 the company is 42 days INSIDE the band, and
the belief dimensions move accordingly — `score_triad`, n=300, three seeds:

| seed | `belief` at W=400 | `belief` at W=50 | `mix` at W=400 | `mix` at W=50 |
|---|---|---|---|---|
| 7 | 0.1519 | **0.4241** (2.8×) | 0.0800 | **0.1933** |
| 11 | 0.1914 | **0.4259** (2.2×) | 0.1033 | **0.2100** |
| 23 | 0.1353 | **0.4000** (3.0×) | 0.0767 | **0.1800** |

"Inert by construction" is published over a parameter that moves the headline figure by up to
three-fold. This is observed, not inferred: the drift is a declared parameter and the scorer is
the shipped one.

**Null control.** `measured_oldest_age_days` is 92 on all six runs and the book is untouched:
the perturbation moved the COMPANY, not the population. So the frozen 400/308/True is the
census being blind to its named subject, not the census correctly reporting an unchanged book.

**Both directions, and the repo really runs all three companies.** The shipped default is 90
(`company/billing/payment_observation_consumer.py:386`), the offline fixture holds 400, and the
live publisher constructs at 6000 (`background/live_payment_triad.py:119`, reaching `score_triad`
at line 678). Against the offline book's 92-day top, a 90-day company is genuinely inside the
band and is published as outside it; the live 6000 company is understated by 5600 days.

## Leg 2 — on the live publishing path neither belief caveat is published at all

`score_triad` attaches both caveats to the BELIEF dimension — `bel.note` and `bel.components`
(lines 10692-10708) — under a comment stating the D22 rationale explicitly: "the ledger writer,
the live wiring and the dashboard take `components` and never read `note`, so a limit only the
prose carries is one the machine strips off". The components are attached. They are attached to
an object the live wiring never writes: `PaymentTriadHarness.measure_and_write` writes the
DETECTION dimension only (`write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, headline, ...)`) and
splices the belief number in as a formatted string via `format_belief_summary`, which renders
rates and carries no caveat.

Read off the published artefact at HEAD, `docs/observability/coupled_gap_ledger.json`, entry
`W2_11_payment_behaviour_source`, measured 2026-08-18T00:46:01Z at commit `0a3113dfe`:

* it publishes `belief balanced error 0.1818` and the mix figure in its note;
* the note contains no occurrence of "band", "census", "resolution", "headroom", "memory" or
  "inert";
* `components` carries 19 keys and neither `belief_resolution_caveat` nor
  `scenario_constant_census_caveat` is among them.

**Positive control, same entry, same commit, same writer.** The detection-side caveats DO arrive
— `recon_saturation_caveat`, `recon_saturation_band_days` and `drift_resolution_caveat` are all
present and populated. The ledger is not dropping caveats; it is publishing the ones attached to
`headline` and never seeing the ones attached to `bel`. Belt-and-braces fastened to the wrong
object.

Repo-wide, neither belief caveat's name appears anywhere under `site/` or in any observability
artefact — only in design and register documents. The limit exists exclusively for readers of
the register, which is the audience the D22 comment says it was written to get past.

## Why it is BLOCKING rather than LATENT

Leg 1's clause is a live claim about the graded company, published in the caveat that exists to
tell a reader whether the belief figures can be trusted, and it is wrong in the direction that
says "you may ignore this parameter" for companies where the parameter is worth three-fold on
the figure. Leg 2 puts a live belief figure on a public door with none of the resolution
apparatus two atoms were built to attach to it.

This also corrects the "Not claimed" paragraph of the 2026-08-18 sibling finding, which stated
that the caveat travelling with a published belief figure is safe at any draw size. That is true
of the offline path. On the live path there is no caveat travelling with the figure at all.

## What a repair must show

1. `measure_scenario_constant_census` reading the scored company's window from the consumer
   `score_triad` already holds, so the three `scored_company_*` fields can differ between two
   companies scored over one book — with the drift sweep above as the axis, and a case that
   pins the window to the module constant proving the control goes green with the defect
   untouched (R15 both ways).
2. The `is_inert` switch falsified in BOTH directions: a company inside the band that the census
   calls outside it, and the live 6000-day company reported at 6000 rather than 400.
3. The two belief caveats reaching `coupled_gap_ledger.json` on the live path — asserted against
   the WRITTEN artefact, not against the `score_triad` result dict, because the result dict is
   where they already are and it is not the thing anyone reads.
4. A control that fails when a dimension carrying a caveat is not the dimension being written,
   so the next caveat attached to a non-published object is caught at the seam rather than by an
   Expert Hour reading the JSON.

## Not claimed

The band measurement itself is unaffected — `measure_belief_window_resolution` reads the scored
book and is correct on any population. Nothing here says the published 0.1818 is wrong; it says
the figure is published without the limits that were built for it, and that the limit which IS
published on the offline path states a company parameter it never read. No published number was
tuned, moved, or written by this pass (R12).

---

## REPAIRED 2026-08-18 (worker tick, BUILD; drawn as the RUNG-1c blocking finding of lane D_billing_metering)

Both legs built and landed together. Every claim below is `observed-with-evidence` from a run of
the shipped code; nothing here is inferred from the diff.

### Leg 1 — the three fields read the scored company

* `PaymentObservationConsumer.dd_failure_window_days` is now a public read-only property. It was
  private, and that was the whole mechanism of the defect: the private attribute was the only
  route to the real value, so every reader took the harness's module constant instead.
* `measure_scenario_constant_census(records, as_of, census=None, window_days=None)` takes the
  window. `score_triad` threads `consumer.dd_failure_window_days` into it **and into
  `measure_belief_window_resolution`**, which was blind at the same call site in the same way —
  the sibling half, repaired with it rather than left for the next Hour.
* The CLI's own census print (`--main`) passes `_cen_c`, the consumer that run scored. It was
  printing "the scored company's 400d memory" from the constant.
* New published field `scored_company_window_source` (`scored_consumer` / `harness_constant`):
  a defaulted 400 and a real 400 were indistinguishable on the artefact, which is what let the
  defect live.
* The caveat's `is_inert` branch had NO else. While the window came off the constant that branch
  was unreachable on every book the constant cleared, so the sentence could only ever say *"you
  may ignore this parameter"* — the one direction a reader must not be told wrongly. There is now
  an INSIDE-the-band sentence, and it says the belief figures MOVE with the parameter.

Measured on the shipped code, n=300, seed 7, through the DECLARED
`organ_failure_window_drift_days` (never a monkeypatch) — the sweep from the finding, re-run:

| drift | company W | census `window` | census `headroom` | census `is_inert` |
|---|---|---|---|---|
| 0 | 400 | 400 | 308 | True |
| −320 | 80 | **80** | **−12** | **False** |
| −350 | 50 | **50** | **−42** | **False** |
| +200 | 600 | **600** | **508** | True |
| +5600 | 6000 | **6000** | **5908** | True |

**Null control held:** `measured_oldest_age_days` is 92 on every row — the perturbation still
moves the COMPANY and not the book, so the fields now move for the right reason.

### Leg 2 — the caveats reach the written artefact

`measure_and_write` lifts every `*_caveat` component from each dimension in a declared
`CAVEAT_LIFT_DIMENSIONS` onto the headline it actually writes, as
`components["dimension_caveats"]`, and refuses to publish if any is missing.

**The first build was generic over EVERY dimension and the gate refused it — that refusal is
part of this record, not a detail.** `ageing.ordinal_direction_caveat` renders the ageing figure
at SIX decimals, and atom D36's entire ruling is that a 6dp site *nobody is handed* does not set
that figure's declared 3dp precision. Publishing it HANDS the reader that render, which would
move a published resolution claim and every floor derived from it as a side effect of a caveat
repair. Seven controls in the published-artefact family went red on exactly that, on the tree the
commit would have created. So the DIMENSION set is declared in one place with that reason beside
it, and within a declared dimension the lift stays generic by suffix — which is the half of the
genericity this defect class needs, since both instances are belief caveats and the next belief
caveat is caught without anyone naming it. `ageing` is excluded on purpose and
`test_the_lift_is_scoped_to_the_belief_dimensions_for_the_D36_reason` pins both the exclusion and
the fact that it is load-bearing.

**Residual, stated rather than buried:** widening the set to `ageing` is a real question (its
caveat is a limit a reader of the ageing figure should have), and it is now a conscious act that
must re-measure `PUBLISHED_GAP_CONSUMERS` first. It is NOT done here and nothing above claims it.

### R15 both ways

* `test_R15_the_census_goes_green_on_the_constant_with_the_defect_untouched` — called without a
  company the census still answers, still passes its own rules, and a real 400d company and a
  defaulted one differ in exactly one field: `scored_company_window_source`.
* `test_R15_MUTANT_a_caveat_on_an_unwritten_dimension_is_caught_at_the_seam` — a brand-new caveat
  fastened to `belief` is caught without anyone naming it; deleting the map entirely is caught
  harder, not read as a clean pass (fail-closed).
* `test_R15_MUTANT_deleting_the_lift_makes_measure_and_write_refuse` — mutates the shipped call
  path, not a hand-built `GapResult`.
* **This test caught a TAUTOLOGY in its own control, and the fix is the point.** Written the
  obvious way, `check_every_caveat_is_published` derived its expectation by calling
  `caveats_by_dimension` — the same helper the publisher uses. Neutering the publisher moved the
  expectation with it and the control passed. The checker now derives its expectation inline;
  those four duplicated lines ARE the independence, and the comment says so.

### What is NOT claimed

The band measurement is untouched and no published number was tuned (R12). This does not close
`WORKER_FINDING_THE_CONSTANT_CENSUS_IS_BLIND_TO_THE_LIVE_PATHS_OWN_WINDOW_2026-08-17`: the live
window now REACHES the published fields, but `_RUN_SPANNING_WINDOW_DAYS` is still not in
`SCENARIO_CONSTANT_CENSUS`'s AST-derived keyset and cannot be — that finding stays LATENT and
open. `docs/observability/coupled_gap_ledger.json` still carries the pre-repair entry; the new
components appear on the next `run_phase2b` write, and the repair is asserted here against a
ledger written by the shipped path in `tmp_path`, not against the stale live file.
