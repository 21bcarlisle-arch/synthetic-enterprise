# D18 — the supplier already holds half the answer, weeks late and only sometimes

**Atom:** `D18_confounder_observable_channel` · **Lane:** D_billing_metering · **Level:** 0 → 2
**Built:** 2026-08-09 (worker tick) · **Minted by:** the D14 build, as a REGISTERED SIMPLIFICATION
**Pair:** `W2_8_self_rationing` ↔ `C10_self_rationing_detection`
**Files:** `company/crm/self_rationing_detector.py` (COMPANY), `tools/couple_w2_8_c10.py` (HARNESS),
`tests/test_c10_self_rationing_detection.py`

---

## The simplification this pays

D14 gave the world hard negatives — a house move, a void, a retrofit, a voluntary cut, each
cutting a household's meter with no hardship behind it — and deliberately kept every **cause**
as answer key, because the company-side detector was not D14's to change. It registered the
consequence in its own module docstring rather than hiding it:

> Hiding them makes detection strictly HARDER than reality, so the measured false-flag rate is
> an UPPER bound, never flattering. The observable channel is a follow-on atom, not a silent
> omission.

That upper bound was **0.0560** of the settled negative. This atom builds the channel and asks
the question the bound could not answer: **how much of that could a real supplier actually have
explained away?**

## What crosses the wall — a RECORD, never the cause

The thing the atom warned against was a channel that hands the detector `DropConfounder`. That
would score the detector ~100% on exactly the cases D14 built to be hard. What crosses instead is
`AccountRecord` — a supplier-held record with a type, an **effective date** and a **received
date** — through three gates:

| gate | what it does | why it is not a label |
|---|---|---|
| **Coverage** | only some events leave a record at all | a **voluntary cut leaves NO record in any system, ever** — a whole class of hard negatives stays permanently unexplainable |
| **Latency** | a record counts only once `received_date <= as_of` | CoT is supplier-internal and "industry-wide, nobody is told"; the occupier tells us in week 1 or month 6, and the tail arrives after the detector has already had to decide |
| **Meaning** | a CoT/void record **invalidates the baseline**, it never clears the case | the history is the previous occupier's, so no drop is *observable*; the incoming occupier may be rationing and we simply cannot see it |

An install record is different in kind: it adjusts **expected** consumption by the **deemed**
saving on the company's own file (a scheme constant, never the home's realised cut — the
deemed-vs-actual performance gap is real and stays), so a household that cut *further* than its
retrofit explains is **still flagged**.

### Coverage and latency shapes (R13 curriculum, [L], fixed before the rates were read)

| cause | record | coverage | latency band |
|---|---|---|---|
| `HOUSE_MOVE` | `change_of_tenancy` | 0.55 | 7–240 days |
| `VACANCY` | `void_notification` | 0.35 | 14–150 days |
| `EFFICIENCY_RETROFIT` | `own_scheme_install` (deemed 0.20) | 0.30 | 1–75 days |
| `VOLUNTARY_CUT` | — none, ever — | — | — |

Anchor: `docs/staging/ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md` — CoT is
supplier-internal with no industry flow, and "discovery latency (occupier tells us in week 1 vs
month 6) is itself a distribution with financial consequences". The install coverage is roughly a
supplier's share of a national programme. All three are curriculum shapes, never tuned to a rate.

## What it measures — explainABLE vs explainED

Every run now scores **two companies on one population**: with the records (`flagged`) and
without (`flagged_unaided`, the pre-D18 company). Reference population `n = 4000`, deterministic:

```
records that EXIST                 228   (CoT 192, void 26, install 10)
...that had ARRIVED by as_of       187   (CoT 152, void  25, install 10)

false flags, pre-D18 company       210 of 3752   = 0.0560   <- the UPPER bound D14 registered
  ...a supplier COULD explain       90 of 210    = 0.4286   <- the ceiling
  ...it ACTUALLY explained          70 of 210    = 0.3333   <- what the records bought
  THE DISTANCE                                     0.0952   <- coverage that arrived too late
false flags, published company     140 of 3752   = 0.0373

THE PRICE, not a footnote:
real rationers explained away        9
recall                             0.6878 -> 0.6439
harm-weighted miss                 0.3094 -> 0.3613
published pair GAP                 0.1787 -> 0.1993
```

