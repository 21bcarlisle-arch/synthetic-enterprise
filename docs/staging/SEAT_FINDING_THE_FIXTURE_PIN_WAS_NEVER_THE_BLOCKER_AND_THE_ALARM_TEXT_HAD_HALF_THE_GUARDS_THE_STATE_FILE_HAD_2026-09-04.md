**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# The fixture pin was never the blocker, and the alarm text had half the guards the state file had

Filed 2026-09-04 by the delivery seat, closing the piece
`SEAT_FINDING_A_ZERO_START_TIME_RENDERED_AS_AN_ESTABLISHED_1970_EPISODE_ON_THE_DIRECTORS_OWN_SURFACE_2026-09-04.md`
left open, and **correcting that finding's own account of what stood in the way.** Both the
correction and the thing it corrects are kept, because a prediction filed after the answer is not a
prediction.

## What was asked, and what was actually true

The direction named one repair — `record_publish_gate_failure` adopts a persisted `wedge_since`
with the same `isinstance`-accepts-0 shape the renderer had just had fixed — and named one cost:
`tests/background/test_publish_gate_blocking_payload.py::
test_the_state_the_supervisor_draw_reads_carries_the_blocking_test` pins
`persisted["wedge_since"] == 0.0`, so *"this is not a free repair"*. Its recommendation was to
change the fixture rather than the semantics, and it said explicitly that whoever took it should
**test that recommendation rather than assume it**.

Pre-registered before any measurement, with what would refute each prediction:
`docs/staging/records/PREREG_WHETHER_THE_FIXTURE_PIN_IS_ACTUALLY_THE_BLOCKER_ON_THE_ZERO_ADOPTION_2026-09-04.md`.

**The recommendation was aimed at the wrong obstacle.** Applying the adoption repair alone and
printing the value:

    persisted wedge_since = 0.0

The named control stayed **green**. The fixture pin was never load-bearing, because the repair it
was supposed to block was a no-op. `_write_publish_gate_state` runs every write through
`episode_monotonic.guard_episode`, where an episode start is a **LOW-water** field — and
`0.0 <= anything`, so the guard wrote the zero straight back on every honest restamp, forever.
A persisted zero was not merely accepted; it was *unbeatable*.

The control that actually reddened was the sibling from the same finding —
`test_a_persisted_zero_does_not_reach_the_alarm_text` — because its fixture drove the writer at
`now=1800`, and an honest restamp of a fake clock renders an honest `1970-01-01T00:30`. **A
fixture's clock has to be a possible clock**, which is the same defect as the pinned `0.0` one
file over, in the file written to complain about it.

## The repair: two changes, each dead without the other

1. **`background/process_run_complete.py`** — `_is_episode_start()`, one definition of "an instant
   an episode could have started at", called by the adoption clause. Positive, and not a `bool`.
2. **`background/episode_monotonic.py`** — `_is_start_to_remember()`, screening the **prior** side
   of a `since_field`. Asymmetric on purpose: of the proposal the guard asks *can I order this?*
   (a call-site property, and a misdeclared field must still raise); of the prior it asks *is there
   a start here to remember?*, and an instant at or before the epoch answers no. Screening at the
   prior rather than inside `_episode_key` keeps `_refuse` firing on genuine type errors alone, so
   this cannot raise inside the failure path of the pipeline it monitors.
3. `episode_age_seconds` takes the same screen, so the centralised reader answers "no start
   recorded" instead of "500,000 hours".

Printed across the whole partition at real inputs before the tests were written:

| persisted `wedge_since` | persisted after a failure at `now` |
|---|---|
| `0.0` | `now` (restamped) |
| `-1.0` | `now` (restamped) |
| `None` | `now` (cold start) |
| `now - 7h` | `now - 7h` — **remembered** |

## What mutation found that no reasoning did

Seven mutations, each a revert or a tautology. Six fired. **One survived, and it was a missing test
rather than an equivalence** — established rather than assumed, because the flattering reading was
available and wrong.

Replacing the writer's entire adoption clause with `wedge_since = now` left all ten new legs green.
The persisted field is guarded **twice** — the writer's screen and the monotonic guard — so the
state file was still correct. But `_episode_phrase` is handed the writer's **local** variable, not
the guarded persisted one, so the alarm the director reads said:

    CURRENT:  EPISODE: wedged since 2027-01-15T01:00 UTC -- 7h00m and 4 consecutive failures
    MUTATED:  EPISODE: wedged since 2027-01-15T08:00 UTC -- 0h00m and 4 consecutive failures

