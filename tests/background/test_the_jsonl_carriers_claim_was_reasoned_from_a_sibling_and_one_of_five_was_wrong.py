"""THE TWO GAPS THE CENSUS-LOADER SWEEP CREATED RATHER THAN CLOSED (2026-09-05).

`docs/staging/SEAT_PREREGISTRATION_THE_UNSWEPT_CENSUS_ROWS_LOADER_PARTITION_2026-09-05.md` closed
46 rows and left two things it named instead of fixing. Both are repaired here, and the second one
turned out to be a wrong claim rather than an unexamined one.

**Gap 1 -- `sanity_daemon._maybe_send_daily_digest`.** Its once-per-day stamp was read with a bare
`LAST_DIGEST_DATE_FILE.read_text().strip()` behind an `.exists()` check, unlike its two siblings
`boot_announce.already_announced_this_boot` and `daily_self_note.already_ran_today`, which both
catch `OSError`. Content corruption is harmless here, so this is not the absent-vs-unreadable
conflation the sweep was about -- it is a permissions error, or a directory at that path, raising
into the daemon's cycle. What the sweep did not see is that the OBVIOUS repair makes it worse: the
read and the write are the same failure (the digest sends at the bottom of the function and the
stamp is written after it), so `except OSError: last_sent = None` alone sends the digest, raises on
the write anyway, and repeats BOTH every 30 minutes.

**Gap 2 -- the five JSONL carriers.** All five were dispositioned `benign` with a `loader` field
reading "JSONL, append-only, same as above", where above is `notification_digest._read_queue`,
which "parses PER LINE, discarding only the lines it cannot read". Only that one sibling was
opened. The other four were graded from it. Measured here by opening every reader:

  * `publish_gate_duration.jsonl` -- `suite_duration_watch.read_series` and
    `settlement_ceiling_probe` both catch `JSONDecodeError` per line. Claim HOLDS.
  * `gate_authorizations.jsonl` -- `generate_evidence_data.ledger_by_atom`,
    `discovery_pass_ceiling`, `map_assertion_provenance` all catch per line. Claim HOLDS.
  * `decisions.jsonl` -- `direction.read_decisions` catches per line. Claim HOLDS.
  * `live_decisions_log.jsonl` -- **claim FALSE, in both of its readers.**
    `generate_track_record_scorecard._load_log` appended `json.loads(line)` unguarded, so one bad
    byte took the whole scorecard down; `run_live_decisions.append_decision_log` did the same
    inside the once-per-day idempotence guard.

The two `live_decisions_log.jsonl` readers needed OPPOSITE repairs, which is why grading four
readers from one sibling's behaviour was never going to work. The scorecard is a pure reader and
must drop the line and carry on -- but must PUBLISH the drop, because its `log_entry_count` reaches
the Proof door through `generate_proof_data`, and a quietly shrunken track record is a plausible
number nobody notices, where a traceback is not. The append guard must do the reverse and REFUSE:
skipping an unreadable line there drops that day out of `existing_dates`, and a re-run appends a
SECOND row for the same day -- the exact duplicate its docstring's one-entry-per-day rule exists
to forbid.

Every refusing test here is paired with a control leg proving the accepting branch is still
reachable, per CLAUDE.md: a guard that refuses everything passes every test of a guard.
"""
from __future__ import annotations

import json

import pytest

# ── Gap 1: the sanity daemon's once-per-day stamp ────────────────────────────────────────────

