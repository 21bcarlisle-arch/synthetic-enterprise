"""WHICH publish STEP failed, and WHICH artefact is therefore frozen on the publish path.

THE DEFECT THIS NAMES
---------------------
`WORKER_FINDING_THE_PUBLISH_PATH_SWALLOWED_199_GENERATOR_CRASHES_2026-08-17.md` (BLOCKING,
class `controls_that_cannot_fail`). `process_run_complete.py` wraps each site-data generator
in its own `try / except Exception` and, on failure, calls `log()` and continues:

    try:
        from tools.generate_customer_sample import generate as gen_sample
        gen_sample(json_path)
        log("Generated site/data/customer_sample.json")
    except Exception as exc:
        log("Customer sample generation failed: {}".format(exc))

No alarm, no NTFY, no gate, no non-zero exit -- and, critically, **the artefact the failed
step was supposed to refresh stays on the publish path and keeps being served**. 199 crashes
of one shape ran for just under four days while `poesys.net` served a frozen per-customer
book under a present-day data stamp.

The reason nobody saw it is the R15 killer pattern 3 (FAIL-SILENT) reached through the
SUBJECT rather than through the checker: every control that reads a published artefact was
reading the frozen file and was satisfied by it. `site/customers/test_wall_exhibit.py`'s
vacuity guard was green *because* publishing was broken, and went red the moment the
generator was fixed. A control whose subject is an artefact that stopped being written
passes forever.

WHAT THIS GUARANTEES
--------------------
Every wrapped step records, per publish cycle, whether it actually refreshed its named
artefacts. The record is a PUBLISHED artefact (`site/data/publish_steps.json`), so:

  1. A failed step makes its own staleness VISIBLE rather than merely logged: the artefact
     is named, with the run stamp at which it was LAST successfully refreshed, carried
     forward across cycles. "customer_sample.json is 4 runs old" is a readable statement;
     a line in a 173,000-line log is not.
  2. A control that reads a published artefact can ask whether the publish path is still
     maintaining it, instead of trusting that a parseable file is a current one.
  3. The clean<->degraded TRANSITION notifies exactly once in each direction (R5: state
     transitions only, never a repeated unchanged status), carrying the failing step names
     and their exceptions as the diagnostic payload.

WHY THE STEPS STILL DO NOT RAISE
--------------------------------
Deliberate, and it is not the defect. One dead generator must not cost the other twenty
their publish -- that trade is what the bare `except` was reaching for and it was right. What
it got wrong was making the failure INVISIBLE. So the swallow stays and the silence goes.

FAIL-SILENT IS THE FAILURE MODE HERE (R15), TWICE OVER
------------------------------------------------------
* An UNAVAILABLE ledger is not a clean one. `read_ledger` / `stale_artefacts` RAISE
  `LedgerUnavailable` when the file is missing, unparseable, or shaped wrong -- they never
  return `{}` or `[]`. A reader that cannot find the record has not learned that everything
  published; it has learned nothing, and an unavailable check is a FAILED check.
* The ledger must never itself red the publish path (it is a diagnostic observing a path,
  and a diagnostic that can kill its subject is worse than none) -- but `write()` returning
  without writing would recreate this module's own defect. So a write failure is raised to
  the caller, which logs it, and the ABSENCE of the file is what the reader trips on.

REUSE: background/publish_step_ledger.py
CLASS: CUSTOM
INDEX: searched "publish", "freshness", "staleness", "step", "generator failure".
       `publish_freshness.py` is the closest and is a different subject: it measures whether
       the publish path as a WHOLE reached origin, which stayed green throughout this
       incident precisely because twenty other steps published normally every cycle. A
       whole-pipeline clock cannot see one frozen artefact among many.
       `publish_provenance.py` records whether the newest run was VERIFIED and what the
       visitor is being shown -- it is about the gate's verdict, not about which generators
       ran. `derived_artefact_register.py` checks that a rendered doc matches its renderer
       when re-run NOW, which is a different question again: it would have re-run the
       generator and seen it crash, but nothing on the publish path consults it per step.
"""
from __future__ import annotations

import json
import traceback
from contextlib import contextmanager
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = PROJECT_DIR / "site" / "data" / "publish_steps.json"
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_step_state.json"

#: Bumped when the on-disk shape changes in a way a reader must notice.
SCHEMA = 1


class LedgerUnavailable(RuntimeError):
    """The ledger could not be read.

    Deliberately an exception and not a falsy return: "I cannot find the record of which
    steps published" must never be indistinguishable from "every step published". That
    conflation is the exact shape of the defect this module exists to end.
    """


def _rel(project_dir: Path, path) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(p)


