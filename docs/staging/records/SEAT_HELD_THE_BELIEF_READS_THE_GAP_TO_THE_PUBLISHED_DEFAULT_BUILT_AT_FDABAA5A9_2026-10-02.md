**Claim:** `the-belief-reads-the-gap-to-the-published-default` (Lane 0) · **Base:** origin/main `fdabaa5a9` · **Status:** built, tested, NOT landed

# The belief reads the gap to the published default: built, held until items two and three land

This holds the code for the pre-registered remedy in
`docs/staging/SEAT_FINDING_THE_VALUE_ARMS_CHURN_BELIEF_PRICES_THE_MOVE_FROM_ITS_OWN_LAST_PRICE_AND_THE_WORLD_PRICES_THE_GAP_TO_THE_MARKET_2026-10-02.md`.
The grading and the reason it is held are in that finding's addendum. Apply with
`git apply` from the repo root on a base where these four modules have not moved since `fdabaa5a9`.
It was also left on the local branch `belief-reads-published-default` in `/var/tmp/wt-belief-gap`,
uncommitted. That copy is not durable. This one is.

## What it changes

- `churn_model.estimate_churn_probability` gets `reference_rate_gbp_per_mwh`. When given, the rate
  term reads `offer / reference - 1` and does not net `market_move_pct`, because the reference is
  already the market's level on the day. Bill stress still reads the last price. `None` leaves the
  current behaviour unchanged.
- `enriched_churn_estimate`, `decide_margin` and `renewal_margin_uplift` pass
  `published_default_rate_gbp_per_mwh` through.
- `renewal_rate_chain.decide_renewal_rate` supplies `cap_ceiling_ex_vat(commodity, day,
  multi_register=False)` for domestic electricity and gas, and `None` otherwise. That is the
  company's own reading of the published default, EPG-net, ex-VAT like the offer.
- No new constant. `RATE_SENSITIVITY`, size scale, saturation and the +83.1% support bound are
  unchanged.

## Controls (in the diff)

`tests/company/pricing/test_value_arm_in_the_renewal_chain.py`:
`test_the_belief_reads_the_offer_against_the_published_default_and_not_the_last_price` and
`test_the_published_default_reaches_the_belief_the_decision_scores`. Six mutations each turned
a control red:

1. The chain passes the electricity default to a gas renewal.
2. The adapter drops the argument.
3. The model ignores the reference.
4. The model nets the market move on top of the reference.
5. `enriched_churn_estimate` passes `None`.
6. `decide_margin`'s scorer drops the argument.

With the change applied, the 550 tests in the eight suites around these modules pass.

## The diff

