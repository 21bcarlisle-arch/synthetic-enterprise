"""Tests for background/naive_organ.py — the deliberately-amnesiac question/
falsify organ (THE_NAIVE_ORGAN.md + the 2026-07-13 DIRECTOR AMENDMENT).

An injectable invoke_fn is used throughout so no real `claude -p` process is
spawned in CI (slow, non-deterministic, costs real tokens) — mirrors
test_director_twin.py. The amnesia is proven at the PROCESS level (empty cwd,
tools off, payload closed over four explicit args), not by prose.
"""
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from background import naive_organ as organ


CANARY = "NAIVE_ORGAN_CANARY_7Q3"

# The frozen weekend fixture (design §4.1) — the real observable surfaces AS THEY
# READ during the 2026-07-11 incidents, reconstructed from git history.
WEEKEND_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "naive_organ" / "weekend_20260711"


def _load_weekend_fixture() -> dict:
    """Build the organ's observable-state dict from the FROZEN FILES on disk
    (not an inline literal) — the same dict shape `load_state()` assembles at
    runtime, so the replay exercises the real detectors against the real weekend
    state. gitlog subjects are split hash-off exactly as `load_state` does."""
    d = WEEKEND_FIXTURE
    atoms = yaml.safe_load((d / "maturity_map.yaml").read_text())
    runhist = json.loads((d / "run_history.json").read_text())
    idle = json.loads((d / "idle_counter.json").read_text())
    gitlog_subjects = [ln.split(" ", 1)[1]
                       for ln in (d / "gitlog.txt").read_text().splitlines() if " " in ln]
    return {
        "atoms": atoms,
        "runhist": runhist,
        "insights": {},
        "agent_status": {},
        "claims_text": (d / "claims.txt").read_text(),
        "gitlog_subjects": gitlog_subjects,
        "idle_count": idle.get("count", 0),
    }


# ── PA-2: empty-cwd / no-bypass assertion (structural, survives refactors) ──
def test_pa2_default_invoke_runs_in_empty_cwd_with_tools_off(monkeypatch):
    captured = {}

    class _Res:
        stdout = "a naive question?"

    def _fake_run(argv, cwd, capture_output, text, timeout):
        captured["argv"] = argv
        captured["cwd"] = cwd
        return _Res()

    monkeypatch.setattr(subprocess, "run", _fake_run)
    organ._default_invoke("prompt")

    argv = captured["argv"]
    assert "--tools=" in argv, "every tool must be disabled at the CLI level"
    assert "--dangerously-skip-permissions" not in argv, "must be default-deny"
    assert "--model" in argv and organ.ORGAN_MODEL in argv, "Opus-tier, non-negotiable"

    from pathlib import Path
    cwd = Path(captured["cwd"])
    assert organ.PROJECT_DIR not in cwd.parents and cwd != organ.PROJECT_DIR, (
        "scratch cwd must be OUTSIDE the repo — no docs/staging to act on"
    )


# ── PA-3: payload closure — build_prompt is a pure fn of its four args ──
def test_pa3_build_prompt_is_closed_over_its_four_args():
    prompt = organ.build_prompt("GOAL_X", "EVIDENCE_Y", "CLAIM_Z", "RUBRIC_W")
    assert "GOAL_X" in prompt and "EVIDENCE_Y" in prompt
    assert "CLAIM_Z" in prompt and "RUBRIC_W" in prompt
    # nothing sourced from disk leaked in
    assert CANARY not in prompt
    assert "simplifications" not in prompt
    # pure: identical args -> identical output, no hidden disk read
    assert organ.build_prompt("GOAL_X", "EVIDENCE_Y", "CLAIM_Z", "RUBRIC_W") == prompt


def test_pa3_goal_is_a_literal_constant_not_read_from_claude_md():
    # the GOAL is a fixed source constant; the amnesia depends on it never
    # being read from CLAUDE.md
    assert "maximise" in organ.GOAL_CONST
    assert isinstance(organ.GOAL_CONST, str)


