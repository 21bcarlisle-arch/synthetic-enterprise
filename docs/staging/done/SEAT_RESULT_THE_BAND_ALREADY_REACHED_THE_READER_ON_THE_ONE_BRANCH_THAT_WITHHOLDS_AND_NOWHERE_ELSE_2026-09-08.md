# The band already reached the reader on the one branch that withholds, and nowhere else

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Lane 0 delivery, 2026-09-08.** Claim:
`the-published-advantage-is-the-top-of-its-own-redraw-band`.

RECORDED rather than LATENT: the defect it names is closed in this same commit, by a control that
is mutation-proven on the branch that had none. What is left open belongs to another lane and is
stated at the foot.

## The drawn premise, and how much of it was spent

The direction read: *"`site/data/value_arms.json` publishes £2,335.87 while carrying redraw_min
£450.99, redraw_mean £1,450.64 and redraw_max £2,433.70 in the same object, and no HTML or JS file
under `site/` mentions any band field — the reader is shown the winner of the redraw and not the
redraw."*

The literal half is true and is not the defect. No file under `site/` names a band field because
the capabilities page renders `d.headline` wholesale, and the headline is composed in
`tools/generate_value_arms_data.py`. Asked of the rendered page rather than of the source, all
three figures were already there — £451, £1,451 and £2,434 for the advantage, and −£8,634,
−£1,861 and £2,350 for the selection leg, whose centre is NEGATIVE beneath a positive published
draw. A reader who opened the page today met the family.

**They met it on one branch.** The band was composed inside `verdict_withheld_because` and inside
the withheld arm of `_leg_clause`, because that is the branch it was written for. The branch that
STATES a verdict — `That figure CLEARS the £991 this same contrast moves across 3 seed re-draws` —
printed the stdev and no family at all. So the property held by accident of which way today's
seeds fell, and it would have been lost silently on the day they agreed.

That is the direction's own sentence, one layer along, and pointed at the branch where it costs
most: "£2,336 CLEARS £991" is the most quotable thing this page can produce, and it is the reading
that most needs "...from a family spanning £451 to £2,434 whose centre is £1,451".

## What was actually wrong, and it was a control

`site/test_the_baseline_comparison_reaches_the_reader.py` asserted the band **inside `if
withheld:`**. That is this project's named backwards-control shape: it goes green on exactly the
day the page states a direction and drops the family. The control could not have caught the defect
it was standing next to, and no other control asked.

## What landed

1. **`_redraw_band_clause`** — one producer of the span/mean/placement sentence, replacing three
   copies (`verdict_withheld_because`, the withheld clause, and nothing at all on the stated
   clause — which is how the mean came to be in two of them and the placement in one).
2. **The stated-verdict branch of `_leg_clause` now carries the band**, and the leg publishes it
   as `redraw_band` so it is a field and not only prose.
3. **The door control is keyed to `verdict_stability.checked`** — did the rung RUN — and not to
   what it concluded, and it runs over BOTH legs. A new verdict branch that omits the band now
   reds here rather than shipping.
4. **A builder-level witness for the branch that had none.** The committed artefacts withhold, so
   every control over this could be satisfied by the branch that was already right. A substituted
   unanimous floor of £20,000/£20,100/£20,200 reaches the stated branch, and it is centred ABOVE
   the £12,071 published draw on purpose — so the sole witness that the placement sentence can say
   the unflattering thing is on the branch where "ABOVE" is the reading a reader most needs.

Both mutation-proven, run and reverted: stripping the band from `_leg_clause`'s stated branch reds
the builder witness; stripping the band sentence from the live feed's headline reds the door.

## What did NOT land, and why

`site/data/value_arms.json` was not committed. The shared working tree's copy of
`generate_value_arms_data.py` carries ~190 lines of another lane's uncommitted work (the
`later_runs_in_this_world` census), and the shared tree's feed carries its OUTPUT — `later_runs_*`
keys that exist in no committed producer. Landing that feed publishes a census whose code is not
at HEAD.

Regenerating from a clean HEAD extract is not the answer either: the extract has no gitignored run
data, so `realised.is_the_published_supplier` degrades from `checked: True` to `checked: False`,
and landing it would publish a refusal the real tree can answer.

So the code landed alone, and it is safe to: **HEAD's committed feed already satisfies the new
control** on both legs — asserted before landing, not assumed. The rendered page is unchanged
today. What changed is that it can no longer quietly stop being true.

## What is next

The other lane's `later_runs_in_this_world` work needs landing by its own author; until it does,
the shared tree's feed and its producer disagree with HEAD, and any publish from that tree carries
one without the other.
