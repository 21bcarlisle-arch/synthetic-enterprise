# Forward-Discovery Register — thinking ahead, ranked

**Established:** 2026-07-21 (DIRECTOR_STEER_FORWARD_DISCOVERY_REGISTER_2026-07-21).
**Class:** OPTIONAL / PREEMPTIBLE (resource-aware scheduling). These tracks soak spare capacity and
**yield instantly to core campaign work** — thinking-ahead never competes with building.
**Discipline:** DISCOVER only. No builds, no new map atoms beyond a track's own register entry, until a
track **graduates by explicit director steer**. Independence + no-personal-data rules apply throughout.

## The ranking principle — certainty × mission-criticality

Thinking ahead is worth fidelity budget only for futures ranked high on **both** axes. Classes (director's):
- **Certain** — every possible world contains it (EV/heat-pump growth, smart-meter completion, warming winters). *W1_10 was this, done right.*
- **Committed** — legislated, dated, live programme (e.g. market-wide half-hourly settlement).
- **Mission-required** — capabilities the ratified purpose cannot function without.
- **Contingent policy** — may never happen (zonal pricing, further cap-reform shapes) → **watching brief only, one line, never a build.**

| rank | track | class | criticality | status |
|---|---|---|---|---|
| **F1** | Simulating conversations | mission-required | **highest** — the pitch's core abatement mechanism | DISCOVER-complete 2026-07-22 (both open items closed, network tick) |
| **F2** | Explaining what we do, simply | committed (legal duty) | high — comprehension = valid consent + trust | DISCOVER-complete 2026-07-22 (6 standards closed, network tick) |
| **F3** | Volunteer programme mechanics | mission-required | high — critical path to any real household | DISCOVER-complete 2026-07-22 (direction-settled to the depth this lane warrants; body §F3) |
| **F4** | International expansion probe | aspirational | medium — tests the "global by design" claim | DISCOVER-complete 2026-07-22 (Ireland magnitudes closed, network tick) |
| **F5** | Simulated competitor field | mission-required | high — pricing/retention are meaningless unopposed | DISCOVER-complete 2026-07-22 (per-supplier % shares closed, network tick) |
| — | *Watching briefs (contingent policy)* | contingent | low | see bottom |

---

## F1 — Simulating conversations *(highest)*

**Purpose.** The pitch's core claim is that **tone, timing and channel ARE the abatement mechanism** — yet
the sim has no conversations: customers don't respond to messages, the company doesn't generate them. Both
sides need designing. This is the missing loop between the engagement-axis *traits* (already estimated in the
segmentation work) and actual *behaviour change*.

**Key DISCOVER questions.**
- What real UK supplier↔customer conversation looks like: contact rates, complaint taxonomies, CSS / Ofgem
  complaints-handling benchmarks, tone-of-voice evidence, channel mix by segment.
- How a message→behaviour response could be modelled against the engagement axes already estimated
  (channel preference, trust, engagement capacity — conversation-revealed traits).
- The epistemic wall here: **the company observes replies and outcomes, never true intent.** A modelled
  customer has an internal state; the company only ever sees what it says/does. Getting this wall right is
  the whole point (a supplier that "reads intent" is a leak).

**Initial scaffolding (not findings — no research run yet).** Two designs are needed: (a) a *company* message
generator keyed to segment + situation; (b) a *customer* response model mapping (message, trait, state) →
action + reply. Anchor generation to real contact/complaint data; validate against an **independent** source
(never SIM ground truth). **Directly serves segmentation:** channel-preference and trust are conversation-revealed.

**Tag:** mission-required × highest. **Status:** DISCOVER pass done (2026-07-22) —
`docs/market_research/f1_simulating_conversations.md`.

**Finding (2026-07-22 tick).** The pitch's premise is **externally corroborated**: Which? 2025 shows a **~6×
complaint-ratio spread** across suppliers on the same regulated product (Octopus 261 vs 1,525 complaints/100k) —
tone/handling IS a real differentiator, not a nicety. The message→behaviour edge already has a benchmark library
(`NUDGE_PHYSICS_BENCHMARKS.md`: debt-letter **tone +3 to +10pp**, framing 10–35%, anchoring 8–20%), wired to the
two hidden conversation traits **FramingSusceptibility / ToneSusceptibility** (`nudge_physics.py`, independent
per-customer draws — no demographic cross-tab exists, §2.3, so susceptibility is an irreducible latent). The
**epistemic wall** is the whole point: SIM holds true susceptibility, COMPANY may only hold a **Bayesian belief
updated on observed replies** (a conversation adds message-response/latency-by-channel as the new observable
stream); a company whose action correlates with the true trait beyond what replies justify is an **intent-leak
the harness must catch (R15 mutation lever)**. Direction validated across **three disjoint sources** — Which?
complaint spread, behavioural-economics causal effects, Ofgem CSAT Wave 20 payment-channel×satisfaction (DD 82% /
prepay 80% / std-credit 76%) — none SIM ground truth; **magnitudes are mostly cross-domain imports** (only Opower
+ UK switching are energy-native), so a build samples magnitude from a distribution (R10 simplification), not a
point estimate. Candidate graduation = the **SIM-response / COMPANY-generator+estimator / HARNESS-gap coupled
triad**; **no atom opened** (director/twin BUILD-open call).

**Increment (2026-07-22, network-restored tick) — both open items CLOSED** (`f1_...md` §Increment). Network probed
live (Ombudsman + Ofgem HTTP 200), so the two previously network-gated items were worked against primary sources,
none SIM ground truth. (1) **Complaint-category taxonomy** — Energy Ombudsman 2024 (92,938 cases, −24% YoY;
**billing 58%** dominant, then customer-service, then smart-meters; within-billing: disputed usage 22% / disputed
balances 8% / back-billing 3,218) gives the *inbound complaint-type mix*; Citizens Advice star-rating gives the
*company-facing outcome axes + weights* — **customer-service 55% / complaints 35% / customer-commitments 10%**, so
the triad's outcome score should be CS-heavy, not equal-weighted. (2) **UK-energy-native tone→outcome study** —
Ofgem complaint-handling research (Ombudsman Services: Energy, Dec 2013; older → a modern-wave refresh is a minor
`[recall, validate]`) supplies a *direct energy-sector* linkage where before only cross-domain imports existed:
tone/language/personalisation → **disengagement**; complaint experience → **~1 in 2 switched/planned to switch**;
and the belief-vs-reality split (**57% domestic dissatisfied**, ~half "supplier thinks resolved / customer disagrees")
is **the coupled-triad GAP in the wild**. Net: the tone→outcome effect's *direction/sign* is now energy-native
corroborated (magnitude stays cross-domain → sample-from-distribution R10). **F1 is now DISCOVER-complete with both
open items closed; no atom opened, no map write** — next tick should draw a still-open increment (F2/F4/F5) or await
director graduation.

## F2 — Explaining what we do, simply

**Purpose.** Comprehension is a **legal duty** (consent that wasn't understood isn't consent — Consumer Duty),
not a nicety, and a trust mechanism. Feeds F3 (volunteer) and the site.

**Key DISCOVER questions.** Plain-language standards (CMA/FCA Consumer Duty comprehension-testing practice,
energy-sector precedents); a **testable bar** — can a lay reader say back what Poesys does with their data and
money; where the current site/pitch fails that bar.

**Tag:** committed (legal) × high. **Status:** DISCOVER-complete (2026-07-22) —
`docs/market_research/f2_explaining_what_we_do_simply.md`. The one open item (validate the six
comprehension-testing standards) was **CLOSED on a later 2026-07-22 network tick** (see §Increment in the
artefact): 5 of 6 standards validated against primary/regulator sources (ICO Art. 12(1); Ofgem OFG1163
SLC 0; FCA Handbook PRIN 2A.5; GOV.UK GDS reading-age-9; CMA EMI Final Report 2016), the 6th (Crystal
Mark) downgraded as a private certification, not a regulatory floor. **F2 now has no open network-gated
item** — residual is the doc-only graduation call only; next tick should draw another still-open track
(F4/F5) or await director graduation.

**Finding (2026-07-22 tick).** F2 fails on the **reader, not the writing**: the live public surface
(`site/index.html`) is a correct *expert* pitch — "Where to go" doors keyed *"Energy CEO / COO"*,
≥6 un-glossed domain terms in the lede ("enterprise simulator", "settles half-hourly", "Elexon and
NESO", "£/tCO₂") — and **no lay-household comprehension surface exists**, so the legal-duty question
"can a reader say back what we do with their **data** and **money**" is currently unanswerable. No
live-consent breach (Poesys holds no household data — F3 gates that); this is *forward* discovery of
the **testable bar** the register asked for. Proposed bar = a **teach-back / say-back test** over four
items (data / money / commitment-and-leaving / human-accountability), **two-tier so it can FAIL
(R15)**: Tier-1 mechanical readability + banned-jargon floor (today's front-door prose must go red),
Tier-2 lay-persona say-back judge (outcome-tested). The **data-consent trap**
(`smart_meter_hh_data_consent_2026.md`), the **SLC money-disclosure floor** (`company_customer_comms.md`)
and **credit-balance ring-fencing** (`ofgem_licence_readiness.md`) are **validated** against independent
already-fetched repo sources; the comprehension-testing *standards* (FCA Consumer Duty PRIN 2A, GDS
reading-age-9, UK GDPR Art. 12(1), CMA EMI) remain `[recall, validate]` pending a live fetch. Candidate
graduation = **harness bar before site page**, gating F3's consent screens; **no atom opened** (director/
twin call). The one lay-facing line the site already gets right — up-front human accountability — must be
preserved.

## F3 — Volunteer programme mechanics

**Purpose.** The pitch makes "will not open until a security-posture review has completed" a public gate — but
no atom exists behind it. This is the **critical path to any real household**.

**Key DISCOVER questions.** What that security review must cover; consent + data-handling design (GDPR lawful
basis, revocation, data minimisation); the smallest honest volunteer pilot. **Design the consent machinery;
hold no data.**

**Tag:** mission-required × high (gated on the security review). **Status:** DISCOVER pass done (2026-07-22) —
`docs/market_research/f3_volunteer_programme_mechanics.md`.

**Finding (2026-07-22 tick).** The critical path is **two director-reserved artefacts** — a security-posture
review and consent machinery — behind a public gate the pitch already commits to ("will not open until a security
posture review has completed"); PURPOSE_PITCH_V4 §4 flags that **no atom exists** for it. This pass converts that
one-line commitment into a **reviewable seven-item scope**: DPIA-first (Art. 35 — the four-dimensional model
profiles household circumstances = high-risk), lawful-basis register, data-minimisation spec, the **Hardened
profile** for storage (CLAUDE.md's own Epoch-5 NFR), consent lifecycle with **revocation-as-easy-as-grant → verified
deletion** (Art. 7(3); a no-op withdraw is an R11 orphan defect), Art. 33 breach path, and both-ways-authenticated
approach channel (PHONE_ACT threat model). **The key finding:** a volunteer **keeps their own supplier**, so Poesys
is a **third party with no supply contract** — *none* of the default-flow contract-necessity basis that lets a real
supplier read HH data (`smart_meter_hh_data_consent_2026.md`) reaches Poesys; every byte rests on **explicit consent
alone** (Art. 6(1)(a); inferred vulnerability edges into Art. 9/Art. 22). This **inverts** the domestic-supplier
intuition — "default-on for a supplier" is exactly *why* a validation partner must be **default-off, minimised,
consent-gated**. Direction validated across **three disjoint source families** — Ofgem/DESNZ data-access law, UK
GDPR + FCA comprehension (via F2's say-back gate), channel-security threat model — none SIM ground truth.
**Smallest honest pilot:** N=1–few, keeps supplier (no switch/money/market crossing), consent+say-back-first,
minimised pseudonymised ingest (consumption+tariff+payment only), publish-the-gap-including-errors, revocable →
deletion, gated on the review. Candidate graduation = a **review gate-atom** + a **holds-no-data consent-machinery
atom**; **no atom opened** — BUILD-open here is **doubly director-reserved** (one-way doors #5 safety-posture and #7
real customer). The load-bearing honesty facts stay true: no volunteer approached, no household data held. Open
items `[recall, validate]` (network-gated): the **DCC "Other User" / Data Access Framework** third-party route, the
**ICO DPIA-mandatory list**, and any **energy-sector parallel-billing precedent**.

**Increment (2026-07-22, network-restored tick).** Network was live this tick, so the three open items were worked
against real sources (WebSearch/WebFetch) and are now **mostly closed** (`f3_...md` §Increment). **Material
finding, CORRECTING the prior "explicit consent alone" conclusion:** a non-supplier third party may **not** receive
HH smart-meter data on bare consent — there is a **named regulatory accreditation gate** (a **DCC "Other User"**
grant, permission renewed *annually*, and/or **Smart Energy Code signatory + DCC User** status carrying *"regulated
privacy and security requirements on an ongoing basis"*; HH is the opt-in tier of the Data Access & Privacy
Framework). Consent is still the only Art. 6 basis (Q2 unchanged) — but *on top of it* sits an external
instantiation of the **Hardened profile**, so the security-review scope **grows an eighth item (regulatory-access
accreditation)** — the finding *raises* the bar, not lowers it. It also **sharpens the pilot:** at N=1 the
**volunteer supplies their own data** (self-service midata/DCC download), staying clear of the accreditation
regime — any move past volunteer-mediated hand-over is the clean scale boundary that trips the gate. **DPIA
confirmed mandatory** on named triggers (Art. 35(3)(a) automated-profiling-with-significant-effects + ICO criteria
profiling/vulnerable/innovative-tech, ≥2 ⇒ required — F3 meets ≥3). **Energy-sector precedent located: midata**
(Ofgem licence-condition-mandated, consent-based third-party consumption/account transfer; ERRA-2013 powers) —
caveat: a 2020 Ofgem update records it *paused for 2020/21*, current framework is the DESNZ-2024 DAP review, so
its *current* status is `[recall, validate]`. Sources all independent, none SIM ground truth; a few residual
`[recall, validate]` refinements remain (exact Art. 35(4) list wording; primary DESNZ-2024 tier text; midata's
current status) — direction-settled, not open. **F3 is now DISCOVER-complete to the depth this lane warrants;**
next tick should draw **F4** or await director graduation.

## F4 — International expansion probe

**Purpose.** The pitch asserts "global by design"; §13 admits transfer is unproven. Produce **evidence for or
against** the transferability claim — not a market-entry plan.

**Key DISCOVER questions.** Pick ONE candidate second market; enumerate concretely what varies (market
structure, settlement, tariff regulation, data availability, consumer protection); assess which variations the
architecture's parameters absorb vs which break assumptions. (Ties to the standing portability constraints.)

**Tag:** aspirational × medium. **Status:** DISCOVER pass done (2026-07-22) —
`docs/market_research/f4_international_expansion_probe.md`.

**Finding (2026-07-22 tick).** The candidate second market is the **Republic of Ireland (SEM/I-SEM)** —
the *gentlest realistic* pick (adjacency, HH heritage), chosen so that if even the closest neighbour
breaks assumptions the "just a variable" reading of §11 is optimistic. §11's "what stays constant" list
**splits cleanly, and the code says where**: the **brain/governance layer ABSORBS** — obligations
register is `regime`-keyed + extensible (`obligations_register.py`, CRU fits as new rows), decision
architecture/observability are counterparty-free (`internal_seams.py`), invariant *classes* carry a
`jurisdiction` field + effective-dates. But the **transactional core BREAKS**: **currency is the deepest
blocker** (no `Money` type; **~6,100 `_gbp` field names**), **tax** is hardcoded VAT literals keyed by
segment not jurisdiction (`invoice.py`, `dual_fuel_bill.py`), **settlement granularity** is `48`
duplicated across ~10 modules (mild for IE, a hard break for ERCOT-15min/NEM-5min — the gentle pick
*hides* it), the **reconciliation window** is Elexon-hardwired (duplicated sim+company), and the
**SIM-seam payload vocabulary** is GB-baked (`mpan`, `:SP`, Elexon/NBP). One sharper class-level break:
the **price-cap invariant structurally assumes a GB institution** — Ireland has *no* domestic cap, so it
needs to be **regime-optional, not re-anchored** (a class change, not a value change). Verdict: **§13's
admission is correct and now quantified — the architecture is portable where it reasons and GB-bound
where it transacts**; transfer is a data-and-adapter exercise for the brain, a real rework for the
plumbing. Verdicts anchored to **actual repo code** (independent of SIM ground truth); Ireland *magnitudes*
(VAT %, PSO levy, ISP length) are `[recall, validate]` pending a SEMO/CRU/Revenue fetch. **Meta-finding:**
the portability debt the doctrine says to "log" is logged **diffusely** (inline notes, no rankable
register) — "mentioned somewhere" reads as covered when it isn't. Candidate graduation, ranked by break
depth: (1) a **doc-only consolidated `PORTABILITY_DEBT.md`** register, (2) a `Money`/currency abstraction
(remediation-on-touch), (3) a `market.settlement_granularity` config, (4) making the cap invariant
regime-optional; **no atom opened** (director/twin call). **No further autonomous DISCOVER increment on
F4 without network** — remaining work is a doc-only graduation call or a live fetch; next tick should
draw a still-open track or await director graduation.

**Increment (2026-07-22, network-restored tick) — the three Ireland magnitudes CLOSED** (`f4_...md` §9).
Network probed live (CRU 200, Revenue 302), so §8's network-gated `[recall, validate]` magnitudes were
worked against primary sources; each **confirms and two *sharpen*** the §4 breaks, none overturns one.
(1) **ISP length** — I-SEM = **48 × 30-min imbalance settlement periods**, each holding **six 5-min
imbalance-*pricing* periods** (SEMO *Industry Guide to the I-SEM*): settlement granularity is *identical
to GB's 48* (so the `48` constant absorbs — confirms "mild for IE"), but the 5-min pricing sub-layer is a
genuine structural addition the constant flattens away — the gentle pick hides even more than first read.
(2) **VAT** — domestic electricity **9%** (temp, extended to **31 Dec 2030** per the 7 Oct 2025 Budget;
13.5% baseline), i.e. **~2× GB's hardcoded 5%** — the break is now a quantified factor-of-2 error, not
just jurisdiction-blindness. (3) **PSO levy** — a **mandatory per-customer charge with no GB bill-line
analogue** (€1.46/mo ex-VAT for 2025/26; total €125.38m) that has been **zero or negative (a rebate)** in
recent years — so it is STRUCTURE (a missing regime-keyed line item) whose value can **flip sign**. Still
`[recall, validate]` (non-blocking refinements): Irish carbon-tax magnitude, SEMO reconciliation
timetable, ESB MPRN smart-meter penetration, CRU-obligation↔Ofgem-SLC mapping. **F4 is now
DISCOVER-complete**; remaining moves are the doc-only `PORTABILITY_DEBT.md` graduation (director/twin) or
the recall refinements. **No atom opened, no map level change.** Next drawable increment: **F5** (per-supplier
% shares) or await director graduation.

**Increment (2026-07-22, network-free forward-discovery tick, R17) — the doc-only `PORTABILITY_DEBT.md`
register is now WRITTEN** (`docs/design/PORTABILITY_DEBT.md`). Re-classification correcting the prior
label: consolidating **already-discovered** portability debt into one rankable register is **DISCOVER
output, not a graduation** — it opens no atom and moves no map level, so it does **not** need a
director/twin call (only the *code-remediation* candidates — a `Money` type, a granularity config, a
regime-optional cap invariant — do, and those stay unopened). This closes F4's own **meta-finding** (debt
was logged *diffusely*, "mentioned somewhere reads as covered when it isn't") with the concrete artifact
it named as candidate #1. The seven breaks are anchored to **freshly verified** repo counts, not copied:
**6,850** `*_gbp` field-name occurrences across **330** files (currency, the deepest blocker); `VAT_RATE
= 0.05` hardcoded in `invoice.py:19` plus segment-keyed (not jurisdiction-keyed) dicts; literal `48` in
**41** files; the `jurisdiction` field present on the invariant classes (the brain-absorbs half, recorded
both ways). **No atom opened, no map level change, no network used.** With this written, F4 has no open
non-network DISCOVER increment left — remaining F4 moves are the *code* remediations (director/twin BUILD)
or the `[recall, validate]` refinements. Next drawable increment: **F5** (per-supplier % shares) or await
director graduation.

## F5 — Simulated competitor field

**Purpose.** Already flagged as an Epoch-2 gap: pricing/retention decisions currently face **no opposition**, so
they're not yet meaningful.

**Key DISCOVER questions.** The minimum competitor model that makes pricing/retention meaningful
(tariff-following vs strategic entrants), anchored to **real switching-market behaviour**.

**Tag:** mission-required × high. **Status:** DISCOVER pass done 2026-07-22 — `docs/market_research/f5_simulated_competitor_field.md`.

**Finding (2026-07-22 tick).** The competitor field is a **scalar, not a field**: best-alternative rate
is a fixed historical series (`simulation/market_switching_propensity.py::MARKET_SAVINGS_BY_YEAR`,
company-side `market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR`), so pricing/retention face a
*non-reactive* opponent. The observable-tariff wall is already correct (`company/market/tariff_benchmarking.py`,
public sources only) — the missing piece is a *response edge*. Minimum useful model = a cap/wholesale-endogenous
**tariff-follower band** + 1–3 **regime-gated strategic archetypes** (Era A challenger-boom vs Era B
post-consolidation). Candidate coupled-triad shape proposed in the artefact; **no atom opened** (BUILD-open is a
director/twin call). Market **structure** figures (29 failures / ~4M / ~£2.7bn SoLR / post-2023
re-fixing) **validated** on the 2026-07-22 tick against ≥3 independent already-fetched repo sources
(not SIM ground truth); only per-supplier **% shares** remain `[recall, validate]` pending a live Ofgem
*State of the Market* fetch.

**Increment (2026-07-22, later tick).** Code-anchored graduation hazard added to the artefact §6: the
2022 "nowhere cheaper to go" regime is encoded **twice, independently** —
`MARKET_SAVINGS_BY_YEAR[2022] = -200.0` (SIM) and `MARKET_SWITCHING_MULTIPLIER_BY_YEAR[2022] = 0.44`
(company-side walled belief). A graduation build making the best-alternative rate endogenous must retire
the **SIM scalar in lockstep** (else the emergent field and the old scalar silently diverge — a
half-migrated-parameter defect), while leaving the company multiplier as a legitimately-independent
belief on the far side of the wall (the coupled-triad GAP). Verified by reading both files, neither
against SIM ground truth. **No further autonomous DISCOVER increment on F5 without network** — the one
open item (per-supplier % shares) is fetch-gated; next tick should await director graduation or a live
Ofgem *State of the Market* fetch.

**Increment (2026-07-22, network-restored tick) — per-supplier % shares CLOSED** (`f5_...md` §8).
Network probed live (Ofgem HTTP 301), so F5's sole remaining network-gated item was worked against
primary/regulator sources. **Q2 2025 domestic-electricity shares (Ofgem *State of the Market*, Jan 2026):
Octopus 25% / British Gas 21% / E.ON 16% / OVO 12% / EDF 10% / Scottish Power 8%**, six-largest = **92%**
(domestic elec+gas; the six sum to exactly 92% — internal consistency check). Octopus has **overtaken**
British Gas as the largest electricity supplier (~12.9m accounts, first change at the top since 1990s
liberalisation) and is the only big-six gaining share in both fuels. **Denominator caveat recorded:**
Ofgem's *domestic* top-six is 91%→92%, but DESNZ *Competition in UK Electricity Markets 2024* reports
top-six=65% / top-three=45% on the **all-sectors traded-electricity** denominator (DESNZ domestic-slice
top-three=44%) — a graduation build must calibrate the *domestic* field to the Ofgem 92%, not the DESNZ
65%. The shares **sharpen** §6's archetype set (a share-taking disruptor + share-ceding incumbents + a
competitive tail), not overturn it. **No atom opened, no map level change.** This closes the **last
non-churn network-gated increment across the whole F1–F5 register.**

---

**Lane state (2026-07-22).** With this pass, **all five forward-discovery tracks F1–F5 are
DISCOVER-complete**; every remaining open item across the register is `[recall, validate]` and
**network-gated** (F1 complaint taxonomy + tone→outcome study; F2 comprehension-testing standards;
F3 DCC "Other User" route + ICO DPIA list; F4 Ireland magnitudes or the doc-only debt-register
graduation call; F5 per-supplier % shares). The always-drawable forward-discovery lane is therefore
**drained-pending-network-or-graduation** — no non-network DISCOVER increment remains that is not
churn. This is the honest floor of the lane: a tick that draws forward-discovery with core/idle lanes
empty and no network should record the drained state and rest at that wall (R17: rest is legitimate
with proof the authorized set is empty at every level — this is that proof for the forward-discovery
lane). Director graduation of any track, or restored network, re-opens work.

**Lane state update (2026-07-22, network-restored tick).** Network *was* available on a later tick (the
`no-network-in-autonomous-runs` assumption did not hold), which — as the note above anticipated — **re-opened
work**. The tick drew **F3** and closed its network-gated open items (DCC "Other User"/SEC accreditation route
found; ICO DPIA-mandatory confirmed; midata located as the energy-sector precedent) — see F3 §Increment. Staying
disciplined to the single drawn track, the other tracks' network-gated items (**F1** complaint taxonomy +
tone→outcome; **F2** comprehension standards; **F4** Ireland magnitudes; **F5** per-supplier % shares) were **left
for their own future draws** rather than opportunistically swept (single-track draw, no scope creep). If network
persists, those remain the drawable increments; otherwise the drained-pending-network floor above stands.

**Lane state update (2026-07-22, F1 network tick).** A later scheduled tick drew **F1** (highest) with network
again live, and closed **both** of F1's network-gated items against primary sources (Energy Ombudsman 2024 category
data + Citizens Advice rating weights = the taxonomy; Ofgem complaint-handling research = the UK-energy-native
tone→outcome linkage) — see F1 §Increment. Single-track discipline held: the remaining tracks' network-gated items
(**F2** comprehension standards; **F4** Ireland magnitudes; **F5** per-supplier % shares) were left for their own
future draws. Residual F1 items are now only minor `[recall, validate]` refinements (modern per-lever energy tone
magnitude; exact CS/smart-meter category %), not open questions. Drawable non-churn increments now sit in **F2/F4/F5**
(each network-gated) or await director graduation.

**Lane state update (2026-07-22, F2 network tick).** A later scheduled tick drew **F2** (rank 2, the highest-ranked
still-open track) with network again live (`ico.org.uk`, `ofgem.gov.uk`, `gov.uk`, `handbook.fca.org.uk`,
`assets.publishing.service.gov.uk` all reachable) and **closed F2's one open item** — the six comprehension-testing
standards — against primary/regulator sources (see F2 §Increment): UK GDPR Art. 12(1) (ICO), Ofgem SLC 0 (OFG1163),
FCA PRIN 2A.5 (FCA Handbook), GDS reading-age-9 (GOV.UK), and the CMA EMI Final Report 2016 all validated; the sixth,
the Plain English Crystal Mark, downgraded as a private certification (not a regulatory floor), so removed from the
set rather than left residual. Single-track discipline held: the remaining tracks' network-gated items (**F4** Ireland
magnitudes; **F5** per-supplier % shares) were left for their own future draws. **Drawable non-churn increments now
sit in F4/F5** (each network-gated) or await director graduation; F1/F2/F3 are DISCOVER-complete with no open
network-gated item. If network persists, F4/F5 are the drawable increments; otherwise the drained-pending-network
floor above stands for those two.

