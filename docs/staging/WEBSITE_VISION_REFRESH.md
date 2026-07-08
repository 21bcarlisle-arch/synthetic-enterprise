# WEBSITE_VISION_REFRESH — Home + Project pages, latest vision & logic (P1)

**Staged:** 2026-07-08 by advisor on the director's explicit instruction; director
set this P1 himself (and it is a director-repeat website ask — third this week).
**Tier:** 2. Copy/narrative work on two pages. Token-cheap: no sim runs, no new
data, no new panels. Sequence alongside/after the in-flight em-dash generator fix;
do not let the two passes tread on the same files simultaneously.

## The problem
The Home page and Project overview page read as the project stood several epochs
ago. The pitch ("proving the software, the data, and the method") is still true
but no longer the sharpest statement of what this is or why. The vision has moved
on in director/advisor sessions and the front door should say so. Below is the
canonical narrative content, agreed with the director. Turn it into page copy in
the site's existing voice (observatory principle: confident, factual, no hype).

## Canonical narrative points (source material — reword freely, drop nothing)

1. **End state.** Poesys is not building a model of an energy supplier; it is
   building a *running autonomous energy business* — one whose commercial,
   financial, and operational processes all execute, and which is on a stated
   path toward handling real customer and market interactions. The final phase of
   the roadmap is a go-live analysis: what would it actually take, legally and
   operationally, for this company to serve a real customer.

2. **Proof-first, in public.** As of Phase RX the company runs a shadow-live
   track record: two decoupled clocks, live Elexon market data flowing in, and a
   public predicted-vs-realised scorecard. The claim to make on the front door:
   *we publish our predictions before the outcomes arrive, and we keep the
   misses.* The track record is public from day one, including the failures —
   that is the trust mechanism, and almost nobody in the industry does it.

3. **Why now — the industry is converging on our premise from the wrong side.**
   Real platform vendors are retrofitting AI onto human-designed cores: agents
   bolted onto billing engines, "universal agent" operating models that still
   assume a human owns the journey. Poesys inverts this: an AI-native company
   built from first principles, with the human as strategic director only (one
   principal, mission and risk appetite, reserved matters — never the keyboard).
   The question the project answers is not "can AI help run a supplier" but
   "what does a supplier look like when AI *is* the company." (Do not name
   specific vendors on the page; characterise the industry pattern.)

4. **Epistemic honesty as the architectural signature.** The company cannot see
   inside the simulation. It discovers its world only through what a real
   supplier could observe: meter reads, market feeds, customer contacts, bills
   and payments, regulatory publications. The boundary is enforced in code, not
   convention. Test on the page: "could a real UK supplier know this?"

5. **A company that can die.** Insolvency and licence revocation are terminal
   states, not exceptions. Mortality is what makes the longevity claim mean
   something: survival across a decade of real market history — including the
   2021-22 crisis that killed ~30 real UK suppliers — is an earned result, not
   an assumption. (The crisis-survival evidence already exists on the Project
   page; elevate it into this framing.)

6. **The physics of the hard parts.** Brand and reputation are behavioural
   physics, not vanity metrics: they move price elasticity, forgiveness, exit
   propensity. Time is a random variable: latency, delay, and unhappy paths are
   first-class citizens, because that is where real suppliers bleed. Noise is
   anchored to real data-quality statistics. These commitments are what
   "high-fidelity" concretely means — say so.

7. **Three products, in order.** (a) The **method** first — tiered governance,
   staging bridge, verify-by-fetch, consistency gates, two-strike redesign — the
   transferable way one human directs an autonomous agent to build a company;
   the casebook is the first product. (b) The **synthetic data** second —
   behavioural trajectories and decision streams as industry-valuable exhaust,
   with a latency-and-fidelity tiered access model (free public → delayed detail
   → live detail → partner). (c) The **software** itself. The current page
   implies equal weighting; the ordering and the casebook-first point are the
   update.

8. **Where it goes next.** Depth before scale, then population scale-up, then
   real market-flows choreography, then products, then the go-live analysis.
   One sentence on the Project page is enough — the roadmap should feel like a
   path to the end state in (1), not a feature list.

## Scope & constraints
- **Pages:** `site/index.html` (Home) and `site/project/index.html` (Project
  overview/narrative) only. Other pages untouched by this instruction.
- Rewrite copy; restructure sections on these two pages if the narrative needs
  it. Do NOT add new metric panels, charts, or data surfaces (0a/R6) — the one
  exception already owed: if the RX shadow-live scorecard link/evidence is not
  yet reachable from the Home page, surface a link to it under point 2.
- All stamps via the generator-owned single stamp (no literals) — per the
  freshness pass.
- Observatory principle and the site's existing light, professional voice.
  Confident and specific beats grand and vague. No vendor names, no hype words.
- Project page: keep the phase-story sections (regime-change blindness, crisis
  survival, etc.) — they are the evidence base — but frame them under the new
  narrative rather than as a bare list.

## Definition of done (R1)
Deployed Home and Project pages, fetched fresh, read as the narrative above to a
first-time visitor: end state, proof-first scorecard claim, AI-native inversion,
epistemic boundary, mortality, product ordering. One NTFY when deployed-verified,
noting anything from the canonical points that was deliberately NOT used and why.
