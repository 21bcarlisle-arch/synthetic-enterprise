# FRAME — W2_25: shape and attitudes

*DISCOVER/FRAME pass, 2026-09-06. No BUILD code: this atom is epoch-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1) and the ruling registers it as
**decided, not authorised**. Nothing here authorises a build.*

Source: `docs/staging/DIRECTOR_RULING_PEOPLE_MONEY_AND_WHO_THEY_ARE_PHASE1_2026-09-05.md`
§2 item 1, **as re-scoped by**
`DIRECTOR_RULING_AMENDMENT_MERIT_ORDER_PEOPLE_PHASES_AND_PRACTICE_BOOKS_2026-09-05`,
which governs. The amended phase-2 list, verbatim: *"Price elasticity and the
stability-versus-time-of-use preference; contact propensity and channel; presence
residuals (working hours, holidays, shift patterns, working from home) and the
shape they make; **consent to control** — the attitudes that grant or withhold
permission over an EV or a battery, which is where geography's asset potential
becomes value or does not; green stance and trust."*

Siblings: `docs/design/W2_24_HOUSING_PHASE3_FRAME.md`,
`docs/design/W2_26_PEOPLE_PHASE3_FRAME.md`, `docs/design/W2_23_HOUSING_PHASE2_FRAME.md`.

---

## 0. What the atom is, in one line

The attitudes axis of the people draw — **of which two elements are drawn and
wired, two are drawn and wired to nothing on a canon claim that says so out loud,
one exists once already under a different roof, and one has no route at all and
is the one the row is named for.**

---

## 1. The census, because "does it exist" and "does it do anything" are two questions

Every element of the amended list, checked against the tree:

| element | drawn? | reaches a response function? |
|---|---|---|
| price elasticity | **yes** — `population_draw.price_elasticity_for_customer` | **yes** — `customer_events.py:543` |
| stability-vs-time-of-use preference | **no** | — |
| contact propensity | **yes** — `simulation/contact_propensity.py` | **yes** — `contact_centre.py:41` |
| contact channel | **yes** — `Cohort.channel_pref` | **no** (§3) |
| presence residuals | **no** — only phase 1's *typical* presence | — |
| consent to control | **no route at all** (§5) | — |
| green stance | **yes** — `Cohort.green_stance` | **no** (§2) |
| trust | **yes, once, elsewhere** (§4) | yes, in one module |

Measured rather than read — every `simulation/` file mentioning each axis:

```
  green_stance        population_draw.py, population_coverage.py
  channel_pref        population_draw.py, population_coverage.py
  price_sensitivity   population_draw.py, population_coverage.py, run_phase2b.py,
                      live_population.py, customer_events.py, market_switching_propensity.py
  consent             (nothing)
```

Two axes reach the draw and the coverage test and nothing else. One reaches six
modules including the response function. That difference is the whole shape of
this phase.

---

## 2. FINDING 1 — green stance and channel preference are already drawn, and the canon page PUBLISHES that they are wired to nothing

`docs/design/canon_claims.yaml` carries two live, probed claims against
`THE_MODEL_ON_A_PAGE.md`:

```yaml
- id: C1_green_stance_carries_no_channel
  anchor: "`green_stance` and `channel_pref` are drawn, coverage-tested and read by
           no response function at all"
  claim:  "green_stance is read by no response function in the world"
  expects: absent
  probe: {kind: token_live, token: green_stance, roots: [simulation],
          exclude: [simulation/population_draw.py, simulation/population_coverage.py]}
```

— and the identical pair for `channel_pref`. `population_draw.py:1202` states it
on the field itself: `green_stance: str  # NO company observable -- hidden truth
only, ever`, and `cohort_discovery.py:53` structurally excludes it from every
company-side inference.

So the world already knows each household's green stance and preferred channel,
already tests its coverage, and **no behaviour anywhere depends on either.** Phase
2's work on these two is **wiring, not drawing** — which is a smaller and much
better-understood job than the ruling implies, and a different one.

**And it has a consequence the phase must carry, not discover.** `tools/canon_drift_check.py`
enforces those two probes with `expects: absent` over all of `simulation/`. **The
first commit that gives green stance a behavioural limb turns the canon drift
check red**, and the canon gate runs on every lane's commit. The claim and its
probe must be retired in the *same* commit that wires the trait, with the page
edited to say what the world now does. Discovering that mid-build means a red
gate whose cause is in nobody's diff.

This is the single most useful thing this pass found, because it is invisible from
inside the phase: the row's `blocked_on`, its scope and its dependencies say
nothing about a published claim that contradicts its deliverable.

---

## 3. FINDING 2 — contact channel has two mechanisms, and the household's own preference is not either of them