**The ceiling is 0.43, not 1.0**, and that is the headline finding: even a supplier reading every
record it holds can explain away well under half of what it wrongly flags, because the largest
single confounder class (a household that could afford its bill and chose to use less) leaves no
record anywhere. The remaining distance — 0.0952 of the false flags — is pure **latency and
coverage**: the record exists, and the company does not have it yet.

## R12, stated before the number is read

The published GAP got **worse** (0.1787 → 0.1993) while the company got a channel that a real
supplier has. That is not a contradiction and it is not a reason to touch anything:

- The pair's gap is the unweighted mean of two **rates on very different denominators** (205 truth
  vs 3752 negatives). Trading ~70 false flags (1.9pp of a big denominator) for ~9 misses (4.4pp of
  a small one) moves the mean up.
- By any cost-weighted reading the trade is favourable; by this instrument it is not.
- **The fix for disliking that is a cost-weighted instrument argued on its own merits, never
  switching metric because this one moved the wrong way.** The rate is a diagnostic (R12). The
  channel was built because a real supplier holds those records, decided blind to what it does to
  the gap — and the gap moved against the atom that built it, which is the evidence that it was.

The channel's cost is also a **real-world harm path, not an artefact**: a vulnerable household
that moves house becomes invisible to consumption-based detection until a new baseline builds.
That is worth having in the world explicitly rather than accidentally.

## R15 — both obligations the atom set, and the guards on the guards

The atom named two mutations. Both exist, and both are differentials against the *same* textbook
signature (2900 → 1200 kWh, below floor, clean payments, baseline present) so a pass can only be
the record's doing:

1. **Not a label leak.** `test_mutation_a_record_that_has_not_arrived_explains_nothing` — the
   event happened, the record exists, it reaches us after `as_of`, and the household is **still
   flagged**. Plus, on the population: the false-flag rate stays clear of zero, the explainable
   *ceiling* is strictly below 1, and `n_records_arrived < n_records_exist` (without which latency
   would be untested by the very measurement that cites it).
2. **The channel moves the rate.** `test_mutation_the_channel_moves_the_false_flag_rate` — records
   off reproduces the pre-D18 company exactly (`false_positive_rate_unaided`,
   `n_flagged_unaided`), and the aided rate is strictly lower.

Also proven: an install record does **not** blanket-clear a deeper cut; an install record with no
deemed figure adjusts **nothing** (a missing number is not a free pass); a deemed saving is clamped
so it can never swallow an arbitrary drop; a record predating the baseline period explains the
baseline, not the fall; `as_of=None` means **no record has arrived** (an unknown clock never
silences a vulnerability flag); a voluntary cut yields no record across 2000 swept ids; and all
three record types both occur and arrive in the scored population.

The two structural invariants live in `check_channel_invariants` — the function the real build
calls — so the mutation test exercises the **shipped** control, not a copy of it:

- a record may only ever **suppress** a flag (it can never create one);
- nothing is explained away with **no record behind it**.

## What changed in the published record

- `missed_because_no_baseline == missed` is no longer true and the test that asserted it is
  **replaced, not repaired**: misses now decompose into the meter-coverage blind spot and the
  channel's own price, both counted, both asserted non-zero.
- `false_positive_rate` on this pair now describes the **record-reading** company. The pre-D18
  figure travels beside it every run as `false_positive_rate_unaided` — 0.0560 keeps its meaning
  as the upper bound it always was, rather than being quietly restated.

## L3 not claimed

No Expert-Hour pass on the changed detector, and the coverage/latency shapes are curriculum
figures that have not been reviewed against a second source. The tick that adds a channel is not
the tick to certify its calibration.
