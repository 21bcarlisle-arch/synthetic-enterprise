"""R15 proof for background/publish_step_ledger.py.

The finding this closes (`WORKER_FINDING_THE_PUBLISH_PATH_SWALLOWED_199_GENERATOR_CRASHES_2026-08-17`,
BLOCKING, class `controls_that_cannot_fail`) is itself about a control that could not fail, so
every test below is written to the three killer patterns rather than to the happy path:

  TAUTOLOGY   -- the ledger must not derive "fresh" from the same act that publishes it. Proven
                 by `test_a_step_that_raises_is_recorded_as_not_refreshed`: the recorded verdict
                 comes from whether the step's body completed, and the failing case is asserted.
  FAIL-OPEN   -- a missing / empty / malformed ledger must RAISE, never read as clean. Proven by
                 the `TestUnavailableIsNotClean` battery, one test per malformation.
  FAIL-SILENT -- the alert must actually fire on the transition it exists for, and must not fire
                 on an unchanged status. Proven by `TestAlerting` in both directions.

The mutation each control is proven against is stated in its own docstring.
"""
import json

import pytest

from background import publish_step_ledger as psl
from background.publish_step_ledger import LedgerUnavailable, PublishStepLedger


def _ledger(tmp_path, run_stamp="run_b"):
    (tmp_path / "site" / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "observability").mkdir(parents=True, exist_ok=True)
    return PublishStepLedger(run_stamp=run_stamp, project_dir=tmp_path)


class TestRecording:
    def test_a_step_that_completes_is_recorded_as_refreshed(self, tmp_path):
        led = _ledger(tmp_path)
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            pass
        assert led.degraded() is False
        assert led.stale_artefacts() == []
        assert led.steps[0]["last_ok_run_stamp"] == "run_b"

    def test_a_step_that_raises_is_recorded_as_not_refreshed(self, tmp_path):
        """MUTATION: this is the 2026-08-13..17 incident in miniature. The real
        `round(clv_data.get("clv_gbp", 0), 2)` raised TypeError on every publish and the
        bare `except` logged it; the artefact stayed served. Here the same exception must
        produce a DEGRADED ledger that names the frozen file."""
        led = _ledger(tmp_path)
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("type NoneType doesn't define __round__ method")
        assert led.degraded() is True
        assert led.stale_artefacts() == ["site/data/customer_sample.json"]
        assert "__round__" in led.steps[0]["error"]

    def test_the_step_still_swallows_so_later_steps_run(self, tmp_path):
        """The swallow is deliberate (one dead generator must not cost the others their
        publish). If this ever starts propagating, the module has traded one defect for a
        worse one."""
        led = _ledger(tmp_path)
        ran_after = []
        with led.step("A", ["site/data/a.json"]):
            raise RuntimeError("boom")
        with led.step("B", ["site/data/b.json"]):
            ran_after.append(True)
        assert ran_after == [True]
        assert led.stale_artefacts() == ["site/data/a.json"]

    def test_a_failed_step_reports_the_run_it_was_last_real_at(self, tmp_path):
        """"Stale" without "since when" is a mood, not a fact. The previous cycle's ledger
        supplies the last good stamp."""
        first = _ledger(tmp_path, run_stamp="run_a")
        with first.step("Customer sample generation", ["site/data/customer_sample.json"]):
            pass
        first.write()

        second = _ledger(tmp_path, run_stamp="run_b")
        with second.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")
        assert second.steps[0]["last_ok_run_stamp"] == "run_a"
        assert second.steps[0]["refreshed_this_cycle"] is False

    def test_a_step_that_has_never_succeeded_claims_no_stamp(self, tmp_path):
        """MUTATION: returning `self.run_stamp` here would stamp a file nothing wrote with
        the current run -- the frozen-artefact-under-a-present-day-stamp defect exactly."""
        led = _ledger(tmp_path)
        with led.step("Never worked", ["site/data/x.json"]):
            raise RuntimeError("boom")
        assert led.steps[0]["last_ok_run_stamp"] is None


