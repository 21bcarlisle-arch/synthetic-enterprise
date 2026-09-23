**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `rerun-the-arrivals-on-value-arm-leg-now-the-crash-is-fixed`

# The pairing class is empty, and the live class is that 36 of 38 registers refuse with a bare key

*The survey owed by §6 of the 2026-09-19 finding is done. **Zero** live call sites have their
registration in a narrower branch than their use — and that zero is worth reading because the walk
is proven to classify the pre-repair `run_phase2b` site NARROWER and the repaired one PAIRED. What
the survey found instead is a class nobody had named: **36 of 38 raise-on-missing accessors refuse
with a bare `KeyError`**, one names its reason, and the bare refusal is the entire reason the
2026-09-19 crash cost an 880s pass to diagnose rather than a traceback to read. **Three of my four
pre-registered predictions are refuted and all three for one reason, which is mine.***

---

## 1. The premise, re-measured first — and the drawn half of it was already spent

The item asked for two things. **The first is done and was done before this turn started.**

| the item's ask | state at draw time |
|---|---|
| re-run the arrivals-ON value-arm leg | **DONE** — `..._on_20260919b.json` on disk, 1,491s |
| answer the pre-registration, prediction left uncorrected | **DONE** — landed `db00d334c` |
| archive the repeating-alarm doc, correct its severity | **DONE** — in `docs/staging/done/` |
| §6 Owed: survey the `advance`-like class | **NOT DONE** — this document |

`3a8d15185` is an ancestor of `origin/main`, the ON leg completed, and
`SEAT_RESULT_MINTING_ARRIVALS_ADDS_SEVEN_DECISIONS_...` answers the widening question:
`decisions_that_existed` 107 → 114, scored 104 → 107, null half-width 0.11280 → 0.11164, and the
rank leg got **the same, not cheaper**. Nothing in this turn re-derives any of that. The claim was
held under this same id by the invocation that did it, which is why the draw flagged a duplicate:
**it is the same work, and only its last bullet was outstanding.**

*So this document discharges the part that was actually owed, and says plainly that the rest was
not.* The crash is gone, the number is published, and the finding's own closing sentence — *"I fixed
the pairing, not the class"* — is what remained.

## 2. The defect class, and the answer

A **raise-on-missing accessor** reads `self.<dict>[key]` on a dict its own class registers into.
Reaching it unregistered raises and kills the caller. The **defect** is a *call site* whose
registration is gated by a strictly narrower condition than its use — at `run_phase2b.py:2496` the
registration sat inside `if old_decision_leg_rate is not None:` and the `advance` sat outside it, so
an account opening on the default tariff reached it unregistered and died.

`tools/conditional_registration_survey.py` walks `simulation/`, `company/`, `saas/`, `background/`
and `tools/`, binds each receiver to a type, and compares guard chains.

| | count |
|---|---:|
| register-shaped classes | 25 |
| raise-on-missing accessors on them | 38 |
| call sites with a typeable receiver | 16 |
| — **NARROWER** (the defect) | **0** |
| — PAIRED | 2 |
| — UNSETTLED (registration not visible in the enclosing function) | 14 |
| call sites whose receiver could not be typed | 11,311 |
| **accessors refusing with a BARE `KeyError`** | **36 of 38** |

**The answer to the question §6 asked — "does any OTHER route into that advance exist for an account
with no struck rate" — is no, on the evidence this walk can produce.** The `advance` at
`run_phase2b.py:2521` is the only bound call site of that accessor in the tree, and it is PAIRED.

## 3. Why the zero is readable, and the one leg that makes it so

**A survey reporting zero because it cannot see is void, not clean**, and this repo has shipped that
shape. So `--prove` runs the same walk against `simulation/run_phase2b.py` at `3a8d15185^` and at
HEAD and refuses unless they classify differently:

```
pre-repair  simulation/run_phase2b.py@3a8d15185^:2496  NARROWER
            "every registration is gated by old_decision_leg_rate is not None and the use is not"
repaired    simulation/run_phase2b.py:2521             PAIRED
```

It names the actual cause, not a proxy for it. **P4 CONFIRMED**, and it is a precondition on
publishing anything above: the tool exits non-zero if it fails, and
`tests/tools/test_a_register_refuses_by_name_and_the_survey_can_see_a_pairing_defect.py` pins it.

**The proof earned its keep on this module's own first draft.** The walk read the repair's
`if get_journey(x) is None: register_customer(x)` as a *narrowing* guard and reported the REPAIRED
site as the defect. That guard cannot narrow — it is true exactly on the paths where the use would
otherwise raise. The proof caught it before any number was written down, and the fix is in the walk
(`_is_idempotence_guard`), not in the proof.

**Two further false positives were fixed the same way, not annotated around:**

* `_FunctionScan._keys` was flagged twice. Its read is `{self.symbols[n.id] for n in ... if n.id in
  self.symbols}` — membership-guarded, it cannot raise. Excluded at the catalogue (`_membership_guarded`).
* `TenancyChangeCoupler._changes_for` was flagged at both `observe_move_*`. There the **use precedes
  the registration**: look first, `_open_change` only for what the look did not find. A registration
  below the use cannot make it safe, so it no longer counts — which leaves those two sites
  **UNSETTLED, not clean**, and that is the honest verdict: their key set comes from a companion
  index (`self._by_key.get(key, [])`) this walk does not follow. By hand, they are safe for that
  reason; the walk does not claim it.

## 4. THE LIVE CLASS: 36 of 38 registers refuse with a bare key

This is the finding, and it was not what I went looking for.

```
KeyError: 'SYN-2016-008'
```

