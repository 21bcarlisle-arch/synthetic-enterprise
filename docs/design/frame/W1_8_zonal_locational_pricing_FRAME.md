# FRAME — W1_8_zonal_locational_pricing — Zonal / locational marginal pricing mechanics (the regional-basis market that does not exist today)

- **atom**: `W1_8_zonal_locational_pricing` | lane `W1_market_weather` | epoch/dial 3
- **level_current**: 0 → **level_target**: 3 | **depends_on**: `W1_6_physics_price_signal`
- **stage**: DISCOVER/FRAME only (BUILD-gated, `loop_stage: idle`) — doc, no code, level unchanged.

This FRAME is doc-only. It writes no `sim/`/`company/` code, changes no `level_current`, and edits
no `maturity_map.yaml` line (F1 — a fork records its output via an `atom_status/` inbox; the level is
held at 0 because a FRAME cannot earn L1, which the map rubric reserves for "been BUILT in any form").
Scope is `docs/design/` only.

---

## 1. What this atom is & real-world grounding

GB today runs a **single national wholesale price**. Balancing is national; there is one System Buy /
Sell Price and one reference wholesale curve for the whole country. There is **no locational marginal
pricing** and — critically — **no regional forward market**: a supplier cannot buy a hedge that pays
out on Scottish prices specifically, because no such instrument trades. Regional differences in the
physical system (congestion, where wind sits, where load sits) are today socialised through network
charges and constraint costs, not expressed as a regional *energy* price a supplier settles against.

Whether GB should move to **zonal** pricing (a handful of price zones) or **nodal / locational
marginal pricing** (a price at every grid node) is exactly the live GB policy question under **REMA
(the Review of Electricity Market Arrangements)**. That debate is unresolved at the time of writing;
this FRAME stays qualitative about it and fabricates no figures. The load-bearing fact for the sim is
structural, not numeric: **a regional-basis market does not exist in real GB 2016–2025 history.**

So W1_8 is not calibrating an observed market — it is a **synthetic / counterfactual market-generation
atom**. It gives the SIM the ability to generate a regional-basis price field — a set of **zones**,
each with a **zonal marginal price**, and a **regional basis** defined as `basis_z(t) = price_z(t) −
price_national(t)` — a structure that has no real-world outturn to fit against for the counterfactual
regime itself.

**This pins the atom hard against R13 (the baseline/curriculum split).** Because there is no real
zonal outturn, the *existence and severity* of a zonal regime cannot be a fidelity calibration — it is
a **director-authored, named, versioned CURRICULUM scenario** ("Scenario: REMA zonal, moderate
congestion"), never agent-tuned in response to company P&L. The **BASELINE world stays national
single-price** and changes only for fidelity-to-reality reasons, decided blind to company results. The
agent builds the *capability* to generate a zonal field; the director chooses whether any given world
runs national-only or zonal, and how hard the zones diverge (see §6).

---

## 2. COUPLED TRIAD (mandatory — the gap is the score)

Per COUPLED_TRIAD every capability is a 3-loop: SIM adds depth → COMPANY discovers & copes through the
wall → HARNESS measures the belief-vs-truth GAP.

- **SIM adds (world depth) — W1_8:** generates the zonal price field as **ground truth** — the true
  zonal marginal price per zone per timestep, derived from the national physics-price-signal (W1_6)
  plus a regional basis that is **aggregation-consistent** with the national reference (§4). The SIM
  knows the true regional basis; that is precisely the thing the company cannot hedge.
- **COMPANY discovers / copes (through the wall — allowed to be wrong):** the company **observes only
  published/settled prices**. Under a zonal regime it would settle its regional volumes at the
  published zonal prices, but it **cannot hedge the regional basis** — there is no regional forward
  market to buy protection in (this is the real-world fact, preserved through the wall). A supplier
  with a regionally-skewed book (e.g. concentrated in a high-basis zone) that has hedged only to the
  **national** forward curve is left carrying **basis risk**: its cost realises at the zonal price
  while its hedge pays at the national price, and the gap is unhedgeable by construction. The company
  builds its own (approximate, possibly stale or biased) belief about regional basis from observed
  settled zonal prices; mis-estimating its zonal concentration or the basis distribution is a
  *permitted* failure mode.
  - **Nearest existing company-side coping atom:** `B3_hedge_tariff_alignment` (company hedges cost
    when price is locked) is the atom whose posture this basis risk attacks — today it hedges to a
    single national curve and has no notion of regional basis. There is **no dedicated company-side
    "regional-basis-risk" atom yet**; the coupling is therefore **largely UNBUILT**. Per
    COUPLED_TRIAD's binding rule (*no world/SIM atom reaches L3 until a company has been tested against
    it and the gap measured*), **W1_8 cannot reach L3 alone** — it needs a company capability that (a)
    observes settled zonal prices and (b) demonstrably carries the basis it cannot hedge, with the gap
    measured. Authoring or opening that company atom is a separate, coupled piece of work.
