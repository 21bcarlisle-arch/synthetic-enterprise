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
- ~~**`live_pixel_verify.py` has been corrected in wording but not in reach.**~~ **Closed
  2026-09-17 — see "The live host is now read by a browser" below.**
- **The vm door beside the new leg still reads `_HERE / "index.html"`** — the working-tree copy, not
  the published one — so it cannot tell "the reader can see this" from "someone in this tree has
  fixed it and not landed it". That is the defect `site/test_the_published_bytes_reader.py` exists
  for, unfixed in that file.
- **Playwright absence still skips rather than fails**, matching how `node` absence is treated. That
  remains right — but the skip must now name where it looked, and a machine that *has* playwright
  can no longer be told it does not.

## The live host is now read by a browser — 2026-09-17

The hole this page described was in the UNION of the two halves, exactly where the reader is. The
vm verifier proved the live host served the bytes and the live feeds parsed; the browser leg proved
a person could read the PUBLISHED bytes. Neither proved a person can read the **LIVE page**, which
is the only claim R11 and CLAUDE.md's "done means the rendered value changed" actually make — and
all three breakages in the table above are deployable, invisible to the vm verifier, and reach
readers.

`site/live_pixel_verify.py` now carries **G4**: the live url is loaded in chromium and every
element the door's own script wrote content into must EXIST in the live DOM, be VISIBLE, and carry
words.

**The element list is derived, never typed.** It is G2's own output — the ids the vm harness
reports the door wrote into — so G4 is a strict addition to G2 rather than a second opinion, and
a section added to a door is graded on the day it ships without anyone editing a list. The three
breakages line up against it by construction: the renamed container reads `exists: false` (the vm
mints an element for any id), the stylesheet rule reads `visible: false` (the vm parses no CSS),
and the later inline script leaves a box with no words in it (the vm's regex takes only the first).

**`:body` — the whole-page reading — is always in the subject list**, which is what carries a
STATIC door. `/privacy/` and the Front Door write into no element, so a G4 whose subject was "the
written elements" would have had an EMPTY subject on exactly the doors where a broken build ships a
nav-and-footer shell.

**It fails closed, and differently from the pytest suite on purpose.** `test_the_browser_reading.py`
SKIPS when playwright is absent, because it runs on every machine and this repo tolerates one
without a browser. G4 RAISES, because this is a tool invoked at door close to produce R11 evidence,
and reporting "the live doors verified" having rendered nothing is the fail-silent shape the module
exists to refuse.

### What the first reading found

Pre-registered before the run, in
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_BROWSER_MEETS_ON_THE_LIVE_DEPLOYED_DOORS_2026-09-17.md`,
which holds the table and the corrections. **86 written elements across the 5 live dynamic doors:
0 not in the DOM, 0 not visible, 0 page errors, every door 200 to chromium.** No live defect. The
prediction that at least one would be hidden was **wrong and is recorded as wrong** — and it is
what let the STRICT rule be chosen instead of the weaker one I had been hedging toward, because the
false-positive risk it was hedging against does not exist on this site.

So G4 has never fired on a real defect, which is weaker than a control caught in the wild. It is
mutation-proved offline instead, through a `reader` seam mirroring `fetcher`: dropping the
visibility clause, letting an unreadable page return an empty reading, and hand-typing the element
list each red their own leg. A fourth mutation did not fire and was established as an
**equivalence**, not a missing test — the clause it removed could never change a verdict, and has
been deleted rather than left reading as protection.

### What is still owed after this

- **The other ~23 vm-backed suites still have no browser leg.** G4 covers every DEPLOYED DOOR; it
  does not cover a door's individual pytest suite, and `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`
  is still the only one of those built.
- **G4 costs a browser launch per door**, so a full run is minutes rather than seconds. That is
  right for a door-close tool and would be wrong in a commit gate — which is where this module has
  always said it does not belong.
