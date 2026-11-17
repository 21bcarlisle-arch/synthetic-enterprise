**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A domain-invariant-refused book is regraded every cycle, and each refusal redraws the wedge (2026-11-17)

**What happened.** The f7e17b1316 book has been refused by the domain-invariant gate 40 times
(`sim-runner-log.md`, first at 16 Nov 09:11Z, latest 17 Nov 11:37Z, about every 20 minutes today).
Each refusal shows the same rows: INV_OVERDUE_WITHIN_PAGE_BALANCE 7, INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5.
`process_run_complete` returns `EXIT_DOMAIN_INVARIANT_REFUSED` and leaves the marker
(`run_complete_20261116T070501Z.md`, and `..._031305Z.md` beside it) in `docs/staging/`. So the next
cycle regenerates the whole site layer (~14 min) and grades the same book again. Each refusal is
counted as another episode failure (45 by now), and the wedge doorbell fires on that count. A
worker tick is drawn to diagnose a cause that `SEAT_FINDING_THE_VAT_ROWS_LAST_BREACH_..._2026-11-16.md`
already graded, and `SEAT_FINDING_D5_SWITCH_ON_PRE_REGISTRATION_ROWS_4_AND_7_2026-11-17.md`
already predicted would keep refusing.

**Why the retry exists, and the narrow case it serves.** A regrade can only change the verdict
when the grader's inputs change. Those inputs are the runner, `DOMAIN_INVARIANTS.yaml`, the
exceptions register, and the customer-page generator that writes `site/data/customers`. The book's
own ledger does not change. While none of those has moved, a retry is the same experiment repeated.

**Proposal (not built here, so the hot publisher is not touched in a bounded tick).** On
`EXIT_DOMAIN_INVARIANT_REFUSED`, record the marker plus a hash of the grader inputs. On the next
cycle, if both match, skip the marker with one log line and do not count a new episode failure.
A grader change, or a new book, re-admits it. The control covers the whole partition: the same inputs
skip, a changed exceptions register regrades, and a new marker regrades.

**What actually ends this episode.** A book built on HEAD carrying 341df4965, the D5 switch-on. Its
admission is `background/next_book_requires.yaml`. Its slot is `d5book-pause-watch.service` (active,
waiting for step 6's pair-2 boundary). sim-runner is currently deferring cycles to
`longjob-value-test-step-6-flag1` on memory.

**Not established.** Whether `_031305Z`'s marker is the same book (its refusals are counted in the
40 above), and whether the regen holds memory the D5 book's admission needs.
