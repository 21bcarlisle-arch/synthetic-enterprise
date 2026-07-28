# PITCH v7 — line-by-line reconciliation vs primary state (2026-07-28)

**Method (mine, per the director's empowerment clause).** I walked every claim in PITCH v7
that describes *what exists* or *what was found* and gave it a verdict against **primary state**:
the maturity map / model-on-a-page (STATE canon), the fidelity evidence ledger, the ratified
rulings + gate-authorizations ledger, and the assumptions/simplifications registers. Claims in
the **conditional** about future states are exempt by the director's instruction — I checked the
document *stayed* careful about tense and flag the one place it slips (§9 machinery is present-tense,
but is backed — see V-6). Claims that are **argument rather than fact** I classify `not-checkable`
rather than force a verdict.

**Verdict keys:** `verified` (traceable to primary state) · `stale` (was true, now closed) ·
`contradicted` (primary state overturned it) · `external` (true/false lives in an outside source,
not our primary state — checked for registration, not truth) · `not-checkable` (argument by design).

**Do-not-self-edit discipline:** every correction below is a **proposal for director ruling**.
The director's text in `PITCH_V7.md` is untouched, including the footer error.

---

## A. The four the advisor already found — all CONFIRMED

### F-1 · §12 payment blind-spot bullet — `contradicted` (the one it cannot afford to get wrong)
PITCH_V7 line ~199: *"A measured blind spot it reported on itself — a class of payment failures it
**structurally cannot observe** — published as a limitation to live with rather than adjusted away."*

**Primary state:** ratified ruling `f6238fd7f` (2026-07-25) **rejected** structural irreducibility:
a real supplier detects a missed push payment by **expected-collection reconciliation**, so the honest
residual is a **detection latency with a measured distribution**, not a structural blind spot. The
sensing carve-out was built on exactly that basis (payment triad SOURCE 1+2, gap 0.278→0.095). The
pitch offers an *overturned* finding as evidence of its own honesty — a claim-status defect in the one
place the argument depends on being honest.

**Proposed correction (for ruling):** replace the bullet with the reconciliation framing —
> *"A payment-failure signal it first believed it structurally could not see — then corrected itself:
> a real supplier detects a missed push payment by expected-collection reconciliation, so the honest
> residual is a measured **detection latency**, not a blind spot. Reported with its distribution rather
> than compressed to zero."*

This keeps the self-audit virtue (it *did* correct itself) while matching the ratified ruling.

### F-2 · §12 spike-tail bullet — `stale`
PITCH_V7 line ~196: *"A price engine whose extreme-spike tail was an order of magnitude too small — found
by its own fidelity instrument and **declared publicly as the blocking defect** rather than smoothed over."*

**Primary state:** `THE_MODEL_ON_A_PAGE.md` line 70 — *"spike-tail fixed (the declared 10× gap)."* The
defect was closed 2026-07-23. Present-tense "the blocking defect" now asserts a block that no longer exists.

**Proposed correction (for ruling):** keep the honesty (real, self-found, published), drop the current-block —
> *"A price engine whose extreme-spike tail was found (by its own fidelity instrument) to be an order of
> magnitude too small, declared publicly as a blocking defect at the time rather than smoothed over — and
> since closed against the fidelity benchmark."*

### F-3 · §9 "Two disciplines" then lists three — `contradicted` (internal count)
PITCH_V7 line ~179: *"**Two** disciplines keep this honest. First… Second… **Third**, the customer-savings
ledger counts only savings from reduced or time-shifted usage…"* The v7 usage-only clause was appended as a
third item without updating the count.

**Proposed correction (for ruling):** change "Two disciplines" → **"Three disciplines"** (no other edit needed).

### F-4 · Footer "Draft v5" while header is v7 — `contradicted` (internal version)
PITCH_V7 header line ~48 reads *"Draft v7"*; footer line ~233 reads *"Poesys · Draft v5"*. Stale footer carried
through the v5→v6→v7 chain.

**Proposed correction (for ruling):** footer → **"Poesys · Draft v7"**.

---

## B. Beyond the four (the audit)

### F-5 · §9/§13 £273/tCO₂e yardstick is an UNREGISTERED external assumption — `external`, registration gap
PITCH_V7 §9 line ~173 cites *"a central carbon value of £273 per tonne of CO₂e for 2025 (2022 prices, ±50%
sensitivity), derived from the marginal abatement cost of meeting legally binding targets"* — the yardstick the
entire **£/tonne** metric (§9, §14) is to be judged against.

