**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
six-frame membership series

# The six-frame series was seven points spliced from two oracles, and the biggest frame at the consumer was not in it

**Filed 2026-09-16 by the delivery seat**, holding
`the-six-frame-membership-series-may-overstate-every-frame-because-it-was-never-measured-at-the-consumer`.

The item's hypothesis was that the six recorded frames overstate their payoff the way the seventh
did — membership +12 against a union delta of +2, a factor of six. **Measured, that is not what is
wrong with them.** Two of the six do overstate, two agree exactly, one moves the consumer in the
OPPOSITE direction to its membership, and three of the seven published numbers are not membership
deltas at all. The published series also omits four frames, one of which is the largest single
movement at the consumer in the whole history of this module.

## What was published

`tools/file_scope_generated_paths.generated_artefacts` said: *"On membership the sequence reads +8,
+9, +1, +11, -6, -1, +12 ... On the UNION it reads as a steady approach to zero."* The union half
was never measured. Only one frame — the whole-string one — had ever recorded a union number
(237 -> 247), and it is the only one of the seven points that was measured at the consumer at all.
The first three points were copied out of two preregs which state them as *"helper +8, signature
default +9, instance attribute +1, named segment +4"* — **frames on the WRITE-keyed oracle**, and
`+8`/`+9` are the counts of paths those sweeps FOUND, not the members they added. The
"named segment +4" point was dropped in the copying, and three whole tree-keyed frames were never
in the list.

## The method

One variable at a time, so the frame is the only thing that moves:

1. `git archive <frame>^ tools background simulation saas company` into a scratch extract.
2. Compute the union `generated_artefacts() | written_artefacts()` — the exact set
   `background/origin_reconcile._split_generated` reads — with `PYTHONPATH` at the extract root.
3. Overwrite **only** `tools/file_scope_generated_paths.py` with the frame's own version.
4. Compute it again.

The thirteen frames chain: every frame's "after" equals the next frame's "before" (180, 226, 226,
230, 234, 234, 237, 247, 246, 259, 260, 254, 253, 255). Nothing in the harness enforces that, so it
is the control on the harness rather than a property of it — a scratch extract that had picked up
another lane's bytes, or a frame whose commit also changed a scanned producer, would break the
chain and it does not.

## The measurement

| # | commit | frame | membership | UNION | tracked paths recovered |
|---|---|---|---|---|---|
| 1 | 3a069daa5 | write-keyed oracle born | write 0->144 | 180->226, **+46** | 39 |
| 2 | acb44a94d | atomic-write idiom | write +1 | **+0** | 0 |
| 3 | a2d130044 | helper frame | write +6 (published +8) | +4 | 1 |
| 4 | c9769d426 | signature default | write +6 (published +9) | +4 | 4 |
| 5 | cc9dba314 | instance attribute | write +1 | **+0** | 0 |
| 6 | d63f19123 | named segment | write +3 (prereg said +4) | +3 | 2 |
| 7 | e5b7a438c | whole string | tree +11 | +10 | 8 |
| 8 | 54e4a7bf2 | docs/status declared | tree +2, write -1 | **-1** | 0 (one WITHDRAWN) |
| 9 | 244f730c0 | site/state + docs/reports | tree +28 | **+13** | 9 |
| 10 | 257b785ea | prefix of any depth | tree +1 | +1 | 1 |
| 11 | 683a86222 | ordered reconstruction | tree -6 | -6 | 0 |
| 12 | 6cc48c6ca | glob refusal | tree -1 | -1 | 0 |
| 13 | fd4653fd9 | cross-expression head | tree +12 | **+2** | 1 |

"Tracked paths recovered" is the harm quantity: members ADDED to the union that are tracked files
at that commit, so a path the reconciler had been offering a landing on and now calls a producer's
output. Untracked dotfile state never reaches the reconciler and is excluded.

The nine at row 9 are `docs/reports/ANNUAL_REPORT.md`, `docs/reports/SEGMENT_REPORT.md`,
`docs/reports/bill_validation_comparison.json`, `docs/reports/c3_shown_price_departure_factors.json`,
`docs/reports/c6_second_pass_departure_factors.json`, `docs/reports/dd_opening_arms.json`,
`docs/reports/ladder_churn_factors.json`,
`docs/reports/run_output_old_reactive_model_pre5c.json` and
`site/state/track_record_scorecard.json`.

## What this changes

**The rule the seventh frame stated is right and the evidence it gave for it was wrong.** Membership
and the union part company on four of thirteen, and the factor-of-six ratio is not the shape:

- Rows 2 and 5: membership moved and the union **did not move at all**. Both frames added a member
  the other oracle already held.
- Row 8 is the strongest case in the series and was not in it. `docs/status` added two tree-keyed
  members the write scan already had, while the same commit carved `SEAT_STRETCH_LOG.md` out of
  both oracles. Membership **+2**, union **-1** — the only frame of the thirteen that made the
  consumer's set smaller, reading as a gain on the published quantity.
- The overlap that drives the gap is not a constant: of the new tree-keyed members, the proportion
  the write oracle already held ran 1 of 11, 2 of 2, 15 of 28, 0 of 1, 10 of 12.

**"Nearly shut" survives, for a narrower reason than the one given.** The union series in frame
order is +46, 0, +4, +4, 0, +3, +10, -1, +13, +1, -6, -1, +2. That is not a decay — row 9 is the
second-largest movement in the module's history and sits between two points the published sequence
plotted. What is true is the **last four points**, +1, -6, -1, +2, three of them from frames that
made the oracle stricter. A reader deciding whether another frame is worth starting gets the same
answer, and now gets it from evidence that exists.

## The class

A frame's payoff was quoted by the frame that came after it, from a prereg written before it, and
nothing anywhere could notice that the quantity had changed hands between two oracles on the way.
The one-line version: **a series is not evidence unless every point in it was measured the same
way, and the cheapest proof of that is that the points chain.** No control is built for this — the
measurement is eight lines of shell and the module now carries the method beside the numbers, which
is the smaller mechanism. Building a checker that re-extracts thirteen trees on every commit would
be the thing that watches the work.

## Correction landed

The false paragraph is kept in `tools/file_scope_generated_paths.py` beside its correction rather
than revised away — it is the only evidence the re-measurement was not fitted to its own answer.
