"""Tests for company/interfaces/bitemporal_event_log.py -- the ordering-
invariant foundation for the reveal-over-time spine (Epoch-2 core, W1/D2,
director-approved 2026-07-10)."""
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog


def _dt(y, m, d, h=12):
    return dt.datetime(y, m, d, h)


class TestRecordAndAsKnownAt:
    def test_returns_none_when_nothing_recorded(self):
        log = BitemporalEventLog()
        assert log.as_known_at(_dt(2020, 6, 1), "elec_spot", "price", dt.date(2020, 6, 1)) is None

    def test_returns_the_recorded_value(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "price", dt.date(2020, 6, 1))
        assert rec.value == 45.0

    def test_none_when_decision_time_before_transaction_time(self):
        """The core point-in-time guarantee: a decision made BEFORE a fact
        was recorded must not see it, even if the fact's valid_time is in
        the past relative to the decision."""
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 5), 45.0)
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "price", dt.date(2020, 6, 1))
        assert rec is None

    def test_restatement_visible_only_after_its_own_transaction_time(self):
        """Real settlement-run restatement: an Initial figure recorded on
        day 2, restated (SF run) on day 40. A decision on day 10 must see
        only the Initial figure; a decision on day 50 must see the SF one."""
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), _dt(2020, 6, 2), 100.0,
                    superseded_by_run="II")
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), _dt(2020, 7, 10), 97.5,
                    superseded_by_run="SF")

        early = log.as_known_at(_dt(2020, 6, 10), "meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        late = log.as_known_at(_dt(2020, 8, 1), "meter_1", "consumption_kwh", dt.date(2020, 6, 1))

        assert early.value == 100.0
        assert late.value == 97.5

    def test_different_entity_id_not_confused(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        log.record("gas_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 20.0)
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "price", dt.date(2020, 6, 1))
        assert rec.value == 45.0

    def test_different_fact_type_not_confused(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), _dt(2020, 6, 2), 100.0)
        log.record("meter_1", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        rec = log.as_known_at(_dt(2020, 6, 3), "meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec.value == 100.0

    def test_no_valid_time_filter_returns_most_recent_across_valid_times(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 2), _dt(2020, 6, 3), 46.0)
        rec = log.as_known_at(_dt(2020, 6, 5), "elec_spot", "price")
        assert rec.value == 46.0

    def test_tie_broken_by_insertion_order(self):
        """Two records with the identical transaction_time -- the later
        INSERTED one wins, a deterministic tiebreak, not undefined behaviour."""
        log = BitemporalEventLog()
        same_tx = _dt(2020, 6, 2)
        log.record("elec_spot", "price", dt.date(2020, 6, 1), same_tx, 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 1), same_tx, 46.0)
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "price", dt.date(2020, 6, 1))
        assert rec.value == 46.0


class TestHistoryAsKnownAt:
    def test_returns_one_record_per_valid_time(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 2), _dt(2020, 6, 3), 46.0)
        history = log.history_as_known_at(_dt(2020, 6, 5), "elec_spot", "price")
        assert [r.valid_time for r in history] == [dt.date(2020, 6, 1), dt.date(2020, 6, 2)]

    def test_excludes_facts_not_yet_knowable(self):
        """The bitemporal generalisation of _price_history_as_of()'s
        bisect-slice fix: a decision at day 5 must not see a fact recorded
        on day 10, even though this function returns the FULL history
        rather than a single value."""
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 10), _dt(2020, 6, 10), 46.0)
        history = log.history_as_known_at(_dt(2020, 6, 5), "elec_spot", "price")
        assert len(history) == 1
        assert history[0].valid_time == dt.date(2020, 6, 1)

    def test_restatement_replaces_earlier_run_in_history(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), _dt(2020, 6, 2), 100.0)
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), _dt(2020, 7, 10), 97.5)
        history = log.history_as_known_at(_dt(2020, 8, 1), "meter_1", "consumption_kwh")
        assert len(history) == 1
        assert history[0].value == 97.5

    def test_empty_when_nothing_recorded(self):
        log = BitemporalEventLog()
        assert log.history_as_known_at(_dt(2020, 6, 5), "elec_spot", "price") == []

    def test_sorted_by_valid_time(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 3), _dt(2020, 6, 4), 47.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 1), _dt(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 2), _dt(2020, 6, 3), 46.0)
        history = log.history_as_known_at(_dt(2020, 6, 10), "elec_spot", "price")
        assert [r.valid_time for r in history] == [
            dt.date(2020, 6, 1), dt.date(2020, 6, 2), dt.date(2020, 6, 3),
        ]


