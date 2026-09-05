**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** measurements_that_mirror

# PRE-REGISTRATION — the four JSONL readers that were graded from a sibling's behaviour

**A pre-registration states no defect of its own; the severity of what it found is carried by
`SEAT_FINDING_THE_PER_LINE_CLAIM_WAS_FALSE_ON_THE_ONE_CARRIER_WHOSE_READER_ALSO_WRITES_2026-09-05.md`.**
Why the question was worth asking: a wrong `loader` disposition is a row that reads as ASKED-AND-ANSWERED and
was never opened. The census's own rule is that a row with no answer is a gap and not a pass; a row
with the WRONG answer is worse, because nothing will ask it again.

**Written 2026-09-05, BEFORE opening any of the four readers.**

## The claim under test

`docs/design/self_clearing_alarm_dispositions.json` carries, on five JSONL carriers
(`ntfy_digest_queue`, `publish_gate_duration`, `live_decisions_log`, `gate_authorizations`,
`decisions`), a `loader` field asserting the whole-file corruption partition does not apply
**because the readers parse PER LINE** — "a corrupt line costs one entry, never the file".

That was verified for exactly one reader: `notification_digest._read_queue`. The other four rows say
"same as above". The grading was by family resemblance, which is the shape that put two wrong
`episode_monotonic` citations into these same rows before anyone opened them.

## What I will measure

For each of the four unverified carriers, the **complete reader set** — every call site that opens
the path, not the one call site the census flagged — and for each reader, which of these it is:

- **T (tolerant)**: iterates lines, `try/except` per line, a bad line costs one entry.
- **W (whole-file)**: `json.loads(f.read())` or equivalent — a bad line costs the file.
- **L (line-fatal)**: iterates lines but `json.loads(line)` is unguarded — a bad line raises out of
  the reader and costs the file *and* the caller's cycle.
- **O (unguarded open)**: no `except OSError` — a permissions error or a directory at the path
  raises into the caller.

## Predictions, recorded before looking

1. **The reader set is larger than one per carrier.** `gate_authorizations.jsonl` alone is named by
   `level_promotion_gate`, `harness_exit_criterion`, `delivery_seat`, `discovery_pass_ceiling`,
   `map_assertion_provenance`, `generate_evidence_data` and `daily_self_note`. The disposition row
   says "the reader" and there is no such thing. **Confidence: high.**
2. **At least one reader of the four is L or W** — not tolerant. **Confidence: moderate.** If every
   one of them is T, the rows were right by luck and I will say so in exactly those words.
3. **More readers are O than are L.** `except OSError` is the guard people forget; per-line
   `try/except json.JSONDecodeError` is the one the idiom carries. **Confidence: moderate.**
4. Whatever I find, **it does not change the `benign` verdict** — the episode question is answered
   by the WRITER (append-only, mode `a`), and none of this touches that. The `loader` field is the
   only thing that can move. **Confidence: high.**

## What would refute each

(1) is refuted by a carrier with exactly one reader. (2) is refuted by every reader in the set being
T or O. (3) is refuted by an L/W count at or above the O count. (4) is refuted by finding a writer
that truncates or rewrites — which would make the row's *verdict*, not its `loader`, wrong.

## Done means

Every reader in the enumerated set opened and classified in a table beside the row it grades; each
of the four `loader` fields rewritten to say what was actually found, including the readers the
original row did not know existed; and any L/W/O reader either fixed or filed with its class named.

## The other half of this turn (no prediction needed — the answer is already known)

`background/sanity_daemon.py::_maybe_send_daily_digest` reads
`.sanity_daemon_last_digest_date` with a bare `read_text().strip()` behind an `.exists()` check and
no `except OSError`, unlike `boot_announce.already_announced_this_boot` and
`daily_self_note.already_ran_today`, which both guard. Content corruption is harmless here (the
text compare fails and the digest re-sends); the exposure is a permissions error or a directory at
that path raising into the sanity daemon's cycle, and the TOCTOU window between `.exists()` and the
read. This is a plain unguarded read and it gets the siblings' guard.
