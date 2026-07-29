# K-PILOT deliverable #2 — Scope-independence evidence (provenance ledger + joint test)

**Atom:** `PLANNER_MINTED_scope_independence_evidence_2026-07-28` (self-drawable RUNG-1 mint).
**Source ruling:** `DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md` — deliverable #2, ruling §2.
**Frame it fills:** `docs/design/KPILOT_WHOLESALE_DOMAIN_TOPIC_MAP.md` §6 explicitly hands off to this
deliverable — "sharpen each scope paragraph here with cited practitioner/market-structure material
… and tag provenance."
**Evidence base (external sources, R9-labelled):** `docs/market_research/wholesale_scope_independence_evidence_2026-07-29.md`
(produced this turn by the read-only `discovery-agent`; primary sources fetched 2026-07-29).

## The bar this artefact must clear (ruling §2, verbatim)
> "A scope brief asks: what must a complete treatment of this topic contain, for a reader who needs to
> understand it? — answered from the domain, from practitioner expectation, from the structure of the
> market itself. **Evidence that this was done properly: the brief contains material neither the director
> nor the repo supplied.**"

The failure this guards against (ruling §2): a scope brief that only reproduces the director's off-the-cuff
gap list is "assembly-first displaced one level — no longer starting from what we hold, but from what the
director last said. Neither is the domain." So the test is **falsifiable, not asserted**: below, every
required scope item is tagged by provenance, and the *independent-domain fraction* is counted. If that
fraction were ~0 the deliverable would FAIL its own bar; it is not.

Provenance tags:
- **`director-list`** — present in the director's decomposition ruling (gas≠electricity; different
  products/mechanisms/drivers; the three-axis joint test; "product structure and shape is possibly the
  most important thing").
- **`repo-material`** — already in the repo before this deliverable (Board Spec 004, the W1_6 merit-order /
  SRMC reconstruction, the existing `wholesale-price-formation` page, the price-formation charts).
- **`independent-domain`** — material neither of the above supplied, sourced from real published
  market-structure references this turn (cited in the evidence artefact, R9-labelled). **This is the
  column the ruling's bar is about.**

---

## 1. Provenance ledger — per scope item, all three top-level nodes

Citations in the `independent-domain` column point to the section of the evidence artefact
(`wholesale_scope_independence_evidence_2026-07-29.md`) that carries the fetched source + R9 tag.

### 1.1 `electricity-wholesale`
| Scope item | Provenance | Note / independent-domain citation |
|---|---|---|
| Marginal plant / SRMC sets the half-hourly price | `repo-material` | W1_6 SRMC reconstruction + Board Spec 004 |
| Residual demand after renewables selects the marginal plant | `repo-material` | merit-order stack (built) |
| "Product structure and shape matters" (the *claim*) | `director-list` | director steer, ruling §5.2 |
| **EFA calendar: 6×4h blocks, peak = WD3/WD4/WD5 only** | **`independent-domain`** | ev-artefact §1.1 `[observed: ICE EFA Calendar via Wikipedia/Schofield 2013]` — peak is a *specific tradeable sub-set of the week*, not "daytime" |
| **EFA months/seasons are non-Gregorian (4/5-wk months; 26-wk seasons; leap week in December)** | **`independent-domain`** | ev-artefact §1.1 — a real calendar-building trap |
| **GB day-ahead = EPEX SPOT (N2EX folded in); results published 09:30 GMT** | **`independent-domain`** | ev-artefact §1.2 |
| **GB is explicitly EXCLUDED from the pan-European SDAC implicit day-ahead coupling** (GB + CH named exceptions) | **`independent-domain`** | ev-artefact §1.2 — post-Brexit structural fact; a non-obvious "why GB is its own price island" |
| Shape risk = shaped demand vs flat baseload hedge → residual peak/profile exposure | `independent-domain` (`[inferred]`) | ev-artefact §1.1 — the *commercial* why behind the director's "shape matters" claim |
| Diurnal/seasonal shape, negative-price frequency (behaviour) | `repo-material` | existing charts |

