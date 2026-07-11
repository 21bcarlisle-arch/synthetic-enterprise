# B2_OPEX_TAXONOMY_EXPANSION — opex scope expansion + segment discipline (P1, director-direct via NTFY)

**Staged:** 2026-07-10, director-direct (NTFY, correlated with
`docs/staging/done/from_rich_20260710_181043.md` + `..._181124.md`).
**Map cell:** B2_opex_cost_to_serve (level 1/2 at time of staging) — this
supersedes/expands the existing scope, does not replace the already-built
(a) DCC comms charge / (b) AI-compute-and-oversight (still hard 0.0, still
blocked on the director's own token-cost-basis + oversight-rate answers from
the earlier NTFY exchange this session) / (c) benchmark ledger.

## Director's exact instruction

> B2 opex scope expansion + segment discipline. Cost model gains categories
> (4) and (5), plus structure (6):
>
> (4) INFRASTRUCTURE AT COMMERCIAL RATES — cloud at supplier-grade
> resilience, commercial market-data licences, DCC connection/enrolment,
> code memberships (BSC/REC/SEC), Bacs sponsorship; public price lists where
> they exist, estimate-and-flag otherwise.
>
> (5) FIXED GOVERNANCE & PROFESSIONAL — statutory audit, legal, Ofgem
> licence fees, insurance (PI/cyber/D&O), cosec: the AI-irreducible floor;
> own P&L line, never blended; golive-conditional items tagged in the
> simplifications register.
>
> (6) SCALE STRUCTURE — every cost classified fixed / stepped / variable
> with anchored scale curves, and customer-acquisition cost per channel per
> segment as a real cost line.
>
> Named output: an emergent BREAK-EVEN ANALYSIS — book size and mix at
> which the company covers its floor, per strategy — updated each run; this
> is the thesis number. Lane A: "path to break-even" becomes a director-set
> strategic objective the company must plan against (board objective, not
> an output-tune — LAW A intact).
>
> SEGMENT DISCIPLINE: allocate capital employed per segment (working
> capital, credit/settlement exposure, collateral) and report segment ROCE
> against a director-set hurdle; persistent under-hurdle forces a governed
> decision artefact (reprice / fix / exit) — cross-subsidy must be visible
> and decided, never silent.
>
> Add single-customer concentration limit (max % of gross margin from one
> customer) to risk appetite — one I&C loss must not be able to kill the
> company undetected.
>
> Register as the full B2 taxonomy and proceed; flag which anchors you
> cannot source.

## Why Tier 2, not Tier 1

Financial-model/cost-taxonomy scope, director-directed and explicit. Does
not touch the SIM/company epistemic boundary or any of the four named
safety controls (this tier itself, skip-permissions, the epistemic
verifier, the staging flow). Proceed immediately per the tiered model; this
doc exists for resilience/durability across session boundaries, not as a
request for approval that hasn't already been given.

## Decomposition (to size the work, not to seek permission)

1. **Category (4) infrastructure-at-commercial-rates anchors** — research
   real, sourceable figures: supplier-grade cloud hosting cost bands,
   commercial market-data licence costs (ICIS/Argus/Bloomberg-tier or
   equivalent), DCC connection/enrolment fees, BSC/REC/SEC code membership
   fees, Bacs sponsorship costs. Public price lists where they exist;
   honestly flagged estimates where they don't (never invented — matches
   R12/the existing (b) discipline already in `saas/opex_ledger.py`).
2. **Category (5) fixed governance & professional floor** — statutory
   audit, legal, Ofgem licence fees, insurance (PI/cyber/D&O), company
   secretarial: research real SME/mid-market cost anchors for a company of
   this book's scale; own P&L line (never blended into the true/benchmark
   ledger's per-customer allocation); tag golive-conditional items in the
   simplifications register (ASSUMPTIONS.md or wherever that register
   lives) rather than the opex ledger itself.
3. **Category (6) scale structure** — classify every existing + new cost
   line as fixed / stepped / variable, with an anchored scale curve
   (e.g. cloud cost scaling with book size, audit fee stepping at revenue
   bands); add customer-acquisition cost per channel per segment as a real
   cost line (needs its own anchor research — CAC by channel is a distinct,
   sourceable UK energy-retail metric).
4. **Break-even analysis (named output)** — emergent, not tuned: book size
   + mix at which true opex + the (5) floor is covered by gross margin,
   recomputed each run, surfaced on a business surface (not just a spec —
   phase-close rule 0b applies). This is the "investor thesis, quantified"
   language from the original MARGIN_REALISM Step 3 instruction, now with
   a real floor to break even against.
5. **Lane A strategic objective** — "path to break-even" becomes a
   director-set planning objective the company plans against, explicitly
   NOT an output the agent tunes toward (R12 anti-goal-seek still applies
   in full — the objective shapes company DECISIONS, e.g. book-growth
   strategy, not the reported numbers).
6. **Segment capital-employed allocation + ROCE** — working capital,
   credit/settlement exposure, collateral, allocated per segment; segment
   ROCE reported against a director-set hurdle rate (needs the director's
   own hurdle figure — do not invent, same discipline as B2(b)'s
   oversight-rate blocker); persistent under-hurdle segments force a
   governed decision artefact (reprice / fix / exit), not a silent
   cross-subsidy.
7. **Single-customer concentration limit** — new risk-appetite metric: max
   % of gross margin sourced from any one customer, checked each run,
   flagged if breached (one large I&C loss must be visible as a risk, not
   discoverable only after the fact).

## What's genuinely open / needs the director

- Segment ROCE hurdle rate (his call, like B2(b)'s oversight-rate — will
  not invent a number).
- Concentration-limit threshold (e.g. "no single customer > X% of gross
  margin") — his risk appetite to set, will propose a reasoned default if
  asked but won't silently pick one for a registered risk-appetite limit.
- Anchors that may not survive research (network access is unavailable in
  autonomous context per this session's own standing note — anchor
  research needs an interactive discovery pass) will be flagged, not
  invented, exactly as (4)/(5) themselves require.

## DoD

Full B2 taxonomy registered (this doc + updated PRIORITIES.md/maturity_map
entry) with anchors sourced-or-flagged; categories (4)/(5)/(6) built into
`saas/opex_ledger.py` (or a clearly-scoped extension) with real fixed/
stepped/variable classification; break-even analysis computed and rendered
on a real business surface; segment capital/ROCE + concentration limit
built as new, real risk/finance mechanisms; every unresolved anchor or
director-owned number explicitly flagged, never invented.
