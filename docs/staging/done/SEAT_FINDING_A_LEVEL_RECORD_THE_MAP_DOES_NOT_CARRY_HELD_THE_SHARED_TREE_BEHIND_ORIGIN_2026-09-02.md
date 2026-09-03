# [SEAT FINDING] A level record the map does not carry sat uncommitted for three days and held the shared tree behind origin

**Severity:** RECORDED (the line is preserved verbatim below and removed from the shared tree so it can advance; the contradiction it names is not mine to resolve)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02 while clearing the publish wedge the director asked for.

## Class registration

`uncommitted_and_orphaned_work`, and it is the fourth instance today after the census overlay work,
the DD/EAC repair and the DD level move. Also touches `controls_that_cannot_fail`: an append-only
ledger with one lane's uncommitted line is a **structural** block on every other lane's advance,
and nothing said so.

## What is actually true

`docs/observability/gate_authorizations.jsonl` carries **two** `LEVEL_UP_SELF_CERTIFIED` records
for `PB3_book_growth_as_earned_outcome` at level 2:

| when | state | provenance HEAD |
|---|---|---|
| 2026-08-25T17:32:20Z | **landed**, on origin | — |
| 2026-08-30T10:51:20Z | **uncommitted**, in the shared tree only, for three days | `357568b87` |

And `docs/design/maturity_map.yaml` says `PB3_book_growth_as_earned_outcome: level_current 0`.

So **the ledger asserts level 2 and the map says 0**, and the landed 2026-08-25 record already
makes that contradiction live on origin. The uncommitted line does not create it; it repeats it
with different evidence. There is no PB3 edit in the working tree's map either — checked, not
assumed.

## Why it mattered today

The publish path commits **from the shared tree**, so it cannot publish while that tree is behind
origin (`_divergence_refusal`). The tree could not advance: `git merge --ff-only` refuses to
overwrite a locally modified file, and the moment any lane landed a ledger line — as the DD salvage
did — this uncommitted line made `gate_authorizations.jsonl` exactly that file.

**An append-only ledger turns one lane's uncommitted line into a hard block on every other lane's
advance.** Not a slow one, not a warning: the tree simply stops moving, and the cause is a file
nobody is looking at. This is the same shape as the census lane's two staged files and the DD
lane's uncommitted map edit, three times in one day on three different files.

## What I did, and what I did not

**Did:** removed the line from the shared tree's working copy so the tree can reach origin, having
first preserved it verbatim here. Nothing is lost — this document is the artefact.

**Did not:** land it. A `LEVEL_UP` record certifies a move; landing it inside another lane's commit
would put a claim on the record that no map change backs, and the lane that made the measurement is
gone. Its own author left it unstaged deliberately, and the DD lane refused to sweep it into their
commit for exactly this reason and were right to.

**Not resolved, and named rather than quietly closed:** whether PB3 is at 0 or 2. Two ledger records
say 2, the map says 0, and I have not measured the atom. That is a question for whoever draws PB3,
and the evidence they need is in the provenance below.

## The line, verbatim, so re-landing it needs no archaeology

```json
{"atom": "PB3_book_growth_as_earned_outcome", "action": "LEVEL_UP_SELF_CERTIFIED", "level": 2, "ts": 1788087080.2895205, "authorized_by": "agent_self_certified", "channel": "self", "provenance": "PB3 0->2, worker tick 2026-08-30, on evidence measured this tick at HEAD 357568b87. (b1) arrival stream FIXED, the company's own market position alone moves book size in BOTH directions; (b2) arrival stream EMPTIED, the book still grows -- both proven in tests/simulation/test_net_new_acquisition.py with the null control test_b1_the_prospect_STREAM_is_identical_across_the_three_price_positions and four MUTATION controls; 74 passed with tests/tools/test_couple_pb3_book_growth.py this tick. (c) no step change that is not a modelled acquisition or loss event: landed 9d21b2a1c. (d) belief-vs-truth gap RE-MEASURED this tick and the ledger refreshed: gap 0.830 over ten market-decided years, nine of them planning on a learned rate (was a five-day-stale 1.228 that the Proof door rendered red as `worse_than_blind`). STOPS AT L2, NOT THE DRAWN L3, on exit (a): the competitor field is wired on the LOSS side only -- simulation/customer_events.py reads competitor_reference_rate_gbp_per_mwh and B10_competitor_switching_response is at L3 -- while the WIN side still has no rival counter-offer (simulation/net_new_acquisition.py:66 declares it, and neither that module nor simulation/acquisition_funnel.py imports competitor_reference). A book whose down is a rival and whose up is the funnel's own leakage is not yet won and lost against the SAME market, which is what L3 would claim."}
```

To re-land it: append that line to `docs/observability/gate_authorizations.jsonl` **in the same
commit as the map move it certifies**, which is what was missing.

## The general point, which outlives this line

Three lanes died today holding work in the shared index, and each one blocked the machine in a
different way — a red test whose fix was on origin, a level claim whose source was not landed, and
now a ledger line. The common shape is not carelessness: **a shared working tree makes every lane's
unfinished work into every other lane's blocker, silently, and the block is discovered from a
refusal that names a symptom rather than an owner.** Worth a mechanism, and I am not proposing one
from inside an incident.
