# Pre-restore bytes: the four worktree copies replaced by HEAD's, 2026-09-08

Kept so the restore is reversible. Each was verified strictly older than HEAD:
its symbol set is a subset of HEAD's and it adds no definition HEAD lacks.

## background/process_run_complete.py
```diff
diff --git a/background/process_run_complete.py b/background/process_run_complete.py
index 143992192..1fa1264ef 100644
--- a/background/process_run_complete.py
+++ b/background/process_run_complete.py
@@ -1,7 +1,6 @@
 #!/usr/bin/env python3
 import ast
 import fcntl
-import io
 import json
 import os
 import re
@@ -1075,6 +1074,7 @@ from background import (  # noqa: E402
     publish_cause,  # (which of the four an rc=77 was, and the observation that decided it)
     publish_gate_blocking_read,  # (the record's honesty contract)
     publish_provenance,  # BOUND HERE ON PURPOSE — see below
+    standing_red,  # (is this the SAME red as last cycle, and for how many cycles)
 )
 
 # ONE GENERATION PER CYCLE (2026-09-01). This was five lazy `from background import
@@ -3175,11 +3175,10 @@ _REFUSING_GATE_BANNERS = (
     ("running-total-order gate",
      ("running-total-order: COMMIT REFUSED.",), "tools/running_total_order.py"),
     ("scope-evidence ratchet", ("[scope-evidence] ❌",), "tools/scope_evidence_ratchet.py"),
-    # Both commons gates print their banner as an f-string, so the needle is the LITERAL part up
-    # to the interpolation -- `REFUSED (` and not `REFUSED (3)`. The trailing `(` is what keeps
-    # the needle off the sibling PASS line, which is the same sentence with one word swapped:
-    # `commons source supersession: PASS (9 artefacts askable)`. Dropping it would name a gate
-    # that let the commit through, which is the fail-open twin this table already has a leg for.
+    # BOTH COMMONS GATES ASSEMBLE THEIR BANNER AS f"...: REFUSED ({n})", so the needle stops at the
+    # open paren -- the count is interpolated and is not a literal. The trailing `: REFUSED (` is
+    # what separates it from the pass line, which is the SAME sentence ending `: PASS (`. A needle
+    # on the module's own name alone would match the run that let the commit through.
     ("commons-source-supersession gate",
      ("commons source supersession: REFUSED (",), "tools/commons_source_supersession.py"),
     ("commons-citation-provenance gate",
@@ -3475,6 +3474,16 @@ def _write_blocking_tests(node_ids, git_hash, census=CENSUS_FAIL_FAST_ONLY):
             sort_keys=True))
     except OSError as exc:
         log("Publish gate: could not record the blocking test(s) for the alarm: {}".format(exc))
+    # AND FOLD IT INTO THE STANDING-RED LEDGER (2026-09-05). The record above is LATEST-wins and
+    # bounded by a staleness age -- it can say what is red now and cannot say whether it is the
+    # SAME red as last cycle, which is the only fact from which "retrying will not clear this"
+    # follows. Both red paths converge here (the scoped gate via `_log_gate_failure_payload`, the
+    # pre-commit hook chain via `_record_commit_refusal_reds`), so this one line sees every
+    # refusal that named a test. Deliberately fed the UNCAPPED list: the file caps its citations
+    # at GATE_MAX_CITED_BLOCKING_TESTS and a subject compared after a cap would read as unchanged
+    # whenever the change fell past the twelfth node id. `note_refusal` never raises.
+    standing_red.note_refusal(node_ids, at=time.time(), git_hash=git_hash,
+                              total_red=len(node_ids), census=census)
 
 
 def _clear_blocking_tests():
@@ -3539,73 +3548,13 @@ def _record_commit_refusal_reds(stdout, stderr, git_hash="unknown"):
                 "No gate banner this classifier knows was in the output either, so the refusal "
                 "is UNNAMEABLE from here -- read the hook output itself, and do not read an "
                 "earlier cycle's blocking list as this cycle's cause."))