# ── PA-1: canary — the map's PROSE rationales never reach the payload ──
def test_pa1_map_simplifications_prose_never_leaks_into_the_payload(tmp_path):
    """The organ receives ONLY the detector-chosen evidence (ids + levels), never
    the map's `simplifications` prose. A canary planted in a simplifications
    field must never appear in the prompt the process is handed."""
    prompts = []

    def _spy_invoke(prompt):
        prompts.append(prompt)
        return "naive question?"

    state = {
        "atoms": [
            {"id": "A1", "level_current": 0, "level_target": 3,
             "simplifications": [f"house rationale {CANARY} — that's just how it is"]},
            {"id": "A2", "level_current": 1, "level_target": 2, "simplifications": [CANARY]},
        ],
        "claims_text": "the map is exhausted, nothing to draw",
        "runhist": [], "insights": {}, "agent_status": {},
        "gitlog_subjects": [], "idle_count": 0,
    }
    written = organ.run_system_organ(state, invoke_fn=_spy_invoke, log_path=tmp_path / "log.jsonl")
    assert written, "a terminal-state claim with open atoms must fire the organ"
    assert prompts, "the organ must have been invoked"
    for p in prompts:
        assert CANARY not in p, "the map's prose rationale leaked into the payload"


# ── trigger-fires: T2 reports the open-atom count computed from the map ──
def test_t2_terminal_state_fires_with_independently_computed_open_count():
    state = {
        "atoms": [
            {"id": "X1", "level_current": 0, "level_target": 3},
            {"id": "X2", "level_current": 2, "level_target": 3},
            {"id": "X3", "level_current": 3, "level_target": 3},  # at target, not open
        ],
        "claims_text": "STATUS: the map is exhausted — no drawable atoms.",
        "runhist": [], "agent_status": {}, "gitlog_subjects": [], "idle_count": 0,
    }
    fires = organ.detect_t2(state)
    assert len(fires) == 1
    t = fires[0]
    assert t.trigger_id == "T2_terminal_state"
    # 2 of 3 atoms are below target — computed from the YAML, not hardcoded
    assert t.observed_value["open_atoms"] == 2
    assert set(t.observed_value["open_ids"]) == {"X1", "X2"}


# ── seed replay (inline weekend fixture): >= 3 distinct triggers rediscover ──
def test_seed_replay_rediscovers_at_least_three_weekend_catches():
    """Blind replay of this weekend's observable state: the organ, with no
    hindsight, must independently fire >= 3 of the 7 real catches (design §4)."""
    state = {
        # 31 atoms below target (the '31 BELOW target' weekend state) ...
        "atoms": [{"id": f"a{i}", "level_current": 0, "level_target": 3} for i in range(31)],
        # ... while claims assert terminal + inherence
        "claims_text": (
            "the map is exhausted, no drawable atoms. "
            "BUILD is inherently narrow and must be one tree at a time."
        ),
        # flat net=£1,505,286 across runs, all statuses healthy (T1)
        "runhist": [{"net_margin_gbp": 1505286.0} for _ in range(3)],
        "agent_status": {"agents": [{"status": "idle", "anomaly": None}]},
        # repeated [ACTION NEEDED] / idle-variant fix-class (T7)
        "gitlog_subjects": [
            "R3 [ACTION NEEDED] guard the idle hole again",
            "another [action needed] patch",
            "[ACTION NEEDED] third idle variant",
            "harness: supervisor idle-turn refill draw tweak",
        ],
        "idle_count": 9,
    }
    fired = organ.run_detectors(state)
    fired_ids = {t.trigger_id.split("_", 1)[0] + "_" + t.trigger_id.split("_")[1] for t in fired}
    kinds = {tid[:2] for tid in (t.trigger_id for t in fired)}
    assert len(kinds) >= 3, f"expected >=3 distinct trigger families, got {kinds}"
    # the three named canonical catches: T2 (exhausted+open), T3 (inherence), T7 (fix-class)
    triggered = {t.trigger_id for t in fired}
    assert any(t.startswith("T2") for t in triggered), "T2 terminal-state must fire"
    assert any(t.startswith("T3") for t in triggered), "T3 inherence must fire"
    assert any(t.startswith("T7") for t in triggered), "T7 repeated-fix-class must fire"


