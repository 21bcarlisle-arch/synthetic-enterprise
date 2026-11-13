**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Draft M3 wording for the hidden per-household utility, for the advisor to read before it lands (2026-11-13)

**What this is.** The 13 Nov ruling
(`docs/staging/advisor/done/DIRECTOR_RULING_CAP_BASELINE_YES_AND_A_HIDDEN_WEIGHTED_UTILITY_THE_SUPPLIER_MUST_DISCOVER_2026-11-13.md`)
asks for M3 wording that adds a world-side utility, weighted by each household's own hidden weights. The
advisor reads the draft before it lands in `docs/design/DIRECTOR_CANON.md` with the trailer
`Director-doc: his-words -- 13 Nov 18:59 ruling on value-test-baseline-and-axis-weighting`. Nothing in canon
changes until then.

## The draft (the changed sentences only; the rest of M3 stands verbatim)

Today: "Each is measured in its own unit and never converted to pounds. Comfort and health are a floor, not
a currency: no gain in any need justifies a breach."

Proposed:

> Each is measured in its own unit and never converted to pounds at a rate the company or the scorer
> chooses. Each household also weighs these needs by its own weights, hidden in the world as part of its
> life: the value created for it is its gain in that weighted utility, which the supplier never sees and
> must discover from what a real supplier could observe. The utility is always published beside the
> vector, never instead of it. Comfort and health are a floor, not a weight: no gain in any need, and no
> gain in utility, justifies a breach.

The provenance note would add: *(Amended 13 Nov on his words "I think a weighted utility score is a good idea
and a way to capture enterprise customer value creation. NB this needs to be hidden in the SIM and
underlying. The supplier must discover it"; the 31 Oct wording is in git history.)*

## The unit: a pound unit IS still a risk, and the proposal for it

The ruling invites this: "If the machine thinks a pound unit is still wrong for the utility, say so with a
proposal."

- **Why a bare, unitless utility does not work.** The headline is a per-household-year gain averaged over a
  book. Averaging needs the households' gains to be on one scale. Unitless utilities cannot be compared
  between households, so their mean is not a quantity (CLAUDE.md: "before dividing two numbers, say out loud
  what each one counts").
- **Why plain pounds is the risk.** If the utility is in pounds, it reads as a bill saving. That invites the
  exact confusion M2 guards against: a bill cut that is pure transfer would look like value created.
  Willingness-to-pay also scales with income, so a pound scale counts a gain to an affluent household more
  than the same change to a precarious one.
- **Proposal.** Express each household's gain as the money it would itself trade for the change, by its own
  hidden weights. In economics this is its compensating variation, so the scale is common but each exchange
  rate is the household's own. Publish it under its own name and unit (for example "household-valued £",
  never just "£"), with three things beside it: the vector; the transfer component (the part that is only
  the household's bill moving against the supplier's margin, which M2 requires shown as transfer); and the
  same mean reweighted equally across precarity bands, so the income effect is visible rather than hidden.
- **What would change this.** If the knowledge page (K8, written first) finds the weight evidence is too weak
  to put a money scale on time or certainty, the fallback is a per-household rank (share of households
  better off by their own utility), which needs no common scale. The knowledge page decides this, not this
  note.

## Sequencing (the machine's call, with its reason)

The first redesigned value-test run reports the **vector**. The utility follows a run later. Reason: steps
1 to 5 are filed and running, and the utility needs a knowledge page, a world-side weight draw tied to the
parsimony factors, and household responses that follow from it, built on the activation-energy and
resentment mechanics. Fitting all that into the step in flight would change two things in one run, and
the result could not be attributed. Sunday's balance proposal (`docs/operations/`, 16 Nov review) carries
the cost and the queue position, and is held to the 70% usage reading's 0.45-points-an-hour pace.