@pytest.fixture()
def daemon(tmp_path, monkeypatch):
    """The daemon with every path it writes redirected into tmp_path, and its NTFY captured.

    The path globals are redirected BEFORE anything runs: this module's failing branches write to
    `LOG_FILE` and page through `_digest`, and a control that damages the live artefact it guards
    is not a control.
    """
    import background.sanity_daemon as sd

    monkeypatch.setattr(sd, "LOG_FILE", tmp_path / "sanity-daemon-log.md")
    monkeypatch.setattr(sd, "LAST_DIGEST_DATE_FILE", tmp_path / ".stamp")
    sent: list[str] = []
    monkeypatch.setattr(sd, "_digest", sent.append)
    # One aged-staging entry so `parts` is non-empty and the digest has something to say; the
    # standing-open-findings half is a different clause and is not the subject here.
    monkeypatch.setattr(
        sd, "_aged_staging_entries",
        lambda *a, **k: [{"filename": "AGED.md", "age_days": 9.0, "summary": "s"}],
    )
    sd._sent_for_test = sent  # type: ignore[attr-defined]
    return sd, sent


def test_a_readable_absent_stamp_still_sends_the_digest(daemon):
    """CONTROL LEG. The refusing tests below are worthless without this one: a
    `_maybe_send_daily_digest` that returned unconditionally would satisfy every one of them."""
    sd, sent = daemon
    assert not sd.LAST_DIGEST_DATE_FILE.exists()

    sd._maybe_send_daily_digest(any_new_this_cycle=True)

    assert len(sent) == 1, "an absent stamp is 'never sent today' and MUST send"
    assert sd.LAST_DIGEST_DATE_FILE.read_text(encoding="utf-8").strip()


def test_an_unreadable_stamp_refuses_the_digest_instead_of_raising_into_the_cycle(daemon):
    """The defect: a bare `read_text()` behind `.exists()`. A directory at that path is the
    cheapest real `OSError` -- `.exists()` says True and `read_text()` raises `IsADirectoryError`,
    which the old code let out into `run_cycle`, where `main`'s blanket handler logged it as
    'Sanity daemon cycle error' every 30 minutes forever.

    It refuses rather than falling back to 'not sent today', because the write below fails for the
    same reason: falling back would page the director every half hour AND still error."""
    sd, sent = daemon
    sd.LAST_DIGEST_DATE_FILE.mkdir()  # a directory where a file is expected

    sd._maybe_send_daily_digest(any_new_this_cycle=True)  # must not raise

    assert sent == [], "an unreadable stamp must not send -- fail closed, not open"
    log_text = sd.LOG_FILE.read_text()
    # NOT `"unreadable" in log_text`. That was the first draft and a mutation restoring the old
    # `except OSError: last_sent = None` SURVIVED it: this test's own name is in `tmp_path`, so the
    # WRITE branch's message -- which quotes the stamp's full path -- contains "unreadable" too,
    # and the assertion passed on the wrong branch. Keyed to a phrase only the READ refusal emits.
    assert "Refusing rather than risking a 30-minute repeat" in log_text, (
        "a refusal that does not name its reason is how the refusal itself never gets corrected"
    )
    assert "could not be written" not in log_text, (
        "the read refusal must be what fired, not the write refusal further down -- both end in "
        "no digest, and only one of them proves the read is guarded"
    )
    assert "IsADirectoryError" in log_text


def test_an_unwritable_stamp_never_sends_rather_than_sending_every_cycle(daemon, monkeypatch):
    """The half the obvious repair misses, and the reason the fix is the ORDER rather than an
    `except`. The read succeeds here (the file is simply absent), so a read-only guard is happy --
    and then the stamp cannot be written. Under the old send-then-stamp order that is 48 pages a
    day, the 2026-07-11 flood reintroduced through the error path, with nothing in this function
    able to suppress it. Stamping first makes the same fault cost one day's summary instead."""
    sd, sent = daemon
    real_write = type(sd.LAST_DIGEST_DATE_FILE).write_text

    def refuse(self, *a, **k):
        if self == sd.LAST_DIGEST_DATE_FILE:
            raise PermissionError(13, "Permission denied")
        return real_write(self, *a, **k)

    monkeypatch.setattr(type(sd.LAST_DIGEST_DATE_FILE), "write_text", refuse)

    for _ in range(4):
        sd._maybe_send_daily_digest(any_new_this_cycle=True)

    assert sent == [], f"four cycles, one unwritable stamp, {len(sent)} pages"
    log_text = sd.LOG_FILE.read_text()
    assert "could not be written" in log_text
    assert "Refusing rather than risking" not in log_text, "the read succeeded here; the WRITE is "\
        "the branch under test, and the two must not be confusable"


