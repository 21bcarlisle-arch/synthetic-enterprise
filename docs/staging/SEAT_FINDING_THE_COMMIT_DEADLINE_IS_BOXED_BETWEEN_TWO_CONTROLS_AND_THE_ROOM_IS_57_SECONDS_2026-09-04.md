**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

> **RAISED LATENT -> BLOCKING, 2026-09-04 ~12:50 BST. The prediction below fired, in about five
> hours rather than the week it estimated, and it is now refusing every commit in the tree.**
> See "THE PREDICTION FIRED" at the foot of this document — the measurement is recorded beside the
> forecast rather than replacing it.

# The commit deadline is boxed between two controls and the room left is 57 seconds

**Found:** 2026-09-04, delivery seat, while unwedging a four-hour publish outage with fourteen
queued runs. Measured from `docs/observability/publish_gate_duration.jsonl`, not inferred.

---

## What happened

`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today` went red and refused
every publish commit. It is a correct control and it was right:

```
worst recent comparable gate : 674.4s   (max of the last 20 recorded runs)
floor (1.25x headroom)       : 843.0s
GIT_COMMIT_HOOK_TIMEOUT      : 840s     -> 1.246x, RED by three seconds
```

Nothing timed out. Recent gates cost 577–674s against an 840s deadline, so no commit was ever
killed. The publish path was stopped by the *control* warning that the margin had thinned, which is
the control behaving exactly as designed — and the cost of it being right was four hours of
publishing and fourteen queued runs, because a red anywhere in the blocking scope refuses the
publisher's own commit.

**This is the second wedge in the same outage, not the first.** The `.publish_gate_state.json` the
doorbell cites records `non_test_gate_refusal` — the finding-class consolidation, seven
`SEAT_PREREGISTRATION_*` files in two rooms at 08:16 UTC. That one is discharged: another lane moved
them to `records/` and `finding_classes --check` now passes 0 failures. The state artefact still
names it, so anyone reading the doorbell diagnoses a cleared defect. `blocking_tests: []` with
`total_red: 0` described the *first* wedge and never the second.

## The box

Both walls are measured, and they are closing on each other.

| | value | set by |
|---|---|---|
| FLOOR | 843s | `COMMIT_DEADLINE_HEADROOM * MEASURED_GATE_SECONDS_2026_09_04`, rises with the suite |
| CEILING | 900s | `PUBLISH_PATH_ALLOWANCE_SECONDS`, may not grow |

The ceiling is not a preference. `test_the_deadline_leaves_room_for_the_publish_path_after_the_gate`
requires `slack >= GIT_COMMIT_HOOK_TIMEOUT_SECONDS`, where slack is the allowance; and the director
ruled on 2026-08-21 that no gate budget grows here — *"A 75-minute gate is absurd on its face and
neither of us said so."* `GATE_SUITE_TIMEOUT_SECONDS` stays 3800, `PUBLISH_PATH_TIMEOUT_SECONDS`
stays 4700.

The floor is rising measurably: the same series read **557s on 2026-08-25** and **674s on
2026-09-04** — 21% in ten days. At that rate the floor reaches the 880s set today in about a week,
and reaches the 900s ceiling in about two.

## What was done

Re-measured and raised, which is a stopgap and is labelled as one in the code:

* `MEASURED_GATE_SECONDS_2026_08_25 = 557` → `MEASURED_GATE_SECONDS_2026_09_04 = 674`. Taken from
  the live series while the staleness assert (`worst <= 1.6 * MEASURED`) was **still green** at
  1.21x — re-measured because it was due, not because it tripped.
* `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` 840 → **880**, leaving the 20s the post-gate push actually
  costs. 880 is the ceiling minus the push, not a round number.

The mutation fires, so the control still has teeth:

```
deadline 600: 0.890x -> RED     deadline 880: 1.305x -> PASS
deadline 840: 1.246x -> RED     deadline 900: 1.335x -> PASS
```

## What is NOT done, and why this is filed rather than closed

**There is no third raise.** When this reds again, raising the deadline is unavailable (ceiling) and
growing the allowance is unavailable (ruling). The repair is the one the 2026-08-25 note in
`process_run_complete.py` already named and deferred:

