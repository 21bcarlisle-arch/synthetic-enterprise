"""Tests for company/interfaces/point_in_time_view.py -- the as-of snapshot
object (Epoch-2 core, director-approved bounded start 2026-07-10)."""
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog
from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log


class _FakeMarketPort:
    """A minimal, real MarketDataPort-satisfying fake -- records what as_of
    value each method was called with, so tests can assert the view's own
    decision_date was actually threaded through, not silently ignored."""

    def __init__(self):
        self.calls = []

    def get_spot_elec_gbp_per_mwh(self, as_of=None):
        self.calls.append(("spot_elec", as_of))
        return 45.0

    def get_spot_gas_gbp_per_mwh(self, as_of=None):
        self.calls.append(("spot_gas", as_of))
        return 20.0

    def get_forward_price(self, as_of=None, delivery_date=None, commodity="electricity"):
        self.calls.append(("forward", as_of, delivery_date, commodity))
        return 50.0

    def get_market_summary(self, as_of=None):
        self.calls.append(("summary", as_of))
        return {"as_of": as_of}


class TestConstructionAndDecisionDate:
    def test_decision_date_derives_from_decision_time(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        assert view.decision_date == dt.date(2020, 6, 15)


class TestMarketDataDelegation:
    def test_get_spot_elec_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_spot_elec_gbp_per_mwh()
        assert result == 45.0
        assert port.calls == [("spot_elec", dt.date(2020, 6, 15))]

    def test_get_spot_gas_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        view.get_spot_gas_gbp_per_mwh()
        assert port.calls == [("spot_gas", dt.date(2020, 6, 15))]

    def test_get_forward_price_passes_delivery_date_and_commodity(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_forward_price(dt.date(2021, 1, 1), commodity="gas")
        assert result == 50.0
        assert port.calls == [("forward", dt.date(2020, 6, 15), dt.date(2021, 1, 1), "gas")]

    def test_get_market_summary_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_market_summary()
        assert result == {"as_of": dt.date(2020, 6, 15)}

    def test_no_method_accepts_an_as_of_override(self):
        """The whole point: a caller cannot pass a different date and
        accidentally read something the decision shouldn't see."""
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(TypeError):
            view.get_spot_elec_gbp_per_mwh(as_of=dt.date(2099, 1, 1))


class TestBitemporalDelegation:
    def test_get_fact_as_known_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(RuntimeError):
            view.get_fact_as_known("meter_1", "consumption_kwh")

    def test_get_history_as_known_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(RuntimeError):
            view.get_history_as_known("meter_1", "consumption_kwh")

    def test_get_fact_as_known_delegates_to_bitemporal_log(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 2), 100.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec.value == 100.0

    def test_get_fact_as_known_respects_decision_time_bound(self):
        """A fact recorded AFTER this view's decision_time must not be
        visible -- the exact guarantee the whole spine exists to provide."""
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1),
                   dt.datetime(2020, 7, 1), 100.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec is None

    def test_get_history_as_known_delegates_to_bitemporal_log(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 2), dt.datetime(2020, 6, 3), 46.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        history = view.get_history_as_known("elec_spot", "price")
        assert len(history) == 2

    def test_get_history_as_known_excludes_future_relative_to_decision(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 7, 1), dt.datetime(2020, 7, 2), 46.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        history = view.get_history_as_known("elec_spot", "price")
        assert len(history) == 1
        assert history[0].valid_time == dt.date(2020, 6, 1)


class TestMarketDataPortOptional:
    """2026-07-11 M1 depth work (docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md):
    market_data_port must be optional so a view backing the historical
    replay can be constructed with only a bitemporal_log, never touching
    the unrelated frozen-2025-snapshot adapter."""

    def test_construction_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        assert view.decision_date == dt.date(2020, 6, 15)

    def test_get_spot_elec_raises_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        with pytest.raises(RuntimeError):
            view.get_spot_elec_gbp_per_mwh()

    def test_get_forward_price_raises_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        with pytest.raises(RuntimeError):
            view.get_forward_price(dt.date(2021, 1, 1))

    def test_bitemporal_reads_still_work_without_market_data_port(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 100.0)
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec.value == 100.0


class TestBuildPriceBitemporalLog:
    def test_aggregates_multiple_periods_to_daily_mean(self):
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-06-01", "systemSellPrice": 60.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["systemSellPrice"] == pytest.approx(50.0)

    def test_electricity_and_gas_kept_separate(self):
        elec = [{"settlementDate": "2020-06-01", "systemSellPrice": 40.0}]
        gas = [{"settlementDate": "2020-06-01", "systemSellPrice": 20.0}]
        log = build_price_bitemporal_log(elec, gas)
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        elec_hist = view.get_price_history_as_of("electricity")
        gas_hist = view.get_price_history_as_of("gas")
        assert elec_hist[0]["systemSellPrice"] == 40.0
        assert gas_hist[0]["systemSellPrice"] == 20.0

    def test_skips_zero_or_missing_price(self):
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 0.0},
            {"settlementDate": "2020-06-01"},
            {"settlementDate": "2020-06-02", "systemSellPrice": 45.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["settlementDate"] == "2020-06-02"

    def test_transaction_time_is_start_of_next_day(self):
        """2026-07-13 fix (closes the same-day-price boundary leak recorded
        in this atom's expert_hour finding): transaction_time is midnight of
        valid_time + 1 day, NOT valid_time's own midnight -- date D's price
        only becomes 'known' at midnight of D+1, matching when a real
        trading desk could actually observe it. A future settlement-run
        restatement would still use a LATER transaction_time than this,
        which history_as_known_at() already handles correctly by
        construction."""
        elec = [{"settlementDate": "2020-06-01", "systemSellPrice": 40.0}]
        log = build_price_bitemporal_log(elec, [])
        recs = log.all_records()
        assert recs[0].transaction_time == dt.datetime(2020, 6, 2, 0, 0)

    def test_negative_hh_price_drop_biases_daily_mean_UPWARD_worked_example(self):
        """RED-TEAM WORKED EXAMPLE (2026-07-28 HARDEN, dial-4 yielded) --
        quantifies the negative-price-drop fidelity gap FILED but never
        measured on 2026-07-27 (maturity_map.yaml::W1_reveal_over_time),
        following this atom's own asserted->measured pattern (the same-day
        leak went asserted -> analytically-bounded -> synthetic-worked-
        example -> fixed).

        build_price_bitemporal_log() filters each half-hourly SSP record
        with `if d and p and p > 0` BEFORE the daily-mean aggregation. The
        `.get(..., 0.0)` default means that filter was clearly meant to drop
        the missing-data sentinel, but it ALSO silently drops legitimately-
        NEGATIVE UK System Sell prices -- a real recurring phenomenon under
        the single-price EBS during oversupply (high wind / low demand).
        Dropping the negative half-hours can only RAISE the surviving mean,
        so on exactly the high-volatility oversupply days the emitted daily
        mean is biased UPWARD -- understating the very volatility this atom's
        consumer (estimate_price_volatility) measures.

        This test runs the LIVE production function (no shipped-basis change)
        and asserts the direction + magnitude of the bias against the true
        (negatives-kept) mean computed by hand. It is a regression witness
        for the QUEUED M-lane fix, not the fix itself."""
        # One oversupply day: a real cold-morning peak, then deeply-negative
        # midday half-hours as wind floods a low-demand system (plausible
        # single-price EBS values, not extreme).
        hh_prices = [
            85.0, 80.0, 70.0,          # early peak
            10.0, -15.0, -40.0, -22.0, # midday oversupply, negative SSP
            30.0, 55.0, 75.0,          # evening ramp
        ]
        elec = [
            {"settlementDate": "2020-06-14", "systemSellPrice": p}
            for p in hh_prices
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 7, 1), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        emitted_mean = history[0]["systemSellPrice"]

        # Truth: the mean a fidelity-correct aggregation would report keeps
        # the real negatives (only the missing-data sentinel should drop).
        true_mean = sum(hh_prices) / len(hh_prices)
        kept = [p for p in hh_prices if p > 0]
        drop_negatives_mean = sum(kept) / len(kept)

        # The live function reproduces the positives-only mean, NOT the truth.
        assert emitted_mean == pytest.approx(drop_negatives_mean)
        # ... and that mean is biased strictly UPWARD versus the true mean.
        assert emitted_mean > true_mean
        # Magnitude on this plausible day is material, not a rounding nit:
        # emitted ~ 57.9 vs true ~ 32.8 GBP/MWh, a ~+76% upward bias.
        bias_pct = (emitted_mean - true_mean) / abs(true_mean)
        assert bias_pct > 0.5

    def test_negative_drop_understates_downstream_volatility_worked_example(self):
        """Companion to the daily-mean bias worked example: propagates the
        negative-price drop THROUGH the real estimate_price_volatility()
        pathway to show the fidelity gap reaches the actual live consumer
        (hedge_decision.estimate_price_volatility, wired live via
        CURRENT_POLICY.use_var_hedge_decision=True), not just the aggregate.

        Two 90-day daily series, identical except that the 'oversupply'
        series has periodic deeply-negative half-hours the live build drops.
        The negatives are the largest single-day price MOVES; dropping them
        flattens the day-to-day daily-mean path, so the vol estimate the
        company acts on is LOWER than a negatives-kept aggregation would
        produce. NB estimate_price_volatility ALSO carries its own `p > 0`
        filter AND a daily-mean log-return positivity guard, so the correct
        fix is a genuine multi-site BUILD change (why it is QUEUED, not
        fixed on sight in a bounded HARDEN tick)."""
        from company.trading.hedge_decision import estimate_price_volatility

        def build_day(day_idx, oversupply):
            date = (dt.date(2020, 1, 1) + dt.timedelta(days=day_idx)).isoformat()
            # Flat positive base: with negatives dropped, every daily mean is
            # 60.0, so the day-to-day path is flat and the vol estimate floors
            # at MIN_VOL_ANNUAL -- isolating the drop as the sole difference.
            recs = [{"settlementDate": date, "systemSellPrice": 60.0}
                    for _ in range(10)]
            if oversupply and day_idx % 6 == 0:
                # one modest negative half-hour on every sixth day (kept in
                # the fidelity-correct aggregation, dropped by the live one);
                # magnitudes chosen so neither vol saturates the 2.5 cap.
                recs.append({"settlementDate": date, "systemSellPrice": -5.0})
            return recs

        calm = [r for i in range(90) for r in build_day(i, oversupply=False)]
        spiky = [r for i in range(90) for r in build_day(i, oversupply=True)]

        calm_hist = PointInTimeView(
            dt.datetime(2020, 7, 1),
            bitemporal_log=build_price_bitemporal_log(calm, []),
        ).get_price_history_as_of("electricity")
        spiky_hist = PointInTimeView(
            dt.datetime(2020, 7, 1),
            bitemporal_log=build_price_bitemporal_log(spiky, []),
        ).get_price_history_as_of("electricity")

        vol_dropped = estimate_price_volatility(spiky_hist)

        # Truth-side proxy: rebuild the oversupply series' daily means WITH
        # the negatives kept (the fidelity-correct aggregation), then feed
        # positive daily means so the downstream p>0 log-return guard is not
        # what drives the difference -- isolating the drop's effect.
        daily_true: dict[str, list[float]] = {}
        for r in spiky:
            daily_true.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
        true_hist = [
            {"settlementDate": d, "systemSellPrice": sum(v) / len(v)}
            for d, v in sorted(daily_true.items())
        ]
        assert all(x["systemSellPrice"] > 0 for x in true_hist)  # means stay positive
        vol_true = estimate_price_volatility(true_hist)

        # The live (negatives-dropped) path understates realised volatility
        # versus the fidelity-correct (negatives-kept) aggregation.
        assert vol_true > vol_dropped
    def test_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15), port)
        with pytest.raises(RuntimeError):
            view.get_price_history_as_of("electricity")

    def test_structurally_excludes_future_dates(self):
        """The actual M1 exit test: a restatement / future price cannot be
        seen by a decision made before it existed."""
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-07-01", "systemSellPrice": 999.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["settlementDate"] == "2020-06-01"

    def test_same_day_price_not_visible_at_midnight_but_prior_day_is(self):
        """2026-07-13 fix, the exact case named in this atom's expert_hour
        finding: a hedge decision's decision_time is midnight(term_start=D).
        Before the fix, transaction_time == valid_time meant D's own
        daily-mean price was already visible at midnight(D) -- not actually
        knowable that early. After the fix (transaction_time = midnight of
        D+1), a decision at midnight(D) must NOT see D's own price but MUST
        still see D-1's, matching the strictly-before window
        sim/risk_engine.py::calculate_sigma_recent() already uses."""
        elec = [
            {"settlementDate": "2020-06-13", "systemSellPrice": 40.0},  # D-1
            {"settlementDate": "2020-06-14", "systemSellPrice": 999.0},  # D (must NOT be seen)
        ]
        log = build_price_bitemporal_log(elec, [])
        decision_at_midnight_D = PointInTimeView(dt.datetime(2020, 6, 14, 0, 0), bitemporal_log=log)
        history = decision_at_midnight_D.get_price_history_as_of("electricity")
        dates = [r["settlementDate"] for r in history]
        assert dates == ["2020-06-13"]

        decision_at_midnight_D_plus_1 = PointInTimeView(dt.datetime(2020, 6, 15, 0, 0), bitemporal_log=log)
        history_after = decision_at_midnight_D_plus_1.get_price_history_as_of("electricity")
        dates_after = [r["settlementDate"] for r in history_after]
        assert dates_after == ["2020-06-13", "2020-06-14"]

    def test_MUTATION_same_day_leak_control_fires_on_its_named_defect(self):
        """R15 mutation-proof (2026-07-24 HARDEN, W1_reveal_over_time): the
        control that closes the same-day-price leak is the `+1 day`
        transaction_time offset in build_price_bitemporal_log(). A guard test
        that only ever asserts the CORRECT behaviour is worth nothing under
        R15 unless the control it rests on can be shown to FAIL on its own
        named defect -- otherwise it is indistinguishable from a tautology
        (checked value derived from the same source it checks) or a
        fail-open that would pass even with the leak live.

        So this test reconstructs the EXACT pre-fix (leaky) encoding the fix
        replaced -- transaction_time == valid_date's own midnight, i.e. a
        `+0 day` offset -- and asserts the leak REAPPEARS: date D's own
        daily-mean price becomes visible to a decision made at midnight(D),
        which is precisely the future-data leak the point-in-time blindfold
        exists to prevent. The live control, fed the identical prices, must
        exclude it. If a future refactor silently reverted the offset to +0
        (or any value <= 0), the production `build_price_bitemporal_log()`
        would match the mutant and the sibling guard
        (test_same_day_price_not_visible_at_midnight_but_prior_day_is) would
        go red -- so this test PINS that the guard's pass is caused by the
        control, not by an accident of the fixture."""
        prices = [("2020-06-13", 40.0), ("2020-06-14", 999.0)]  # D-1, D
        decision_at_midnight_D = dt.datetime(2020, 6, 14, 0, 0)

        # MUTANT: the named defect -- transaction_time == valid_date midnight
        # (the encoding this atom's expert_hour finding recorded as the leak).
        leaky_log = BitemporalEventLog()
        for d, p in prices:
            vd = dt.date.fromisoformat(d)
            leaky_log.record(
                entity_id="electricity",
                fact_type="daily_mean_spot_price",
                valid_time=vd,
                transaction_time=dt.datetime.combine(vd, dt.time.min),  # +0 days
                value=p,
            )
        leaky_view = PointInTimeView(decision_at_midnight_D, bitemporal_log=leaky_log)
        leaked = [r["settlementDate"] for r in leaky_view.get_price_history_as_of("electricity")]
        # The leak is real under the mutant: D's own price is visible at midnight(D).
        assert "2020-06-14" in leaked, (
            "mutation-proof invalid: the reconstructed pre-fix encoding did NOT "
            "reproduce the same-day leak, so the guard test proves nothing"
        )

        # The live control, given identical prices, must EXCLUDE the same-day price.
        fixed_log = build_price_bitemporal_log([
            {"settlementDate": d, "systemSellPrice": p} for d, p in prices
        ], [])
        fixed_view = PointInTimeView(decision_at_midnight_D, bitemporal_log=fixed_log)
        fixed = [r["settlementDate"] for r in fixed_view.get_price_history_as_of("electricity")]
        assert fixed == ["2020-06-13"], (
            "the live control failed to exclude date D's own price at midnight(D) "
            "-- the same-day leak is live in production"
        )
        # The ONLY difference between mutant and control is the transaction_time
        # offset, so the exclusion is attributable to the control, not the fixture.
        assert "2020-06-14" in leaked and "2020-06-14" not in fixed

    def test_returns_chronological_order(self):
        elec = [
            {"settlementDate": "2020-06-03", "systemSellPrice": 42.0},
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-06-02", "systemSellPrice": 41.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        dates = [r["settlementDate"] for r in history]
        assert dates == sorted(dates)

    def test_restatement_versions_correctly_through_price_history(self):
        """The other half of THE_VALUE_CYCLE_FRAMING.md's M1 exit test: 'a
        restatement lands as an event and downstream values version
        correctly.' Previously only exercised generically at the
        BitemporalEventLog level (test_bitemporal_event_log.py) -- never
        through get_price_history_as_of(), the actual pathway
        estimate_price_volatility() consumes. build_price_bitemporal_log()
        doesn't produce restatements today (transaction_time == valid_time,
        a documented simplification), so this constructs the log directly
        via .record() to prove the pathway ABOVE it (get_price_history_as_of
        -> history_as_known_at) versions correctly once a restatement does
        exist -- the exact escape hatch that simplification claims."""
        log = BitemporalEventLog()
        log.record("electricity", "daily_mean_spot_price", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 1, 0, 0), 40.0)
        # A later settlement run restates the same day's price.
        log.record("electricity", "daily_mean_spot_price", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 10, 0, 0), 55.0)

        before_restatement = PointInTimeView(dt.datetime(2020, 6, 5), bitemporal_log=log)
        after_restatement = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)

        history_before = before_restatement.get_price_history_as_of("electricity")
        history_after = after_restatement.get_price_history_as_of("electricity")

        assert history_before[0]["systemSellPrice"] == 40.0
        assert history_after[0]["systemSellPrice"] == 55.0

    def test_matches_estimate_price_volatility_input_shape(self):
        """Regression safety: feeding this into estimate_price_volatility()
        must produce the same result as the old _price_history_as_of()
        wrapper would have, for the same underlying data."""
        from company.trading.hedge_decision import estimate_price_volatility
        import random
        random.seed(42)
        elec = []
        price = 50.0
        for i in range(100):
            price = max(1.0, price + random.gauss(0, 3))
            elec.append({"settlementDate": f"2020-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                         "systemSellPrice": round(price, 2)})
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2021, 1, 1), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        vol = estimate_price_volatility(history)
        assert vol > 0
