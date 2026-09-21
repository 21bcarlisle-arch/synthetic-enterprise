**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `rerun-the-arrivals-on-value-arm-leg-now-the-crash-is-fixed`

# PRE-REGISTRATION — how many `advance`-like calls have their registration in a NARROWER branch?

**Filed 2026-09-21, delivery seat, before the survey instrument was written and before any call-site
figure existed.** Checkable: the instrument is `tools/conditional_registration_survey.py` and at the
moment this file was written `ls` returned *no such file* for it, and
`docs/observability/conditional_registration_survey.json` did not exist.

Discharges the third bullet of §6 Owed in
`docs/staging/SEAT_RESULT_THE_WORLD_THAT_MINTS_ARRIVALS_CANNOT_FINISH_A_VALUE_ARM_PASS_AND_THE_ALARM_THAT_SAID_SO_HAD_NO_CAUSE_2026-09-19.md`:

> **Not done here:** whether any OTHER route into that advance exists for an account with no struck
> rate. I fixed the pairing, not the class; a survey of every `advance`-like call whose registration
> sits inside a narrower branch is a separate pass and is not claimed.

---

## 1. The class, stated before it is counted

A **raise-on-missing accessor** is a method that reads `self.<dict>[<key>]` in a Load context on a
dict the same class writes in a `register`-like method. Reaching it with an unregistered key raises
`KeyError` and kills the caller. `ChurnJourneyRegister.advance` is one; the AST walk over
`simulation/`, `company/`, `saas/`, `background/` and `tools/` finds **28 register-shaped classes**
carrying at least one. *That denominator is measured, not predicted — it was in hand before this
file was written, and no prediction below is about it.*

The **defect** is not the accessor. It is a **call site** where the pairing is conditional: the
registration that makes the accessor safe sits inside a strictly narrower guard than the accessor
call itself, so some path reaches the accessor unregistered. At `run_phase2b.py:2496` the
registration sat inside `if old_decision_leg_rate is not None:` and the `advance` sat outside it —
safe only while every account's decision leg opened on a product that struck a rate, which an
account opening on the default tariff never does.

## 2. What the instrument must do, and the three buckets

For every call to a raise-on-missing accessor outside `tests/`, compute the chain of enclosing `if`
tests **within the enclosing function**, and the same chain for every registration call on the same
receiver in that function. Classify:

* **NARROWER** — a registration exists in the function and *every* registration's guard chain is a
  strict superset of the accessor's. This is the exact defect.
* **PAIRED** — a registration exists whose guard chain is a subset of (or equal to) the accessor's,
  so no enclosing test can separate them. Includes the repaired shape
  (`if get_journey(x) is None: register_customer(x)` immediately above the `advance`, same depth).
* **UNSETTLED** — no registration on that receiver is visible in the enclosing function. Registration
  is elsewhere and static analysis **cannot** settle it. **This bucket is reported as unsettled, not
  as clean.** A survey that calls what it cannot see safe is the fail-open shape this project keeps
  paying for.

## 3. The predictions

**P1 — call sites.** Calls to a raise-on-missing accessor outside `tests/`: point **45**, 80% band
**25–80**.

**P2 — the defect class, NARROWER.** Point **2**, 80% band **1–5**.

*Warrant:* the one instance we have was found by a crash, and a crash is how this shape normally
surfaces — so most of them should already be gone. The counter-mechanism, and the reason the band
does not start at 0, is the arrivals case itself: that site was **unreachable** until a world change
made it reachable, and was fatal rather than wrong when it was. A path no world we run today takes
cannot have crashed yet, so latent instances are exactly the ones that survive.

**P3 — UNSETTLED.** Point **35**, 80% band **15–65**. Most `company/` books are registered by a
different function from the one that uses them; that is ordinary and is not a finding, but it is
also not a clean bill.

**P4 — the instrument must be shown to FIRE on the known instance.** Run it against
`simulation/run_phase2b.py` as of `3a8d15185^` — the pre-repair tree — and it must classify the
`advance` at that site **NARROWER**; run it against HEAD and it must classify the same site
**PAIRED**. An instrument that reports zero because it cannot see the one defect we know exists is
VOID, not a result. **If it does not separate those two trees, the survey is not published.**

## 4. What may NOT travel out of this

**A NARROWER classification is a reachability claim about the TEXT, not a proof a world takes that
path.** Each flagged site needs its own answer to "what world reaches this unregistered", and that
answer is per-site work, not a number. The survey's output is a **question list**, not a defect
count.

**An UNSETTLED count is not a defect count either**, and no sentence in the result will let it
become one.