That is what 880s of a value-arm pass produced on 2026-09-19. The key, and nothing about which book
refused, what should have registered it, or whether the book was empty or merely missing one
account. Exactly one accessor in the tree does better — `HomeRegistry.get_profile`, which raises
`KeyError("No property registered for account {}")` from the identical shape, and the same failure
off that accessor is read from the traceback in seconds.

**CLAUDE.md asks for refusals that name their reason.** On a raise-on-missing accessor that is not
decoration; it is the whole diagnosis, because these fire deep inside long runs where the cheap
evidence is the traceback and the expensive evidence is re-driving the run.

**`ChurnJourneyRegister.advance` is fixed in this commit** — the instance with a measured cost, and
the one whose caller the earlier finding already repaired:

```
SYN-2016-008 has no churn journey: advance() was reached before register_customer().
1 accounts are registered.
```

**The other 35 are NOT fixed and are not claimed.** They are listed in
`docs/observability/conditional_registration_survey.json` under `refusals`. Naming them all is a
35-file diff across `company/` touching several lanes' working copies, and it is a worse trade in
one turn than landing the instrument that can find them again. *Stated as owed, not as done.*

## 5. Three predictions refuted, and the reason is the same one and it is mine

*Filed at `docs/staging/records/PREREG_HOW_MANY_ADVANCE_LIKE_CALLS_HAVE_A_REGISTRATION_IN_A_NARROWER_BRANCH_2026-09-21.md`,
before the instrument existed. Left standing, not revised.*

| # | predicted | observed | verdict |
|---|---|---:|---|
| **P1** | call sites: point 45, band **25–80** | **16** | **REFUTED** — below the band |
| **P2** | NARROWER: point 2, band **1–5** | **0** | **REFUTED** — below the band |
| **P3** | UNSETTLED: point 35, band **15–65** | **14** | **REFUTED** — below the band, by one |
| **P4** | the walk fires on the known instance | pre 1 / post 0 | **CONFIRMED** |

**All three misses are the same error: I predicted a count before deciding how the instrument would
count.** The bands were priced against a walk that keyed accessors by method NAME — and the first
run of exactly that walk returned **11,330 call sites and 11,324 UNSETTLED**, because `get`, `add`
and `record` are accessor names on these books *and* on several thousand unrelated objects. That
number is not above P1's band in any informative sense; it is a question asked so loosely the answer
carries none. Binding receivers to types took the same tree from 11,330 to 16.

**So P1's "true" value was 11,330 or 16 depending on a decision I had not made when I predicted it,
and the prediction was never about the world.** A count prediction is a prediction about an
instrument, and pre-registering one before the instrument is specified pre-registers nothing. That
is worth more than the three ticks it cost: *the pre-registration discipline needs the measurement
DEFINED, not merely the answer unknown* — which is this project's own "before measuring a thing, say
what it is", arriving from a direction I had not seen it come from.

**P2 is the substantive refutation and it is the good kind:** I predicted 1–5 live instances, warranted
on "a path no world we run today takes cannot have crashed yet". The warrant was sound and the answer
is zero. What it means is narrower than it looks — see §6.

## 6. What may NOT travel out of this

**"Zero NARROWER" is not "no account can reach an accessor unregistered."** It is: no call site *with
a typeable receiver* has its registration under a strictly narrower guard *in the same function*. The
14 UNSETTLED sites register somewhere this walk does not look, and that is ordinary rather than a
finding — but it is not a clean bill and no sentence here upgrades it to one.

**The 11,311 untypeable receivers are a blind spot, counted rather than dropped.** 11,290 of them are
bare `.get(` on objects that are mostly not registers at all. Of the distinctive names, one is a real
register arriving as an untyped parameter — `decarb_recommender.recommend_from_registry(home_registry,
...)` — and it is the one accessor in the tree that already names its refusal, so it fails readably.
*A survey that silently discards its own uncovered set reads as "covered everything"; the count is in
the artefact and in a control that reds if it stops being collected.*

**36 of 38 is a count of accessors, not of defects.** A bare `KeyError` on an accessor nothing can
reach unregistered costs nothing. The number says how expensive the *next* one will be to diagnose,
and that is all it says.

## 7. Provenance and controls

* Instrument: `tools/conditional_registration_survey.py`. Artefact:
  `docs/observability/conditional_registration_survey.json`.
* Controls: `tests/tools/test_a_register_refuses_by_name_and_the_survey_can_see_a_pairing_defect.py`
  — four legs. **Three mutations run, each fired on its own leg and on no other:** restoring the bare
  subscript in `advance` (reds the named-refusal leg); blinding `_guard_chain` to return `[]` (reds
  the proof leg); dropping the `unbound` append (reds the blind-spot leg). The partition leg asserts
  the register can SERVE a registered account before anything asserts it REFUSES an unregistered one
   — a guard that refuses everything passes every test of what it refuses.
* The blind-spot leg is keyed to the property (the uncovered set is counted and non-empty), not to
  today's 11,311, which moves with every call site anyone adds.

## 8. Disposition of the finding this discharges

`SEAT_RESULT_THE_WORLD_THAT_MINTS_ARRIVALS_CANNOT_FINISH_A_VALUE_ARM_PASS_AND_THE_ALARM_THAT_SAID_SO_HAD_NO_CAUSE_2026-09-19.md`
is **BLOCKING** and all three bullets of its §6 Owed are now discharged: the ON leg ran and is
published, the alarm is archived, and the class is surveyed. **It is archived to
`docs/staging/done/` against this commit.**

Its BLOCKING severity was correct when written — a value-arm pass could not complete — and the
condition is gone. This document is **LATENT**: a real defect class (36 bare refusals) that
invalidates no published figure and no control's verdict.
