# [WORKER-FINDING] A public panel served "Loading..." for 8 days, and three controls all passed over it

**Found:** 2026-08-11, cold-eyes Expert Hour on the live site (`cold-eyes-walk`, two blind
persona forks + a sighted mechanical pass).
**Disposition:** the BLOCKER was FIXED THIS TICK (it is a live user-visible defect with a
class fix and a precedent already in-repo). Everything else below is **QUEUED** per
SELF_INTERRUPT_DISCIPLINE — the supply is infinite; these are atoms, not interrupts.

---

## FIXED THIS TICK — the orphan renderer (observed-with-evidence)

`site/company/index.html:327` defined `renderBookMix` and **never called it**. Verified on
the LIVE SERVED BYTES, not the repo copy:

```
curl -s https://poesys.net/company/  -> 63,164 bytes
grep -n renderBookMix   -> 327:function renderBookMix(d){      (one occurrence, the definition)
grep -n 'id="mix-intro"'-> 134:<p ... id="mix-intro">Loading...</p>
git log -S"renderBookMix(d);" -- site/company/index.html  -> (empty: the call never existed)
```

Dead since `93fbc41a7` (2026-08-03) — **8 days**. The block's own source comment states its
purpose: a reader who meets "Net margin / customer" before learning ~99% of the revenue is
earned by five I&C accounts *"has been misled by ORDERING, even though every figure carried
its clock."* That is exactly what every live reader got, and the FRONT door delegates to this
panel by name ("the exact mix, account counts and per-segment unit economics are on The
Company"). R3 territory: this block was itself the remediation for a previous cold-eyes Hour.

### Why nothing caught it — three independent fail-opens, which is why the fix is a CLASS

1. **The harness supplied the missing call itself.** `site/company/_render_harness.mjs:53`
   hand-typed `sandbox.renderBookMix(d)`, so the three door tests in `test_company_door.py`
   asserted *rendered pixels* for a panel the page never renders. The control was a PRODUCER
   of the evidence it graded — the R15 tautology, in the one dimension it was built for.
2. **`site/live_pixel_verify.py` grades only elements the page's script WROTE.** An element
   left at its shipped `Loading...` placeholder is outside the checked population: fail-open
   for PARTIAL render, which is a commoner shape than the total-render failure it was built
   for. Its static-markup scan runs only under `if res.static:`.
3. **The precedent existed and was never generalised.**
   `tests/tools/test_site1_proof_citations_resolve.py::test_the_generator_actually_calls_the_resolver`
   ("a mechanism nobody invokes is the fix that isn't", mutation M8) landed **2026-08-03 — the
   same day this shipped dead**.

### The fix, and its R15 evidence

- **Page wired**, deliberately FIRST in the boot path, because ordering is the block's purpose.
- **Harness de-tautologised**: it now derives its call set from the page's own boot path and
  exits non-zero on an orphan. Arguments stay declared (only the harness knows which payload
  each function eats); the CALL SET is derived. Mismatch fatal in both directions.
- **Class control** `site/test_door_render_functions_are_wired.py` (R10 — the class, not the
  instance): every `function render*` in every door must be invoked by that door's own script,
  counting both wiring shapes (direct call, and `.then(fn)` by-reference).

**Blast radius measured BEFORE choosing the predicate:** 110 render functions across 12 doors,
**exactly 1 orphan**. So this is a standing guard, not a ratchet over known dirt.

**R15 both ways, byte-clean restore verified (md5 before == after on both mutants):**

| mutation | result |
|---|---|
| re-orphan the real call in `index.html` | live gate FAILS, naming `{'company/index.html': ['renderBookMix']}` |
| same, against the harness | harness exits **3**, `page defines but never invokes: renderBookMix` |
| break the door glob | **vacuity guard fires** — and the main gate went GREEN under it, which is precisely the fail-open the guard exists to cover |
| commented-out call `// renderThing(d);` | counted as an ORPHAN (mutation M8's shape, pre-empted) |
| direct call / `.then(fn)` by-reference | both counted as wiring — the predicate is not always-positive |

7/7 new tests green; 31/31 `test_company_door.py` green against the de-tautologised harness.

---

## QUEUED — not fixed on sight

### A. R12 DIAGNOSTICS, and they must be read as diagnostics
The blind CFO fork committed Ofgem-anchored priors *before* reading, then found the book
outside them by 4–9×: book net margin **28.4%** billed / 10.9% of revenue, gross **45.8%**,
against a retail-supply prior of −5% to +3%. Bad debt renders **−0.00% of revenue** while 12
of 18 accounts are in arrears and the deepest owes £187,424.72 — and that figure is what turns
SLC 27 / 27A **GREEN**. The world fork independently reached the same place from the cost side:
a £55/MWh non-commodity stack and £0.27/day standing charge against a real 2024 cap of
53.4–60.1p/day, implying an all-in ~15.7p/kWh into a 24–27p market.

**R12/R13 WALL — the reason this is a finding and not a work order:** margin is a DIAGNOSTIC,
never a target. These are cues to **R4-diagnose the mechanism** (the cost stack, the missing
provisions policy), NEVER to tune an output toward a benchmark, and the BASELINE may only
change for fidelity-to-reality reasons decided blind to company P&L. Both forks independently
named the same first fix — *put provisions and write-offs through the ledger so bad debt can
be non-zero* — which is a fidelity change, not a margin change, and is the right shape.

### B. Controls that cannot fail
- The obligations register is **9 domain verdicts wearing 23 names**
  (`saas/reporting/annual_report.py::populate_compliance_scorecard` records one RAG + one note
  per *domain*). Live: `GDPR/PECR "Data Breach Notification (72h ICO)" -> GREEN, "Net assets
  positive"`; `UK EMIR "Trade Repository Reporting (T+1)" -> GREEN, "Net assets positive"`.
  All four AMBERs are exactly the four `billing_metering` rows. A GDPR breach-notification
  obligation is GREEN iff `total_equity >= 0`.
- The freshness-banner door set is **hand-typed** in
  `tests/background/test_publish_provenance.py`, so it cannot fail on the omission of
  `/customers/` — a public door rendering per-household money with no staleness banner while
  verification was paused 33.7h. `/director/` (7 feeds) also uncovered.
- Overall compliance renders **AMBER and GREEN on the same page**.

### C. Denominators and one-name-two-numbers
Per-customer figures divide by **fuel legs (18)**, not households (13), while the customers
door itself knows the distinction. `/customers/` renders C1's **electricity leg only**
(£495.99) while labelling it "dual fuel" and "lifetime" — the feed's `combined` block
(net £1,244.51) is present and unused, understating the flagship household by 2.5×; and its
`annual_pnl` covers **2016–2021 only**, so the "lifetime" excludes the 2021-22 crisis outright.
"£6.42M" renders twice meaning two different quantities (settled gross vs billed net), 0.079%
apart — so the collision is invisible. Payment-channel and tenure cuts sum to 11 of 18 with no
"other" row.

### D. The world door's coupling claim
The page's own falsifiable hypothesis ("perturb the weather and the effect propagates to the
bill") is not evidenced by anything on it: node 1's weather is **2025-12** while node 2's price
is a Jan–7 Jun 2025 mean, so the cause post-dates the effect — and the rendered December is
*milder* than average, so even the sign is wrong. The demand model's own table shows the CWV
wind-chill term making error **worse** in the cold-and-windy cell (2,420 → 2,456) directly under
a caption claiming it "earns its keep" there. And a **2.4% max** account-level annual volume
forecast error is graded GREEN — by this project's own doctrine the tightest gap deserves the
most suspicion, not a green badge. **This one is squarely H_GAP/W1_12 territory.**

---

## Protocol note, per the skill's own wall

This was **blind, not independent** — the reviewers are the same model family as the builder,
so shared priors survived the blindfold. Nothing here should be recorded as an independent
verdict. The arithmetic quoted above was re-derived from the live feeds; the *judgements* were
not.

I did **not** write to `docs/observability/sanity_adjudication_ledger.json` — it is a live
control input on a shared tree with concurrent writers, and filing into it is a separate,
deliberate act, not a reviewer's side effect.

## Related
- `feedback_a_grader_quoting_its_own_detection_marker_joins_its_own_producer_set` — same family:
  a control that produces the evidence it grades.
- `feedback_reported_state_is_not_a_control`, `feedback_population_control_needs_a_vacuity_guard`.
