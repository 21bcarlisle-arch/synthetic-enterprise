**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_refusal`

# Pre-registration: is `predates_landing_carrying_some` evidence of anything for a `.json`?

**Claim:** `is-partial-a-signal-for-a-data-artefact-and-which-callers-ask-the-blind-oracle`
**Written BEFORE the measurement. Predictions below are not revised after the answer.**

## The question, stated so it can be wrong

`stale_copy_refusal.PARTIAL` fires when a working copy is OLDER than its own last landing (by the
file's own mtime, `taken_before`) and carries SOME but not all of that landing's distinctive lines.
`BASE_WINS_RULES = (PREDATES, CLOCK)` excludes it, with this reason written at the constant:

> `PARTIAL` says the copy carries SOME of the landing and therefore may be built on it

That sentence is an argument about **derivation**, and it is only true if a shared line is unlikely
to arise any other way. For a `.py` a distinctive line is a *statement*, and two lanes writing the
same non-trivial statement independently is rare. For a generated `.json` a line is a **key and its
value**, and two regenerations of one report share a line **whenever the figure did not move** —
which is not derivation, it is arithmetic.

So: **is the coincidence rate for a `.json` line materially higher than for a `.py` line?** If it
is, the sentence at `BASE_WINS_RULES` is false for data and `PARTIAL` is not a vouch there. If it is
not, the exclusion stands as written and the two `ladder_churn_factors` copies must stay refused.

## The instrument

The coincidence rate of a line class = the share of one document's non-trivial, within-document-
unique lines that also appear in a **second document that is provably in no derivation relation with
it**. Two sibling reports from one generator over different inputs are that second document: neither
was built from the other.

- **Data arm:** `docs/reports/ladder_churn_factors.json` at HEAD vs
  `docs/reports/ladder_churn_factors_continuous_satisfaction.json` at HEAD (different inputs, same
  generator), and the `_svt_segment_decisions` pair likewise.
- **Control arm (`.py`):** the same statistic over pairs of unrelated `tools/*.py` modules of
  comparable size. `_trivial()` is the filter in both arms — the same filter the rule itself uses,
  so the number measures the rule and not a ruler I chose.

Second measurement, on the live copies rather than a proxy: for each of the two refused
`ladder_churn_factors*.json` working copies on the shared tree, the **carried** distinctive lines
(the ones that make the verdict PARTIAL rather than PREDATES), classified by whether each also
appears in an unrelated sibling report.

## Predictions

1. The data-arm coincidence rate is **above 20%**; the `.py` control arm is **below 5%**.
2. The two live copies' carried share is **above 30%** of their landing's distinctive lines.
3. **The sharpest one:** of the distinctive lines each live copy CARRIES, **a majority also appear
   verbatim in a sibling report that cannot have been derived from that landing.** If this holds,
   the carry is demonstrably coincidence for these files specifically, not a population statistic
   borrowed from elsewhere.
4. `judge`'s production callers: all of `stale_copy_refusal.violations`, `census` and
   `refused_to_run` are already gated `if suffix in READABLE else clock_judge`, so **none** of them
   is blind. `refresh_to_head`'s two remaining `judge` call sites are unreachable for a `.json`
   **only because the `DATA_SUFFIXES` branch returns above them** — an ordering invariant, not a
   guard. I predict **no control pins that ordering**, so the blindness returns silently the day the
   branch moves or a suffix is added.

## What I do with each answer

- Predictions 1–3 all hold → widen the base-wins licence to admit `PARTIAL` **for
  `DATA_SUFFIXES` only**, with the coincidence measurement as its stated reason, and clear the two
  copies through the ordinary door.
- Any of 1–3 refuted → the exclusion stands, `BASE_WINS_RULES` is untouched, and the two copies stay
  refused with the measurement written beside them as the reason they must stay.
- Prediction 4 holds → write the control that pins the ordering. It is owed either way.
