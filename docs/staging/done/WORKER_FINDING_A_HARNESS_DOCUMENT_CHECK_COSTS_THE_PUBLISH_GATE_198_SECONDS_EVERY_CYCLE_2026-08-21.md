# [WORKER-FINDING] A harness visibility-document check costs the publish gate 198 seconds on every cycle, by running the real BUILD draw 192 times (2026-08-21)

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-21, scheduled tick, diagnosing the 22-hour publishing outage. Found by reading
the in-flight gate's own process tree rather than its log — the child it was sitting in named
itself.
**Disposition:** QUEUED (SELF_INTERRUPT_DISCIPLINE — the machine was blocked on a different
cause, which is fixed and landed separately; this one is real, measured, and not blocking).
**Rank:** backlog, but it is the concrete instance under the director's 2026-08-21 question
*"worth checking whether the loop is self-feeding … if that's real, say so."* It is real.

## Observed, with evidence

The publish gate was live (pid 2175749, 2593s elapsed). Its only child:

```
2328063  136  R  /usr/bin/python3 -m background.blocked_atom_visibility --check
```

Timed standalone on the same box, `/usr/bin/time` around the same command:

```
rc=0
ELAPSED 198.28 s
```

The caller is `tests/background/test_blocked_atom_visibility.py::
test_the_committed_document_agrees_with_the_live_derivation`:

```python
rc = subprocess.run(
    [sys.executable, "-m", "background.blocked_atom_visibility", "--check"],
    cwd=REPO, capture_output=True, text=True,
)
```

No `timeout=`. That file is in `publish_scope.resolve_scope()`'s blocking set — confirmed
against the live resolution, `6 publish-path source(s) -> 200 blocking test file(s)`, and
`tests/background/test_blocked_atom_visibility.py` is one of the 200. It is also in the
write-time gate's 62-file set, so it is paid twice per cycle.

## Where the 198 seconds go, from the module's own docstring

`background/blocked_atom_visibility.py::build_report` says it plainly:

> `probe_draw` / `probe_clocks` exist because both probes are slow (the draw runs twice per
> parked atom, AO11 walks git history)

Measured against the live map: **316 atoms, 96 parked**. `park_exclusion_status` calls
`draw_offers` once per parked atom, then again on the unparked control for every atom that was
not drawn — so up to **192 invocations of `supervisor._maturity_map_draw_concurrent()`**, the
real BUILD draw, per `--check`. `clock_visible_ids` then walks git history for all 316 through
`tools.map_assertion_provenance.build_rows`.

Both probes are correct and neither is wasteful for what it is. The defect is not the probe. It
is that a **harness visibility document** is being reconciled inside the gate that decides
whether the *company's published figures* may go to the site, on the cadence of a sim run.

## Why this is the self-feeding loop, with the arithmetic

The director asked whether each wedge makes a finding, each finding a control, each control more
tests, and a slower gate more wedges. This is one full turn of it, dated:

- `background/blocked_atom_visibility.py` exists because parked atoms were invisible to the draw.
- Its `--check` mode exists so the committed document cannot drift from the derivation (R11).
- `test_the_committed_document_agrees_with_the_live_derivation` wires that into pytest.
- `resolve_scope()` pulls it into the publish gate through the static import graph — nobody chose
  to gate publishing on it; the import graph did.
- It now costs the gate 198s per run, and a slower gate is the substrate every publish wedge in
  `CLASS_PUBLISH_GATE_AND_WEDGE` grows on.

Nothing here was a mistake in isolation. That is the point: the loop does not need anyone to be
careless, only for the gate's membership to be derived and its cost to be watched by nobody.

## The unbuilt work, named rather than done

1. **The subject question the director actually asked** — *"what genuinely must run before a
   publish and what belongs somewhere else entirely, on its own cadence."* A document-freshness
   check on a harness artefact is the clearest possible instance of "somewhere else". It belongs
   on the daily self-note's cadence, not the publish path's.
2. **`resolve_scope()` needs a cost axis, not just a correctness axis.** It currently answers
   *"which tests could this publish break?"* and never *"what does asking cost?"* — so a 198s
   test and a 0.2s test enter the blocking set on identical terms. There is a record to derive it
   from (`publish_gate_duration.jsonl`) and no consumer that reads per-file cost.
3. **The missing `timeout=`** on the subprocess above is a smaller, separate defect: with no
   bound, a hung `--check` is indistinguishable from a slow one, and the gate's own timeout takes
   the blame. Fix it with (1), not before — a timeout on a test that should not be in the gate is
   the accretion OPERATIONAL_LAYER_DESIGN forbids.

## What this finding is NOT

It is not the cause of the 2026-08-20/21 outage, and it must not be recorded as such. That was
two things, both closed or named elsewhere: the gate's bound shipping 352s below its own measured
floor (fixed and landed, see `measured_gate_timeout_floor` in
`background/process_run_complete.py`), and two gate runs censored at 4500s while a second and
third pytest suite were live on the same box. 198s is real and repeating; it is not 3200s.
