# Choice and channel — the roadmap, with every simplification named

**Date:** 2026-08-30. **Author:** the delivery seat. **Status:** ROADMAP, sequenced.
**Occasion:** `docs/staging/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md`, WORK item 3 —
*"sequenced, with each simplification named alongside what it would take to do properly."*

Reads on: the knowledge (`site/knowledge/how-households-choose/`,
`site/knowledge/the-price-a-household-is-shown/`) and the discovery
(`docs/design/CHOICE_AND_CHANNEL_DISCOVERY.md`). Folds in, and does not restart,
the standing S1–S6 roadmap in `docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md`.

---

## 0. What the brief changed about how this gets decided

Section 7 delegates something that has previously stopped work. Curriculum values remain the
director's, **and** the instruction is to *"take them from published evidence and cite them;
where the evidence is ambiguous, choose the option that makes the company's advantage harder to
demonstrate, record why, and move on."*

That is a standing tie-break, so no step below stalls on a value. Each step states which of its
numbers is a curriculum value, where it was taken from, and — where the evidence was ambiguous —
which direction the choice errs and why that direction is against our own thesis. Anything that
would *tune an output* still stops and goes to the console.

---

## 1. The sequence, and why this order

**C1 SVT product → C2 departures with a cause → C3 the quoted price → C4 channel →
C5 a market rather than a number → C6 home moves.**

C1 is first because it is the only item already costing a published result, and because C2
cannot be done without it: a departure from a variable tariff is a different event from a
departure at a term end, and a world with only the second can only ever have one cause. C3 is
independent of both and could be done at any time; it sits third because C4 and C5 need
somewhere to show a price and there is nothing to show one on until it exists.

The compounding item is C2. Everything before it makes the reason distribution possible and
everything after it makes it richer.

---

## C1 — A standard variable product, generated from behaviour

**Brief WORK item 4. The repair `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` registered as
owed on 2026-08-28 and re-measured this morning.**

The world settles 100% of drawn domestic accounts as annual fixed-term contracts with a locked
rate. The published domestic fixed share is a minority in every year of the window. The repair is
a settled variable product: **no locked unit rate, no term boundary, cap-bounded from January
2019 off the series `simulation/svt_rates.py` already holds, and an inertia hazard in place of a
renewal decision.**

**Generated, never drawn.** A household is on SVT because of something that happened to it:
never engaged; a fixed term ended and it did not act; or it moved in and inherited the
incumbent. The published year-by-year split is the **check on the output**, printed beside the
result, and is never an input. If the split has to be set to land in range, the behaviour is
wrong and setting it would hide that.

**What this is worth.** The value arm has never priced a customer the company won: 158 of 168
accounts unreached, because `UPLIFTABLE_TARIFF_TYPES` receives `tariff_type` present-and-`None`.
C1 does not remove that guard — removing it is the change R13 exists to stop — it gives the
accounts a product, and the determination's own arithmetic puts the honest in-scope surface at
roughly a third of the electricity book, about 70 renewals against 25 today.

**Simplified:** the third route on — a home move onto a deemed contract — does not exist in the
world at all, so the generated split comes from disengagement and lapse alone.
**To do it properly:** a housing-move stream (C6), with tenure-conditioned move rates.
**What it would change:** the SVT share comes out **too low**, because a real route on is
missing. Direction recorded in advance: this errs against our own thesis by leaving more of the
book priceable than reality would, so the measured in-scope surface after C1 is an **upper**
bound on the honest one.

**Simplified:** the inertia hazard is one rate for everybody at first.
**To do it properly:** condition it on the engagement type already drawn and wired
(Ofgem RMI 45/35/20).
**What it would change:** the variable book becomes bimodal — a sleepy majority and a small
population that leaves on the first bill shock — which is the shape GB retail actually has and
the shape a churn model can be right or wrong about. Cheap; do it in the same step if the first
half lands clean.

**Curriculum, and where it comes from:** the year-by-year fixed/SVT split, already held at H
confidence in `docs/market_research/svt_rates_active_passive_2016_2025.md`. Used as a check, not
a marginal, so no value is being set.