### 1.2 `gas-wholesale`
| Scope item | Provenance | Note / independent-domain citation |
|---|---|---|
| Gas price = "fuel cost that sets the marginal plant's bid" | `repo-material` | the collapsing `gas-price` stub blurb |
| GB tracks TTF / Asian LNG as a price-taker (the *claim*) | `director-list` + topic-map scope | stated in map §3.1 |
| **NBP is a *virtual* hub with soft cash-out (marginal system buy/sell price), no hard penalty; 4,000-therm min clip on the ICE ENDEX OCM** | **`independent-domain`** | ev-artefact §2.1 `[observed: NBP Wikipedia citing OIES NG-63]` — mechanism detail neither list nor repo held |
| **Grain LNG ≈ 645 GWh/day regas, ~20% of UK gas demand; 50:50 Centrica/ECP sale £1.5bn (Aug 2025)** | **`independent-domain`** | ev-artefact §2.2 `[observed: Grain LNG Wikipedia citing FT]` |
| **South Hook + Dragon together up to ~25% of UK gas requirement** | **`independent-domain`** | ev-artefact §2.2 `[observed: BBC via Wikipedia]` |
| Bacton–Zeebrugge used to balance *continental* positions via NBP | `independent-domain` | ev-artefact §2.1 |
| Seasonal storage arbitrage / Rough thinness | `independent-domain` (**NAMED GAP**) | ev-artefact §2.2 — Rough capacity could not be verified this turn; flagged, not fabricated |

### 1.3 `carbon-price`
| Scope item | Provenance | Note / independent-domain citation |
|---|---|---|
| Per-tonne CO₂ cost enters every fossil plant's marginal bid (the *claim*) | `director-list` + topic-map scope | map §3.3 |
| **UK ETS: started 1 Jan 2021, auction reserve price £22/t, cap ~5% below implied EU ETS Phase-4 share** | **`independent-domain`** | ev-artefact §3.1 `[observed: UK ETS Wikipedia citing HoC Library CBP-9212]` |
| **Cost Containment Mechanism actually TRIGGERED Dec 2021** (Sep–Nov 2021 avg > £52.88 trigger; Authority chose not to intervene) | **`independent-domain`** | ev-artefact §3.1 `[observed: live gov.uk CCM decision statement 2021-12-14]` — a real dated event with a real number |
| **CPS is levied as £0.00331/kWh gas (GCV), NOT £/tCO₂; frozen 1 Apr 2016 → 31 Mar 2028 (≈£18/tCO₂)** | **`independent-domain`** | ev-artefact §3.2 `[observed: live gov.uk climate-change-levy-rates]` |
| **Fossil bid carbon cost has TWO independently-moving components** (market UKA price w/ reserve+CCM dynamics PLUS fixed CPS excise that does not track UKA) | `independent-domain` (`[inferred]` synthesis) | ev-artefact §3.2 |
| ICE Futures Europe as UK ETS auction operator | `independent-domain` (**NAMED GAP**) | ev-artefact §3.1 — could not confirm this turn; flagged |

### 1.4 Independent-domain fraction (the legibility the bar requires)
Counting the substantive scope items above: **electricity 5–6 of ~9, gas 4 of ~7, carbon 4 of ~6** are
`independent-domain` — i.e. a clear majority of each node's sharpened scope is material **neither the
director's list nor the repo supplied**, with two items honestly carried as NAMED GAPS rather than
fabricated. The ruling's §2 bar ("contains material neither director nor repo supplied") is met on all
three top-level nodes, and it is *falsifiable*: strike the `independent-domain` rows and each node
collapses back to the director-list + repo sketch the ruling warns against — which is exactly the
before-state this deliverable improves on.

---

## 2. The joint test (ruling §3) applied with independent-domain evidence

Ruling §3: shared **products / mechanisms / drivers** = one topic; different on all three = two topics.
The topic map already argued the split; here it is re-argued **using the independent-domain evidence
above, not the director's three bullets restated** (that restatement is precisely the failure §2 names).

