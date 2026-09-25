**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Discharged:** `tests/background/test_publish_gate_wedge_draw.py::test_a_dark_publisher_still_draws_when_its_failures_have_aged_out`, `tests/background/test_publish_gate_wedge_draw.py::test_a_spent_wedge_stops_drawing_once_a_clean_PUBLISH_is_on_record`, `background/supervisor.py` — the episode limb fires on the live 81-hour shape, and its mutation twin proves the PASS and not recency is what quiets it.

# A screen that asked "did it fail RECENTLY" for "is it WEDGED" got LESS satisfiable as the outage got worse, and held RUNG 1 silent for 81 hours

## The defect, in one sentence

`supervisor._publish_gate_wedge_active` — RUNG 1, priority zero, and the only detector pointed at a
dark publisher — decided "sustained" from `len(failures inside the last hour) >= 3`. A publisher deep
enough in a wedge STOPS ATTEMPTING, and one that is not attempting records no failures, so the
in-window count falls as the outage deepens. The screen was least satisfiable exactly when the
condition it screens for was worst.

## The evidence, read not inferred

`docs/observability/.publish_gate_state.json` at 2026-09-25 06:40 UTC:

| field | value |
|---|---|
| `episode_failures` | 58 |
| `wedge_since` | 80.7 hours old |
| `episode_clean_publishes` | 0 |
| `last_clean_publish` | 2.4 h **before** `wedge_since` — the publish the episode interrupted |
| `failures` (on disk) | 2 entries, **1** inside the hour |

`1 < 3`, so `None`, every tick, for 81 hours — against a record that says on its face that the gate
has failed 58 consecutive times and passed not once since.

## Why this is worse than an ordinary wedge

The detector that would have DRAWN the unwedge work is the thing that was broken. An alarm reading
healthy for 81 hours about the one outage it exists for is not a missing alarm; it is a false
negative that also suppresses the draw, so nothing downstream could notice either.

## The R15 band, which is wider than the instance

**A screen whose satisfiability is ANTI-CORRELATED with the severity of its subject.** Not a
tautology, not fail-open, not fail-silent — the three this project catalogues. It is green for a
reason that is *caused by* the condition worsening. Sibling shapes to look for:

* any count over a WINDOW used as evidence of a STANDING state (a window bounds how much evidence
  can exist, so the count answers a question about the instrument);
* any "still happening" test keyed to activity, where the failure mode is that activity STOPS.

## The correction, written beside the claim it corrects

The trim-on-read added 2026-09-24 said it stopped a frozen record "drawing priority-zero unwedge work
forever for a wedge that is over". The middle term is false: a publisher that has stopped attempting
has not ended its wedge — it IS the wedge, at its worst. That trim SHARPENED the defect and did not
cause it: the WRITER trims the same list on every write, so the count was window-bounded from the
start and the shape predates the trim by months.

## What was done

Landed: a second limb, `supervisor._standing_publish_episode`, keyed to the question the record can
answer and the one this function already rests on — **has the gate PASSED since this episode began?**
It reads the un-trimmed episode fields (`wedge_since` as the episode start and the only un-trimmed
clock; `episode_failures` defaulted to the recorded list's length exactly as the writer's own
`_read_publish_gate_state` defaults it; `episode_clean_publishes` and `last_clean_publish` as the pass
evidence, the latter read only AGAINST the episode start because 2026-09-16 made it deliberately not
episode-scoped). A pass must be POSITIVELY established to quiet the highest rung there is, so an
absent or unreadable pass field reads as NO PASS. The window limb is untouched.

`_wedge_sustained_clause` names which limb established the wedge. Both obvious strings were false:
"58 failures in-window" lies about the window, "1 failure in-window" reads as a flake to the worker
acting on it at priority zero.

The control that encoded the false premise
(`test_a_spent_wedge_stops_drawing_once_its_failures_age_out_of_the_window`) is **re-keyed, not
deleted**: its concern — a record nobody is writing must not draw forever — is real, and is now keyed
to the property that settles it (the PASS) rather than the symptom that correlates with it. Its
mutation twin asserts the same record with no pass on file must FIRE, so a drift back to recency
cannot go green.

## What is NOT claimed

The publisher had not yet recorded a clean publish when this was filed. Three run_complete markers
were pending. Whether the first gate cycle whose throwaway checkout postdates this landing publishes
clean is the open half, and
`WORKER_FINDING_THE_GATE_CYCLE_IN_FLIGHT_AT_A_LANDING_GRADES_A_CHECKOUT_OLDER_THAN_IT_2026-09-25.md`
is the reason the NEXT cycle is not evidence about this one.

## Two shared-tree reds seen in passing, neither mine, both green at HEAD

* `tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census` —
  I001 reads 1304 against a frozen 1305. Another lane's uncommitted in-place I001 fix; the baseline
  file itself is identical to HEAD. Already filed as
  `WORKER_FINDING_THE_RUFF_CENSUS_REDS_IN_THE_SHARED_WORKTREE_AND_IS_CLEAN_AT_HEAD_2026-09-24.md`.
* `tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` —
  undispositioned hit `toolchain_freshness.json`, which is UNTRACKED and in no commit. The census
  reads the filesystem, so it reds the shared tree and cannot red a HEAD checkout. Not filed
  separately: it is one disposition row away from green and belongs to whoever is writing
  `background/toolchain_freshness.py`.
