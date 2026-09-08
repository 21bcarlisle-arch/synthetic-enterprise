**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A control that reads Python by substring is wrong in both directions, and two of them are walls

A test that walks `*.py` and asks `"token" in text` cannot tell a line that DOES the thing from a
comment that DESCRIBES it. That is not one bug with two symptoms — it is two independent failure
modes that arrive together, and this repository hit both inside one subsystem on one day.

`test_the_only_thing_that_invokes_it_is_the_declared_schedule` — the one control between this
repository and a second unattended writer — was simultaneously:

- **RED AT HEAD for eight days**, because `background/launch_long_job.py` cites the seat-executor
  cgroup as its worked example of a `KillMode=control-group` teardown. Naming the cgroup you die
  in is the opposite of arming a turn.
- **FAIL-OPEN** against the argv-list `subprocess.run` its own docstring offered as its mutation
  proof, because `-m background.seat_executor` is never contiguous in
  `["python3", "-m", "background.seat_executor"]`.

It had been widened FOUR times, each by an accurate comment, and each fix corrected the instance
and left the class. `tools/launch_shape_census.py` made the same correction independently before
shipping and recorded it. Two independent instances in one subsystem in one day is why this is a
class.

## The class, and the third direction nobody names

The screen — `tests/**/*.py` that `read_text` + enumerate + `in text`, with no `ast.parse` — is
noisy: most hits assert substrings over a function's OUTPUT, which is legitimate. The members are
the ones whose SUBJECT is Python source. A tight reading returns 12, a loose one 31; the
direction's screen returns 22, which is between them.

The third direction is the one worth naming, because it converts the noisy failure into the silent
one: **a NEGATED substring check inverts the two.** `"arrears_ledger" not in text` treats a module
that merely MENTIONS the shared reader in a comment as one that USES it — so an accurate note
about the fix is what hides the defect the fix was for.

## What was found, per instance

| Control | Direction | What it meant |
|---|---|---|
| `tests/sim/test_scenario_spine.py` | both | **WALL** (FRAME §A.3). Matched two line spellings; `from sim.scenario import (spine)` and the line-broken parenthesised form walked straight through. A docstring naming the spine read as importing it. Its reachability leg re-implemented the scan inline, so it proved a COPY could fail. |
| `tests/tools/test_credit_bureau_adapter.py` | both | **WALL** (SIM ground truth). Plus a second substring bug in the same control: `"test" in path.name` excluded four production modules — `liquidity_stress_test.py`, `collateral_death_test.py`, `stress_test.py`, and `annual_compliance_at**test**ation_register.py`. Risk and compliance code is exactly where a creditworthiness leak would be worth having. |
| `tests/saas/test_arrears_ledger_unavailable_is_not_green.py` | negated → fail-open | A comment naming the shared reader cleared a real offender. Separately, `saas/money.py` and `tools/generate_customer_consumption.py` were carried in the class on prose alone. |
| `tests/hooks/test_seat_guard.py` | fail-open | `# TODO: add is_resident_seat` certified a hook as guarded — the note admitting it is unguarded is what passed it. |
| `tests/architecture/test_a_mutation_marker_never_reaches_production_source.py` | none | **NOT a member.** It reads COMMENT tokens via `tokenize`; the comment IS its subject. Left alone. |

**Neither wall had a live breach under either reading.** These fixes change no verdict today —
they are keyed to the property rather than to today's answer, which is the point.

## What was done

`tools/python_code_text.py`, with the discriminator that was duplicated in
`tools/launch_shape_census.py` and in the seat-executor test:

- `searchable(source)` — comments and bare string expressions blanked to spaces (offsets, line
  numbers and quote style preserved, so `in` and `.splitlines()` behave as before at every call
  site), then every all-string list/tuple appended rejoined with spaces, so an argv literal reads
  the way a shell receives it.
- `imported_modules(source)` — the import graph from the AST, so a wall is keyed to the import
  rather than to how somebody typed it.
- **Fail-closed:** unparseable source returns its ORIGINAL text and `imported_modules` returns
  `None`. Not looking is never evidence of absence, and adopting this can never make a control
  quieter than it was.

Seven mutations against the module, five against the rewired controls, each killed by exactly one
leg.

## The one that got away, and what it cost to notice

The first draft of the arrears leg called `searchable()` directly instead of going through
`_ledger_reading_modules`. It passed with the naive reading restored — it proved the helper works
and said nothing about whether the scan uses it. This is the catalogued shape *"a control that
calls the estimator directly is blind to the wiring"*, entered while fixing a finding about
controls that cannot fail. `_ledger_reading_modules` now takes a `_root` so its legs run the
production scan.

## What is next

- The remaining screen members were triaged as legitimate (substring over an output, or over a
  `.service`/`.yaml`/`.json` where the mention IS the wiring) — **but only the five above were
  read line by line.** The tight/loose gap of 12–31 is unresolved and the residue is not zero.
- `tools/launch_shape_census.py` and `tests/background/test_the_seat_executor_stands_down.py`
  still carry their own correct copies of this discriminator. Both are right; neither was touched,
  because a rewrite of a live wall control is not a free change. Collapsing them onto
  `tools/python_code_text.py` is the obvious follow-on and is NOT done.
