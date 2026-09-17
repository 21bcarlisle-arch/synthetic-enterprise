# Pre-registration: what a headed browser launch actually costs this machine

**Filed 2026-09-17, delivery seat, BEFORE the measurement.** Lane 0 item
`the-headed-chromium-gap-is-latent-and-nothing-decides-when-it-becomes-live`.

The item offers two doors: install `chromium-1234` and require it in `REQUIRED_PIXEL_BROWSERS`, or
record that pixel verification here is headless-only by design. Both assume the gap is exactly
"headed". I do not believe that, and the predictions below are what I would have to be wrong about
for either door to be the whole answer. Written before running anything.

## What is already established (not predicted)

- `~/.cache/ms-playwright/` holds `chromium_headless_shell-1234` and `ffmpeg-1011` only.
- `chromium.launch(headless=True)` renders; `headless=False` fails on a missing executable
  (measured 2026-09-17, landed `31847df8a`).
- No committed door launches a browser at all: `site/live_pixel_verify.py` and
  `site/harness/_render_harness.mjs` both run node's `vm`, not a browser. The three files naming
  `playwright` are `background/health_check.py`, its test, and the egress allowlist.

## P1 — the gap is wider than "headed"

`chromium.launch(channel="chromium", headless=True)` will **FAIL** with the same missing-executable
error, not render. Modern Playwright routes plain `headless=True` through the headless shell, but
`channel="chromium"` selects the full binary deliberately — it is Playwright's own recommended way
to get *accurate* headless rendering. If this holds, the absent binary blocks a **headless** use
case a future session plausibly wants, and "headless-only by design" is a false description of the
gap rather than a smaller one.

*If P1 is wrong* (the channel falls back to the shell), the gap really is headed-only and the
knowledge-layer door is the honest one.

## P2 — a headed launch needs a SECOND thing, and the item names only the first

`DISPLAY` is unset in this process's environment, but `/tmp/.X11-unix/X0` exists (WSLg). So:

- With `chromium-1234` installed and `DISPLAY` unset, `headless=False` will **FAIL**, and on a
  *different* cause than today's — an X/display error, not a missing executable.
- With `DISPLAY=:0` set, it will **render**.

If that holds, "does this machine owe a headed launch" has two answers, and only one of them is a
property of the machine. The display half is a property of the **caller's environment**: a daemon
health check cannot assert it on a session's behalf, because the daemon's own environment is the one
without `DISPLAY`. Installing the binary therefore cannot close the gap on its own, and a health
check that claimed it did would be asserting something it had not measured.

## P3 — installing costs disk and nothing else

`npx playwright install chromium` will add roughly 150–200MB under `~/.cache/ms-playwright/` and
will not alter the `chromium-headless-shell` entry the live probe depends on. `df` reports 739G
free, so cost is not the deciding factor and I should not pretend it is.

## P4 — what I expect to decide, and what would change it

Expected: install the binary (it is cheap and removes a trap), do **not** add `"chromium"` to
`REQUIRED_PIXEL_BROWSERS` (nothing consumes it; requiring a capability no door uses is the false red
that has now cost this lane two Lane 0 items), and replace the comment that holds the trigger with a
**control** — the item's actual complaint is that *nothing decides when it becomes live*, and a
sentence in a comment is not a decision procedure.

I would abandon the install if it turned out to disturb the headless shell (it will not, per P3), and
I would abandon the control if the tree's only plausible future consumer could not be detected
without a narrowing written to dodge a false positive.
