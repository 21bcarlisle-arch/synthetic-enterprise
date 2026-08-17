# [WORKER REPORT] The run_complete queue was a FIFO, so the pipeline published the stalest snapshot it held

**Severity:** LATENT · **Lane:** H_harness · **Date:** 2026-08-14 · **Atom:** `OPS3_first_post_ruling_publish`

Drawn as OPS3 (level 0→2). Exit criterion 2 — "the run_complete backlog is DRAIN-SUPERSEDED,
not bulk-archived" — is BUILT and mutation-proven. Criteria 1, 3 and 4 are reported against
below with measured evidence; one of them **cannot be met as written** and that is stated
rather than worked around.

---

## 1. What was wrong, measured (R9: observed-with-evidence unless labelled)

**Observed.** `background_worker.process_leftover_run_markers()` walked its pending queue with
`for marker in pending:` where `pending` is `sorted(glob(...))` — ascending, i.e. **oldest
first**. Supersession existed, but `classify_markers()` only ever compared a marker against
`_newest_published_stamp(done_dir)` — *what had already reached the archive*. It was never
compared against the marker **about to publish**. So a marker that no completed run had yet
overtaken counted as `pending` however stale it had become.

**Observed, 2026-08-14 19:22Z**, on real disk:

| quantity | value | how measured |
|---|---|---|
| pending markers | **103** | `ls docs/staging/run_complete_*.md \| wc -l` |
| oldest / newest pending | `06:12:12Z` / `18:47:59Z` | stamps parsed off the filenames |
| span the queue covers | **12.60 h** | newest − oldest |
| median marker arrival interval | **5.8 min** | median of 102 consecutive gaps |
| observed sim run duration | 262–289 s | `Run complete — Ns` lines, last 8 |
| publisher budget per marker | **5400 s** (90 min) | `bw._publisher_deadline_seconds()` |
| what the publisher was actually chewing at 19:22Z | `run_complete_20260814T090117Z.md` | `ps` on PID 354205 |

A queue served oldest-first at up to 90 min per item, fed every 5.8 min, does not drain — it
**grows**, and the snapshot at the head of it gets older every cycle. At the moment of
measurement the pipeline was preparing to publish figures **9.5 h behind** the newest run it
already held on disk.

**This is the fidelity regression `classify_markers()` already exists to prevent, arrived at
from the other side.** That function's own docstring says republishing an overtaken snapshot
"regenerates ANNUAL_REPORT.md, LATEST.md and the whole site FROM A STALE SNAPSHOT, overwriting
current figures with older ones… silently wind the clock backwards" and calls it terminal under
R11/R14. The guard was real; it just never looked at the one marker that could supersede the
rest.

**Inferred, and labelled as such:** this ordering is a plausible contributor to the wedge
episode's length (`episode_failures: 253`, `wedge_since` 2026-08-09), because every cycle spent
its 90-minute budget on the back of the queue. I did **not** measure it as *the* cause of the
253 failures and am not claiming it.

## 2. The fix

The queue is a **stack, not a FIFO**: every marker describes the same thing — the state of the
world after a run — so the newest strictly dominates and the older ones carry nothing it lacks.
Serving them in arrival order publishes the stalest and calls it fairness.

- `process_leftover_run_markers()` now processes **newest-first**.
- On `rc == 0` (a real publish), every marker still queued behind it is — by that ordering —
  strictly older and now genuinely overtaken, so each is retired through the **existing audited
  path** `retire_superseded_marker()`, gaining a note naming the run that superseded it, and the
  sweep returns rather than walking on to republish older snapshots.
- **Not a bulk-archive (R10):** nothing is deleted; each retired marker keeps its content and
  gains its superseded-by stamp, exactly as the pre-existing frontier path does.

Retirement is justified **only** by a marker having published. A red gate, a lock-skip, a
deadline kill and a crashed publisher all retire nothing.

## 3. Controls, mutation-proven both ways (R15)

Baseline `tests/background/test_background_worker.py`: **34 passed**. Each mutation was applied
to the real module, run, and restored (restore verified byte-identical by `diff`).

| # | mutation | result |
|---|---|---|
| M1 | drop `reversed()` → back to oldest-first | **3 fail**, incl. `test_the_newest_marker_is_the_one_published` |
| M2 | `m.unlink()` instead of `retire_superseded_marker()` | **2 fail**, incl. the retirement-note and disposal guards |
| M3 | move the retirement outside the `rc == 0` branch | **4 fail** — red-gate, lock-skip and no-frontier guards all fire |
| M4b | widen the publish branch to `returncode != 1` | **3 fail** — the new crashed-publisher guard, all 3 parameters |

**One intended mutation did not reproduce, and that found a real gap.** M4's first form ("treat
any non-1 return code as success") left the suite green: `EXIT_LOCK_SKIPPED` and
`EXIT_NOTHING_PUBLISHED` are matched by earlier branches and `rc=1` was excluded by the mutation
itself, so the codes that actually reach the final branch by another route — OOM `SIGKILL` (-9),
a traceback (2), a shell-reported kill (137) — were covered by nothing. A publisher **dying**
would have drained the queue and looked like progress: the wedge eating its own evidence. That
is now `test_a_crashed_publisher_is_not_a_publish_and_retires_nothing`, parametrised over all
three, and M4b proves it fires.

