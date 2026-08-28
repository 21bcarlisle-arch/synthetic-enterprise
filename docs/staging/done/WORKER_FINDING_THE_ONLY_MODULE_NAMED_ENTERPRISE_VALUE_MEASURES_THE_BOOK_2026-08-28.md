**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# The one module named `enterprise_value` measures the book — which is precisely the definition the mission supersedes

The director's mission sentence (2026-08-28) ends its first clause on a distinction the codebase
makes in the opposite direction:

> "the enterprise value is the automated method for finding those customers, not the book itself."

## Observed-with-evidence

`saas/enterprise_value.py`, module docstring, verbatim:

> "The portfolio-wide sum of the resulting per-account CLVs is the **enterprise value**: the total
> discounted future net margin of the customer book, accounting for both renewal risk and home-move
> win-back potential."

That is the book, discounted. It is the only place in the repository that claims the mission's own
noun, and it is reached in the live run — `company/analytics/customer_value_view.py` calls
`saas.enterprise_value.build_enterprise_value` as the roll-up of its four sub-phases, and
`simulation/run_phase4c_on_phase2b.py` calls that view through
`company/interfaces/customer_value.py`. So the superseded definition is not a stale comment; it is a
computed figure on the live path.

`company/analytics/customer_value_view.py` is explicit about which direction it points, and honest
about it: *"the supplier's OPINION about value and retention"* — the value **of** a customer **to
us**. Correct as CLV. It is not a measure of the method.

## What this finding does NOT ask for

**Not a rename.** The CLV roll-up is a real and useful quantity, it is correctly built, its epistemic
position is well documented, and it should keep its name inside its own domain. Renaming the module
would satisfy a word and change nothing measurable — the exact shape of defect this project files
against itself elsewhere.

**Not a demotion of the book.** The director's sentence does not say the book is worthless; it says
the book is the *evidence the method works*. A method that finds no customers worth having is
refuted by an empty book.

## What is actually missing

**Nothing in this repository measures the method.** There is no figure for:

- how reliably the machine **finds** an individual customer it can create value for;
- what it **costs** to find one (search, model, offer, persuade — including compute, which
  `PITCH_V7`'s £/tCO₂e formula already knew to include on the carbon side);
- whether either of those is **improving** run over run.

Every headline the project publishes today — £153,245 vs £157,913, level explains 102.4%, choosing
worth −£175 — is a statement about the book under two internal policies. Under the old mission that
was the headline. Under this one it is the evidence, and the thing it is evidence *for* is
unmeasured.

## Why it is LATENT rather than BLOCKING

No published figure is wrong. `enterprise_value` computes what it says it computes and labels its
clock. What is wrong is which figure is treated as the headline, and that is a mission-level judgement
the director has now made — so this is work created, not a defect in flight.

## WORK THIS CREATES

1. **`A48`** — define one measurable method figure and instrument it. My recommendation, to be
   argued down rather than assumed: **cost per customer-found-and-kept, against the value created for
   that customer** — which needs `A47`'s household side to exist first, and is why the two atoms are
   coupled.
2. **`A47`** — the score's missing household side. `A48` cannot be computed without it: "a customer
   we can create value for" is unidentifiable while nothing measures value created for a customer.
3. Note the ordering consequence for **P9** (`A46`): under the old mission a wider book was the
   growth story. Under this one, width is the **finding** half of the method and depth is the
   **creating-and-sharing** half, so the founder-book question stops being growth-versus-science and
   becomes a choice between measuring two different halves of the same asset. That does not settle
   it, and it is still the director's, but the ground it is argued on has changed and the P9 note
   should say so.

## DISPOSITION (2026-08-28) — all three items discharged, and one thing deliberately not claimed

**1. `A48` — define one measurable method figure and instrument it. DONE, L0→L2.**
`tools/run_value_cycle_ab.method_skill()`, wired into the artefact next to `belief_vs_outcome`
because the pair is the reading. It asks whether the arm's own per-customer signal
(`chosen_margin_gbp_per_mwh`) ranks the JOINT value created —
`(household_saving_gbp + our_net_margin_gbp) / counterfactual_gbp`, per **priced term** — better
than chance. Legs are independent (R15): the signal is the company's own logged decision, the
outcome is built from the world's settled records against the published default tariff. A price
and a consequence, not two readings of one number.

The recommendation in item 1 above was **argued down, as it invited**. "Cost per
customer-found-and-kept" needs a cost-to-acquire ledger that does not exist; the FRAME split
the mission's three method questions and instrumented only the first (*how reliably does it
find one*), naming cost-to-find and run-over-run improvement as explicitly out of scope at L2
rather than half-building them.

**2. `A47` — the household side.** Already landed at `039f202ce`, which is what made item 1
computable at all. `A48`'s build generalised its grouping: `build_household_value_share` now
takes `period_of`, defaulting to the calendar year so every pre-`A48` caller is unchanged. That
was the FRAME's §4 problem — a term straddles two calendar years, so a customer-year mixes two
priced decisions — resolved by its recommended option (a).

**3. The P9 ordering consequence. DONE**, as an addendum on
`SEAT_TO_DIRECTOR_P9_BOOK_DEPTH_PRICED_2026-08-28.md`: width is the *finding* half of the
method and depth the *creating-and-sharing* half, so Option 1's width cost is no longer growth
paid for science but resolution on one half of the asset bought with resolution on the other.
Recorded as a reframing, **not** as a decision — it stays the director's under R13.

**WHAT IS STILL TRUE AND UNFIXED.** The finding's central observation stands: `saas/enterprise_
value.py` still computes the discounted book and still carries the mission's noun. That was
never what this asked for — the docstring is honest about what it computes and a rename would
have satisfied a word and changed nothing measurable. What has changed is that the book is no
longer the *only* thing measured.

**AND THE FIGURE IS BOUNDED, STATED BEFORE ANYONE READS IT.** A rank statistic over a handful
of decisions on a handful of accounts has a wide confidence interval. `A46` (book depth) is
upstream of it being worth much, and that remains the director's decision — see the addendum.

## Still live
