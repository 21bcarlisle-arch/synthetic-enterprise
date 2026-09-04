# SEAT FINDING — the send-once memory lost every id to a file it could not read

**Date:** 2026-09-04
**Class:** R10 (an absurdity is fixed as a class, not an instance) · R15 fail-silent
**Severity:** BLOCKING · **Lane:** H_harness — the crash is on the ntfy send path, and the silent
half makes the machine read its own outbound as a message **from the director**.
**Status:** REPAIRED, except one judgement that is named and deliberately not guessed.
**Continues:** `SEAT_FINDING_THE_THREE_CARRIERS_THE_CENSUS_HAD_NEVER_DISPOSITIONED_WERE_OUTSIDE_THE_CONTROL_BY_CONSTRUCTION_2026-09-04.md`,
whose residual named these two carriers as the next item. This is that item, measured rather than
left as a hypothesis.

---

## The finding in one line

**`benign` on the self-clearing-alarm census answers one question — "can a write shorten an
episode?" — and it had been read as a clean bill of health.** Both carriers below are correctly
benign on that question. Both were failing a different one, with consequences that have nothing to
do with episodes.

## Measured, against a control leg with a readable prior

**`ntfy_utils.record_sent_id` / `was_sent_by_us`** — prior = three ids we had sent:

| prior | file after the send | `was_sent_by_us('id1')` |
|---|---|---|
| LIVE PRIOR (control) | `['id1','id2','id3','id_new']` | `True` |
| missing file | `['id_new']` | `False` — correct, nothing was ever sent |
| truncated / empty | `['id_new']` | **`False` — all three lost** |
| `null` / `{"a": 1}` | **AttributeError inside the flock, on the send path** | — |

`record_sent_id`'s own docstring says this file exists to stop an unrecorded id making
`was_sent_by_us()` return False for our own outbound, "which ntfy_responder captures as INBOUND and
stages a bogus from_rich — observed live". The flock it describes protects against a **race losing
one id**. A file it could not read lost **all of them**, silently, and nothing had ever looked.

A fabricated `from_rich` is not an ordinary defect: it is a message carrying the director's
authority that he never sent, and this seat is instructed to treat his words as authoritative
without a second channel or a minimum length. "yes" and "go" are complete.

And a third shape, the opposite failure: `json.loads('"abc"')` is a **string**, and `msg_id in
"abc"` is a **substring test** — so a corrupt file could answer `True` for an id nobody ever sent.

**`notify._read_transitions`** — annotated `-> dict`, returned **`None`** for a file containing the
four characters `null`, one `.get` away from every caller. `-> dict` is not enforcement; that is the
lesson `background/episode_prior.py` was built on, one module over.

## What was repaired, and the one thing that was not

Repaired: no member of the partition raises; an unreadable sent-ids file is **preserved beside
itself** before the rebuild rather than overwritten; a non-list can no longer answer `was_sent_by_us`
by accident; `_read_transitions` always returns a dict.

**Not repaired, and named rather than guessed: what `was_sent_by_us` should ANSWER when it cannot
tell.** `False` says "not ours" and fabricates a `from_rich`. `True` suppresses a real message from
him. Both are wrong and neither is obviously less wrong — it is a decision about the **responder's**
fail direction, not a detail of this loader, and guessing it here would produce a control nobody
chose. `sent_ids_unreadable()` makes the third state askable in the meantime, and the docstring
carries the question where the next reader will hit it.

`.notify_transitions.json` keeps absent and unreadable on **one answer, deliberately**: that memory
only suppresses a repeat, so losing it costs one duplicate message and never a missed one. Stated in
the row so it reads as a decision and not an oversight.

## The control

`tests/background/test_benign_rows_were_never_asked_the_loader_question.py`, 23 legs, each carrier
with a reachability leg.

| mutation | result |
|---|---|
| stop preserving the bytes | FIRED |
| restore the bare `ids = json.loads(...)` / `append` pair | FIRED |
| drop the `isinstance` screen in `was_sent_by_us` | FIRED |
| `sent_ids_unreadable` always False | **SURVIVED, then fixed** |
| drop the `isinstance` screen in `_read_transitions` | FIRED |

**The survivor was a missing test, not an equivalence, and establishing which is the rule.** The
first draft tested only the truncated file — which takes the `except` branch, so replacing the final
screen with `return False` changed nothing it asserted. The legs that **parse** are exactly the ones
that escape every except-clause, and they were the ones not covered. A leg over `null`, a mapping, a
bare string and a list of ints now fires it.

## Residual

**32 `benign` rows still unasked**, each now visibly so: a row with no `loader` field has not been
asked, which is a gap and not a pass. The shape to look for remains a read-modify-write over a state
file — `.dispatcher_seen.json`, `.staging_watcher_seen.json`, `.last_processed_fingerprint.json`,
`.ntfy_responder_seen_hashes.json`. Their consequence is re-processing, which is milder than this
one; that is a reason to rank them, not a reason to assume them.
