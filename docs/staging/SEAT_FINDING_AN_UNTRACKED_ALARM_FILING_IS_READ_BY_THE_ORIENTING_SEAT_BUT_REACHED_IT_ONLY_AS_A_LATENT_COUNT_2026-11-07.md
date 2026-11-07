**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# An untracked alarm filing IS read by the orienting seat, but it reached the seat only as one LATENT count among eighteen (2026-11-07)

**Question (Lane 0, `does-the-draw-rank-an-untracked-alarm-filing-on-the-shared-tree`):** do the
delivery-lane draw and the orienting seat read a staging finding that `alarm_repetition` wrote
UNTRACKED onto the shared tree? The 7 Nov fork-open alarm was filed at 17:31 UTC and the
orientation after it (logged 18:48 UTC) does not mention it.

## What was measured

- **The draw does not read staging at all.** `delivery_lane.next_item` walks continuations and the
  orienting seat's `focus`. A staging finding reaches the draw only if the seat puts it into focus.
- **The seat reads untracked files.** `delivery-seat.service` runs with
  `WorkingDirectory=/home/rich/synthetic-enterprise`, and `findings_now()` →
  `finding_severity.scan_staging_root` globs the filesystem, so tracked or untracked makes no
  difference. Run on the shared tree just now: `{'BLOCKING': 2, 'LATENT': 18, 'RECORDED': 1}`.
  The fork-open filing is in that 18.
- **The brief names only BLOCKING and UNCLASSIFIED findings.** Every other severity reaches the
  seat as a number. `alarm_repetition` files at LATENT, so all 15 live repeating alarms reached it
  as counts, with no names and no dates. The 18:48 session could only have found the fork-open
  filing by listing the directory itself, without any cue to do so.

So the premise "invisible until someone commits them" is **refuted**. Committing the filing would
not have made it visible. The gap is in the brief, not in git.

## What changed

`background/delivery_seat.py` gains `live_alarms()` (a brief key, fail-soft) and
`_render_live_alarms()`, which goes into the prompt ABOVE the JSON so the 60k truncation cannot
drop it. It lists every live alarm document by name, newest observation first, with its first and
last observed dates and its day count. All of that comes from `alarm_repetition`'s own readers
(`alarm_documents`, `document_counts`), so no second detector and no second parser was added. The
control is `tests/background/test_a_latent_alarm_filing_is_named_in_the_orientation_prompt.py`.
Its mutation (dropping the render from `_prompt`) was run and it fires.

## What it does not settle

On the shared tree tonight, **all 15** live alarms were last observed today. If the list is mostly
furniture, it will be read the way the 139-name staging blob was (see
`supervisor._differentiated_staging`). Whether the seat acts on a firing alarm now is a question
about the next orientation records, not one this change answers. Check them: a record that does
not mention a newly filed alarm, while the alarm is named in its prompt, is a reader problem, not
a route problem.
