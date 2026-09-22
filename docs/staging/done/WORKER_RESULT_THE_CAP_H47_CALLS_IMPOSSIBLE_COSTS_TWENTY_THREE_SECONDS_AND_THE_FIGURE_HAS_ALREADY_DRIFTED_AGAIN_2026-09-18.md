# The cap H47 calls impossible costs twenty-three seconds, and the figure has already drifted again

**Date:** 2026-09-18
**Lane:** H_harness (drawn as LANE 1 BUILD — `H47_the_orientation_header_states_a_figure_it_computes`,
level 2→3, `loop_stage: harden`, `expert_hour.status: attempted_finding_open`)
**Subject:** `tools/startup_anchor_freshness.py`; `CLAUDE.md` Build line; `docs/PROJECT_OVERVIEW.md`
**Severity:** LATENT — the gate is green and stays green. The content is that it is green over a
figure that is currently wrong, and the reason it cannot notice is a bound this atom's own residual
already names.

---

## The residual, and the sentence that closed it prematurely

H47's Expert Hour record ends: *"EH-3 repaired in part the same day … **Residual: floored, not
capped.**"* The module says why, in its own docstring (`tools/startup_anchor_freshness.py:89`):

> *"It floors the figure and does NOT cap it — `@parametrize` expansion is unbounded, so **only a
> real collection could** — and the published table says so in the reader's own words."*

Every clause of that is true. The half that was never measured is what a real collection *costs*,
and that is the number the design turns on.

## Measured

```
$ python3 -m pytest --collect-only -q -p no:cacheprovider
37065 tests collected in 16.93s          # 23s wall clock including interpreter start
```

**Twenty-three seconds.** The cap is not impossible; it is cheap. "Only a real collection could"
was read as *therefore no cap*, when the missing step was to price the real collection.

## The same measurement exposes a live instance

```
$ python3 -c "import tools.startup_anchor_freshness as saf; ..."
commits    stated=  10,474  band=10144-10523   floor=None    -> AGREES
lines      stated= 960,622  band=925703-967049 floor=None    -> AGREES
modules    stated=   2,948  band=2898-2959     floor=None    -> AGREES
tests      stated=  36,838  band=26731-36838   floor=33511   -> AGREES
```

| | |
|---|---|
| stated, in both documents | **36,838** |
| index floor (what the control can see) | 33,511 |
| **real collection** | **37,065** |
| verdict | **AGREES** |

The published figure understates the suite by **227**, and the control agrees with it — correctly,
by its own rules. Nothing here is a bug in the floor: the floor is doing exactly what it was built
to do. It simply cannot see this.

## The number that makes the residual concrete

**The floor sits 3,554 below the truth, and that gap is the control's blind width.**

That is not a tolerance anybody chose — it is the ratio of `@parametrize` expansion to bare test
functions, and it drifts on its own. It is also the honest measure of how far the *original
incident* could run again before this control noticed: the 2026-09-17 finding was 26,731 stated
against 36,838 real, and the repair catches that case only once the figure falls below 33,511. A
figure that goes stale while the suite grows by fewer than ~3,500 collected items is invisible, and
the drift already on file is 227 of that budget spent.

Keyed to the property rather than today's numbers: **the floor's headroom IS the recurrence window,
it is currently 3,554 wide, and only a real collection closes it to zero.**

## What this turn did NOT do, and why

**It did not add the cap.** That is a change to `figure_verdicts` — a function carrying twelve
mutation-proven legs, two of them (`test_the_floor_CANNOT_BE_MOVED_by_the_hand_typed_line_it_exists_to_check`,
`test_a_test_count_BELOW_THE_INDEX_FLOOR_is_refused_though_both_documents_agree`) built specifically
to stop this leg being softened. Landing a half-designed cap into it at the tail of a bounded
invocation risks reddening every lane's commit gate, and the design question underneath is real and
unanswered: a 23-second collection is cheap for a commit gate or a daemon tick and **not** cheap on
the session-startup path this module also serves. That belongs to a turn that can carry it.

**It did not move the figure to 37,065.** Tempting, and wrong to do quietly. The band's high end is
taken from the CLAUDE.md Build line itself, so `PROJECT_OVERVIEW.md` alone would read `OVERSTATES`
and refuse; making it pass means editing **both** documents in one commit — which is the precise
move EH-3 identified as the hole (*"an author who invents a count and updates both documents in one
commit was agreed with"*). Doing it on the strength of a real collection is legitimate, but it
should land *with* the collection wired in, not ahead of it, or the next reader cannot tell the two
apart. CLAUDE.md's own instruction is to correct the Build line **at each phase close**; this is not
one.

## What the next turn on H47 owes

1. Wire the real collection as the cap, on a path that can afford 23s — **not** session startup.
2. Then move both documents to the collected figure, in the same commit as the wiring, so the
   correction is evidence-backed rather than typed.
3. Key the new leg to the property: a stated figure that no truthful collection could produce is
   refused **in either direction**. The existing `..._IN_EITHER_DIRECTION` leg names that intent
   already; today only one direction has a source that cannot be typed into.

Until 1 and 2 land, `expert_hour.status` stays `attempted_finding_open` and the level stays 2. This
finding changes what is *known*, not what is built: the residual is no longer "impossible", it is
**priced at 23 seconds**, and it has a live instance.