class TestRecordIdAndAllRecords:
    def test_record_ids_increase_monotonically(self):
        log = BitemporalEventLog()
        r1 = log.record("a", "x", dt.date(2020, 1, 1), _dt(2020, 1, 1), 1)
        r2 = log.record("a", "x", dt.date(2020, 1, 2), _dt(2020, 1, 2), 2)
        assert r2.record_id > r1.record_id

    def test_all_records_returns_everything_unfiltered(self):
        log = BitemporalEventLog()
        log.record("a", "x", dt.date(2020, 1, 1), _dt(2020, 1, 1), 1)
        log.record("b", "y", dt.date(2020, 1, 2), _dt(2020, 1, 2), 2)
        assert len(log.all_records()) == 2

    def test_all_records_is_a_copy_not_the_internal_list(self):
        log = BitemporalEventLog()
        log.record("a", "x", dt.date(2020, 1, 1), _dt(2020, 1, 1), 1)
        records = log.all_records()
        records.append("tampered")
        assert len(log.all_records()) == 1

    def test_superseded_by_run_is_informational(self):
        log = BitemporalEventLog()
        rec = log.record("a", "x", dt.date(2020, 1, 1), _dt(2020, 1, 1), 1, superseded_by_run="SF")
        assert rec.superseded_by_run == "SF"


class TestAppendOnlyImmutability:
    """R10 class regression for the Expert-Hour-demonstrated alias holes:
    the log documents itself append-only ('Nothing is ever mutated or
    deleted') but stored/returned payloads were shared by reference, so a
    caller (on write) or a consumer (on read) could silently rewrite a past
    record. Copy-on-write + copy-on-read closes this for every consumer."""

    def test_mutating_caller_dict_after_record_does_not_change_store(self):
        """Payload #1 (write side): a caller that mutates its own dict AFTER
        record() must not rewrite the stored 'immutable' record."""
        log = BitemporalEventLog()
        payload = {"rate": 100}
        log.record("elec_spot", "quote", dt.date(2020, 6, 1), _dt(2020, 6, 2), payload)
        payload["rate"] = 999  # caller mutates its own object after logging
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        assert rec.value == {"rate": 100}

    def test_mutating_as_known_at_return_does_not_corrupt_store(self):
        """Payload #3 (read side): mutating a dict returned by as_known_at()
        must not corrupt the store -- a second read returns the original."""
        log = BitemporalEventLog()
        log.record("elec_spot", "quote", dt.date(2020, 6, 1), _dt(2020, 6, 2), {"rate": 100})
        first = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        first.value["rate"] = 999  # consumer mutates its returned copy
        second = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        assert second.value == {"rate": 100}

    def test_two_reads_do_not_alias_each_other(self):
        """Reads must be decoupled from EACH OTHER too, not just the store."""
        log = BitemporalEventLog()
        log.record("elec_spot", "quote", dt.date(2020, 6, 1), _dt(2020, 6, 2), {"rate": 100})
        a = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        b = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        assert a.value is not b.value
        a.value["rate"] = 999
        assert b.value == {"rate": 100}

    def test_record_return_is_decoupled_from_store(self):
        """record() returns a read, so it must not hand back a live alias
        into the store either."""
        log = BitemporalEventLog()
        returned = log.record("elec_spot", "quote", dt.date(2020, 6, 1), _dt(2020, 6, 2), {"rate": 100})
        returned.value["rate"] = 999  # mutate the returned record's payload
        rec = log.as_known_at(_dt(2020, 6, 3), "elec_spot", "quote", dt.date(2020, 6, 1))
        assert rec.value == {"rate": 100}

    def test_history_as_known_at_returns_decoupled_payloads(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "quote", dt.date(2020, 6, 1), _dt(2020, 6, 2), {"rate": 100})
        hist = log.history_as_known_at(_dt(2020, 6, 3), "elec_spot", "quote")
        hist[0].value["rate"] = 999
        again = log.history_as_known_at(_dt(2020, 6, 3), "elec_spot", "quote")
        assert again[0].value == {"rate": 100}
