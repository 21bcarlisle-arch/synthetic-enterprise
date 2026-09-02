**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — whether 2022's declared cause survives the market term

**Filed 2026-09-02, delivery seat, Lane 0, BEFORE any measurement below was run.**
**Subject:** `simulation/departure_level_anchor.UNFITTED_YEARS[2022]`, clause (ii).

---

## What provoked this, stated so the reader can discount it

I did not arrive at this by suspicion. I read
`docs/staging/WORKER_FINDING_THE_SVT_ROUTE_CAN_NOW_SEE_THE_MARKET_AND_THE_NEXT_GATE_IS_A_STALE_CAPTURE_2026-09-01.md`
first, and its measured table reports 2022's SVT floor at **2.33%** (and **2.34%** on a second
worker's re-run at a moved denominator) against the 12.80% it carried before the market term.

**So P1 below is a reproduction, not a discovery, and I am declaring that rather than dressing it
up.** It is still worth running: that finding is dated 2026-09-01, its own second table shows the
union denominator moving under it inside one day (2022: 55 → 52 accounts), and this project has
already paid for a cited baseline that came from a different run than the comparison it was used
in. *The hole being open goes stale exactly like a green.* What is genuinely unmeasured — and what
P3 and P5 are actually about — is what that floor does to the **declared refusal** built on top of
it, which no document in the tree has yet asked.

## The claim under test, quoted from HEAD

`UNFITTED_YEARS[2022]` at HEAD (`19e68169b`) declares two independently binding causes. Clause (ii):

> *"(ii) The reason that is NOT capture-scoped: its SVT floor is 12.09% against a published 4.30%
> ceiling, and `build_departure_risks` deliberately does not scale `svt_inertia`, so NO anchor >= 0
> brings 2022 to the record."*

`docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md` restates it as current — *"this is
the one that binds"* — and uses it as the **defence** for setting 2022 to `NO_LEVEL_CORRECTION`:
*"2022's whole-book floor is already ~12.09% against a 4.30% ceiling, so the year runs ~2.8x above
the record before the anchor touches it."* That defence is what P5 is about.

## Established before filing, by reading source only — NOT predictions

* **E1.** `departure_risks.py:408` is `CAUSE_SVT_INERTIA: _clip_hazard(svt_inertia *
  action_propensity)` — no `level_anchor`. Clause (ii)'s middle sentence, *"`build_departure_risks`
  deliberately does not scale `svt_inertia`"*, is **TRUE at HEAD** and this pass does not touch it.
  The market multiplier is a different term, wired into `svt_inertia_hazard`'s own signature.
* **E2.** `tests/architecture/test_switching_rate_commons.py tests/simulation/test_departure_risks.py`
  run **57 passed, 2 xfailed** at HEAD, so nothing in the tree is red on this today.
* **E3.** `svt_market_invariance_refusal()` returns `None` live — the refusal that used to block the
  whole-book fit has lifted.

## Predictions — the MOVE, not an invariance

**P1 — the floor MOVED and the declared 12.09% is stale.** Recomputing 2022's SVT floor live at
HEAD, from the committed capture's own per-row `sim_years_on_svt` / `sim_segment_days` /
`market_year` under the current hazard, returns a value **below the published 4.30% ceiling**.
Point prediction **2.3%**, band **1.8–3.0%**. Filed as a fall of **~9.8pp** against the declared
figure. *Refuted by:* any value at or above 4.30%, or outside 1.8–3.0%.

**P2 — the clause's CONCLUSION inverts, and that is the finding.** *"NO anchor >= 0 brings 2022 to
the record"* was true because the floor sat 7.8pp ABOVE the ceiling — a floor cannot be lowered by
a non-negative multiplier on a different term. With the floor BELOW the target the barrier is gone:
the year is now short of the record, not over it, and short is the direction an anchor exists to
close. *Refuted by:* the floor coming back above 4.30% (i.e. P1 refuted).

**P3 — and 2022 is STILL unidentified, for the OTHER cause, which is the half I expect to survive.**
Clause (i) is capture-scoped: zero 2022 renewal decisions in the `c2`/`ladder` family, so the anchor
multiplies nothing. Prediction: in `docs/reports/c2_departure_factors.json` the 2022 renewal
decision count is **0**, and the whole-book **floor and ceiling for 2022 are equal to 4 decimal
places**, so no anchor moves the year regardless of P2. *Refuted by:* a non-zero 2022 renewal count
in that capture, or floor ≠ ceiling.

**P4 — the two causes therefore change RANK, not count.** Before: (ii) binds and (i) is scoped.
After: **(i) binds and (ii) is void.** This is a stronger claim than "one clause is stale", because
it means the entry's own sentence *"a reader given only the first would go looking for renewal
decisions"* becomes exactly backwards — looking for renewal decisions is now the ONLY thing that
would help. *Refuted by:* P2 or P3 failing.

**P5 — the answered document's self-flagged defence is VOID, in the direction it flagged against
itself.** `THE_LEVEL_ANCHOR_COLLISION_ANSWERED` set 2022 to `NO_LEVEL_CORRECTION = 1.0`, noted 1.0
is the flattering direction, and defended it on the 12.09%-vs-4.30% overshoot. With the floor at
~2.3% the world sits **BELOW** the record at 2022, so 1.0 no longer sits on a year that is running
hot — it sits on a year that is running cold with no lever. Prediction: the declared value stays
**1.0** and the DEFENCE has to be rewritten, because 1.0 is still the identity of the parameter and
the identity is not a calibration. *Refuted by:* finding any anchor value in the block that is
better justified than the identity for a year with no lever.

