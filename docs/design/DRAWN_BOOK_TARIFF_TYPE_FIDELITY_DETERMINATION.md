# Should the drawn book carry a `tariff_type`? A fidelity determination

Decided 2026-08-28, delivery seat, on the direction issued after `4be65df49`.
R13 governs: this is a **baseline-world** question, decided on fidelity-to-reality
evidence and blind to what it does to company P&L or to the value-cycle A/B's
decision surface.

**RULING IN ONE LINE.** It **is** a fidelity defect, it is **not** the labelling
defect it was reported as, and the repair is **not** to set the field. Setting the
213 drawn accounts to `fixed` would move the world from *silent* to *100% fixed*
against a published domestic fixed share of roughly **one third**, which is a
fidelity **regression** asserted as a correction — and the only thing it improves
is `n`. The field stays unset. What is owed is a standard-variable product the
world does not have.

---

## (a) What these accounts ARE in the world today

Verified by executing the settlement path, not by repeating the commit message.

**The mechanism is one line sharper than reported.** `4be65df49` says
`_draw_one` "never sets" `tariff_type`. It is worse than unset:
`to_customer_dict()` (`simulation/population_draw.py:280`) renders
`"tariff_type": self.tariff_type` **unconditionally**, so the key is **present
with value `None`**.

Census of the electricity book (`simulation.run_phase2b.ELEC_CUSTOMERS`, 222
accounts):

| population | `tariff_type` | what `.get("tariff_type", "fixed")` returns |
|---|---|---|
| 213 drawn | key **present**, value `None` | **`None`** — the default is defeated |
| 9 hand-authored seed | key **absent** | `"fixed"` — the default works |

The two populations are exactly disjoint, and the `.get(..., "fixed")` calls at
`run_phase2b.py:1124` and `:1144` exist to prevent precisely this outcome. They
are dead code on 96% of the book. A rendered `None` is not the same census as an
absent key — this is the same class as the memory note on unset Optionals sizing
every downstream experiment.

**Every downstream branch then takes the fixed path.** With
`tariff_type=None` passed explicitly, `build_renewal_schedule`'s own
`tariff_type: str = "fixed"` signature default is bypassed too, and:

| site | branch | outcome for `None` |
|---|---|---|
| `renewals.py:175` | `if tariff_type != "flex"` | **True** → locks `prev_fixed_unit_rate` |
| `renewals.py:188` | `== "flex"` | False → no flex markup |
| `run_phase2b.py:1395` | `in ("deemed","flex")` | False → **not** indexed |
| `run_phase2b.py:1996` | `== "deemed"` | False |
| `run_phase2b.py:2004` | `== "flex"` | False |
| `run_phase2b.py:2086/2148/2199` | `== "pass_through"` | False |
| `run_phase2b.py:2183` | `naked_kwh` | `aq_kwh * (1 - hf)` → **hedged as a fixed contract** |

Each term is priced through `request_renewal_offer` and carries a real
`unit_rate_gbp_per_mwh`, on contiguous 365-day terms, with an active renewal
decision at every boundary.

**So the commit's description is confirmed:** the world settles these as ordinary
annual fixed-term contracts with locked rates, whose product was never labelled.
The company's `UPLIFTABLE_TARIFF_TYPES = {fixed, pass_through}` check receives
`None` and refuses all 213.

## (b) The external anchor

Already in the repository commons — no new fetch needed, and the regulation-commons
doctrine makes it readable by every lane:
`docs/market_research/svt_rates_active_passive_2016_2025.md` (Ofgem, CMA, DESNZ,
HoC Library; H-confidence on the split figures) and
`docs/market_research/company_commercial_strategy.md`.

Domestic fixed-versus-variable share across the run window:

| window | on a fixed deal | on SVT / variable | source |
|---|---|---|---|
| 2016 | <30% | **70%+** | CMA 2016, Big Six domestic (H) |
| Sep 2017 | ~43% | **~57%** | Ofgem, non-PPM, 10 largest suppliers (H) |
| 2019–20 pre-crisis | **~44–46%** | ~54–56% | `company_commercial_strategy.md` |
| late 2021 – Apr 2023 | **~10–20%** | ~80–90% | fixed deals withdrawn; ~29m on SVT by Apr 2023 |
| Jul 2025 | **~33%** | ~67% | Ofgem State of the Market, Jan 2026 (H) |

**In every single year of the window the domestic fixed share is a minority**,
ranging ~10% to ~46% and centred near one third.

**This is a domestic book, so the domestic statistic governs.** Measured on the
live roster: **220 of 222** electricity accounts are `resi` (2 SME); **395 of 397**
accounts overall. The SME carve-out — where fixed-term contracts genuinely *are*
the dominant structure — covers two accounts and cannot carry the change.

## (c) The ruling

### It is a defect, and the defect is not the label

The world settles **100%** of drawn domestic accounts as annual fixed-term
contracts with a locked rate and an active renewal decision. Reality puts roughly
**one third** of domestic accounts on a fixed deal at any point in the window, and
the other two thirds on a standard variable tariff **with no renewal decision at
all**.

The world has no standard-variable product. `build_renewal_schedule` can settle
exactly four types — `fixed`, `flex`, `deemed`, `pass_through`. SVT exists in the
world only as a **comparison benchmark** (`rate_vs_svt_pct`,
`run_phase2b.py:599–621`) and as a published observable handed into the renewal
offer. It is never a settled product. `deemed` is out-of-contract spot + 20%: a
*gap between* contracts, not a variable tariff.

**`tariff_type is None` is the symptom.** The field was never decided because the
world only has one domestic product to offer.

