**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The notification digest has not flushed since 4 Nov, because the guard reads the whole digest as one ask (2026-11-13)

**What was found.** Since 2026-11-04 07:52 UTC the deadman logs `Notification digest flush failed
(queue intact): RecommendationRequired` on every cycle, about every 6 minutes (`journalctl --user`;
the latest seen was 20:57 UTC today). The digest holds 378 batched items. `background/ntfy_utils.py:334`
runs `recommendation_guard.check_message` over the whole digest text. Two queued items contain a
`?` in their prose: #6973 (PB6 parked, "...withhold offers from prepayment?") and #7186 (EAC
practitioner questions, which says "I am proceeding without the answers"). The `?` makes
`_looks_like_an_ask` true for the whole digest. The first 180 characters of the digest have no
recommendation phrase, so the guard refuses it. The high-water mark only moves on a confirmed
delivery, so the same digest is refused on every cycle and the queue keeps growing.

**Explanations, ranked by the evidence.**

1. **The guard is applied to a relay, not to an ask.** A digest quotes landing lines. It is not the
   machine asking the director anything. One quoted `?` is enough to refuse every later digest,
   permanently.
2. **The digest should not be sent at all.** NTFY was mothballed on 15 Oct ("Nothing reaches his
   phone except the dead-man's single push"). If the digest is meant to go only to the ops mirror,
   the send path is the defect, and the guard is just where it surfaces.

**Impact.** Low for the reader: NTFY is mothballed and every item is still in
`docs/observability/ntfy_digest_queue.jsonl`. The cost is about 240 log lines a day in the deadman
log, which hide real failures there, plus a queue that grows without bound.

**What retires it.** Decide (2) first. If the digest is still meant to be sent anywhere, run the
guard per item rather than over the concatenation, or exempt `kind: work_done` relays. Then put
one control on the property: a digest that quotes an item containing `?` still flushes.

## Reverse

Delete this file. Nothing else was changed.

## Disposition (worker tick, 2026-11-15): explanation 1, fixed

**Decided (2) first.** The digest should still be sent. With NTFY mothballed, `send_ntfy` writes it to the ops mirror
and the director input log (`out-mothballed`), the surfaces his advisor reads. So the send path is right, and the
defect is the guard's.

**Measured before the fix, on the live queue:** all 378 pending items pass `check_message` individually. #6973 and
#7186 each recommend ("My recommendation:", "I am proceeding"), but past the 120-character excerpt. So the digest was
refused for text it never carried.

**The fix.**
- The guard judges each relayed item in full: `send_ntfy(..., _relay_items=)`, forwarded by `notify` and passed by
  `notification_digest.flush`.
- An item that does ask bare is withheld from the digest by name ("withheld: it asks without recommending"), rather
  than raising. Raising on one item would hold every later item back for good. The queue keeps it in full.
- Live queue after the fix: 378 relayed, 0 withheld, no raise.

**Controls** (`tests/background/test_notification_digest.py`, both through the real `send_ntfy`, with curl made
unreachable):
- A digest quoting a `?` whose recommendation lies past the excerpt still flushes.
- A bare-ask item is withheld, and a bare ask handed over as a relay item still raises.
- Four mutations each red a test, and each was reverted: judging the whole message; not withholding in `compose`; not
  filtering in `relayed_items`; `flush` not passing the items.

**Expected:** the next deadman cycle logs `Notification digest flushed`, and the failure line stops.

**Reverse:** revert the commit.
