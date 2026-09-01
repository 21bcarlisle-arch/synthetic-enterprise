**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# What re-running the C2 capture on the current world must show

**Filed 2026-08-31, delivery seat, Lane 0. Written BEFORE the capture was run.**

---

## The instruction, and the premise I am testing before obeying it

The lane draw says, verbatim: *"Re-run `tools/capture_departure_factors` … so the sibling
`c2_departure_factors_svt_segment_decisions.json` exists … WHY: **the data is not missing, it is
under another capture's name.**"*

That premise is checkable in ten minutes and it decides whether the instruction is a repair or a
regression, so it gets checked first. Two readings of where the SVT rows come from:

* **(A) The draw's reading.** `run_phase2b` records SVT segment decisions; every capture gets them;
  `c2_departure_factors.json` simply has no sibling because it was captured before the recorder, or
  because someone ran it with a different `--out` stem. Re-running fixes it.
* **(B) The alternative.** The SVT *departure route* is not in this tree at all. The 1,266-row
  siblings under `ladder_churn_factors*` were produced by a working tree carrying another lane's
  uncommitted roll plus an uncommitted `_svt_decisions` recorder. Re-running produces an **empty**
  sibling.

`tests/architecture/test_churn_carries_per_customer_signal.py:19-26` asserts (B) in prose. It is a
comment, and a comment is not a control, so it is a hypothesis here and not an answer.

## The predictions, and what refutes each

Run `python3 -m tools.capture_departure_factors <scratch>/probe.json` — **to a scratch path, never
to `docs/reports/`**, because if (B) holds then writing the sibling is the harm, not the repair.

| # | Prediction | Refuted by |
|---|---|---|
| P1 | `probe.json` is populated, order 400–500 renewal rows, order 70–90 `churned`. | An empty or wildly different renewal table — the capture wrapper is broken and nothing below is readable. |
| P2 | `probe_svt_segment_decisions.json` is written and is `[]`, and the tool prints its `⚠ NO SVT SEGMENT DECISIONS CAPTURED` line on stderr. | Any non-empty SVT sibling. That refutes (B), confirms (A), and the draw's instruction is then simply correct — carry it out. |
| P3 | `run_phase2b`'s return dict carries **no `svt_decisions` key at all** (not an empty one). The `[]` is manufactured by `result.get("svt_decisions", [])` in the capture tool. | The key being present. |
| P4 | `tests/simulation/test_svt_product.py::test_no_account_is_on_the_svt_product_yet` is GREEN at this HEAD — i.e. the world genuinely has nobody on the product, so there is nothing for a recorder to record. | The test being red or absent. |

## The consequence I am predicting, and it is the reason this is filed as a pre-registration

If P2 and P3 hold, then obeying the draw literally **replaces an honest declaration with a false
one**, and the seat's own instruction — *"do not touch the declaration except by making it true"* —
forbids it. Measured against `declare_rows` before the run, with a hand-fed empty SVT list:

```
covers_svt_route          False  ->  True
routes_readable           ['renewal']  ->  ['renewal', 'svt_segment']
share_of_departures_visible  None  ->  1.0
causes_not_observable     ['svt_inertia']  ->  []
warning                   SVT_BLIND_WARNING  ->  None
account_denominator_refusal  <refuses>  ->  None
```

**P5.** That transition is driven by the file's EXISTENCE, not by any evidence about the SVT route:
`declare_rows` computes `covers_svt = svt_rows is not None`, and `load_svt_decisions` returns `[]`
for an empty sibling. So an unwired recorder would certify the renewal route as seeing 100% of
departures and would silence the one warning that exists to say otherwise.

Refuted by: any code path between `load_svt_decisions` and the published artefact that downgrades
`covers_svt_route` on the empty case. I have read `tools/departure_population.py` end to end and
believe there is none, but the run is what settles it.

## What I will do with each outcome

* **(A) confirmed** — carry out the draw as written: capture to `docs/reports/`, re-fit, republish.
* **(B) confirmed** — do NOT write the sibling. File the finding, repair the fail-open at both ends
  (the producer must not default a missing key to `[]`; the reader must not count an empty-and-
  reasoned route as coverage), mutation-prove the repair, and land it. The C2 mix's declaration
  stays exactly as it is, because it is true and cannot be made truer until the world has an SVT
  departure route to see.

Either way the honest `None` on the page is not touched by a number picked to fill it.