> the publisher pays for TWO full suite runs per cycle: its own scoped gate, and then a comparable
> chain again inside `git commit`. Halving that is the fix with headroom in it; raising a deadline
> only buys time against a curve that is still rising.

That was written nine days ago, predicted this, and was right. It touches the commit gate, which is
a wall, so it needs its own design and its own controls — it is not a bounded-tick change.

## The class

This is `publish_gate_and_wedge`, and it is a specific shape within it worth naming: **a control
keyed to a rising measurement eventually refuses the work it protects, and the refusal is
indistinguishable from the failure it was built to prevent.** The deadline control exists to stop
suite growth wedging publishing. Suite growth wedged publishing *through* the control instead of
past it. Nothing here is wrong except the room.

The honest reading is that the deadline was never the mechanism with headroom in it — the second
suite run is — and every cycle spent raising the number is a cycle not spent removing the run.

---

## THE PREDICTION FIRED — 2026-09-04 ~12:47 BST

Recorded beside the forecast, not in place of it. The forecast said *"at that rate the floor reaches
the 880s set today in about a week"*. **It took about five hours.**

| | at filing (~08:00) | now (12:47 BST) |
|---|---|---|
| worst of last 20 | 674.4s | **714.6s** |
| floor (1.25x) | 843.0s | **893.3s** |
| `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` | 880 | 880 |
| verdict | PASS (1.305x) | **RED (1.231x)** |

The 714.6s row is `outcome: pass`, git `3d369242c`, written at 12:47:09 BST — the publish cycle that
successfully published `run_complete_20260904T104410Z.md`. **The gate did not fail; it succeeded,
slowly, and its own success is what broke the control.** Nothing timed out here either.

