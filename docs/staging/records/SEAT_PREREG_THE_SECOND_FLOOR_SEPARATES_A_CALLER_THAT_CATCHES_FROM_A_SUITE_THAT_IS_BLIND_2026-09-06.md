**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: does the second floor separate a caller that CATCHES it from a suite that is blind?

**Written 2026-09-06, delivery seat, claim id `converged-battery-next-subject`. Every prediction
below is fixed BEFORE the battery runs, and this file lands in the same commit as the instrument
and ahead of any result, so the ordering is in the record and not in a claim about the record.**

---

## The drawn reason is spent, and it is recorded spent rather than worked around

`tools/generate_company_data.py` was ranked as the sweep's fifth subject for having **zero test
importers**. It has one. `tests/tools/test_generate_company_data.py` — 16 tests, dedicated, 0.6s —
landed at `cbd5f6298` ("42 tests move to where a runner looks"), which is already an ancestor of
`origin/main`. The previous pre-registration's closing line, *"in `tests/` only as a string inside
a manifest"*, was true when written and is not true now.

That does not retire the subject, and the replacement reason is stronger than the one it replaces:
**this is the first subject in the sweep whose call sites defeat the instrument.**

## The screen says four callers. One of them is not a caller, and not committed

`converged_contract_screen --module tools/generate_company_data.py` answers **4 callers / 1 direct
/ 133 reaching**. The drawn item recorded 3 / 1 / 132. The fourth caller is
`tools.test_generate_company_data`, and three things are true of it:

* it is `tests/tools/test_generate_company_data.py` **byte for byte** (`diff` is empty);
* it is **not in `HEAD` and not on `origin/main`** — `cbd5f6298` moved it, and `git ls-tree` finds
  it at neither revision;
* it is present on disk and staged `A` in the **shared index** by another lane.

