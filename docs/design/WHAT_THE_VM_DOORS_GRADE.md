# What the render doors actually grade

*Measured 2026-09-17, by construction, against `site/harness/index.html` at `origin/main`. This
page exists because "done means the rendered value changed" is load-bearing in CLAUDE.md and the
doors named as its enforcement were not grading rendering.*

---

## The sentence, and its two experiences

> **done means the rendered value changed**

"The rendered value" has two different experiences behind it:

1. **the page computed it** — the feed arrived, the render function ran, it wrote the right string
   into the right element;
2. **a person can read it** — that element exists in the markup, survives the stylesheet, survives
   every later script, and occupies a box on a screen.

Every committed door graded **(1)** and called it **(2)**. That is the definitional shape CLAUDE.md
names as this project's most expensive recurring failure — *average unit rate*, *net margin*, *bill
shock* — one phrase, two populations, nobody having said which is meant.

## How the doors work, and what that lets through

Five node/`vm` harnesses back roughly two dozen door suites: `site/_live_harness.mjs`,
`site/assets/_freshness_harness.mjs`, `site/explore/_bill_render_harness.mjs`,
`site/harness/_render_harness.mjs`, `site/knowledge/electricity-wholesale/_render_harness.mjs`.
Each extracts the page's inline script, runs it in `vm.createContext` against a stub `document`,
and reports the string a named render function wrote into a named element.

The stub is the whole story. `document.getElementById` **mints an element for any id asked of it**.
`style` is a plain object nothing reads. `classList.add/remove` are no-ops. `querySelectorAll`
returns `[]`. No CSS is ever parsed, because no stylesheet is ever loaded. And
`html.match(/<script>([\s\S]*?)<\/script>/)` is neither global nor greedy, so only the **first**
inline script exists.

### The measurement

One live door — `site/harness/test_the_deployment_reading_reaches_the_reader.py`, six legs
including a fail-closed leg and a null control. Three breakages of the page it grades, each run
twice: once through the door, once through chromium against the same bytes.

| | breakage | the vm door | what a reader meets |
|---|---|---|---|
| **A** | `#deployment { display: none }` added to the page's own `<style>` | **6 passed** | zero-height nothing (`display=none`, box `0×0`) |
| **B** | a **second** inline `<script>` clears the section after render | **6 passed** | empty section (`innerLength=0`) |
| **C** | container renamed `#deployment` → `#deployment-panel`, script unchanged | **6 passed** | **the element is not on the page at all** |

*Baseline, unmodified: door 6 passed, reader sees the full table. So the door was not simply
passing everything.*

**C is the one that sets the bar**, and its consequences were measured rather than assumed:

- `$("deployment")` returns `null`, so `.innerHTML =` throws a `TypeError`;
- the throw lands inside `fetch(...).then(...)`, so `renderCorrections`, `renderRules` and
  `renderControls` — later in the *same callback* — **never run**. Four sections dead from one
  renamed div;
- the chain's `.catch()` swallows it and writes *"The record behind this page could not be loaded,
  so no figures are shown"* into `#stamp`. **That is false** — the feed loaded perfectly;
- `pageErrors` is **empty**. No console error, nothing in any log.

So: a page telling its reader that its own record failed to load, four dead sections, and every
committed control green and silent.

### A note on `innerText`

`innerText` is specified to fall back to `textContent` when the element itself is not rendered — so
under breakage A the full sentence was still readable through the API while the reader met nothing.
**Words are not visibility.** Any control asserting only on text passes breakage A.

## The naming defect

`site/live_pixel_verify.py` is named for pixels and its guarantee **G2** is written *"rendered pixel
(R11) — each door is driven by its LIVE feeds and must render real content"*. It drives
`site/_live_harness.mjs`, which is node/`vm`. **No pixel has ever been rendered by it.** What it
does do is real and valuable and not available any other way — it fetches the **live deployed host**
and proves the feeds are reachable, 200, and parse — but that is feed-and-wiring evidence on a live
origin, not a rendering.

