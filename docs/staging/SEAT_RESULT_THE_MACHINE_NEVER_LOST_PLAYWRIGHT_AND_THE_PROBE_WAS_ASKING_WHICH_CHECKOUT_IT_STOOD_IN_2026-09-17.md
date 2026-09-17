**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `playwright-lost-so-the-pixel-verification-door-cannot-run`)

# The machine never lost Playwright. The probe was asking which checkout it stood in, and the doors never used Playwright at all

**Filed 2026-09-17, delivery seat.** Discharges
`SEAT_FINDING_THE_MACHINE_HAS_LOST_PLAYWRIGHT_..._2026-09-17.md` by **refuting its title**.
Prediction registered before the measurement:
`docs/staging/records/PREREG_WERE_THE_SITE_DOORS_FAILING_OR_SKIPPING_THROUGH_THE_PLAYWRIGHT_OUTAGE_2026-09-17.md`.

---

## 1. There was no outage

The drawn item asked me to restore Playwright. Running `npm install` in the main tree answered in
526ms:

```
up to date, audited 3 packages in 526ms
```

It was never gone. The same probe, one second apart, on one machine:

```
cwd=/home/rich/synthetic-enterprise   npx --no-install playwright --version  ->  Version 1.62.0
cwd=/var/tmp/se-seat-executor         npx --no-install playwright --version  ->  npm error npx
    canceled due to missing packages and no YES option: ["playwright@1.63.0"]
```

**`npx --no-install` resolves by walking UP from its cwd, and `node_modules/` is gitignored**
(`.gitignore:64`). So it exists in the main worktree and in no linked one, ever. The finding was
filed from a linked worktree. Its truncated error string — `["play....0"]` — is the second line
above, character for character.

So the reading was true of the checkout and false of the machine, and the function's own name,
the sentence it returns and the alarm it raises all claim the machine.

**Pixel verification is not merely installed, it works.** A real launch-and-render, not a version
string (`chromium.launch()` → `setContent` → read back the text):

```
headless(default):          LAUNCHED ok, rendered=42
headless:chromium-channel:  LAUNCHED ok, rendered=42
```

## 2. The doors were never affected, because they never used Playwright

The finding's §2 named the expensive outcome: doors quietly SKIPPING for the outage window, so that
every "done" claim inside it inherits doubt. **Registered prediction: neither — they were
unaffected.** The run, made BEFORE any restore attempt so it reads the alleged outage state:

```
python3 -m pytest site/ -p no:randomly -q -rs
807 passed, 38 skipped in 72.72s
```

**Zero failures, and not one of the 38 skips is browser-related** — every reason is a content reason
(`cites no data/state evidence files`, `renders no tables`, `the error bar and the point estimate
come from the same run`). `-rs` was the point: it prints every skip reason, so a silent skip could
not hide in a dot.

The cause is that the two capabilities wear one name. `site/test_home_door.py` says so in its own
docstring: the doors *"execute the page's ACTUAL inline JavaScript (via a **Node/vm harness**)"*.
`vm` is a node built-in; the harness requires nothing from `node_modules/`. A repo-wide search for
`playwright` outside `node_modules/` returns nine paths and **not one is under `site/`**.

**So no close in any window inherits doubt from this cause.** That is the finding's own stated worst
case, closed.

### The live risk in my prediction, and how it landed

The prereg named one way I could be wrong: `node_modules/` is gone *entirely* from a worktree, not
just its `playwright` entry, so a `require()` of any npm package inside the render harness would
break it too. It did not happen — the harness is `["node", HARNESS, page]` over built-ins only — but
it was the right thing to have written down, because it is the version of this bug that WOULD have
made the doors go red.

## 3. What I changed

`background/health_check.py::_check_pixel_verification_capability` now probes with
`cwd=_pixel_verification_root()` — `tree_lock.common_git_dir().parent`, the one tree that holds the
dependency, identical from every checkout. The resolver is reused from `background/tree_lock.py`
rather than re-derived: there is one correct answer to *which tree is the shared one*.

**This is a correction, not a narrowing**, and the distinction is the whole reason I touched the
control the previous hand deliberately left red. The finding was right that relaxing it to a skip or
mocking the probe could only hide. Anchoring it cannot: delete `node_modules/` from the main tree and
every caller in every checkout goes red together. What is removed is the FALSE red — the one that
cost a full Lane 0 item.

Two controls now hold it, and they are keyed to the property rather than to today's answer:

- `test_the_answer_does_not_depend_on_the_callers_cwd` — chdir to `tmp_path`, assert the answer is
  still `None`. **Mutation-proven**: dropping the `cwd=` argument reds it, with the exact
  `["play....0"]` string the original finding quoted.
- `test_the_root_it_probes_is_the_tree_that_holds_the_dependency` — the anchor names the MAIN
  worktree, asserted structurally (`.git` exists there) rather than against a hand-kept path string.

The three pre-existing mocked tests **cannot** grade this: they stub `subprocess.run` with
`lambda *a, **k`, which swallows `cwd` without looking at it. That is the catalogued
"a function gaining a parameter is ungraded" shape, and it is why the new leg had to drive the real
subprocess.

`tests/background/test_health_check.py`: **44 passed** from the worktree where the red fired.

## 4. The bounded gap I am NOT closing, named rather than left implicit

**The probe is version-only, so it cannot see a missing browser binary.** Its docstring argues that
deliberately (it runs every health-check cycle and must stay fast), and I am respecting that rather
than widening scope inside someone else's design decision. But the fail-open is real and should be
written down: `npx playwright --version` answers from the npm package alone, so if
`~/.cache/ms-playwright/` were emptied the probe would still say "available" while every real pixel
check failed.

It is currently benign, and I checked rather than assumed: `playwright-core/browsers.json` wants
`chromium 1234`, `chromium-headless-shell 1234` and `ffmpeg 1011`; the cache holds
`chromium_headless_shell-1234` and `ffmpeg-1011`, and **full `chromium` 1234 is absent**. Headless
launches work anyway (§1) because modern Playwright drives `headless: true` through the headless
shell. **A HEADED launch on this machine would fail today.** Nothing in the tree asks for one, which
is why this is a note and not a repair.

## 5. What this cost, and the shape worth keeping

A Lane 0 delivery item, a filed finding and most of a seat turn, to establish that nothing was
broken. The generalisable shape, and this project has now paid for it more than once:

> **A red measured in a linked worktree is a claim about that checkout until you have re-measured it
> in the main tree.** Anything resolved relative to cwd — `npx`, `node_modules/`, a gitignored
> artefact, a generated feed — differs between checkouts *by construction*, so the worktree
> isolation that makes concurrent lanes safe is the same mechanism that manufactures false reds.

The previous hand was right not to touch the control on the evidence it had, and right to file
rather than install. The missing step was cheap and is worth making reflexive: **before believing a
red about the machine, run the same probe in the main tree.** Under two seconds, and it would have
turned this item into a one-line note.
