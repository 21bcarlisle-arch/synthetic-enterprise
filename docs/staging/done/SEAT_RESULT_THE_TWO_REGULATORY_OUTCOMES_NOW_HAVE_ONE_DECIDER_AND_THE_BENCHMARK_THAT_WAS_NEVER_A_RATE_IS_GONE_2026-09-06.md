**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** C32_one_obligation_one_vulnerability_scorer
· **Class:** no_caller_and_never_runs

# The two regulatory outcomes now have one decider — and the "UK benchmark" was never a registered rate

**Result document, 2026-09-06, delivery seat.** Second turn on atom C32. It continues
`SEAT_RESULT_THE_OBLIGATION_HAS_FIVE_IMPLEMENTATIONS_AND_THE_ONE_MATCHING_THE_REGULATOR_HAS_NO_CALLER_2026-09-05.md`,
which established the census, filed the commons artefact, deleted `vulnerability_index.py`, and
listed three things left. Two of the three are done here. The third is not, and is stated below
rather than folded away.

---

## What the previous turn left, and what happened to each

| left | status |
|---|---|
| `#1` should stop claiming to decide `psr_required` / `no_disconnect_required`, delegating both to `#4` | **DONE.** Both properties deleted. |
| `#4`'s `UK_PSR_RATE_PCT = 31.0` must carry an origin or an honest `None` before it becomes the survivor | **DONE, and the number was wrong** — see below. |
| `#3`'s free-text `flag_type` is a SQLite migration with a back-compat read path | **NOT DONE.** Unchanged and still the largest remaining piece. |

## 1. One decider, and it is the one whose vocabulary is the regulator's

`company/regulatory/priority_services_register.py` gains `disconnection_protection(categories,
as_of, household)` and `needs_code_for(term)`. `company/crm/vulnerability_register.py` deletes
`psr_required` and `no_disconnect_required` and calls them.

**The old `no_disconnect_required` was `'no_disconnect' in required_actions`, and only
`MEDICAL_EQUIPMENT` carried that string.** So a table with no date in it decided a rule that turns
on the month. The published rule (commons §2) is categorical, **seasonal**, and turns on household
composition; the decider now holds all three, and returns a fourth answer the old boolean could not
express:

- `PROHIBITED` — SLC 27.10: pensionable age, a winter month, and the composition limb.
- `REASONABLE_STEPS` — the weaker duty, on disability / chronic illness / pensionable age.
- `CANNOT_DETERMINE` — **the point of the exercise.** Pensionable age in winter with the household
  unknown is not "not protected"; it is not knowable from what we hold. `may_disconnect` is `False`
  on it, because failing open here disconnects someone the licence protects.
- `NOT_ESTABLISHED` — nothing held confers protection in the published record.

**October, not November.** `consumer_vulnerability_register`'s docstring said Nov–Mar — one month
short, in the direction that removes protection from customers who have it. Its refuted `75+` went
with it. Neither had a production caller, so neither was doing harm; both would have become
load-bearing the moment one was wired.

**Medical-equipment dependency now returns `CANNOT_DETERMINE`, which reads as weaker and is not.**
It is a PSR needs code but is not one of the three terms in the reasonable-steps limb, and the old
absolute year-round protection was *stronger* than SLC 27.10 and *weaker* than the Energy UK
commitment, matching neither (commons §3.3). Whether such a customer is also disabled or
chronically sick is a fact we may hold; it is not established by the category.

## 2. The mapping has three values, because two would have been the defect

The atom's own warning was that wiring these means "burying the choice in a mapping table". A term
maps to a needs code **only where it is the same concept**:

- `disabled → DISABILITY`, `medical_equipment → MEDICAL_EQUIPMENT`, `language_barrier →
  LANGUAGE_SUPPORT` — **EVIDENCED**.
- `elderly`, `child_dependent`, `serious_illness`, `mental_health` — **CANNOT_DETERMINE**, each
  naming the criterion it is missing. `elderly` carries no age at all and the published criterion is
  pensionable age; a dependent child is not a child under five (or six — S2 and S3 disagree and the
  disagreement is not resolved); a serious acute illness is not established to be chronic.