**Primary state:** this figure is **not in `ASSUMPTIONS.md`.** The only carbon-price anchor we have registered is
the DESNZ **traded** carbon value **£44/tCO₂e (2025, real 2025 GBP)** (ASSUMPTIONS.md line 505). These are two
different DESNZ series — £44 is the *traded* (ETS-market) price; £273 is the *appraisal / non-traded* central
value based on marginal abatement cost. The pitch describes £273 correctly and does **not** contradict the £44
figure. But by the pitch's **own §4 "Anchored" discipline** ("Every assumption is registered against an external
source"), the single most load-bearing external number in the document is unregistered.

**Proposed action (not a text edit):** a DISCOVER task to register the DESNZ appraisal carbon value series in
ASSUMPTIONS.md with its exact cut (publication, table, price base, year), so the yardstick meets the pitch's own
anchoring standard. No pitch wording change proposed — the figure reads as plausibly correct; the defect is the
missing register entry, not the claim.

### F-6 · §12 self-audit machinery ("naive benchmark / remove one factor / same household twice") — `verified`
PITCH_V7 line ~203 asserts, present tense, that the machinery *"holds itself against a deliberately naive benchmark,
removes one factor at a time…, and runs the same simulated household twice — once contacted, once not."* This is a
present-tense claim about existing capability (the exact class the director is policing). **It holds:** naive organ
live (`docs/observability/naive_organ_log.jsonl`, 6,768 entries); ablation live (`background/fidelity_emitter.py`,
`fidelity_grid_scorer.py`); counterfactual twin-run live (`company/analytics/counterfactual_retention.py`,
`nudge_discovery.py`, `saas/channel_attribution.py`). No correction — recorded so the present tense is *evidenced*,
not merely tolerated.

### F-7 · §12 forward-premium bullet vs §12 flagship-retraction bullet — `verified`, possible overlap noted
Bullet 1 (line ~195): *"A forward premium an order of magnitude above the industry benchmark, traced to its own
volatility mathematics."* Bullet 4 (line ~198): *"A flagship discovery publicly retracted when its evidence turned
out to be leaked by a subtle look-ahead in the system's own inputs."* CLAUDE.md records the calm-years near-naked-
hedging retraction as traced to a **point-in-time volatility-calc leak** (`HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG`).
Both bullets touch the volatility calculation. They are presented as **distinct** findings (an over-high forward
premium; a retracted hedging discovery) and are individually defensible, so both `verified`. **Note for the director:**
if these are in fact the same root incident narrated twice, §12 slightly over-counts the self-audit record — worth a
one-line confirmation, not a correction I should make.

### Spot-checked `external` claims (true/false outside primary state — no verdict forced, no correction proposed)
- §2 *"thirty suppliers left the market in 2021–22"* — external, matches the known UK 2021–22 supplier-failure count.
- §9 boiler flow-temp *"roughly a tenth of a household's gas"* — external (published trial evidence); plausible.
- §3 *"a decade of real half-hourly settlement prices"* — `verified` (real Elexon/NESO history is the project's spine).

### `not-checkable` by design (argument, not fact) — classified, not forced
The one-paragraph thesis (§ "In one paragraph"), §1 "the pattern nobody disputes", §5 "the budget is the design",
§6 "the end of economies of scope", §7 personalisation semantics, §8 "real homes, real reluctance", the mission's
status as *chosen not derived* (Note on claims). These are the pitch's **argument**; the Note on claims already
labels the mission "chosen, not derived". No verdict forced.

---

## C. Pitch ↔ model-on-a-page disagreements (findings, not edits)
- **Spike-tail:** pitch §12 (blocking, present) vs model-on-a-page line 70 (fixed). → resolved by F-2.
- **Payment blind spot:** pitch §12 (structural) vs ratified `f6238fd7f` (detection latency). → resolved by F-1.
No other STATE disagreement found.

---

## Acceptance check
Every factual claim in the pitch now carries a verdict traceable to primary state (verdicts above); the two cited
findings that were stale/overturned (F-1, F-2) are identified with their corrections proposed; one anchoring gap
(F-5) and one possible over-count (F-7) surfaced. **Four proposed text corrections (F-1…F-4) and one DISCOVER task
(F-5) are returned for director ruling. The director's text in `PITCH_V7.md` is unedited.**
