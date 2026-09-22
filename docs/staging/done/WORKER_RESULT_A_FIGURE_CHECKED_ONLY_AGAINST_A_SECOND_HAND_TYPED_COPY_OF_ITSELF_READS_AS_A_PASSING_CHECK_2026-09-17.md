**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H47_the_orientation_header_states_a_figure_it_computes

# A figure checked only against a second hand-typed copy of itself reads as a passing check

**Filed** 2026-09-17 · worker · lane 1 build
**Item** `H47_the_orientation_header_states_a_figure_it_computes` (dial 12, L2->L3, harden)

> **The previous pass predicted this hole and deferred the repair. The hole was already occupied.**
> The startup header said `26,731 tests collected`; a real collection of a clean HEAD extract
> returned **36,835**; the control said `tests AGREES`; and the live site published the typed
> number. The figure was 27% low and had been frozen for 20 days and 1,440 commits.

---

## What the drawn work was

The atom's own Expert Hour (2026-09-17, earlier the same day) returned FAIL and held the level at
2. Two of its three disqualifying answers were repaired in that pass. The third, EH-3, was
deferred with a stated reason: the honest source is a real suite collection, and this project has
already retired one per-publish collection for costing 30-40s of a 9-minute cycle, so "the fix is a
design choice about publish cost, not an edit."

That reason rested on a false dichotomy, and the deferral cost nothing to discover because the
first thing the repair did was measure the thing the prediction was about.

## The defect, measured

Three of the four header figures are graded against git — `git rev-list --count`, and the `*.py`
blobs in the index — which no author can type into. The fourth was graded against CLAUDE.md's
`**Build:**` line, itself hand-typed. Two hand-typed numbers agreeing with each other produced a
degenerate band (`low == high == stated == 26,731`) that the stated value is inside by
construction.

| | |
|---|---|
| Stated in both documents | 26,731 |
| Real `pytest --collect-only` at a clean HEAD extract | **36,835** (37.9s) |
| Test functions in the git index at HEAD | 34,171 |
| Last change to the Build line | 2026-08-28, when the `**Build:**` spelling was introduced |
| Commits since | 1,440 |
| Verdict the control returned | `AGREES` |

The figure is parsed by `generate_dashboard_data._derive_build_from_claude_md`, so the live site
was publishing it. This is the same class as the 2,905-test gap in the incident that produced the
atom — unrepaired, one layer in.

## The third source, and why it costs nothing

The choice was never "per-publish collection or nothing". `_figures_at` **already** streams every
`*.py` blob at both window revisions to count newlines. The test functions in collectible-named
files are counted in that same pass, so the bound is free.

A collected item is never fewer than one per test function: class-nested, skipped and xfailed
functions are all still *collected*, and `@parametrize` only multiplies. So the index count is a
floor no truthful collection can sit below — 34,171 against 36,838 collected, a 7.2% margin.
Verified that no `testpaths`, `norecursedirs`, `collect_ignore` or `python_files` exists anywhere
at HEAD, so collection is pytest's default and the two filename spellings are exactly what it
walks.

Taken at the **low** end of the window, so an honestly-computed figure never races the suite's
growth. Checked **before** the band and before the `low is None` branch, because the whole point is
that it does not depend on the typed source being present, readable, or right: it is the only leg
that survives the Build line being deleted.

## What is NOT closed, and it is named on the reader's page

The floor bounds the figure below. **Nothing bounds it above** — `@parametrize` expansion is
unbounded and only a real collection knows it. An overstatement typed into both documents at once
still reads `AGREES`. The published legend now says so in the reader's own words: the four
verdicts are not worth the same, `tests` is floored but not capped, and an `AGREES` there rules out
a count too small and not one too large.

## The class, and where else to look

**A control that grades an artefact against a second hand-typed copy of itself is not a control; it
reads exactly like a passing one.** The reviewer predicted the shape blind ("roughly half the
self-consistency controls I have seen grade an artefact against a copy of itself") and it was
half-true here — the two documents *had* disagreed historically, so it was not a tautology, but it
was not independent evidence either.

**Nobody has censused the other places this repo compares a published figure to a second copy of
it rather than to the thing it counts.** That census does not exist and is the obvious follow-on;
it is not this atom's scope and is not filed as a claim here.

## The first draft of the floor was the same defect again, and the gate caught it

The floor was first counted with a **regex over the raw bytes**. `def test_x():` inside a string
literal is not a test, and this repository's own control fixtures write exactly that text into
temporary files: it over-counted by **25** (34,196 against 34,171). A floor that counts prose can
rise *above* the truth it bounds and red an honest figure — the one direction a lower bound must
never fail in.

`tests/architecture/test_a_control_reads_python_as_code.py` refused the landing and named both
functions. Two things worth keeping:

- `python_code_text.searchable()`, which that control's message recommends, removed only **one** of
  the 25 — the literals are call arguments, not bare string expressions — and cost **5.7s** against
  the AST's **1.4s**. The sanctioned-looking remedy was both less correct and more expensive here.
- The AST count is matched to what pytest *actually* collects (module-level functions, plus methods
  of `Test`-prefixed classes), not to every `def test_`. Counting nested or non-`Test`-class
  functions would inflate the floor the same way the regex did.

## Incidental, and it is the same lesson

Six existing tests in the control's own suite were pinned to the literal `9,385 commits` and the
old date. All six failed the moment the header became correct — a suite keyed to today's answer,
which is precisely the trap those tests exist to enforce *against the module*. They are now derived
from the header.

## Disposition

Landed. EH-3 repaired in part, residual named on the map row and on the published table. The level
stays at **2**: L3 waits on the residual and on a second blind pass, because a verdict cannot
certify the repairs it prescribed.