**That is the 2026-08-09 defect verbatim** — a 10h26m outage paging as 14 minutes — the exact
failure the whole `episode_monotonic` module exists to cure, live on the NTFY path, and no control
in this repository could see it. The state file was protected twice and the sentence a person acts
on was protected once. `test_the_alarm_text_reports_the_open_episodes_real_age_not_a_fresh_one` is
that leg; it asserts what is **sent**, where the others assert what is **written**, and they are
different values read from different variables.

## Still open, named rather than left for the reader

`background/supervisor.py::_publish_gate_wedge_active` (~L3791) reads `wedge_since` and
`alerted_at` with its own hand-rolled `isinstance(v, (int, float))` and takes `min()` over them
together with the raw failure timestamps. A zero there dates the wedge to 1970 — always older than
any threshold — so the RUNG-1 draw fires permanently. **Not fixed here, and the reason is that
fixing the two state keys would not fix it**: the `failures[].ts` entries feed the same `min()` and
carry no screen at all, so this is a different subject (a failure timestamp, not an episode start)
and deserves its own measurement rather than a clause smuggled in beside this one. It is now
unreachable from the writer — no zero can persist — but a legacy state file on disk still reaches
it, which is what makes it worth writing down instead of closing silently.

## The tooling gap this turn reproduced on itself, and it is the parent finding's own class

The parent finding added `site/data/director_reserved.json` to
`tests/production_surface_guard.PROTECTED_FILES` — the *sink* level of its three-level fix. While
measuring the partition table above I drove `record_publish_gate_failure` from ad-hoc
`python3 - <<EOF` probes rather than from pytest, and **evicted the director's live one-way-door
escalation from that exact file**, replacing it with a fixture's alarm carrying the `0h00m` phrase
from a mutation.

The guard did not fire, and could not: it is a pytest fixture, so it protects the surface from
TESTS and not from anything else that imports the writer in the same tree. That is a fail-open on
the same sink the parent finding had just closed, found by walking into it. Restored explicitly
from `HEAD` (`git show HEAD:<path> > <path>`; `git checkout <path>` is banned here and I used it
once by reflex earlier in this turn, which silently reverted a completed edit to
`episode_monotonic.py` — the ban is well earned).

**Filed as its own subject, not fixed here**, because the honest fix is at the writer
(`action_needed._mirror_reserved_to_site` refusing to write a live surface when its own state is
fixture-shaped) and that is a design question, not a clause.

---

# Two further findings from the same turn, folded in rather than filed separately

Both were found while LANDING the repair above, not while making it. They are sections here
rather than root documents because the staging root is already running a net +42 filings over
dispositions across seven days, and a queue whose filing outruns its dispositioning grows
without bound whatever its size today. Neither is fixed; each names its own subject and remedy.

## `surgical_land --merge` cannot pass a control that reads the index, and the merged tree was clean

Filed 2026-09-04 by the delivery seat, hit while promoting the zero-episode-start landing. **Not
fixed here** — the control is a day old and belongs to the lane that wrote it, and the workaround
is legal and cheap. Written up because the two mechanisms are both sanctioned and they deadlock.

### The two halves

`tests/background/test_only_work_is_in_the_work_channel.py::
test_no_document_is_TRACKED_in_the_staging_root_that_a_disposition_will_move_out` (landed
2026-09-04 in 413f8c661) states its subject deliberately, and the reasoning is good:

> **THE SUBJECT IS THE INDEX, and that is not an accident.** `surgical_land` gates a standalone
> extract whose HEAD is the PARENT sha but whose INDEX is the tree the commit would create, so
> `git ls-files` is the only subject that judges the commit being made rather than the one before
> it.

`tools/surgical_land --merge` states its own, and that reasoning is good too:

> The merged tree is computed by plumbing (**the shared index is never opened**, so another lane's
> staged work cannot be swept into it), gated like any other resulting tree.

**Each is right and together they cannot both hold.** A merge route whose whole safety property is
that it never opens the index cannot present an index that describes the tree it is about to
commit.

### What it did, measured

Merging `origin/main` (which had MOVED `SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_
2026-09-04.md` out of the staging root into `records/`) into a branch that still carried the file
at the root was refused:

    E  AssertionError: these are tracked in the staging root but their kind sends them to a room
    E  `room_collisions` treats as mutually exclusive with it
    E  assert ['SEAT_PREREG...026-09-04.md'] == []

The merged tree does not contain that path. Checked with plumbing, not inferred:

    $ git merge-tree --write-tree HEAD origin/main   ->  5460d8b69...
    $ git ls-tree -r --name-only 5460d8b69 -- docs/staging | grep FOUR_SMALL_REPAIRS
    docs/staging/records/SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_2026-09-04.md
    $ git ls-files docs/staging | grep FOUR_SMALL_REPAIRS
    docs/staging/SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_2026-09-04.md   # <- the gate's subject

