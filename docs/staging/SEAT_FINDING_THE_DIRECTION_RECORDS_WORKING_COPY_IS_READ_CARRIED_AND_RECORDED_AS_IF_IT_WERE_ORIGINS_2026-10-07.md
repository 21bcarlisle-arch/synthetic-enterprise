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