-        # A refusal that named no test is STILL a refusal, and the ledger's denominator is
-        # refusals. Folding nothing here is the point: a non-test gate has no test subject and
-        # inventing one for it is the 2026-09-02 defect where five GREEN tests were published as
-        # the blockers of an orphan-ratchet refusal.
-        _note_standing_red_refusal([], git_hash)
         return []
     log("Publish commit REFUSED by the hook chain -- blocking test(s): {}".format(
         "; ".join(node_ids[:GATE_MAX_CITED_BLOCKING_TESTS])))
     _write_blocking_tests(node_ids, git_hash, census=CENSUS_HOOK_CHAIN)
-    # THE SNAPSHOT CANNOT HOLD AN AGE, and the age is the whole finding (988270c2e, e0cc653c9).
-    # `_write_blocking_tests` above is overwritten every cycle and deleted on green, so a red that
-    # has refused twenty-four consecutive cycles reads, at every reader in this system, exactly
-    # like one that broke a minute ago -- and nothing escalates, so the publisher retries into it
-    # on a rhythm that by measurement cannot clear it. This is the same node ids, folded into a
-    # store that remembers.
-    _note_standing_red_refusal(node_ids, git_hash)
     return node_ids
 
 
-# ── THE AGE THE SNAPSHOT THREW AWAY ───────────────────────────────────────────────────────────
-#
-# Both of these are here rather than at their call sites for the reason R10 gives: the refusal
-# reaches the ledger from `_record_commit_refusal_reds`, which is the ONE function that holds the
-# hook chain's node ids, so a third refusal path added later inherits the fold for free.
-#
-# THEY MUST STAY SYMMETRIC. Every commit path that folds a refusal in must also record its pass,
-# or the ledger becomes a ratchet that only ever accumulates -- which is the failure mode that
-# would make it worse than the snapshot it replaces, because a register nobody can empty is a
-# register nobody reads.
-def _note_standing_red_refusal(node_ids, git_hash="unknown"):
-    """Fold this refusal into the standing-red ledger. Never raises, never blocks the publisher."""
-    try:
-        from background import publish_standing_red
-        standing = publish_standing_red.note_refusal(node_ids, git_hash)
-    except Exception as exc:  # noqa: BLE001 -- a diagnostic must never red the path it observes
-        log("Standing-red ledger: could not fold this refusal ({}: {}).".format(
-            type(exc).__name__, exc))
-        return []
-    if standing:
-        log("Publish STANDING RED -- {} test(s) have now refused the publisher {}+ cycles with no "
-            "landing between: {}. Retrying will not clear these; they are drawn as work in "
-            "docs/staging/reference/{}.".format(
-                len(standing), publish_standing_red.STANDING_AFTER_CYCLES,
-                "; ".join(standing[:GATE_MAX_CITED_BLOCKING_TESTS]),
-                publish_standing_red.REGISTER_NAME))
-    return standing
-
-
-def _record_commit_hook_pass(git_hash="unknown"):
-    """The hook chain PASSED, so discharge the standing-red ledger. Never raises.
-
-    A commit that returned 0 ran the same chain over the same tree, so nothing it did not stop can
-    still be stopping it. This is the ledger's only exit and it is one act -- absence from a later
-    refusal discharges nothing, because the chain is fail-fast."""
-    try:
-        from background import publish_standing_red
-        cleared = publish_standing_red.note_landing(git_hash)
-    except Exception as exc:  # noqa: BLE001 -- as above
-        log("Standing-red ledger: could not record the hook chain's pass ({}: {}).".format(
-            type(exc).__name__, exc))
-        return 0
-    if cleared:
-        log("Standing-red ledger DISCHARGED: the hook chain passed, clearing {} tracked "
-            "test(s).".format(cleared))
-    return cleared
-
-
 def last_blocking_tests(now=None, path=None):
     """(node_ids, git_hash) from the last red gate, or ([], None) if not knowably recent.
 
@@ -3708,54 +3657,29 @@ def _cohort_coverage_gate_permits_publish():
 
 
 def _trigger_frozen_baseline_refresh_out_of_band(git_hash="unknown"):
-    """Launch the weekly frozen-policy baseline refresh out of band when (and only
-    when) it is stale -- never block the publish path.
-
-    THIS SPAWN WAS A LIVE INSTANCE OF THE CGROUP DEATH (2026-09-08). It read
-    `start_new_session=True ... so it outlives this publish process`, and that
-    claim is the one three launches of one measurement refuted: every user unit
-    here is KillMode=control-group, `setsid` changes the session and the process
-    group, and a cgroup is neither. A multi-minute decade replay spawned from a
-    publish cycle died with the publisher's teardown -- silently, because both
-    streams went to DEVNULL, so a death and a success left the identical trace.
-
-    `background.launch_long_job` is the one launcher: a transient user unit the
-    publisher's teardown cannot reach, both streams appended to one file, and a
-    liveness record the deadman re-asks. NEVER RAISES INTO THE PUBLISH PATH -- a
-    refusal is logged and publishing continues on the existing baseline, which is
-    what "never blocks" has always meant here.
-
-    THE UNIT NAME NOW DOES THE DE-DUPLICATION THE LOCK WAS DOING ALONE. The
-    refresh still holds its own non-blocking single-writer lock, so nothing here
-    depends on the launcher for correctness; but a second launch while the first
-    is alive is now refused by systemd, by name, before a process is spawned at
-    all -- rather than spawned, only to exit on the lock's absence."""
+    """Spawn the weekly frozen-policy baseline refresh as a DETACHED background
+    process when (and only when) it is stale -- never block the publish path.
+
+    The refresh itself (tools.run_frozen_baseline.generate) holds a non-blocking
+    single-writer lock, so spawning it every cycle a stale baseline is seen
+    cannot stack overlapping multi-minute decade replays: the second and later
+    spawns take the lock's absence and exit at once. Detached via
+    start_new_session so it outlives this publish process; its output is
+    discarded (it writes site/state/frozen_policy_baseline.json directly)."""
     sys.path.insert(0, str(PROJECT_DIR))
     from tools.run_frozen_baseline import should_refresh_baseline
     if not should_refresh_baseline():
         return
