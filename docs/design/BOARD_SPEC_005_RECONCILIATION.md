# BOARD SPEC 005 — THE WEBSITE — line-by-line reconciliation (the director's standing axis-1 rubric)

**What this is.** A line-by-line reconciliation of every scoreable expectation in *BOARD SPECIFICATION 005 — The website*
(`docs/staging/BOARD_SPEC_005_WEBSITE_2026-07-22.md`, verbatim blind practitioner spec) against **(a)** the live site as
built (`site/**`, read this session) and **(b)** the project's ratified canon. Per the board's own instruction, **this
document is the director's standing axis-1 scoring rubric** — each expectation is individually scoreable and re-scoreable
over time; the director's "site n/5 — reason" verdicts reference these rows. Both §7 batteries (8 credibility + 6 usability)
join the standing practitioner fidelity oracle.

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **no level claimed**. Writes no `site/`/`sim/`/`company/`/
`harness/` code, edits no `maturity_map.yaml`, no engine, no `DIRECTOR_CANON.md`, no ratified site/brand canon. It follows
the reconciliation STRUCTURE already fixed in `docs/design/TRIANGULATION_SITE_SEGMENTATION_FRAME.md` §1 (canon table §1.1,
axis-1 rubric shape §1.2) — not re-invented here. Per the steer, **conflicts between board expectation and ratified canon
are surfaced as director findings, not silently resolved.**

**Evidence discipline.** Every row cites a specific live surface read this session (2026-07-22, autonomous run, no network).
Files inspected directly: `site/index.html`, `site/now/index.html`, `site/director/index.html`, `site/project/index.html`
(headers), `site/proof/index.html` (section map + data-layer grep), `site/company/index.html` (grep), `site/customers/index.html`
(grep), `site/shared/director-comments.js`, `site/shadow/**` (rendered HTML), `site/data/*.json` + `site/state/*.json`
(directory + keys). **No figure is fabricated**; where a surface was searched and not found, the row says "not found after
checking X". ABSENT is a first-class, expected verdict — nothing is inflated.

**Canon reconciled against** (`TRIANGULATION_SITE_SEGMENTATION_FRAME.md` §1.1): `PURPOSE_PITCH_V4.md` (apex; £/tCO₂e carbon
thesis, three-ledger, honest-incompleteness), `POESYS_SITE_BRIEF.md` (six-doors + private IA, audiences), `SITE_CONSTITUTION.md`
(binding rules 1–7: evidence links, number passports, rendering-not-author, honesty featured, progressive disclosure,
claim-status, time-sensitive honesty facts), `BRAND_CONSTITUTION.md` (visual identity), R11 (CLAIM=PIXEL) + R14 (basis clock).

---

## Reconciliation table

Verdict legend: **MET** (a live surface proves it) · **PARTIALLY MET** (present but incomplete/mis-sited) · **ABSENT**
(searched, not found) · **N/A**.