- **HARNESS measures (belief-vs-truth GAP):** the company's **regional-basis belief vs SIM truth** —
  how far the company's inferred/assumed basis for its own zones diverges from the SIM's ground-truth
  basis, and whether that divergence produces an unhedged loss under a zonal-severity scenario. The gap
  is reported per coupled pair (W1_8 SIM ↔ company hedge/basis coping ↔ this harness) each digest and
  at the Proof door.

---

## 3. Level decomposition (target L3) — modest and honest

- **L0 (current):** DISCOVER + this FRAME. No code, no zonal field. ✅ (this doc)
- **L1 — a small number of zones, basis coherently derived from national physics + aggregation-consistent.**
  A small fixed zone set (a handful of GB-plausible zones, not a value chosen here — see §6) with a
  zonal marginal price built as `price_z(t) = price_national(t) + basis_z(t)`, where `basis_z(t)` is
  **derived from** the W1_6 national physics-price-signal (not an independent draw) plus a modest
  regional term, and where the **demand-weighted zonal aggregate reconciles to the national reference**
  (§4). The reconciliation invariant exists and is **mutation-tested** from day one. No congestion
  structure yet; basis is a simple coherent offset.
- **L2 — zone-to-zone correlation / congestion structure.** Inter-zone correlation and a congestion
  model: basis widens when a boundary binds (e.g. surplus wind in a northern zone that cannot export
  depresses that zone's price while a southern zone stays high), giving realistic zonal *divergence*
  rather than a static offset. Zones inherit the regional geometry of the W1_4 regional weather field
  where sensible (a zone that has a weather deviation can have a coherent price basis — see §5).
  Reconciliation invariant holds across the correlated field.
- **L3 — coupled-triad gap measured (COUPLED_TRIAD).** The **belief-vs-truth basis gap** is measured
  against a company that **cannot hedge the basis** (a regionally-skewed book hedged only nationally),
  under a director-authored zonal-severity scenario. Full triad gap reported per zone. Time-scale
  invariance of the reconciliation identity stated explicitly (C-S5). Per COUPLED_TRIAD, L3 is
  unreachable until that company has been tested against this field and the gap measured (§2).

---

## 4. The central INVARIANT — demand-weighted zonal aggregate reconciles to the national reference

W1_8's **defining invariant** (mirroring W1_4's demand-weighted-reconciles-to-national identity): the
zonal price field is **not free** — re-aggregating the zonal prices with the correct weights must
recover the national reference within a stated tolerance. This makes the zonal field a *decomposition*
of the national truth, not an independent, contradictory second price story:

```
  price_national(t)  ==  Σ_z  w_z(t) · price_z(t)      within tolerance ε
```

where `w_z(t)` are the reconciliation weights (natural choice: **demand/volume share per zone**, since
a national settled reference is a volume-weighted quantity). Equivalently, the **weighted basis sums to
zero**: `Σ_z w_z(t) · basis_z(t) == 0` — the basis only *redistributes* price across zones, it neither
adds nor removes national-level cost.

**Acceptance condition (R15 — controls must be able to FAIL):** the reconciliation invariant MUST be
mutation-tested at BUILD. The killer test corrupts one zone's basis (or swaps the weights) so the
weighted aggregate no longer equals the national reference, and the check MUST FAIL on it. Three
failure surfaces to close, per R15 doctrine:
- **TAUTOLOGY:** the checker recomputes the aggregate **independently** from the zonal field, never
  reads back a stored "national" value derived from the same sum — it reconciles against W1_6's
  national price, produced upstream and independently.
- **FAIL-OPEN:** an empty/missing zone set, all-zero bases, or a NaN weight must **fail**, not pass
  trivially (a degenerate field is not a reconciled field).
- **FAIL-SILENT:** if the national reference or the weight table is unavailable, the check is a
  **FAILED** check, never a skipped-and-green one.
`ε` is a stated, justified number (float round-off + any named simplification), never slack wide enough
to hide a real reconciliation break.

---

## 5. Dependencies & sequencing

- **`depends_on: W1_6_physics_price_signal`.** The zonal price is defined **as a decomposition of the
  national derived price**: `price_z = price_national + basis_z`, and the reconciliation invariant is
  *against* that national price. There is nothing to decompose and nothing to reconcile against until
  W1_6 emits a stable national derived-price signal — building a zonal field on a placeholder national
  price would bake a fake decomposition. W1_6 itself is not yet settled (its inherited calibration
  failure is unresolved), so W1_8 is **BUILD-gated** on it.
