# Pixel verification on this machine — what renders, what does not, and why

**Established by measurement 2026-09-17** (delivery seat, Lane 0
`the-headed-chromium-gap-is-latent-and-nothing-decides-when-it-becomes-live`).
Pre-registration:
`docs/staging/records/WORKER_PREREGISTRATION_WHAT_A_HEADED_BROWSER_LAUNCH_ACTUALLY_COSTS_THIS_MACHINE_2026-09-17.md`.

This exists so the next session that wants a screenshot stops re-deriving it. Three Lane 0 items
have now been spent on questions this page answers.

## The committed doors do not use a browser at all

`site/live_pixel_verify.py` and `site/harness/_render_harness.mjs` execute the page's own JavaScript
in node's `vm`. **Every committed "done means the rendered value changed" door runs that way.** The
only files in the tree naming `playwright` are `background/health_check.py`, its test, and the egress
allowlist. So a browser is a session tool here, not a harness dependency — which is why
`REQUIRED_PIXEL_BROWSERS` is deliberately smaller than what Playwright would install.

## What launches, measured (not assumed)

| Launch | Result |
|---|---|
| `chromium.launch(headless=True)` | **renders** — routed to `chromium-headless-shell` |
| `chromium.launch(headless=True, channel="chromium")` | **renders** (since 2026-09-17; failed before) |
| `chromium.launch(headless=False)`, `DISPLAY` unset | **FAILS** — "Target page, context or browser has been closed" |
| `chromium.launch(headless=False)`, `DISPLAY=:0` | **renders** |
| `firefox`, `webkit` | **absent** — never installed, nothing has asked |

## Two conditions, and only one of them is a property of the machine

The gap here was called "headed" for a day, and that name was wrong in the expensive direction.

**First condition — the binary.** With `chromium-1234` absent, `headless=False` *and*
`channel="chromium", headless=True` both failed with the identical `Executable doesn't exist at
.../chromium-1234/chrome-linux64/chrome`. The second is a **headless** mode — Playwright's own
recommended channel for accurate rendering. "We only render headless here, so a headed binary cannot
matter" was therefore a false sentence, and it was the sentence holding the decision. The binary is
now installed (184 MiB; 739 G free — cost was never the constraint).

**Second condition — a display.** With the binary present, a headed launch *still* fails when
`DISPLAY` is unset, and this environment has it unset while WSLg's `/tmp/.X11-unix/X0` exists.
`DISPLAY=:0` renders. **Set `DISPLAY=:0` if you want a headed browser** — the failure without it
names nothing you could act on.

This half is a property of the **caller's environment**, not the machine, and that is why no health
check asserts it: the daemons that run the health check are themselves in the environment without a
display, so a green there would be evidence about the wrong process. A capability check can only
honestly answer the binary half.

## Why the alarm still does not require `chromium`

Because nothing launches it. Requiring a capability no door consumes is the false red that has cost
this lane two Lane 0 items, and "it is on disk now" is the same today's-answer keying the constant's
own comment already forbids for `ffmpeg`.

What changed is that the trigger is no longer prose.
`tests/background/test_health_check.py::test_the_requirement_tracks_what_the_tree_launches_in_both_directions`
parses the tree for a launch selecting the full binary (`headless=False` or `channel="chromium"`, in
Python via AST and in JS via its call text — so a *sentence about* a headed launch, like this page,
does not trip it) and grades the constant **in both directions**: red if a consumer appears without
the requirement, red if the requirement is asserted with no consumer. Mutation-proven all three ways
— blinded detector, requirement-without-consumer, consumer-without-requirement.

If you are the session that adds the first consumer: the control will red and tell you to add
`"chromium"` to `REQUIRED_PIXEL_BROWSERS`. Do that. On a machine missing the binary,
`npx playwright install chromium` fixes it.