The set was printed rather than trusted to the `max` —
410/577/585/588/590/607/609/611/614/631/640/647/654/674/**714**, median 607.5. The rise is in the
body of the distribution, not one outlier.

### CORRECTION, same document, beside the claim it replaces

I first wrote here: *"Not contamination: this seat's own test runs began at ~12:45 and the series row
precedes them."* **That is wrong, and it is wrong in the direction that flattered the finding.** The
row was WRITTEN at 12:47:09 BST after a 714.6s gate, so that gate was RUNNING from roughly 12:35 to
12:47. This seat's own pytest batch ran 12:45–12:47 — 284 tests, ~73s — and therefore **overlapped
the last ~2 minutes of the measured gate.** There is a real contamination window and I asserted
there was none.

So the honest reading of the 714.6s point is **"I cannot yet say"**: more than one thing changed
(the suite grew AND this box was loaded by a concurrent test run), so it cannot be attributed. The
one-variable version is the next gate cycle that runs with no seat activity on the box, and it has
not happened yet.

**What this correction does NOT rescue.** The trend is independent of me: 557s on 2026-08-25 →
674.4s at 08:00 today, both measured with no seat load, and 674.4 alone puts the floor at 843.0s
against a deadline that has 880s. The box is real and closing whether or not 714.6 is admissible.
What changes is only that **the deadline must not be re-set against 714.6**, because that number
would bake this turn's own load into a domain constant — the "key a control to today's answer"
failure, arriving through a measurement instead of a guess.

### The third raise is unavailable IN SUBSTANCE, not just on the number

Arithmetically it looks available — 893.3 < the 900s ceiling — and that is the trap:

    raise to the floor (893.3)  ->  900 - 893.3 = 6.75s left for the post-gate push
    the post-gate push actually costs ~20s (which is why 880 was chosen: 900 - 20)

So a raise to ~895 would turn **both** asserts green while guaranteeing the push dies inside the
deadline. That is a control keyed to today's answer — green because the number moved, not because
the property holds — and it is the exact shape `CLAUDE.md` names: *"a short-term fix that answers
today's request, with a number picked because a number was needed, that comes undone when it meets
the rest of the system."* **Declined deliberately. Not taken in this tick and not to be taken in
the next one without the design.**

### Consequence, stated plainly

This red is in the blocking scope of any change to `background/process_run_complete.py`, so it
refuses the publisher's own commits. **The publish path is now wedged by this control** — which is
the second time today that publishing stopped for a reason that was not a broken publisher. The
first was diagnosed in
`SEAT_FINDING_A_CLEAN_PUBLISH_INSIDE_AN_OPEN_EPISODE_LEFT_NO_TRACE_SO_A_BACKLOG_READ_AS_AN_OUTAGE_2026-09-04.md`.

The repair is unchanged and is the one this document already named: **remove the second full suite
run per publish cycle.** It touches the commit gate, which is a wall, so it needs its own design and
its own controls. It is not a bounded-tick change and this tick did not attempt it.

---

## THE ONE-VARIABLE VERSION HAPPENED — 2026-09-04 14:50 UTC, autonomous worker

This document asked for exactly one thing it could not have:

> The one-variable version is the next gate cycle that runs with no seat activity on the box, and
> it has not happened yet.

**Four of them have now run.** Recorded in the same series, after the contaminated 714.57 row and
with no seat pytest batch on the box:

| ts (UTC) | git | duration | outcome |
|---|---|---|---|
| 13:05:15 | `239c40605` | 664.3s | pass |
| 13:21:28 | `e340cefd8` | 649.6s | pass |
| 13:51:31 | `5952aaa4e` | 672.4s | pass |
| 14:27:03 | `b0ba91858` | 651.1s | pass |

Worst 672.4s, mean 659.3s. **None approaches 714.6.**

### What this settles, and what it does not

**Settled: the control is red on a measurement, not on the property it protects.**

```
floor on ALL admissible data   : 1.25 x 672.4 = 840.5s   vs deadline 880s -> HOLDS, ~40s spare
floor on the last-20 EXCLUDING
  the contaminated point       : 1.25 x 674.4 = 843.0s   vs deadline 880s -> HOLDS
floor as the control computes it: 1.25 x 714.6 = 893.2s  vs deadline 880s -> RED by 13.2s
```

Every reading that excludes the one row the previous section already ruled inadmissible passes
with room. The publish path is therefore being refused by a single observation that this document
itself established must not be used to set a constant — and grading the control against it is the
same error as setting the deadline from it.

**NOT settled: the drift is real and the box is still closing.** Successive five-run windows:

```
2026-09-03 22:01  mean 574.9  max 640.5
2026-09-04 04:19  mean 600.6  max 631.7
2026-09-04 07:50  mean 599.3  max 674.4
2026-09-04 11:47  mean 670.4  max 714.6
```

The body moved ~575s -> ~660s in sixteen hours. The forecast in this document is not refuted by the
above; only the claim that the floor has *already crossed* the deadline is. **The named repair
stands unchanged and is still the only one with headroom in it.**

### The wedge is self-clearing, and the cost of waiting is measured

The contaminated row sits 5th from the end of the series. `rows[-20:]` drops it after **15 more
recorded cycles**. Refused cycles DO append (the 13:51 and 14:27 rows are both refused publishes),
so the window advances without publishing — but at the observed ~35 min cadence that is **roughly 9
to 15 hours of refused publishing**, every cycle of it regenerating surfaces that never land.

That is the real cost of doing nothing, stated so it can be weighed rather than discovered.

### What this tick did NOT do, deliberately

**No constant, control or data row was changed.** Three separate stopgaps were available and each
was declined:

1. **Raise the deadline** — declined for the reason this document already gives: ~895 leaves 6.75s
   for a push that costs ~20s. Green control, guaranteed dead push.
2. **Widen or re-key the control** (max -> a quantile, or a longer window) — that is weakening a
   control in the same tick it refuses me, which is this project's most expensive recurring shape.
3. **Delete or flag the contaminated row** — defensible on the evidence, and still declined: there
   is no mechanism to mark an observation inadmissible with its reason, and inventing a hand-lever
   that silences inconvenient measurements, on the tick where it unblocks the person building it,
   is how that lever gets used next time.

**The recommendation, which is the director's to weigh because his 2026-08-21 ruling sets the
ceiling:** authorise the named repair — remove the second full suite run per publish cycle — as the
next design item. It is the only move that is not keyed to today's answer. If publishing is wanted
back before that lands, the honest stopgap is to mark the 11:47:09 row inadmissible **with its
reason recorded in the series**, never to raise the deadline.

Filed rather than acted on, because every action available inside a bounded tick turns a red
control green in the same tick that it blocks the actor.