---

## C2 — A reason attached to every departure

**Brief WORK item 5, and the headline ask.**

Today five causes are multiplied into one scalar and rolled once, so a departure is not
unlabelled — it is **uncaused by construction**. The repair is to stop composing and start
competing.

**The mechanism.** Replace `p = p_base · Π m_k` with a competing-risks form: each cause carries
its own hazard, survival is `Π (1 − p_k)`, and the cause that fires names the departure. End of
fixed term. Dissatisfaction. Bill shock. A better offer seen through a channel (needs C3/C4;
until then it is one risk with a placeholder rate, declared). Home move (needs C6). Where more
than one fires, the tie is broken on a declared order and the tie rate is published, because a
model that resolves ties silently is a model whose reason distribution is an artefact of its
tie-break.

**This changes the aggregate and must not be allowed to change it quietly.**
`1 − Π(1 − p_k) ≠ p_base · Π m_k`, so churn rates move. Pre-register before touching anything:
write down what the aggregate should do and why, run the one-variable version, and keep the
prediction beside the result whether or not it survives. Two variables changing means no
attribution, and this step changes one on purpose.

**And it needs a fresh anti-goal-seek proof.** The present form carries `m(d)·m(−d) == 1` at the
population mean — being dearer costs departures in exactly the proportion being cheaper wins
them. That guarantee does not survive the rewrite for free and must be re-established, or the
step is a licence to make over-pricing cheap again.

**The thing that looks like progress and is not.** Keeping the composed probability and emitting
each factor's marginal contribution as an attributed "reason" is a third of the work and none of
the value. It is a story told after the roll, it cannot produce a departure the composed
probability would not have produced, and it would publish a reason distribution that is a
property of the decomposition arithmetic rather than of the world. Rejected explicitly, so that
it is not rediscovered as a shortcut.

**Simplified:** the cause-specific hazards are calibrated to reproduce today's aggregate churn
before any of them is allowed to be interesting.
**To do it properly:** each hazard anchored to its own published rate.
**What it would change:** nothing that can be sourced. The published record gives stated reasons
among **movers** (Ofgem, January–February 2024, base 174, multi-code: 44% cheaper tariff, 19%
reputation, 16% issues with supplier or tariff, 16% poor service, 15% good service), and a
stated-reason share among movers is not a hazard over everybody. Converting one into the other
needs an assumption the published record does not contain, and the Knowledge page says so. So
the mover-mix is the **check** — the simulated reason mix among departures should land near the
published one — and never the input.

---

## C3 — The price the household is shown

**Brief §4: *"model what the household is shown, not only what it would pay."***

Every household today responds to a true differential computed at its own billed consumption. No
real household can observe that. The published convention is exact: an annual figure at typical
consumption, 2,700 kWh electricity and 11,500 kWh gas, which is how the cap headline and every
comparison listing are constructed.

**The mechanism.** A `shown_price` alongside the true one — the tariff annualised at typical
consumption — and the switching decision keys on the **shown** differential while the settlement
keys on the true one. The gap between them is then a real quantity in the world, with a sign that
depends on where the cap sits relative to costs.

**This is the wall pointing the other way, and it should be said out loud.** The epistemic wall
is enforced on `company/` and `saas/`; nobody has written down that the *population* is deciding
on ground truth. C3 is an extension of the wall's principle into `simulation/`, not a breach of
it, and the discovery document records that judgement so it can be overturned rather than
discovered.

**Predicted direction, filed before the run:** households get **worse** at choosing, because they
are now deciding on a lossy number. 2022 should reproduce as a price effect through the
convention rather than by assertion. And the company's measured advantage should not improve —
if it does, the step needs re-reading before it is believed.

**Simplified:** one typical-consumption pair for every household, as published.
**To do it properly:** the real conventions are more than one — sites offer a
personalised estimate when the customer supplies usage.
**What it would change:** high-consuming households would see a number closer to their truth, so
the error would concentrate in the disengaged, which is plausibly the real pattern and is not
sourced. Left simple and stated.