### 2.1 `gas-wholesale` vs `electricity-wholesale`
| Axis | gas-wholesale (independent-domain evidence) | electricity-wholesale (independent-domain evidence) | Same? |
|---|---|---|---|
| **Products** | NBP virtual-hub contracts, 4,000-therm min clip, within-day→annual on ICE ENDEX OCM; a globally-traded molecule (TTF/JKM linkage) | EFA-block baseload/peak (peak = WD3–5 only), non-Gregorian EFA calendar, EPEX SPOT day-ahead half-hourly | **NO** — different traded objects, different calendars, different venues |
| **Mechanisms** | supply/demand balance of pipeline + LNG send-out + storage withdrawal; *soft* cash-out balancing | uniform-price day-ahead auction + merit-order marginal pricing; GB *excluded* from SDAC coupling | **NO** — molecule-balance vs marginal-auction; different clearing physics |
| **Drivers** | Norwegian pipeline flows, LNG cargo optionality (Grain/South Hook/Dragon), global LNG (Asian JKM), storage arbitrage | residual demand after renewables, marginal plant's SRMC (fuel+carbon), interconnector coupling | **NO** — global-fuel-supply-led vs domestic-residual-demand-led |

**Verdict: different on all three axes → two topics.** The independent-domain evidence *strengthens* the
map's split: the EFA/EPEX product-and-calendar structure (electricity) and the NBP virtual-hub /
LNG-cargo structure (gas) are concretely, citably distinct — this is no longer "the director said they're
different", it is "here is the traded-product granularity, the clearing mechanism and the driver set for
each, and they do not overlap."

### 2.2 `carbon-price` vs `electricity-wholesale` (the second independent worked example the ruling invites)
| Axis | carbon-price | electricity-wholesale | Same? |
|---|---|---|---|
| **Products** | UKA allowances (auctioned) + fixed CPS excise (£0.00331/kWh gas) | EFA-block power contracts, day-ahead MWh | **NO** |
| **Mechanisms** | cap-and-trade auction w/ reserve price £22/t + CCM (triggered Dec 2021 @ £52.88) | merit-order marginal auction | **NO** |
| **Drivers** | declining cap trajectory, free allocation, industrial demand, frozen CPS policy | residual demand, marginal fuel+carbon cost | **NO** (though *coupled*: carbon `--drives-->` electricity via the bid stack) |

**Verdict: separate topic, coupled by a `drives` edge** — exactly the map's placement. The
two-independently-moving-components finding (§1.3) is *why* carbon cannot be a mere sub-stub of
electricity: the CPS excise moves on a policy clock that has nothing to do with the UKA auction or the
power auction, so a reader who conflates them mis-models every fossil bid.

---

## 3. R9 / honesty discipline
- Every independent-domain claim above is tagged `[observed-with-evidence: URL]` or `[inferred]` in the
  evidence artefact; **no URL, figure or document title was invented**. Every blocked/failed fetch
  (epexspot.com 403, elexon.co.uk JS-challenge, Rough storage, EUPHEMIA, ICE-as-UK-ETS-operator) is
  listed as a NAMED GAP in the artefact's source table, not papered over.
- This deliverable adds NO new external claim of its own — it only *classifies* (provenance) and
  *applies the joint test to* the evidence artefact's fetched material.

## 4. Exit-criteria check (against the mint)
- [x] Per-node scope brief contains material **neither director nor repo supplied** — §1 ledger, majority
  `independent-domain` on all three nodes (EFA microstructure, SDAC exclusion, NBP virtual-hub/OCM clip,
  LNG shares, UK-ETS reserve/CCM, CPS-as-£/kWh, two-component bid stack).
- [x] Explicit **provenance ledger** per scope item tagging `director-list` / `repo-material` /
  `independent-domain` — §1; independent-domain fraction counted (§1.4) so "transcription is not scoping"
  is falsifiable, not asserted.
- [x] Joint test (§3) applied to the **gas-vs-electricity** split using independent-domain evidence
  (products, mechanisms, drivers) — §2.1 — AND independently to carbon-price — §2.2.
- [x] R9 discipline — §3; no fabricated citations; gaps named.

**Coverage note (per mint):** the earlier `KPILOT_SCOPE_BRIEF_PRICE_FORMATION.md` (DONE) was anchored on
Board Spec 004 — a *repo-supplied* instrument — so it met the first ruling's bar but not §2's sharpened
bar. This deliverable is that new independence requirement; the earlier brief is the baseline the
independent material now exceeds. Not re-minted.

## 5. Reverse / undo
Delete this file and `docs/market_research/wholesale_scope_independence_evidence_2026-07-29.md`; git
revert the commit. Doc-only, no production/sim/site state touched, no wall crossed.
