# FRAME — W2_26: the residual and the change

*DISCOVER/FRAME pass, 2026-09-06. No BUILD code: this atom is epoch-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1) and the ruling registers it as
**decided, not authorised**. Nothing here authorises a build.*

Source: `docs/staging/DIRECTOR_RULING_PEOPLE_MONEY_AND_WHO_THEY_ARE_PHASE1_2026-09-05.md`
§2 item 1, as re-scoped by `DIRECTOR_RULING_AMENDMENT_MERIT_ORDER_PEOPLE_PHASES_AND_PRACTICE_BOOKS`
the same day, which governs. Siblings: `docs/design/W1_23_WEATHER_PHASE2_FRAME.md`,
`docs/design/W1_24_WEATHER_PHASE3_FRAME.md`.

---

## 0. What the atom is, in one line

The change axis of the people draw — life events, income shocks, children
arriving and leaving, unprompted device purchases, and the value-add term — of
which **most is already built, one part is built in name only, and one part is
genuinely new and its name is already taken.**

---

## 1. FINDING 1 — two of the four elements are already built and anchored

The amended scope names four things. Checked against the tree, not against
memory:

| element | state | evidence |
|---|---|---|
| income shocks | **BUILT, anchored** | `job_loss` (2.2%/household/yr), `income_recovery`, `illness`, `retirement_starts` — `life_events.py:175` ff. |
| unprompted device purchases | **BUILT, anchored** | `solar_install`, `ev_acquired`, `heat_pump_installed`, `battery_installed`, `smart_meter_installed`, `insulation_upgraded`, `boiler_replaced` |
| children arriving and leaving | **NAME ONLY** — see §2 | `new_baby` exists and changes no composition; no leaving event |
| the value-add term | **ABSENT**, and the name collides — see §3 | nothing |

The device-purchase probabilities are sourced, not picked: solar from DESNZ REPD
cumulative domestic installs over 28.4M households (3.0% stock 2016 → 5.7% 2025),
EV from a stock curve of 0.3% → 7% over the same window, both as *marginal annual
install probabilities for a household that does not yet have one*.

**This retires the row's own stated worry.** The `origin_note` says the
unprompted device purchase is "the people-side twin of the housing timeline
(W2_24): a world where kit only ever arrives because we sold it cannot tell value
created from value claimed." That world is not the one we have — kit already
arrives on an anchored national curve with no company involvement whatsoever. The
concern was right in general and is already discharged in this particular. I am
recording that rather than letting phase 3 re-derive it.

So "extending the existing life-event stream" is the correct instruction for
income shocks and device purchases, and it is **the wrong instruction for
children**, because there is nothing there to extend.

---

## 2. FINDING 2 — `new_baby` is an income-stress event, not a composition event, and no route exists to make it one

`new_baby` is in `EventType` (`life_events.py:78`) and is drawn against a real
anchor (ONS Birth Summary Tables, ~1.1% per residential household per year,
`:180`). It reads, from the outside, like children arriving.

It is not. In `apply_events`, `new_baby` does exactly one thing:

```
elif event.event_type == "new_baby":
    if state["income_stress"] == IncomeStress.LOW:
        state["income_stress"] = IncomeStress.MODERATE
```

No occupant is added. `divorce` and `retirement_starts` have the identical
shape — all three are income-stress transitions wearing composition names.

**And the reason is structural, not an oversight.** Composition does not live on
the object life events mutate:

- `apply_events` operates on `Household` (`simulation/household.py`), which
  carries no occupancy or children field at all.
- `children_count` and `people_count` live in `dwelling_records.py` / the premise
  trace. `people_count` is a deterministic hash of `customer_id`
  (`_derive_people_count`, `:125–133`) — static for the household's whole
  tenure. `children_count` is `DEFAULT_CHILDREN_COUNT`, and the module states
  plainly at `:115` that it "does NOT fabricate a children distribution".
- **`life_events.py` imports nothing from `dwelling_records`, `demand_model` or
  `premise_trace`.** There is no route, not a missing branch.

So "children arriving and leaving" is not an extension of the existing stream. It
needs (a) a seam that does not exist, (b) a children distribution that the
owning module has deliberately declined to invent, and (c) a leaving event that
has no anchor yet. That is a materially bigger piece of work than the ruling's
"extending the existing stream" implies, and it is better known now than at
build time.

**Why it matters beyond this atom.** Phase 1 (W2_19) draws "occupancy versus
typical for the house" and makes people-driven usage depend on presence. If
composition is constant for a household's whole tenure, the phase-1 occupancy
draw is a per-household constant and phase 3's change axis has nothing to move.

---

## 3. FINDING 3 — `willingness` is already a bound term in this tree, and phase 3 proposes two more senses of it