- **The world's channel choice** is `contact_centre.py:88-94`: a roll against a
  fixed population channel mix (phone / webchat / email), whose anchors the module
  itself marks provisional at `:24`. It does not read `channel_pref`.
- **The household's channel preference** is `Cohort.channel_pref`, drawn per
  customer, read by nothing in `simulation/` (§2).
- **The company's discovery of it** is scored in `tools/couple_cohort.py:162`,
  `_true_channel_pref_to_observed_channels` — which manufactures the observed
  channels **from the truth**, inside the harness.

That third bullet is not a tautology: it is a deliberate noisy-observation
instrument and the inference is genuinely non-trivial. But it means the company's
channel inference is scored against observations the harness synthesises, while
the world's actual contact log is generated by a mechanism that has never heard of
`channel_pref`. **The scoring path and the world path are disconnected.** Phase 2's
"contact propensity and channel" is therefore two very different jobs: propensity
is done (§4 below), and channel is a convergence — one channel decision, reading
the household's own preference — not a new draw.

---

## 4. FINDING 3 — contact propensity is done, and trust already exists once

**Propensity is built, world-side, for a stated reason.**
`simulation/contact_propensity.py` exists because
`WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_ESTIMATE_2026-08-11`
found the world drawing its own contact events off the *supplier's* estimate — a
belief-vs-truth gap that was zero by construction. It is keyed on the household's
**engagement archetype** (`household_segments.engagement_level_for_customer`),
which the company structurally cannot read. Nothing to build.

Note the sequencing this creates: the amendment moved **engagement archetype
forward into phase 1**. Phase 2's contact element therefore now rests on a phase-1
quantity that is *already built* — so "conditional on phase 1" is satisfied for
this element the moment phase 1 opens, not when it lands.

**Trust already exists, once, under another roof.**
`simulation/conversation_response.py:245`:

```python
def _trust(customer_id: str) -> float:
    """Hidden trust in [0, 1): high trust dampens the adverse (switch/complain)
    reaction; low trust amplifies it. Never crosses the wall."""
    return _stable_unit(customer_id, "conv_trust")
```

It is real and load-bearing — `:311` scales the adverse-reaction share by
`0.6 + 0.8 * (1 - trust)`. It is also: **uniform on [0,1) with no published
anchor**, **scoped to the conversation model alone**, **not a `Cohort` axis**, so
not coverage-tested and not crossed with anything.

**Recommendation, and it needs no ruling:** phase 2 extends *that* scalar onto the
Cohort and anchors it. It does not mint a second trust. This project's most
expensive recurring shape is one concept with several homes — the VAT rule with
five implementations, the vulnerability scorer with two, `willingness` with three
senses (`W2_26_PEOPLE_PHASE3_FRAME.md` §3). A phase-2 `trust` beside
`conv_trust` would be the next one, and it would be born that way.

---

## 5. FINDING 4 — consent to control has no route, and it is the element the row is named for

The row's `gain` says it plainly: *"Consent to control is the new term and the one
with product consequences: a battery or EV the household will not let us touch has
a technical ceiling and no realisable value."*

The token `consent` does not appear anywhere in `simulation/`. The company side has
`customer_comm_preferences.py` and `privacy_register.py` — **consent to CONTACT**,
which is a different quantity wearing the same word, and the distinction has to be
made before anything is measured (CLAUDE.md: *before measuring a thing, say what it
is*). A household that will take an email will not necessarily let a supplier
choose when its car charges.

Two things make this element more tractable than it looks:

1. **The population it applies to already exists.** EVs and batteries arrive on
   anchored, unprompted curves — `ev_acquired`, `battery_installed` in
   `life_events.py` (see `W2_24_HOUSING_PHASE3_FRAME.md` §1 and
   `W2_26_PEOPLE_PHASE3_FRAME.md` §1). There is already a drawn population of
   households with controllable assets and no permission field.
2. **It is a ceiling term, not a behaviour term.** It multiplies the technical
   ceiling W2_18 computes; it does not need its own response function to be worth
   something. That makes it the cheapest of the six to make consequential and the
   one most likely to change a business answer.

**What it needs and does not have:** an anchor. Published GB evidence on
willingness to cede control of an EV or battery (DESNZ smart-tariff and
demand-flexibility-service participation and drop-out are the places to look) was
**not established this pass and no number is offered.**

---

## 6. FINDING 5 — the elasticity element's real precondition is a director value, not a landed phase

`price_elasticity_for_customer` is a mean-preserving lognormal spread over a
segment level read from the curriculum. The row's opening condition is *"conditional
on phase 1"* — true, and not the binding constraint.

