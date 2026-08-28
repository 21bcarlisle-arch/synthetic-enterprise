**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A47_the_score_has_no_household_side`

# The mission rewrite: what I changed, what I rejected, and the four things it invalidates

Your sentence, 2026-08-28, taken verbatim and treated as binding:

> We are creating enterprise value by automating ways to find individual customers we can create
> value for, and sharing in that value — by saving them money, time and carbon, through personalised
> modelling, tariffs and advice.

## Where it now lives

| surface | what changed | state |
|---|---|---|
| `CLAUDE.md` §What this project is | the fidelity line replaced by the mission + the three consequences | landed |
| `docs/design/THE_MODEL_ON_A_PAGE.md` | "The one-sentence company" → §The mission; THE SCORE annotated as one-sided | landed |
| `site/index.html` — front door, `<meta>` + pitch + mission block | superseded sentence gone; three currencies and three channels named, with the honest state of both | **live** — R11 verified by fetching https://poesys.net/ after the push |
| `tools/generate_company_data.py` — segment panel `mission_note` | rewritten; the mission-vs-book escalation to you is KEPT and sharpened | landed |
| `docs/design/PITCH_V7.md` | supersession banner; **body unedited** per its own do-not-self-edit rule | landed |
| map | 4 atoms minted: `A47`, `A48`, `C30`, `C31` | landed |

## The three things you said follow — and what each one costs

### 1. Two sides, and transfer is not creation

Taken as a change to the **objective**, not a caveat on it. `THE_MODEL_ON_A_PAGE` now carries the
six-cell table (two sides × three currencies) and the score section says plainly that **all three
legs — Survive, Earn, Abate — are scored on the company**, and that this is the structural reason a
maximiser can win by transferring.

**This re-reads a finding already on file.**
`WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25` diagnosed
the cap-seeking as a **missing ceiling in the churn model**. That repair is real and still wanted. But
a ceiling cannot repair a score with a side missing: the maximiser was optimising a one-sided
objective *correctly*. A two-sided score makes cap-pricing unattractive on the merits rather than
merely unreachable. Both fixes stand; the order changed.

### 2. Three currencies — and time is not "thin", it is absent

Verified rather than repeated. **Observed-with-evidence, 2026-08-28:** no time-, hours-, effort- or
hassle-as-value symbol exists anywhere in `company/`, `simulation/`, `saas/` or `tools/`, and no
design document names time as a currency. Of the six cells, **time is the only one that is absent
rather than uninstrumented** — carbon is designed and unwired (`E5`); household money is unmeasured
but computable from figures the run already has.

What time would cost, stated so it can be priced later: it needs a household model of what things
cost in **attention** — a switch, a query, a bill dispute, a meter read — and that model belongs
behind the wall with the other hidden traits. `C31`, idle, sequenced behind the household atoms.

### 3. The enterprise value is the method, not the book

**This one bit within the hour.** `saas/enterprise_value.py` — the only module in the repository
carrying the mission's own noun — defines it, in its own docstring, as *"the portfolio-wide sum of
the resulting per-account CLVs: the total discounted future net margin of the customer book."* That
is exactly the definition you superseded, and it is on the live phase-4c path, not a stale comment.

**I am not proposing a rename.** The CLV roll-up is correct and useful and keeps its name in its own
domain. What is missing is that **nothing measures the method**: how reliably the machine finds an
individual customer it can create value for, what finding one costs, and whether either improves.
Filed as `WORKER_FINDING_THE_ONLY_MODULE_NAMED_ENTERPRISE_VALUE_MEASURES_THE_BOOK_2026-08-28`, atom
`A48`.

## The channels: noted, not fixed, as you instructed — with which one is which

- **Tariffs — LIVE, and the only channel that reaches a household.** Renewal rate → churn decision
  in `simulation/customer_events.py` → the household's outcome changes.
- **Personalised modelling — EXISTS, pointed at us.** `company/analytics/customer_value_view.py`
  says it in its own words: *"the supplier's OPINION about value and retention."* Modelling **of**
  customers for our decisions, never modelling **for** a customer. Nothing it computes is offered to
  the household it is about.
- **Advice — MODULES ON DISK, NO RECIPIENT.** `switching_recommendation.py` renders inside the
  portal; `decarb_recommender.py` is discovery-wired. **Nothing in `simulation/` consumes a
  recommendation** and no simulated customer visits the portal. Built everywhere except where it
  would matter.

## What I rejected, and why

- **Rejected: rewriting the carbon commitments down.** Carbon is now one of three currencies, not
  the mission — but `E5`, the SAVED/SPENT/NET ledger and the £273/tCO₂e yardstick all survive at
  their levels, and the front door still carries the score and its honest NOT YET MEASURED tag. Your
  sentence demoted carbon's *monopoly on the purpose*, not carbon.
- **Rejected: editing the ratified pitch bodies.** `PITCH_V7` is director-authored canon with an
  explicit do-not-self-edit rule. It gets a supersession banner; the argument, the market read and
  the £/tCO₂e formula stay verbatim.
- **Rejected: building any of the three channels now.** You said note it. `C30` and `C31` are minted
  **idle** with the sequencing stated: an advice channel delivered into a world where nothing
  responds (C2), scored by an objective with no household side (`A47`), produces a capability that
  cannot be measured. Same argument that parks `C29`. DISCOVER and FRAME on both are drawable now.
- **Rejected: leaving the site to a later pass.** The canon page's own reading rule makes a
  superseded mission on a live surface a claim-status defect, and the front door said the old
  sentence in five places. It now also states, on the page rather than in a footnote, that two of
  three currencies and two of three channels are not built.

## Four things this invalidates that were true this morning

1. **The headline is now evidence, not the thing.** £153,245 vs £157,913, level explains 102.4%,
   choosing worth −£175 — all still correct, all still about the **book under two internal
   policies**. Under the old mission that was the result. Under this one the result is unmeasured.
2. **Every A/B taken so far is one-sided twice over** — against a market that cannot react (your C2)
   *and* on a score with no household term. The second is new today and is the larger of the two,
   because it applies even after B10's defence leg lands.
3. **P9's ground has moved** (`A46`). My note argued 80 founders because nothing compounds and, since
   yesterday's ladder, because nothing is measurable. Both still hold. But the trade-off is no longer
   growth-versus-science: under this mission, **width is the *finding* half of the method and depth
   is the *creating-and-sharing* half**, so the choice is between measuring two halves of the same
   asset. That does not settle it — it is still yours — but the P9 note now understates the case for
   width, and I am flagging that rather than quietly re-recommending.
4. **`docs/design/THE_WORLD_MUST_PRESS_SEQUENCE.md` keeps its order and gains its reason.** Fidelity
   was the goal; it is now the precondition, because **a world that cannot press cannot tell value
   created from value transferred**. P1–P10 do not re-sequence. What changes is that they are no
   longer realism for its own sake.

## The household side is now measured — in the same change, not the next one

`A47` is at **level 2**: `company/analytics/household_value_share.py` computes, per customer-year,
what a household paid us against what it would have paid on the published default tariff at its own
metered volumes, and how the resulting surplus split between it and us. The price ladder reads it, so
every rung now reports both sides.

**A real dual-fuel household, priced against the 2022 Ofgem default (TDCV: 2,700 kWh electricity +
11,500 kWh gas):**

| our position | household paid | would have paid | **household kept** | we kept (gross) | household's share of the split |
|---|---|---|---|---|---|
| −20% | £1,274 | £1,593 | **£319** | £319 | 50.0% |
| −10% | £1,434 | £1,593 | **£159** | £478 | 25.0% |
| −5% | £1,513 | £1,593 | **£80** | £558 | 12.5% |
| **at the cap** | £1,593 | £1,593 | **£0** | £637 | **0.0%** |
| +10% | £1,752 | £1,593 | **−£159** | £796 | −25.0% |

Your sentence is the bottom two rows: at the cap the household keeps **exactly zero** and we keep the
lot — and the row below it is not a smaller version of the same thing, it is the household paying us
£159 for the privilege. `test_pricing_at_the_counterfactual_shares_nothing` pins the zero.

**It is measured and it is NOT scored, and that gap is yours to close.** Wiring a household term into
a decision surface changes what the company does, which is a difficulty change and therefore R13's
and yours. So the figure is barred from every company organ, world module and draw by
`tests/company/test_household_share_is_not_yet_a_target.py`, which names its own release: your
decision on the two-sided objective. **My recommendation, and I will take it if nothing comes back:
score the two sides jointly and let the maximiser see both.** That is the smallest change that makes
cap-pricing lose on the merits rather than by a ceiling.

**Three defects of mine were caught before this ran, all by looking at real inputs rather than at
output.** A half-covered year compared a whole year's payments against a partial counterfactual. An
uncovered year reported a confident negative saving where the truth is "we cannot say". And the
settled book is **dual fuel** — the first draft would have valued every household's *gas* at the
*electricity* tariff, roughly four times over, silently, in our favour. All three are now named
tests.

**One honest bound, published rather than smoothed:** the gas default tariff is only published from
2019, so a 2017 customer-year has 19% coverage — electricity only — and the module reports that
rather than valuing gas at a substitute rate.

## What I am doing next, unless you say otherwise

`A47` — the household side of the score, in the one currency that is computable today: **money saved
against a stated counterfactual**, per customer, per renewal. That is the cell the maximiser needed
and did not have, it is the precondition for `A48`, and it needs no book change and no decision from
you. It also gives the price ladder a continuous, two-sided surface — which is the same measurement
gap the ladder hit yesterday, arriving from the mission side.

## Two things the rewrite itself triggered

**The mission claims are now machine-checked, where they can be.** A45's drift check went live this
morning (another lane, `tools/canon_drift_check.py`) and I registered the advice channel against it as
two claims: the world never reads `switching_recommendation`, and never reads `decarb_recommender`.
Both HOLD; both mutation-proven to report SUPERSEDED the moment a world module reads either. So the
day advice reaches a household, the page is told — nobody has to re-read it.

**Two mission claims are NOT registerable and I did not fake it.** "Time has never appeared" is the
absence of a *family* of names, and any single token probe would pass trivially. "The score has no
household side" would have to bind to a name that does not exist yet, which goes fail-silent if the
build picks a different one. Both are stated on the page with their evidence and carry atoms
(`C31`, `A47`) instead. This is the register's own rule — a claim needing a judgement call is not
registerable — applied against my own work.

**CLAUDE.md is at 12 characters of headroom, and its own rule says that is a trigger.** The mission
block put the file over its 35,000-char hard limit; the control caught it. I paid for it out of decay
rather than out of the mission — the largest single cut was 400 chars describing a model-tiering pilot
that **ended on 2026-08-19** and is off by mechanism, and the rest came from enumerations that now
live in code (the deleted permission surface is held by a test, not by prose). MAKE IT STICK says
re-run the decay audit at headroom <500 chars. That is now due and is not this piece of work; it is
the next harness item.

## The headline reversed while I was working, and I cannot yet tell you why

The site refused my commit: the published run and the A/B baseline arm had diverged by £6,179. The
A/B artefact was from 07:36 and the market gained the ability to **defend** at 08:25, so the
comparison was describing a world the site no longer runs. I re-ran it (35 minutes). The baseline arm
now reproduces the published run to 6.75×10⁻⁹ of a pound, and the result has turned over:

| arm | net margin | churned |
|---|---|---|
| flat rules (control) | £159,423 | 35 |
| per-customer (value arm) | **£154,699** | 46 |
| flat-at-level, £44.50 | **£164,326** | 38 |

The per-customer arm now **loses £4,724** to flat rules; the level arm **beats** them by £4,903;
selection is worth **−£9,627**. This morning it was flat £153,245, per-customer £157,913, level
explaining 102.4%, choosing −£175.

**I am not telling you the defending market caused this, because there are two candidates and I
nearly named only the interesting one.**

1. **The chase.** The mechanism fits exactly — the value arm prices high, and the world can now take
   those customers. It churns 46 against the control's 35.
2. **A clock repair I nearly missed.** The tree this run executed carries another lane's
   *uncommitted* `simulation/settlement_clocks.py`, which re-derives `total_net_gbp` **after** the
   bad-debt and debt-recovery mutations. That is the exact field every figure above is read from,
   and their own note puts the discrepancy it repairs at £39,962.17. This reversal is reproducible
   with no world change at all.

The experiment that separates them is one chase-off A/B on this same tree. It is running next, and
it is B10's coupled-triad measurement arriving through the **P&L** — which has no 1/17 quantum —
after yesterday's churn instrument could not resolve it.

**Two things about that run you should know before the number.** It is not reproducible from any
commit: HEAD was `01ac4b751` plus three files from a lane still in flight. And the error bar beside
the published figure is now **older than the figure it bounds** — measured 2026-08-27 in a market
that could not react, published beside a 2026-08-28 estimate in one that can. The page says so, in
a sentence derived from the two runs' own timestamps rather than written down, so it will keep
saying it for the next world change too.

## Still live