# ── DoD seed-replay: the FROZEN weekend fixture (design §4), not an inline dict.
# Blind replay — the organ, given only the amnesiac inputs, must independently
# rediscover >= 3 of the 7 real catches the director caught by hand. ──
def test_fixture_exists_and_encodes_the_weekend_state():
    """The frozen fixture is real (31 atoms below target, flat net, the live
    claim strings), so the replay below is a closed-loop replay of the actual
    weekend state (R4), not a hand-tuned pass."""
    state = _load_weekend_fixture()
    assert len(organ.open_atoms(state["atoms"])) == 31, "the '31 BELOW target' weekend state"
    vals = organ._net_margins(state["runhist"], 3)
    assert vals and max(vals) - min(vals) < organ.FLAT_METRIC_EPSILON_GBP, "flat net=£1,505,286"
    assert "exhausted" in state["claims_text"].lower()


def test_seed_replay_from_frozen_fixture_rediscovers_at_least_three_catches(tmp_path):
    """DoD: run the full detector suite over the FROZEN fixture and assert >= 3
    distinct trigger families rediscover the real catches, with the three named
    canonical ones (T2 exhausted+open, T3 inherence, T7 repeated-fix-class)
    among them. Opus is STUBBED for determinism — the FIRING is what we assert
    mechanically; real-Opus question-wording is the L3 residual."""
    state = _load_weekend_fixture()

    fired = organ.run_detectors(state)
    families = {t.trigger_id[:2] for t in fired}
    assert len(families) >= 3, f"expected >= 3 of 7 catches rediscovered, got {sorted(families)}"

    ids = {t.trigger_id for t in fired}
    assert any(t.startswith("T2") for t in ids), "T2: 'exhausted' while 31 atoms open"
    assert any(t.startswith("T3") for t in ids), "T3: 'build must be narrow' inherence claim"
    assert any(t.startswith("T7") for t in ids), "T7: repeated [ACTION NEEDED]/idle fix-class"

    # T2 reports the open-atom count computed FROM THE FIXTURE MAP (31), not hardcoded
    t2 = next(t for t in fired if t.trigger_id.startswith("T2"))
    assert t2.observed_value["open_atoms"] == 31

    # every firing produces a well-formed, OPEN log record with a non-empty question
    log = tmp_path / "log.jsonl"
    written = organ.run_system_organ(
        state, invoke_fn=lambda p: "which is true?", log_path=log, max_new=None)
    assert len(written) >= 3
    for rec in written:
        assert rec["verdict"] == "open"
        assert rec["question"], "the amnesiac organ must have produced a question"
        assert rec["fired_on"]["claim"]


def test_run_organ_cycle_and_digest_section_are_wired(tmp_path, monkeypatch):
    """The LIVE HOOK: run_organ_cycle() loads state + fires the organ (Opus
    injected), and render_digest_section() emits the 'NAIVE ORGAN asks:' sink
    with the open questions. max_new bounds new questions per cycle."""
    monkeypatch.setattr(organ, "load_state", lambda **kw: _load_weekend_fixture())
    log = tmp_path / "log.jsonl"

    written = organ.run_organ_cycle(
        invoke_fn=lambda p: "a sharp naive question?", log_path=log, max_new=2)
    assert len(written) == 2, "max_new must cap NEW questions per cycle"

    section = organ.render_digest_section(log_path=log)
    assert section.startswith("**NAIVE ORGAN asks:**")
    assert "a sharp naive question?" in section

    # a fresh cycle re-fires the un-asked triggers (still debounced on the open ones)
    more = organ.run_organ_cycle(
        invoke_fn=lambda p: "another question?", log_path=log, max_new=None)
    assert more, "un-asked triggers surface on the next cycle"