**Lane state update (2026-07-22, F4 network tick).** A later scheduled tick drew **F4** (now the highest-ranked
still-open track, F1/F2/F3 already DISCOVER-complete) with network again live (CRU 200, Revenue 302) and
**closed F4's one open item** — the three Ireland magnitudes (VAT %, PSO levy, ISP length) — against
primary/regulator sources (SEMO *Industry Guide to the I-SEM*; gov.ie/Irish Times; CRU 2025/26 final decision).
See F4 §Increment: the ISP is **48×30-min** (settlement absorbs GB's `48`, the **5-min pricing** sub-layer is the
hidden addition), VAT is **9% temp→13.5%** (**~2× GB's 5%**), and the **PSO levy** is a sign-flipping regime-keyed
line item GB has no slot for — each **confirms/sharpens** a §4 break, none overturns one. Single-track discipline
held: **F5**'s one open item (per-supplier % shares) was left for its own future draw. **Only ONE network-gated
non-churn increment now remains across the whole register: F5 per-supplier % shares.** Everything else is either
DISCOVER-complete (F1/F2/F3/F4) or a doc-only director/twin graduation call (the F4 `PORTABILITY_DEBT.md`
register). If network persists, **F5 is the sole drawable increment**; otherwise the drained-pending-network floor
stands.

**Lane state update (2026-07-22, F5 network tick — REGISTER NOW FULLY DISCOVER-COMPLETE).** A later
scheduled tick drew **F5** (the sole remaining still-open track) with core/idle empty and network probed
live (Ofgem HTTP 301) and **closed F5's one open item** — the per-supplier % shares — against
primary/regulator sources (Ofgem *State of the Market* Jan 2026 + DESNZ *Competition in UK Electricity
Markets 2024*). See F5 §Increment: Q2 2025 domestic-electricity shares **Octopus 25 / BG 21 / E.ON 16 /
OVO 12 / EDF 10 / ScotPower 8** (six-largest 92%), with the domestic-vs-all-sectors denominator caveat
recorded so a build can't mis-calibrate. **With this pass every non-churn increment across F1–F5 is
closed** — all five tracks are DISCOVER-complete, no open network-gated item remains anywhere in the
register. The always-drawable forward-discovery lane is now **genuinely drained** for DISCOVER: the only
remaining moves are **director/twin graduation calls** (opening a coupled-triad BUILD atom for any track,
or the F4 doc-only `PORTABILITY_DEBT.md` register) and minor `[recall, validate]` refinements — no
autonomous non-churn DISCOVER increment remains. Per R17 this is the honest floor with proof: a subsequent
tick that draws forward-discovery with core/idle empty should record this drained-complete state and rest
at the graduation wall until the director opens a track or new network-gated questions are authored.

**Rest-tick confirmation (2026-07-22, later scheduled tick — network-live drained proof, R17).** A
subsequent forward-discovery draw fired with core/idle BUILD empty and staging empty. Per the standing
"probe before declaring drained-pending-network" discipline, network was probed live this tick
(Ofgem HTTP 200) — so the drained state is **not** a network artifact. Re-scanned all five tracks:
**no open network-gated item has re-opened anywhere in the register** (F1–F5 all remain DISCOVER-complete
per the F5 pass above). This is the honest empty-at-EVERY-level floor R17 defines: BUILD-empty,
DISCOVER-drained, network-live-yet-nothing-open. No autonomous non-churn increment exists to draw, so the
tick **rests at the graduation wall** — the only remaining moves are director/twin graduation calls
(coupled-triad BUILD open, or the F4 doc-only `PORTABILITY_DEBT.md` register). No map write: the
`H_forward_discovery_draw` atom's recorded state (mechanised, R15-proven, drained, `level_current` 1 pending
a director ledger ratification per R16) is already accurate; manufacturing a map edit or speculative new
question purely to avoid rest would violate SELF_INTERRUPT_DISCIPLINE and R17's own definition of legitimate
rest (rest IS legitimate *with* proof).

---

## Watching briefs — contingent policy (one line each, never a build)

- **Zonal / locational marginal pricing (REMA).** REJECTED in reality — DESNZ chose Reformed National Pricing
  on 2025-07-10; zonal is a declined counterfactual. GB single-national-price baseline already matches the
  decided regime. **Only ever a director-authored R13 curriculum scenario, never a baseline.** Atom
  `W1_8_zonal_locational_pricing` closed 2026-07-21. Evidence: `docs/market_research/REMA_ZONAL_PRICING_DISCOVER.md`.

*(Add contingent-policy items here as one-liners; add forward tracks above on the same certainty × criticality
test. The director invites additions.)*