---

## C4 — Channel

There is no channel anywhere in the world: every quote costs the same and is introduced by
nobody. The taxonomy is real and the cost structures differ in kind — a per-switch commission of
about £25–30 per fuel for a comparison site; an ongoing per-kWh trail of 0.5–2.0p for a small
business broker; and no published GB figure at all for direct brand.

**The mechanism.** A channel on every acquisition and on every departure — which channel showed
this household the alternative — with the per-channel cost structure attached. Retention is a
channel too and is the one the supplier owns.

**Simplified:** the channel **shares** are set as a curriculum value rather than sourced.
**To do it properly:** a primary series splitting GB domestic switches by acquisition route.
**What it would change:** the shares drive blended acquisition cost directly. The knowledge page
holds the PCW share at moderate confidence from secondary commentary, and the per-supplier CAC
that would settle it is redacted in the published CMA appendix. Under §7's tie-break the share
is set to the option that makes our advantage **harder** to show — the higher-cost channel mix —
and the reason is recorded on the page rather than in the code.

**Note for whoever does this:** `channel_pref` already exists, is drawn per household, is
coverage-tested and wall-guarded, and means something else entirely — `("digital", "phone",
"assisted")`, a service **contact** preference. It reaches no live behaviour. Do not overload it.
It is why this gap was invisible: a search for "channel" lands on a well-tested subsystem and
stops.

---

## C5 — A market rather than a number

`simulation/competitor_reference.py` landed on 2026-08-28 and gave the world a rival that
defends. It is a single scalar reference price. It has no identity, no product range, no offer,
and it cannot be seen.

**The mechanism.** More than one rival, each with an offer that can be **shown** through a
channel (C4) at a **quoted** price (C3), so that a household chooses between named alternatives
rather than responding to a differential. This is the step that makes "a better offer seen
through some channel" a real departure cause rather than a placeholder in C2.

**Simplified:** a small field of stylised rivals rather than the 23 active domestic suppliers
Ofgem counts.
**To do it properly:** a field whose size and concentration match the published market — six
largest at 91% domestic share.
**What it would change:** concentration determines how much of the market a household's shown
menu actually represents, which is what makes a long listing and a concentrated outcome
coexist. Worth doing once C4 exists; not worth doing first.

---

## C6 — Home moves

The third route onto a variable tariff, and absent entirely. A move onto a deemed contract is a
departure for the losing supplier with a cause, an arrival for the gaining one that was never
won, and the origin of a large share of the SVT stock.

Placed last not because it is least important — it is the missing half of C1's check — but
because it is the only step here that needs a population mechanism rather than a decision
mechanism, and it can be built against C1's product once that product exists.

**Simplified when it lands:** move rates conditioned on tenure only.
**To do it properly:** a housing-transaction and rental-churn stream.
**What it would change:** renters move several times more often than owners, and tenure is
already drawn and already reaches the churn decision, so the cheap version is not far off the
expensive one. Says so here so the expensive one is not assumed necessary.

---

## 2. What this roadmap does not do

It does not raise the ceiling `WHAT_A_HOUSEHOLD_DECIDES_ON.md` §4 identified — universal
response functions, so nothing latent to infer — except at C2, where a departure with a cause
becomes something a company can be right or wrong about for the first time. S3 in that document
(a per-household weight vector, so service can outrank price) remains the deep item and remains
unstarted. C2 and S3 compound: causes give the company a target with structure, and trade-offs
give households a reason to differ in which cause fires.

It does not solve the measurement problem. The level-versus-selection instrument needs 61 seeds
across 3 arms to resolve a £1,106 effect because a decade run prices about 30 renewals. C1
roughly triples that count by a fidelity argument, which helps and does not fix it. **No step
here should be judged by a single-run A/B figure**, and any step that appears to improve the
company's measured advantage should be re-read before it is believed.

And it does not touch the four reserved classes. Nothing here spends real money, contacts a real
person, makes a public claim under Poesys's name, or touches anyone's safety.