def test_falsify_staged_doc_reads_from_disk(tmp_path):
    """TARGET 2 entry point is real + callable: read an advisor-staged doc from
    disk and run a FALSIFY pass on it before the agent acts."""
    doc = tmp_path / "ADVISOR_PLAN.md"
    doc.write_text("PLAN: open every BUILD atom at once; it is obviously safe.")
    prompts = []
    log = tmp_path / "log.jsonl"
    rec = organ.falsify_staged_doc(
        doc, invoke_fn=lambda p: prompts.append(p) or "assumption: file scopes disjoint",
        log_path=log)
    assert rec["mode"] == organ.MODE_FALSIFY
    assert rec["target"] == organ.TARGET_ADVISOR
    assert "MODE: FALSIFY" in prompts[0]
    assert "open every BUILD atom" in prompts[0], "the doc text on disk reached the payload"


# ── the answer-writer REJECTS an empty-evidence answer (mechanism) ──
def test_answer_rejects_empty_evidence_and_accepts_with_evidence(tmp_path):
    log = tmp_path / "log.jsonl"
    trig = organ.Trigger(
        trigger_id="T2_terminal_state", mode=organ.MODE_INTERROGATE,
        claim_text="map exhausted", evidence_refs=("maturity_map.yaml",),
        observed_value={"open_atoms": 5}, fire_reason="terminal claim w/ 5 open",
    )
    rec = organ.ask_organ(trig, invoke_fn=lambda p: "which is true?", log_path=log)
    assert rec["verdict"] == "open"
    eid = rec["entry_id"]

    # 'that's just how it is' — empty evidence — is REJECTED
    with pytest.raises(organ.EmptyEvidenceRejected):
        organ.answer_question(eid, "that's just how it is", [], log_path=log)
    with pytest.raises(organ.EmptyEvidenceRejected):
        organ.answer_question(eid, "no answer text", ["  "], log_path=log)

    # 'no, that was true because X' with a fetchable ref CLOSES it
    closed = organ.answer_question(
        eid, "no — the 5 were parked idle, not drawable",
        ["docs/design/maturity_map.yaml#loop_stage"], log_path=log,
    )
    assert closed["verdict"] == "answered_with_evidence"
    assert closed["answer_evidence"] == ["docs/design/maturity_map.yaml#loop_stage"]
    assert organ.open_questions(log_path=log) == []


# ── THE LINE: the organ NEVER questions PURPOSE (declined before any Opus call) ──
def test_the_line_declines_purpose_claims_without_invoking(tmp_path):
    log = tmp_path / "log.jsonl"
    calls = []

    def _tracking(prompt):
        calls.append(prompt)
        return "should never be asked"

    rec = organ.interrogate_claim(
        "the fitness function should reward enterprise value growth",
        source="director", invoke_fn=_tracking, log_path=log,
    )
    assert rec["verdict"] == "declined_purpose"
    assert rec["question"] is None
    assert calls == [], "THE LINE: purpose must be declined BEFORE any Opus spend"

    # a FACTUAL claim from the same source IS interrogated
    rec2 = organ.interrogate_claim(
        "the 2021 gas price never exceeded 200p/therm",
        source="director", invoke_fn=_tracking, log_path=log,
    )
    assert rec2["verdict"] == "open"
    assert len(calls) == 1


def test_is_purpose_claim_guards_values_but_not_facts():
    assert organ.is_purpose_claim("what should the company value most?")
    assert organ.is_purpose_claim("the Epoch-4 fitness function is wrong")
    assert not organ.is_purpose_claim("the map is exhausted")
    assert not organ.is_purpose_claim("net margin was £1,505,286")