def test_the_day_is_stamped_before_the_digest_is_sent_not_after(daemon, monkeypatch):
    """The ordering asserted DIRECTLY, because the two tests above can both be satisfied by a
    function that simply never sends, and because an ordering control has to make the two orders
    give different answers rather than assert the outcome of one of them. The stamp is read from
    inside `_digest`: under send-then-stamp it is absent at that moment, under stamp-then-send it
    already carries today."""
    sd, sent = daemon
    seen: list[str | None] = []

    def capture(msg):
        p = sd.LAST_DIGEST_DATE_FILE
        seen.append(p.read_text(encoding="utf-8").strip() if p.exists() else None)
        sent.append(msg)

    monkeypatch.setattr(sd, "_digest", capture)

    sd._maybe_send_daily_digest(any_new_this_cycle=True)

    assert len(sent) == 1
    assert seen == [sd.datetime.now(sd.timezone.utc).strftime("%Y-%m-%d")], (
        "the digest was sent before the day was stamped -- an unwritable stamp then pages every "
        "cycle and this function cannot stop it"
    )


# ── Gap 2a: the scorecard reader, which must DROP the line and PUBLISH the drop ───────────────

def _decision(day: str) -> dict:
    return {"decision_run_at": f"{day}T00:00:00Z", "hedge_recommendation": "HOLD",
            "renewal_flags": [], "acquisition_prices": {}}


def _write_log(path, lines):
    path.write_text("\n".join(lines) + "\n")


def test_the_scorecard_survives_a_corrupt_line_and_says_how_many_it_dropped(tmp_path):
    """The dispositioned claim, refuted. `json.loads(line)` unguarded raised `JSONDecodeError`
    out of `_load_log`, so ONE bad byte cost the whole scorecard -- not one entry, which is what
    the row said. The non-dict rows are the second half the claim did not cover: they parse
    happily and then `entries.sort(key=lambda e: e.get(...))` raises `AttributeError`."""
    from tools.generate_track_record_scorecard import generate

    log = tmp_path / "log.jsonl"
    _write_log(log, [
        json.dumps(_decision("2026-09-01")),
        "{not json at all",
        json.dumps(_decision("2026-09-02")),
        '"abc"',
        "[1, 2, 3]",
    ])

    result = generate(log_path=str(log), portfolio_path=str(tmp_path / "absent.json"),
                      out_path=str(tmp_path / "out.json"))

    assert result["log_entry_count"] == 2, "the two readable decisions must survive"
    assert result["unreadable_log_lines"] == 3
    assert result["clock_started"] == "2026-09-01"


def test_the_scorecard_publishes_a_zero_drop_count_when_nothing_was_dropped(tmp_path):
    """CONTROL LEG for the field itself. Without it, `unreadable_log_lines` could be hard-wired
    to a non-zero number and the test above would still pass -- and a count that is never zero on
    a clean log is a false alarm on the Proof door rather than a bound on it."""
    from tools.generate_track_record_scorecard import generate

    log = tmp_path / "log.jsonl"
    _write_log(log, [json.dumps(_decision("2026-09-01")), json.dumps(_decision("2026-09-02"))])

    result = generate(log_path=str(log), portfolio_path=str(tmp_path / "absent.json"),
                      out_path=str(tmp_path / "out.json"))

    assert result["unreadable_log_lines"] == 0
    assert result["log_entry_count"] == 2


def test_an_absent_log_is_not_an_unreadable_one(tmp_path):
    """The distinction the whole census sweep was about, asserted at this reader. An absent log
    means the live decisions run has never logged a day, and an empty scorecard is then the truth.
    An `OSError` means we cannot tell, and it is still allowed to raise rather than publish 'no
    track record' as a finding."""
    from tools.generate_track_record_scorecard import _load_log

    entries, unreadable = _load_log(str(tmp_path / "never-written.jsonl"))

    assert entries == [] and unreadable == 0