### §1 — The audiences, and what each must be able to find

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 1.EXP.method | expert reaches "the methodology (how anchored, the epistemic wall, how fidelity measured)" | SITE_BRIEF §4 The Method/World; SITE_CONSTITUTION rule 5 | PARTIALLY MET | `site/method/index.html` (operating model/harness), `site/world/index.html` (wall), `site/proof/index.html` §"Fidelity — model vs real (W1_6)" all exist and are nav-reachable | Method spread across 3 doors with no single "how it's anchored + wall + fidelity" spine; advance = one methodology path (the Expert-Hour tour) |
| 1.EXP.assumptions | "assumptions register with external anchors and the divergences left standing" | SITE_BRIEF §6b Simplified; R13 baseline | PARTIALLY MET | `site/simplified/index.html` (simplifications register, from `data/simplified.json` 809KB); `proof/index.html` renderFidelity shows model-vs-real divergence | Simplifications ≠ an external-anchor assumptions register with divergences explicitly "left standing"; advance = an anchors register (ONS/Ofgem/Elexon) with each divergence flagged, per SITE_BRIEF §2-World |
| 1.EXP.decisions | "the decision record — what the system chose, when, on what evidence" | SITE_BRIEF §1 Company (pricing/decisions log) | PARTIALLY MET | `site/data/decisions.json`; `shadow/supplier` renders a 150-row "Portfolio Decision Event Stream" (believed-vs-truth). BUT `now/index.html` line 298-304 states the supplier operational decision feed "is not yet a separate stream" | Live decision record is on the deprecated shadow page + a mixed build/governance JSON; advance = a company-door decisions ledger scoped to supplier acts |
| 1.EXP.fidelity | "the fidelity results including failures" | Proof door; R15 | MET | `proof/index.html` sections: "What We Have Not Proven", "Honest Holds — levels not rounded up", "Open Work — every below-target atom unhidden", "Controls That Cannot Fail — kill-list (R15)" | Failures are featured, not hidden — strongest area |
| 1.EXP.retractions | "the retraction history" | Pitch §12 (regime-change retraction narrated); §6 discipline | PARTIALLY MET | `proof/index.html` has "Incident → Rule" timeline + "Retrospective Library"; but grep of `proof/index.html` + `data/proof.json` finds no rendered *retraction/correction history* — the "correction" hits in `proof.json` are Expert-Hour verification notes, not the public regime-change retraction | The flagship retraction (pitch §12) is not a rendered correction-history entry anywhere; advance = a dedicated corrections/retractions surface (see §6.RETRACT, §7.3) |
| 1.EXP.depth2click | "from any headline claim… reach the underlying data or derivation in two or three clicks" | SITE_CONSTITUTION rule 1; R11 | PARTIALLY MET | Evidence links present (front-door thesis card → `data/dashboard.json→opex_ledger`; director/proof "evlink" → source JSON) | Not universal — many prose claims (method/world narrative) dead-end without a data/derivation link; advance = evidence-link audit per SITE_CONSTITUTION rule 1 |
| 1.EXP.challenge | "a published channel for challenge, and evidence that prior challenges were answered" | NEW (no canon surface) | ABSENT | No public challenge channel found in any live page. `director-comments.js` is PIN-gated director-only feedback, not a public expert channel; grep for challenge/argue-back/rebuttal across public doors = none | First-class gap; advance = a public challenge intake + an answered-challenges register (see §7.8) |
| 1.FUND.onepage | funder needs "the argument in one page" | Front door; Pitch (apex) | PARTIALLY MET | `site/index.html` hero + thesis card carry the argument; no dedicated funder one-pager | Front door doubles as pitch; advance = a single evidence-linked funder page (ask + stage + cost + governance) |
| 1.FUND.stage | "what stage this is honestly at (and what it is not)" | Pitch §"What this is, plainly" + §13; SITE_CONSTITUTION rule 7 | MET | `index.html` hero states "a fully autonomous licensed supplier will not be permitted"; `proof/index.html` "What We Have Not Proven"; simplified register | Honest-stage framing is present and prominent |
| 1.FUND.cost | "what it costs to run" | Pitch §5/§14; method | PARTIALLY MET | `site/data/activity_cost.json`; `method/index.html` renders token cost denominator (line ~353) | Cost-to-run exists as a method sub-metric, not a funder-facing "what it costs to run" statement; advance = surface the burn plainly |
| 1.FUND.governance | "who is accountable and how it is governed" | SITE_BRIEF §4 Method/Director; one-way-door doctrine | PARTIALLY MET | `director/index.html` (twin, anti-decay, one-way-door banner); `method/index.html` operating model | Governance is described; "who is accountable" (the single human director, named-humans-needed) is thinner; advance = an accountability statement |
| 1.FUND.ask | "what the money would buy and what the next proof point is" | Pitch §14; Journey/epoch roadmap | PARTIALLY MET | `project/index.html` epoch roadmap + provisional plan; pitch §14 has the ask | The "next proof point / what money buys" (volunteer cohort, carbon proof) is in the pitch doc, not clearly a site surface; advance = wire pitch §14 onto Journey |
| 1.FUND.independent | "independent signals — any external human who has assessed it, on the record" | Pitch (honest: "no external person has yet seen this") | ABSENT | No independent-assessment surface found. The honest current answer is "none yet" (pitch), but the site does not state it | Advance = an "external assessment: none yet" honesty line (time-sensitive fact per SITE_CONSTITUTION rule 7) |
| 1.LAY.path | curious lay person "needs §4 below, and nothing on their path should require reading anything else" | §4 (see below) | ABSENT | No dedicated lay path; front door hero is technical ("settles half-hourly against real Elexon and NESO"). See 4.artefact | Advance = a plain-language explainer on the shortest path |
| 1.DIR.priority | "The Director needs §3. His needs outrank the others in priority of build" | Operational-window causal-chain canon | PARTIALLY MET | Director surfaces exist (`now/`, `director/`) but are the weakest vs their spec (see §3 rows) while the public showcase doors are the most complete — inverting the board's stated build priority | Finding: build order inverted the board's priority (see Director Findings) |