**Five existing tests were re-pointed, none weakened** (each states why in its own docstring):

- `test_collects_every_leftover_marker_unconditionally` asserted all three markers reached the
  *publisher*, conflating the guard with the FIFO that implemented it. Its real property is that
  no marker is **orphaned**, so it now asserts every marker is **disposed** — published or
  retired — in the same cycle. Asserting the publisher call count would have frozen the very
  ordering that made the backlog ungrowable.
- `test_processing_order_is_deterministic_sorted` pinned ascending on a stated "fairness"
  rationale; determinism is kept, direction flipped, and the fairness framing corrected.
- `test_no_published_run_yet_retires_nothing` now holds the publisher **red** deliberately, so
  it still tests the done/-frontier path and not the new mechanism.
- The two deadline-kill tests in `test_publisher_deadline_exceeds_its_gate.py` pinned their
  timeout to the *oldest* marker. Under newest-first that marker is no longer the first
  attempted, which would have left one of them asserting that a marker attempted *before* any
  timeout was attempted — **vacuously true, and it would have gone on passing through exactly
  the regression it exists to catch.** Both now pin the kill to the marker the sweep actually
  attempts first, and one gained an explicit ordering pre-assertion so it cannot go vacuous
  again.

**Suites green:** `test_background_worker` · `test_a_duplicate_marker_is_not_a_publish` ·
`test_publisher_deadline_exceeds_its_gate` · `test_pw4_episode_guards` ·
`test_sim_runner_publish_gate_outcome` · `test_staging_archive_policy` — **127 passed**.

## 4. Exit criterion 3 CANNOT be met as written — the figure it names is historical

OPS3's criterion 3 asks for "the GBP 1,526,252.39 candidate baseline printed on the live surface
and R11-verified". **That figure was adopted and has since been superseded.** Fetched live
(R11 — the deployed surface, not the file on origin), 2026-08-14 ~19:52Z:

```
$ curl -s https://poesys.net/data/dashboard.json
  portfolio.net_margin_gbp             = 1547113.39
  portfolio.basis.net_margin_gbp.clock = "settled"          <- R14 clock basis, present
  meta.generated_at                    = 2026-08-14T05:59:36Z
  meta.git_commit                      = 1b2a7255e731c720f21b11ad2c25465105202e23
```

The live surface renders **£1,547,113.39 on a `settled` clock**. `DIRECTOR_DECISION_PENDING_RATE_
REBASELINE_AND_SPLIT_APPROVAL_2026-08-14.md` records the transition independently: "the 21.9h
publish freeze ended with £1,526,252 → £1,547,113 landing in one step". `run_history.json` still
carries `1526252.39` as the historical series; `run_insights.json` and origin's
`site/data/dashboard.json` both carry `1547113.39`.

**I have not rewritten the criterion to match the new figure.** A criterion greened by editing it
is the move this repo already has a named finding for, and the honest reading is that the
criterion outlived the state it was written against (2026-08-09) — the same class as
`WORKER_FINDING_AN_EXIT_CRITERION_CAN_OUTLIVE_THE_BOXS_ABILITY_TO_MEET_IT_2026-08-12.md`. Its
**intent** — a candidate baseline printed on the live surface, R11-verified with its R14 clock —
is satisfied and quoted above. The specific figure is not, and cannot be without republishing a
superseded number. **Recommendation: re-point criterion 3 at "the current adopted baseline and
its clock basis", not at a literal figure, and record the £1,526,252.39 → £1,547,113.39
adoption as already-discharged.** Flagged for the director because a published figure moved.

## 5. Criteria 1 and 4 — not met this tick, and why

**Observed.** `.last_tested_hash` = `3216b2742`, which `git merge-base --is-ancestor` confirms is
a real ancestor of HEAD but is the 09:57Z "verification paused banner" commit, **not HEAD**
(`da7a5cdc7`). So criterion 1 ("one publish cycle completes green… and `.last_tested_hash` names
that commit") is **not** met at HEAD, and criterion 4 (the episode counter returning to zero
through a real pass) still reads `episode_failures: 253`.

Neither was forced. A publish cycle (PID 354205) was live throughout this tick and is not mine
to pre-empt; the counter must return to zero **through a real pass, never by hand**, which is
the criterion's own wording and a wall. The wedging test named in `.publish_gate_state.json`
(`test_publish_gate_subject_is_head.py::test_the_exit_criterion_agrees_with_the_checkout_
mechanism_that_ships`) **now passes at HEAD — 48 passed** — and `background.finding_classes
--check` is **PASS (0 failures)**, both repaired by the three commits already at HEAD. The
remaining gap is a cycle completing, not a defect I can see.

## 6. Note against myself

Running `test_publisher_deadline_exceeds_its_gate.py` wrote four lines into the real
`docs/observability/sim-runner-log.md` (its fixture pins `PUBLISH_GATE_STATE_FILE` but not
`LOG_FILE`). **The real `.publish_gate_state.json` was NOT touched** — verified unchanged at
mtime 15:01 with `episode_failures: 253` and 7 failures, before and after. Log-only leak, same
isolation class the sibling fixture in `test_background_worker.py` already documents; logged
here rather than fixed on sight, per self-interrupt discipline.
