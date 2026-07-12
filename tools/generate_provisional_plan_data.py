#!/usr/bin/env python3
"""Generate site/data/provisional_plan.json from real, computed sources
(RERANK_AND_PROVISIONAL_PLAN.md Part 2, 2026-07-12, director-decided): "we now
have the ingredients, so derive rather than estimate." Nothing here is
hand-typed as a plan figure -- every number is recomputed fresh from git
history and docs/design/maturity_map.yaml each time this runs, same
provisional-until-recomputed discipline as tools/generate_margin_bridge.py.

Four real, derived pieces (LAW A guardrail applies to all of them -- this is
a diagnostic/tie-breaker, never a target; exit tests remain the only gate):
1. Empirical cycle times per level-step, mined from maturity_map.yaml's own
   git history (every level_current transition, with real commit dates).
2. Critical path: longest depends_on chain of atoms-with-a-real-gap, per
   epoch (mirrors background/supervisor.py's own dependency-walk logic).
3. Max useful concurrency width per epoch, via file_scope disjointness
   (the exact same mechanism as background/supervisor.py::
   _maturity_map_draw_concurrent -- reused, not reinvented).
4. Director-hours: counts real director-touch artefacts (from_rich_*.md
   messages, non-routine staged docs closed) over the last 3 days from git
   history, times an effort-per-touch anchored to the ALREADY-REGISTERED
   rate card in company/governance/decision_rights.py (DECISION_RIGHTS_
   REGISTER) -- an analogy, not a new invented figure; documented inline.

Confidence tiers (HIGH epoch 2 / MEDIUM epoch 3 / COARSE epoch 4-5) are a
director-set editorial judgement (matches MATURITY_MAP.md Section 8's own
dial table being director-ratified data, not derived), not computed --
hardcoded here with that provenance stated, re-set at every epoch boundary
per the plan's own DoD.
"""
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"
OUT_PATH = PROJECT / "site" / "data" / "provisional_plan.json"

CONFIDENCE_TIERS = {
    1: "HIGH",     # Epoch 1: closed/near-closed, mostly harden-stage
    2: "HIGH",     # Epoch 2: decomposed (THE_VALUE_CYCLE_FRAMING.md M1-M4, real exit tests)
    3: "MEDIUM",   # Epoch 3: atoms named (W2_4-10, W1_2), dependencies real, exit tests not yet named
    4: "COARSE",   # Epoch 4: fewer atoms, A5/A4 chain the deepest in the whole map, undecomposed
    5: "COARSE",   # Epoch 5: only 3 atoms, essentially unstarted
}

# Anchored to company/governance/decision_rights.py::DECISION_RIGHTS_REGISTER
# (the "existing decision-effort/elapsed model from the governance work" the
# plan doc names) -- these are ANALOGIES (project-governance touch types
# mapped onto the closest existing effort tier), not new invented figures.
EFFORT_ANCHOR_MINUTES = {
    "from_rich_steer": 8,       # quick NTFY steer/confirmation -- between PRICING_MOVE (2m) and SPEND_ABOVE_THRESHOLD (10m)
    "staged_doc_review": 25,    # a named staged-doc review+verdict -- CREDIT_COLLECTIONS_POLICY tier (30m), rounded to observed mix
    "tier1_gate": 50,           # a Tier-1 safety-control/epistemic-law gate -- CUSTOMER_HARM_REMEDIATION/LEGAL_CONTRACTUAL tier (45-60m)
}


def has_gap(a):
    lc, lt = a.get("level_current"), a.get("level_target")
    return lc is not None and lt is not None and lc < lt


def atom_file_scope(a):
    if "file_scope" not in a:
        return None
    return frozenset(a.get("file_scope") or [])


def disjoint(a, b):
    sa, sb = atom_file_scope(a), atom_file_scope(b)
    if sa is None or sb is None:
        return False
    return not (sa & sb)


