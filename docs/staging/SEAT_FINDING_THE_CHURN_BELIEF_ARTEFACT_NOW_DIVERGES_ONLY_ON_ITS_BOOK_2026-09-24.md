**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — the residue of `SEAT_FINDING_THE_PUBLISHED_CHURN_KNEE_IS_GBP_3000_AND_THE_CODES_KNEE_IS_GBP_0_1_2026-09-23.md`

# The churn-belief artefact's knee now reproduces exactly and its BOOK does not, so what keeps it out of the covered set has changed identity

Filed on discharging the churn-knee finding (`6fd5aa1dc`, merged `19bf3e20b`). That finding's own
subject is repaired. This is what is left, and it is **not the same defect wearing the same
verdict** — which is the reason it gets its own document rather than keeping the old one open.

## The measurement

`check()` over `WATCHED_DERIVED_ARTEFACTS`, run in a clone at HEAD on 2026-09-24:

```
verdict: DIVERGES        n_changed: 46
TOP-LEVEL: Counter({'book': 46})
non-/book keys: (none)
```

**All 46 diverging keys are under `/book`. Zero under `/knee`, `/reading`, or the flat/deaf
booleans.** On 2026-09-23 the divergence was 35 keys and *"the weight of them"* was
`/knee/by_rate[*]/knee_kwh`. The knee is now byte-identical on regeneration.

What moved instead is the population:

| key | committed bytes | regenerates now |
|---|---|---|
| `/book/billing_accounts` | 164 | **154** |
| `/book/by_segment/resi/legs` | 242 | **224** |
| `/book/leg_annual_kwh/min` | 58.0 | **35.0** |
| `/book/leg_annual_bill_gbp/p50` | 745.2 | **767.2** |

## Why this is a different subject with a different owner

The old divergence was **the artefact against its own code** — a stale intermediate describing a
belief the tree no longer held. The remedy was to re-run the producer, and it worked.

This divergence is **the artefact against the book the company now has**. Re-running the producer
does not settle it, because the next run will disagree with *that* run as soon as the book moves
again. The question it raises is one nobody has asked here: *is this artefact supposed to be a
statement about a book at an instant, or about the belief?* If the former it can never sit in
`COVERED_DERIVED_ARTEFACTS` and the watch is mis-specified; if the latter the `/book` block is
subject matter that does not belong in a reproducibility comparison and should be excluded from it
by name, the way `NOT_A_FUNCTION_OF_ITS_COMMIT` already excludes `knowledge_review.json`.

**That is a judgement about what the artefact IS, and by this repo's own rule the definition comes
before the difference** — so it is filed, not guessed at.

## What is NOT wrong, recorded so the next pass does not re-derive it

* `COVERED_DERIVED_ARTEFACTS = {}` is **correct today** and the control proves it: the verdict is
  `DIVERGES`, so `test_a_watched_derived_artefact_that_reproduces_must_be_promoted` is correctly
  quiet. Promotion is not owed and forcing it would red every lane.
* The control is **not** fail-silent. It was worth checking — a promotion gate that can never fire
  is this project's commonest R15 shape — and it fires: it reaches a real verdict on a real diff.

## The trap this nearly walked into, which is the transferable part

`_verdict` truncates `changed` to `[:10]` while reporting `n_changed: 46`. **The sample is not the
population.** The first ten keys are all `/book`, and so are all forty-six — but that agreement is
luck, not inference, and reading the sample as the population is how a pass concludes "the knee is
fine" without having looked at the knee. The full set has to be captured by wrapping `_verdict`:

```python
import tools.published_feed_regeneration_check as M
orig = M._verdict
def spy(committed, first, second):
    from tools.artefact_rerun_diff import compare
    captured['full'] = compare(json.loads(committed), json.loads(first))
    return orig(committed, first, second)
M._verdict = spy
```

Separately, `--working-tree <generator>` returns `WROTE_NOTHING` for this producer. That is a
different standpoint from the one the control uses, and **it is not evidence about reproduction**.
Read as a verdict it says the opposite of what the control says.
