**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
on the director's question of 2026-09-16 16:55

# The stretch alarm was hosted inside the publisher that was wedged, and the product floor was a sentence

Delivery seat, 2026-09-16. Discharges
`docs/staging/WORKER_FINDING_REPEATING_ALARM_STRETCH_LOG_2026-09-15.md`.
The full account is the stretch entry itself: `docs/status/SEAT_STRETCH_LOG.md`, newest.

---

## The director's question

> *"100 commits today and I can't find the product in them… And the stretch log has been silent
> since 10 September. You diagnosed that silence yourself, fixed it, and the fix has been quiet for
> six days. Fourth instance, second time the repair went mute. So tell me plainly: what did today
> produce that a customer or a domain reader would notice?"*

## The answer, measured

`tools/product_machinery_split` classifies by the PATHS a commit touched, not its subject:

| window | product | machinery | neither | share |
|---|---|---|---|---|
| 50 | 2 | 28 | 20 | 6.7% |
| 100 | 5 | 65 | 30 | 7.1% |
| 200 | 11 | 140 | 49 | 7.3% |
| 400 | 15 | 304 | 81 | 4.7% |

Floor is 25%. Today's 91 commits: **74 machinery, 10 neither, 7 product** — and three of the seven
are merges carrying product paths. Four real product commits, of which one matters: **a gas-only
billing account can now leave this world.** The director's own filter read 36%; the diffs say 7%.
**Commit subjects flatter this project by a factor of five**, which is worth knowing independently
of anything else here.

## Cause 1 — the alarm shared a failure domain with its subject

`raise_stretch_report_owed` was written in `background/process_run_complete.py` and that publisher
was its **only** caller. The publisher last succeeded **2026-09-10 02:35** and not again until
**2026-09-16 14:41**: six days, 34 refused publishes, 184 commits with no report.

So the alarm that says *the machine has stopped telling you why* could not run, because it was
inside the loudest instance of that. **An alarm hosted in the subsystem it reports on is silent
exactly when it is right** — and its silence is indistinguishable from a healthy machine writing its
reports. The hosting was chosen for a good local reason: a report is owed when *a piece of work
finishes*, and the publisher is where finishing is detectable.

This is NOT a fourth instance of *a landed fix is not a running one* (the fix was landed and its
process existed), nor of *a control keyed to a structure that moved*. It is its own shape.

When the alarm finally did fire — 2026-09-15 07:43, on a run that got far enough —
`background/alarm_repetition.py` correctly escalated it to a staging document and suppressed the
page, as designed. The design assumes the queue drains. That document then sat undrawn for 33 hours
behind ~90 others, so the last channel that could have reached the director was closed by a
mechanism whose premise — *a filed defect is not a forgotten one* — is currently false.

**Repair.** The alarm moved to the leaf, `tools/stretch_log.raise_stretch_report_owed`.
`background/supervisor._self_refill_draw_ladder` — the tick, which ran throughout the six days —
now calls it, and the publisher still calls it too. **Two independent hosts, because the point is
that neither one's outage is the alarm's outage.** `notify`'s transition key makes the second
caller free. The move went to the leaf rather than importing the publisher into the supervisor
because `supervisor.py` line ~167 forbids exactly that, and names the 33-hour outage it caused.

## Cause 2 — the canon's one unbuilt clause

Of DIRECTOR_CANON_PRODUCT_AND_MACHINERY_2026-09-05's four pieces of WORK THIS CREATES, three were
built. The fourth — *"the ratio itself becoming a finding when it goes wrong"* — became a
**sentence**. `product_machinery_split.main()` prints `BELOW FLOOR` on every window and
`return 0`. Its one live consumer, `supervisor._product_share_phrase()`, composes a clause into a
`log()` line, which right now reads *109 commits since any product-priority atom was named, against
a median of 6; product share 7%, floor 25%* — into a channel with no reader.

The comment that chose logging said why, and was right about documents: *"a rung that mints a
document every thirty minutes is the treadmill this is meant to end."* But it chose between FILE
EVERY TICK and LOG, and never considered **PAGE ONCE ON THE CROSSING** — which `transition_key` has
done for every other alarm here for weeks.

**Repair.** `supervisor._page_product_floor_crossing()`, called each tick. Keyed
`product-machinery:floor`, state is the *verdict* not the number (so 6%–8% is one condition, one
page), `re_escalate_after=24h` while it stands. It pages on recovery too: a control that only ever
speaks bad news teaches its reader that silence is good news.

## Controls

`tests/background/test_an_alarm_hosted_in_the_subsystem_it_reports_on_is_silent_when_it_is_right.py`
— 10 legs. Mutation-proven: removing the tick's floor call reds
`test_the_tick_asks_the_floor_every_cycle`; collapsing the floor's two states to one reds
`test_the_floor_pages_on_both_crossings[0.4-ok]`. Both branches of each partition are asserted
reachable, not only that the quiet branch is correct.

## What is NOT repaired, and it is the bigger half

**Ninety machinery findings in the queue is a rate problem, not a draw problem.** The machine files
them faster than any draw clears them and every one is real. The selector was already fixed — the
product-starvation override lets a product atom jump the blocking-finding exclusion — but an
override that lets product win *when product is on the map* does nothing when the map's top ninety
items are the machine's own defects. **Product work cannot win a draw it is not in.**

I have no mechanism for that and deliberately did not invent one in the same hour I diagnosed it.
Naming it is the deliverable; a rule about how machinery findings get filed would be machinery about
machinery, which is the defect performing itself.

## Class registration

Belongs to `controls_that_cannot_fail`.

The auto-classifier routed this to `publish_gate_and_wedge` on the wedge words in the evidence, and
that reads the SETTING rather than the defect. The publisher's six-day wedge is the circumstance
that exposed both halves of this document; neither half is about the wedge. Both are controls that
ran, were correct, and could not fail — one because its host was down whenever it was right, the
other because its only output was a sentence in an unread log. That is this class exactly, in the
"blind to its own subject" shape rather than the fail-open one.