- **Relationship to `W1_4_regional_weather_field`.** Zones should be **aggregation-consistent with /
  built on** the W1_4 regional geometry where sensible: regions that have a weather deviation are the
  natural carriers of a price basis (a low-wind, cold zone versus a high-wind, exporting zone). W1_4
  supplies the *physical* regional structure (weather, embedded generation, congestion drivers) that a
  *price* basis should track; W1_8 need not invent an independent geography. Whether the zone set
  equals the W1_4 region set exactly or is a coarser roll-up is a BUILD/curriculum question, not
  decided here.
- **Available NOW (does not move BUILD level):** this FRAME, the zone-key research (how a zonal roll-up
  of the W1_4 geometry would look), and the reconciliation-method design. **Unblocks BUILD when** W1_6
  exposes a stable national derived price at the SIM seam AND the director opens a zonal-regime
  curriculum scenario for the atom to generate against.

---

## 6. Open questions / director gates — CURRICULUM (R13)

Because a zonal regime is a **counterfactual absent from real history**, every difficulty/existence
knob below is a **director-authored, named, versioned scenario dial** — the agent frames the SHAPE and
names the gates, it does **not** pick values, and it never tunes them toward company outcomes:

- **Does a zonal regime EXIST at all in a given world?** national-only (baseline) vs a zonal
  counterfactual (`Scenario: REMA zonal`). This is a values/curriculum decision (which world the
  company lives through), director-owned.
- **Zone definition:** how many zones and what GB-plausible boundaries (e.g. a Scotland/England split
  vs a finer roll-up of the W1_4 regions). A director-authored zone set, not an agent-chosen count.
- **Congestion severity:** how wide the basis is allowed to blow out when a boundary binds — a
  curriculum severity dial ("moderate congestion" vs "severe split"), named and versioned, never tuned
  to make company results look a particular way.

The **BASELINE** (national single-price) and any *fidelity* calibration of realistic weather/congestion
drivers change only for fidelity-to-reality reasons, decided blind to company P&L.

---

## 7. Portability & scale-readiness

- **Portability:** the zone set is **keyed by market/regime, not hardcoded to GB zones** — model it as
  a typed zonal-price field over a configurable zone key set + weight table, so a second market (its
  own zones, its own basis convention, or a nodal rather than zonal granularity) fits **behind the same
  seam** by supplying its own zones + weights, without touching the reconciliation logic (which is
  geography-independent by design). Hardcoded zone names/count in shipped code = portability debt,
  remediated on next touch.
- **Scale-readiness (C-S1..C-S3):** zonal price observations are **events arriving over time** — the
  company must cope with zonal prints arriving one at a time, late, or out of order (C-S1), processing
  the same zonal print twice is idempotent (C-S2, and the SIM zonal generator draws from its own named
  seeded RNG substream so its draws cannot perturb any other subsystem), and request/response for a
  zonal snapshot are separate events in time, not same-step resolution (C-S3). SIMPLICITY GUARD: a zone
  set + a weight table + a basis term + a linear reconciliation projection is the whole mechanism — no
  zonal-market cathedral.

---

## 8. Typed-flow seam & epistemic wall

Zonal price formation is **SIM-side physics**. Zonal/regional prices cross the SIM/company wall as
**observables only** — the **settled/published zonal prices** — through a typed, versioned message
adapter (`company/interfaces/sim_interface.py` style), exactly as a real supplier would read a
published locational price. The company **never** reads the SIM's zonal-generation internals (the true
basis, the congestion model, the reconciliation weights, the RNG state). A BUILD that lets any
`company/`/`saas/` module import the zonal generator or its intermediates is an epistemic violation and
fails the verifier — it would let the company hedge a basis it is physically supposed to be unable to
hedge, destroying the point of the atom.

The adapter is the **go-live seam**: if GB ever adopts locational pricing under REMA, swap the SIM
zonal generator for a real locational-price feed behind the unchanged interface; the company code that
consumes settled zonal prices does not change.

---

## 9. What this FRAME is NOT claiming

- NOT a level move — held at **L0** (FRAME ≠ built; EPOCH_GATING Rule 1, BUILD-gated).
- NOT a decision that any world runs zonal — regime existence/severity are director curriculum gates
  (§6), not the agent's.
- NOT any new numeric claim — the REMA debate is kept qualitative; no zonal figures are fabricated (GB
  is single-national-price today, zonal/nodal is under review, no live regional forward market exists
  to hedge basis).
- NOT a claim that the coupling is built — the company-side basis-risk capability is unbuilt, so L3 is
  structurally unreachable until it exists and the gap is measured (§2).
