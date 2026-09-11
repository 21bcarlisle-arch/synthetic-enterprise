**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** C32_one_obligation_one_vulnerability_scorer
· **Class:** no_caller_and_never_runs

# The obligation has five implementations, not two — and the one whose vocabulary matches the regulator is the one with no caller

**Result document, 2026-09-05, delivery seat.** It corrects the census in
`SEAT_FINDING_ONE_OFGEM_OBLIGATION_HAS_TWO_VULNERABILITY_SCORERS_THAT_DISAGREE_AND_THE_DEAD_ONE_DECIDES_DISCONNECTION_2026-09-05.md`,
which is right about the shape and wrong about the extent and about who calls what. Kept beside the
claim rather than revising it, per CLAUDE.md.

---

## What the earlier finding said, and what is actually there

It named **two** implementations and gave this caller attribution:

> `vulnerability_register.py` — **LIVE** — `self_rationing_detector`, `life_event_detector`,
> `portal/app.py`, `warm_home_discount`

Two of those four callers are not callers of that module. `portal/app.py` and
`warm_home_discount.py` call `ServiceLog.vulnerability_register()` — a **method on a different
class in a different module**, returning a **third** vocabulary. The finding matched on the name
`vulnerability_register` and read a method call as a module import. That is the
`a grep for a concept's name is blind to the mechanism` shape, inverted: the grep hit the name and
attributed the mechanism to the wrong owner.

## The census, measured

Import graph over the tree, production importers = non-test files importing the module; the
`service_log` row counts callers of the method rather than of the module, because that vocabulary
has no module of its own.

| # | module | vocabulary | terms | numeric scale | **production callers** |
|---|---|---|---|---|---|
| 1 | `company/crm/vulnerability_register.py` | `VulnerabilityFlag` (enum) | 12 | severity weights 1–5 | **2** — `self_rationing_detector`, `life_event_detector` |
| 2 | `company/crm/vulnerability_index.py` | `FuelPovertyIndicator` (enum) | 6 | scores 10–60, bands at 15/35/60 | **0** |
| 3 | `company/crm/service_log.py` | `VulnerabilityFlag` (dataclass) | **unbounded** — `flag_type: str`, free text, persisted in SQLite | none | **2** — `warm_home_discount`, `portal/app.py` |
| 4 | `company/regulatory/priority_services_register.py` | `PSRCategory` (enum) | 9 | none — categorical | **0** |
| 5 | `company/regulatory/consumer_vulnerability_register.py` | `VulnerabilityCategory` (enum) | 8 | none | **0** |

### Row 5 was found by the control, after this census had already been written

The table above said four until the guard
(`tests/company/crm/test_one_obligation_one_vulnerability_vocabulary.py`) was run for the first
time and immediately went red naming a module no by-hand pass had reached. Both censuses — the
earlier finding's two, and this document's four — were built by grepping the *names* of modules
already known, which is blind to a fifth rendering that spells the concept differently and lives in
a different directory. **The AST detector found in one second what two manual passes missed.** That
is the argument for the control existing, made by the control, and it is left here rather than
tidied away because the correction is the evidence.

Row 5 also carries two constants the published record does not merely fail to support but
**refutes**:

- its docstring's *"Elderly/frail (self-reported, 75+)"* — the published criterion is pensionable
  age, the same invented 75 that `vulnerability_index.ELDERLY_75` held, arrived at independently in
  a second place;
- its docstring's *"Do not disconnect vulnerable customers **Nov-Mar**"* — the published winter
  months are **October** to March (commons §2). It is one month short, in the direction that
  removes protection from customers who have it.

Neither has a production caller, so neither is currently doing harm. Both would have become
load-bearing the moment one was wired, and the second is the sharper warning: a *narrower* winter
than the law, written in prose in a docstring, where nothing compares it to the licence condition.

## The result

**#4 is the one that matches the published record, and nothing calls it.**

Against the needs codes established in
`docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`,
`PSRCategory` is very nearly the published list — pensionable age, disability, medical equipment,
child under 5, chronic illness, mental health, visual impairment, hearing impairment, language
support. Its `PSRService` enum is the published core-services list. It is categorical, with no
invented numeric scale, which is what the published record supports and all the published record
supports. The two `crm/` scorers invented parallel vocabularies and numeric scales beside it, and
`ELDERLY_75`'s age threshold is not merely unsourced but **refuted** — the published criterion is
pensionable age, which is not 75.

So the earlier finding's question "which of the two disagreeing scorers wins?" had a false premise.
Neither wins. The answer was already in the tree, in a third directory, unwired. **Three of the five
have no production caller at all; the two that do are the operational flag enum and the free-text
string.** Nothing that runs is grounded in the published needs codes.

**And the vocabulary that decides real money is the free-text one.** `whd_eligible_customers`
returns every customer holding any active flag of any `flag_type` whatsoever, and the live portal
renders that as Warm Home Discount eligibility at ~£150 a customer. Nothing constrains `flag_type`
to any of the three enums. That is a worse defect than the one the atom was opened for, it was
invisible to a census that stopped at two modules, and it is **not** fixed here — WHD eligibility
is a separate published obligation (benefit receipt and property cost, not PSR need) and is
recorded as the named next research question in §4 of the commons artefact.

## What was done this turn

1. The published obligation established and filed in the regulation commons — PSR needs codes,
   SLC 27 disconnection protection and its seasonal term, the Energy UK voluntary commitment, and
   the finding that **no published source assigns a weight or ranking to any of these categories**,
   which is what makes every numeric scale in `company/` ours rather than the regulator's.
2. `company/crm/vulnerability_index.py` **deleted**, with its dedicated suite and its section of
   `tests/company/test_phase_ir_coverage_expansion.py`. Five implementations → four. It had no
   production caller, its `disconnection_protected` rule (`band == CRITICAL`, i.e. a score of 60)
   bears no relation to the published rule and carries no seasonal term at all, and it held the
   refuted `ELDERLY_75` threshold. Deleted rather than deprecated, per the earlier finding's own
   disposition.
3. A control over the convergence itself — `tests/company/crm/test_one_obligation_one_vulnerability_vocabulary.py`.

## What is left, and why the atom is not closed

C32 asks for **one** scorer. There are four. The remaining convergence is #1 and #3 onto #4, and
it is not a mapping exercise:

- #3's `flag_type` is free text persisted in a SQLite column, so converging it is a data migration
  with a back-compat read path, not an enum swap.
- #1 carries seven terms with no PSR analogue (`BEREAVEMENT`, `JOB_LOSS`, `PAYMENT_DIFFICULTY`,
  `FUEL_POVERTY`, `PPM_SELF_DISCONNECTED`, plus `MENTAL_HEALTH` and `LANGUAGE_BARRIER` which do map).
  Those are real operational states that are **not** PSR needs codes, and collapsing them into
  `PSRCategory` would assert a regulatory meaning they do not have. The likely right shape is that
  #1 keeps its operational vocabulary and stops claiming to decide `psr_required` /
  `no_disconnect_required` at all, delegating both to #4 — but that is a design decision with a
  live blast radius across `self_rationing_detector` and `life_event_detector`, and it is more than
  the remainder of this turn.
- #4's own `UK_PSR_RATE_PCT = 31.0` is unsourced and must carry an origin or an honest `None`
  before it becomes the survivor.

Level unchanged. The atom keeps carrying work.
