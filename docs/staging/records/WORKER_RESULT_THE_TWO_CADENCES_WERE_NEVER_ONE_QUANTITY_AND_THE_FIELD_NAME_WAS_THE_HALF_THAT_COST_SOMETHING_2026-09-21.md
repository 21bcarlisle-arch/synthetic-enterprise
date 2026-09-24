**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The two cadences were never one quantity, and the FIELD name was the half that cost something

*2026-09-21, worker tick. Lane 0, claim `one-publish-cadence-two-constants-112x-apart`.*

Landed. Answers the "give the quantity one home" half in full; names what is still owed and why it
was not taken in the same turn.

---

## The one-sentence result

`publish_freshness.PUBLISH_CADENCE_SECONDS` (604,800s) and
`suite_duration_watch.PUBLISH_CADENCE_SECONDS` (5,400s) were **not two homes for one quantity** —
they were a DECISION and an OBSERVATION of different subjects wearing the same name, and the
resolution is a rename rather than a tie-break. **Nothing in `suite_duration_watch` was wrong
except its name.**

## Which reader used which — established before anything was changed

The drawn item asked for this first, and the answer is cleaner than expected: **no reader was
confused across a module boundary, because no reader ever imported the rival.**

| reader | picks up | how |
|---|---|---|
| `sim_runner._declared_cadence_seconds` | DECLARED, 604,800s | imports it |
| `supervisor._publish_cadence_seconds` | DECLARED, 604,800s | imports it |
| `publish_freshness.STALE_AFTER_SECONDS`, `snapshot()` | DECLARED, 604,800s | same module |
| `suite_duration_watch.absolute_band`, `record`, both alarm fragments | MEASURED, 5,400s | same module |
| **`settlement_ceiling_probe.publisher_context()`** | **MEASURED, 5,400s** | **reads the FIELD** |

**The one that crossed did not use the symbol at all.** It reads `cadence_seconds` out of
`docs/observability/publish_gate_duration.jsonl`, and `recommend()` spends that as the publish
interval the settlement ceiling is priced against. `publish_freshness.snapshot()` writes a field
of the *same name* carrying the *declared* cadence. So the collision that actually cost something
was **between two artefacts' field names, not between two symbols** — and a repair that renamed
only the constants would have passed every review and left the damage running.

That is the finding I did not expect and would not have got by grepping for the symbol.

## Why it was load-bearing

Run duration SETS marker inter-arrival, so a ceiling bounded by the measured interval grows
whenever the ceiling it bounds grows. That is the exact circularity `net_new_acquisition`'s own
note records as *removed*, re-entered through a second door nobody re-asked. Against 5,400s the
binding leg is **time**; against 604,800s it is **memory**. The two answers differ in kind.

## What landed

`background/suite_duration_watch.py`, `background/publish_freshness.py`,
`tests/background/test_suite_duration_watch.py`,
`tests/architecture/test_the_publish_cadence_has_one_home.py`.

* `PUBLISH_CADENCE_SECONDS` → `MEASURED_RUN_ARRIVAL_SECONDS`; `measure_publish_cadence_seconds`
  → `measure_run_arrival_seconds`.
* the stamped field `cadence_seconds` → `measured_arrival_seconds`.
* `row_arrival_seconds()` reads the legacy key for the 5,570 stored rows that predate the rename.
  **That is data, not a live second spelling** — no writer emits it any more, so the branch is
  reachable only by rows older than today and can never be reached by a row written from here
  again. Returns the value AS STORED: `float()` turns *"the 330s interval"* into *"330.0s"* in the
  line the director reads, which is a display regression I caused and caught on the first run.
* the alarm and note prose stop calling the arrival interval a cadence.
* `publish_freshness` now names the quantity it is NOT, **beside the "single source of truth"
  claim rather than over it** — that claim was false on the day it was written, and saying so is
  the evidence the fix was not retrofitted to look prescient.

**Deliberately NOT renamed:** `over_cadence` / `within_cadence` / `cadence_band`. Those strings
are stored on 5,570 historical rows; renaming them would silently change what every old row says,
which is the opposite of the repair. The band vocabulary is the module's local word for its own
comparison; the NUMBER is what a foreign reader picked up, so the number got the unmistakable name.

## The control, and its mutations

A comment cannot see a rival — that is exactly how seventeen days passed — so the "single source
of truth" claim needed something that reds when a second home appears.
`test_the_publish_cadence_has_one_home` is keyed to the property (one definition of the name
anywhere in the tree), **not to today's two modules**, so it fires for a third module nobody has
written yet. It parses rather than greps, because a text control would red on its own explanation.

Three mutations, all kill it, tree restored bytes-identical afterwards:

1. re-add `PUBLISH_CADENCE_SECONDS = 5400` to `suite_duration_watch` → reds naming the file.
2. write `cadence_seconds` from `record()` → the field leg reds.
3. drop the interval from the row entirely → the *same* leg reds, so it is not satisfied by
   absence.

A third test proves the AST can tell a MENTION from a DEFINITION on the same file, so leg 1 is not
passing for being vacuous.

## Still owed, and why it was not taken in this turn

**`tools/settlement_ceiling_probe.py` still reads `cadence_seconds` and still defaults its time
bound to it.** Two reasons it is a separate piece of work, not laziness:

1. The file carries **226 uncommitted lines** of another lane's priced-menu (A46) work right now,
   so a hunk in it needs `tools/isolate_hunks.py` rather than a pathspec.
2. The substantive half is not a rename. Whether the probe's fallback interval should become the
   *declared* cadence is a **judgement about the settlement ceiling**, and the lane holding
   `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` is fitting that curve right
   now. Taking that decision from underneath them mid-flight buys a collision, not a fix.

**Nothing breaks in the interval.** Every row on disk today carries the legacy key, so the probe
reads exactly what it read yesterday until a new gate run appends one — and when one does, the
probe's own `publisher_context` fails CLOSED (`cadence_seconds: None` → `recommend` refuses the
time bound with a named reason) rather than substituting a plausible number. That is the correct
direction to be caught in.

Also stale, both in prose only and both in dirty files another lane holds:
`tools/generate_book_growth_data.py:442` and
`site/test_the_book_is_bounded_by_compute_reaches_the_reader.py:288` still name
`suite_duration_watch.PUBLISH_CADENCE_SECONDS`, a symbol that no longer exists.

## One thing a reader should not conclude

That the ratchet red seen during this turn was mine. `tests/architecture/test_static_quality_ratchet.py`
reds on F841 123≠124 and I001 1305≠1306 — violations *removed* without the baseline being lowered.
My four files contribute **zero** of either, before and after, checked against their own HEAD
copies. It is another lane's dirty working copy having fixed a violation, and `surgical_land`
gates HEAD-plus-my-hunks, so this landing never inherited it.