- the other five (`fuel_poverty`, `bereavement`, `job_loss`, `payment_difficulty`,
  `ppm_self_disconnected`) — **NOT_A_NEEDS_CODE**. Real operational states; they confer nothing.

`ELDERLY` used to confer PSR outright. It now goes to `psr_eligibility_review`, visible in
`required_actions` rather than swallowed, so **"we have not asked" never reads as "not eligible"**.
`annual_summary` reports `no_disconnect_required: None` with the reason, because a count there
would be the deleted boolean under a new name.

## 3. The benchmark was not a rate we ever measured

`UK_PSR_RATE_PCT = 31.0  # UK benchmark` cited nothing, had no caller, and its only control
asserted its own value back at it.

**Nothing published supports 31% of domestic customers being registered.** Fetched 2026-09-06 and
filed as commons S6: Ofgem, 25 October 2016 — *"Around 3.6 million electricity and 3 million gas
customers (13% of customers for both fuels) are signed up"*. The nearest thing to a 31 in the record
is Ofgem's separate finding that **~40% of households could access PSR support and have not signed
up** — the *eligible* share, not the *registered* one.

**Two different quantities, and the constant was named for neither.** That is this project's
recurring shape — *before dividing two numbers, say what each one counts* — in the form of a
benchmark whose subject was never stated. Replaced by `UK_PSR_REGISTERED_PCT_2016` carrying
`UK_PSR_REGISTERED_PCT_AS_OF`, and reached by `penetration_against_published`, which returns the
date and a staleness flag beside the figure so the nine-year gap cannot be dropped in transit. A
citation with no caller is refused here by construction, so the method is what makes the citation
legal as well as useful.

**A gap closed, a gap opened.** The *current* registered rate is still unsourced: the register has
grown since 2016 and Ofgem broadened eligibility again from January. The 2025 Consumer Vulnerability
Strategy PDF would answer it and defeated automated extraction, as the licence conditions did.
Nothing in `company/` may quote a present-day PSR rate until it does.

## 4. The controls, and the poison round before them

Five mutations of the decider, run before the results were read, each restored:

| mutation | verdict | killed by |
|---|---|---|
| winter narrowed to Nov–Mar | KILLED | `test_the_winter_is_october_to_march_not_november_to_march` |
| `CANNOT_DETERMINE` reads as a permission to disconnect | KILLED | `test_only_not_established_permits_disconnection` (+2) |
| `elderly` mapped to `PENSIONABLE_AGE` as EVIDENCED | KILLED | `test_a_term_maps_only_where_it_is_the_same_concept` (+3) |
| household composition ignored in winter | KILLED | `test_the_composition_limb_is_load_bearing_in_winter` (+1) |
| medical equipment restored to year-round protection | KILLED | `test_medical_equipment_alone_confers_neither_protection_nor_permission` (+1) |

Each patch asserted its target present before applying, so a survival could not have been a patch
that never applied. `test_every_outcome_is_reachable` asserts the **whole partition** in one
control: a decider that answered `CANNOT_DETERMINE` to everything would pass a leg per branch, and
would read exactly like caution — which is the shape a fail-closed rewrite drifts into.

The existing convergence guard's numeric-band leg now names `disconnection_protection` as well as
the deleted `disconnection_protected`, or it would guard a name nothing implements any more.

## 5. What is left, and the level

**Still four vocabularies.** What converged is the two DECISIONS, not the enums.
`service_log.flag_type` is free text in a SQLite column; `consumer_vulnerability_register` still
holds its own eight terms with no caller. `KNOWN_VOCABULARIES` is unchanged and the guard is green,
which is correct — nothing was removed.

**And the worse defect the previous turn named is still live and still not this atom's:**
`whd_eligible_customers` returns every customer holding any active flag of any type and the live
portal renders that as Warm Home Discount eligibility at ~£150 a customer. WHD is a separate
published obligation (benefit receipt and property cost, not PSR need). It remains the named next
research question in commons §4.

`level_current` recorded **0 → 2** — DISCOVER-lite and VERIFY passed, artefacts genuine. Not 3: the
full loop and the Expert Hour have not been run, and the atom's own target is unchanged at 3.