# ── TARGET 2: advisor-staged doc FALSIFY entry point ──
def test_falsify_advisor_doc_runs_a_falsify_pass(tmp_path):
    log = tmp_path / "log.jsonl"
    prompts = []
    rec = organ.falsify_advisor_doc(
        "docs/staging/ADVISOR_PLAN.md",
        "PLAN: parallelise all builds at once; it is obviously safe.",
        invoke_fn=lambda p: prompts.append(p) or "assumption: file scopes are disjoint...",
        log_path=log,
    )
    assert rec["mode"] == organ.MODE_FALSIFY
    assert rec["target"] == organ.TARGET_ADVISOR
    assert rec["verdict"] == "open"
    assert rec["question"]  # a falsification attempt was produced
    # the FALSIFY rubric (break the plan) was used, not INTERROGATE
    assert "MODE: FALSIFY" in prompts[0]


# ── anti-capture: the payload carries no prior questions/answers (Law-B) ──
def test_anti_capture_payload_contains_no_prior_qa(tmp_path):
    log = tmp_path / "log.jsonl"
    prompts = []

    def _spy(prompt):
        prompts.append(prompt)
        return f"question number {len(prompts)}"

    t1 = organ.Trigger("T3_inherence", organ.MODE_INTERROGATE, "build must be narrow",
                       ("gitlog",), {"inherence_token": "must be narrow"}, "inherence")
    t2 = organ.Trigger("T3_inherence", organ.MODE_INTERROGATE, "worktrees are impossible to use",
                       ("gitlog",), {"inherence_token": "impossible to"}, "inherence")
    r1 = organ.ask_organ(t1, invoke_fn=_spy, log_path=log)
    organ.ask_organ(t2, invoke_fn=_spy, log_path=log)
    # the second prompt must not contain the first question or the first claim
    assert r1["question"] not in prompts[1]
    assert "build must be narrow" not in prompts[1]


def test_anti_capture_thresholds_are_source_constants():
    # thresholds are fixed module constants — the only permitted change is a
    # director/twin-authored source edit, never learned from outcomes
    for name in ("FLAT_METRIC_EPSILON_GBP", "FIXCLASS_MIN_COUNT",
                 "SUSTAINED_BUCKET_FRACTION", "IDLE_TURN_THRESHOLD"):
        assert isinstance(getattr(organ, name), (int, float))


# ── debounce: an already-open (trigger, claim) is not re-asked ──
def test_debounce_does_not_reask_an_open_question(tmp_path):
    log = tmp_path / "log.jsonl"
    trig = organ.Trigger("T2_terminal_state", organ.MODE_INTERROGATE, "map exhausted",
                         ("maturity_map.yaml",), {"open_atoms": 3}, "terminal")
    r1 = organ.ask_organ(trig, invoke_fn=lambda p: "q?", log_path=log)
    r2 = organ.ask_organ(trig, invoke_fn=lambda p: "q?", log_path=log)
    assert r1 is not None
    assert r2 is None, "an already-open question must not be re-asked (no duplicate Opus call)"


def test_hit_rate_is_a_diagnostic(tmp_path):
    log = tmp_path / "log.jsonl"
    t = organ.Trigger("T2_terminal_state", organ.MODE_INTERROGATE, "map exhausted",
                      ("m.yaml",), {"open_atoms": 3}, "terminal")
    rec = organ.ask_organ(t, invoke_fn=lambda p: "q?", log_path=log)
    organ.mark_verdict(rec["entry_id"], "hit", log_path=log)
    hr = organ.hit_rate(log_path=log)
    assert hr["hits"] == 1 and hr["misses"] == 0
    assert hr["hit_rate"] == 1.0


# ═══════════════════════════════════════════════════════════════════════════
# L2 -> L3 (2026-07-14, NAIVE_ORGAN_BLIND_SPOT_AND_USAGE_WRITE.md): the organ
# runs on its OWN wall clock (director gap #1) + T8 EXPECTED OUTPUT ABSENT
# (director gap #2), with the R15 mutation test against THIS outage, plus the
# shared-failure-domain self-audit.
# ═══════════════════════════════════════════════════════════════════════════

