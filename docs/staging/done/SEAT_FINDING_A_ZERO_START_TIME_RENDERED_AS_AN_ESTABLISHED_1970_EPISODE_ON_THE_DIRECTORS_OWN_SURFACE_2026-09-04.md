**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# A zero start time rendered as an established 1970 episode, on the director's own surface

Filed 2026-09-04 by the delivery seat. **Fixed and landed in the same commit as this finding**, at
two levels. Written up because the shape is general and the provenance took research.

## The defect

`process_run_complete._episode_phrase` guarded its episode start with

    if not isinstance(wedge_since, (int, float)):

which refuses `None` correctly and **accepts 0, because 0 is an int**. What the director read, in
`site/data/director_reserved.json` — the queue reserved for the four classes nothing here may
decide:

> EPISODE: wedged since **1970-01-01T00:00 UTC** — **0h00m** and 3 consecutive failures in THIS
> episode (not a fresh hour). Markers pending: 0.

The `None` branch beside it says *"start time unrecorded (this alarm cannot bound the episode)"*,
and a reader can act on that. `1970-01-01T00:00 UTC — 0h00m` cannot be told apart from a real
reading. **The failure is not the missing figure; it is that a value nobody recorded was rendered
with the same confidence as one that was.**

## Where the zero came from — researched, because the two answers have opposite remedies

The direction that raised this said plainly: *a fixture, or a real write path that stamps 0 when it
has no clock — a question to research, never a value to pick.* It is **fixture-origin, and no
production path can produce it**:

* `record_publish_gate_failure(now=None)` resolves `now = time.time()`, and stamps
  `wedge_since = prev if isinstance(prev, (int, float)) else now`. A live publisher therefore
  stamps a 2026 clock or adopts an already-persisted one. It has no branch that yields 0.
* `"wedge_since": 0.0` appears **verbatim in publish-gate test fixtures**, beside
  `git_hash="abc1234"` — and `git=abc1234` is exactly what the observed alarm carried. Sibling
  fixtures drive the real writer with `now=100` and similar, and the writer faithfully stamps the
  clock it is handed, so a fake clock becomes a 1970 episode start.
* `0h00m` corroborates it. Age is `now - wedge_since`; an epoch start against a real clock reads as
  ~500,000h. **Both fields at zero means the clock was a fixture's too.**

The route to the page was the mirror hole fixed in 33b54b3ee: the publish-gate fixtures monkeypatch
`action_needed.REGISTER_PATH`, which was one of the two values the mirror guard compared.

## What was done

1. **The renderer** degrades any non-positive start to the same string `None` gets — the two are
   the same fact, and the reader must not be able to tell them apart.
   `tests/background/test_a_zero_start_time_is_not_a_start_time.py`, seven legs including a
   reachability null control and one end-to-end leg through the real writer. Mutation: reverting
   the guard fails six of seven; the survivor is the null control, which is an **equivalence by
   design**, not a missing test.
2. **The sink.** `site/data/director_reserved.json` joins `PROTECTED_FILES` in
   `tests/production_surface_guard.py`. `site/data/` stays file-scoped, and the 2026-08-10 blast
   radius that keeps it file-scoped was **re-measured rather than quoted**: this path has exactly
   one writer, `action_needed._mirror_reserved_to_site`. `tools/generate_director_data.py` names
   the file in `FEED_FILES` but `load_feeds` only reads it, and its single `out_path.write_text`
   writes `DELTA_NAME`. The generator argument does not reach this path.

   **Blast radius, pre-registered and then run: `768 passed, 0 failed`** across all 25 test modules
   referencing `action_needed` / `director_reserved` / `SITE_RESERVED` — an exhaustive population,
   not a sample, because the path has one writer and that writer lives in `action_needed`.

Three levels now: the caller (33b54b3ee), the renderer, and the sink.

**The sink question was already on the map, and this closes it rather than re-opening it.**
`SEAT_FINDING_TWO_GREEN_TEST_SUITES_WRITE_LIVE_PUBLISHED_SITE_FEEDS_IN_WHATEVER_TREE_THEY_RUN_IN_2026-09-04.md`
(same day, same seat, self-corrected to RECORDED) left it open in as many words: *"That may put it
on the public-claim side of the same line the existing rule already draws… If a lane picks it up,
the subject is one line in `_PROTECTED_WRITE_PATHS`, not a new guard."* It is one line, and the
blast radius it asked for was measured before adding it. That document also reproduced
`test_publish_gate_alert.py` writing the live feed in a clean extract — **before** 33b54b3ee closed
the mirror; the whole-population run below is what establishes it no longer does.

## What is NOT fixed, named rather than left for the reader

`record_publish_gate_failure` carries **the same `isinstance`-accepts-0 shape** when it adopts a
persisted `wedge_since`, so a zero that reaches the state file is kept rather than restamped to
`now`. Fixing it is not free: `tests/background/test_publish_gate_blocking_payload.py` pins
`persisted["wedge_since"] == 0.0` as a deliberate "the episode fields are not disturbed" control,
so changing the adoption semantics reds a live control that another lane wrote.

**The recommendation is to change the fixture, not the semantics** — `0.0` was never a legitimate
persisted value, and a control whose fixture states an impossible value teaches the next reader
that it is possible. Not done here because it is another lane's control and the renderer already
closes the surface. Left as the next piece.
