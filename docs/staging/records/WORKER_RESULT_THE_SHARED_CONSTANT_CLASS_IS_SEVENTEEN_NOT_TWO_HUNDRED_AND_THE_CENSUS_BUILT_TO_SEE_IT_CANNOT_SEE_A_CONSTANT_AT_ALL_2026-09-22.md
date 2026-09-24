**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0

# The shared-constant class is 17, not 265 — and `shared_primitive_census`, the register built to notice re-duplication, structurally cannot see a constant at all

Lane 0 item `a-shared-canonical-constant-with-three-consumers-and-no-leg-that-reds-when-it-narrows`.
The item asked: census the shared canonical constants in `background/` with 2+ consumers — the
`_ITEM_PROSE_KEYS` shape — and for each ask whether any leg in the tree reds when it is changed.

## The premise is NOT spent

The draw reported all three cited commits (`0b1898452`, `14dc33969`, `c9bb7bd34`) as ancestors of
`origin/main` and all three named paths as `already landed`. Both readings are correct and neither
touches the ask. Those commits are the item's **context** — the coverage already bought for
`_ITEM_PROSE_KEYS` and `premise_note` — not its deliverable. The deliverable is the sibling census,
which had not been run. The item is live; nothing was done twice.

The base was 5 commits behind `origin/main`, so the door's own `[stale-copy]` caveat applied.
Advanced first (`166021f0c`); every number below is measured on a tree level with the trunk.

## The population is 17, and the first two counts are both wrong

| reading | count | why it is the wrong number |
|---|---|---|
| module-level literal constants in `background/` | 265 | most are module-private; sharing is the question |
| …whose name appears in any other non-test file | 62 | **a name match is not a consumer** — 24 of these are independent *re-definitions* of the same name |
| …genuinely reachable: `from background.X import NAME` or `X.NAME` | **17** | this is the class the item asked about |

Of the 17, six are named by a test somewhere; **11 are named by no test at all**. Naming is only a
proxy — a test can reach a constant behaviourally without spelling it — which is why the item asked
for mutation rather than for a grep, and why the mutation verdicts below are the real answer.

## The bigger half of what the name-match found is a different defect, and most of it is noise

Widening the duplicate-name scan to the whole tree gives 372 constant names defined at module level
in 2+ non-test files, 132 of them with disagreeing values. **That number should not be published as
a defect count and is not one.** `LEDGER_PATH` (22), `STREAM_NAME` (10), `TWIN_ATOM_ID` (17),
`WORLD_ATOM_ID` (16), `POLL_INTERVAL_SECONDS` (9) and `OUTPUT_PATH` (11) are per-module by
construction: each module legitimately owns its own. Counting them as duplication measures the
naming convention, not the repo.

The signal is the subset where **the constant's value is a claim about the world**, so two
definitions disagreeing means the company believes two things at once:

**`CRISIS_YEARS` — 17 definitions across `background/`, `company/`, `saas/`, `simulation/`, `tools/`.**
Fifteen say 2021–2022. One does not:

    background/fidelity_emitter.py:145          CRISIS_YEARS  = ("2021", "2022")   # cites EPOCH2 evidence doc
    company/compliance/crisis_bad_debt_validator.py:70  CRISIS_YEARS  = (2021, 2022)       # cites docstring provenance
    tools/population_anchor.py:108              _CRISIS_YEARS = {2021, 2022, 2023}  # no comment, no source

The types also split — `str` against `int`, `tuple` against `set` — so no leg could compare two of
them even if one tried. This is the VAT shape `CLAUDE.md` names as the seat's own class: one fact
about the 2016–2025 record, seventeen implementations, and nothing anywhere able to notice.

**`WINTER_MONTHS` / `_WINTER_MONTHS` — 5 definitions, 3 distinct values.** `tariff_engine` and
`priority_services_register` mean Oct–Mar; `weather_demand_triad` and the `sim/` weather chains mean
Dec–Feb; `tools/weather_cell_drivers` means `(11, 0, 1)`, zero-based indices into a January-first
axis. These are probably two real concepts — heating season and meteorological winter — sharing one
name, which is the "before measuring a thing, say what it is" failure rather than a divergence.

## The register that exists for exactly this cannot see it

`background/shared_primitive_census.py` is the standing "should this have been shared?" look, wired
into `gap_register_scan._REGISTERS` as row #9. It cannot return any constant in this finding, for
two independent structural reasons:

- its clone detector skips every AST node that is not a function — `if not isinstance(node,
  (ast.FunctionDef, ast.AsyncFunctionDef)): continue` — so a module-level assignment is never a
  candidate, at any threshold;
- `DEFAULT_NODE_THRESHOLD = 45` would exclude a one-line assignment even if it were;
- and `SCAN_ROOTS = ("company", "sim", "simulation", "saas", "background")` excludes `tools/`, which
  is where the one divergent `CRISIS_YEARS` lives.

So the census reads OPEN/closed on function clones while 17 definitions of a domain fact sit outside
its vocabulary. This is the silently-scoped-guard shape: the guard exists, so the gap reads covered.

## Two corrections to my own instrument, recorded beside the claim

**The first sweep measured nothing and said so in the colour of a red.** It passed `--timeout=120`
to a pytest with no `pytest-timeout` installed; pytest exits `4` (usage error) having collected
nothing. Ten of the 17 constants were graded `BASELINE ALREADY RED (rc=4) -- cannot attribute`. That
verdict is indistinguishable, in the log, from a tree with ten real reds. A setup error wearing a
red's colour is the same class this finding is about.

**Return-code equality was then the wrong comparator.** With the flag removed the first target ran
`1 failed, 623 passed` — a pre-existing red — and rc-comparison again refused to attribute. The
correct measurement is the **set of new failing test ids** against the unmutated baseline, which
tolerates reds the mutation did not cause. The sweep was relaunched on that comparator and carries
positive controls (constants already known to be covered) deliberately: a harness that reports
"nothing reds" for every subject is indistinguishable from one that cannot red at all.

## What is established and what is not

Established: the population is 17, not 62 and not 265; 11 of the 17 are named by no test; the
existing census structurally cannot see any of them; `CRISIS_YEARS` has 17 definitions of which one
disagrees on the years and several on the type.

**Not established, and not to be guessed:** whether `{2021, 2022, 2023}` in `population_anchor.py`
is a defect or a deliberate choice. It sits in the arrears-and-complaints benchmark block, and
arrears genuinely lagged the price shock into 2023, so a wider crisis window may be correct *for
that quantity* and wrong for the price fit. The constant carries no comment and no source in a file
where its neighbours carry extensive provenance, so the repo cannot answer it. **This is a question
for the practitioner side of the knowledge layer, not a value to pick** — per `CLAUDE.md`, an honest
gap beats a plausible number. Filed here rather than silently unified.

Also not established: the per-constant mutation verdicts. The sweep runs ~4.5 min per constant
(baseline + narrow + wide over each importer's suite) and outlives this invocation; results land in
`~/.cache/const_census/mutation_results.json` for the next turn.

## The next increment

The durable fix is to widen `shared_primitive_census`'s vocabulary to module-level constants and its
`SCAN_ROOTS` to `tools/` — repairing an existing guard's scoping rather than minting register #10,
which is what `CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md` is already carrying. Deliberately not
done in this turn: widening the detector changes what row #9 reports, and a register whose residue
moves for a vocabulary reason rather than a tree reason needs its own before/after on one variable.
