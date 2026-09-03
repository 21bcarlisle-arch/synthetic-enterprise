**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The mixed-world verdict has no branch for a live leg beside an unstamped one

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Established by reading `_world_provenance` and its caller, not by measurement, so this is a finding
and not a prediction.*

---

## What is wrong

`tools/generate_value_arms_data.py::_world_provenance` has three verdicts and only two of them can
be reached today.

1. **Unstamped** — any artefact carries no `world_identity`. Returns early with
   `available: False`, and sets **no** `one_world_across_every_figure` key.
2. **All stamped, all one world** — clean, `_world_clause` renders nothing.
3. **All stamped, more than one world** — sets `one_world_across_every_figure: False`, and
   `_world_clause` renders *"THE FIGURE BELOW AND THE BOUND ON IT WERE MEASURED IN DIFFERENT
   WORLDS."*

Branch 3's own comment states the rule it was built for:

> `MIXED IS NOT HISTORY. When one leg IS the live world, "read this as history" is false about that
> leg, and the falsehood runs in the direction that stops a reader asking which figure is the stale
> one -- when which figure is stale is the entire question.`

**That rule is implemented for exactly one of the two ways a page can be mixed.** A page holding a
run stamped with the LIVE digest beside a run that predates the stamp is mixed in precisely the
sense the comment describes — and it takes branch 1, because branch 1 fires on the presence of any
unstamped artefact and returns before the mixed test is ever reached. `_world_clause` then reads
`one_world_across_every_figure` with `is False`, finds the key **absent**, and falls through to
`"READ THIS AS HISTORY, NOT AS TODAY."`

So the sentence a reader meets is false about the one figure on the page that is current, and false
in the direction that hides which figure is the stale one. That is the defect branch 3 exists to
prevent, arriving through the door branch 3 does not watch.

## Why it has never fired

Every artefact on disk until 2026-09-03 predated the stamp, so branch 1 was the only live branch and
its neighbour's coverage read as coverage of both. This is the same shape the file already records
one layer down — *"It had never been caught because every artefact on disk predates the world stamp,
so the unstamped branch is the live one and its neighbour's coverage read as coverage of both."*
The previous repair fixed the missing DATE on branch 3. It did not ask whether branch 1 could also
be mixed.

**It becomes live the instant the page reads `value_cycle_ab_s1_three_arm_20260903.json`** — the
three-arm leg re-run in the live world, landed as `416e829c7`, `world_identity.digest`
`39a192ce04c1eda8`, which is the live digest. The floor and the decomposition are still the
2026-08-30/31 artefacts and carry no stamp at all, because their re-runs are in flight.

## The repair

Branch 1 gains the mixed test rather than a second copy of the mixed sentence: it now partitions the
artefacts into those that name the live world and those that cannot name any, and when both sets are
non-empty it sets `one_world_across_every_figure: False` and populates
`runs_measured_in_the_live_world`, which is what `_world_clause` already keys on. **No new sentence
is written and no new branch is added to `_world_clause`** — the existing mixed verdict is made
reachable from the state that can actually produce it. `available` stays `False`, because a page
that cannot name one of its worlds still cannot be shown current; what changes is that the verdict
no longer calls a live figure history.

## What it costs while it stands

Nothing was published wrongly, because the page did not yet read the live-world run. The cost is
that the correct order of work was blocked: the live-world contrast could not be put on the page
without the page then mislabelling it, and the honest interim state — *one leg current, its bound
absent, and the page saying so* — had no verdict to render.

Related: [`c30b98048`], and
`SEAT_FINDING_EVERY_CONTROL_ASKED_IF_THE_FIGURE_WAS_RIGHT_AND_NONE_ASKED_IF_ITS_WORLD_STILL_EXISTED_2026-09-03.md`.
