**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The census's dismissal rule was fail-open, and the scope is now the whole class

Answers `PREREG_HOW_MANY_ROWS_DOES_THE_CENSUS_MODULE_EVIDENCE_FALLBACK_HIDE_2026-09-08.md`.
Continues `SEAT_RESULT_ELEVEN_OF_THE_THIRTY_EIGHT_TOOLS_AND_BACKGROUND_SCANS_ARE_REAL_...` (commit
`413be79d4`), whose "what is next" list this closes.

## The drawn premise was already spent, and the draw could not know it

The direction was to read the ~30 `tools`/`background` rows and route or dismiss each. **That pass
had already been done** at `413be79d4`, over a population of 38, with 27 dismissals and 5 routed.
Its four-item "what is next" list is where the live work was, and three of the four are now done —
by that lane and by ones after it, not by this turn:

| item | state on arrival |
|---|---|
| 1. `commit_refusal_attribution.gate_ranks` | **already fixed** — `body()` calls `searchable()` |
| 2. `shared_primitive_census`, `gap_ledger_reconciler`, `annual_report_import_ratchet`, `half_hourly_dependency_ratchet` | **already fixed** — all four now import `searchable` |
| 3. the dict-membership blind spot, as an exemption row | done here, as floor rows carrying the reason |
| 4. extend the baseline past `tests/` | **the live work**, and its stated blocker is now clear |

Item 4 was deferred because *"extending it needs the six left rows retired or exempted first, or the
freeze pre-authorises them"*. Those six are retired. It is done here.

## The finding: the dismissal rule could only ever be wrong in one direction

`census()` decided a scan's subject with `evidence = _path_evidence(scope) or module_evidence`. That
fallback fires **only** when a scope says nothing about what it reads — which the module's own rule 3
calls `unknown` and REPORTS, under a docstring paragraph headed FAIL-CLOSED IS TOWARDS REPORTING. So
the fallback can only turn a member into a non-member, and never the reverse.

It was not a careless line. It was the fix for the opposite defect: concatenating scope and module
evidence made a test reading `site/capabilities/index.html` report as a Python scan because another
literal in the same file ended `.py`. **The false positive got a six-line comment; the false negative
it introduced got nothing** — which is the shape worth carrying forward, not the line itself.

The tell was in the module's own prose. Its docstring named `tools/canon_drift_check.py` and
`tools/capability_index.py` as *"the two worth a reader first"* — and the census returned neither.
`413be79d4` read that as a prior the measurement refuted, and for `capability_index` that is exactly
right (six `ast.parse` sites). For `canon_drift_check` **the right answer was reached by the wrong
route**: `probe_text_in_file` reads a path named in `docs/design/canon_claims.yaml`, so no
source-level evidence will ever say what its subject is, and it was being dismissed as `non-python`
on the strength of two markdown literals elsewhere in the file. It is a dismissal today only because
no live claim uses the `text_in_file` probe — a fact about the register, not about the code.

### Predictions, against results

| # | predicted | measured | |
|---|---|---|---|
| 1 | `tests/` gains 5–25, point estimate **12** | **12** | held |
| 2 | `tools`/`background` gains 3–15, point estimate **7** | **29** | **REFUTED** |
| 3 | both `canon_drift_check` rows appear | they do | held (and was near-certain — the worked example) |
| 4 | no row is lost | none lost, in either scope | held |

**Prediction 2 was wrong by a factor of four, and the error is the interesting part.** I sized it
from the `tests/` population, where a scanner's subject is usually a literal in the test that reads
it. Production code does not look like that: it reads a path off a module-level constant or a
parameter and matches in a scope carrying no literals at all — so the fallback fires far more often
outside `tests/` than inside it. **A rate measured on `tests/` does not transfer to `tools/`, and I
transferred it.** The prereg is what makes that legible rather than a rounding of the story
afterwards.

## What the 29 newly-visible rows are, and the one that was real

Read individually. Twenty-eight are dismissals in three families, and they are now floor rows
carrying that reason rather than exemptions nobody can re-examine:

* **The subject is not Python** — a Markdown register, a systemd unit, `robots.txt`, `requirements`,
  a rendered HTML door, a JSONL log. Reported only because the census fails closed.
* **Container membership, not a substring** — `key not in data` where `data` is a dict `json.loads`-ed
  out of file text. `_match_sites` cannot tell `x in dict` from `x in str`, and the taint sweep
  follows the text through the parse. This is `413be79d4`'s item 3, and it is the largest family.
* **A widening prefilter** whose verdict is taken from a parse tree afterwards
  (`reduction_dimension.claim_modules`, `running_total_order.scan_tree`). Too *wide* costs nothing.

The exception is **`tools/generate_evidence_data._count_test_functions`**, and it is the argument for
the whole fix: it counts `def test_` in Python source by regex, for a figure the evidence page
**publishes** as a count of what exists. `^\s*def` cannot be satisfied by a `#` comment, which is why
it read as safe — but a docstring can, and this repo's suites quote the signatures they replaced
constantly, because CLAUDE.md asks them to say what they superseded. Routed through `searchable()`.

**It changes no published number today, and saying otherwise would be the easy overclaim.** On the
real tree exactly one file in 1,680 moves — `tests/tools/test_generate_project_state.py`, 5 → 4 — and
that file is not cited by any atom, so `site/data/evidence.json` is unaffected. The control is keyed
to the property, not to today's answer: the count is wrong whenever a cited suite quotes a
signature, and nothing was stopping that.

## A pre-existing red, cleared in passing and recorded so it is not attributed here

`tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources` was **already red at
HEAD**, proved by restoring both `tools/generate_evidence_data.py` and `site/data/evidence.json` from
`HEAD` and re-running: still red. The committed artefact carried `test_functions: 100` for
`tests/controls/test_control_mutation.py`, which has been 98 on disk for some time. Regenerating
clears it, so the `site/data/evidence.json` in this commit fixes a stale published figure that is
**not** this lane's work and is not evidence for it. Recorded because a green that arrives beside
your change reads as caused by it.

## What is next

1. **Taint does not cross a call boundary.** `capability_index._wire_edges` reads a file and hands
   the text to `_path_references(text, ...)`, which does the matching. Neither scope is a member
   alone, so a scanner split across two functions is invisible however plainly it scans — and
   `_root_parameter` already concedes this shape exists for *paths* with nothing equivalent for
   *text*. The census cannot state its own coverage until this is either fixed or written down as a
   named limit, the way the nested-function case already is.
2. **A module's own AST helper is not recognised as a router.** `publisher_budget` calls
   `_module_int_constants(source)`, which is `ast.parse`, and the census reports it anyway because
   `ROUTERS` is a name set. Same root cause as (1).
3. **`closed_atom_delivery._scan` and `capability_index._path_references` now disagree about whether a
   path in a comment is a reachability edge**, and both are live. `413be79d4` dismissed the first by
   citing the rule that a commented path IS an edge; commits `2e4fa042a` and `0a1ba2d2f` then measured
   34 modules held up by comments and 128 more by docstrings, and stopped counting them. One tree,
   two opposite answers, landed days apart — the interconnection question, not a new-work question.
4. **`orphan_ratchet.scheduled_entrypoints` reads git hooks whole.** A commented `-m tools.x` line in
   a hook counts as scheduled. Out of scope for `python_code_text`, which is Python-only; noted so the
   next reader does not have to re-find it.
