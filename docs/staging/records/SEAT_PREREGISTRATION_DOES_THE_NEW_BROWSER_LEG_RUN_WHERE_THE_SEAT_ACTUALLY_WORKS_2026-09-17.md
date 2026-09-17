**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-committed-rendered-value-door-runs-the-pages-js-in-nodes-vm-and-no-browser-ever-sees-it`)

# PRE-REGISTRATION: does the browser leg landed at `7f40070a6` run in a LINKED WORKTREE?

**Filed 2026-09-17, delivery seat, BEFORE the measurement.** The drawn item's own work — measure
what the vm doors cannot see, then state it or wire a browser leg — landed at `7f40070a6` and is
spent. What is NOT established is whether the leg that landed can *run* in the environment this
seat, and the autonomous executor, actually work in: an isolated linked worktree.

---

## The observation that prompted the question

From this worktree (`/var/tmp/se-seat-executor`, a linked worktree of
`/home/rich/synthetic-enterprise`):

```
browser_available() -> 'playwright is not installed, so no browser reading can be taken'
```

`node_modules/` is gitignored and exists **only in the main checkout**. Every executor turn and
every isolated seat invocation runs in a linked worktree. So the reading above is what the browser
leg says on every such turn.

`site/test_the_browser_reading.py::read_in_browser` names this exact hazard in its docstring and
states the mitigation:

> *"Runs with `cwd=PROJECT` DELIBERATELY. `node_modules/` is gitignored and exists only in the main
> checkout, and node's ESM resolution walks up from the IMPORTING FILE — so a probe copied into a
> temp dir or a linked worktree reports 'Cannot find package playwright' … the probe stays in
> `site/` and only the PAGE is served from elsewhere."*

`PROJECT` is `Path(__file__).resolve().parent.parent` — **the worktree root, not the main
checkout**. So the mitigation is written for the temp-dir case and, if the reasoning in its own
docstring is right, cannot cover the linked-worktree case: the importing file *is* under the
worktree, and no `cwd` changes ESM ancestor-directory resolution.

## What I predict, before running anything

1. **The whole browser leg SKIPS in every linked worktree**, including under `surgical_land`'s
   gate when that gate runs in a worktree. Not one of its four scratch-page proofs, nor
   `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`'s three legs, executes.

2. **The skip reason is FALSE about the machine.** It says *"playwright is not installed"*. This
   machine has playwright installed (`/home/rich/synthetic-enterprise/node_modules`), with both
   `chromium-1234` and `chromium-headless-shell` present since `b55667741`. The true cause is
   *"this checkout has no `node_modules`"* — a different fact with a different remedy. CLAUDE.md:
   *write refusals that name their reason* — a refusal naming the wrong reason is how the refusal
   itself escapes correction.

3. **Setting `cwd` will not fix it.** ESM resolution walks from the importing file. I predict
   `node -e "require.resolve('playwright')"` (CJS, resolves from `cwd`) and
   `import { chromium } from "playwright"` inside `<worktree>/site/_browser_probe.mjs` (ESM,
   resolves from the file) BOTH fail here, and that the CJS one would succeed with
   `cwd=/home/rich/synthetic-enterprise` while the ESM one still fails.

4. **Resolving explicitly against the main checkout WILL fix it** — `createRequire` anchored at
   the directory `git rev-parse --git-common-dir` points into, then a dynamic import of the
   resolved absolute path. I predict a headless chromium render then succeeds from this worktree.

## What would refute each

1 is refuted if any browser-leg test reports `passed` from here.
2 is refuted if playwright cannot in fact be resolved from the main checkout either.
3 is refuted if either resolution succeeds unchanged from this worktree.
4 is refuted if the explicit resolution still fails — in which case the honest outcome is to leave
the skip and correct only its wording, and say on the surface that the leg is main-checkout-only.

## Why this matters more than it looks

A skipped control and a passing control are the same colour in a run summary. This project has
already paid for that exact shape (`SEAT_FINDING_THE_DOOR_REPORTED_THE_UNPUBLISHED_ENVELOPE_AS_A_SKIP_SEVEN_TIMES_A_RUN_FOR_106_HOURS`).
The browser leg exists precisely because the vm doors were silently green on three breakages that
left a reader looking at nothing. If the leg that fixes that is itself silent everywhere the work
happens, the gap it closed is still open in practice — and the page that says it is closed
(`docs/design/WHAT_THE_VM_DOORS_GRADE.md`, *"What is now true"*) would be overstating.