The phase-1 ruling reserves **household-level switching amplitude** as an R13
curriculum slot: an un-anchorable quantity to be *presented with evidence and a
recommended default for the director to ratify, never filled*
(`docs/market_research/household_switching_response_amplitude.md`). Elasticity's
*level* is exactly that quantity. So phase 1 landing with the slot presented but
**unratified** would open phase 2 onto a spread whose level nobody has set.

**Recommendation to the director, treated as adopted unless he objects:** the row's
opening condition reads *"phase 1 lands **and** the switching-amplitude slot is
ratified"*. Not edited into `block_reason` here — the same reason as
`W2_24_HOUSING_PHASE3_FRAME.md` §4: rewriting the condition before he has read the
argument is the wrong order.

Note also the standing separation this must not break: `market_switching_propensity`
holds the **market** level and shape, and its own docstring records that the world
ran 3.15× below the published GB switching record for the project's whole history
because the level was cancelled out and only the shape survived. A per-household
amplitude that re-levels the book would reintroduce that defect from the other end;
the existing spread is mean-preserving for exactly this reason and must stay so.

---

## 7. PREDICTIONS — filed before the answer

1. Wiring `green_stance` to any response function turns `tools/canon_drift_check.py`
   red on the next commit from **any** lane, not just this one. If it does not, the
   probe's `exclude` list or its `roots` are wider than they read, and that is a
   defect in the probe.
2. Consent to control will change a published figure faster than any other element
   here, because it multiplies an existing ceiling rather than needing a new
   behaviour path.
3. Elasticity is the only one of the six whose build is *already* scored: the R1
   inference-ceiling instrument (`tools/r1_inference_ceiling.py:147`) treats
   `price_elasticity_for_customer` as ground truth. If phase 2 changes the draw,
   R1's ceiling moves under it — so R1 must be re-run, not assumed.

---

## 8. Level definitions and exit criteria (so `level_target: 3` is checkable)

The row carries `level_target: 3` and no level definitions. Proposed, for
ratification when the phase opens:

- **L1 (DISCOVER)** — §1's census completed and anchored: every attitude the world
  holds, where it is drawn, what reads it, and for each un-anchored one, the
  published evidence or the declared absence. *Exit:* one register, no row without
  either an anchor or a named gap.
- **L2 (BUILD, when authorised)** — each element either **wired or retired**: a
  trait with no response function is a finding, not a feature. Consent to control
  drawn, anchored and multiplying W2_18's ceiling. Trust extended from
  `conv_trust` rather than duplicated. The canon claims of §2 retired in the same
  commit that wires their subjects. *Exit:* a control per element that dies when
  its limb is removed — reachability proved before behaviour asserted.
- **L3 (the target)** — the attitudes are *discoverable and scored*: each one the
  company is allowed to infer has a coupled-triad belief-vs-truth gap on the
  `couple_cohort` pattern, non-zero and moving; each one it is not (green stance)
  stays structurally excluded and the exclusion has a control. *Exit:* a published
  per-axis gap with the bound its sample earns.

**Proposed `file_scope`** (currently `[]`): `simulation/population_draw.py`,
`simulation/conversation_response.py`, `simulation/contact_centre.py`,
`docs/design/canon_claims.yaml`, and the control file the build writes. Held as a
proposal — a level-0 row's `file_scope` is checked by nothing, so naming files no
build has written is itself a defect.

---

## 9. What would make this phase wrong

- **Drawing what is already drawn.** §1. Two of the six exist and need a consumer;
  drawing them again gives the tree two green stances.
- **Minting a second trust.** §4. The failure would be invisible for weeks and
  expensive to unpick, which is the profile of every previous instance.
- **Wiring a trait without retiring its canon claim in the same commit.** §2.
- **Treating "consent" as one word.** §5. Consent to contact exists; consent to
  control does not; measuring one across both is the bill-shock shape again.
- **Re-levelling the book through a household amplitude.** §6.
- **Starting it.** The phase is registered, not authorised, and W2_19 has not
  landed. This document is the whole of what is permitted.

---

## 10. What this pass did not establish

- **Any anchor for consent to control, trust, or the stability-vs-time-of-use
  preference.** Named as gaps, deliberately without numbers.
- **Whether `couple_cohort`'s synthesised channel observations bias the scored
  inference.** §3 states the disconnection; measuring its effect needs a run.
- **Whether presence residuals have a route.** `demand_model.py:447` carries
  pensioner-presence and employment as *independent* published marginal cuts —
  which is phase 1's typical presence and also, on its face, the same independence
  defect the people ruling names. Not chased this pass; it is phase 1's ground and
  belongs in W2_19's frame.
- **The size of any of this.** No demand, churn or margin figure was computed. This
  is a read of the tree, not a run.