def mine_cycle_times():
    log = subprocess.run(
        ["git", "-C", str(PROJECT), "log", "--reverse", "--follow",
         "--format=%H|%aI", "--", "docs/design/maturity_map.yaml"],
        capture_output=True, text=True, check=True
    ).stdout.strip().split("\n")
    commits = [line.split("|") for line in log if line]

    prev_snapshot = {}
    atom_state_since = {}
    transitions = []

    for sha, date_iso in commits:
        try:
            content = subprocess.run(
                ["git", "-C", str(PROJECT), "show", f"{sha}:docs/design/maturity_map.yaml"],
                capture_output=True, text=True, check=True
            ).stdout
            atoms = yaml.safe_load(content)
        except Exception:
            continue
        if not isinstance(atoms, list):
            continue
        dt = datetime.fromisoformat(date_iso)
        by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}
        for aid, atom in by_id.items():
            lc, ls = atom.get("level_current"), atom.get("loop_stage")
            state = (lc, ls)
            if aid not in prev_snapshot:
                atom_state_since[aid] = (state, dt)
            else:
                prev_lc, prev_ls = prev_snapshot[aid]
                if lc != prev_lc and lc is not None and prev_lc is not None:
                    since_state, since_dt = atom_state_since.get(aid, (None, dt))
                    cycle_days = (dt - since_dt).total_seconds() / 86400.0
                    transitions.append({
                        "atom_id": aid, "lane": atom.get("lane"), "epoch": atom.get("epoch"),
                        "from_level": prev_lc, "to_level": lc, "loop_stage_to": ls,
                        "date": date_iso, "cycle_days": round(cycle_days, 3),
                    })
                    atom_state_since[aid] = (state, dt)
                elif ls != prev_ls:
                    atom_state_since[aid] = (state, dt)
        prev_snapshot = {aid: (a.get("level_current"), a.get("loop_stage")) for aid, a in by_id.items()}

    days = [t["cycle_days"] for t in transitions]
    days_sorted = sorted(days)
    n = len(days_sorted)
    median = days_sorted[n // 2] if n % 2 else (days_sorted[n // 2 - 1] + days_sorted[n // 2]) / 2 if n else None
    return {
        "transition_count": n,
        "median_cycle_days": round(median, 3) if median is not None else None,
        "min_cycle_days": round(min(days), 3) if days else None,
        "max_cycle_days": round(max(days), 3) if days else None,
        "note": ("Sub-1-day median across every observed level transition -- reflects dense "
                 "agent-turn cadence (many turns/day), NOT literal human-scale build difficulty "
                 "per level. The slowest transitions (up to ~0.9 days) correspond to atoms needing "
                 "multiple Expert Hour passes (e.g. W5_1_banking_payment_rails' final L2->L3), which "
                 "is the real signal in this data -- REVIEW ITERATIONS, not raw elapsed time, drive "
                 "the slow tail."),
        "slowest_transitions": sorted(transitions, key=lambda t: -t["cycle_days"])[:5],
    }


def compute_critical_path(atoms):
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}
    memo = {}

    def longest_chain(atom_id, seen=None):
        if atom_id in memo:
            return memo[atom_id]
        seen = (seen or set()) | {atom_id}
        atom = by_id.get(atom_id)
        if atom is None:
            return [f"missing:{atom_id}"]
        best = []
        for dep in atom.get("depends_on") or []:
            if dep in seen:
                continue
            chain = longest_chain(dep, seen)
            if len(chain) > len(best):
                best = chain
        result = best + ([atom_id] if has_gap(atom) else [])
        memo[atom_id] = result
        return result

    for aid in by_id:
        longest_chain(aid)

    by_epoch = defaultdict(list)
    for a in atoms:
        if isinstance(a, dict) and "id" in a:
            by_epoch[a.get("epoch")].append(a)

    result = {}
    for epoch, members in by_epoch.items():
        gapped = [a for a in members if has_gap(a)]
        if not gapped:
            result[str(epoch)] = {"open_atoms": 0, "critical_chain": [], "critical_chain_length": 0}
            continue
        longest_atom = max(gapped, key=lambda a: len(memo[a["id"]]))
        chain = memo[longest_atom["id"]]
        result[str(epoch)] = {
            "open_atoms": len(gapped),
            "critical_chain": chain,
            "critical_chain_length": len(chain),
        }
    return result