### Why setting the field to `fixed` is refused

It has no fidelity argument of its own once the distribution is consulted. It
would replace an honest silence with a distributional claim the anchor refutes by
a factor of about three. It would also — not coincidentally — take the A/B's
decision surface from 25 to roughly 213. R13's test is whether the change would be
made blind to that consequence, and it would not be, because after the anchor is
read the only thing the change improves is `n`. That is the change R13 exists to
stop, and the direction issued with this work said so in advance: *what is not
allowed is setting the field because it makes n bigger.*

### The discriminating precedent is in the same file

`smart_meter` (`population_draw.py:388`, `:752`) was a legitimate baseline-world
correction, and its own comment states the test it passed: drawn from a **published
national series** (DESNZ Q4 2024 Smart Meters Statistics Table 5a, 10.6% (2016) →
68.9% (2024)), decided blind to P&L, and it made the book **harder** to serve.

The proposed `tariff_type` change has the same shape and the opposite provenance:
no published series behind the value it would assign, and it makes the company's
own experiment easier. **Same shape, opposite sign.** That is the whole ruling.

### What is owed instead

A **standard-variable product in the world**, drawn from the published year-by-year
domestic fixed/SVT split above: no locked unit rate, no term boundary, cap-bounded
from Jan 2019 (`simulation.svt_rates` already holds the series), and ongoing
inertia churn in place of a renewal decision. The anchor is already in the commons
and is H-confidence on the split.

This is a real baseline-world fidelity atom with a strong external anchor. It is
**not a one-turn change** and it must not be executed as a label assignment. It is
registered as owed, exactly as `4be65df49` registered this question as owed.

### Consequence for the A/B — recorded as a consequence, not a reason

When that repair lands honestly the renewal-pricing decision surface gets **smaller
as a share of the book**, not bigger, because two thirds of domestic accounts would
correctly have no renewal decision to price at all.

The direction anticipated a permanent finding in its "not a defect" branch — that
per-customer pricing can only touch a small part of a real domestic book. **That
finding stands, for a better reason than the one proposed.** It is not a plumbing
artefact and it is not something to be engineered away: it is market structure.
Roughly one third of a domestic book is on a fixed deal at any time, and only that
third has a renewal rate that can be moved.

So 25 is not the right number either. Once the world is honest the in-scope surface
is on the order of **a third of 222 ≈ 70** electricity renewals — arrived at by a
fidelity argument, not by removing a guard. The A/B's power problem is real and is
not solved by this change; it is bounded by how much of a domestic book per-customer
pricing can legitimately reach.

---

## Mechanism, not prose

Per MAKE IT STICK, this determination is enforced rather than exhorted:
`tests/simulation/test_drawn_book_tariff_type_fidelity.py` pins the verified
settlement behaviour above and **ratchets against the unanchored repair** — it
fails if the drawn population is given a blanket upliftable label, and passes for
an anchored distribution. R15 mutation recorded in that file's docstring.

---

## Addendum, 2026-08-30 — the census re-measured, and one thing it could not see

Re-measured on the roster `simulation.run_phase2b` binds today, because the census in
section (a) is now stale in its counts and — more importantly — was taken over the
**electricity book only**, which is exactly where the defect is uniform and therefore
where it looks like one fact rather than two.

| population | electricity legs | `.get("tariff_type", "fixed")` | gas legs | `.get(...)` |
|---|---|---|---|---|
| won by the funnel (`net_new_won`) | 90 | key **present**, `None` | 86 | key **absent** → `"fixed"` |
| drawn by the curriculum (`synthetic_draw`) | 51 | key **present**, `None` | 18 | key **present**, `None` |
| founder, hand-authored | 9 (+6 successors) | key **absent** → `"fixed"` | 4 | key **absent** → `"fixed"` |

Two readings follow, and the second is new.

**The ruling above is confirmed and is now measured rather than argued.** All 141
electricity legs the company found — every one of the 90 it won and the 51 it drew —
resolve to `None` and are refused at `UPLIFTABLE_TARIFF_TYPES`; all 15 founder
electricity legs omit the field, take the `"fixed"` default and are admitted. The gate
is a property of the record shape, so **no book size opens it**: the first won household
is not priced at any book size, only at a world that gives it a product. That sentence
is on the live arms page, and its premise is now published beside it as
`renewal_funnel.product_label_by_account_class` rather than asserted in prose
(`tools/run_value_cycle_ab.py`, controls in `tests/tools/test_the_renewal_funnel.py`).

**A won account's two legs disagree about whether its product was ever decided.** The
electricity leg carries the key present and `None`; the gas leg omits it and takes
`"fixed"`. 86 billing accounts, one per won dual-fuel customer, because the two legs are
minted by different paths — the electricity leg through
`population_draw.to_customer_dict`, which renders the key unconditionally, and the gas
leg by a constructor that never mentions it. Section (a) could not see this: it censused
one commodity, and within that commodity the answer is uniform.

It is **latent, not active**. The commodity guard refuses gas one stage earlier
(`not_the_arms_commodity`, 429 renewals), so nothing today reads the gas leg's label. It
becomes live the moment any writer prices gas — at which point 86 won gas legs would be
priced as a *fixed* product on the strength of a default nobody chose, while their own
electricity legs record that the product was never decided. **The repair is the same one
this determination already registered as owed** — a product distribution the world
actually draws — and it must cover both legs of an account, not the electricity book
that happened to be censused first.

Recorded here rather than as its own finding because it is the same defect as the one
ruled on above, seen at a second call site: a default defeated by one minting path and
relied on by another, in one account.