### §2 — How showcase and window coexist

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 2.SSOT | "one source of truth, two presentations… derived from the same underlying data at render time — never retyped" | SITE_CONSTITUTION rules 3 & 5 | MET (live layer) | Every live door fetches `site/data/*.json` at render (`index.html` L319-330, `now/index.html` L404-416, `director/index.html` L301-306); no number authored in markup | Undercut by `shadow/**` (hand-baked static HTML with divergent figures) — see Director Findings #4 |
| 2.PASSPORT | "freshness stamps and basis labels travel with every figure to every surface" | SITE_CONSTITUTION rule 2; R14 | PARTIALLY MET | `now/` per-panel as-of clocks + settlement-lag (L265-271); front-door pulse `.pn` passports; company/director sources cited | Not every figure carries basis+freshness; shadow figures carry none; advance = passport audit site-wide |
| 2.SEP | "reading and acting separated… controls behind authentication on a surface the public cannot reach and ideally cannot enumerate" | SITE_CONSTITUTION rule 3 (rendering never author); PROCEED one-way-door cat 5/8 | MET | `director/index.html` is read-only by construction ("It cannot act", L118-123), `noindex`, and linked from no live page (grep: nothing links to `director/`) | Public cannot enumerate the console — satisfied |
| 2.RATIFY | "irretractable claims in slow motion… traceable to evidence status mechanically, so a retraction sweeps every surface" | R11 CLAIM=PIXEL; claim-status discipline | PARTIALLY MET | R11 pixel discipline + claim-status labels partially applied; PROVISIONAL badges on front door | No demonstrated mechanical retraction-sweep (a retraction propagating to every surface); advance = a claim-status registry that gates render |

