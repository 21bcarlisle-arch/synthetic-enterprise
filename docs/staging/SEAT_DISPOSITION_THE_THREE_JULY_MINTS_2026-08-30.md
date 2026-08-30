**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `H45_the_queue_is_chained_to_the_map`

# The three July mints, dispositioned: one is finished, one is stuck on something real and small, one is waiting on a run

**Occasion:** `[ACT] 3 SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for 2.2h` — filed
2026-08-22, live for eight days, asking the only question worth asking: *"Draw them or explain why
they are stuck."* This is the explanation, one per mint, with the evidence beside each.

The alarm's premise was that the draw was wedged or resting. Neither. **The three have three
different states and none of them is "nobody looked".**

---

## 1. `PLANNER_MINTED_generator_draw_wiring_2026-07-24` — FINISHED. Archive it.

Not stuck: **done, and done seventeen days ago.** The mint was held from 2026-07-24 on one R13
curriculum word, which arrived on 2026-08-13 — *"Authorised: activate the population draw
(SE_DRAW_POPULATION) and wire the entrypoints. The book stays earned, never granted. Tell me
before any published figure moves, and re-baseline honestly."*

Measured on the live roster this morning rather than read off the mint's own header:

```
electricity legs by acquisition_type: {founder: 9, synthetic_draw: 51, net_new_won: 90}  total 150
docs/design/curriculum/population_draw_activation.json: activated.value = true,
  status "ACTIVE — director-authorised 2026-08-13", profile B_trickle_lambda_1.0
```

The activation is a committed versioned artefact rather than an environment variable, so the
activated world is reconstructible from the repo alone; 51 drawn legs are live and earned at the
director's Profile B trickle. Its own header already said *"REMAINING #3 IS DONE, the block is
gone, and this doc is now a re-baseline follow-through"*, and the re-baseline it was following
through on has been happening continuously in the publish cycle ever since.

**It has been sitting in `in_progress/` as a finished piece of work for seventeen days, and it is
one third of an alarm that has fired for eight.** That is the whole of its contribution to the
condition.

**One correction it forces elsewhere.** `docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md` §3 states, as
a thing the roadmap "must not re-litigate", that *"`SE_DRAW_POPULATION` is default-OFF and
director-reserved; the varied pool is armed but no published run consumes it."* Written
2026-08-27, fourteen days after activation, and false when written. It matters because that
document's §3 uses it to argue that flipping the population "would yield a book varied in
composition and identical in behaviour... theatre" — an argument whose premise is that the flip
has not happened. The flip HAS happened; the conclusion about behavioural inertness stands on the
attitude axes being unwired, which is independently true, so the argument survives its false
premise. Corrected here rather than silently in that file, and folded into
`docs/design/CHOICE_AND_CHANNEL_ROADMAP.md`.

---

## 2. `PLANNER_MINTED_one_node_to_depth_with_charts_2026-07-28` — STUCK, on something real, small, and now named

Its owed work is *"verify the four rung-5 charts on the LIVE surface (R11, deferred to 'the next
publish' and never taken), then self-certify the level on that evidence."* No director act is
involved. So why has it not been done?

Because it looks done. The four charts each carry three controls —
`_present_and_pipeline_sourced`, `_chart_renders_to_svg_from_data`, `_chart_is_data_driven_not
_constant` — plus a DoD gate asserting all four render and two both-ways mutations. Forty-three
tests pass. Anyone opening that suite concludes the verification exists.

**It does, and it is not the verification R11 asks for.** Those tests drive the page through
`site/knowledge/electricity-wholesale/_render_harness.mjs`, a PER-DOOR harness. The generic
harness's own docstring is the indictment, and it was written about exactly these files:

> Every existing harness in this repo (`site/*/_render_harness.mjs`, `site/proof/_door_harness.mjs`)
> is written PER DOOR: it imports the page's inline script and then calls that page's render
> functions BY NAME, in the page's own order. That is fine for a door-level unit test, **but it
> cannot be pointed at the LIVE site**, and it goes stale the moment a door renames a render
> function.

R11's whole point is that "done" for a user-visible surface means the value RENDERED on the live
surface, and the failure it exists to catch is the one a by-name harness passes straight through:
page deploys fine, its json 404s or drifts schema, every panel sits on "Loading..." forever.

**So the owed work is genuinely still owed, and it is now a defined task rather than a deferral:**
re-verify the four charts through `site/_live_harness.mjs`, which supplies only `fetch` and lets
the door's own boot sequence drive itself. That is the same move made this morning for the
consolidated Knowledge pages
(`site/knowledge/test_the_consolidated_pages_render_their_own_record.py`), so the pattern is
landed and the second application is cheap.

**Sequenced: next site-lane item.** Not drawn in this turn because it is a different lane's
subject from the brief in hand and because writing it while two gated jobs were in flight on the
shared tree would have been the fix-on-sight this project keeps paying for.

---

## 3. `PLANNER_MINTED_value_chain_observation_window_cap_2026-07-24` — WAITING ON A RUN, correctly

Fourteen touches, and the fourteenth block rested on trigger (a): the `mc2_collateral_death_test`
key appears in `run_output_latest.json` only on the next auto-processed sim run, after which the
site render becomes drawable.

That trigger could not fire for seventeen days, and not because of a director act:
`run_phase2b.py` had emitted the key on every run since 2026-07-27, and the publish reduction
(`saas/reporting/annual_report.py::extract_report_data`) is a WHITELIST that never listed it. The
key was computed and dropped on the way to the file the trigger watched — the module's own
self-named "silent-drop class", fourth instance. That was repaired on 2026-08-13. Trigger (b) moved
the same day with the SE_DRAW_POPULATION activation. Triggers (c) the §6 survival score and (d) the
WVC_R world-half remain walled and are not mine.

**So it is not stuck; it is waiting on the next auto-processed publish — which is itself the thing
that has been flapping.** The two alarms are coupled: `[PUBLISHING DOWN]` was refusing the very
commits that would fire this mint's trigger. Both publish refusals this morning are now cleared
(one a real mobile-layout defect on `/capabilities/`, one an unlanded control of mine), so the next
successful auto-publish should discharge trigger (a) without anyone drawing anything.

**Action: none. Re-check after the next green publish**, and if the key is still absent, the
whitelist repair did not hold and that is a fresh finding rather than this mint's problem.

---

## What this says about the alarm, which is the part worth keeping

The alarm asked whether the draw was wedged. It was not. Of three items sitting undrawn for eight
days: **one was finished**, one was **waiting on a mechanism that was itself broken**, and only one
had real work owed — and that one looked done to anyone who opened it, because it carried
forty-three passing tests that verify the wrong surface.

None of those three states is "undrawn". The queue was reporting a shape it could see (a marker
that says self-drawable, a file that has not moved) rather than the one that matters (is there
work here, and is anything stopping it). A finished mint left in `in_progress/` is
indistinguishable from a stalled one, and it will keep firing this alarm forever.

**The cheap repair, if it is wanted:** a mint whose owed work is discharged should be archived by
the act that discharges it, and the alarm should distinguish *undrawn* from *unarchived*. Filed as
an observation against `H45_the_queue_is_chained_to_the_map` rather than as a new atom, because
that atom is P8 and this is exactly its subject.
