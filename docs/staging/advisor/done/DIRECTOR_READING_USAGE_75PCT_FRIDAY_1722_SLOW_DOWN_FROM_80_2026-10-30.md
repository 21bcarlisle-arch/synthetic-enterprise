**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 75% on Fri 30 Oct, 17:22 GMT: slow down from 80% and leave the weekend's headroom for the director

**Type:** READING, through the advisor channel. The director's words, from chat:

- Fri 30 Oct, 17:22 GMT: "75% usage. Please slow down from 80% as I have some other no project related stuff to dot his weekend"

## The reading

- Plan usage was **75%** at Friday 17:22 GMT. The weekly reset is **Monday 2 Nov, 03:00 GMT**, about 57.6 hours away.
- From Tuesday 17:49 (29%) to now, the burn was about 0.47 points an hour [derived]. That includes the advisor's research passes today, which were heavy.
- At that rate, usage reaches **80% at about Saturday 03:00–04:00 GMT** [derived].

## What the director asks

**Hold the project at or near 80% until Monday's reset.** The remaining headroom is the director's, for other work this weekend.

1. **From now until about Saturday 02:00 GMT, work normally but lean.**
   - Finish what is already landing.
   - Prefer the cheap correctness items.
   - Open no new large items.
   - Launch no new full runs beyond any already in flight.
2. **From about Saturday 02:00 GMT until Monday 03:00 GMT, run in minimal mode:**
   - no BUILD or drafting draws;
   - no new runs;
   - no knowledge drafting;
   - no cold reads.

   Keep running only what must run: the daemons, safety controls, and whatever the Monday publish pipeline needs. Land nothing that cannot wait. If a genuine incident happens (data loss, a failing safety control, a broken publish), act on it and record it.
3. **Monday after 03:00:** resume normal pacing. The Monday run and publish go ahead as usual.

The machine cannot read the usage meter itself, so this is a time-based rule from the director's 17:22 reading. Under his 15 Oct delegation, pacing is yours to decide. The ceiling, though, is his ask.

**The advisor will also stop new research passes until the reset.**

## Done

Actioned on Fri 30 Oct at 17:46Z by the seat executor, through the dial rather than a promise:

    python3 -m background.tick_mode fold-only --until 2026-11-02T03:00Z --then normal

- **What it does.** worker-tick, delivery-seat and two-reader-review do not spawn. The seat executor
  still spawns, but it takes only items that grade a long job already in the launch register. So no
  BUILD or drafting draws, no new runs, and no cold reads. Daemons that spend no model tokens keep
  running. At Monday 03:00Z the dial reverts to normal by itself, ahead of the Monday run and publish.
- **One deviation, toward his headroom.** The dial cannot chain two modes (lean until Sat 02:00,
  then minimal), so minimal starts now, about 8 hours early. This forgoes the "work normally but
  lean" window. Work already landing is not stopped: the surgical_land for the PC2 fixes and the
  in-hand gas build both finish in their own processes. To reverse it:
  `python3 -m background.tick_mode normal` (or `slow --until 2026-11-02T03:00Z`).
- **The three customer-needs steers of 30 Oct** are large drafting items, so they are not started
  this weekend. They stay in the advisor root, and one continuation,
  `customer-needs-corpus-after-the-reset`, carries them with the embargo
  `DO NOT DRAW BEFORE 03:00 on 2026-11-02`. `delivery_lane --embargoed` reads it as HELD.
