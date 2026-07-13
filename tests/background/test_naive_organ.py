"""Tests for background/naive_organ.py — the deliberately-amnesiac question/
falsify organ (THE_NAIVE_ORGAN.md + the 2026-07-13 DIRECTOR AMENDMENT).

An injectable invoke_fn is used throughout so no real `claude -p` process is
spawned in CI (slow, non-deterministic, costs real tokens) — mirrors
test_director_twin.py. The amnesia is proven at the PROCESS level (empty cwd,
tools off, payload closed over four explicit args), not by prose.
"""
import subprocess

import pytest

from background import naive_organ as organ


CANARY = "NAIVE_ORGAN_CANARY_7Q3"


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
