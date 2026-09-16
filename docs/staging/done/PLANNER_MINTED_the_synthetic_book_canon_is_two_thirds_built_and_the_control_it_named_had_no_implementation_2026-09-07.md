<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over

# [PLANNER-MINTED] The synthetic-book canon: five deliverables, two already built, one delivered here, two minted — and the plausibility control it claimed did not exist (2026-09-07)

**Source ruling:** `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, WORK THIS CREATES,
five deliverables. This is the third of the three documents the doorbell drew as unminted; the other
two were settled by `PLANNER_MINTED_the_ruling_and_the_canon_are_seven_eighths_minted_and_the_map_rows_are_not_at_head_2026-09-07.md`
and no longer appear in `background.primary_state_scan.named_but_unminted()` (residue 42, and these
five were the only entries from this canon).

**Mint rule applied:** §2+§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27` — one
atom per named deliverable, and **a deliverable already covered is not re-minted.**

Machine-readable coverage, one line per deliverable:

- Source: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, deliverable 1 — COVERED (built: `tools/stock_joint_generator.py`, commit `122c08ec3`), with a defect found and fixed here
- Source: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, deliverable 2 — COVERED (built: `tools/stock_joint_generator.scotland_type_marginal`, `tools/demand_vector_coverage.py`, commit `122c08ec3`)
- Source: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, deliverable 3 — DELIVERED HERE (`tools/space_filling_sample.py` docstring)
- Source: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, deliverable 4 — MINTED here as `W2_32`
- Source: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07.md`, deliverable 5 — MINTED here as `W2_33`

---

## The five, checked against disk rather than against the commit message

| # | Deliverable | Status | Evidence, checked this tick |
|---|---|---|---|
| 1 | Population generated from a fitted joint rather than selected from survey rows, with plausibility as a control | **COVERED — built**, one defect fixed here | `tools/stock_joint_generator.py` at `HEAD`, landed `122c08ec3`. `fit_joint` over NEED's eight-key co-occurrence, `generate` drawing from it, `generate_independently` as the contrast, `unobserved_share` measuring the difference. |
| 2 | Scotland reachable, and the resulting change to cell coverage stated | **COVERED — built** | `scotland_type_marginal()` reads Scotland's Census 2022 pack and `raked_joint` rakes the fitted joint onto it; `measurement()` reports `scotland_reachable`. The coverage change is stated in `tools/demand_vector_coverage.py:344` — the frame "carried Scotland's 2,508,542 households; only the survey did not" — and the margin moved onto Scotland's own UV402 shares (34.4% flats against England's). |
| 3 | The tail-density principle written where the sampling criterion is documented, as intent rather than side effect | **UNCOVERED → DELIVERED HERE** | Before this tick, `tools/space_filling_sample.py` — the module that *is* the sampling criterion — mentioned tails twice, both as consequence: the `REDUCES_OVER` note calling the draw one that "over-represents the tails of everything except the quantity the price is settled on" (a blind spot to apologise for), and the closing line "the tail curve is what that price buys". The canon's §2 principle appeared nowhere. It is now a docstring section of its own, quoting §2 and naming both halves. |
| 4 | The billing and commercial axes assessed against the demand sample — spanned, or named as an uncounted dimension | **UNCOVERED → MINTED as `W2_32`** | No module measures a billing or commercial axis against the drawn book. `tools/demand_vector_coverage.py` measures the demand vector's five components and declares what it is blind to; meter type, read pattern, payment method, tariff dates, move history and credit position are not among either. |
| 5 | Inflation of a weighted case into a small population kept possible, and not foreclosed | **UNCOVERED → MINTED as `W2_33`** | Nothing asserts this property. It is a negative deliverable — the canon says of both halves "neither is built now, both must stay possible" — so what is missing is not a build but a control, and no control names it. |

---

## The finding: the canon's own named control had no implementation

Deliverable 1 asks for **"plausibility as a control"**, and `tools/stock_joint_generator.py`'s
docstring answered it by name:

> Drawing each attribute independently is what manufactures the impossible ones, and
> **`implausible_share`** measures exactly that difference rather than asserting it.

**There is no `implausible_share`.** The module defines `fit_joint`, `scotland_type_marginal`,
`raked_joint`, `generate`, `generate_independently`, `unobserved_share`, `solid_wall_cavity_share`,
`measurement` and `main`, and the string `implausible_share` occurs exactly once in the whole tree —
in that sentence. `measurement()` reports `solid_wall_cavity_share_observed`.

This is the inverse of the shape this project usually catches. The usual one is a mechanism
implemented without its concept's name, invisible to a grep for the name. This is the **name
published without its mechanism**: a reader grepping the tree for the canon's control finds a
confident sentence, one hit, and no code. A test would not have caught it either — the module has no
test file at all, and the sentence is in a docstring, so nothing executable was ever wrong.

**And the substantive gap it hid is real, which is why the fix is not a rename.** A quantity called
`implausible_share` would be read as covering all eight joint keys. What the module can actually
measure today is one pair — solid wall with cavity insulation, a fabric that does not exist — because
that is the only impossibility for which a rule is written. The docstring now names the two figures
that exist (`unobserved_share` under the joint draw against the same figure under
`generate_independently`, and `solid_wall_cavity_share` as the named instance) and states plainly
that there is no general scalar and why: a general measure needs a rule for what is impossible on
every axis, and this module has that rule for one pair. **An honest gap with a named reason, not a
plausible scalar** — the rule that exists because a number invented to fill a slot is load-bearing
within a week.

---

## What was delivered for item 3, and the thing checking it changed

The canon's §2 is a two-halves claim: *"The choosing deliberately over-weights the tail; the solved
weights restore the mass when aggregating. Both halves are required and neither is a compromise."*

I set out to write that the restoring half was missing — `grep` for `solved weight`, `solve_weights`,
`case_weight` and `restore the mass` across `tools/` and `simulation/` returned nothing. **That was
a grep for the name, blind to the mechanism.** It is built: `demand_vector_coverage.fit_weights`, an
NNLS solve onto the population's CDF at published cut points, with non-negativity enforced on the
stated ground that a negative weight is a household count below zero. The over-weighting half is
`space_filling_sample`'s maximin draw and its `tail_coverage` at `TAIL_QUANTILE`.

So the honest statement is: **both halves are built, in two different modules, and neither module
said so.** That is what the new section records, along with why bypassing either does not degrade
gracefully — over-weighting without the solve publishes a tail-heavy book as if it were the
population, and the solve without the over-weighting is proportional sampling wearing this module's
name.

---

## The two atoms minted

Both are written into `docs/design/maturity_map.yaml` in this commit, with `file_scope` naming
**runnable controls** rather than directories — a level-0 row whose scope names `docs/` cannot be
asserted past by anything, which is why 28 of 34 level-0 rows name no control a runner can execute.

### `W2_32_the_billing_and_commercial_axes_are_measured_against_the_demand_sample`

Lane `W2_customer_generator`, L0 → L2, dial 50, `depends_on: [W2_29]`. The canon rules this an
**open measurement, not an assumption**, and offers both outcomes as acceptable — spanned, or named
as an uncounted dimension. The failure mode is neither: it is a sample sized on demand being read as
if it were sized on billing, which is `W2_28`'s undeclared-reduction shape one seam further out.
Exit asks for a runnable census per named axis, publication of every unspanned axis on a
reader-facing surface, and a control that reds when the canon's list gains an axis the census lacks.

### `W2_33_a_weighted_case_can_still_be_inflated_into_a_small_population`

Lane `W2_customer_generator`, L0 → L2, dial 50. A **negative deliverable**: nothing is to be built,
and what is asked is that nothing else forecloses inflation or a raised count. An intention cannot
hold that — a foreclosure arrives as another lane's reasonable simplification with a green suite —
so it needs a control keyed to the property, not to today's contents. The known hazard is named in
the row: near-duplicates are rejected by construction, so any code reading "one case, one household"
(an integer count, a 1:1 case-to-account join, a uniqueness assumption on the roster) is the
foreclosure, and it will look like a simplification when it lands. Exit requires a poison round,
because a control over a property nobody violates today passes vacuously.

---

## The four at-risk rows are at `HEAD` as of this commit

The prior planner document's own finding was that `W2_28`, `W2_29`, `W1_28`, `W2_30` and `W2_31`
lived only in the shared working tree, and it declined to land them on the ground that a pathspec
commit of the map would carry another lane's 207 uncommitted lines. **Measured this tick, those 207
lines *are* that work** — `git diff -U0` on the map returned one hunk, purely additive, at the end
of the file, containing exactly the five canon rows and nothing else. There was no other lane's
content in it to sweep. They land here, and the exposure the prior document named — that a
`reset --hard`, a mixed reset onto a moved origin, or a whole-file rewrite deletes four map rows and
the coverage evaporates — is closed.

## What this tick did and did not do

**Did:** checked all five deliverables against disk and `HEAD` rather than against commit messages;
found and fixed a named control with no implementation; delivered item 3; minted items 4 and 5;
landed the five at-risk canon rows.

**Did not:** write a test for `tools/stock_joint_generator.py`, which has none — that is a real gap
and it is named here rather than folded into either new atom, because it belongs to deliverable 1's
own row and not to 4 or 5. **Did not** verify the canon's §4 list of billing axes against what the
book carries; that is `W2_32`'s first job and asserting it here would be the answer written before
the measurement.

— Delivery seat, 2026-09-07.
