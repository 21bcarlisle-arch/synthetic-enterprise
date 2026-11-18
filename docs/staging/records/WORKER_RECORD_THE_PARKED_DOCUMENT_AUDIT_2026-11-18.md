**Severity:** RECORDED · **Lane:** H_harness · **Atom:** `H48_the_parked_document_audit_is_the_idle_hole_at_scale`

**Knowledge:** none -- a harness audit of the staging queue's parked documents, not domain research

# The parked-document audit: 22 documents, one question each (2026-11-18)

This is the audit the director commissioned on 5 Sep
(`docs/staging/done/DIRECTOR_RULING_JULY_STEERS_RECONCILED_AND_PARKED_AUDIT_2026-09-05.md` §3). He wrote
then that 121 documents sat in `in_progress/`. Today 22 do (plus an August symlink, `.claude`, which is
not a document). The other 99 were drained piecemeal between those dates, and that drain was not
audited here. Each of the 22 was asked the ruling's one question: **is the reason this was parked
still true?** The answer was checked against the tree, not against the document's own header.
Each document now opens with a dated `H48 PARKED-DOCUMENT AUDIT` line that carries its evidence.

## Counts (denominator: the 22 documents in `in_progress/` at 2026-11-18)

| Disposition | n | Where it went |
|---|---|---|
| DONE | 4 | `done/` |
| SUPERSEDED | 6 | `done/` (one of them is an advisor input rejected with its reason) |
| UNBLOCKED | 9 | 8 re-staged to the staging root, where the queue draws them; 1 (item 2) routed by `finding_classes --consolidate` into the `publish_gate_and_wedge` class register as its 101st instance |
| STILL PARKED | 2 | stay, with the condition re-stated and dated |
| DIRECTOR | 1 | stays; raised in `for_the_director` |

Of the 22 parks, 19 (86%) were no longer true. That rate rhymes with the director's 3 of 3 sample
on 5 Sep, and it is the idle-hole class at scale.

## The UNBLOCKED work

1. **Staging-root resurrection: name the writer.** The instrument has fired 97 times, the latest at
   03:47 today, and nobody has read its records.
   *Corrected the same day, after reading them: 97 rows were not 97 occurrences. 95 were fresh
   runs finishing while a gate ran (no `done/` twin). The one return with a twin, logged twice, was
   a hand re-offer by copy (f000ad71dc). The finding is closed in `done/`, and the instrument now
   records only twin-bearing arrivals.*
2. **Memory: measure a gate phase's peak with `ru_maxrss`.** Unbuilt. It bears on today's stale
   census, which the memory governor deferred for budget. The class gate routes it to
   `reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` as an instance, not to the root.
3. **Featured household: prefer one still supplied.** `DRILLDOWN_ID = "C1"` is still hardcoded.
4. **Projection feed: rewritten every run, and no page reads it.** Re-wire it to a page or unwire it.
5. **Proof door: a live site tripwire against its ledger.** Its blocker is recorded as landed.
6. **EPC register: staleness and absence carry information.** Knowledge work. The agents for
   published sources now exist.
7. **Capability index §2-§4: the demo, the blind check, and splitting exhaust from record.** `AO8` is
   not on the map, so the next draw mints or rejects these.
8. **Harness page method account, and the PB3 growth path.** `PB3` is not on the map, so the next
   draw mints or rejects it.
9. **The 15 level re-verifications from the July reversibility mint.** Each is redone, or closed
   against today's census grade.

Items 1, 2 and 3 are the ones a reader would notice: a queue writer nobody has named, a census that
cannot run, and a page featuring a household that has left.

## The DIRECTOR list (one item)

- **The repository is still public.** Making it private is his click in GitHub settings. The July
  blocker (deploys at about twice the private Actions quota) is fixed, because deploys now fire only
  on the published files. Asserting copyright on the site needs the legal entity name and a crawler
  decision. Raised as `the-github-repository-is-still-public-gh`, with a recommendation.

## What this audit did not do, said plainly

- Two SUPERSEDED closes rest on a frame change, not on item-by-item verification:
  `WORKER_MINTED_THREE_RULINGS_WORK_BLOCK_DEFECT` items A5-A7, and the re-audit of 9 Aug promotions
  in `WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD`. Each document's own audit line says so.
- UNBLOCKED item 5 rests on the 12 Oct fate line, which was not re-checked.
- The mothball ruling the 5 Sep text names was not among the 22, so it is out of scope.
- **Built in passing:** the one control a parked document asked for that was a single leg,
  `tests/architecture/test_every_hook_command_is_project_anchored.py`. All 11 hook commands pass it,
  and a relative mutant is named by it. That moved `WORKER_FINDING_RELATIVE_HOOK_PATHS` to DONE.

Three re-staged documents carried no `**Severity:**` header, which the root gate requires. They
got one each: BOOK_VALUE got its existing BLOCKING, moved to the top. MEASUREMENTS got LATENT.
The reversibility mint got LATENT, because the census grades levels on its own now and a stale
provenance string does not change a graded level. That last reason is a judgement and is stated
here so it can be refuted.

## How to reverse

Revert the commit. Every document is moved with `git mv` and its audit line is a prepend, so a revert
restores each one byte for byte.
