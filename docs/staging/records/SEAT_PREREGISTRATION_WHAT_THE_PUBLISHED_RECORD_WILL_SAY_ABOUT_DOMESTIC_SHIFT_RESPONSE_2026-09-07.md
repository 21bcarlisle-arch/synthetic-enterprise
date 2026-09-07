# PREREGISTRATION — what the published record will say about domestic shift response

**Filed:** 2026-09-07, BEFORE reading any source.
**Claim:** `a49-shift-response-as-a-function-of-pass-through`
**Subject:** the named gap in `docs/observability/tou_sharing_ceiling.json` — *"THE SHIFT RESPONSE
as a function of pass-through ... nothing in the knowledge layer, the commons or the market
research establishes one. A question to research."*

This file is written before a single source is opened, so that the reading can refute it. Nothing
below is evidence. It is what I expect to find, recorded so that being wrong is visible.

---

## P0 — the definitional split I expect to be the whole difficulty

**Predicted, and this is the prediction I am most confident in and which most changes the work:
no published source measures response against "pass-through" at all.** The trials measure response
against a **price differential** — a peak-to-off-peak ratio, in p/kWh, on a tariff a household was
actually put on. The frontier in `tou_sharing_ceiling` is parameterised on the **share of created
value that reaches the bill**. These are not the same quantity and the difference is not a
rescaling:

- a *pass-through share* is dimensionless and is about how a surplus is divided;
- a *price ratio* is a property of the tariff a household sees, and it is what a household can
  actually respond to.

So I predict the deliverable is a **composition of two things, not one number**:

1. a **bridge** — pass-through share α → the peak-to-off-peak price ratio a household on this
   book's own price series would actually face at that α. This is **measurable in this repository**
   from the Elexon MID half-hourly series the ceiling already reads. It is arithmetic on our own
   data, not a literature question.
2. a **response function** — price ratio → share of shiftable load actually moved. This is the
   literature question, and it is the only part that can be *established* rather than computed.

If I find a source that genuinely measures response against value-share pass-through, this
prediction is refuted and I will say so here.

## P1 — what the literature will actually contain

**Predicted:** no continuous GB function exists. What exists is (a) a small number of GB trial
POINTS, and (b) one international meta-analysis that fits a continuous arc across many pilots.

- The meta-analysis I expect to be the load-bearing source is Faruqui & Sergici's pilot database
  (the "Arcturus" work), which fits peak reduction against peak-to-off-peak price ratio and finds
  a **concave, saturating** curve with a clear **split between households with enabling technology
  and households without**. I predict the without-technology arc is far the more relevant one for a
  book of ordinary domestic accounts.
- GB-specific points I expect to exist and to be lower than the international central case:
  **Low Carbon London** (UKPN, dynamic ToU, ~1,100 households) and **Customer-Led Network
  Revolution** (Northern Powergrid). I expect both to report **single-digit to low-double-digit
  percent** peak reduction.
- I expect **Octopus Agile** to have published or third-party analysis, and I expect it to be
  **unrepresentative upward**: a self-selected population that chose a half-hourly tariff is not
  this book.

## P2 — the magnitudes, stated as numbers so they can be wrong

At a realistic domestic peak-to-off-peak ratio of about **2–3x**, I predict the published central
response for households **without** enabling technology is **3%–10% of peak-period load moved**,
and **with** enabling technology (storage heating, EV, battery) **15%–30%**.

I predict the arc **saturates**: doubling the price ratio well past ~5x buys much less than the
first doubling, because what is left is load that is not physically movable.

## P3 — the consequence for the ceiling, predicted before it is computed

`tou_sharing_ceiling` publishes **£51.36 per household-year** at shiftable share 1.0 and perfect
compliance. **I predict that composing a real response function with a real shiftable share brings
the reachable figure down by roughly one order of magnitude — to single-digit pounds per
household-year — and that this is the finding, not a disappointment.** A ceiling that survived
contact with a measured response would mean the ceiling was not a ceiling.

I predict the **interior optimum sits at high pass-through, not in the middle** — nearer α = 0.6
than α = 0.3 — because a saturating response means the company's share of a rapidly-growing pie
beats a large share of a small one until quite late. I hold this one weakly; it is the prediction I
most expect to be wrong, because it depends entirely on the arc's curvature, which I have not read.

## P4 — what I expect NOT to be establishable, and will file as a gap rather than fill

- **Persistence.** Whether a trial's measured response survives beyond the trial's own novelty
  window. I expect most GB trials are too short to say.
- **Response to the *carbon* signal at zero pass-through.** The instrument already names carbon as
  the one thing that moves at α = 0. I do not expect published evidence of a money-free carbon
  shift response at domestic scale, and I will not invent one.
- **The shiftable share itself.** That is R3's own named gap and it is a *different* question
  (what fraction of load is physically movable) from this one (how much of the movable fraction a
  household actually moves for a given price signal). I predict I will be tempted to conflate them
  and that the two multiply.

---

## How this file gets graded

Against `docs/market_research/domestic_shift_response_as_a_function_of_pass_through.md` when it
lands. Each of P0–P4 is either borne out, refuted, or unaddressed, and the refutations are written
into that file **beside** the claim, not here. This file is not edited after the reading starts.
