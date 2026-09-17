**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-pixel-probe-is-version-only-so-it-cannot-see-a-missing-browser-binary`)

# Pre-registration: which browser binaries the pixel probe must require

**Filed 2026-09-17, delivery seat, BEFORE the measurement.** The answers below are predictions. If
the measurement refutes them, the refutation stays here beside the prediction and the design
changes.

---

## The question

`background/health_check.py::_check_pixel_verification_capability` runs `npx --no-install playwright
--version`, which answers from the npm package alone. Empty `~/.cache/ms-playwright` and the probe
still reports "available" while every real pixel check fails. Closing that fail-open requires
knowing **which browser binaries to require**, and that is not obvious:

- `playwright-core/browsers.json` marks chromium, chromium-headless-shell, firefox, webkit and
  ffmpeg as `installByDefault: true`.
- `~/.cache/ms-playwright` holds **only** `chromium_headless_shell-1234` and `ffmpeg-1011`. Full
  `chromium-1234`, `firefox-1538` and `webkit-2336` are **absent**.

So a probe keyed to `installByDefault` would go **RED today** on a machine where pixel verification
demonstrably works. That is the same false-red class that cost a full Lane 0 item on 2026-09-17
(`SEAT_RESULT_THE_MACHINE_NEVER_LOST_PLAYWRIGHT_..._2026-09-17.md`). The required set has to be
defined by **what the pixel-verification path actually launches**, not by what Playwright would
install if asked.

## What "pixel verification" is here, stated before it is measured

Per CLAUDE.md, "done means the rendered value changed", enforced by `site/test_*_door.py` — the
page's own JavaScript against the real feed. A grep of the committed tree for `playwright` returns
**three** files: `background/health_check.py`, its test, and `tests/background/test_egress_allowlist.py`.
**No committed door launches a browser through Playwright.** Pixel verification is performed
ad-hoc by sessions via `chromium.launch()`, headless.

## Predictions

1. **A headless `chromium.launch()` succeeds on this machine today**, with full `chromium-1234`
   absent, because modern Playwright routes `headless:true` through the headless shell.
2. **A headed `chromium.launch(headless=False)` fails today**, naming the missing
   `chromium-1234` executable.
3. Therefore the required set is **`chromium-headless-shell` alone**. `ffmpeg` is for video
   recording, not pixel verification, and is excluded despite being present — including a browser
   because it happens to be there is keying the control to today's answer.
4. The rewritten probe **returns `None` (available) on this machine today**. A fail-closed control
   that reddened a correct machine would be a defect, not a fix.

## How the control will be driven

`npx --no-install playwright install --dry-run` prints a resolved `Install location:` per browser,
honours `PLAYWRIGHT_BROWSERS_PATH`, touches no network, launches nothing, and costs **0.6s**
(measured) — so the probe's every-cycle speed budget survives. Both legs of the control are driven
for real, not mocked:

- **missing leg:** `PLAYWRIGHT_BROWSERS_PATH` pointed at an empty tmpdir → probe reports unavailable.
- **present leg:** the real cache → probe reports available.

A guard that refuses everything passes the missing leg alone, so both legs are required, and
prediction 4 is what makes the present leg falsifiable.

## What would refute the design

If prediction 1 is wrong — if a headless launch needs full `chromium-1234` — then the required set
is chromium **and** headless-shell, the probe is **correctly red today**, and the finding changes
from LATENT to a live outage.
