**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Eleven of the thirty-eight `tools`/`background` scans are real, and the two I was pointed at are not members

Continues `SEAT_RESULT_THE_CENSUS_FINDS_117_WHERE_THREE_HAND_PASSES_FOUND_NINE_2026-09-08.md`,
which landed `tools/substring_source_scan_census.py` scoped to `tests/`. The drawn direction was
to read the `tools`/`background` population — *"production scanners whose subject is largely prose
CLAIMS about the tree, so routing them through `python_code_text` by reflex would retire rows that
ought to fire"* — and route or dismiss each with a stated reason.

That framing was right, and it is the finding: **27 of 38 are dismissals.** But it was right for a
different reason than the one it gave.

## The population is 38, not ~30, and the two files the direction named are not in it

`tools/canon_drift_check.py` and `tools/capability_index.py` were named as *"the two worth a reader
first"*. Neither is a member. Both already read Python through `ast.parse` — `canon_drift_check` at
four sites, `capability_index` at six — and the census correctly returns neither. The one substring
read in `canon_drift_check` (L479) is a claim anchor against a rendered HTML page, which is not
Python and never was.

**Nothing was wrong with the direction; the two names were a guess made before the census was run
over this scope, and the census is what the guess was for.** Recorded because a doorbell's named
priorities read as findings, and these two were priors.

## What the 27 dismissals actually are, and why "prose claims about the tree" is only half of it

The direction predicted the dismissals would be *scanners whose subject is prose*. Nineteen are
exactly that — the subject is Markdown, JSON, a systemd unit or a log, and the census reported them
only because it fails closed towards reporting when path evidence is absent or mixed. Those are
free.

The other eight are more interesting, and they split three ways:

**The subject is Python and the prose IS the point (3).** `shared_primitive_census._quantity_coverage`
reads `text[:2000]` deliberately, to find an ownership declaration *in a module docstring*.
`closed_atom_delivery._scan` reads comments on purpose, because a path written in a prose comment is
a reachability edge — this project has already established that in
`feedback_a_path_written_in_a_prose_comment_is_a_reachability_edge`. Routing either through
`python_code_text.searchable` would delete the thing it is looking for. `profile_test_suite.classify_population`
declares itself a heuristic starting point for manual review and nothing refuses on it.

**The substring is a widening prefilter and the verdict comes from the AST (3).**
`running_total_order.scan_tree`'s `any(f in source ...)` is only its fail-silent producer guard;
`scan_source` does the real work on a parse tree. `reduction_dimension.claim_modules` and
`startup_anchor_freshness.discover_maintained_surfaces` are the same shape. A prefilter that is too
*wide* costs nothing.

**The substring cannot reach the verdict (2).** `gap_register_scan.register5_claim_placeholders`
does regex `claim_status|PLACEHOLDER|not[_\s-]wired` over `company/carbon/carbon_ledger.py` — a
genuine Python-source-as-text read, and a comment saying "not wired" does match it. But the row is
seeded **unconditionally**; the regex only chooses which of two reason strings is printed. It cannot
open or close anything. Dismissed as cosmetic, and named here so the next reader does not re-find it.

## A census defect this scope exposed, which `tests/` could not have

`background/publisher_budget.declared_publisher_budget_seconds` is reported as a member. It is not
one. Its `in` is a **dict membership test** — `BUDGET_CONSTANT not in constants`, where `constants`
came out of `_module_int_constants(source)`, which is `ast.parse`. The census's taint sweep follows
`source` into that call and cannot tell a text container from a structured one on the way out, so
`x in dict_derived_from_source` reads as `x in source`.

Filed rather than fixed: this is one row in 38, the direction is fail-closed towards reporting by
design, and widening the taint model is the census's own lane. **The row should be retired by an
exemption with this reason attached, not by narrowing the sweep** — a narrowed sweep is how this
class survived four instance fixes.

## The eleven real members, and the five that are fixed here