### §3 — The Director's window: SEE and DO

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 3.SEE1.queue | "Is anything waiting for me? … the single most important element. If empty, say so affirmatively." | NEW (Advisor flag b); operational-window canon | PARTIALLY MET | `director/index.html` "Action-Needed Queue" renders `system_status.json→staging_queue` with modified-age + affirmative empty ("Queue empty — nothing awaiting action"). BUT it is on `/director/`, NOT the default landing `/now/`, and it lists staging files, not "decisions routed up / gates awaiting authorisation / questions the machine may not answer" as first-class | Advance = put the reserved-to-director queue FIRST on the default landing, typed by kind (gate/routed-question/decision) with age |
| 3.SEE2.health | "Is the machine alive and healthy? Heartbeat, last completed action, anything wedged or failing, incidents since last visit." | operational-window canon | PARTIALLY MET | `now/index.html` shows as-of clocks + hedge-band pill; `system_status.json` has `continuity`/`session_history`; `project/` §"Agent Health"+"Continuity" | "Anything wedged/failing" and "incidents since last visit" are not surfaced on the operator landing; advance = a health tile with wedge/incident state |
| 3.SEE3.delta | "What changed since I last looked? A delta view… ordered by materiality — not a raw log" | NEW (Advisor flag b) | ABSENT | No delta-since-last-visit anywhere. (`customers/index.html` "delta" is a bill-decomposition, unrelated.) | First-class gap; advance = a per-visitor delta (new decisions/results/challenges/retractions since last seen), materiality-ordered |
| 3.SEE4.stand | "Where does the enterprise stand? current front, headline financials with clocks and provisional flags, open risk, count+age of unanswered internal challenges" | Company/Journey; R14 | PARTIALLY MET | `now/` supplier panel (net margin, settled clock, hedge band); `company/` board pack; `director/` provisional plan; EV PROVISIONAL on front door | "Count and age of unanswered internal challenges" absent (no challenge register exists); advance = wire it once challenges exist |
| 3.DO.gate | "authorise or refuse a gate" from the same surface | NEW; CONFLICTS with SITE_CONSTITUTION rule 3 | ABSENT | Site is read-only by construction; gate authorisation is console-only (`director/` banner) | Genuine canon conflict (Director Findings #2) |
| 3.DO.answer | "answer a routed question" | NEW | ABSENT | No answer affordance on any surface; twin Q&A on `director/` is read-only display | As above |
| 3.DO.ruling | "issue a ruling that becomes part of the record" | NEW | ABSENT | No ruling-capture affordance | As above |
| 3.DO.annotate | "annotate any page or figure with a comment the machine must treat as input" | DIRECTOR_COMMENTS_BOX doctrine | PARTIALLY MET | `site/shared/director-comments.js` on every primary page: PIN-gated POST to a comments ntfy topic, checked server-side by `background/director_comments.py`, staged for review (machine input) | The one DO capability that exists; advance = attach comment to a specific figure/claim, not just page-state |
| 3.DO.evidence | "demand evidence" | NEW | ABSENT | No such affordance found | Advance = a "demand evidence" action tied to a claim |
| 3.DO.stop | "reach a stop control — a way to halt autonomous operation — never more than one screen away" | NEW; safety control | ABSENT | grep for stop-control/halt/kill-switch/pause across all `site/**.html` = none | Material safety gap in the window; advance = an authenticated stop control ≤1 screen from the landing (note: writing a live control is one-way-door cat 5/8, director-reserved) |
| 3.DO.phone | "DO… including from a phone" | SITE_BRIEF §6c mobile pass | PARTIALLY MET | Mobile media queries present (`now/` L108-114, `director/` L83-92, `index.html` L76-83) — SEE-from-phone works; DO-from-phone moot while DO is absent | Reading passes mobile; acting does not exist |
| 3.PAIR | "wherever the Director can see a problem, he must act on it without changing tools" | NEW; directly CONFLICTS with SITE_CONSTITUTION rule 3 (read-only rendering) | ABSENT | Read-only site → every act requires the console/terminal | Core conflict — the board's window is not a static rendered site (Director Findings #2) |

### §4 — The lay reader's bar (the Child, cannot be overruled)

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 4.artefact | "a dedicated artefact on the shortest path from the front door — not the opening paragraphs of a technical document" | SITE_BRIEF §4; Pitch "What this is, plainly" | ABSENT | No dedicated lay page. `index.html` hero is the shortest path and it is technical ("settles half-hourly against real Elexon and NESO… discovers its world… never the simulation's own internals"). The "Domain expert / skeptic" honesty door is not a lay page | The exact failure §4 names; advance = a plain "What is this?" page one click from the front door |
| 4.answers | after 2 unaided minutes answer: what is this / is it real / why / who / what found / what not proven | Pitch (apex); §13 | PARTIALLY MET | Front door + `proof/` "What We Have Not Proven" cover most; "who is behind it" and "no customers/licence/revenue" are in the pitch doc, not plainly on the front door | Advance = the six answers on one plain page |
| 4.nocustomers | a stranger must NOT come away believing real customers exist | Pitch; §7.7 | PARTIALLY MET | Front door says "An energy company built and run by AI" and "a running one" without a plain "no real customers / no licence / no revenue" line on the landing; only the `<meta name=description>` says "no customers" | At-risk; advance = an explicit no-customers line above the fold |

### §5 — What must NOT be public (the Worrier)

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 5.CONTROL | "No write endpoint, steering mechanism, or authorisation channel reachable or discoverable" | PROCEED one-way-door cat 5/8 | MET | No write/steer/auth endpoints in `site/**`; `director/` read-only + unlinked; `director-comments.js` posts feedback only (not a control) | Satisfied |
| 5.SECRETS | "keys, tokens, internal hostnames, security topology" | secrets_location/egress doctrine | MET | No secrets/hostnames found; the comments ntfy topic is intentionally public and non-authenticating (documented in `director-comments.js` header) | Satisfied (principles, not topology, published) |
| 5.PII | "Personal data, absolutely and pre-emptively… including aggregates small enough to deanonymise" | Pitch (no household data yet) | MET | Customers are synthetic `C_*` accounts (`customer_sample.json`); no real personal data exists | Rule holds ahead of the first volunteer, as required |
| 5.UNRATIFIED | "drafts, superseded documents without supersession banners, or anything not accepted as an external claim" | SITE_CONSTITUTION rule 3/6 | PARTIALLY MET | `site/shadow/**` (old dashboard) is served, **not `noindex`** (grep: 0), carries no supersession banner, presents Phase-RX-era financials as current | Superseded surface public without a banner — Director Findings #4; advance = banner + noindex or removal |
| 5.IMPERSONATION | "the site should make clear what its only authentic channels are" | NEW | ABSENT | No statement of authentic channels found on any page | Advance = an "our only authentic channels are…" line |
| 5.THIRDPARTY | "Named third parties without their consent — reviewers, contacts, prospective partners" | NEW | MET | No non-consented third parties named; Power TAC etc. are public prior art (pitch §3), not private partners | Satisfied |

### §6 — Presenting incompleteness so it builds credibility

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 6.STATUS | "a maturity label from a small fixed vocabulary — designed / built-untested / tested / externally-reviewed / validated-against-reality — dated, with what would advance it" | SITE_CONSTITUTION rule 6; Pitch Note on Claims | PARTIALLY MET | Vocabulary appears in `customers/index.html` (grep: built-untested/externally-reviewed/validated-against-reality); maturity map rendered on `project/` from `data/maturity_map.json` | Not applied to every capability/claim site-wide, nor consistently dated-with-what-advances-it; advance = the fixed vocabulary as a site-wide badge |
| 6.CONSEQUENCE | "Each stated gap says what it means the reader cannot conclude" | Pitch §9 (three-ledger); R10 | PARTIALLY MET | `now/` carbon panel states the consequence ("no honest tCO₂e to show… we will not fake one"); `proof/` "What We Have Not Proven" | Consequence attached in places, not universally; advance = pair every simplified-register entry with its consequence |
| 6.RETRACT | "Retractions narrated, never deleted. The corrected claim, the reason, the date, in place." | Pitch §12; §7.3 | PARTIALLY MET | `proof/` "Incident → Rule" + "Retrospective Library" narrate incidents→rules; but no rendered corrected-claim-in-place history (see 1.EXP.retractions) | Advance = a corrections/retractions surface with claim + reason + date in place |
| 6.PROPORTION | "The honesty machinery must not become the product… state it once, clearly, and stop" | SITE_CONSTITUTION rule 4 | MET | Front door leads with the carbon thesis and pulse, not apologies; honesty is featured but not dominant | Balance is acceptable |

### §7 — The battery (credibility 1–8, usability 9–14)

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 7.1 | figure without basis/clock/freshness, OR two pages disagree on the same number | SITE_CONSTITUTION rule 2; R14 | PARTIALLY MET | Live layer carries passports; BUT `shadow/index.html` headline "Net Margin £1,521,070" vs `shadow/supplier` ledger "net_margin_gbp £6,424,233" — two served pages disagree on "net margin", and shadow financials carry no basis/claim-status | Live layer largely clean; shadow violates both clauses — Director Findings #4 |
| 7.2 | headline claim cannot be walked to evidence in a few clicks | SITE_CONSTITUTION rule 1 | PARTIALLY MET | Evidence links exist on data-driven claims; prose claims often dead-end (see 1.EXP.depth2click) | Advance = evidence-link audit |
| 7.3 | the correction history is empty | Pitch §12; §6.RETRACT | PARTIALLY MET | No dedicated correction/retraction history rendered; incident→rule + retros are the nearest surface | The board calls an empty correction history "disqualifying" — material; advance per 6.RETRACT |
| 7.4 | stale content presented as current — dates missing or old without acknowledgement | SITE_CONSTITUTION rule 7 | PARTIALLY MET | Live pages carry `generated_at`/run stamps; `shadow/**` presents Phase-RX-era state as current with no staleness acknowledgement | Shadow violates; advance = banner/noindex/remove |
| 7.5 | machine-readable layer broken, empty, or diverges from human layer | SITE_CONSTITUTION rule 5; Advisor flag d | MET | `site/data/*.json` + `site/state/*.json` rich and fresh (timestamps 2026-07-22 11:2x); human layer derived from them at render | Strong — the site about an autonomous system is itself machine-legible (minor: shadow is hand-baked, but it is not the JSON layer) |
| 7.6 | prose reaches for superlatives, or celebrates effort metrics (commit counts, LOC, test counts) as outcomes | Advisor flag c; SITE_BRIEF §6 (hand-figures die) | **ABSENT** (discipline violated) | `project/index.html` §"Test Count Growth" (chart) + §"Build Cadence (commits/day, last 30 days)" (chart); `method/index.html` "rework_commits"/"commits"; `shadow/**` "18504 tests \| 454 modules" and "6 domains \| 72+ capabilities" | Effort metrics are celebrated as headline growth charts — direct item-6 violation. Director Findings #3; advance = recast as outcome/quality metrics or demote |
| 7.7 | lay page fails the two-minute test, or a stranger believes real customers exist | §4 | PARTIALLY MET | No dedicated lay page (4.artefact ABSENT); no plain no-customers line above the fold (4.nocustomers) | At-risk; advance per §4 |
| 7.8 | no route for challenge, or challenges visibly absorbed without answer | 1.EXP.challenge | ABSENT | No public challenge channel; no answered-challenges register | First-class gap |
| 7.9 | cannot tell within ten seconds whether anything needs him | 3.SEE1 | PARTIALLY MET | Queue exists on `/director/` but not on the default landing `/now/`; on the operator landing he cannot tell in 10s | Advance = queue first on the landing |
| 7.10 | no delta since last visit — must re-read to find what changed | 3.SEE3 | ABSENT | No delta view exists | First-class gap |
| 7.11 | window lags the machine materially, or he cannot tell whether it lags | R14; freshness | PARTIALLY MET | Pages carry data `generated_at`/run stamps (he can see the data timestamp); no explicit window-vs-live-machine lag indicator (the `/now/` "settlement lag" is sim-vs-settlement, a different lag) | Advance = a "window last synced N ago vs machine live" indicator |
| 7.12 | aggregation flatters: failures, wedges, incidents averaged into green | R15; SITE_CONSTITUTION rule 4 | MET | `proof/` surfaces open work, honest holds, kill-list; `now/` hedge pill can read OFF BAND; nothing averages failures into green | Does not flatter |
| 7.13 | can see a problem but must go elsewhere to act, or stop control >1 screen away | 3.PAIR + 3.DO.stop | ABSENT | Read-only site → must use the console; no stop control at all | Core conflict + material safety gap (Director Findings #2) |
| 7.14 | needs the builder to explain what the window is showing | operational-window canon | PARTIALLY MET | Pages carry self-describing intros/passports; but the default landing `/now/` is a public causal showcase (world→supplier→customer→carbon), not an operator needs-me view, and `/director/` is dense | Advance = an operator-first landing that reads without narration |

---

## Director findings — where the board's expectation conflicts with ratified canon (flag, do not resolve)

**F1 — Dual-audience density/candour tension, and the operating-window half is decorative (carried forward from FRAME §1.1).**
The board §2 demands both "one source of truth, two presentations" AND (§3) a dense, operator-first, needs-me window; the v4
pitch orders "public thesis first". The live site resolved this toward the **showcase**: the default landing `/now/` is a
public causal-order narrative (world→supplier→customer→carbon), not the SEE/DO operator window §3 specifies. This is exactly
the FRAME §1.2 "NOT credible" seed (d): *the director's operating-window half is decorative — a surface that drives no
decision.* Confirmed against the live pages, per Advisor flag (b). **For the director:** which audience wins the default
landing, and does the operator window get its own primary surface?

**F2 — "Read-only rendering, never an author" (SITE_CONSTITUTION rule 3) directly conflicts with the board's SEE→act pairing,
DO battery, and stop control (§3, §7.13).** The board's window must *act from the same surface it shows* — authorise/refuse
gates, answer routed questions, issue rulings, demand evidence, and a stop control ≤1 screen away. The canon makes the site a
read-only rendering and routes every write to the console (one-way-door cat 5/8, director-reserved). These cannot both be
true on the director's authenticated surface. The board's window is **not a static rendered site**; it needs an authenticated
app surface (the stop control especially is a live safety control — building it is director-reserved). **For the director:**
does the operating window become an authenticated app that can act, and how does that reconcile with console-only writes?

**F3 — Effort-metric celebration (§7.6 violation), against the board's explicit ban.** `project/index.html` carries headline
growth charts "Test Count Growth" and "Build Cadence (commits/day)"; `method/` surfaces commit-based rework; `shadow/**`
advertises "18504 tests \| 454 modules \| 72+ capabilities". The board bans celebrating commit/test counts as outcomes. Note
a mild mechanism tension: CLAUDE.md's build-stamp coupling requires a "N tests collected" figure for the publish gate — that
is an internal stamp, not a public celebration, so the fix is to demote/recast the *public* charts, not touch the gate.

**F4 — The shadow site (`site/shadow/**`) is a public, un-bannered, stale, effort-metric-celebrating, self-contradicting
surface (§5.UNRATIFIED, §7.1, §7.4, §7.6).** It is served, **not `noindex`**, linked from no live page (so not enumerable via
nav, but directly reachable), carries no supersession banner, presents Phase-RX-era financials with no claim-status, and its
"Net Margin £1,521,070" disagrees with `shadow/supplier`'s "£6,424,233". Not a canon conflict — a straightforward defect
against the Worrier's list and three battery items. **Advance:** supersession banner + `noindex`, or remove.

**F5 — No dedicated lay artefact (§4), and the front door doubles as a technical pitch — the exact failure §4 names.** The
Child's bar "cannot be overruled", yet the shortest path from the front door is the technical hero. Mild ordering tension with
the v4 brief, which makes the Front-Door thesis *chart* (technical) the headline visual. **For the director:** does a plain
"What is this?" page sit one click from the front door, ahead of the thesis chart, for the lay reader?

---

## Summary scoreline

**58 scoreable expectations · 11 MET · 31 PARTIALLY MET · 16 ABSENT · 0 N/A.**

By section (MET / PARTIAL / ABSENT): §1 audiences 2/10/3 · §2 coexist 2/2/0 · §3 SEE&DO 0/5/7 · §4 lay 0/2/1 ·
§5 must-not-be-public 4/1/1 · §6 incompleteness 1/3/0 · §7 battery 2/8/4.

**The strongest half is the public showcase** (machine-readable layer 7.5 MET; failures unhidden 1.EXP.fidelity / 7.12 MET;
render-time single-source-of-truth 2.SSOT MET; secrets/PII/control-surface discipline MET). **The weakest half is precisely
the one the board says outranks it in build priority — the director's operating window** (§3 scored 0 MET).

**The 5 most material gaps:**
1. **The operating window (§3) is largely unbuilt** — no delta-since-last-visit (7.10), no act-from-surface (DO gate/answer/
   ruling/evidence all ABSENT), no stop control (3.DO.stop), and the needs-me queue is on `/director/` not the default
   landing (7.9). A read-only rendered site cannot be the SEE→act window the board specifies (F1, F2).
2. **No public challenge channel and no answered-challenges surface (7.8, 1.EXP.challenge)** — the board calls the absence
   disqualifying for the sceptical expert.
3. **No rendered correction/retraction history (7.3, 6.RETRACT)** — the flagship regime-change retraction lives in the pitch
   doc, not on Proof; the board calls an empty correction history "disqualifying".
4. **Effort-metric celebration (7.6)** — "Test Count Growth" / "commits/day" charts on `project/`, and `shadow/`'s "18504
   tests / 454 modules / 72+ capabilities" — a direct violation of the board's ban (F3).
5. **The shadow site (F4)** — public, un-bannered, stale, self-contradicting financials without claim-status — and **no lay
   page (F5)** on the shortest path, risking a stranger's only impression.
