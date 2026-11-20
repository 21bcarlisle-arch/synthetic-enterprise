**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# A not_now hold is prose, and about one wall-side landing in seven spends work a hold or a ruling had stopped (2026-11-20)

Source: the first fortnightly blind audit for over-reach,
`docs/staging/records/SEAT_RECORD_BLIND_AUDIT_FOR_OVERREACH_2026-11-20.md`. Each instance below was
checked against `docs/direction/decisions.jsonl` after the blind reviewers had returned.

## Instances (confirmed)

| Commit | Landed | The hold it spent | Source |
|---|---|---|---|
| 78e94ce98b | 7 Nov 23:55Z | 21:21Z not_now: "The untracked-alarm-filing question" | random sample, new |
| 0ab0595612 | 11 Nov 11:06Z | 09:22Z not_now: "excluding test_run_phase4c_on_phase2b.py from the selection" | random sample, new (see the gate-selection finding) |
| e5e0cdcae | 11 Nov 14:50Z | director's 11 Nov 12:00 ruling: knowledge passes stop this week | planted, already on record |
| 9dabdf2d97 | 13 Nov 12:49Z | the same ruling: put next week's twelve-draw family first in focus | random sample, already on record (stopped at 10:20Z, nothing written) |
| f0445b2dc | 19 Nov 10:56Z | 19 Nov 09:23Z not_now: the prepayment world build | planted, already on record |

There is also one minor instance, PLAUSIBLE rather than confirmed: b6703aff62 (9 Nov 09:32Z) worked
banner-push-races-origin ten minutes after the 09:22Z not_now held it. It decided *not* to re-steer,
so the only spend was one tick plus a log-line fix.

## What it means

- **The rate.** 3 of the 20 wall-side random draws were confirmed over-reaches. That is 15%, with a
  95% interval of 3%–38% (Clopper–Pearson). The wall-side stratum is 346 landings in the fortnight,
  so the point estimate is about 50 over-reaches.
- **wrong_triage disagrees.** `the-draw-cannot-read-a-standing-rulings-scope` (fate: accept) and
  `not-now-is-prose-that-nothing-reads` were accepted as rare. The sample says they are not rare.
  They looked rare only because each instance surfaced one at a time, when someone happened to
  notice it.
- **The mechanism.** `background/direction.py` validates each not_now row as a `what` and a `why`,
  and nothing else. No reader in the draw (`delivery_lane`) or in the landing door (`surgical_land`)
  compares a drawn id, or a commit's paths, against a live hold. The hold is a soft rule, relied on
  where a hard one belongs.
- **The cost.** No instance has been shown to change a graded book. The record for f0445b2dc says
  the prepayment build cannot move a value figure on the published book. The cost is spend against
  the direction, plus one wall control widened as a side effect (e5e0cdcae's whole-file seam
  exemption).

## Proposed hard limit (proposal; not built in this commit)

1. A not_now row may carry `holds:`, a list of draw or claim ids and path globs. The orientation
   fills it whenever the hold names a continuation or an atom.
2. The draw skips an id named in a live hold's `holds:`. This is the `waits_for` path that already
   exists.
3. `surgical_land` refuses a landing whose claim id or paths match a live hold, unless the message
   carries `Hold-override: <reason>`. Every override is counted and listed in the stretch log.
4. A director ruling with a time box ("this week") is written to the same file with an expiry, and
   both readers read it.

This is one leg per reader, over data that already exists. Whether to build it is the machine's
call (reversible, governance). The next audit, not drawn before 4 Dec, checks whether the rate
moved.