| # | Site | Why it is real | This turn |
|---|---|---|---|
| 1 | `tools/company_network_isolation.py::network_capable_directly` | **the epistemic wall**, fail-open | **fixed** |
| 2 | `background/stop_control_audit.py::_check_module_symbols` | fail-open | **fixed** |
| 3 | `background/stop_control_audit.py::_check_flag_readers` | fail-open | **fixed** |
| 4 | `background/stop_control_audit.py::_check_cited_tests` | fail-open | **fixed** |
| 5 | `tools/grid_intensity_guard.py::_check_owner` | fail-open | **fixed** |
| 6 | `background/shared_primitive_census.py::_primitive_inventory` | a comment inflates `caller_count`/`migrated_count` | left |
| 7 | `background/gap_ledger_reconciler.py::discover_writers` | a comment naming the write marker invents a writer | left |
| 8 | `tools/commit_refusal_attribution.py::gate_ranks` | a comment moves a gate's **byte-offset rank** | left |
| 9 | `tools/half_hourly_dependency_ratchet.py::scan` | already hand-rolls half the remedy (strips full-line `#` only) | left |
| 10 | `tools/annual_report_import_ratchet.py::render_debt` | a **published** count (`_section` importers) | left |
| 11 | `background/shared_primitive_census.py::_quantity_coverage` | the inverse: wants the docstring, reads 2000 raw chars | left |

Six left, all RECORDED not blocking: none is a wall, and each changes a diagnostic figure rather
than a refusal. #8 is the one to take next — `searchable()` blanks in place and preserves offsets,
so it is a one-line change, and the rank it corrupts is what makes the refusal log analysable.

## The five fixes were invisible from the live tree, which is why the poison round came first

**Every one of the five is an equivalence on today's tree.** The wall returns the same 31 modules
before and after; `stop_control_audit` still reports PASS; `grid_intensity_guard` still reports
clean. A suite run is silent on whether the reading changed at all.

So reachability was proved by poison before any control was written, and the wall's table is the
argument for the whole exercise:

| case | byte reading | code reading | |
|---|---|---|---|
| `"""...never shell out to "curl"..."""` | `['curl']` | `[]` | prose fired the rule |
| `# never invoke "curl" here` | `['curl']` | `[]` | prose fired the rule |
| `run(["curl -sS " + URL], shell=True)` | `[]` | `['curl']` | **the wall was blind** |
| `run(["curl", "-s", URL])` | `['curl']` | `['curl']` | same |
| `run(" ".join(["curl","-sS"]), shell=True)` | `['curl']` | `['curl']` | same |

Row 3 is the one that matters. **Every shell-out in this repo that passes flags writes them inside
the string**, so the single control standing between company-side code and a socket was blind to the
commonest spelling of the thing it forbids. Row 1 is not hypothetical either: the byte reading made
`tools/company_network_isolation.py` report **itself** as network-capable, because the paragraph
explaining that a shelled `curl` is a route contains the token `"curl"`.

Six controls added; five kill the reverted reading, verified by reverting each fix and re-running:

```
FAILED test_MUTATION_a_binary_named_only_in_PROSE_does_NOT_fire
FAILED test_MUTATION_a_binary_inside_a_shell_STRING_fires
FAILED test_a_symbol_surviving_only_in_a_COMMENT_is_still_missing
FAILED test_a_cited_test_recited_only_in_a_DOCSTRING_is_still_missing
FAILED test_a_flag_named_only_in_a_COMMENT_is_not_a_reader
FAILED test_an_owner_declaring_its_names_only_in_COMMENTS_has_lost_its_subject
```

The sixth — `test_a_word_that_merely_CONTAINS_a_binary_name_does_not_fire` — is green in **both**
directions and kills nothing. It guards the `\b` boundary in the widening I introduced, not the fix:
without it, `nc` fires on every `increment`. Named as what it is rather than counted towards the
kills.

## What is next

1. **#8, `gate_ranks`** — one line, and it corrupts the ordering evidence the refusal log rests on.
2. **#6, #7, #10** — the diagnostic-figure three; #10 is published, so it goes first of those.
3. **The census's dict-membership blind spot** — as an exemption row carrying the reason above, in
   the census's own lane. Not a narrowing of the taint sweep.
4. **Scope the baseline.** `docs/observability/substring_source_scan_baseline.json` is frozen over
   `tests/` only. Extending it to `tools`/`background` needs the six left rows retired or exempted
   first, or the freeze pre-authorises them. **Not done here on purpose**, and not merely deferred:
   local `main` is 4 commits behind `origin/main`, the baseline and the census both live only on
   `origin`, and freezing a baseline from a tree that does not contain its own subject is the
   `feedback_freezing_a_ratchet_baseline_from_the_dirty_shared_tree` shape. It belongs to the turn
   that reconciles the divergence.