class PublishStepLedger:
    """Records, for one publish cycle, which steps refreshed which artefacts.

    Usage inside `process_run_complete.py`::

        ledger = PublishStepLedger(run_stamp=git_hash, log=log)
        with ledger.step("Customer sample generation", ["site/data/customer_sample.json"]):
            from tools.generate_customer_sample import generate as gen_sample
            gen_sample(json_path)
            log("Generated site/data/customer_sample.json")
        ...
        ledger.write()
        ledger.notify_on_transition()

    The context manager swallows the step's exception exactly as the bare `except` it
    replaces did -- and unlike it, records the failure against the artefacts that did not
    get refreshed.
    """

    def __init__(self, run_stamp: str, *, project_dir: Path | None = None, log=None):
        self.run_stamp = str(run_stamp)
        self.project_dir = Path(project_dir) if project_dir else PROJECT_DIR
        self._log = log
        self.steps: list[dict] = []
        # Carried forward so a step that fails can still say WHEN its artefact was last
        # real. Without this the ledger says "stale" and cannot say "since when", which is
        # the difference between a fact and a mood.
        self._previous = self._read_previous()

    # -- recording ---------------------------------------------------------------

    def _read_previous(self) -> dict:
        try:
            prev = json.loads((self.project_dir / LEDGER_PATH.relative_to(PROJECT_DIR)).read_text())
        except Exception:
            return {}
        return {s.get("name"): s for s in prev.get("steps", []) if isinstance(s, dict)}

    def _last_ok_stamp(self, name: str, ok: bool) -> str | None:
        if ok:
            return self.run_stamp
        prior = self._previous.get(name) or {}
        # A step that has NEVER succeeded within the ledger's memory reports None, not this
        # run's stamp -- claiming the current stamp for an artefact nothing wrote this cycle
        # is precisely the frozen-file-under-a-present-day-stamp defect.
        return prior.get("last_ok_run_stamp")

    def record(self, name: str, artefacts, ok: bool, error: str | None = None) -> dict:
        paths = [_rel(self.project_dir, a) for a in (artefacts or ())]
        row = {
            "name": name,
            "artefacts": paths,
            "ok": bool(ok),
            "refreshed_this_cycle": bool(ok),
            "error": error,
            "last_ok_run_stamp": self._last_ok_stamp(name, ok),
        }
        self.steps.append(row)
        return row

    @contextmanager
    def step(self, name: str, artefacts=()):
        try:
            yield
        except Exception as exc:  # noqa: BLE001 -- see WHY THE STEPS STILL DO NOT RAISE
            detail = "{}: {}".format(type(exc).__name__, exc)
            self.record(name, artefacts, ok=False, error=detail)
            if self._log:
                self._log("{} failed: {}".format(name, exc))
                self._log(
                    "{} left {} STALE on the publish path (last refreshed at run {}) -- "
                    "recorded in site/data/publish_steps.json".format(
                        name,
                        ", ".join(_rel(self.project_dir, a) for a in artefacts) or "no named artefact",
                        self._last_ok_stamp(name, False) or "never (within ledger memory)",
                    )
                )
            if self._log is None:
                traceback.print_exc()
        else:
            self.record(name, artefacts, ok=True)

    # -- verdict -----------------------------------------------------------------

    def failing_steps(self) -> list[dict]:
        return [s for s in self.steps if not s["ok"]]

    def stale_artefacts(self) -> list[str]:
        out: list[str] = []
        for s in self.failing_steps():
            out.extend(s["artefacts"])
        return sorted(set(out))

    def degraded(self) -> bool:
        return bool(self.failing_steps())

    def payload(self) -> dict:
        return {
            "schema": SCHEMA,
            "run_stamp": self.run_stamp,
            "degraded": self.degraded(),
            "step_count": len(self.steps),
            "failing_step_count": len(self.failing_steps()),
            "stale_artefacts": self.stale_artefacts(),
            "steps": self.steps,
        }

    def write(self, path: Path | None = None) -> Path:
        target = Path(path) if path else (self.project_dir / "site" / "data" / "publish_steps.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.payload(), indent=2) + "\n")
        return target

    # -- alerting (R5: transitions only) -----------------------------------------

    def _state_path(self) -> Path:
        return self.project_dir / "docs" / "observability" / ".publish_step_state.json"

    def notify_on_transition(self, *, send=None) -> str | None:
        """NTFY once on clean->degraded and once on degraded->clean. Returns the
        transition name, or None when the state is unchanged (R5: never repeat an
        unchanged status)."""
        now_degraded = self.degraded()
        state_path = self._state_path()
        try:
            was_degraded = bool(json.loads(state_path.read_text()).get("degraded"))
            known = True
        except Exception:
            was_degraded, known = False, False

        # THE STATE IS RECORDED ONLY ONCE THE ALERT HAS GONE OUT. It used to be written
        # here, BEFORE the decision below, and that is a correctness bug rather than a
        # style point.
        #
        # MEASURED over the 24h to 2026-08-20 09:20, from the outbound ntfy mirror: SEVEN
        # "PUBLISH RECOVERED" messages, four of them naming the same run (810561e4f) --
        # and 37 `degraded->clean` transitions in the sim-runner log against **zero**
        # `clean->degraded`, and zero "PUBLISH DEGRADED" lines in any log in the repo. You
        # cannot recover thirty-seven times without degrading. Every one of those recoveries
        # announced the end of a degradation that was never announced and left no trace.
        #
        # The mechanism: a cycle that computed `degraded=True` wrote it here and then died
        # (159 deadline kills in the same window) before reaching the send or the log. The
        # flag latched, and the next healthy cycle read it and announced a recovery from a
        # fault the director had never been told about. Writing after the send means an
        # interrupted cycle records nothing, and the degradation is re-detected next time --
        # failing toward RE-ALARMING rather than toward a phantom recovery.
        def _commit_state():
            guard_live_ledger_write(
                state_path, writer="publish_step_ledger._commit_state")
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(json.dumps({
                "degraded": now_degraded,
                "run_stamp": self.run_stamp,
                "failing_steps": [s["name"] for s in self.failing_steps()],
            }, indent=2) + "\n")

        # An unknown prior state is treated as CLEAN, so the first degraded cycle after the
        # state file is lost still alerts. The opposite default would swallow exactly the
        # alert this module exists to raise.
        if known and was_degraded == now_degraded:
            _commit_state()          # no alert to lose; recording it cannot strand anything
            return None
        if not known and not now_degraded:
            _commit_state()
            return None

        if send is None:
            # Through the ONE contract, not around it. This module called send_ntfy directly,
            # so it never saw transition-only, auto-keying or escalation -- which is why the
            # repetition fix of 2026-08-20 could not touch it, and why it stayed the loudest
            # thing on the channel after that fix landed.
            from background.notify import notify as _notify

            def send(text):
                return _notify(text, kind="real_alarm",
                               transition_key="publish_step_ledger",
                               state="degraded" if now_degraded else "clean")

        if now_degraded:
            lines = [
                "PUBLISH DEGRADED — {} of {} step(s) failed; their artefacts are FROZEN on the "
                "publish path and are still being served.".format(
                    len(self.failing_steps()), len(self.steps)),
            ]
            for s in self.failing_steps():
                lines.append("· {} → {} (last real at run {}) — {}".format(
                    s["name"],
                    ", ".join(s["artefacts"]) or "no named artefact",
                    s["last_ok_run_stamp"] or "never",
                    s["error"]))
            lines.append("Detail: site/data/publish_steps.json @ run {}".format(self.run_stamp))
            send("\n".join(lines))
            _commit_state()
            return "clean->degraded"

        send("PUBLISH RECOVERED — all {} publish steps refreshed their artefacts at run {}.".format(
            len(self.steps), self.run_stamp))
        _commit_state()
        return "degraded->clean"


# -- readers, for controls ---------------------------------------------------------


def read_ledger(project_dir: Path | None = None) -> dict:
    """Return the published ledger, or RAISE. Never returns a clean-looking default."""
    root = Path(project_dir) if project_dir else PROJECT_DIR
    path = root / "site" / "data" / "publish_steps.json"
    try:
        raw = path.read_text()
    except OSError as exc:
        raise LedgerUnavailable(
            "no publish-step ledger at {} -- the publish path's own record of which "
            "generators ran is absent, so nothing here can be called fresh".format(path)
        ) from exc
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise LedgerUnavailable("publish-step ledger at {} is not JSON".format(path)) from exc
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list):
        raise LedgerUnavailable("publish-step ledger at {} has no `steps` list".format(path))
    return data