-    from background import launch_long_job
-    artefact = str(PROJECT_DIR / "site" / "state" / "frozen_policy_baseline.json")
-    # The launcher narrates to stdout by default; this publish process's stdout is not a log
-    # anyone reads, so it is captured and re-emitted through `log()` -- the whole point of the
-    # change is that a launch stops being invisible.
-    narration = io.StringIO()
-    try:
-        entry = launch_long_job.launch(
-            "frozen-policy-baseline-refresh",
-            [sys.executable, "-m", "tools.run_frozen_baseline", "--if-stale"],
-            artefact=artefact, workdir=str(PROJECT_DIR),
-            description="weekly frozen-policy baseline refresh (out of band from a publish cycle)",
-            out=narration)
-    except Exception as exc:  # noqa: BLE001 -- publishing NEVER blocks on this, see the docstring
-        log("Frozen-policy baseline stale -> refresh NOT launched: {}. Publishing continues "
-            "with the existing baseline.".format(exc))
-        return
-    for line in narration.getvalue().splitlines():
-        log("  frozen-baseline launch: {}".format(line))
-    log("Frozen-policy baseline stale -> refresh launched OUT OF BAND as unit {} (log {}); "
-        "publishing continues with the existing baseline (never blocks).".format(
-            entry["unit"], entry["log"]))
+    proc = subprocess.Popen(
+        [sys.executable, "-m", "tools.run_frozen_baseline", "--if-stale"],
+        cwd=str(PROJECT_DIR),
+        stdout=subprocess.DEVNULL,
+        stderr=subprocess.DEVNULL,
+        stdin=subprocess.DEVNULL,
+        start_new_session=True,
+    )
+    log("Frozen-policy baseline stale -> refresh spawned OUT OF BAND (PID {}); "
+        "publishing continues with the existing baseline (never blocks).".format(proc.pid))
 
 
 def generate_dashboard_json(json_path, git_hash="unknown"):