# ── Gap 2b: the append guard, which must REFUSE rather than duplicate the day ─────────────────

def test_an_unreadable_line_refuses_the_append_rather_than_duplicating_the_day(tmp_path, capsys):
    """The reflex repair -- skip the bad line, carry on -- is WRONG here and would have been what
    'same as above' licensed. If the unreadable line is today's own entry, skipping it drops the
    day out of `existing_dates`, the guard reports 'not logged yet', and the re-run appends a
    second row for the same day. `generate_track_record_scorecard` then grades both."""
    from tools.run_live_decisions import append_decision_log

    log = tmp_path / "live_decisions_log.jsonl"
    # Today's entry, corrupted mid-write -- a truncated append is the realistic way this happens.
    _write_log(log, [json.dumps(_decision("2026-09-01"))[:40]])

    appended = append_decision_log(_decision("2026-09-01"), log_path=str(log))

    assert appended is False
    assert len(log.read_text().splitlines()) == 1, "the day must not be duplicated"
    err = capsys.readouterr().err
    assert "REFUSING" in err and "2026-09-01" in err, (
        "a silent False here is a lost day nobody could attribute -- every production caller "
        "discards the return value"
    )


def test_a_row_without_the_date_field_refuses_too(tmp_path, capsys):
    """`KeyError` and `TypeError`, the two shapes the old bare `json.loads(line)["decision_run_at"]`
    also raised and which a `JSONDecodeError`-only guard would let through into a duplicate."""
    from tools.run_live_decisions import append_decision_log

    log = tmp_path / "live_decisions_log.jsonl"
    _write_log(log, ['{"hedge_recommendation": "HOLD"}'])

    assert append_decision_log(_decision("2026-09-01"), log_path=str(log)) is False
    assert "REFUSING" in capsys.readouterr().err


def test_a_readable_log_still_appends_a_new_day_and_still_refuses_a_repeat(tmp_path):
    """CONTROL LEG over the whole partition, in one assertion set: the guard must ACCEPT a new
    day, REFUSE a repeat of a logged day, and refuse an unreadable one. A guard that only ever
    refused would pass both tests above."""
    from tools.run_live_decisions import append_decision_log

    log = tmp_path / "live_decisions_log.jsonl"
    _write_log(log, [json.dumps(_decision("2026-09-01"))])

    appended_new = append_decision_log(_decision("2026-09-02"), log_path=str(log))
    refused_repeat = append_decision_log(_decision("2026-09-01"), log_path=str(log))

    assert appended_new is True and refused_repeat is False
    assert len(log.read_text().splitlines()) == 2


# ── The four carriers whose claim HELD, asserted so the disposition row is checkable ──────────

@pytest.mark.parametrize("reader_module,reader_name", [
    ("background.suite_duration_watch", "read_series"),
    ("background.direction", "read_decisions"),
])
def test_the_carriers_whose_per_line_claim_holds_really_do_discard_only_the_bad_line(
    tmp_path, reader_module, reader_name,
):
    """`publish_gate_duration.jsonl` and `decisions.jsonl` were graded from a sibling too, and for
    these two the grade was right. Asserted rather than re-reasoned, so the disposition rows stay
    checkable claims: a good line either side of a corrupt one must both come back."""
    import importlib

    mod = importlib.import_module(reader_module)
    read = getattr(mod, reader_name)
    path = tmp_path / "carrier.jsonl"
    _write_log(path, [
        json.dumps({"marker": "first", "ts": 1.0, "atom": "a"}),
        "{truncated",
        json.dumps({"marker": "second", "ts": 2.0, "atom": "a"}),
    ])

    rows = read(path=path)

    assert [r.get("marker") for r in rows] == ["first", "second"] or \
           [r.get("marker") for r in rows] == ["second", "first"], (
        f"{reader_module}.{reader_name} lost more than the corrupt line"
    )