```diff
diff --git a/company/crm/churn_model.py b/company/crm/churn_model.py
index a182b4e9d..dc9a6cf40 100644
--- a/company/crm/churn_model.py
+++ b/company/crm/churn_model.py
@@ -558,6 +558,7 @@ def estimate_churn_probability(
     segment: str = "resi",
     market_move_pct: float = 0.0,
     arrears_state: str = ARREARS_STATE_UNKNOWN,
+    reference_rate_gbp_per_mwh: float | None = None,
 ) -> float:
     """Estimate churn probability from observable renewal signals.
 
@@ -590,6 +591,17 @@ def estimate_churn_probability(
         fraction (0.667 = the market rose 66.7%). The rate response is taken on this
         customer's rate change NET OF IT -- see below. Defaults to 0.0, which is no netting
         and behaviour identical to every estimate this model has ever produced.
+    reference_rate_gbp_per_mwh: the company's own reading of the published default tariff for
+        this fuel on the renewal date, on the offer's VAT basis. When given, the rate term reads
+        the offer's GAP TO IT, and `market_move_pct` is not netted: the reference is today's
+        market level, so the market's move is already inside it. `old_rate` still sets the
+        bill-stress term. `None` is the move from `old_rate`, unchanged.
+
+        Why (2026-10-02): the move from the household's own last price ratchets with the
+        supplier's own uplifts. A household priced 1.7x the default last term reads a further
+        rise as small. Over 18 rolled value-arm renewals that input ranked churn at r = -0.12
+        against the world. See
+        `docs/staging/SEAT_FINDING_THE_VALUE_ARMS_CHURN_BELIEF_PRICES_THE_MOVE_FROM_ITS_OWN_LAST_PRICE_AND_THE_WORLD_PRICES_THE_GAP_TO_THE_MARKET_2026-10-02.md`.
 
     THE RATE RESPONSE IS ON THE SUPPLIER-SPECIFIC MOVE, NOT ON THE BILL (2026-08-25). A
     customer whose bill rises 60% because THIS SUPPLIER raised its price, and one whose bill
@@ -639,13 +651,19 @@ def estimate_churn_probability(
     # stable prices during their last contract → less reactive to headline rate changes.
     effective_rate_sensitivity = rate_sensitivity * (1.0 - hedge_fraction * HEDGE_SENSITIVITY_REDUCTION)
 
-    if old_rate_gbp_per_mwh > 0:
-        rate_increase_pct = (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh
+    if reference_rate_gbp_per_mwh is not None and reference_rate_gbp_per_mwh > 0:
+        # Already market-relative: the published default IS the market's level today.
+        own_move_pct = (
+            (new_rate_gbp_per_mwh - reference_rate_gbp_per_mwh) / reference_rate_gbp_per_mwh)
     else:
-        rate_increase_pct = 0.0
-    # The part of this customer's rate change that is THIS SUPPLIER'S doing, and therefore the
-    # part against which a cheaper alternative demonstrably exists.
-    own_move_pct = rate_increase_pct - float(market_move_pct)
+        if old_rate_gbp_per_mwh > 0:
+            rate_increase_pct = (
+                (new_rate_gbp_per_mwh - old_rate_gbp_per_mwh) / old_rate_gbp_per_mwh)
+        else:
+            rate_increase_pct = 0.0
+        # The part of this customer's rate change that is THIS SUPPLIER'S doing, and therefore
+        # the part against which a cheaper alternative demonstrably exists.
+        own_move_pct = rate_increase_pct - float(market_move_pct)
 
     tenure_discount = tenure_discount_per_year * min(tenure_years, MAX_TENURE_DISCOUNT_YEARS)
 
diff --git a/company/crm/enriched_churn_estimate.py b/company/crm/enriched_churn_estimate.py
index 86e8fe4ea..514d08afd 100644
--- a/company/crm/enriched_churn_estimate.py
+++ b/company/crm/enriched_churn_estimate.py
@@ -176,6 +176,7 @@ def enriched_churn_estimate(
     renewal_year: int | None = None,
     payment_method: str | None = None,
     arrears_state: str = ARREARS_STATE_UNKNOWN,
+    published_default_rate_gbp_per_mwh: float | None = None,
 ) -> float:
     """Return enriched churn probability from rate-sensitivity and payment-behaviour signals.
 
@@ -232,6 +233,10 @@ def enriched_churn_estimate(
         # of the published cap. Netted off inside the rate model so its sensitivity applies to
         # what THIS SUPPLIER did. Zero -- no netting -- when the year is unknown.
         market_move_pct=market_rate_move_pct(renewal_year, fuel=fuel),
+        # When the company has read the published default for this fuel and day, the rate term
+        # reads the offer's gap to it and the netting above is not applied. See
+        # `estimate_churn_probability`'s `reference_rate_gbp_per_mwh`.
+        reference_rate_gbp_per_mwh=published_default_rate_gbp_per_mwh,
     )
     payment_est = combined_churn_probability(bill_shock_count, behaviour_score, satisfaction_score)
     result = _apply_market_conditions(max(rate_est, payment_est),
diff --git a/company/pricing/renewal_rate_chain.py b/company/pricing/renewal_rate_chain.py
index e4caa4124..7ef028fec 100644
--- a/company/pricing/renewal_rate_chain.py
+++ b/company/pricing/renewal_rate_chain.py
@@ -459,6 +459,14 @@ def decide_renewal_rate(
         # door and must not gain a policy argument, and a second resolution path is how one run
         # comes to be executing two policies. `None` on every ordinary run.
         flat_level_gbp_per_mwh=active_policy().renewal_margin_flat_level_gbp_per_mwh,
+        # The default tariff a domestic household is actually charged for this fuel on the day
+        # (EPG-net, single-rate, ex-VAT like the offer). The churn belief reads the offer's gap
+        # to it, whether or not this term is held at the cap: the household compares against it
+        # either way.
+        published_default_rate_gbp_per_mwh=(
+            cap_ceiling_ex_vat(
+                commodity, date.fromisoformat(term_start[:10]), multi_register=False)
+            if is_domestic and commodity in ("electricity", "gas") else None),
     )
     # THE DENOMINATOR, WRITTEN AT THE SAME SITE AS THE DECISION. Unconditional and before the two
     # branches below, so a renewal cannot reach the funnel through one path and miss it through
diff --git a/company/pricing/value_based_renewal.py b/company/pricing/value_based_renewal.py
index b94b21841..ffc447b80 100644
--- a/company/pricing/value_based_renewal.py
+++ b/company/pricing/value_based_renewal.py
@@ -747,6 +747,7 @@ def decide_margin(
     book_general_margin_gbp_per_mwh: float | None = None,
     ladder_multiplier: float = 1.0,
     flat_level_gbp_per_mwh: float | None = None,
+    published_default_rate_gbp_per_mwh: float | None = None,
 ) -> MarginDecision:
     """The offered margin for ONE customer, under ONE arm.
 
@@ -820,6 +821,10 @@ def decide_margin(
             # An arrears state that moved with the margin would be this model predicting its own
             # collections -- a second, unsourced elasticity beside the churn model's.
             arrears_state=arrears_state,
+            # THE OFFER AGAINST THE PUBLISHED DEFAULT, not against this account's last price.
+            # Constant across candidates: it is the market's level on the day, read from public
+            # data. `None` (non-domestic, or no reading) keeps the move from the current rate.
+            published_default_rate_gbp_per_mwh=published_default_rate_gbp_per_mwh,
         )
         p_stay = max(0.0, 1.0 - float(p_leave))
         return p_stay, expected_value_gbp(
@@ -1272,6 +1277,7 @@ def renewal_margin_uplift(
     segment: str | None = None,
     ladder_multiplier: float = 1.0,
     flat_level_gbp_per_mwh: float | None = None,
+    published_default_rate_gbp_per_mwh: float | None = None,
 ) -> MarginArmUplift:
     """The £/MWh this renewal moves by, under ONE arm, from the supplier's own settled book.
 
@@ -1388,6 +1394,7 @@ def renewal_margin_uplift(
             # ladder block in `decide_margin`. Default 1.0 leaves every existing caller alone.
             ladder_multiplier=ladder_multiplier,
             flat_level_gbp_per_mwh=flat_level_gbp_per_mwh,
+            published_default_rate_gbp_per_mwh=published_default_rate_gbp_per_mwh,
         )
     except MarginDecisionUnavailable as exc:
         # "NO OFFER" IS AN ANSWER, AND A LIVE PRICING CHAIN MUST BE ABLE TO HEAR IT (2026-08-26).
diff --git a/tests/company/pricing/test_value_arm_in_the_renewal_chain.py b/tests/company/pricing/test_value_arm_in_the_renewal_chain.py
index 8bc84445c..559b5eb4f 100644
--- a/tests/company/pricing/test_value_arm_in_the_renewal_chain.py
+++ b/tests/company/pricing/test_value_arm_in_the_renewal_chain.py
@@ -1018,3 +1018,78 @@ def test_a_fuel_this_supplier_does_not_sell_is_REFUSED_rather_than_priced_as_ele
 
     with pytest.raises(ValueError, match="hydrogen"):
         standing_charge_rate("hydrogen", "resi")
+
+
+def test_the_belief_reads_the_offer_against_the_published_default_and_not_the_last_price(
+        monkeypatch):
+    """The value arm's churn belief reads the offer's gap to the published default tariff.
+
+    The move from the household's own last price ratchets with the arm's own uplifts: a household
+    the arm priced at 1.7x the default last term reads the next rise as small. The world prices
+    the gap to the default. Over 18 rolled value-arm renewals the old input ranked churn at
+    r = -0.12 against the world (2026-10-02 finding, `..._PRICES_THE_MOVE_FROM_ITS_OWN_LAST_PRICE_
+    AND_THE_WORLD_PRICES_THE_GAP_TO_THE_MARKET_...`).
+
+    Both legs of the partition are asserted reachable first: a domestic renewal gets its own
+    fuel's default, and a non-domestic one gets None (no domestic default applies to it).
+    Dropping the argument at the chain, passing one fuel's default to both, or ignoring it inside
+    the churn model each turns this red.
+    """
+    from datetime import date as _date
+
+    from company.crm.churn_model import estimate_churn_probability
+
+    seen: list[dict] = []
+    real = vbr.decide_margin
+
+    def spy(**kwargs):
+        seen.append(kwargs)
+        return real(**kwargs)
+
+    monkeypatch.setattr(vbr, "decide_margin", spy)
+    book = _dual_fuel_book(year=2020)
+    with policy_scope(VALUE_ARM_POLICY):
+        for commodity, rate, domestic in (("gas", 28.0, True), ("electricity", 150.0, True),
+                                          ("electricity", 150.0, False)):
+            _drive(commodity=commodity, is_domestic=domestic, tariff_type="fixed",
+                   term_start="2021-06-01", struck_unit_rate_gbp_per_mwh=rate,
+                   settled_records=book)
+    defaults = [call.get("published_default_rate_gbp_per_mwh") for call in seen]
+    assert len(defaults) == 3, f"the arm did not reach all three decisions: {defaults!r}"
+    on = _date(2021, 6, 1)
+    assert defaults == [
+        pytest.approx(chain.cap_ceiling_ex_vat("gas", on, multi_register=False)),
+        pytest.approx(chain.cap_ceiling_ex_vat("electricity", on, multi_register=False)),
+        None,
+    ], "the chain did not hand each domestic renewal its own fuel's published default"
+
+    # Inside the model: with a reference, only the gap to it moves the rate term, with no market
+    # netting. `no_debt` silences the bill-stress term, which still reads the last price.
+    ref = defaults[1]
+    offer = ref * 1.5
+    with_ref = estimate_churn_probability(ref * 1.4, offer, 3.0, 3_000.0, market_move_pct=0.3,
+                                          reference_rate_gbp_per_mwh=ref, arrears_state="no_debt")
+    gap_as_a_move = estimate_churn_probability(ref, offer, 3.0, 3_000.0, arrears_state="no_debt")
+    without_ref = estimate_churn_probability(ref * 1.4, offer, 3.0, 3_000.0, market_move_pct=0.3,
+                                             arrears_state="no_debt")
+    assert with_ref == pytest.approx(gap_as_a_move)
+    assert without_ref < with_ref, (
+        "a household already priced 1.4x the default reads a 1.5x offer as a small move without "
+        "the reference; if the two agree this control cannot tell the inputs apart")
+
+
+def test_the_published_default_reaches_the_belief_the_decision_scores():
+    """The middle of the chain: `decide_margin` -> `enriched_churn_estimate` -> the churn model.
+
+    The control above reads the adapter's call and the model directly, so a decision that took
+    the argument and never scored with it would pass both. This one reads the decision's own
+    belief. A household already priced 1.4x the default must be believed likelier to leave at
+    the same offer once the decision sees the default.
+    """
+    kwargs = dict(customer_id="C1", arm=vbr.FLAT_RULES, current_rate_gbp_per_mwh=210.0,
+                  base_rate_gbp_per_mwh=200.0, eac_kwh=3_000.0, tenure_years=3.0,
+                  cost_to_serve_gbp_per_year=60.0, renewal_year=2021)
+    without = vbr.decide_margin(**kwargs)
+    with_default = vbr.decide_margin(**kwargs, published_default_rate_gbp_per_mwh=150.0)
+    assert with_default.p_retain < without.p_retain, (
+        "the published default reached `decide_margin` and did not move its belief")
```