@@ -4231,6 +4155,11 @@ def generate_dashboard_json(json_path, git_hash="unknown"):
         # AFTER gen_company, not beside it: regulatory.json reads obligation_count, overall_rag
         # and status_counts OUT of site/data/company.json, so running it first would stamp the
         # PREVIOUS cycle's compliance state with this cycle's clock.
+        #
+        # RESTORED 2026-09-06 after an in-place edit from a base that predated it deleted the
+        # block: this call is the ONLY edge that reaches `tools.generate_regulatory_data`, so
+        # losing it made that module and `company.regulatory.fuel_mix_disclosure` orphans in the
+        # working tree and the orphan ratchet then refused EVERY commit, publisher included.
         from tools.generate_regulatory_data import main as gen_regulatory
         gen_regulatory()
         log("Generated site/data/regulatory.json (Journey door, Regulatory tab)")
@@ -5520,12 +5449,6 @@ def git_commit_push(git_hash, net_margin, outcome=None):
                                       "this same commit"))
             return _outcome(NOTHING_TO_COMMIT, False)
 
-        # THE COMMIT LANDED, so the hook chain passed over this tree. Symmetric with the fold in
-        # `_record_commit_refusal_reds` above -- see `_record_commit_hook_pass` for why the two
-        # must stay paired. Placed BEFORE the push throttle on purpose: the discharge is evidence
-        # about the pre-commit CHAIN, and whether the push is deferred says nothing about it.
-        _record_commit_hook_pass(git_hash)
-
         if not _push_due():
             log("Committed locally, push deferred (throttled to every {}min)".format(
                 PUSH_THROTTLE_SECONDS // 60
@@ -6207,10 +6130,6 @@ def _commit_and_push_paths(paths, msg, *, label, git_hash="unknown"):
                 "the pre-commit hook chain refused the commit (rc={}): {}".format(
                     result.returncode, _tail), git_hash)
         return False
-    # Paired with the refusal fold this same function does through `_record_commit_refusal_reds`
-    # ten lines up. The liveness commit runs the SAME hook chain, so it must discharge the ledger
-    # it can add to -- a path that only ever adds turns the register into a ratchet.
-    _record_commit_hook_pass(git_hash)
     push = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=str(PROJECT_DIR),
                           timeout=60, stderr=subprocess.PIPE, text=True)
     local_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
@@ -7431,6 +7350,17 @@ def record_publish_gate_success(*, now=None, markers_pending=None):
             except Exception as exc:  # noqa: BLE001 - diagnostics may never gate a recovery
                 log("Suspect-list scoring skipped (the wedge still clears): {}".format(exc))
         stamp = float(now) if now is not None else time.time()
+        # THE ONLY WHOLE-POPULATION GREEN THE PUBLISH PATH EVER GETS (2026-09-05). A clean publish
+        # means nothing refused, so no red is standing — and this is the ONE place that fact is
+        # known. It is deliberately NOT wired to `_clear_blocking_tests`, which fires whenever the
+        # publisher's own SCOPED gate is green: that happens every cycle whose red lives in the
+        # pre-commit HOOK CHAIN instead, which is the population the 67.8h of measured RED TEST
+        # outage was measured over. Clearing there would have zeroed the ledger once a cycle and
+        # recorded a standing red exactly never. What protects the wedge clear from this call is
+        # that `note_clean_publish` swallows its own faults, NOT its position — the lesson the
+        # suspect-list scoring above had to learn the hard way, where an un-wrapped diagnostic
+        # write one line before the clear abandoned the whole function and left the gate wedged.
+        standing_red.note_clean_publish(at=stamp)
         prev_clean = prev.get("episode_clean_publishes")
         # On a CLOSE this is proposed as 0 and the guard lets it reset with the rest of the
         # episode. On a preserved episode it counts the publish that just happened, which is the