_NOW = 1_800_000_000.0  # a fixed wall-clock 'now' for deterministic silence maths
_SIX_HOURS = 6 * 3600


def _silent_state(silence_seconds: float, *, last_commit_epoch=None) -> dict:
    """A minimal live-shaped state carrying the T8 silence signal. Defaults to a
    commit `silence_seconds` in the past; `last_commit_epoch` overrides directly
    (e.g. 0.0 to simulate an unavailable clock)."""
    lce = last_commit_epoch if last_commit_epoch is not None else _NOW - silence_seconds
    return {
        "atoms": [], "runhist": [], "insights": {}, "agent_status": {},
        "claims_text": "", "gitlog_subjects": [], "idle_count": 0,
        "last_commit_epoch": lce, "now": _NOW,
    }


# ── R15 MUTATION TEST — the 6h blackout: silent 6h -> the organ FIRES ──
def test_t8_fires_on_the_six_hour_blackout():
    """R15 mutation test against THIS outage (NAIVE_ORGAN_BLIND_SPOT §DoD):
    reproduce the 6h silent wedge (22:12->04:00, no commit/publish) as the named
    defect and prove T8 fires on it. 6h > the 3h cadence -> the organ asks 'why
    is it quiet?' — the exact question the publish-coupled organ never could."""
    fires = organ.detect_t8(_silent_state(_SIX_HOURS))
    assert len(fires) == 1
    t = fires[0]
    assert t.trigger_id == "T8_expected_output_absent"
    assert t.mode == organ.MODE_INTERROGATE
    assert t.observed_value["silence_hours"] == 6.0
    assert t.observed_value["clock_available"] is True


# ── the control CAN pass (not fail-open / not a tautology): recent commit -> silent ──
def test_t8_does_not_fire_when_a_commit_is_recent():
    """A control that always fires is as useless as one that never does. A commit
    10 min ago is inside cadence -> T8 must NOT fire, proving it discriminates on
    the real signal rather than firing unconditionally."""
    assert organ.detect_t8(_silent_state(10 * 60)) == []
    # exactly at the threshold is still inside (>= cadence fires; < does not)
    assert organ.detect_t8(_silent_state(organ.EXPECTED_OUTPUT_CADENCE_SECONDS - 1)) == []
    assert len(organ.detect_t8(_silent_state(organ.EXPECTED_OUTPUT_CADENCE_SECONDS + 1))) == 1


# ── FAIL-SILENT DOCTRINE (R15): an unavailable clock is a FAILED check -> fire ──
def test_t8_fires_when_the_commit_clock_is_unavailable():
    """last_commit_epoch == 0.0 means git itself was unreachable. Per R15's
    fail-silent doctrine an unavailable liveness check is a FAILED check — so the
    organ must FIRE (ask), never assume health. Silence reads as effectively
    infinite (now - 0)."""
    fires = organ.detect_t8(_silent_state(0, last_commit_epoch=0.0))
    assert len(fires) == 1
    assert fires[0].observed_value["clock_available"] is False


# ── ABSENT signal (a claim-only fixture that never collected it) must not alarm ──
def test_t8_no_fires_when_the_silence_signal_was_never_collected():
    """A hand-built claim-only state (no last_commit_epoch key) never gathered the
    silence signal, so T8 must NOT manufacture an alarm from its absence — that
    keeps every existing claim-driven fixture/replay clean and is the honest
    distinction from the clock-unavailable (0.0) case above."""
    state = {"atoms": [], "runhist": [], "claims_text": "", "gitlog_subjects": [],
             "idle_count": 0, "agent_status": {}, "insights": {}}
    assert "last_commit_epoch" not in state
    assert organ.detect_t8(state) == []