The ruling's hard part, correctly identified in the row's own note, is keeping
**willingness to buy** kit or services distinct from **willingness to appreciate**
being saved money and carbon. The note calls it "a definition rather than a
number" and warns this is the same shape as average unit rate, net margin and
bill shock.

It is — and there is a prior collision the note does not know about. The word is
already taken, twice:

1. **Willingness to PAY — hard-bound, live, and decides outcomes.**
   `saas/arrears_classifier.py:90` defines `class Willingness(str, Enum)` with
   members `WILL` / `WONT`, the can't-pay/won't-pay quadrant, scored against a
   SIM-side hidden answer key in `simulation/willingness_classification.py`. This
   is not prose: it is an enum with a classifier and an epistemic-wall seam.
2. **Willingness to SHOP — prose only.** `simulation/renewal_engagement.py:159`
   ("the household's own willingness to shop does not arise") describing the
   active/passive/disengaged engagement archetype. Weaker than (1) — a docstring
   phrase, not a named quantity — and I am not overstating it.

Adding "willingness to buy" and "willingness to appreciate" as bare
*willingness* gives four senses of one word in one tree, one of which already
decides collections outcomes. This project has a landed result document about
exactly this failure, and CLAUDE.md's rule is that the definition must come
first and the split must follow from it — never the reverse.

---

## 4. RECOMMENDATIONS — what I am doing, and what is the director's

**Mine, decided here:** the naming constraint. Phase 3's two value-add quantities
**do not get called `willingness` bare.** Whatever they are named, the name must
not be ambiguous with the arrears enum, and the frame that defines them cites
§3. I am not inventing the two names now — naming them before defining them is
the failure this finding exists to prevent — but I am ruling out the one name
that would collide. This is reversible and needs no ruling.

**Mine:** §1's retirement of the row's device-purchase worry is recorded against
the row, so phase 3 does not re-derive it.

**For the director:** the children element (§2) is scoped as "extending the
existing life-event stream" and is not an extension — it needs a new seam and a
distribution the owning module has declined to fabricate. My recommendation,
treated as adopted unless he objects, is that **children arriving and leaving is
split out of phase 3 and sequenced against phase 1's occupancy work**, because
phase 1 already draws composition and this is the same seam from the other end.
Doing it inside phase 3 means building the seam twice or building phase 1's
occupancy on a constant.

---

## 5. Level definitions and exit criteria (so `level_target: 3` is checkable)

- **L0 (now).** Scope registered; three findings above recorded against it.
- **L1.** The two value-add quantities are **defined** — each with its population,
  its trigger, and what would distinguish it from the other in observable
  behaviour — before any number is attached, and neither is named `willingness`.
  Exit: a definition document that states, for a single household, what would have
  to be true for it to score high on one and low on the other.
- **L2.** Composition change has a route: an event that reaches `children_count`,
  with the distribution anchored or an honest named `None` recorded in its place.
  Exit: a control asserting composition can both increase **and** decrease over a
  tenure — one control over the whole partition, because a mechanism that can only
  add passes a per-direction suite.
- **L3.** The change axis is drawn and its effect on usage/CLV is measured against
  the static-composition baseline. Exit: a stated figure for how much the change
  axis moves the answer, not a hope that it does.

---

## 6. PREDICTIONS — filed now, before the answers, so they can refute me

1. **Adding composition change will move published usage figures**, because
   `people_count` currently drives demand and is static. Anything landing this
   must expect a diff on existing outputs and say so before it lands, not after.
2. **The two value-add quantities will correlate strongly but not collapse** —
   they are distinct, which is the director's whole point, and a fitted model
   will still be tempted to collapse them. If a build reports them as effectively
   one factor, the first suspect is the measurement, not the world.
3. **"Children leaving" has no clean published anchor** at household level in the
   sources this repo already holds, and will be the element that forces an honest
   `None` with a named reason rather than a number.
4. **§2's seam, once built, will be reused by moves and change of tenancy** —
   which the amendment moved forward into phase 1. If phase 1 builds a move
   emitter, it is building most of this seam, which is the practical argument for
   §4's recommendation.

---

## 7. What this pass did NOT establish

- **What the two value-add quantities actually are.** Deliberately: §4 rules out
  a name and defines nothing. That is L1 work and doing it here would be the
  definition-follows-the-split failure.
- **Whether a published anchor exists for children leaving home** at the grain
  the draw needs. Not searched; recorded as prediction 3 rather than answered.
- **Whether `people_count`'s hash draw is raked to any published distribution.**
  I read that it is deterministic per `customer_id`; I did not establish what
  distribution it targets or whether it is anchored.
- **What phase 2 leaves behind.** The presence residuals (working hours,
  holidays, shift patterns, working from home) went to phase 2 per the amendment;
  I have not checked whether phase 2's registration is consistent with what
  phase 1 already draws.

---

*Frame only. `level_current: 0`, `loop_stage: idle`, unchanged. The row's target
stays 3 and nothing here moves it.*
