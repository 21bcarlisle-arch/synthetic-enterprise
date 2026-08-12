# WORKER FINDING — the shadow page's arrears rows read a key nobody emits, and print 0.00% for every year

**Severity:** HIGH · **Lane:** D_reporting

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
