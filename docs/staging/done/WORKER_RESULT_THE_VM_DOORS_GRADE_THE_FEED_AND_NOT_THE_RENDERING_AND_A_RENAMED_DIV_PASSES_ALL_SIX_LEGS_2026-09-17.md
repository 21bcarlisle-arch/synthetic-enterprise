**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The vm doors grade the feed and not the rendering, and a renamed div passes all six legs

*Lane 0 delivery, 2026-09-17. Claim:
`every-committed-rendered-value-door-runs-the-pages-js-in-nodes-vm-and-no-browser-ever-sees-it`.*

## Premise: HELD

The item cited `b55667741` and the draw flagged it as already an ancestor of `origin/main`. It is —
but that commit is the item's stated **precondition** (chromium installed on this machine), not its
work. Re-measured at `origin/main`, not at the local worktree, which was 19 commits behind:
`playwright` appears in `background/health_check.py`, its test, the egress allowlist and one
generated feed. **No door.** The premise was not spent.

## What was measured

By construction, on one live door — `site/harness/test_the_deployment_reading_reaches_the_reader.py`
(six legs, including a fail-closed leg and a null control) — in a clean `git archive` extract of
`origin/main`, with each breakage run through both the door and chromium against the same bytes.

| | breakage | vm door | reader |
|---|---|---|---|
| — | pristine | 6 passed | full table, visible |
| A | `#deployment{display:none}` in the page's `<style>` | **6 passed** | box `0×0` |
| B | a second inline `<script>` clears the section | **6 passed** | empty |
| C | container renamed to `#deployment-panel` | **6 passed** | **element absent** |

The stub `document` is why: `getElementById` mints an element for any id, `style` is a bag nothing
reads, `classList` is a no-op, no CSS is loaded, and the script regex is neither global nor greedy
so only the first inline `<script>` exists.

**Breakage C's real cost, measured:** the `TypeError` lands inside `fetch().then()`, so
`renderCorrections`, `renderRules` and `renderControls` never run — four sections dead — and the
`.catch()` publishes *"The record behind this page could not be loaded"*, which is false. Zero page
errors. Every committed control green.

## What landed

- `site/_browser_probe.mjs` — chromium probe: existence, computed visibility, box, shown text.
- `site/test_the_browser_reading.py` — serves the **published (index)** copy over http and takes the
  reading. Mechanism and proofs share a file for the reason
  `site/test_the_published_bytes_reader.py` gives: a `_browser_reading.py` whose only callers are
  test files is an orphan by construction under `tools/capability_index.py`.
- `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py` — the first browser leg.
- `docs/design/WHAT_THE_VM_DOORS_GRADE.md` — the statement on the surface.

Mutation-proved against a scratch repo: pristine GREEN; A, B, C RED each on its own clause; a fourth
mutation (rename `#corrections`, leave `#deployment` perfect) reds the `#stamp` leg alone, so that
leg is independent.

## Two things found on the way

**A lock-free subject was forced, and the first version was wrong.** `published_site_server` first
resolved the index with `git write-tree`, which takes `.git/index.lock` — and the first run in the
shared tree failed because another lane held it. A door keyed to acquiring that lock reds on other
lanes' *timing*, not on its subject, and would wedge every commit it ran under. It now uses
`ls-files -s` + `cat-file --batch`, which answer the same question reading only `.git/index`.

**`node_modules` is gitignored and lives only in the main checkout**, and node's ESM resolution
walks up from the *importing file* — so a probe copied to `~/.cache` or run from a linked worktree
reports "Cannot find package 'playwright'" and reads as *a machine with no browser*. That is the
same artefact shape behind
`SEAT_FINDING_THE_MACHINE_HAS_LOST_PLAYWRIGHT...` and its correction
`SEAT_RESULT_THE_MACHINE_NEVER_LOST_PLAYWRIGHT_AND_THE_PROBE_WAS_ASKING_WHICH_CHECKOUT_IT_STOOD_IN`.
The probe therefore stays in `site/` and only the *page* is served from elsewhere; this is written
into the docstring so the next lane does not re-derive it.

## Owed, and deliberately not done here

1. **~23 other vm-backed door suites have the same gap.** One leg landed; the rest is not done. The
   design page states this rather than leaving it implied.
2. **`site/live_pixel_verify.py` is named for pixels and renders none** — it drives
   `site/_live_harness.mjs`, node/`vm`. Its guarantee **G2** is written *"rendered pixel (R11)"*.
   What it uniquely does (fetching the **live deployed host** and proving feeds are reachable and
   parse) is real and worth keeping; the wording is the defect. Correct G2 or give it a browser leg.
3. **The vm door beside the new leg reads `_HERE / "index.html"`** — the working-tree copy. It
   cannot separate "the reader can see this" from "someone in this tree has fixed it and not landed
   it", which is exactly what `site/test_the_published_bytes_reader.py` exists for. Belongs to that
   door, not to this claim.
4. **Playwright absence skips**, matching `node` absence. A stated hole, not a pass.