class TestUnavailableIsNotClean:
    """FAIL-OPEN battery. An unavailable check is a FAILED check (R15)."""

    def test_a_missing_ledger_raises(self, tmp_path):
        (tmp_path / "site" / "data").mkdir(parents=True)
        with pytest.raises(LedgerUnavailable):
            psl.read_ledger(tmp_path)
        with pytest.raises(LedgerUnavailable):
            psl.stale_artefacts(tmp_path)

    def test_an_unparseable_ledger_raises(self, tmp_path):
        (tmp_path / "site" / "data").mkdir(parents=True)
        (tmp_path / "site" / "data" / "publish_steps.json").write_text("{not json")
        with pytest.raises(LedgerUnavailable):
            psl.read_ledger(tmp_path)

    def test_a_ledger_without_a_steps_list_raises(self, tmp_path):
        (tmp_path / "site" / "data").mkdir(parents=True)
        (tmp_path / "site" / "data" / "publish_steps.json").write_text('{"degraded": false}')
        with pytest.raises(LedgerUnavailable):
            psl.read_ledger(tmp_path)

    def test_assert_fresh_raises_for_an_unregistered_artefact(self, tmp_path):
        """An artefact no step claims to write is UNMEASURED, and unmeasured must not read
        as fine -- that conflation is the whole finding."""
        led = _ledger(tmp_path)
        with led.step("A", ["site/data/a.json"]):
            pass
        led.write()
        with pytest.raises(LedgerUnavailable):
            psl.assert_fresh("site/data/customer_sample.json", tmp_path)

    def test_assert_fresh_raises_for_an_artefact_whose_step_failed(self, tmp_path):
        led = _ledger(tmp_path)
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")
        led.write()
        with pytest.raises(LedgerUnavailable) as ei:
            psl.assert_fresh("site/data/customer_sample.json", tmp_path)
        assert "NOT refreshed" in str(ei.value)

    def test_assert_fresh_passes_only_on_a_positive_measurement(self, tmp_path):
        led = _ledger(tmp_path)
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            pass
        led.write()
        psl.assert_fresh("site/data/customer_sample.json", tmp_path)


