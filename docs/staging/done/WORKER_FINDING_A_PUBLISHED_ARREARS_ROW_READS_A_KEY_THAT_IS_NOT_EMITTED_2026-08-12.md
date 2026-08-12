# WORKER FINDING — the shadow page's arrears rows read a key nobody emits, and print 0.00% for every year

**Severity:** BLOCKING · **Lane:** D_billing_metering
<!-- Severity and lane normalised 2026-08-12 by a worker tick: `HIGH` is not one of OPS9's
     three tokens and `D_reporting` is not a lane in the map, so this was UNCLASSIFIED twice
     over. BLOCKING: a published page prints 0.00% arrears for every year off a key nobody
     emits -- a published figure IS wrong, not may be. Lane is the arrears/collections value
     stream, meter_to_cash = D_billing_metering. -->

**Date:** 2026-08-12
**Found by:** worker, while closing
`WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md` as a class
**Class:** one name, two numbers / a confident figure over a field that was never populated
**Status:** QUEUED — not fixed on sight (SELF_INTERRUPT_DISCIPLINE; the machine is not
blocked, and this is a different mechanism from the fail-open just closed)

## The claim, and how it is evidenced

`observed-with-evidence` (R9). Read from the tree and from the published artefact,
not inferred:

- `tools/population_anchor.py::_arrears_check_by_year` emits each year's rate under
  the key **`new_arrears_rate_pct`** (and `ic_arrears_rate_pct`). There is no
  `arrears_pct` key in the payload it writes to `site/state/population_anchoring.json`.
- `tools/generate_shadow_html.py:1599` renders that block with
  `format(check.get("arrears_pct", 0), ".2f") + "%"` — a key that is never emitted,
  so the default `0` is used **every time, for every year**.
- The published page agrees. From `site/shadow/sim/index.html` as it stands:

  ```
  Arrears 2023</td><td>0.00%</td><td><span class="rag-chip rag-amber">AMBER</span>
  Arrears 2024</td><td>0.00%</td>
  Arrears 2025</td><td>0.00%</td>
  ```

  The correct figures for those years, from the same run and a present ledger, are
  **30.8%, 46.2% and 0.0%**. Only the last one is right, and it is right by accident.

## Why it matters

1. **It is a published figure that has never been the figure it names.** The row is
   labelled "Arrears <year>" and shows a rate; the rate is a default, not a reading.
   R14's clock discipline is not the issue here — the number has no source at all.
2. **The RAG chip beside it is real.** `check.get("rag")` resolves correctly, so the
   row pairs a genuine AMBER/RED verdict with a 0.00% value that would justify GREEN.
   A reader reconciling the two sees a contradiction and has no way to tell which
   half is wrong.
3. **It survived the sibling fix.** The fail-open closed on 2026-08-12 makes an
   absent ledger render `UNAVAILABLE` rather than green — and this row will faithfully
   show `UNAVAILABLE` next to `0.00%`. The class guard added there is scoped to
   surfaces that *derive* a population rate; this surface only *renders* one, so it is
   correctly outside that guard and correctly still broken.
4. **The defect shape is a missing-key default, and it is silent by construction.**
   `dict.get(key, 0)` cannot distinguish "the producer renamed this field" from "the
   value is genuinely zero" — the same indistinguishability that made the fail-open
   invisible, at a different seam.

## Suggested fix (not applied)

- Read `new_arrears_rate_pct` (the emitted name), and decide deliberately whether the
  headline should be the overall rate or `ic_arrears_rate_pct` — the RAG beside it is
  computed from the **10-year aggregate IC rate**, so pairing it with the per-year
  overall rate is a third, separate mismatch worth settling in the same pass.
- The class fix, not the instance: `_row(...)` renderers in
  `generate_shadow_html.py` that pull a numeric from a JSON payload should not
  silently default. A `_required(payload, key)` helper that raises (or renders an
  explicit `—`) on a missing key would fail loudly at generation time, which is when
  a renamed producer field is cheap to catch. There are other `.get(k, 0)` numeric
  reads on that page; this finding does not enumerate them, and that census is part
  of the work.
- R15: the control must be able to fail — assert the rendered row for a known year
  carries the value the payload actually holds, and mutate the producer's key name to
  prove the assertion fires.

## Related

- `WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md` — the
  sibling closed on 2026-08-12; same family (a confident number over data never read),
  different mechanism (absent file vs absent key).
- `saas/reporting/arrears_ledger.py` — where the availability question now lives.

---

