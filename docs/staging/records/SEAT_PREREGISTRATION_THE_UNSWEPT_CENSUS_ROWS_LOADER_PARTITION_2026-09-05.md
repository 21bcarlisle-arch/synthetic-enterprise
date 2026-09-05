# PRE-REGISTRATION — what the 34 unswept census rows do on an unreadable prior

**Date:** 2026-09-05
**Class:** R15 fail-silent · R10 (an absurdity is fixed as a class, not an instance)
**Severity:** RECORDED · **Lane:** H_harness — the six repairs land in the same commit as this
note, and the census `--check` exits 0 with all 46 rows dispositioned. The one item left open
(`.sanity_daemon_last_digest_date`'s unguarded read) is named at the end and is not this class.

A defect class already proven live twice (`.sent_ntfy_ids.json`,
`.notify_transitions.json`, both swept 2026-09-04 under a `benign` verdict that had answered a
different question). Written 2026-09-05 BEFORE the measurement, by the delivery seat, under claim
`ask-the-remaining-32-benign-census-rows-the-loader-question-2026-09-04`.

## The subject

`docs/design/self_clearing_alarm_dispositions.json` carries 46 rows; 12 now have a `loader` field
and **34 do not** (8 `real`, 26 `benign`). The lane text names four carriers as the ranked head —
`.dispatcher_seen.json`, `.staging_watcher_seen.json`, `.last_processed_fingerprint.json`,
`.ntfy_responder_seen_hashes.json` — and **all four already carry a `loader` field**, landed by
another lane (`38f94a7e8`, the seen-hashes sweep) between the draw being written and this turn.
The ranked head is therefore re-derived here from the writers the census itself reports, not taken
from the draw.

The second half of the lane text — "settle the open judgement in `background/ntfy_utils.
was_sent_by_us`" — **is already settled and wired**, not open. `was_sent_by_us` still answers
plainly; `ntfy_responder.check_once` asks `sent_ids_unreadable()` FIRST (line 732) and quarantines
without staging or replying, with `notify` on a per-key cooldown. Controls:
`tests/background/test_the_responder_refuses_to_guess_whose_a_message_is.py`. **There is nothing to
put to the director**; re-asking would be asking him to re-decide something a lane already decided
correctly. Recorded here so the next reader does not re-open it.

## Ranking rule (from the dispositions file's own `_scope_of_benign`)

A **read-modify-write** carrier can DESTROY the record on a corrupt read: the loader fails open to
empty, the writer writes that empty back, and the prior is gone. A **pure reader** only loses a
suppression or spends a cycle. Rank by the writer, not by the loader.

## Predictions (recorded before running anything)

| # | Carrier | Predicted worst state | Predicted consequence |
|---|---|---|---|
| 1 | `run_history.json` (`generate_insights.append_run_history`) | truncated/empty | RMW writes a **1-entry history over 100 runs**; the Project tab's "Sim runs" KPI (`count_run_history_total`) falls to 1 and stays there. A **published figure destroyed by a corrupt read.** |
| 1b | same, `null` / mapping / list-of-scalars | parses | `h.get` / iteration raises inside `append_run_history`; **swallowed** by `_process`'s `except Exception` → the run is silently missing from history forever, logged only as "Run insights generation skipped". |
| 1c | `extract_run_history` / `count_run_history_total` on `null` | parses | `len(None)` → **TypeError uncaught** (only `JSONDecodeError, ValueError` are caught) → dashboard generation raises. |
| 2 | `.supervisor_map_exhausted_state.json` (`_load_map_exhausted_state`) | `null`, list | `except (JSONDecodeError, OSError)` never sees them; `state.get` at supervisor.py:6291 raises **AttributeError**. Predicted to land the same way the idle-counter row did — caught by `main`'s blanket handler, so the supervisor does not die but **the cycle never completes**, every two minutes, forever. |
| 3 | `.wedge_suspect_hit_rate.json` (`_append_suspect_outcome`) | any unreadable | no crash; loader returns `[]` and the append writes **one episode over the whole measured series** — H42's own evidence that the suspect list works, silently reset to "not yet measured". |
| 4 | `.harden_cooldown.json` (`record_harden_pass`) | any unreadable | no crash; RMW writes **one atom over every other atom's cooldown**, so recently-hardened atoms are re-offered. |
| 5 | `.ntfy_digest_state.json` (`notification_digest`) | any unreadable | `digested_through_seq` reads 0, so `pending()` returns **every entry ever queued** and `_due` fires immediately → one digest replaying the whole queue. Not destructive (the write restores the mark) but a flood. |
| 6 | the remaining ~28 | — | predicted **pure readers that fail open correctly**: a lost suppression, a re-fired reminder, a re-run step. No repair earned; a `loader` field saying so, and why, is the deliverable. |

## What would refute each

- 1: a `try` around `append_run_history` inside `generate_insights`, or a caller that repairs.
- 2: `check_map_exhausted_escalation` not on the `run_cycle` path, or a caller-level `.get` guard.
- 3/4: a writer that re-reads under a lock, or a consumer that ignores the reset.
- 6: any of them turning out to be a read-modify-write.

## Control leg (required, per the class)

Every partition run carries a **LIVE PRIOR** leg — a genuinely readable file with real content —
asserted to survive. Without it, "the prior was destroyed" is satisfiable by a harness that
destroys the prior itself, and every row would read as defective for free.

Partition measured per carrier: `missing file / empty / truncated / json-null / mapping /
list-of-scalars / bare-string`, plus a live prior.

---

# RESULT, recorded beside the predictions (same day, after the measurement)

All 46 rows now carry a `loader` field; `self_clearing_alarm_census --check` exits 0. Six carriers
were repaired, six more were already correct, and the rest were asked and are clean. Control:
`tests/background/test_the_census_rows_that_had_never_been_asked_the_loader_question.py`, 36 tests,
and **six named mutations each verified to red it** (restore any of the four old loaders, or delete
either `preserve_unreadable` call).

## Where the predictions HELD

Rows 1b, 1c, 2, 3, 4 and 5 were all confirmed exactly as written, including that
`check_map_exhausted_escalation`'s raise lands the same way `_load_idle_turn_count`'s did.

## Where they were WRONG, and it matters more than the part that was right

**Prediction 1 named the destruction and missed the FABRICATION.** I predicted `count_run_history_
total` would *crash* on `null`. It does. What I did not predict is that `"abc"` and `[1, 2, 3]`
**publish 3** — `len()` answers happily for both — so a corrupt file rendered as a plausible run
count on the director's Project tab rather than as a failure. A crash gets noticed; a plausible
smaller number does not. That is the more serious half and I had not seen it before running.

**Prediction 6 was wrong about `retired_paths_served.json`**, which I put in the "pure readers,
no repair earned" tail. `[1, 2, 3]` and `"abc"` raise AttributeError in `transitions`. The reason
I misread it is worth keeping: `null` answers *correctly, by accident* — `None or {}` is `{}` —
and one member of a partition passing for the wrong reason is what made the other two look
impossible.

**Two claims in the first draft of the disposition rows were written before they were opened**, and
both were wrong: `.run_marker_sweep_state.json` and `.operational_layer_signal.json` were recorded
as "guarded by `episode_monotonic`", which is the EPISODE question, not the loader question. Opening
them showed both already answer the loader question properly by other routes. Corrected in place in
the rows themselves. The habit that caught it is the only reason this note exists: a row citing an
artefact is a checkable claim, so open it.

**One control was a tautology and the mutation caught it, not me.** The first
`retired_paths_served.json` test called `load_episode_prior` directly and passed under the mutation
that restored the old inline read — it was asserting the helper against itself while the caller went
unexamined. `run()` cannot be called instead (it refuses without a real site checkout), so
`tools/retired_paths_still_served.py` grew a named `_load_previous_state` seam and the control's
subject became the module. Without the mutation pass this would have shipped green and empty.

## The one thing left open, named rather than quietly fixed

`.sanity_daemon_last_digest_date` is read at `sanity_daemon._maybe_send_daily_digest` with a bare
`read_text()` behind an `.exists()` check — no `except OSError`, unlike its two siblings
`.boot_announced` and `.daily_self_note_last_date`. Content corruption is harmless (a text compare
fails and the digest re-sends), so this is **not** the absent-vs-unreadable conflation this sweep is
about; it is a plain unguarded read that a permissions error or a directory would raise into the
cycle. Left unrepaired deliberately — inventing a guard for it inside this sweep would be the
guard-by-reflex the dispositions file's own `_scope_of_benign` forbids. Recorded here so it is a
visible gap rather than an assumed pass.

## Done means

The table is printed from a real harness (not reasoned), every one of the 34 rows carries a
`loader` field recording the ANSWER (repaired, or deliberately left with its reason), the repairs
that are earned are landed with a mutation-provable control, and the ones not earned say so.
