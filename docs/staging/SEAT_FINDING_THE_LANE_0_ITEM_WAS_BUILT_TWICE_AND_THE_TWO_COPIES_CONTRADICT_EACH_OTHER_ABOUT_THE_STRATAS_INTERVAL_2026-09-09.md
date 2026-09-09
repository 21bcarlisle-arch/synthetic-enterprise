**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the published inversion must carry its attribution on the page) · **Class:** measurements_that_mirror

**Subject:** `tools/run_value_cycle_ab.py::pair_strata`, `::cross_stratum_null_spread`,
`::_pair_strata_reading`; `tools/generate_value_arms_data.py::_skill_pair_strata`,
`::_pair_strata_interval_clause`; `site/capabilities/index.html::pairStrataBlock`;
`site/data/value_arms.json::method_skill.fixed_horizon.pair_strata`.
Commits `b16281092` (local, unpushed) and `2df665040` (origin/main).

# FINDING — the Lane 0 item was built twice, and the two copies contradict each other about whether the strata have an interval

## The drawn premise is spent, and its own grep was already false when it was written

The item asked me to wire `run_value_cycle_ab.pair_strata` through to the reader, and stated as its
evidence that `grep -rn pair_strata tools/generate_value_arms_data.py site/capabilities/index.html`
returns nothing. It returns twelve lines. The identity is wired, published and rendered on both
sides of the divergence:

* `site/data/value_arms.json` carries `method_skill.fixed_horizon.pair_strata` with all three strata
  (`within_settled` 7,606 comparable pairs at 0.5130; `within_zero` 0 comparable pairs — the tie
  mass; `cross` 4,588 at 0.2686), `the_tie_mass_can_move_the_estimand: false`, and
  `the_stratum_that_carries_the_departure: "cross"`.
* `site/capabilities/index.html:1011` renders it via `pairStrataBlock(fh.pair_strata)`.

All three of the item's deliverables exist. **But no single commit holds all three**, which is the
finding.

## It was built twice, concurrently, by two lanes — and neither copy is a superset

| | local `b16281092` | origin `2df665040` |
|---|---|---|
| `pair_strata` wired to the page producer | yes | yes |
| rendered in `fixedHorizonBlock` beside the 0.4210 | yes | yes |
| door control on the property | yes | yes |
| **the leverage / interval caveat** (`_pair_strata_interval_clause`) | **yes** | **no** |
| **a permutation null for the cross stratum** (`cross_stratum_null_spread`) | **no** | **yes** |
| the split published by the *run* rather than derived by the page | no | yes |
| producer tests (`tests/tools/test_run_value_cycle_ab.py`) | no | yes (+53 lines) |
| `run_value_cycle_ab.py` touched | no | yes (+311 lines) |

The item's third deliverable — *"say plainly what is STILL unattributed … the leverage caveat in its
own docstring (z\*s cross pairs determined by z rows' signals) is a statement about the interval that
the page does not yet make"* — exists **only in the local copy**. Origin does not make it.

Origin's answer to the same gap is better in kind and absent here: it computes
`cross_stratum_null_spread`, an actual permutation null for the cross stratum, and
`_pair_strata_reading` quotes that interval on its `bounded` branch.

## The contradiction a merge arms

The live local page states, as a categorical claim composed into prose:

> "**These strata carry NO interval of their own.** They are terms of the 0.4210 above … so the only
> bound here is the one that figure's own permutation earned, 0.4458–0.5540."

Origin computes precisely such an interval, for precisely one of those strata, and prints it.

The two sentences cannot both be on the page. Today the contradiction is **latent, and latent for a
reason origin itself documented**: origin's bounded branch is unreachable from any artefact on disk.
Its own docstring says so —

> "**No run on disk could reach it** — `pair_strata` landed the same day and every artefact predated
> it, so `_skill_pair_strata`'s identity fallback served the withheld branch to every reader."

So on today's feed origin renders the *withheld* branch, which quotes no cross figure and no
interval, and the local sentence would not yet be visibly false. **The nine-seed pair move already on
origin (`3e85fefe3`, `8b846013e`) is building the first run that will carry the block.** On that run
the bounded branch becomes reachable, and a naive merge that keeps the local prose publishes
"these strata carry NO interval of their own" directly beside a printed interval for the cross
stratum.

This is the shape the project already pays for: a sentence that is true about the feed it was
written against and false about the feed that is coming, with the two halves written by lanes that
could each only see their own.

## Why neither lane could have caught it

Each copy is internally consistent and each passes its own door control. The local control asserts
the reader is shown which stratum carries the departure; origin's asserts the reading quotes the
interval when it has one. Both are keyed to the property, both are green, and neither can see the
other's tree. This is only visible from the seat, holding both sides at once — which is the
interconnection review CLAUDE.md reserves to it.

## Tree state, measured

`HEAD` is **9 behind and 3 ahead** of `origin/main`. Working-tree copies of the five contested code
files equal local `HEAD` (only `site/data/value_arms.json` is dirty), so origin's version is not on
disk anywhere: `cross_null` does not appear in `tools/run_value_cycle_ab.py` as checked out.

The signatures do NOT collide — origin's `pair_strata(settled_leg, estimand_leg, zero_decisions,
cross_null=None)` accepts the local caller's three positional arguments unchanged. **The hazard is
entirely in the prose and the page, not in the call.** That is what makes it easy to merge wrong: a
merge that resolves the Python cleanly still leaves the contradiction standing.

## What is next — the reconcile recipe, not a re-build

Do **not** rebuild either half. The correct resolution keeps origin's producer and demotes the local
sentence from a categorical claim to a conditional one:

1. Take **origin's** `tools/run_value_cycle_ab.py` and `tests/tools/test_run_value_cycle_ab.py`
   whole. It is the superset on the producer side and carries the only permutation null.
2. Keep the local `_pair_strata_interval_clause`, but **rewrite its sentence to compose from
   `cross_null`'s availability** rather than to assert absence: when the cross stratum has a null,
   quote it and keep only the leverage/clustering clause; when it does not, keep today's sentence.
   The leverage caveat is correct under both branches and is the item's own third deliverable — it
   must survive.
3. Add one door control keyed to the property that spans both: *a reader shown a stratum figure is
   never told that stratum has no interval while an interval for it is present in the feed.* That is
   the control neither lane could have written, and it is the only new code this finding asks for.
4. `git merge` is the wrong instrument here — there is no receipt and this tree is dirty across 1,117
   paths. Land through `python3 -m tools.surgical_land`.

## What I am NOT claiming

I have not run either side's test suite in a clean extract, so I cannot say whether origin's door
control is green at origin's HEAD; I am reporting what the two trees *say*, not what they pass. The
prediction that the bounded branch becomes reachable on the first block-carrying run is origin's own
docstring's claim, restated — I have not produced such a run to confirm it. If the nine-seed run
lands and the bounded branch still does not fire, that refutes this finding's urgency but not the
contradiction, which is a fact about the two texts.