## RESOLVED 2026-08-12 (worker tick, drawn as the lane's BLOCKING finding)

`observed-with-evidence` throughout.

**The instance.** `_population_anchoring_rag` reads `new_arrears_rate_pct` — the key the
producer emits. Rendered from the live `site/state/population_anchoring.json`, the three
rows the finding quotes now read **30.80% / 46.20% / 0.00%**, which are the figures the
finding named as correct. The previous 0.00% for every year is gone.

**The second instance, found by the census this finding asked for.** The bad-debt rows
read `bad_debt_pct`; `population_anchor._bad_debt_check` emits `bad_debt_rate` (already
in percentage points — `round(rate * 100, 2)`). Every published bad-debt year was also a
default, not a reading, and was accidentally right only because the recent years really
are near zero. Fixed in the same pass.

**The census.** All 43 distinct `.get(<key>, 0)` numeric read keys in
`generate_shadow_html.py` were checked against every key actually present in the six live
artefacts the page renders from. Exactly two named keys no producer emits — the two
above. The six remaining unmatched names (`application`, `credit_check`, `onboarding`,
`low`, `moderate`, `high`) are reads from dicts the function itself aggregates a few lines
earlier, where a zero is a real count, not an absence. No third instance.

**The class fix.** `_payload_num()` never substitutes a number it did not read: absent,
null, non-numeric, or `bool` returns `None` and the cell renders an em dash. It renders an
absence instead of raising, so a renamed producer field cannot wedge a run mid-publish;
the loudness lives at test time instead, in `POPULATION_ANCHORING_NUMERICS` — the declared
list of every numeric key this page reads from that payload, asserted against the LIVE
artefact.

**The third mismatch, settled.** The chip is computed from the 10-year aggregate I&C rate
whenever I&C customers are present, not from the row's per-year rate. The producer now
states its own basis (`rag_basis_label` / `rag_basis_pct`) rather than leaving each
consumer to re-derive it, and the cell prints that basis whenever it differs from the
value beside it — so the row reconciles against its own chip without opening the JSON.
An unavailable ledger now renders no rate at all, rather than the 0.0 its division guard
produces beside an UNAVAILABLE chip.

**R15.** `tests/tools/test_shadow_arrears_row_reads_an_emitted_key.py`, **12** tests, each
control paired with the mutation that makes it fire: rename the producer's rate key, read
under the never-emitted key, drop the availability flag. All three mutations were run and
observed red before the fix and green after.

<!-- Corrected at landing 2026-08-12: this paragraph said 13 tests; the file declares and
     runs 12. The finding's own class is "one name, two numbers", so an uncorrected count
     here would have been the defect restated in its own resolution. -->

**One mutation was strengthened at landing.** `test_the_producer_contract_fires_on_a_key_
the_producer_does_not_emit` re-implemented the control's assertion inline and asserted
that its own `assert` raised — R15's TAUTOLOGY pattern: it never read
`POPULATION_ANCHORING_NUMERICS`, so it would have passed with the real control deleted.
Both the control and its mutation now run one shared body over an injected declaration
list, so the mutation exercises the shipped logic; the mutation also re-runs the
unmutated tuple through the same body, making the red attributable to the injected key
rather than to the fixture.

**The gate caught this commit's own local-green, and it was a real one.** The live-artefact
control passed in the working tree and RED in the gate's checkout: the tree carried a
regenerated `site/state/population_anchoring.json` carrying the producer's two new fields,
uncommitted, while HEAD's copy predated them. The local pass rested on a file the commit
did not include — the untracked/uncommitted-artefact local-green shape. The artefact is
landed with the commit; it was diffed semantically against HEAD first and is a PURE
ADDITION (20 added keys, all `rag_basis_label`/`rag_basis_pct`, **zero** changed values),
so it moves no published figure and the verification-pause reasoning below is untouched.
Had it changed a single rate, the correct move would have been to leave it and weaken
nothing — the control was right to refuse.

**What is NOT done, and why.** `site/shadow/sim/index.html` still carries the old 0.00%
rows. Re-rendering it now would stamp a page with the CURRENT run while verification is
paused (`docs/observability/.publish_gate_state.json`, blocking test in
`tests/company/test_phase_ob_settlement_reconciliation.py`, a different lane), which is
the fake-fresh cardinal sin under DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10 property
3. The corrected rows reach the published bytes at the next verified publish, which is
that ruling's designed mechanism. The generator is fixed and proven; the published bytes
are behind, not wrong-forever, and the banner already says so.
