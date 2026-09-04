**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# Pre-registration: what the inbound channel's three unasked carriers must show

Filed 2026-09-04 by the delivery seat, **before the measurement was run**, under the Lane 0 claim
`ask-the-remaining-32-benign-census-rows-the-loader-question-2026-09-04`.

## Why these three, out of the 31 unasked `benign` rows

The direction ranks the sweep by **what the carrier's WRITER does** — a read-modify-write over the
whole state file can destroy the record, where a pure reader only loses a suppression. It named
four: `.dispatcher_seen.json` and `.staging_watcher_seen.json` were swept earlier today
(`tests/background/test_the_two_read_modify_write_seen_carriers.py`), leaving
`.last_processed_fingerprint.json` and `.ntfy_responder_seen_hashes.json`.

Reading `background/ntfy_responder.py` to rank the second of those moved the whole answer. That one
daemon holds **three** unasked carriers, and they are not independent — they are the three loaders
on the only inbound route the director has into this machine:

| Carrier | Loader | When it runs |
|---|---|---|
| `.ntfy_responder_since.json` | `_load_since` | `main()`, first act, **outside every try** |
| `.ntfy_responder_seen_hashes.json` | `_load_seen_hashes` | `main()`, second act; held in memory, re-saved every 20s |
| `.ntfy_responder_rate.json` | `_load_rate_state` | inside the poll, on the flood/provenance paths |

So the unit of work is *the inbound channel*, not *one census row*. A defect in the first two is
not "a lost suppression": it is the director's messages not arriving, with a daemon that is either
absent or alive-and-looping.

## The predictions — each one refutable, recorded before the run

Partition per carrier: **missing file · empty file · truncated · `null` · `[1, 2, 3]` ·
`{"other": 1}` · `["x", 2]`**, plus a **CONTROL LEG holding a live prior**. The control leg is not
decoration: without it "absent and unreadable differ" is satisfied by a loader that answers
UNREADABLE to everything, which for `_load_since` means discarding every message on every start.

**`_load_since`** — `json.loads(STATE_FILE.read_text())["since"]` under
`except (json.JSONDecodeError, KeyError)`.

1. `null` and `[1, 2, 3]` **RAISE TypeError**, uncaught. `None["since"]` and `list["since"]` are
   neither JSONDecodeError nor KeyError. This is the first statement of `main()` and there is no
   try above it, so the prediction is that **the responder does not start at all** — the
   `.sim_next_run_not_before.json` shape, on the inbound channel instead of the producer.
2. empty / truncated / `{"other": 1}` → `time.time()`, the same answer as a missing file.
3. Control leg (`{"since": 1234.5}`) → `1234.5`.
4. The conflation costs more than a reason string here: `time.time()` on an UNREADABLE watermark
   **silently discards every message that arrived while the daemon was down**, which is exactly
   right for a cold start and exactly wrong for a lost watermark.

**`_load_seen_hashes`** — `json.loads(...)` under `except (json.JSONDecodeError, ValueError)`,
annotated `-> list[str]`.

5. `null` returns **`None`** and `{"other": 1}` returns a **dict**; both parse, so the except-clause
   never sees them, and the annotation is not enforcement.
6. Downstream, `None` makes `set(seen_hashes)` raise TypeError **inside `check_once`**, which
   `main`'s loop catches and logs. Prediction: the responder then **polls forever, logging
   `Responder error:` every 20 seconds, never advancing `since` and never processing a message** —
   alive, warm, and deaf. A dict survives `set()` and raises `AttributeError` on
   `seen_hashes.append(h)` instead, i.e. **only when a new message actually arrives**.
7. `[1, 2, 3]` and `["x", 2]` do not raise: they become a set of the wrong things, every hash misses,
   and the record is then **written back** by `_save_seen_hashes` on the next cycle — the
   destructive half, and the reason this row outranks `.last_processed_fingerprint.json`.
8. Control leg (a live list of two hashes) → those two hashes.

**`_load_rate_state`** — has an `isinstance(state, dict)` screen.

9. Predicted **sound in every direction**: no member raises, all six unreadable members fall to
   `{"events": [], "last_alert": 0}`. The defect is the reason only — a lost flood window costs at
   most one duplicate alert and one undetected window. Ranked last, and expected to need no repair
   beyond telling the two priors apart.

**`.last_processed_fingerprint.json`** (`_read_last_fingerprint`, the fourth carrier the direction
named) — predicted **safe in every direction and unranked for repair this turn**: it returns `None`
for absent and for unreadable, `None != fingerprint`, so every member forces a republish. The write
is a full overwrite of a freshly computed value, not a read-modify-write, so nothing is destroyed.
If the measurement shows a raise, this prediction is wrong and it jumps the queue.

## What would refute this

Any member raising where I predicted a value, or returning a value where I predicted a raise. In
particular, if `_load_since`'s `null` leg does **not** kill `main()` — because something above it
catches, or because the daemon is started by a supervisor that retries — then prediction 1 is wrong
and the severity of the whole first carrier drops to the second one's.

## What done means

Each of the three carriers tells ABSENT from PRESENT-BUT-UNREADABLE, no member of the partition
raises out of a loader, the unreadable bytes are preserved before any write that would overwrite
them, and the census row carries a `loader` field recording the answer. Controls assert the two
answers **DIFFER** and carry a reachability leg proving a live prior reaches a third answer.
