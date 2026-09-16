**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `seven-knowledge-pages-now-say-unchecked-and-nobody-has-checked-them`) · **Class:** `figures_on_a_superseded_clock`

# Three of the seven unchecked pages are checked, and the correction this project already made once had not survived the rewrite

**2026-09-10.** Premise re-measured first and it is **live**, not spent. The three commits the
drawn item cites (`bedb08ea4`, `6ad1aa5d3`, `fd9d6292a`) are ancestors of `origin/main`, but they
are the commits that *made the debt visible*, not the commits that pay it.
`site/data/knowledge_review.json` read `{due 0, unchecked 7, stub 0, fresh 9}` at the start of this
turn and all seven bodies carried `last_verified: null`. Nobody had done the work.

Three pages checked against published source this turn, by the route recorded in `bedb08ea4`: read
the body feed, check the assertions, write the verification back. **No page was rendered at any
point** — they are JS-rendered and the static HTML holds no claims.

Tally moves **`{unchecked 7, fresh 9}` → `{unchecked 4, fresh 12}`**. The remaining four —
`electricity-wholesale`, `gas-wholesale`, `imbalance-cashout-settlement`,
`hedging-forward-market` — are untouched and still say "Written, awaiting check", which is the
honest state and is what a reader is shown.

---

## 1. The headline finding: a correction made in August did not survive the body moving house

The drawn item supplied the best available prior — on 2026-08-19 the same exercise over these
topics' **predecessors** found two of six materially wrong. Both of those corrections were tested
against the bodies written on 2026-08-24 to replace them. **One of the two had been lost.**

**`carbon-price` — the CPS correction was gone, and this is a real error a reader was being told.**
On 2026-08-19 the predecessor page was corrected for calling Carbon Price Support "a tax per
tonne"; it is not, and the correcting commit spelled out why it matters practically. The body
written on 2026-08-24 opened with *"A carbon price is a cost per tonne emitted"* and named the
top-up without ever saying what it is charged on. Not a verbatim repeat of the old sentence — and
wrong in exactly the same way, so a reader who went looking for the rate was sent to the wrong
table.

Corrected in the reader's view, with the published rates rather than only the mechanism: CPS rates
sit inside the Climate Change Levy and fuel duty, are levied **per unit of fuel supplied for
generation** — 0.331p/kWh gas, 5.28p/kg LPG, 1.5479p/GJ solid fuels — and were frozen in 2016,
running unchanged to 31 March 2028 at a level calibrated to about £18/tCO₂.

**The same conflation had a second home.** The topic graph's `blurb` for `carbon-price` read *"…
added to every tonne burned"*, and `site/knowledge/index.html` held a hardcoded copy of it. Both
corrected. `test_the_card_copy_is_quoted_from_the_record` caught the index copy the moment the
record moved — that control worked, and it is why the second home did not survive this turn.

**A second, smaller finding on the same page.** Its `no_current_level` refused to state *any*
number. That is right for UK ETS allowances, which trade continuously; it was wrong for CPS, which
is frozen by statute to 2028. The blanket refusal withheld a stable published fact and left the
reader holding only the per-tonne framing the page had got wrong. An honest refusal has to name
which quantity it is refusing.

**`merit-order-residual-demand` — the other August correction was not violated, but its substance
was absent.** The predecessor said generators "are dispatched cheapest-first", a description of the
Pool that GB abolished in 2001. The new body never names a dispatcher, so it is **not wrong** and
is recorded as *checked*, not *corrected*. But it never says there isn't one either, and "work
along the line until it is met" invites the reader to supply one. The August commit had recorded
why this matters beyond wording — self-dispatch against contracted positions is what makes the
merit-order page and the imbalance page one story rather than two. Stated explicitly now.

## 2. What else the check turned up

**`gb-electricity-market` — a dated fact stated in the present tense.** The page's account of
buying, truing up and settling is correct and stands. Its settlement timetable is not timeless:
"re-run repeatedly over more than a year" is a true description of **2016–2025, the record this
simulation is built on**, and MHHS is compressing it on a published schedule — go-live 22 September
2025, Final Reconciliation from 14 months to seven for settlement days from **1 October 2026**
(three weeks after this check), seven to four from 1 April 2027, migration to May 2027. Nothing on
the page told the reader which of the two it described. Now dated, with the run names (II, SF, R1,
R2, R3, RF) a reader would need to look any of it up.

**Also narrowed on that page:** *"A supplier is not a participant"* in the Balancing Mechanism.
True of a domestic supplier and of this simulation's company; not true as a rule, since a supplier
with generation can hold a BM unit and virtual lead parties route domestic flexibility into the BM
without being the supplier. Narrowed to the claim the evidence supports.

**Confirmed unchanged, and worth recording because a check that confirms is still a check:** the
0.35 tCO₂/MWh CCGT intensity and the ~0.35 £/MWh-per-£/tonne pass-through slope that rests on it
(published estimates run ≈320–353 kgCO₂/MWh); the roughly 2:1 gas-to-power slope; gate closure at
one hour ahead; the five market layers and their order; residual demand as the selector of the
marginal plant; bimodality under rising renewable penetration. And the single-price-zone note is
now a *decided* question rather than an open one — DESNZ's REMA Summer Update of 10 July 2025
rejected zonal pricing and confirmed reformed national pricing.

## 3. The generalisable shape

**A correction is attached to a body, not to a topic, and rewriting the body drops it.** The August
work corrected six pages. Six weeks later a worker replaced their bodies wholesale, from
"established market mechanism", and one of the two corrections came back. Nothing could have gone
red: the correction lived in prose, and the control that would later catch the *date* drifting
(`test_a_review_date_describes_the_body_it_serves`) is deliberately not a check on whether a page
is correct.

This is the same class as `figures_on_a_superseded_clock`, one level up: not a figure on a stale
clock but a *correction* on one. It is why the remaining four pages should be checked against the
predecessors' correction list and not only against source — the cheapest question to ask of any
rewritten body is "what did we already know about this page, and does the new text still say it?"

## 4. What is next

Four pages still read "Written, awaiting check" and that is accurate: `electricity-wholesale`
(five of its seven rungs written 2026-08-24), `gas-wholesale`, `imbalance-cashout-settlement`,
`hedging-forward-market`. `electricity-wholesale` is the one to take next — it is the topic graph's
own body, it is the most-read of the four, and its `superseded_check` note already records that its
badge was rendering a 2026-07-25 date over a body five-sevenths written a month later.
