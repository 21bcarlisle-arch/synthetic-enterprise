**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-committed-rendered-value-door-runs-the-pages-js-in-nodes-vm-and-no-browser-ever-sees-it`)

# The browser leg skipped in every linked worktree and blamed a playwright the machine had

**Delivery seat, 2026-09-17.** Pre-registration filed before any measurement:
`docs/staging/records/SEAT_PREREGISTRATION_DOES_THE_NEW_BROWSER_LEG_RUN_WHERE_THE_SEAT_ACTUALLY_WORKS_2026-09-17.md`.
All four predictions in it held.

---

## 1. The drawn item's premise was spent, and by more than the premise check saw

The item was drawn on the premise that `b55667741` (the chromium install) was already an ancestor
of `origin/main`. It was — but that commit is the *enabling capability*, not the work. The work
itself, both branches of it, had also landed:

> *"Measure what the vm harness can and cannot see … then EITHER state on the surface what the door
> actually grades, OR wire a browser leg for the part it cannot reach."*

`7f40070a6` did **both**: `docs/design/WHAT_THE_VM_DOORS_GRADE.md` is the statement, and
`site/_browser_probe.mjs` + `site/test_the_browser_reading.py` +
`site/harness/test_the_deployment_reading_is_visible_to_a_browser.py` are the leg. The item's own
supporting sentence — *"a tree-wide search for playwright returns only `background/health_check.py`,
its test, and the egress allowlist"* — was false at draw time.

**This is the un-re-asked-prediction shape again**, and the cheap tell was in the HEAD commit
subject: *"…the site lane's browser controls"*.

## 2. What was NOT established, and is the real finding

Nobody had asked whether the leg **runs where the work happens**. It did not.

From `/var/tmp/se-seat-executor`, a linked worktree, at `ce4806807`:

```
1 passed, 7 skipped      # the 1 is the git-index leg, which needs no browser
browser_available() -> 'playwright is not installed, so no browser reading can be taken'
```

**Every autonomous executor turn and every isolated seat invocation runs in a linked worktree.**
`node_modules/` is gitignored, so playwright exists only in the main checkout, and node's ESM
resolution walks up from the **importing file** — which is under the worktree.

So for one day: the control built *because* the vm doors were silently green on three breakages
that left a reader looking at nothing was **itself silently absent** in the environment the doors
are graded in. A skip is the same colour as a pass in a run summary.

### The mitigation was written, named its own hazard, and could not work

`read_in_browser`'s docstring said `cwd=PROJECT` was set "DELIBERATELY" for exactly this reason —
and stated, correctly, that ESM "walks up from the IMPORTING FILE". Those two sentences contradict
each other: `cwd` is what **CJS** resolves against. Measured both ways from the worktree —

| | resolves? |
|---|---|
| `node -e "require.resolve('playwright')"`, `cwd` = worktree | no |
| `node -e "require.resolve('playwright')"`, `cwd` = main checkout | **yes** |
| ESM `import` inside `<worktree>/site/_browser_probe.mjs`, `cwd` = main checkout | **no** |

`PROJECT` is the worktree root, so even the CJS check was asked the wrong question.

### The refusal named the wrong reason, which is what made it uncorrectable

It said *"playwright is not installed"*. Playwright was installed, with both chromium binaries,
throughout. The remedy that wording implies — `npx playwright install` — was not the remedy.
CLAUDE.md: *write refusals that name their reason*; a refusal that names the wrong one is how the
refusal escapes correction.

## 3. The fix, and the control that keeps it honest

- `_browser_probe.mjs` tries ordinary resolution first (main checkout needs no environment), then
  `createRequire` anchored at `POESYS_PLAYWRIGHT_BASE`, then **fails closed naming both attempts**.
  (`playwright/index.js` is CJS, so the ESM namespace puts it under `default` — asking for
  `ns.chromium` returned `undefined` and failed one call later with a message naming neither
  playwright nor resolution.)
- `playwright_base()` derives the main checkout from `git rev-parse --git-common-dir`, which is the
  shared `.git` from a worktree *and* from the main checkout. It falls back to `PROJECT` when git
  cannot answer — a clean `git archive` extract has no `.git`, and raising there would turn "no
  browser here" into a collection error in every non-repository tree.
- The skip reason now names **where it looked**.
- `test_a_machine_that_has_playwright_is_never_told_it_does_not` is the anti-skip control, and it is
  the only leg in that file that does **not** guard itself with `browser_available()` — a guard
  shared by every leg is precisely how they all go quiet together. Keyed to the property: it asserts
  the *refusal is true*, not that this machine has a browser, so it passes honestly where there is
  none. **Mutation-proved**: reverting the base to `PROJECT` reds it from a worktree and leaves it
  green in the main checkout — the asymmetry that let the defect live.

**Result: 9 legs pass from this worktree, none skip.** Chromium genuinely rendered.

## 4. Also corrected

`live_pixel_verify.py`'s G2 said *"rendered pixel (R11) — each door … must render real content"*.
No pixel has ever been rendered by it; it drives `site/_live_harness.mjs`, which is node/`vm`. G2
now reads "live render" and states which of the two experiences it grades, what it *is* evidence
for (the live host served these bytes, the live feeds parsed), and that the reader-side half is not
wired to the live host yet. `"pixel #"` in its report became `"wrote #"`.

*The phrase "the rendered pixel" was deliberately NOT purged tree-wide.* It is an established term
of art here — R11 is literally named "Verify to the rendered pixel" in `tools/generate_method_data.py`
— and 18 other sites use it to mean "the value the page's JS produced". Renaming a project idiom is
not this finding's business; the module whose **name** promises pixels, and which
`WHAT_THE_VM_DOORS_GRADE.md` explicitly recorded as owing a correction, is.

`docs/design/PIXEL_VERIFICATION_ON_THIS_MACHINE.md` had gone stale within hours of being written —
it asserted "the committed doors do not use a browser at all" and named the three playwright files.
Corrected **beside** the old claim rather than over it.

## 5. What is still owed

1. **A browser leg against the LIVE host.** `live_pixel_verify.py` reaches the deployed surface and
   nothing else does; its render half is vm-only. This is the highest-value next piece.
2. **~23 vm-backed suites still have no reader-side leg.** One door has one.
3. **The vm door beside the new leg still reads `_HERE / "index.html"`** — the working-tree copy —
   so it cannot separate "the reader can see this" from "someone in this tree has not landed it".

## 6. The generalisable shape

**A control's availability guard is part of the control, and it is the part nobody grades.** Every
leg here guarded itself with one shared predicate, so one wrong answer from that predicate silenced
all of them at once — and silence is indistinguishable from success. The remedy is the shape used
here: **one leg that does not share the guard, and that asserts the guard's own answer is true.**

Sibling instance already in the registers:
`SEAT_FINDING_THE_DOOR_REPORTED_THE_UNPUBLISHED_ENVELOPE_AS_A_SKIP_SEVEN_TIMES_A_RUN_FOR_106_HOURS_2026-09-15.md`.
That makes two, which is a class.
