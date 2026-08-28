**Severity:** LATENT · **Lane:** H_harness

# The publisher's "order-dependent blocking test" cannot be order-dependent — there is no ordering plugin. Its fixture copies 192MB of the live working tree, 170MB of which is four logs a daemon is appending to while the copy runs

The publish wedge of 2026-08-28 was handed on with a diagnosis: one of the five blocking tests in
`tests/background/test_derived_artefact_register.py` is **order-dependent**, `TestRepair::
test_repair_restores_a_corrupted_rendering_and_reports_convergence` failed "under the default random
ordering" in a 302s full-file run and passed alone in 33s with `-p no:randomly`, and it "shares state
across the `head_checkout` / `head_checkout_running_tree_code` fixtures". That diagnosis names a
mechanism this repository does not have, and the real shared state is somewhere else. Naming the
wrong mechanism is a plausible reason the wedge has been declared fixed three times and come back
three times (R3).

## Observed-with-evidence

**1. There is no random ordering. `pytest-randomly` is not installed.**

```
$ python3 -m pytest --version        → pytest 9.0.3
$ python3 -c "import pytest_randomly" → ModuleNotFoundError: No module named 'pytest_randomly'
```

No `addopts` in `pytest.ini`, `setup.cfg`, `pyproject.toml` or `tox.ini` (none of those files carries
one). Collection order is deterministic file order, every run. `-p no:randomly` is therefore a
**no-op flag** — it disables a plugin that is not there. So "full file fails / this test alone with
`-p no:randomly` passes" is not a contrast between two orderings. It is a contrast between two
**populations** (13 tests vs 1) and two **wall-clocks** (302s vs 33s), and only the second contrast
has a mechanism behind it.

**2. The full file is green right now, in the order the gate runs it.**

```
$ python3 -m pytest tests/background/test_derived_artefact_register.py -p no:cacheprovider -q
............. [100%]
13 passed in 173.64s (0:02:53)     rc=0
```

Run against the current dirty shared tree, no `-k`, no deselection, no ordering flags. The file has
13 tests, not the 9 the handoff's "1 failed, 8 passed" implies — so that run was already a different
population from the gate's.

**3. The shared state is the live working tree, and it is 192.5 MB of which 169.7 MB moves.**

`head_checkout_running_tree_code` composes HEAD with the tree under review by copying every path in
`git diff --name-only HEAD` ∪ `git ls-files --others --exclude-standard`. Measured now:

```
153 files copied per fixture use, 192.5 MB total
  107.0 MB  docs/observability/supervisor-log.md
   31.0 MB  docs/reports/run_output_latest.json
   21.5 MB  docs/observability/sim-runner-log.md
   10.2 MB  docs/observability/size_ratchet_warnings.jsonl
```

`supervisor-log.md` had an mtime **9 seconds old** when that census was taken. These four are
append-only artefacts that background daemons rewrite continuously; none of them is a derived
artefact, a source of one, or anything the register checks. Four tests use the fixture, so a
full-file run copies ~770 MB out of a tree that is being written to throughout, on top of four
~130 MB `git archive` extractions, into a 12 GB tmpfs the file's own docstring records finding at
100% full. That is the shared state: **not one test leaving something behind for the next, but every
test taking its subject from a surface other processes are mutating between and during the copies.**
Two tests in one session do not receive the same tree, and `shutil.copyfile` of a 107 MB file being
appended to is a torn read by construction.

**4. `converged` is a property of all three artefacts, so the assertion misattributes blame.**

`repair_from` returns `converged = not still_stale` where `still_stale` is computed over the **whole**
`REGISTER` (`background/derived_artefact_register.py:229-233`).
`test_repair_restores_a_corrupted_rendering_and_reports_convergence` corrupts `REGISTER[0]`
(`blocked_atom_visibility`) and then asserts `res["converged"]`. A source violation in `REGISTER[1]`
or `REGISTER[2]` — exactly what `PULL_FORWARD_PROPOSALS.md`'s `block_reason_history` was until
`0c3bfada6` — fails this test with a message that reads as *the repair of blocked_atom_visibility did
not converge*. The failing test names the wrong artefact, which is how a whole-tree condition gets
re-diagnosed as a defect in one oracle.

## Inferred

I could not reproduce the reported failure and I am not claiming which of (3) and (4) produced it;
both were live at the time. (4) is the better fit for a single clean failure at 302s — the map's
`block_reason_history` violation was still unrepaired in that run unless the seat had already edited
`docs/design/maturity_map_closed.yaml`, and that file was **not** among the four paths the handoff
listed in its index. Under (4) the test would also have failed alone, which the handoff says it did
not, so (3) or a race between them remains open. What is settled is that neither is ordering.

## Class registration

Belongs to `publish_gate_and_wedge`. Declared rather than left to the title regex: this document's
subject is the *account* of a wedge, so its heading names the blocking test and the fixture and
carries neither `publish gate` nor `wedge`, and the filename carries neither either. The keyword net
would route it nowhere, which is the hole the declaration route exists for.

## The class

This is the publish-gate wedge class arriving as a *diagnosis* defect rather than a control defect.
The control was fine; the account of why it was red named a plugin that is absent, and the repair
that followed from that account (isolate the fixtures per test) would have changed nothing, because
the fixtures are already function-scoped on `tmp_path`.

## What would actually close it

1. **Stop copying what the register cannot read.** The fixture needs the tree under review, not the
   daemon logs in it. Excluding `docs/observability/**` and `docs/reports/run_output_latest.json`
   removes 88% of the bytes and every concurrently-written file, and cannot weaken the control:
   `discover()` scans `background/`, `saas/`, `tools/` for modules taking `--write`, and no oracle
   reads a log. Do it as an **explicit named exclusion with a stated reason**, not a directory
   prefix rule — an exclusion scoped by directory hides everything that directory mixes.
2. **Narrow the assertion to its own subject.** Assert `art.rendered not in res["still_stale"]`
   first, so the corrupted artefact is named, and keep the global `converged` assertion with a
   message that reports *which* artefacts are still stale. No teeth are lost — the repair must still
   restore what the test broke — and a whole-tree violation stops presenting as a defect in
   `REGISTER[0]`.
3. **Mutation-prove both** before landing, per R15: the test must still fail when the repair does not
   restore the corrupted rendering, and must still fail when a genuinely stale artefact is present.

Neither is done here. This is filed rather than fixed under SELF-INTERRUPT DISCIPLINE — the road is
open (live `publish_provenance.json` reads `verification_state: verified`, `paused_reason: null`,
`showing_run.git_commit e3ee53cc5`, a descendant of `28eaca4c9`), the file is green, and changing a
blocking control on the day the wedge cleared buys nothing that waiting for a deliberate,
mutation-proven pass does not.