So the screen — which reads the working tree — is counting the file the collection-gap repair
removed, resurrected in a tree state no commit contains. It is left exactly where it is (another
lane's staged work; not my pathspec) and recorded here.

It is **excluded from the battery**. `survived_all`'s population is the CALLER suites; entering the
subject's own dedicated tests into that column as well as the direct one would have the subject
grading itself, and the number would still read as a caller result.

## The mechanism under test, stated before the measurement

All three real callers import the subject **lazily, inside a function body**. Two wrap that import
in `except Exception`:

| caller | call site | guard |
|---|---|---|
| `background/process_run_complete.py:4104` | `generate_dashboard_json()` | `try: … except Exception as exc: log("company.json generation failed: …")` |
| `tools/generate_world_data.py:408` | `_book_population_class()` | `try: … except Exception: return _POP_UNSTATED, "…could not be imported"` |
| `tools/generate_dashboard_data.py:2631` | `_check_front_door_segment_claim()` | none |

The engine's reachability floor raises an **`Exception`** at import time. Two of these three catch
it. Their suites can therefore run the call site end to end and stay **green** — and on every
previous subject the engine stamped that green `NEVER REACHES`, which here would be false in the
flattering direction twice over: it excuses the row, and it hides that the call site cannot
propagate a failure of the subject at all.

So this subject gets a **second floor**, added to `tools/contract_battery.py` in the same commit:
`HARD_POISON_*` raises a `BaseException` subclass, which `except Exception` does not catch. Its
premise was verified before the run rather than assumed — a module raising a `BaseException` at
import, imported under `try/except Exception`, propagates and exits non-zero.

**Green under the first floor and RED under the second is a third state:
`swallows_subject_failure` — reached, executed, and structurally unable to fail.** It is the state
that reads most like the good answer, and the sweep has had no way to name it.

## The four suites

| | suite | why it is here |
|---|---|---|
| S1 | `tests/tools/test_generate_company_data.py` | the dedicated suite; the only one that NAMES contracts of this module |
| S2 | `tests/tools/test_generate_dashboard_data.py` | the unguarded caller's suite |
| S3 | `tests/saas/test_net_after_cts_and_blindfold_arithmetic.py` | the ONLY suite importing `generate_world_data` — and it imports `_crossing_blindfold`, not the function that reaches this subject. Scored anyway: "the caller's only suite does not run the path" is the answer, and excluding it would delete the question |
| S4 | `tests/background/test_process_run_complete.py` | drives `prc._process()` / `prc.main()` 11 times; 65s, the run's cost |

Controls (must stay GREEN under both floors): `tests/background/test_delivery_lane.py`,
`tests/design/test_atom_notes_store.py`.

## The ten contracts and the predictions

M1–M7 are `segment_revenue_mix` and `_book_mix` — **the converged surface, the one thing two
separate callers import.** M8–M10 are the distributions the dedicated suite was written for,
included so the direct column can be *told from* the caller columns rather than assumed stronger.

| id | the contract as the module states it | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| M1 | an EMPTY mix is unavailable — never a zero mix, which reads as a DOMESTIC book | survives | survives | survives | survives |
| M2 | a mix with no positive revenue is unavailable | survives | survives | survives | survives |
| M3 | unclassified revenue stays in the denominator | survives | survives | survives | survives |
| M4 | the DOMINANCE threshold is what makes a book non-domestic | survives | survives | survives | survives |
| M5 | a genuinely MIXED book says mixed | survives | survives | survives | survives |
| M6 | a segment divides by ITS OWN n, never the whole-book denominator | survives | survives | survives | survives |
| M7 | account counts come from the `segment` field, not an id substring | survives | survives | survives | survives |
| M8 | the cost-to-serve distribution fails closed on an empty sample | **DIES** | survives | survives | survives |
| M9 | the arrears distribution fails closed | **DIES** | survives | survives | survives |
| M10 | gross arrears exposure is a FLOOR, not a net | **DIES** | survives | survives | survives |

**Headline prediction, fixed now: the converged surface has NO proof anywhere. M1–M7 survive all
four suites. The only three contracts that die are killed by the dedicated suite alone — which no
caller reaches through — so `killed_by` is `[S1]` for M8–M10 and empty for the rest.**

**Floor predictions:** S1 RED under the first floor (module-scope import). S2 and S3 green under
BOTH floors — genuinely blind, because neither suite calls the function holding the import. S4 is
**the uncertain cell and the reason the second floor exists**: green under the first floor whatever
happens (its call site catches it), and I predict **RED under the second** — reaches and swallows.

**Null round:** no suite grades the text. None of the four reads the subject's source. (The tree's
text-grader for this call site is `tests/tools/test_website_integrity_fix.py`, which does
`source.index("generate_dashboard_json(json_path, git_hash)")` and is the one suite that actually
drives `prc.generate_dashboard_json`. It is NOT a caller suite and is outside the graded
population — named here so that, if the caller columns come back empty, it is on the record as the
next place to look and not a discovery made after the answer.)

## Every way this can be wrong is informative

* **S4 comes back green under BOTH floors** — then the 65s suite that drives `_process()` eleven
  times never reaches this generator at all, the second floor cost a round and answered a
  different question than the one it was built for, and `generate_dashboard_json`'s company leg is
  covered by nothing in `tests/background/`.
* **Any caller column kills anything** — then a lazily-imported, exception-guarded call site can
  still carry contract evidence, and the sweep's model of this shape is too strong.
* **S1 misses M8, M9 or M10** — a dedicated suite written *for* these distributions, landed nine
  days ago, is not proving the contracts it was written for.
* **A control reddens under either floor** — the floor is measuring the harness, and the
  reachability column is void for this subject and for the four before it, which used one engine.
* **The second floor reddens a control while the first does not** — the `BaseException` is
  escaping through pytest itself rather than through the call site, and the new round is void
  independently of the old one.

## What a result here cannot establish

Three callers is the whole caller population, so there is no sampling bound to declare. But the
screen is a proxy: it is blind to callers reached by subprocess or dynamic dispatch, and — as the
fourth-caller row above shows — it is not blind to files that exist only in a dirty index. And ten
contracts is what I chose to write down, not the module.