def test_t8_is_registered_and_wired_into_run_detectors():
    assert organ.detect_t8 in organ.ALL_DETECTORS
    fired = organ.run_detectors(_silent_state(_SIX_HOURS))
    assert any(t.trigger_id == "T8_expected_output_absent" for t in fired)


# ── INDEPENDENT WALL CLOCK (director gap #1): the daemon fires with NO publish ──
def test_run_daemon_fires_the_organ_off_its_own_clock_not_a_publish(tmp_path, monkeypatch):
    """The organ's schedule must NOT be wake-coupled to the publish cycle. Prove
    the daemon runs run_organ_cycle on its OWN tick — here it asks a T8 question
    about a 6h silence while NO publish/process_run_complete ever ran. This is the
    condition the old publish-hooked organ went blind on (it woke on the pipeline
    that had died)."""
    monkeypatch.setattr(organ, "load_state", lambda **kw: _silent_state(_SIX_HOURS))
    log = tmp_path / "log.jsonl"
    prompts = []

    cycles = organ.run_daemon(
        invoke_fn=lambda p: prompts.append(p) or "why is it quiet?",
        log_path=log, once=True)
    assert cycles == 1
    opens = organ.open_questions(log_path=log)
    assert any(e["trigger_id"] == "T8_expected_output_absent" for e in opens), (
        "the daemon must fire T8 on silence with no publish having occurred"
    )
    assert prompts, "the amnesiac organ was invoked off the wall clock, not a publish"


def test_run_daemon_loops_on_its_own_timer_and_never_raises(monkeypatch):
    """The loop is driven by an injected sleep so no real time passes; it must run
    the configured number of cycles and NEVER propagate an exception (a doubt
    organ that crashes its own loop is itself fail-silent)."""
    ticks = {"cycles": 0, "sleeps": 0}

    def _boom(**kw):
        ticks["cycles"] += 1
        raise RuntimeError("cycle blew up")

    monkeypatch.setattr(organ, "run_organ_cycle", _boom)
    n = organ.run_daemon(sleep_fn=lambda s: ticks.__setitem__("sleeps", ticks["sleeps"] + 1),
                         max_cycles=3, poll_interval=0)
    assert n == 3, "the loop ran its cycles despite every cycle raising"
    assert ticks["cycles"] == 3
    assert ticks["sleeps"] == 2, "sleeps between cycles, not after the last"


# ── SHARED-FAILURE-DOMAIN SELF-AUDIT (L3 meta-task): the organ questions its OWN
# coupling, with the 6h outage as the worked example ──
def test_shared_failure_domain_audit_flags_the_pre_fix_couplings():
    audit = organ.shared_failure_domain_audit()
    by_name = {e["name"]: e for e in audit}

    # the two organs that shared a failure domain with what they monitored
    assert by_name["naive_organ (pre-2026-07-14)"]["shares_failure_domain"] is True
    assert by_name["deadmans_switch (pre-2026-07-14)"]["shares_failure_domain"] is True
    # both are FIXED now — the post-fix rows are uncoupled
    assert by_name["naive_organ (post-2026-07-14)"]["shares_failure_domain"] is False
    assert by_name["deadmans_switch (post-2026-07-14)"]["shares_failure_domain"] is False
    # the twin/cold-eyes are not continuous liveness monitors -> no silent-death class
    assert by_name["director_twin approver"]["shares_failure_domain"] is False


def test_shared_failure_domain_findings_are_only_historical_post_fix():
    """Post-fix, the only rows admitting a shared failure domain are the PRE-fix
    historical ones — no LIVE mechanism may still share a clock with what it
    audits, or that is a defect to fix, not a note to file."""
    findings = organ.shared_failure_domain_findings()
    names = {f["name"] for f in findings}
    assert names == {"naive_organ (pre-2026-07-14)", "deadmans_switch (pre-2026-07-14)"}
    for f in findings:
        assert "pre-2026-07-14" in f["name"], "a LIVE shared-failure-domain row is a defect"
