# WORKER REPORT — the wrong population was a population nothing still produced

**Severity:** LATENT · **Lane:** D_billing_metering
<!-- Header added 2026-08-12 by a worker tick: this report carried a lane and no severity, so
     it was UNCLASSIFIED. LATENT and not RECORDED because work IS still owed by its own
     'Left open, deliberately' section -- the live site serves the three retired files until
     the next publish, and R11 wants the re-fetch as the proof. -->

**Closes:** `WORKER_FINDING_THE_PRINTED_FOOTING_CONTROL_RUNS_ON_A_SMALLER_POPULATION_THAN_THE_PAGE_2026-08-12.md`
(BLOCKING, lane `D_billing_metering`) · **Found:** 2026-08-12 worker tick · **Lane:** D_billing_metering

## What the finding got right, reproduced exactly

Both censuses reproduce on the working tree, using the control itself
(`check_printed_bill_foots_exactly`), not a re-implementation:

    site/state/billing_ledger.json   18 accounts  1557 invoices   0 not footing
    site/data/customers/*.json       21 accounts  1682 invoices  30 not footing
                                     C2_2 17 · C5_2 13 · C1_2 0

Both named records reproduce to the penny, and — the finding did not check this — they
reproduce **on the live site**, not just on disk (observed-with-evidence, `curl`):

    poesys.net/data/customers/C2_2.json  HTTP 200  C2_2-INV248  components 24.61  declared 24.62
    poesys.net/data/customers/C5_2.json  HTTP 200  C5_2-INV733  components 936.88 declared 936.87

The R15 WRONG POPULATION diagnosis is correct: the control is real, fires correctly, and
its subject excludes exactly the sub-population where the defect lives.

*(One correction to my own first pass: a naive four-component sum reports 171 failures, not
30. The extra 141 are legitimate catch-up bills carrying `catchup_adjustment_gbp`, a fifth
printed component the control counts and my ad-hoc census had omitted. 30 is the real
number; the control was right and my shortcut was wrong.)*

## What the finding got wrong, and why it matters

**1. The page does not render these three.** The finding's blocking rationale is that
`site/customers/index.html` renders the wider file set. It does not render *these* accounts:
they are absent from `site/data/customers/_index.json` (18 entries) and from
`site/data/customers.json` (13 household groups, the list the page actually fetches). They
are unlinked. They are nonetheless **fetchable**, which is the real reach — published, not
navigable. No published *figure* derives from them (the only other references are prose
notes in `proof.json`/`simplified.json`).

**2. The recommended fix would have fixed nothing.** The finding recommends adding penny
quantisation to `tools/generate_invoice_data.py`. That module sources every printed figure
from the ledger — which foots 0/1557 — and iterates only
`run_output_latest.json::per_customer_lifetime`. All three accounts are absent from it, so
`real_invoices_for` returns `[]` and **the code path never executes for the 30 records**.
The change would have been made, the tests would have passed, and the finding would have
been closed with the defect untouched.

**3. The alternative was a category error.** Option 1 — "extend
`PRINTED_BILL_FOOTS_EXACTLY`'s enforcement to `site/data/customers/*.json`" — treats the
control as a file auditor. It is a **production-time gate**
(`company/billing/pre_bill_validation.py:286`), sitting in the bill-production path.
Pointing it at a second artefact could have turned the 30 red; nothing would have been able
to turn them green, because nothing still produces them.

## The actual defect: orphaned published state

`C1_2`/`C2_2`/`C5_2` are **successor** accounts (`saas/customers.py::SUCCESSOR_CUSTOMERS`) —
activated only when the predecessor churns *and* we win the home-mover competition. They
activated in earlier runs and not in this one. That is legitimate simulation variation, not
a regression.

`tools/generate_customer_data.generate()` wrote a file per account in the population and
**never removed the file of an account that left it**. So the artefacts persisted:

    C2_2.json  last written 2026-07-10      C5_2.json  last written 2026-07-08
    C1.json/C9.json (live)  2026-08-11      → 33-35 days stale, still served

Frozen at whatever the last run containing them produced — which was the era when
`generate_invoice_data` "fabricated invoice amounts by splitting lifetime revenue across
months with a hand-picked seasonal weight curve" (its own docstring). That fabricator
rounded components and total independently. Which is precisely the defect
`PRINTED_BILL_FOOTS_EXACTLY` exists to catch, and had eliminated everywhere it could see.

**So the failing sub-population was not merely unchecked — it was unreachable by
regeneration.** That is the part worth more than the 30 pennies, and it is a different
shape from the one filed: not "the control's path list is too short" but "a conditionally
present entity leaves published state behind when it departs, and nothing owns it after."

## What landed

* **Root cause, mechanism** — `tools/generate_customer_data._retire_departed_artefacts()`:
  after writing `_index.json`, any `<account_id>.json` not in the population is deleted.
  Fails **closed** on an empty population (a broken run is not an instruction to wipe the
  publish path); only this generator's own naming is a candidate, so `_index.json` and any
  hand-added artefact are never touched.
* **The three orphans retired** via that path — not by hand, so the fix is the thing that
  was exercised.
* **R10 class guard** — `tests/tools/test_no_orphan_published_customer_artefacts.py`:
  nothing is served that the publish path does not currently claim, in both directions
  (orphan file, and index entry with no file). Fails closed on a missing/malformed index;
  vacuity floor of 10 accounts so the assertions cannot go quietly true on an empty set.
* **D36's docstring corrected** — it recorded the 21/18/30 exemption as standing.

## Evidence

    BEFORE  publish path  21 accounts  1682 invoices  30 not footing
    AFTER   publish path  18 accounts  1557 invoices   0 not footing
    ledger  (unchanged)   18 accounts  1557 invoices   0 not footing

The two populations are now the same population, which is the honest resolution of a
wrong-population finding — the gap is closed by removing the divergence, not by pointing a
second control at it.

**R15, both directions, control seen red before green.** The guard was run against the real
tree *before* the fix and failed naming the exact three:
`3 artefact(s) on the publish path belong to no account the index claims: ['C1_2', 'C2_2', 'C5_2']`.
Mutation tests restore an orphan of the finding's own shape (`C2_2-INV248`, 24.61 vs 24.62)
and a missing artefact, and assert the guard rejects each; a third proves an absent index
fails closed rather than skipping. `test_generate_retires_a_departed_account_end_to_end`
puts a departed account's file on disk, runs the whole of `generate()`, and asserts it is
gone — the finding's defect as a named killable mutation.

    94 passed  (footing · footing-render · orphan guard · generate_customer_data)

## Left open, deliberately

* **The live site still serves the three files** until the next publish. The retirement is
  in the tree; R2 says committed != deployed, and R11 says the live re-fetch is the proof.
  Next publish removes them; I have not forced a deploy to claim it.
* **Six successors exist (`C1_2`…`C6_2`), three had files.** Whether the current run
  *should* be activating any is a population question for `D_billing_metering`, untouched
  here — I fixed the artefact lifecycle, not the activation rate.
* **One stale prose reference I caused and did not chase.** `tools/scale_probe_10k.py`
  describes "the 22 REAL documents in `site/data/customers/`" in two docstrings; the
  directory now holds 19. It **globs and uses `len(docs)`**, so no behaviour and no
  assertion depends on the number — it is prose only. Left alone deliberately:
  remediation-on-touch, and editing that file would enlist its suite for a word.
* **The same shape elsewhere — checked, and narrow today.** `site/data/` has exactly two
  subdirectories: `customers/` (19 files, now guarded) and `snapshots/` (9, deliberately
  historical and correctly not subject to this rule). So there is no second instance to
  sweep right now. The rule to carry forward is the general one — *a publish-path
  directory written per-entity from a varying population needs a retirement path and an
  orphan guard, or it accumulates served state nothing owns* — which applies to the next
  such directory created, not to an existing one.