def stale_artefacts(project_dir: Path | None = None) -> list[str]:
    """Artefacts a failed step left un-refreshed on the publish path. Raises if unknown."""
    data = read_ledger(project_dir)
    out: list[str] = []
    for s in data["steps"]:
        if isinstance(s, dict) and not s.get("ok"):
            out.extend(s.get("artefacts") or [])
    return sorted(set(out))


def assert_fresh(artefact: str, project_dir: Path | None = None) -> None:
    """Raise unless the publish path refreshed `artefact` in its most recent cycle.

    The hook a control uses so its subject cannot silently become a file nothing writes.
    An artefact the ledger has never heard of raises too: an unregistered artefact is an
    unmeasured one, and this module's whole point is that unmeasured reads as fine.
    """
    data = read_ledger(project_dir)
    want = str(artefact)
    for s in data["steps"]:
        if not isinstance(s, dict):
            continue
        if want in (s.get("artefacts") or []):
            if s.get("ok"):
                return
            raise LedgerUnavailable(
                "{} was NOT refreshed by run {} -- step {!r} failed ({}); last real at run {}".format(
                    want, data.get("run_stamp"), s.get("name"), s.get("error"),
                    s.get("last_ok_run_stamp") or "never"))
    raise LedgerUnavailable(
        "{} is not a registered publish-step artefact -- no step claims to write it, so "
        "nothing measures whether it is still being written".format(want))