class TestAlerting:
    """FAIL-SILENT battery, both directions (R5: transitions only)."""

    def test_clean_to_degraded_alerts_with_the_diagnostic_payload(self, tmp_path):
        sent = []
        led = _ledger(tmp_path)
        led._state_path().write_text(json.dumps({"degraded": False}))
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("type NoneType doesn't define __round__ method")
        assert led.notify_on_transition(send=sent.append) == "clean->degraded"
        assert len(sent) == 1
        assert "customer_sample.json" in sent[0]
        assert "__round__" in sent[0]

    def test_degraded_to_clean_alerts_once(self, tmp_path):
        sent = []
        led = _ledger(tmp_path)
        led._state_path().write_text(json.dumps({"degraded": True}))
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            pass
        assert led.notify_on_transition(send=sent.append) == "degraded->clean"
        assert len(sent) == 1

    def test_MUTATION_an_INTERRUPTED_cycle_records_nothing_and_re_alarms(self, tmp_path):
        """THE defect, measured rather than imagined. Over the 24h to 2026-08-20 09:20 this
        alarm sent seven PUBLISH RECOVERED messages -- four naming the same run -- against 37
        `degraded->clean` transitions, ZERO `clean->degraded`, and not one "PUBLISH DEGRADED"
        line in any log in the repo. You cannot recover 37 times without degrading.

        The state was written BEFORE the alert. A cycle that computed degraded, wrote the flag
        and then died (159 deadline kills in the same window) latched a degradation nobody was
        told about; the next healthy cycle announced a recovery from it. The recoveries were not
        noisy, they were FALSE.

        Simulated here by the send raising -- any interruption between the decision and the
        delivery has the same shape. What must survive is that the flag is NOT latched, so the
        degradation is found again next cycle: fail toward re-alarming, never toward a phantom
        recovery."""
        led = _ledger(tmp_path)
        led._state_path().write_text(json.dumps({"degraded": False}))
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")

        def dies(_text):
            raise RuntimeError("killed mid-send")

        with pytest.raises(RuntimeError):
            led.notify_on_transition(send=dies)
        assert json.loads(led._state_path().read_text())["degraded"] is False, (
            "the interrupted cycle latched a degradation it never announced -- the next clean "
            "cycle will report a recovery from a fault nobody was told about"
        )

        # Next cycle, still broken: it alarms, because nothing was recorded.
        again = _ledger(tmp_path)
        with again.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")
        sent = []
        assert again.notify_on_transition(send=sent.append) == "clean->degraded"
        assert len(sent) == 1

    def test_an_unchanged_status_never_repeats(self, tmp_path):
        """MUTATION: dropping the `was_degraded == now_degraded` guard would have sent 199
        identical NTFYs over four days, which is how an alert channel becomes noise and
        then becomes ignored -- R5's whole subject."""
        sent = []
        led = _ledger(tmp_path)
        led._state_path().write_text(json.dumps({"degraded": True}))
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")
        assert led.notify_on_transition(send=sent.append) is None
        assert sent == []

    def test_a_lost_state_file_still_alerts_on_a_degraded_cycle(self, tmp_path):
        """MUTATION: defaulting an unknown prior state to DEGRADED would swallow the first
        alert after any state-file loss -- the one cycle it most needs to fire."""
        sent = []
        led = _ledger(tmp_path)
        assert not led._state_path().exists()
        with led.step("Customer sample generation", ["site/data/customer_sample.json"]):
            raise TypeError("boom")
        assert led.notify_on_transition(send=sent.append) == "clean->degraded"
        assert len(sent) == 1

    def test_a_lost_state_file_on_a_clean_cycle_is_not_a_recovery(self, tmp_path):
        sent = []
        led = _ledger(tmp_path)
        with led.step("A", ["site/data/a.json"]):
            pass
        assert led.notify_on_transition(send=sent.append) is None
        assert sent == []


class TestPublishedShape:
    def test_the_written_ledger_names_the_stale_artefacts_at_the_top_level(self, tmp_path):
        """The record has to be readable without walking every step -- a reader who must
        reconstruct the verdict will not."""
        led = _ledger(tmp_path)
        with led.step("A", ["site/data/a.json"]):
            pass
        with led.step("B", ["site/data/b.json"]):
            raise RuntimeError("boom")
        path = led.write()
        data = json.loads(path.read_text())
        assert data["degraded"] is True
        assert data["stale_artefacts"] == ["site/data/b.json"]
        assert data["failing_step_count"] == 1
        assert data["step_count"] == 2
        assert data["run_stamp"] == "run_b"


class TestWiredIntoThePublishPath:
    def test_the_publish_path_actually_uses_the_ledger(self):
        """R11's shape on a mechanism: a ledger nothing calls measures nothing. If the
        conversion in `generate_dashboard_json` is ever reverted to a bare `except
        Exception: log(...)`, this goes red."""
        import inspect

        from background import process_run_complete as prc

        src = inspect.getsource(prc.generate_dashboard_json)
        assert "_ledger = PublishStepLedger(" in src
        assert "_ledger.write()" in src
        assert "_ledger.notify_on_transition()" in src
        for step in ("Customer sample generation", "Customer data generation",
                     "Billing ledger generation", "Invoice data generation",
                     "Portfolio event stream generation"):
            assert '_ledger.step("{}"'.format(step) in src, step

    def test_the_five_evidenced_failures_are_all_covered(self):
        """The finding's evidence table names five steps that actually fired (130/131/32/
        31/31 times). Each must be wrapped, or the class fix does not reach the instances
        that proved the class."""
        import inspect

        from background import process_run_complete as prc

        src = inspect.getsource(prc.generate_dashboard_json)
        for step in ("Customer data generation", "Customer sample generation",
                     "Billing ledger generation", "Invoice data generation"):
            assert '_ledger.step("{}"'.format(step) in src, step