```

## tests/background/test_launch_liveness.py
```diff
diff --git a/tests/background/test_launch_liveness.py b/tests/background/test_launch_liveness.py
index 1523331ed..3ca2f1844 100644
--- a/tests/background/test_launch_liveness.py
+++ b/tests/background/test_launch_liveness.py
@@ -75,7 +75,7 @@ def test_a_broken_probe_is_not_a_death(tmp_path):
     assert ll.reask(entry, lambda unit: None)["verdict"] == ll.UNREADABLE
 
     ll.save([entry], tmp_path / "records.json")
-    stale, lines, _ = ll.check(tmp_path / "records.json", probe=lambda unit: None)
+    stale, lines = ll.check(tmp_path / "records.json", probe=lambda unit: None)
     assert stale == 0, "an unreadable probe settled a live claim"
     assert json.loads((tmp_path / "records.json").read_text())[0]["claim"] == ll.LIVE
     assert any("not evidence the job ended" in line for line in lines)
@@ -88,8 +88,8 @@ def test_the_check_names_the_documents_that_are_now_wrong(tmp_path):
     store = tmp_path / "records.json"
     ll.save([_entry(tmp_path, asserted_live_by=["docs/prereg.md", "docs/correction.md"])], store)
 
-    stale, lines, _ = ll.check(store, probe=_probe(ActiveState="inactive", Result="success",
-                                                   ExecMainStatus="0"))
+    stale, lines = ll.check(store, probe=_probe(ActiveState="inactive", Result="success",
+                                                ExecMainStatus="0"))
     assert stale == 1
     joined = "\n".join(lines)
     for doc in ("docs/prereg.md", "docs/correction.md"):
@@ -110,134 +110,11 @@ def test_a_settled_record_never_returns_to_live(tmp_path):
     store = tmp_path / "records.json"
     ll.save([_entry(tmp_path, claim=ll.DIED, settled_at="2026-09-08T01:00:00Z",
                     evidence="Result=oom-kill")], store)
-    stale, lines, _ = ll.check(store, probe=_probe(ActiveState="active"))
+    stale, lines = ll.check(store, probe=_probe(ActiveState="active"))
     assert (stale, lines) == (0, []), "a settled record was re-asked and could have been re-opened"
     assert json.loads(store.read_text())[0]["claim"] == ll.DIED
 
 
