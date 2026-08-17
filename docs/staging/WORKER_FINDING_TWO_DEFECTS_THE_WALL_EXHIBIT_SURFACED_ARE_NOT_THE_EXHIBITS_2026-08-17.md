# WORKER FINDING — two defects the wall exhibit surfaced are not the exhibit's to fix

**Severity:** LATENT · **Lane:** W2_customer_generator

Both defects are real and unrepaired, and neither invalidates a published figure or any
control's verdict: the per-customer records are internally consistent and the exhibit
renders them faithfully. LATENT, not BLOCKING, is a decision and not a default — declaring
these BLOCKING would freeze `W2_customer_generator`'s whole lane on two items nobody has
scoped, which is the perverse gradient a lane-scoped refusal is meant to avoid. Both
producers sit in the customer-generator lane: `tools/generate_customer_data.py` for #1, the
domestic consumption generator for #2.

**Raised:** 2026-08-17, SITE2_two_sided_wall_exhibit worker tick (scheduled draw)
**Rank requested (P-1):** backlog
**Why this doc exists:** both defects sat on `SITE2_two_sided_wall_exhibit`'s open
Expert-Hour findings list for five days, holding that atom's verdict at NO, while neither
could be fixed by any edit inside its `file_scope`. Re-homing them without writing them
down would lose them; leaving them on SITE2 held an atom on work it cannot do. R9 labels
below: every claim is `observed-with-evidence` unless marked `inferred`.

---

## 1. One household's two fuel legs disagree about whether it still has a churn risk

**Owner:** generator lane — `tools/generate_customer_data.py`. Not `site/customers/**`.
**Ledger:** `coldwalk:site2_churned_account_presented_in_the_present_tense` → `data_half_rehomed`.

`observed-with-evidence`, re-measured against the working tree on 2026-08-17:
`site/data/customers/C1.json` and `C1g.json` are the electricity and gas legs of one
household and both carry a `churned` timeline event dated **2021-12-30**. C1 publishes
`churn_probability: 0.23`; C1g publishes `churn_probability: null`. Same household, same
closure date, one leg asserting a forward churn belief and the other asserting none.

**The claim as recorded on 2026-08-14 is now mostly stale, and that correction matters
more than the residue.** It named four divergent fields; three of them
(`clv_gbp`, `expected_lifetime_periods`, `forecast_annual_profit_gbp`) now publish `null`
on C1, matching C1g — repaired by another lane's null-belief work, not by anyone acting on
this finding. Only `churn_probability` remains. *Do not inherit the four-field framing; it
is false today.*

**Not a render defect.** The page's render half was built 2026-08-15: a closed household's
forward-looking figures render as `<label> (at closure)` with the closure date, mutation-
proven both ways. The page now presents the figure in the right tense. It cannot make two
published records agree.

**Suggested falsifier (not yet run):** for every household publishing a `churned` event,
assert every leg agrees on whether a forward-looking belief exists. `inferred`: this is a
class, not an instance — C1 is one of five households the 08-15 tick found carrying a real
churned event, and only C1/C1g were measured here.

---

## 2. Domestic electricity consumption has no winter peak

**Owner:** sim/world lane — the consumption generator. Not `site/customers/**`.
**Ledger:** `coldwalk:site2_consumption_has_no_winter_peak_under_a_seasonality_panel` → `rehomed`.

**The finding's own evidence already said this** — *"this is a WORLD/SIM fidelity finding
surfaced by the exhibit, not a SITE2 render defect — it needs its own atom in the sim lane,
and R12 applies"* — and it was filed against SITE2 anyway, where it stayed for five days.
That is the re-homing failure this doc is really about; the physics below is unchanged from
the original adjudication and is reproduced so the next reader does not have to re-derive it.

`observed-with-evidence`, independently computed over all 72 C1 electricity invoices, mean
kWh by month: Jan 140.4, Feb 144.3, Mar 151.0, Apr 137.1, May 158.3, Jun 148.3, Jul 162.0,
Aug 163.4, Sep 150.9, Oct 145.0, Nov 134.6, Dec 143.7. Winter (Dec/Jan/Feb) 142.8 vs summer
(Jun/Jul/Aug) 157.9 — a winter:summer ratio of **0.90**, i.e. summer is 10.6% *higher*. GB
domestic electricity runs ~1.3–1.6:1 the other way. Total ~1,779 kWh/yr also sits below
Ofgem's LOW TDCV (1,800).

**R12 governs the repair.** The 1.3–1.6:1 figure is a plausibility band and a trigger for
R4 (diagnose the mechanism), **never a target to tune the output toward**. The defect to
find is in how the consumption generator applies seasonality, not in the ratio it produces.

**Second-order, `observed-with-evidence`:** the exhibit devotes a customer-observable panel
to explaining that use is "heavily seasonal … through winter you use far more than you pay",
so the page's narrative and its own data contradict each other on a public surface. That
contradiction is *visible today* and will remain until the generator is fixed — the page is
faithfully rendering what it is given, so there is nothing for SITE2 to repair, but anyone
reading /customers/ can see it.

---

## What this tick did and did not do

Did: verified both against the tree, corrected #1's scope, re-homed both in the ledger with
`why`/`owner`/`staged_as` pointers, and removed them from SITE2's open findings list with a
`findings_rehomed` record on the atom naming where each went.

Did not: mint an atom for either (minting is a code change and wants its own ruling-check),
or run either suggested falsifier.
