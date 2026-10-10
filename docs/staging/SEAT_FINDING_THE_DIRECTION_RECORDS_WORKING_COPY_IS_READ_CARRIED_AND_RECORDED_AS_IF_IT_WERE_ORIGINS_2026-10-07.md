**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The direction record's working copy is read, carried and recorded as if it were origin's

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Three carried items share one cause, so they share this home.*

## The cause

`docs/direction/DIRECTION.yaml` has two copies that matter: origin's, which is the record, and the
shared checkout's working copy, which is what every daemon and every landing actually reads. Nothing
compares the two before acting. Three separate defects follow from that.

## The three defects

1. **The brief reads the director's open concerns from the working copy.**
   `background/director_concerns.read_raw()` reads `direction_mod.DIRECTION_PATH`, which is the
   shared checkout's file. When the checkout is behind origin, a concern the director raised on
   origin is missing from the brief, and a record written from the brief alone would drop it.
   It recurred on 2026-10-05 (four listed, six on origin; `2b404892e`) and 2026-10-06 (`7211bc03a`).
   Every orientation since has checked it by hand. Carried as
   `the-brief-reads-director-concerns-from-the-behind-checkout`, 18 listings.

2. **Another lane's landing can carry the record from a stale working copy.** A `surgical_land`
   that names `DIRECTION.yaml` in its pathspec lands whatever copy its worktree holds. On
   2026-10-06 the B7 slice-4 landing (`dfa787a37`) put the 05:21 record back on origin, so origin's
   live focus was three finished items. `0be518a08` fixes the seat's OWN landing (re-base and page
   on refusal). It does not stop a landing that is not about the record from carrying it. Carried
   as `a-landing-carries-a-stale-direction-record`, 15 listings.

3. **A failed session is recorded as `oriented`.** In `background/delivery_seat.py` (around line
   2496) a session that exits non-zero and writes nothing leaves the PREVIOUS record on disk. It
   validates, so the row is written with `outcome: oriented` and `ran: false`, and the stretch log
   republishes the old record. That happened at 2026-10-06 20:21. `0be518a08` writes `refused` and
   pages only for a refused LANDING, not for a session that did not run. Carried as
   `a-failed-seat-session-is-recorded-as-oriented`, 4 listings.

## What done means

- The brief reads concerns from `origin/main:docs/direction/DIRECTION.yaml`, and falls back to
  the working copy only with a stated reason.
- A landing whose pathspec includes `DIRECTION.yaml` is refused unless its copy is byte-identical
  to origin's, or it is the seat's own direction commit.
- `ran: false` (or no new write to the record) is recorded as `outcome: refused` with the session's
  exit detail, and pages `blocked_work`.

Each leg needs a control that can fail: a behind-checkout fixture whose origin carries an extra
concern; a landing fixture that carries an older record; a session stub that exits 1.

## Why 167d583a4 never reached origin (2026-10-09 17:44Z), and what now says so

*Worker, 2026-10-10, drawn as `a-seat-run-whose-record-is-not-on-origin-says-so`. Read from the
`delivery-seat.service` journal 17:22-17:46Z, `docs/observability/delivery-seat-log.md:578`, the
refused row in `decisions.jsonl` and the NTFY mirror.*

**What happened, in order.**

1. The 17:22Z orientation's session wrote its record, and `land_direction_on_origin` gated it in
   `/var/tmp/se-direction-seat`, cut at origin `224e4af02`. The gate was green: 1220 passed, 87
   skipped, 413 s. That commit is 167d583a4 (17:44:35Z).
2. Promotion was refused. Origin had moved to 63f429536 (the front-door ruling and SITE15) while
   the gate ran.
3. 63f429536 touched none of the record's five paths, so the loop took the merge route
   (`_merge_origin_into`) rather than a re-cut. The `--merge origin/main` landing's gate selected
   no tests ("0 of 5 staged path(s)"), passed the test gate and the site lane, and then went **red
   at `[knowledge-gate] COMMIT REFUSED.`**
4. `_merge_origin_into` re-raises `LandingRefused`; only `IndexNotRefreshed` is caught. So the
   refusal left `land_direction_on_origin` as `LandingRefused`, not `DirectionNotLanded`, and
   `commit_direction` recorded `landing refused (LandingRefused): GATE RED ...`. 167d583a4
   stayed as the worktree's HEAD, in no ref on origin.