-def test_a_retrofitted_record_keeps_the_real_launch_time(tmp_path, monkeypatch):
-    """A job recorded LATE must not be stamped with the moment it was recorded.
-
-    THE DEFECT THIS CAUGHT, on the module's first real use: the live floor leg was launched at
-    01:39:56Z and recorded three hours later, because the module was written after the launch. With
-    `launched_at` defaulting to now, the record said the run had been going for zero minutes --
-    and how long a claim has stood is precisely what a later reader judges it by. A record whose
-    age is the age of the RECORD rather than of the RUN understates every stale claim it holds.
-
-    THROUGH `main`, NOT `record`. The first draft of this control called `record(launched_at=...)`
-    directly and stayed green when the CLI was mutated to pass `None` -- it graded the function and
-    was blind to the wiring, which is the only part that changed. The argv is the subject.
-    """
-    store = tmp_path / "records.json"
-    monkeypatch.setattr(ll, "RECORDS_PATH", store)
-
-    assert ll.main(["--record", "floor", "--unit", "floor.service",
-                    "--artefact", str(tmp_path / "a.json"),
-                    "--launched-at", "2026-09-08T01:39:56Z"]) == 0
-    assert json.loads(store.read_text())[0]["launched_at"] == "2026-09-08T01:39:56Z"
-
-    # And the default still holds for a genuinely fresh launch -- the flag must not become the
-    # only way to get a launch time, or every caller that omits it writes None.
-    monkeypatch.setattr(ll, "_now", lambda: "2026-09-08T04:40:00Z")
-    assert ll.main(["--record", "fresh", "--unit", "fresh.service",
-                    "--artefact", str(tmp_path / "b.json")]) == 0
-    fresh = [r for r in json.loads(store.read_text()) if r["job"] == "fresh"][0]
-    assert fresh["launched_at"] == "2026-09-08T04:40:00Z"
-
-
-def _deadman(monkeypatch):
-    """The deadman check with every live-effect path stubbed. Never touches the real log, the real
-    ntfy route or the real record store."""
-    from background import deadmans_switch as dms
-    sent, cleared = [], []
-    monkeypatch.setattr(dms, "notify", lambda msg, **kw: sent.append((msg, kw)))
-    monkeypatch.setattr(dms, "log", lambda msg, path=None: None)
-    monkeypatch.setattr(dms, "clear_transition", lambda key: cleared.append(key))
-    return dms, sent, cleared
-
-
-def test_the_deadman_pages_the_documents_a_stale_claim_makes_wrong(monkeypatch):
-    """THE POINT OF THE WHOLE MODULE: the contradiction has to ARRIVE, not wait to be asked for.
-
-    A `--check` that only runs when someone types it is still a person checking, one indirection
-    along -- and every one of the four launches was caught by a person going to look. This is the
-    leg that makes the arrival automatic, so it is the leg worth a control.
-    """
-    dms, sent, _ = _deadman(monkeypatch)
-    dead = {"job": "a-long-run", "claim": ll.DIED, "asserted_live_by": ["docs/prereg.md"]}
-    monkeypatch.setattr(ll, "check", lambda: (1, ["a-long-run: DIED -- Result=oom-kill"], [dead]))
-    dms._check_launch_liveness()
-
-    assert len(sent) == 1, "a stale liveness claim did not page"
-    msg, kw = sent[0]
-    assert "docs/prereg.md" in msg, (
-        "the page named no document, so the reader inherits the search that was the whole cost")
-    assert kw.get("kind") == "real_alarm"
-
-
-def test_a_run_that_SUCCEEDED_is_batched_and_never_paged(monkeypatch):
-    """A DEATH AND A COMPLETION ARE NOT THE SAME EVENT, and the first draft of the wiring paged an
-    identical `real_alarm` for both.
-
-    Both contradict a document reading "in flight", so both are stale -- but one is an incident and
-    the other is the good news the run was launched for. Paging him for success is how this
-    project's one inbound channel has buried its own signal before, so the split is a control and
-    not a preference. Caught before it ever fired: the floor leg was minutes from finishing
-    successfully when this was written.
-    """
-    dms, sent, cleared = _deadman(monkeypatch)
-    done = {"job": "floor", "claim": ll.FINISHED, "asserted_live_by": ["docs/result.md"]}
-    monkeypatch.setattr(ll, "check", lambda: (1, ["floor: FINISHED -- rc=0"], [done]))
-    dms._check_launch_liveness()
-
-    assert len(sent) == 1, "a completed run said nothing at all; the document stays wrong silently"
-    msg, kw = sent[0]
-    assert kw.get("kind") != "real_alarm", (
-        "a run that SUCCEEDED paged the director as an alarm: " + msg)
-    assert kw.get("kind") == "work_done" and kw.get("topic_class") == "routine_landing", (
-        "a completion must go to the batched digest, not the instant route: " + repr(kw))
-    assert "docs/result.md" in msg, "the batched note still has to name what is now wrong"
-    assert cleared, "no death stood, so the alarm key must be cleared rather than left armed"
-
-
-def test_a_death_and_a_completion_in_one_pass_both_get_their_own_route(monkeypatch):
-    """The partition asserted over the whole set, not one leg at a time. A branch that handled only
-    whichever came first would pass both single-verdict tests above."""
-    dms, sent, cleared = _deadman(monkeypatch)
-    monkeypatch.setattr(ll, "check", lambda: (2, ["two"], [
-        {"job": "dead-one", "claim": ll.DIED, "asserted_live_by": ["docs/a.md"]},
-        {"job": "done-one", "claim": ll.FINISHED, "asserted_live_by": ["docs/b.md"]}]))
-    dms._check_launch_liveness()
-
-    kinds = {kw.get("kind") for _, kw in sent}
-    assert kinds == {"real_alarm", "work_done"}, (
-        "one verdict swallowed the other; got " + repr(kinds))
-    assert not cleared, "a real death stood, and its alarm key was cleared anyway"
-
-
-def test_the_deadman_is_silent_when_nothing_is_stale_and_when_it_could_not_look(monkeypatch):
-    """Two silences with different meanings, and neither may page.
-
-    A run that is simply still going is the ordinary state -- paging on it would make this the
-    third channel that buries its own signal. A check that RAISED did not look, and "we did not
-    look" must not clear the alarm either: that would report an answer we never had.
-    """
-    dms, sent, cleared = _deadman(monkeypatch)
-    monkeypatch.setattr(ll, "check", lambda: (0, ["floor: RUNNING -- ActiveState=active"], []))
-    dms._check_launch_liveness()
-    assert sent == [] and cleared, "a live run paged, or the settled alarm was never cleared"
-
-    def _boom():
-        raise OSError("systemctl is not on this box")
-    monkeypatch.setattr(ll, "check", _boom)
-    cleared.clear()
-    dms._check_launch_liveness()
-    assert sent == [], "a check that could not run reported a death"
-    assert cleared == [], (
-        "a check that could not run CLEARED the alarm -- that is 'we did not look' rendered as "
-        "'nothing is wrong', which is the fail-open this module exists to refuse")
-
-
 @pytest.mark.parametrize("state", ["active", "activating", "deactivating", "reloading"])
 def test_a_unit_that_has_not_finished_is_never_settled(tmp_path, state):
     """`deactivating` is the one worth naming: a job inside its own teardown has produced no exit
```

## background/launch_liveness.py
```diff
diff --git a/background/launch_liveness.py b/background/launch_liveness.py
index b1c99b4e8..9cb0036e4 100644
--- a/background/launch_liveness.py
+++ b/background/launch_liveness.py
@@ -182,18 +182,9 @@ def record(job: str, unit: str, artefact: str, *, log: str | None = None,
     return entry
 
 
-def check(path: Path | None = None, probe=systemd_probe) -> tuple[int, list, list]:
+def check(path: Path | None = None, probe=systemd_probe) -> tuple[int, list]:
     """Re-ask every record still claiming `live`; settle the ones that are not, and say so.
 