**The commit being made was clean and the commit being graded was the one before it** — precisely
the failure mode the control's own docstring says reading `git ls-tree HEAD` would cause. It reads
the right thing on the pathspec route and the wrong thing on the merge route, and nothing marks the
difference.

`staging_rooms.REPO_ROOT` is `Path(__file__).resolve().parent.parent`, so the query follows
whichever tree the gate process imported from. That is the seam.

### Why this is BLOCKING rather than an annoyance

The refusal is **unconditional for the merge route**, and a merge is how every lane re-gates on a
moved origin. Any room-rule violation anywhere in the tracked staging root — including one another
lane introduced and origin has already fixed — refuses every merge in every worktree until someone
reproduces the fix locally by hand. The failure presents as *your* merge being dirty.

### The workaround, which is legal and is what this landing used

Land origin's move on your own branch **by pathspec** first, which is the route the control grades
correctly, and then merge:

    git show origin/main:<room path> > <room path>
    python3 -m tools.surgical_land --content-remove <root path> -m '...' <root path> <room path>
    python3 -m tools.surgical_land --merge origin/main -m '...'

Landed as 0f4efdf7a then d831f7153. The pathspec commit passed the identical gate the merge had
just been refused by, on the same tree, seconds apart — which is the cleanest available evidence
that the subject and not the content is what differs.

### The remedy this seat would pick, offered rather than taken

Have `--merge` populate the extract's index from the computed merge tree, exactly as the pathspec
route already populates it from the candidate tree. That keeps both stated properties: the SHARED
index is still never opened, and the gate still grades the commit being made. It is a change in
`tools/surgical_land`, not in the control — the control's reasoning is correct and should not be
weakened to accommodate a route that is not giving it what it asks for.

---

## A grid-intensity refresh dropped 288 of 1247 records, and nothing in the tree noticed

Filed 2026-09-04 by the delivery seat. **Observed, not diagnosed** — the cause is not established
here and this document does not guess at one. It is filed because the observation was about to be
thrown away, and because the thing that surfaced it was a landing gate refusing for an unrelated
reason.

### The observation

While promoting an unrelated landing, `tools/promote_worktree_landing` refused on uncommitted
tracked changes, one of which was `docs/market_data/grid_intensity_feed.json`, rewritten in this
worktree at `2026-09-04T14:01:41Z` by a daemon tick (not by this seat — no fetch was run here).

Counted rather than eyeballed from the diff:

| | `records` rows | `named_gaps` rows |
|---|---|---|
| committed at HEAD (`published_at` 2026-08-26T13:14Z) | **1247** | 8 |
| rewritten in tree (`published_at` 2026-09-04T14:01Z) | **959** | 8 |

The refresh **lost 288 records, 23% of the series**, while keeping the same top-level keys and the
same `named_gaps`. The shape is intact; the history is not.

### Why it is filed rather than fixed

Two readings have opposite remedies and this seat cannot tell them apart from one sample:

* a **partial fetch** silently persisted as a whole feed — the file is rewritten, not appended, so
  a short upstream response becomes the record; or
* a **deliberate re-derivation** on a narrower window or a changed source, in which case 959 is
  correct and the only defect is that nothing says so.

Establishing which is a question for whoever owns the feed's writer, against the published source,
and is exactly the kind of number this project's rules forbid picking. Both readings share one
consequence, and that consequence is the reason this is worth a document at all:

**Nothing in the tree can tell the two apart either.** A feed whose row count can fall by a quarter
between refreshes with no floor, no delta bound and no provenance note is indistinguishable from a
feed being quietly truncated. The remedy in either case is the same first step — the writer records
what it fetched and refuses to shrink the series without saying so — and that step is worth taking
before the cause is known.

### Disposition of the bytes

The working-tree copy was restored to the committed one (`git show HEAD:<path> > <path>`) so the
short version was **not** landed, and this landing carries none of it. The daemon will rewrite it on
its next tick, so this is a reprieve and not a fix: if the cause is a partial fetch, the 959-row
version reaches origin the next time a lane lands with a dirty tree and does not look.

Two sibling files were dirtied by the same tick and restored the same way —
`site/data/explore_carbon.json` and `site/data/weather.json` — both timestamp-only changes, and
neither is evidence of anything.

### What made it visible, which is the part worth generalising

Nothing was watching this feed. It surfaced only because an unrelated landing gate refuses to
promote a worktree with uncommitted tracked changes and **named the paths**. A refusal that lists
what it found is doing a second job nobody designed it for, and this is the second time this turn
that a gate's own output was the evidence (`finding_severity` prints the full BLOCKING roster).
Worth remembering when a refusal is made quieter.
