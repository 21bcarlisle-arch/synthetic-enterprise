**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** controls_that_cannot_fail

**Subject:** `tools/generate_value_arms_data.py::_staleness_caveat`, `::_seed_spreads`;
`site/test_the_baseline_comparison_reaches_the_reader.py::test_an_error_bar_older_than_its_figure_says_so_on_the_page`;
the artefact `tools/run_value_cycle_ab.py::noise_floor` writes.

# FINDING — the floor names no book, so the pairing rule is a stamp proxy, and it is wrong in both directions

Found while working out what it costs to publish the leg-conditioning run. It is not that item's
subject and it blocks it, which is why it is filed rather than folded in.

## The rule

`contrast_bounds` (`_seed_spreads`) gates **every directional claim on the page**: no headline may
name a winner unless the contrast clears the noise floor's seed spread. Whether a given floor may
bound a given run is decided by three questions, and until today all three were asked of the floor
alone:

1. does the floor name **a** world? (`world_identity.digest` present)
2. is the floor **not older** than the run? (`_staleness_caveat`, a comparison of `generated_at`)
3. does it carry two or more seeds?

The property all three are proxies for is *was this spread drawn over the book this figure is made
of*. **The floor artefact carries no book identity at all** — `world_identity`, `report_end`,
`clock`, `redraw_scope`, `seeds`, and nothing that says which decisions it ran over. The three-arm
run it bounds carries a full `book_identity`. So the pairing can only ever be argued from stamps,
and a stamp is wrong in both directions.

## Direction one — it refuses a pair that is provably the same world. MEASURED

```
_seed_spreads(floor 06:57:00Z, run 14:00:00Z)  ->  available: False
```

The leg-conditioning re-run is a bit-identical re-run of the run the live floor was measured
beside: `git diff 62334dc76 8b846013e -- simulation/ company/ saas/ sim/` is empty, and the only
non-additive change to the producer is a three-line hoist. Same world digest `39a192ce04c1eda8`.
Publishing it costs the page **every directional claim it makes**, in exchange for one column.
That is the trade this turn declined; see the result document beside this one.

## Direction two — it admits a pair that is provably a different world. MEASURED, and this is the half nobody had named

```
_seed_spreads(floor in world ffffffffffffffff, stamped 01:24:35Z,
              run   in world 39a192ce04c1eda8, stamped 01:24:34Z)  ->  available: True
```

One second of stamp order. The block that gates every direction on the page published a spread from
a different world as the bound on this world's figure, and named no reason because it had none to
name. Question 1 asks whether the floor names *a* world and question 2 never compares it to the
run's, so nothing in the chain ever asked whether the two are the same. `world_provenance` would
have gone amber elsewhere on the page — and `contrast_bounds` would still have been `available`,
and the headline would still have named a winner.

**The two halves are one defect.** The rule refuses what it can prove is safe and admits what it
can prove is not, because it is asking a stamp a question only a book identity can answer. Fixing
only the noisy direction is the asymmetry this project keeps paying for.

## Direction three — the refusal's own reason was false

`_staleness_caveat`'s sentence asserted, on **every** firing:

> *"...and something did, on 2026-08-28: the market gained the ability to DEFEND against a company
> that undercuts it."*

That is the incident the guard was built for, typed into a refusal that fires on any ordering. On
the pair above it would have told a reader the market gained a capability inside seven hours of
2026-09-09. **A refusal whose reason is false is worse than no refusal, because the reason is the
part a reader acts on.**

And the door control was enforcing it. `test_an_error_bar_older_than_its_figure_says_so_on_the_page`
asserted `"DEFEND" in rendered` under a message reading *"the page says the error bar is old
without naming what changed between the two runs"*. Those are not the same claim. A page that named
a **different** change, correctly, would have gone red; a page that named that change when it had
not happened stayed green. Keyed to the answer, exactly backwards, and it is the fourth instance of
this shape in this file's own history.

## What landed with this finding

1. **`_staleness_caveat`'s clause is composed from the two artefacts.** Same digest: the page says
   the departure surface did not move *and* says what that still does not establish — that the
   floor names no book, so it cannot be shown to have been drawn over the decisions the figure is
   made of. Different or absent digests: both are named. **The ordering predicate is untouched**,
   so no pair admitted before is refused now and none refused before is admitted; only the words
   differ. The widening that suggests itself here — clear the guard whenever the digests agree —
   is refused, and direction two is why: the digest is the departure level, the book can change
   without the anchors moving, and that is precisely the 2026-08-31 defect this guard was extended
   for.
2. **`_seed_spreads` refuses a floor whose world is not the figure's**, naming both. Distinct from
   the live-world claim the block deliberately declines to make: this asks whether the floor's
   world is the world of the figure it bounds, not whether it is today's, so the superseded panel
   keeps its own bound.
3. **The door control is on the property**: the rendered caveat must name the two run stamps the
   ordering is between (read off the caveat itself, not hardcoded) and must say what is known about
   whether the two runs describe one world — on whichever branch the artefacts earn.
4. **Nine of this file's own controls were pairing a fixture-world floor with the LIVE run**, and
   the world gate is what surfaced it. `_floor_with_spread` typed `"fixture-world"` beside a
   comment arguing that its subject is the superseded panel, "whose bounds are admitted on naming
   a world and not on naming THIS one" — but every caller pairs it with `_load(THREE_ARM)`. It was
   never the superseded panel; it was a mismatched pair that went green because nothing compared
   the two worlds. The digest is now derived from the run, exactly as `_stamped_after` derives the
   stamp one property along and for the same reason. And one control's **null rung was the
   fail-open itself**: *"Stamp it — any world — and the direction comes back"*, asserted as proof
   the guard is not a machine for refusing. It now stamps the run's own world, and keeps
   `"any-world"` as a second rung that must be **refused** — the two together are what separate
   "names a world" from "names the figure's world".
5. **Seven controls, mutation-proved.** Reachability over the whole partition asserted first, then
   the legs. Killed: restoring the hardcoded clause; the same-digest widening (kills two); dropping
   the digest from the sentence; treating two absent digests as agreement; deleting the world gate;
   refusing when the *run* names no world. **One mutation SURVIVED and it is an equivalence, not a
   kill** — comparing against the live world digest instead of the run's, which no artefact in the
   tree can distinguish because every three-arm run on disk is in the live world. Recorded rather
   than quietly dropped, and a synthesised leg (a floor and a run agreeing in a third world) now
   separates the two rules; with it the mutation dies.

## What is still owed, and it is the actual repair

**`noise_floor` should stamp a book identity onto its artefact**, the way the three-arm run already
does. Then the pairing rule reads it, a re-run of an identical book pairs freely however the stamps
fall, and a floor from a different book refuses however the stamps fall — and both directions above
close for the same reason instead of being patched one at a time. It is not done here because it
needs a floor re-run (hours) and because the nine-seed floor now in flight
(`longjob-noise-floor-20260909b`, started 09:05Z) would have to be redone to carry it. Filed as
what it is: the stamp rule is a proxy, both patches above are still patches on a proxy, and the
book identity is the thing that would retire it.

Severity **LATENT**: nothing on the live page is wrong today — the live pair shares a world and the
floor is the newer — and both directions are one promotion away from mattering.