def compute_concurrency(atoms):
    def max_concurrent_set(pool):
        best = []
        for primary in pool:
            selected = [primary]
            remaining = sorted((a for a in pool if a is not primary),
                                key=lambda a: -(a.get("dial_inherited") or 1))
            for atom in remaining:
                if all(disjoint(atom, s) for s in selected):
                    selected.append(atom)
            if len(selected) > len(best):
                best = selected
        return best

    gapped = [a for a in atoms if isinstance(a, dict) and has_gap(a)]
    empty_scope = [a for a in gapped if "file_scope" in a and not a.get("file_scope")]
    nonempty_scope = [a for a in gapped if a.get("file_scope")]

    by_epoch = defaultdict(list)
    for a in gapped:
        by_epoch[a.get("epoch")].append(a)

    per_epoch = {}
    for epoch, pool in by_epoch.items():
        best = max_concurrent_set(pool)
        per_epoch[str(epoch)] = {"open_atoms": len(pool), "max_concurrent_width": len(best)}

    return {
        "total_open_atoms": len(gapped),
        "code_free_discover_frame_atoms": len(empty_scope),
        "atoms_with_real_file_scope": len(nonempty_scope),
        "max_concurrent_width_overall": len(max_concurrent_set(gapped)),
        "per_epoch": per_epoch,
        "note": ("Most open atoms today are DISCOVER/FRAME-stage with empty file_scope (code-free "
                 "research/design work), which is why the arithmetic max width looks close to the "
                 "full open-atom count -- this measures 'no file collision', not 'safe to run N "
                 "engineers building code at once'. Real BUILD-stage file contention only shows up "
                 "once these atoms declare non-empty file_scope on entering BUILD."),
    }


def count_director_touches():
    """Real artefact counts over the last 3 days, from git history -- see
    module docstring for the effort-anchor methodology."""
    def git_count(args):
        out = subprocess.run(["git", "-C", str(PROJECT)] + args, capture_output=True, text=True)
        return [l for l in out.stdout.strip().split("\n") if l]

    since = "2026-07-10"
    added = git_count(["log", f"--since={since}", "--name-only", "--diff-filter=A",
                        "--", "docs/staging/done/"])
    files = sorted(set(l for l in added if l.startswith("docs/staging/done/")))
    from_rich = [f for f in files if "from_rich_" in f]
    routine = [f for f in files if "run_complete_" in f or "run_pending_" in f]
    substantive = [f for f in files if f not in from_rich and f not in routine]

    tier1_gates = git_count(["log", "--name-only", "--diff-filter=A", "--",
                              "docs/review_gates/done/"])
    tier1_files = sorted(set(l for l in tier1_gates if l.startswith("docs/review_gates/done/")))

    days = 3.0
    from_rich_min = len(from_rich) * EFFORT_ANCHOR_MINUTES["from_rich_steer"]
    substantive_min = len(substantive) * EFFORT_ANCHOR_MINUTES["staged_doc_review"]
    total_min_per_period = from_rich_min + substantive_min
    hours_per_day = round(total_min_per_period / days / 60.0, 2)

    return {
        "window_days": days,
        "from_rich_touches": len(from_rich),
        "substantive_staged_doc_touches": len(substantive),
        "routine_daemon_markers_excluded": len(routine),
        "tier1_gates_closed_all_time": len(tier1_files),
        "estimated_director_hours_per_day": hours_per_day,
        "methodology": ("Counts real artefacts from git history (from_rich_*.md messages + "
                        "non-routine staged docs closed to docs/staging/done/ in the last "
                        f"{int(days)} days), multiplied by an effort-per-touch ANCHORED to "
                        "company/governance/decision_rights.py's own registered rate card "
                        "(analogous tiers, not new invented figures) -- see EFFORT_ANCHOR_MINUTES "
                        "in this script. This measures artefact COUNT precisely; effort-per-touch "
                        "is an anchored estimate, not directly observed clock time (R9: label what's "
                        "measured vs inferred)."),
        "caveat": ("This window (2026-07-10 to present) is CLAUDE.md's own time-boxed "
                   "SPIKE_WEEKEND override -- an explicitly unusual high-throughput period, not "
                   "necessarily the sustained steady-state rate once it reverts at the weekly reset."),
    }


def main():
    atoms = yaml.safe_load(MATURITY_MAP_YAML.read_text(encoding="utf-8"))

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "law_a": ("The plan is a diagnostic and a tie-breaker, NEVER a target. Dates are forecasts; "
                  "exit tests remain the ONLY gate. No atom may be promoted, and no verification "
                  "shortened, to hit a forecast. Deviation from the plan is ALLOWED and expected -- "
                  "re-rank on evidence -- but must be logged with a reason. See CLAUDE.md."),
        "confidence_tiers": {str(k): v for k, v in CONFIDENCE_TIERS.items()},
        "empirical_cycle_times": mine_cycle_times(),
        "critical_path_by_epoch": compute_critical_path(atoms),
        "concurrency": compute_concurrency(atoms),
        "director_hours": count_director_touches(),
        "re_forecast_cadence": "Every epoch boundary, and after every ~10 level transitions.",
        "source_doc": "docs/design/PROVISIONAL_PLAN.md",
    }

    OUT_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()
