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
