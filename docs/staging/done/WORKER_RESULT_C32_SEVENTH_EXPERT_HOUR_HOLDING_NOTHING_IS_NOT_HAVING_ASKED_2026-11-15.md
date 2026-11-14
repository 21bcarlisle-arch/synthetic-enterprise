# C32's seventh Expert Hour: holding no evidence is not having asked

**Fate (2026-11-15):** RESULT. **C32 stays at level 2.** The pass failed on items 2 and 4, in
winter. The defect is fixed in this tick, with commons §2 and §4 amended first.

**Blocker:** an eighth blind pass is owed, on one rule only. In winter, the licence decider reads
"cannot determine" for any household not otherwise protected, naming SLC 27.11(A). I chose that
rule and graded it in the same tick.

**Why this was drawn and not skipped.** The draw asked for the fifth pass. That pass and a sixth
had already landed (a333b8d772, a4f0da0b04), so the ask was spent. The sixth had named the
seventh pass as the blocker, owed on "any evidence held" by an instance that did not write that
fix. This instance did not write it.

## The pass

- **Reviewer:** a fresh agent with no tools (0 tool uses), as a veteran of PSR and
  debt-and-disconnection operations.
- **What it was shown:** the sixth pass's plain words, with the Safety Net paragraph rewritten to
  the two-strength rule:
  - six categories read "prohibited";
  - any other evidence held reads "cannot determine";
  - a household is permitted only when the company holds no evidence on it;
  - the over- and under-protection stated.
- **Measured before writing it:** the restatement was checked against `safety_net_on_record` at 15
  Jul 2024, case by case.
- **Ledger:** row 2026-11-15T00:30Z in `docs/observability/blind_review_ledger.jsonl`. It has 14
  questions, 8 of them disqualifying. `--audit` reports the blindfold intact on all 18 rows.

**The reviewer's first doubt was the finding.** "No evidence" mostly means "never asked", so a
supplier that records less disconnects more.

## What the doubt found, measured

On **15 Jan 2024**, a household with no registration, no flag and no birth date was **permitted**.
No company path holds a birth date, so that describes every household the company knows nothing
about.

- **The licence.** SLC 27.11(A) (S8, read in the instrument) requires all reasonable steps to
  ascertain whether 27.10 or 27.11 applies before disconnecting. Such a household may be an
  80-year-old living alone, whom 27.10 prohibits disconnecting.
- **The commons already said it.** §2 read "an unasked question is an unmet duty".
- **The code did not apply it.** The decider read the duty only where something was on record.
  Its own docstring says "when no birth date is passed, the flag alone decides".
- **The packet was also wrong.** It described a missing birth date as "cannot determine". That
  sentence was carried over from the sixth pass's wording, and the code did not do it.

## The fix

**Knowledge first.** Commons §2 now carries the correction beside the 27.11(A) bullet. §4 carries
the amendment, with its design choice, cost and reversal.

**What changed in the code:**
- **`_disconnection_protection`.** In a winter month, any household the licence does not already
  protect now reads CANNOT_DETERMINE, naming 27.11(A).
- **`protection_weighing_undetermined`.** When the base answer already cannot determine, a term
  is still named if assuming it would change the answer. Elderly in January turns the answer into
  the 27.10 composition question, which tells the agent what to ask. A term that changes nothing
  is not named: the child-dependent flag, and language support. Without this, the fix would have
  dropped "elderly" and "needs code 22" from the reasons.

**After the fix:**
- In every winter month, no household with no evidence is permitted. The control checks every
  composition, with four birth dates: none, 1985, 1961 and 1944.
- In July, a household with no evidence and a birth date that is absent or from 1985 is
  permitted, so the permit branch is still reachable.

**Controls:**
- **New:** `test_a_winter_household_held_nothing_on_has_not_been_asked`, over the whole partition.
- **Four older controls held a winter permit for a household held nothing on.** That is the
  defect, keyed to the answer of the day. Each now permits in July and refuses in January:
  - `test_the_licence_rule_is_asked_and_every_answer_is_reachable`;
  - the sixth pass's partition control;
  - `test_an_established_age_protects_and_a_young_one_does_not`;
  - the child-dependent leg of `test_an_undetermined_term_that_could_protect_...`.

**Mutations, all red, run in a scratch worktree:**

| Mutation | Tests failed |
|---|---|
| winter leg dropped | 5 |
| winter leg applied all year | 10 |
| refuse everything | 8 |
| term naming reverted | 2 |
| a term named though it changes nothing | 1 |

**Tests:** 548 pass across the 15 test files that import the deciders.

**What it costs.** No winter disconnection at all, until an ascertainment step (contact, a visit)
exists. That step belongs to the collections atom.

**Reversible** by removing the `if in_winter:` leg at the end of `_disconnection_protection`.

## The other items

| # | | grade |
|---|---|---|
| 1 | DISQ | **Partly.** The permit branch is proven reachable, in July, by the new control. There is no run, so there is no count. This is the same open item as fourth pass item 7 and sixth pass items 6 and 12. |
| 2 | DISQ | **FAILED in winter, fixed** (above). Summer stays open: the Safety Net's "knowingly" sets no duty to ask, so a summer household never asked is permitted. That is the collections atom's ascertainment step, already named by the fifth and sixth passes. |
| 3 | DISQ | **Open, collections atom** (sixth pass items 3 and 4): ability to pay, notices, the warrant and the site visit. |
| 4 | DISQ | **The same defect as item 2,** fixed through 27.11(A). Inferring vulnerability from free-text contact history beyond the agents' flags is not built. |
| 5 | DISQ | **Open, within the claim.** This is sixth pass item 7, restated wider. No production caller disconnects today. `disconnection_warning.can_disconnect` reads no vulnerability, and the first caller must route through the one decider. The other paths are unverified: a remote smart switch to prepay, de-energisation on change of occupancy, and prepayment self-disconnection. These are named for the eighth pass. |
| 6 | DISQ | **Outcome passes, vocabulary partly.** Any registration blocks every month. The "vulnerable situation" limb of SLC 26.1(a) is mapped to temporary life change (commons §1). A standing catch-all category is not held. |
| 7 | DISQ | **New, not yet established.** The needs-code list is not versioned by date. Under the "any evidence" rule, a code read in a year before it existed can only add protection, so there is no harm on the disconnection outcome. It is a fidelity gap, to file. |
| 8 | DISQ | **Outside the claim.** Whether the world charges the supplier for not disconnecting is a world and collections question. It belongs with M2's two sides of value. |
| 9-14 | SUPP | Known gaps from earlier passes: resolving a "cannot determine", the 24-hour reconnection (fifth pass item 10), network sharing and data cleanse, PSR services, the instrument text by year, and sex-specific pension age before 2018 (handled as "cannot determine", which the reviewer accepted). |

## Verdict

**FAIL on items 2 and 4, fixed in this tick in the direction of protection.** Held at 2. If the
eighth pass, on the 27.11(A) winter rule alone, raises nothing within the claim, the level moves.
Item 5 must be graded in that pass.
