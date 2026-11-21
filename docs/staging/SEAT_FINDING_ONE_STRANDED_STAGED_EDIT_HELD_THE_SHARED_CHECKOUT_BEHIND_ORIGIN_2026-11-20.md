**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One stranded staged edit held the shared checkout behind origin for six hours, and from 12:02 the book with it

Measured 2026-11-20 on the shared tree, against origin/main 32b77a9874, for the lane-0 item
the-shared-checkout-rejoins-origin-so-the-book-runs.

## What held it

The reconciler logged NOT_ADVANCED on every cycle from 06:27Z. Its "Held by" list was one path
from 06:27 to 09:28: `docs/staging/done/WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT_2026-08-13.md`.
After 09:28 it was that path plus three the delivery seat writes at orientation (DIRECTION.yaml,
decisions.jsonl, SEAT_STRETCH_LOG.md). Those three were in flight to origin by their owner, so
they were transient. The one path was not. Until about 12:00 the box was held anyway, by the
resident value-test long job and the memory budget. From 12:02 the stall was binding. On every
cycle with no landing in flight, sim-runner deferred, because a run is stamped with HEAD and its
imported `company/billing/ledger_store.py` held origin's bytes (a1fdada3ee), not HEAD's.

Two dispositions of that file existed:

- the shared index and disk: the 18 Nov worker tick's "DISCHARGED -- item 3 is built", staged with
  the build itself (tools/generate_company_data.py, its test, site/data/company.json) and never
  committed;
- origin, from 6594aec2b6 (the triage of the ten BLOCKING findings, 20 Nov): "OBSOLETE ... if a
  drill-down returns, item 3 here is its spec".

The triage worked from origin, as its item told it to. On origin the code still read
`DRILLDOWN_ID = "C1"`, so it graded the finding against a build it could not see. The reconciler
then correctly refused to choose between two dispositions. Its abandonment line is 48h, and the
edit was 42h old, so it would have held for six more hours.

## The kind the item asked about does recur, and it did not hold anything

The item asked whether landings leave origin's bytes in the shared tree without advancing HEAD.
They do. Of the 138 paths blocking the fast-forward at 12:40Z, 60 were byte-equal to origin. They
came from 9 commits, and 51 of the 60 came from the four triage landings (16 from 8ee7d4be90, 16
from 17b3697d6d, 12 from dfd53e8bf0, 7 from 6594aec2b6). That is the prescribed door:
`surgical_land` refuses a primary checkout that is behind, and it tells the lane to land from a
worktree. The reconciler's twin classes clear these copies by hash. They are not a defect, and the
item's hypothesis is refuted: the producer of the stall was one stranded staged edit, not the
twins.

## What was done

The 18 Nov build was landed from a trunk worktree (tests 21 passed). The finding kept origin's
triage line, gained the discharge, and says why both are there. That made the shared copy equal
to origin. Of the staged paths in the shared index, only these 4 still had a file on disk, so no
second instance is waiting.

## Open

A lane that rewrites a file on origin cannot see a newer, unlanded copy of it in the shared tree.
That is the shape here, and it costs up to 48h of books each time it happens. One instance does
not justify a control (CLAUDE.md: the smallest mechanism). If it recurs, the cheap leg is a single
check in the staging triage: whether the shared tree holds a staged copy of the file it is about
to rewrite.

## Correction 2026-11-21 (autonomous worker): a twin is harmless only until HEAD passes it

The verdict above ("they are not a defect") held at 12:40Z on 20 Nov. It stopped holding once the shared
HEAD advanced past those twins. From then on, each twin was an OLDER copy than HEAD, and every reader of the
shared tree read it as a reversion. The supervisor's draw is one of those readers: its `MATURITY_MAP_PATH` is
the working-tree file, at eight load sites.

Measured: the shared `docs/design/maturity_map.yaml` was byte-equal to dfd53e8bf0's blob, one of the four
triage landings named above. Against HEAD, its whole diff (11 lines) removed only content HEAD already
carried: W2_30's `blocked_on: [W1_14_...]` (landed 0ddafc418b, 19 Nov 14:02), its `l3_gate_note` pointer,
AO5's `simplifications_count` and a D48 file_scope entry. The W2_30 simplification file was byte-equal to
f165c9b1ee's older blob. So the draw saw W2_30 as unblocked. `supervisor-log.md` records 439 dial-weighted
draws of W2_30 between 2026-11-20 04:46 and 2026-11-21 01:41, every one after origin had blocked it. A blocked
atom handed to a worker tick each time. Pre-change copies are in `/tmp/w230_restore/`.

Done: both files restored to HEAD's bytes, after checking that no hunk was unique to any lane. To reverse,
copy the `.wt_before_restore` files back.

Not done: the census of other stale twins. The working-tree-is-older test is `git diff HEAD -- <p>` having no
`+` line absent from some earlier blob. The cheap leg the Open section names would now also need to cover
"the shared tree holds an older copy than HEAD". A one-leg alternative is for the draw to read
`git show HEAD:` (or origin) for the map rather than the working tree. Neither is built here.