5. The next orientation (20:40Z) re-cut the worktree and landed bd189e491, which carried the
   same five files forward. So nothing was lost except three hours of origin's steer.

**Corrections to the drawn item.** It said *"nothing said so for three hours"*. That is wrong:
`record_landing_refused` paged at 17:45:51Z ("the direction record did NOT reach origin ...", NTFY
mirror line 2002), and the decisions record carries a `refused` row. What was missing is
narrower. The page and the row named a gate refusal, not the commit. And the 20:40Z brief, the
one place the next orientation reads, said nothing about the record the director reads being a
stretch old.

**Why the knowledge gate went red: I cannot yet say.** The refusal's own reasons went to stderr
after the `COMMIT REFUSED.` line, and `refusal_verdict`'s 600-character cut dropped them. So
the record does not name which file it refused. A faithful replay does not reproduce it. I
rebuilt the merge tree (`git merge-tree --write-tree 167d583a4 63f429536` gives `f1b934afb`, the
tree the receipt names), extracted it as `materialise` does into a standalone repo with HEAD at
167d583a4, ran the four re-derive renderers, and ran the whole `pre-commit` chain with
`PRE_COMMIT_GATE_MERGE_PARENT` set. Result: **rc=0**, knowledge gate included. The one staging
change in that diff is the ruling's move to `in_progress/`, and git reads it as `R077`, not an add,
so `staged_new_research` returns nothing.

Ranked by evidence:

- (a) Something in the live extract differed from the replay: environment, a concurrent sweep,
  or the overlay.
- (b) The gate's input at 17:45 differed from the receipt's tree.
- (c) Neither. Any other cause is outside what the replay can test.

The cheap next step is not more replay. It is to keep the knowledge gate's reasons in the refusal
(`refusal_verdict` keeps the `❌` tail but not a non-`❌` gate's stderr). Filed here, not built:
it is the `surgical_land` door's subject, not the seat's.

**What now says so (landed with this section).**

- `delivery_seat.seat_commit_not_on_origin()` reads the seat worktree's HEAD before the next
  landing re-cuts it. When that is a `delivery seat:` commit and not an ancestor of origin/main,
  it returns the sha:
  - The brief carries it as `seat_commit_not_on_origin`, third key, ahead of `commits`.
  - `is_material` orients on it, so a quiet stretch cannot skip the orientation that lands a
    fresh record.
  - `page_a_stranded_record` pages once per sha (`transition_key`
    `delivery-seat:record-not-on-origin`, state = sha). It stays silent when the last decisions
    row is a `landing_refused` that `record_landing_refused` already paged, so one event buzzes
    once.
- Defect 1 above is fixed. The brief's `previous_for_the_director` and the carry check in
  `orient` now use `director_concerns.open_rows_on_either(working copy, origin/main)`. That is the
  working copy's open rows plus the open rows only origin holds. An id that either copy has
  answered or withdrawn is excluded. A record that drops a row only origin holds is refused,
  naming it.

All of this is held by `tests/background/test_a_seat_record_not_on_origin_says_so.py`, nine
mutations, each red. The not-landed branch is asserted reachable before anything is asserted
about it.

**Still open here:** defect 2. A landing not about the record can still carry a stale
`DIRECTION.yaml`. So this finding stays in the staging root. A `done/` copy of it was on disk,
untracked and byte-identical to HEAD's. That was an unlanded move made while defects 1 and 2 were
both open, and it was removed with this landing. The seat's triage row
`the-brief-reads-director-concerns-from-the-behind-checkout` can now be marked `already_fixed`,
citing the commit that landed this section.

*Landing note, 2026-10-10 ~03:20Z.* The 01:25-01:31Z invocation built all of the above in the
shared tree and never landed it. A redraw under the same id carried those bytes into an origin-cut
worktree; `delivery_seat.py` and `director_concerns.py` were unchanged on origin since. Nine
mutations were re-run there, each hitting one of the branches above, and all nine went red. The
587 tests that import `delivery_seat` pass.
