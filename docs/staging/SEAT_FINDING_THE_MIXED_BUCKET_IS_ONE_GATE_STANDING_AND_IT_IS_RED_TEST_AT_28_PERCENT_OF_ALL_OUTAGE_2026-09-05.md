**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The MIXED bucket is ONE gate standing, and it is RED TEST at 28.3% of all publish outage

**Measured:** 2026-09-05, delivery seat, against the shared tree's live
`docs/observability/sim-runner-log.md` (446 publish cycles, 38 bounded episodes). Re-derivable by
running `python3 -m tools.commit_refusal_attribution --log <the shared tree's copy>`; the committed
copy is truncated at 2026-07-17 and the module refuses it.

**The pre-registration is
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_MIXED_BUCKET_IS_STANDING_ON_2026-09-05.md`,
filed as d64384443 — a separate commit, landed before a line of the classifier existed.** Its three
predictions and six controls are graded below as written, including the one that was wrong.

## The answer

**`MIXED` was hiding a single gate, and it is the largest driver of publish outage in the log.**

The published by-cause table's largest *named* row is the level-promotion gate at 18.2h, 7.6%.
Underneath `MIXED`, RED TEST holds **67.8h of BRACKETED interval time — 37.9% of MIXED outage and
28.3% of ALL bounded outage.** It is nearly four times the largest row we were publishing, and it
appeared in that table as a 4.0% footnote.

| MIXED outage, 16 episodes, 178.8h, 157 intervals | hours | share | n |
|---|---:|---:|---:|
| **BRACKETED** — same gate both ends, no evidence it cleared | **83.2h** | **46.5%** | 63 |
| **CLEARED-WITHIN** — the far end reached past it, so it demonstrably passed inside | 20.2h | 11.3% | 19 |
| MASKED — a lower rank at the far end; the near gate is unobservable | 17.0h | 9.5% | 13 |
| UNRANKABLE — an end that refuses nothing or names nothing | 37.3h | 20.9% | 46 |
| TRAILING — everything cleared inside; unattributable *by construction* | 21.1h | 11.8% | 16 |

| Per gate — **the two columns are not added** | BRACKETED | CLEARED-WITHIN |
|---|---:|---:|
| **RED TEST** | **67.8h** | 6.1h |
| orphan-ratchet | 5.1h | — |
| site-lane gate | 4.6h | 3.3h |
| level-promotion gate | 3.7h | 2.8h |
| finding-class consolidation | 1.5h | 7.9h |
| scope-evidence ratchet | 0.5h | — |

A floor on a gate that stayed red and a ceiling on a gate that went green are opposite quantities
and their sum is not a quantity, so they are never one column. Neither is "how long the gate was
red", which the log cannot say.

## The three predictions, graded as written

1. **"A named gate can be put on the majority of MIXED outage" — over 50%. HELD at 57.8%.**
   Refutation was set at a residue ≥ 50%; the residue is 42.2%.
2. **"The largest named gate is RED TEST" — by BRACKETED hours. HELD, and not narrowly:** 67.8h
   against 5.1h for the next row. The document named the way this could fail — the level-promotion
   gate's 18.2h median as a solo cause outweighing many short RED TEST intervals — and it does not:
   level-promotion holds 3.7h inside MIXED.
3. **"BRACKETED exceeds CLEARED-WITHIN" — one gate standing, not gates queueing. HELD at 4.12:1**
   (83.2h against 20.2h).

Prediction 3 is the one that changes what gets built, and it was written so both answers were
possible. **The label `MIXED` reads like a queue and the log says it is not one.** A queue — each
gate clearing in turn and the next firing — would put its time in CLEARED-WITHIN, and the remedy
would be to run the chain further or in parallel so the whole red set is visible at once. That
remedy would be competing for 11.3%. What is actually there is one gate sitting red across most of
the interval time, and the remedy for that is to work the red.

## What this composes with, and why it is now one picture

Four measurements now agree and none was designed knowing the next:

- 82.9% of multi-cycle outage is redness **standing**, against a 17.1% upper bound on the retry
  rhythm (988270c2e).
- 77.8% of same-gate re-refusals are the **identical complaint**, and one red was retried 24 times.
- Of seven SAME TEST re-arrivals, **zero demonstrably re-broke** — all seven are persistence.
- And now: the 74.6% that carried no cause is 46.5% one gate bracketed, and that gate is RED TEST
  at 28.3% of everything.

**A red test nobody is working, retried on a rhythm that cannot clear it, is the single largest
cost in the publish path — and no mechanism anywhere acts on it.** The cadence lever is ruled out
by measurement rather than by argument, and this names the thing the other lever must point at.

## The residue, named rather than bucketed

42.2% is not attributed and it is not a bucket. **20.9% is UNRANKABLE, and the largest single cause
of that is the publisher's own `behind_origin` cycles**: of the 46 unrankable intervals, 27 have a
non-refusal attempt at one end and 26 at the other. A `behind_origin` attempt refuses nothing, so
it carries no rank and blinds the interval either side of it. That is a property of the instrument
and of the publisher, not of the gates, and it is the first candidate if this attribution is ever
wanted tighter. The remaining unrankable ends are `UNNAMED` (6 and 6) and `UNATTRIBUTABLE` (3 and
3). TRAILING's 11.8% is unattributable by construction, exactly as the single-cycle 100% tail is.

## The controls, and the one that was wrong

Five of the six pre-registered controls hold. All six are in
`tests/tools/test_commit_refusal_attribution.py` and nine mutations were killed by them.

- **C1 — the partition is exact.** PASS on all 16 episodes, to the second, re-derived from the
  members' own timestamps.
- **C2 — the classes partition the intervals.** PASS: 63+19+13+46+16 = 157, and the class hours sum
  to 178.8h.
- **C3 — every class is REACHABLE.** PASS, all five reached on the live log and each pinned to the
  interval it was built for in one control over the whole partition. This is the control that
  killed four of the nine mutations, including a classifier that never returns BRACKETED and one
  that swaps CLEARED-WITHIN with MASKED.
- **C5 — a BRACKETED interval's ends are consecutive attempts.** PASS — but see the tautology note
  below; what actually protects the claim is that walking `members` rather than `refused` turns an
  interval containing a `behind_origin` attempt into two UNRANKABLE intervals instead of one wide
  BRACKETED span, and *that* is mutation-proven.
- **C6 — no gate is attributed more than its episode's outage.** PASS.
- **C4 — "MASKED episodes equal `ordering_report`'s established episodes, in both directions".
  THE PRE-REGISTRATION ASKED FOR THE WRONG RELATION.** The correct relation is a **subset**, and
  the strict direction is real: **two established episodes have no MASKED interval at all**
  (2026-08-27 05:21 and 2026-08-31 15:00). `ordering_report` walks the ranked causes with unranked
  cycles *skipped*, so it sees a backward step across an unattributable cycle; an interval with an
  unranked end is UNRANKABLE, so the interval view cannot. Both are right about different
  questions. **Asserting the equality I pre-registered would have been a red control over a sound
  measurement**, and the fix is the subset plus the gap as a reported quantity — not a smoothing.

**Two controls are pinned tautologies and are labelled as such in the code rather than trusted.**
Mutating them kills nothing, and I established that rather than assuming the flattering reading:

- The `adjacent` flag cannot go false. An episode is a maximal run of *consecutive* non-landing
  cycles, so members are adjacent by construction. It survives as a canary over a future change to
  `_episodes` and is explicitly not what carries C5.
- `masked_not_established` is empty by theorem, not by observation. Two adjacent ranked members are
  also adjacent among the ranked causes, and `rank(b) < rank(a) ≤ peak`, so every MASKED interval is
  necessarily a backward step against the running peak — given both routes read one rank table,
  which they do. It fires only if those tables ever come apart. The half that carries information
  is `established_without_masked`, and that half is mutation-proven twice.

## What this licenses

**Nothing yet, and that was pre-registered.** The deliverable of this turn is the attribution and
the residue named honestly. No cadence change: the preceding pre-registration pre-refused one and
its prediction held at 17.1%. No change to the `MIXED` episode field, which is correct — this sits
beside it. What it does decide is the *subject* of the next mechanism, which four turns of
measurement had left unnamed: **a standing red test, and not the chain, not the cadence, and not
"mixed causes".**

## Where the derivation lives

`tools/commit_refusal_attribution.py::interval_report` and `::interval_attribution`, printed by the
module's own `main` as the `=== WHAT IS THE **MIXED** BUCKET STANDING ON? ===` section, so every
figure above is re-derivable rather than quoted. Nine controls in
`tests/tools/test_commit_refusal_attribution.py`, each mutation-proven to fire on its own defect,
and the two that cannot fire named above as the tautologies they are.