## What is now true

`site/test_the_browser_reading.py` takes the reader-side reading: it serves the **published (index)
copy** of `site/` over http and loads it in chromium, reporting existence, computed visibility, box
and shown text. `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py` is the first
door leg built on it.

Mutation-proved 2026-09-17 against a scratch repo (pristine → GREEN; A, B, C → RED, each on its own
clause). A fourth mutation — renaming `#corrections`, leaving `#deployment` perfect — reds the
`#stamp` leg alone, so that leg is independent and not a restatement of the first.

**The two halves stay separate on purpose.** The vm doors are faster, need no browser, and grade the
feed and the wiring better than a browser would; the browser leg grades only what they structurally
cannot see. This is not a replacement and the vm harnesses are not deprecated.

## The leg existed and did not run — corrected 2026-09-17

The section above was filed the day the browser leg landed. What it did not establish is whether
that leg *runs* in the environment the work happens in, and it did not:

**In every linked worktree — where every autonomous executor turn and every isolated seat
invocation runs — 7 of the 8 browser legs skipped, and the reason given was false.** They reported
*"playwright is not installed"* on a machine that has had playwright and both chromium binaries
installed since `b55667741`. `node_modules/` is gitignored, so it exists only in the main checkout,
and node's ESM resolution walks up from the **importing file** — `<worktree>/site/_browser_probe.mjs`
— which has no `node_modules` above it.

`read_in_browser` named this hazard in its own docstring and stated `cwd=PROJECT` as the
mitigation. That mitigation could not work and the docstring's own reasoning said why: `cwd` is what
**CJS** resolves against, ESM is not. Measured both ways from a worktree — `node -e
"require.resolve('playwright')"` succeeds with `cwd` set to the main checkout, and the ESM `import`
inside the probe fails identically with or without it. Pre-registered before the run:
`docs/staging/records/SEAT_PREREGISTRATION_DOES_THE_NEW_BROWSER_LEG_RUN_WHERE_THE_SEAT_ACTUALLY_WORKS_2026-09-17.md`.

**So the gap this page reported closed was still open in practice for one day**, and nothing could
have noticed: a skip is the same colour as a pass in a run summary, and the remedy the wrong reason
implied (`npx playwright install`) was not the remedy.

The probe is now handed `POESYS_PLAYWRIGHT_BASE`, derived from `git rev-parse --git-common-dir`
(whose parent is the main checkout from a worktree *and* from the main checkout itself), and falls
back to ordinary resolution first so the main checkout needs no environment.
`test_a_machine_that_has_playwright_is_never_told_it_does_not` is the control, and it is the one leg
in that file that does **not** guard itself with `browser_available()` — a guard shared by every leg
is exactly how they all go quiet together. It is keyed to the property, not to today's answer: it
asserts the *refusal is true*, so it passes honestly on a machine with no browser at all.
Mutation-proved — reverting the base to the worktree reds it from a worktree and leaves it green in
the main checkout, which is the asymmetry that let the defect live. **From this worktree, 9 legs now
pass and none skip.**

### What is still owed

- **Only one door has a browser leg.** The other ~23 vm-backed suites carry the same gap. This page
  is the statement on the surface that they do; wiring them is not done.
- **`live_pixel_verify.py` has been corrected in wording but not in reach.** Its G2 now says "live
  render", states plainly that no pixel has ever been rendered by it and what it *is* evidence for.
  A browser leg against the **live host** — the one subject no other control reaches — is still
  owed, and is the single highest-value next piece here.
- **The vm door beside the new leg still reads `_HERE / "index.html"`** — the working-tree copy, not
  the published one — so it cannot tell "the reader can see this" from "someone in this tree has
  fixed it and not landed it". That is the defect `site/test_the_published_bytes_reader.py` exists
  for, unfixed in that file.
- **Playwright absence still skips rather than fails**, matching how `node` absence is treated. That
  remains right — but the skip must now name where it looked, and a machine that *has* playwright
  can no longer be told it does not.
