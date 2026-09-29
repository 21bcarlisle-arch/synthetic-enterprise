**Severity:** RECORDED · **Lane:** H_harness · **Atom:** none (Lane 0 delivery)

# DISPOSITION: the tick drew `a-long-job-that-dies-is-shown-dead-in-the-brief` one minute after the seat drew it

**What happened.** The seat executor (pid 1070814, cwd `/var/tmp/se-seat-executor`) started on this
item at 18:57 BST. The tick worker (pid 1072519) drew the same id at 18:58. The duplicate-work note
said the id was already held in `.seat_work_in_hand.json`. A `ps` taken before any build showed the
seat's `claude -p` process with this exact WORK text. So the claim was the seat's own claim, not the
draw's write.

**What the worker built:** nothing. `background/delivery_seat.py` is still HEAD's bytes in the shared
tree. The seat builds it in isolation and lands it.

**Why the worker did not `--release`.** The precedent
(`WORKER_DISPOSITION_THE_SUCCESSOR_OF_FIELD_..._2026-09-29.md`) released the tick's claim. Here
there is only one id, and it names the seat's claim too. A release from the tick could free the
claim the seat's `promote_worktree_landing --work-id` has to bind to, and then the pool could re-offer
the item while the seat is landing it. Leaving the claim alone costs nothing: the seat releases it
when it finishes, or the 100-minute sweep does.

**Disposition:** the seat's landing is the one of record, and this worker took no share of it. The
mechanism gap is the same one the precedent named. When a tick draw and a seat claim share an id and
start within about 60 s of each other, the draw's rule for telling its own stamp from another
writer's cannot separate them. `ps` separates them.