**P6 — no existing control fires on any of this, and I predict which one people will assume did.**
`test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` corroborates a
refusal by counting **renewal decisions in the capture** — clause (i) only. Prediction: it does not
read the floor, the string "12.09" appears in no assertion in that file, and the suite stays
**57 passed, 2 xfailed** with clause (ii) false. *Refuted by:* any leg going red when clause (ii)'s
number is edited.

**P7 — what the repair must move, filed before it is written.** A new leg that corroborates the
FLOOR half of a declared cause against a live recomputation must be **RED against HEAD's current
text** and green after correction — the opposite way round from a leg keyed to today's answer.
Mutation, pre-registered: put "12.09" back into the entry and the leg fires. Prediction: the two
`xfail(strict)` band legs stay **xfailed** through this repair — correcting a refusal's stated cause
does not put the world in band, and if this pass ends with them green I have discharged something
by accident and must not claim it. *Refuted by:* an xpass, or the new leg passing against HEAD.

## What must NOT happen

* 2022 is not clamped, not interpolated, the band is not widened, and no anchor value is invented
  for it. If the honest state is "unidentified for a different reason than we said", that is the
  result and it goes on the surface.
* Clause (ii) is **corrected beside its own text, not deleted** — a refusal whose superseded reason
  is erased takes with it the evidence that the refusal was ever checked.
* No `git checkout <path>`, no `git stash`, no `-A`, no `--no-verify`. Pathspec commit only, and
  `git status --porcelain` pasted into the finding.

---

## GRADED, 2026-09-02, beside the filed text above. One MISS, kept.

Graded by the worker seat that verified and landed the repair, not the one that wrote it. Every
number below was measured before this section was written; the leg was mutation-proven under
`python3 -B` in-process, so the shared tree was never mutated.

| # | Filed | Measured | Grade |
|---|---|---|---|
| **E1** | `CAUSE_SVT_INERTIA` carries no `level_anchor`; the middle clause is TRUE and untouched | confirmed — the anchor still does not reach `svt_inertia` | **HELD** |
| **E2** | the two files run **57 passed, 2 xfailed** at HEAD | 58 passed, 2 xfailed *with* the new leg = 57 + 1 | **CONFIRMED** |
| **P1** | 2022 floor below 4.30%; point **2.3%**, band **1.8–3.0%** | **2.3368%** | **CONFIRMED**, inside band, ~0.04pp off the point |
| **P2** | the conclusion INVERTS — the year is short, not over | floor 2.34% < 4.30% target | **CONFIRMED** |
| **P3** | 2022 renewal count **0** in the `c2` capture; floor == ceiling | 0 rows | **CONFIRMED** |
| **P4** | the causes change RANK, not count: (i) binds, (ii) void | that is what the corrected entry now says | **CONFIRMED** |
| **P5** | declared value stays **1.0**; the DEFENCE is rewritten | value unchanged; defence rewritten in the answered doc | **CONFIRMED** |
| **P6** | no existing control fires; `"12.09"` appears in **no assertion** in that file | **the value is right, the scope claim is WRONG** — see below | **SPLIT: confirmed / MISSED** |
| **P7** | new leg RED against HEAD's text, green after; the two band `xfail`s stay xfailed | mutation fires on the value; empty-subject arm also fires; **2 xfailed** | **CONFIRMED** |

### P6 is the miss and it is the one worth keeping

P6's *mechanism* claim was right: no leg reads the floor, and the entry stayed green with half of
it false. Its *scope* claim — that `"12.09"` appears in no assertion in that file — is **false**.
It appears at `test_switching_rate_commons.py:1473`, inside the disclosure register's own entry for
`YEAR_LEVEL_ANCHOR[2022]`, and that entry went on asserting the **voided** conclusion in the
present tense: *"no anchor >= 0 reaches 2022's band while `build_departure_risks` leaves
`svt_inertia` unscaled"*.

The conclusion is still true; **its stated reason is not**. 2022 is unreachable because it has zero
renewal decisions for the anchor to multiply — cause (i) — not because an unscaled `svt_inertia`
pins it above the record. The repair corrected the declaration in `UNFITTED_YEARS` and left the
same void clause standing one file away, because the new leg's regex scans `UNFITTED_YEARS` and
**structurally cannot see this register**. That is the mechanises-one-disclosure-and-leaves-the-rest-
in-prose shape, caught inside the very commit that exists to fix an instance of it.

Corrected in this commit, beside its own text, and **named in the register as an unheld prose
disclosure rather than dressed up as a held one**. Not mechanised: a leg that scanned every prose
string in the repo for stale figures is the register-that-breeds-registers this project has already
paid for. The honest state is *"corrected, and held by nothing but this sentence"*.

### The "must NOT happen" constraints, discharged against the artefact

2022 is not clamped, not interpolated, the band is not widened, and no anchor value was invented —
`NO_LEVEL_CORRECTION` (1.0) is unchanged. Clause (ii) is corrected beside its own text, not
deleted. No `git checkout <path>`, no `git stash`, no `-A`, no `--no-verify`; pathspec commit only.
`git status --porcelain` over the pathspec, immediately before the commit:

```
 M docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md
 M simulation/departure_level_anchor.py
 M tests/architecture/test_switching_rate_commons.py
?? docs/staging/WORKER_FINDING_THE_BINDING_HALF_OF_2022S_REFUSAL_WAS_VOIDED_BY_A_TERM_THAT_LANDED_THE_DAY_BEFORE_2026-09-02.md
?? docs/staging/WORKER_PREREGISTRATION_WHETHER_2022S_DECLARED_CAUSE_SURVIVES_THE_MARKET_TERM_2026-09-02.md
```

`tools/population_anchor.py` is **absent from that list on purpose**: the measured-zero repair the
direction listed as still owed was already committed at HEAD. Verified, not assumed.
