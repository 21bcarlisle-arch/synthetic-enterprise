**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the switching-rate commons registers one claim per cause string with search"

# Two refusal-claim readers registered the first claim in a cause and never asked about a second, and repairing the read exposed a pairing hole the grammar cannot close

**Delivery seat, 2026-09-19, claim
`the-switching-rate-commons-registers-one-claim-per-cause-string-with-search`.**

---

## 1. The premise, re-measured before any work

The drawn item cited `087e3ad58`, an ancestor of `origin/main`. That commit repaired the SIBLING
instance (the here-relative census) and NAMED these two as the remaining known ones — it does not
spend this premise. Re-measured at HEAD `087e3ad58` before any edit:

```
tests/architecture/test_switching_rate_commons.py:886:  found = _LIVE_FLOOR_CLAIM.search(cause)
tests/architecture/test_switching_rate_commons.py:964:  found = _CITED_ROWS_CLAIM.search(cause)
```

**Live.** The duplicate-work note named this same id as already held; it is this item, held by this
seat, not a rival claim — so the work was done rather than disposed.

## 2. What was wrong, and why nothing could see it

`simulation.departure_level_anchor.UNFITTED_YEARS` maps a year to a prose CAUSE for refusing to fit
it. Two legs in this file open that prose and judge what it claims: one re-drives every stated SVT
floor under the live hazard, one opens every cited capture and checks what its rows actually are.
Both read their pattern with `search(cause)`. A cause stating two floors, or citing two captures,
registered **one**.

The second claim was not judged wrongly. **It was never asked about** — which is why no assertion
downstream could notice, and why both legs could stay green over half the subject they name.

A second half made the floor reader worse than the class: it stored results in `dict[int, ...]`
keyed by year. Widening the read alone would have found both claims in one cause and then
**overwritten one**, so the `finditer` and the flat list had to land together.

Measured at `087e3ad58`, each pattern finds exactly ONE match per real cause (2022's, no other year
states either grammar). **LATENT, not live** — and latent only until a cause gains a sentence or
either vocabulary widens, which is precisely what happened to the sibling instance the same
morning.

## 3. The repair, and the mutation that proves it

`_floor_claims` / `_cited_rows_claims` read with `finditer` and return flat lists. The legs call
them. A new leg, `test_a_cause_stating_two_claims_registers_both_and_not_only_the_first`, holds
both readers on **synthetic** causes.

Synthetic is not laziness, it is the only shape that works. With one claim per real cause, `search`
and `finditer` return the same one-element answer, so a control keyed to `UNFITTED_YEARS` as it
stands **cannot tell the repair from the revert** — every rung stays green. A dropped match is an
absent question; the only way to hold an absent question is to supply a subject that has a second
one. Proven with `python3 -B`, both fire, and no other leg in the file sees either:

```
finditer -> search in _floor_claims        -> 1 failed, 101 passed   (the new leg, on the count)
finditer -> search in _cited_rows_claims   -> fires on the cited leg
unmutated                                  -> 102 passed, 2 xfailed
```

## 4. What the wider read exposed and I did NOT fix — the part worth keeping

`_CITED_ROWS_CLAIM` pairs a filename with a claim across a gap `.{0,900}?`. With one claim per
cause the gap was harmless. Read wide, a cause naming both files BEFORE stating both claims is
mis-read. The obvious tightening — forbid a second `.json` inside the gap, so a claim binds to the
NEAREST preceding filename — was written, and then measured:

```
subject: "`alpha_factors.json` and `beta_factors.json` are both cited.
          ALL 53 OF THOSE ROWS CARRY `passive_churn_cap = 0.1` in the first;
          ALL 7 OF THOSE ROWS CARRY `passive_churn_cap = 0.25` in the second."

plain `.{0,900}?`    -> [('alpha_factors.json', '53', '0.1')]
tempered (?!\.json)  -> [('beta_factors.json',  '53', '0.1')]
```

**Two wrong answers, not one right one.** Both drop the second claim entirely; the tempering only
changes which file the surviving claim is attributed to. Its claimed mutation did not fire, and the
reason was neither flattering reading: a MISSING TEST whose missing subject, once supplied, showed
the change was not an improvement. So the tempering was **reverted rather than landed**, and the
docstring that asserted its mutation was corrected beside the claim rather than quietly dropped.

**The remaining hole:** a cause citing two captures before stating two claims registers one claim,
bound to one of the two files by an artefact of the gap. It is named in the pattern's own comment,
in `_cited_rows_claims`, and in the new leg's "what this does not hold" paragraph, so no reader can
mistake the green for wider than it is. It is not closed here because no candidate grammar
measured today registers the lost claim, and inventing one to look complete is the shape this
project repairs.

## 5. The class

Same class as `087e3ad58`: **a detector whose match is the registered subject of a downstream
judgement, read with `search`.** With those two repaired and
`site/test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py` already
`finditer` throughout, the known instances of the class are discharged. The secondary lesson is
new and belongs to `controls_that_cannot_fail`: **widening a one-shot read can expose a PAIRING
ambiguity the one-shot read concealed, and the first repair that suggests itself may swap one wrong
answer for another** — measure the candidate on the shape it exists for before landing it.