-    RETURNS `(stale, lines, settled)`. `settled` carries the records this call moved, each with the
-    verdict that moved it, because A DEATH AND A COMPLETION ARE NOT THE SAME EVENT and only the
-    caller can know what to do about that. Both contradict a document that says "in flight", which
-    is why both count as stale; but one is an incident and the other is the good news the run was
-    launched for. Handing back only a COUNT forced the caller to choose one severity for both, and
-    the first version of the deadman wiring duly paged a `real_alarm` for a job that had succeeded
-    -- crying wolf on the director's own channel, which is how this project has buried its signal
-    before. The split has to exist here, at the point where the verdict is known.
-
     THE CONTRADICTION IS THE OUTPUT, and the writeback is what stops it being a nag. A record that
     the re-ask settles keeps the verdict and the evidence, so the next reader of the documents in
     `asserted_live_by` is contradicted by a file rather than by a person who thought to check a
@@ -204,7 +195,7 @@ def check(path: Path | None = None, probe=systemd_probe) -> tuple[int, list, lis
     the job: an UNREADABLE probe settles nothing, and neither does UNKNOWN, because "we could not
     tell" is not permission to overwrite what the launch said.
     """
-    records, lines, settled = load(path), [], []
+    records, lines, stale = load(path), [], 0
     for entry in records:
         if entry.get("claim") != LIVE:
             continue
@@ -217,15 +208,15 @@ def check(path: Path | None = None, probe=systemd_probe) -> tuple[int, list, lis
             lines.append(
                 f"  (claim left at `live`: {verdict} is not evidence the job ended)")
             continue
+        stale += 1
         entry["claim"] = FINISHED if verdict == FINISHED else DIED
         entry["settled_at"] = _now()
         entry["evidence"] = answer["why"]
-        settled.append(entry)
         for doc in entry.get("asserted_live_by") or []:
             lines.append(f"  CONTRADICTS {doc} -- it says this run is in flight; it is not")
-    if settled:
+    if stale:
         save(records, path)
-    return len(settled), lines, settled
+    return stale, lines
 
 
 def main(argv: list | None = None) -> int:
@@ -239,13 +230,6 @@ def main(argv: list | None = None) -> int:
     parser.add_argument("--rc-path")
     parser.add_argument("--asserted-live-by", action="append", default=[],
                         help="a document that states this run is in flight (repeatable)")
-    # A job is often recorded LONG after it was launched -- the first real use of this module was
-    # a floor leg recorded three hours in, because the module was written after the launch. Without
-    # this flag `launched_at` silently becomes the moment someone got round to recording, which is
-    # the one field a later reader uses to judge how long the claim has stood. Defaulting to now is
-    # right for a fresh launch and wrong for every retrofit, so the retrofit has to be able to say.
-    parser.add_argument("--launched-at", metavar="ISO8601",
-                        help="when the job ACTUALLY started, if that is not now")
     args = parser.parse_args(argv)
 
     if args.record:
@@ -253,12 +237,11 @@ def main(argv: list | None = None) -> int:
             print("--record needs --unit and --artefact: a record with neither cannot be re-asked")
             return 2
         entry = record(args.record, args.unit, args.artefact, log=args.log,
-                       rc_path=args.rc_path, asserted_live_by=args.asserted_live_by,
-                       launched_at=args.launched_at)
+                       rc_path=args.rc_path, asserted_live_by=args.asserted_live_by)
         print(f"recorded {entry['job']} -> unit {entry['unit']}, claim {entry['claim']}")
         return 0
 
-    stale, lines, _ = check()
+    stale, lines = check()
     for line in lines:
         print(line)
     if stale:
```

## tools/couple_value_based_pricing.py
```diff
diff --git a/tools/couple_value_based_pricing.py b/tools/couple_value_based_pricing.py
index 0b90ff512..b2da98d2b 100644
--- a/tools/couple_value_based_pricing.py
+++ b/tools/couple_value_based_pricing.py
@@ -665,19 +665,6 @@ def compare(run: dict, book: dict, as_of_year: int = AS_OF_YEAR) -> dict:
         bills = float(leg.get("bill_count") or 0.0)
         years = max(1.0, bills / BILLS_PER_YEAR)
         eac = total_kwh / years
-        legacy_rate = (leg.get("avg_commodity_rate_gbp_per_mwh")
-                       or leg.get("avg_rate_gbp_per_mwh"))
-        if avg_rate <= 0.0 and legacy_rate:
-            # THE SURFACE PREDATES THE TWO-RATE PUBLICATION, and that is its own answer rather than
-            # a missing number (2026-08-31). A leg carrying `avg_rate_gbp_per_mwh` (the ambiguous
-            # old name) or only `avg_commodity_rate_gbp_per_mwh` was published before the generator
-            # started saying which rate is which. BOTH legacy shapes are recognised, because the
-            # first version of this branch checked only the newer one and the live artefact -- the
-            # one that actually exists -- carries the older. There is deliberately NO FALLBACK to the
-            # commodity leg: reading it as the price is the exact defect this change fixes, and a
-            # silent fallback would restore it while looking like resilience.
-            skipped["the published surface carries no effective rate yet (regenerate it)"] += 1
-            continue
         if eac <= 0.0 or avg_rate <= 0.0:
             # NAMED, not dropped. An account the company cannot price is a fact about its own
             # records, and a comparison that silently covers 200 of 263 accounts is a different
```

