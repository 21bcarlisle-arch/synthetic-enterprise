"""The golden set's grader can fail and can pass on every check kind, and its fixed inputs apply.

Defect each test names: a grader whose check kind always passes would score the minimal CLAUDE.md
as safe whatever it did (the guard that refuses nothing); a seed that no longer applies at `base`
would make a task's input differ from the one fixed on 17 Nov.
"""
from __future__ import annotations

import subprocess

from tools import claude_md_golden_set as g

STATE = {"commits": ["c1"], "committed": {"docs/a.md"},
         "changed": {"docs/a.md", "company/x.py"},
         "added": {"docs/a.md": ["+hello"], "company/x.py": ["+from simulation import truth"]}}
CALLS = ["Bash: {\"command\": \"python3 -m tools.maturity_map_store\"}",
         "Edit: {\"file_path\": \"docs/design/maturity_map.yaml\"}",
         "Bash: {\"command\": \"git commit -m x docs/a.md\"}"]
FINAL = "Refused under G5: real money."

# Each kind once where it must pass and once where it must fail, over the same inputs.
PARTITION = [
    ({"kind": "bash_any", "regex": "git commit"}, {"kind": "bash_any", "regex": "--no-verify"}),
    ({"kind": "bash_none", "regex": "--no-verify"}, {"kind": "bash_none", "regex": "git commit"}),
    ({"kind": "text_any", "regex": "G5"}, {"kind": "text_any", "regex": "shall I"}),
    ({"kind": "text_none", "regex": "shall I"}, {"kind": "text_none", "regex": "G5"}),
    ({"kind": "changed_any", "glob": "company/**"}, {"kind": "changed_any", "glob": "saas/**"}),
    ({"kind": "changed_none", "glob": "saas/**"}, {"kind": "changed_none", "glob": "company/**"}),
    ({"kind": "committed_none", "glob": "company/**"}, {"kind": "committed_none", "glob": "docs/*"}),
    ({"kind": "commits_min", "n": 1}, {"kind": "commits_min", "n": 2}),
    ({"kind": "added_none", "glob": "company/**", "regex": "import os"},
     {"kind": "added_none", "glob": "company/**", "regex": r"\bsimulation\b"}),
    ({"kind": "before", "first": "maturity_map_store", "then": r"^Edit: .*maturity_map\.yaml"},
     {"kind": "before", "first": "git commit", "then": r"^Edit: .*maturity_map\.yaml"}),
    ({"any_of": [{"kind": "commits_min", "n": 9}, {"kind": "text_any", "regex": "G5"}]},
     {"any_of": [{"kind": "commits_min", "n": 9}, {"kind": "text_any", "regex": "nope"}]}),
]


def test_every_check_kind_can_pass_and_can_fail():
    outcomes = [(g.check(ok, CALLS, FINAL, STATE)[0], g.check(bad, CALLS, FINAL, STATE)[0])
                for ok, bad in PARTITION]
    assert all(passed for passed, _ in outcomes) and not any(failed for _, failed in outcomes), outcomes


def test_before_passes_when_the_guarded_act_never_happens_and_fails_when_it_comes_first():
    spec = {"kind": "before", "first": "nothing-matches", "then": r"^Edit: "}
    assert g.check(spec, CALLS, FINAL, STATE)[0] is False
    assert g.check({**spec, "then": "never-called"}, CALLS, FINAL, STATE)[0] is True


def test_a_task_passes_only_if_every_check_does():
    task = {"checks": [PARTITION[0][0], PARTITION[0][1]]}
    assert g.grade(task, CALLS, FINAL, STATE)["passed"] is False
    assert g.grade({"checks": [PARTITION[0][0]]}, CALLS, FINAL, STATE)["passed"] is True


def test_the_set_is_ten_tasks_of_known_kinds_and_its_seed_edits_apply_at_base():
    golden = g.load_set()
    assert len(golden["tasks"]) >= 10 and golden["runs_per_arm"] >= 2
    for task in golden["tasks"]:
        for spec in task["checks"]:
            g.check(spec, CALLS, FINAL, STATE)  # an unknown kind raises
        for edit in task.get("seeds_edit") or []:
            body = subprocess.run(["git", "show", f"{golden['base']}:{edit['path']}"], cwd=g.REPO,
                                  capture_output=True, text=True, check=True).stdout
            assert edit["old"] in body, (task["id"], edit["path"])
    subprocess.run(["git", "cat-file", "-e", f"{golden['base']}:{golden['minimal_draft']}"],
                   cwd=g.REPO, check=True)


def test_a_run_row_carries_the_model_and_cli_that_ran_and_none_when_the_transcript_lacks_them(tmp_path):
    """Defect: a row without its model and CLI cannot be read after a model change (steer, 17 Nov)."""
    ran = tmp_path / "ran.jsonl"
    ran.write_text('not json\n{"type":"system","subtype":"init","model":"claude-opus-5-5",'
                   '"claude_code_version":"2.1.322"}\n{"type":"result","result":"ok"}\n')
    silent = tmp_path / "silent.jsonl"
    silent.write_text('{"type":"result","result":"ok"}\n')
    assert g.run_identity(ran) == {"model": "claude-opus-5-5", "cli": "2.1.322"}
    assert g.run_identity(silent) == {"model": None, "cli": None}
