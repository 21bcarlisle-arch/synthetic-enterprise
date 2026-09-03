**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The world caveat drops its date on the branch that is about to become live, and calls a live figure history

**Class:** `controls_that_cannot_fail` (primary), `figures_on_a_superseded_clock` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/generate_value_arms_data.py::_world_provenance`, `::_world_clause`.

**LATENT and not BLOCKING, deliberately.** Every artefact on disk today is unstamped, so the live
branch is the one that DOES name its runs and DOES carry the date. Nothing currently published is
invalidated by this. It becomes BLOCKING the moment a stamped artefact goes stale — which the three
floor legs running now make imminent — and it is fixed in the same commit that files it.

## What

`tools/generate_value_arms_data.py::_world_provenance` has two returning branches for "these figures
were not measured in the live world":

- **unstamped** (line ~2720) — an artefact predates the world stamp. Sets
  `runs_that_cannot_name_their_world`, a list of run labels each carrying its `generated_at`.
- **superseded** (line ~2742) — every artefact names its world, and at least one is not the live one.
  Sets `worlds_these_figures_were_measured_in` and `one_world_across_every_figure`, and **names no
  runs at all**.

`_world_clause` composes the headline sentence a reader actually meets. It harvests dates by
regexing `runs_that_cannot_name_their_world` — **a key only the unstamped branch sets**:

```python
runs = world_provenance.get("runs_that_cannot_name_their_world") or []
dates = sorted({match.group() for run in runs if (match := re.search(r"\d{4}-\d{2}-\d{2}", str(run)))})
when = (" The runs behind it are dated {}. ".format(" and ".join(dates)) if dates else " ")
```

So on the superseded branch `dates` is empty and the clause renders **with no date**, exactly
contradicting its own docstring — *"THE DATE IS IN THE CLAUSE, because 'a superseded world' is not
something a reader can place and 'measured on 2026-08-31, before two re-fits' is."*

Two defects, both on that branch:

1. **The date is dropped.** The reader is told "read this as history" and given no date to place it
   by. The drawn direction this page serves states the done-condition as *"the date each figure was
   measured is on the surface a reader sees"*; on this branch it is not.

2. **A live figure is called history.** When runs come from *different* worlds and one of them is
   the live one, the clause still says *"These figures were measured over a departure level that is
   no longer the one this world runs at"* — false for the run that is current. The specific harm is
   that the reader cannot tell **which** figure is stale, and the interesting case is precisely the
   one where the point estimate is live and its error bar is not. That is `c30b98048`, filed
   2026-08-31 on this same artefact: *"the bound that decided 'cannot resolve' was measured in
   another world, and the new one is wider."*

`one_world_across_every_figure` is computed at line 2748 to answer exactly this and is **read by
nothing that publishes** — asserted in one unit test and consumed by no caller. A verdict that is
computed and never read is a fail-silent, not a control.

## Why it has never fired

Every artefact on disk today predates the world stamp, so the **unstamped** branch is the live one
and it does set the run labels. The superseded branch has never executed against real data. It
becomes reachable the instant stamped artefacts exist and then go stale — and
`simulation/departure_level_anchor.py` has been re-fitted twice in 48 hours (`a621edb15`,
`712ae5323`). Three floor legs stamped with the live world are running now
(`se-noise-floor-20260903`, `se-floor-only-20260903`, `se-floor-except-20260903`); the next re-fit
after they land puts the page on this branch.

This is the R15 shape *"a control whose PASS branch is unreachable reports a CONSTANT verdict"*,
inverted: the branch that has never run is the one carrying the defect, and its neighbour's
coverage reads as coverage of both.

## The fix

Landed in the same commit as this finding.

- `_world_provenance`'s superseded branch now names its runs — `runs_measured_in_a_superseded_world`
  and `runs_measured_in_the_live_world`, both label lists carrying each run's `generated_at` — so
  the date is available to the clause on every non-clean branch.
- A distinct **mixed** reason when `one_world_across_every_figure` is false, which says the figure
  and its bound come from different worlds and names which ran where, instead of describing the
  whole page as history.
- `_world_clause` harvests dates from both branches' run lists, and renders the mixed case as its
  own sentence.

## What this does not fix

The page's contrast and its bound still come from two different worlds today, and will until the
three running legs finish and all four artefacts are promoted together. That is the rest of this
lane's work and is not claimed here. This commit makes the surface tell the truth about that state;
it does not resolve it.
