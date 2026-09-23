**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# The daytime reference was one number for three incompatible scales, and the property record's two silent cuts were what would have found it

Found on 2026-09-23 while giving `build_properties` the two composition fields
`demand_model._daytime_occupancy_rate` is keyed on. The measurements, and the predictions they
were made against, are in
`docs/staging/records/PREREG_the_property_record_composition_fields.md` — filed there because a
pre-registration is a record and this is the part that is work.

## The defect I was sent for

`_daytime_occupancy_rate` takes three EFUS cuts — household size, pensioner presence, employment —
and averages *the ones it is given*. `build_properties` supplied the size cut only, so on the live
book of 144 homes `pensioner_present` and `someone_employed` were absent from **all 144**, while
`premise_trace.behaviour_profile_for` drew both for itself at an uncited 0.22 and
0.25-given-a-pensioner. One home, two answers — the shape `people_count_for_area` closed for the
headcount on 2026-09-17, committed again in the next two fields along. Unlike `children_count`,
whose R10 GAP comment refuses to fabricate a distribution nobody publishes, **these two had no
stated reason at all.** The silence read like a refusal and was not one: EFUS publishes the
marginal share in the same table as the rates the model already reads, as a headline that has to be
inverted.

**Repaired.** `dwelling_records.composition_cuts_for` is now the one function, the shares are
EFUS's own headline inverted (0.3103 and 0.6800 — arithmetic on the source, derived in code so a
corrected rate moves the share with it), and the book went from 5 distinct daytime rates to 18,
spread 1.793x.

## The defect underneath it, which is why this is BLOCKING

> `_daytime_occupancy_rate` averages the cuts it was GIVEN. A size-only rate and a three-cut rate
> are therefore **not the same quantity on the same scale** — their population means are 0.470 and
> 0.443. `_reference_daytime_rate` was a single constant. So `rate / reference` was only
> aggregate-neutral for households carrying *exactly the cut-set the reference was computed on*,
> and nothing anywhere said so.

While every caller in the world supplied the size cut alone, this was invisible and harmless. It
would have become a **4.1% silent cut to the whole book's daytime demand** the first time any
caller supplied more — measured at **0.95866** mean multiplier on the live 144-home book against a
0.02 tolerance, and dressed as a composition response rather than as a re-levelling. Mine was the
first caller. The next one would have been someone else's, and the change that triggered it would
have looked like the fidelity improvement it was.

**Repaired.** The reference is a function of the cut-set, each centred on its own population mean;
the size-only answer is unchanged to the float and the book lands at 0.99836.
`population_mean_daytime_multiplier` now accepts the two cuts, because a control scoring a
size-only population is asking about a world the book is no longer in — that is the
*control-whose-own-filters-empty-the-evidence* shape, and it was one argument away from being live.

**The class, not the instance.** A response built as "average the cuts you have" makes its own
output's SCALE a function of its input's completeness. Any single centre for it is wrong for every
cut-set but one. That is worth looking for elsewhere: a mean, ratio or index whose denominator is a
constant while its numerator is assembled from a variable number of terms.

## Why BLOCKING and not LATENT

Clause 1, *"a published figure may be wrong"*. The comparison arm is what the value arm's advantage
is measured against, and its daytime shape had two of three cuts silent, so the flattening sat
inside every advantage figure we publish. Grading my own finding LATENT to keep my own lane open is
the anti-pattern `background/finding_severity.py` names in its own docstring.

## What is owed, and this severity holds until it lands

1. **`premise_trace.behaviour_profile_for` still draws its own 0.22 / 0.25.** So one home still has
   two answers — no longer symmetrically, since the property record's is now EFUS-derived and
   testable and the fabric path's is uncited, but two answers all the same. Closing it means
   routing that draw through `composition_cuts_for`, which moves the fabric book's demand
   (pensioner share 0.22 → 0.310, and the employment draw stops being conditional on it). That is
   a baseline fidelity change decided blind to P&L, of exactly the kind `fabric_demand_path`
   records for the headcount — 130 of the book's premises settle on that path. **This is the next
   increment and the reason the severity stays up.**
2. **Then the control that cannot exist yet**: the `test_one_home_has_one_headcount` sibling for
   these two fields, keyed to AGREEMENT between the two paths rather than to either one's output.
   It is unwritable until (1) lands, because today the paths are *designed* to disagree.
3. **The JOINT of the two cuts is a named gap, not an anchor.** EFUS §4.1–4.2 is one-way; no
   located source cross-tabulates pensioner presence against employment. They are drawn
   independently and `demand_model` states that at the shares rather than leaving it to be
   inferred. If a cross-tabulated source is found, **independence is the thing to replace** — not
   the marginals, which are determined by the published table.

## Landed with this finding

`simulation/demand_model.py`, `simulation/dwelling_records.py`,
`tests/simulation/test_w2_13_occupancy_volume_shape.py` — four controls, each naming its defect.
The one for the new class is mutation-proven against the *production* wiring, not only against its
own monkeypatch: forcing the cut-set to `(False, False)` reds
`test_a_three_cut_population_is_also_mean_neutral` at 0.9661. Note the direction — the pre-existing
mutation on this control pushes the mean **above** 1.0 and the new one **below** it, so a control
that only ever caught inflation would have passed this one silently.
