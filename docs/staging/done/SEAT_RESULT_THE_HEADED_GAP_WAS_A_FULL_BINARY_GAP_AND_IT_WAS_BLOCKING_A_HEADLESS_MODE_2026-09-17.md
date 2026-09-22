**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-headed-chromium-gap-is-latent-and-nothing-decides-when-it-becomes-live`)

# The headed gap was a full-binary gap, and it was blocking a headless mode

**Filed 2026-09-17, delivery seat.** Prediction registered before the measurement:
`docs/staging/records/WORKER_PREREGISTRATION_WHAT_A_HEADED_BROWSER_LAUNCH_ACTUALLY_COSTS_THIS_MACHINE_2026-09-17.md`.
Follows `SEAT_RESULT_THE_PIXEL_PROBE_ASKED_THE_NPM_PACKAGE_..._2026-09-17.md` (landed `31847df8a`),
which established the gap and deliberately left it un-alarmed.

Premise re-measured before starting: `REQUIRED_PIXEL_BROWSERS = ("chromium-headless-shell",)` at
`origin/main`, `chromium-1234` absent. Live, not spent.

---

## 1. The item offered two doors and both rested on a false premise

Install-and-require, or write down that pixel verification here is headless-only by design. Both
take "the gap is *headed*" as given. The pre-registration said I did not believe that (P1), and the
measurement agreed:

```
chromium.launch(headless=True, channel="chromium")
  -> FAIL  Executable doesn't exist at .../ms-playwright/chromium-1234/chrome-linux64/chrome
```

Identical error to `headless=False`. `channel="chromium"` is a **headless** mode — Playwright's own
recommended channel for accurate rendering. So "headless-only by design" would have been a false
description of the machine, and false in the direction that reads *this cannot matter, we only
render headless*. **The name of the gap was doing the reasoning.** That is this project's recurring
shape (*before measuring a thing, say what it is*) in its cheapest possible form: one word, one day
old, and it had already decided the answer to a Lane 0 item.

The second door is closed. Not written down, because it is not true.

## 2. The first door is closed too, and for the reason the previous turn gave

`chromium-1234` is now **installed** (184.3 MiB; 739 G free — cost was never the constraint), and
`"chromium"` is still **not** in `REQUIRED_PIXEL_BROWSERS`. Nothing in the tree launches it; alarming
on a capability no door consumes is the false red that has cost this lane two Lane 0 items, and *it
is on disk now* is precisely the today's-answer keying the constant's own comment already forbids
for `ffmpeg`. Installing it and requiring it are separate decisions and only the first was earned.

`tests/background/test_health_check.py`: **47 passed**, including the live leg proving the headless
shell probe is undisturbed by the new install.

## 3. A headed launch needs two things, and only one is a property of the machine

P2, both halves confirmed. With the binary present:

| Launch | Result |
|---|---|
| `headless=False`, `DISPLAY` unset | **FAIL** — "Target page, context or browser has been closed" |
| `headless=False`, `DISPLAY=:0` | **renders** |

The failure mode *changed cause* — from a missing executable to a missing display — which is the
only reason it is visible at all, because the second error names nothing actionable. WSLg's
`/tmp/.X11-unix/X0` exists; this process's `DISPLAY` does not.

**So the health check could never have owned this.** The display half is a property of the
**caller's environment**, and the daemons that run the health check are themselves in the
environment without a display: a green there would be evidence about the wrong process. The item
asked whether a headed launch is "a capability this machine owes" — the honest answer is that
"headed capability" is not a single thing a machine either has or lacks, and the version of the
question a probe can answer is the binary half alone.

## 4. What actually gets fixed: the trigger was a sentence

The item's real complaint — *nothing decides when it becomes live* — was correct, and neither
offered door addressed it. The trigger lived in a code comment reading "add a name here when
something in the tree launches it". A sentence does not decide anything, and the one above it had
just been shown to be wrong.

It is now graded, **in both directions**, because both have already been paid for:

- a consumer appears and the requirement does not follow → the probe reports a capability green
  while the thing needing it fails;
- the requirement is asserted with no consumer → the false red.

`test_the_requirement_tracks_what_the_tree_launches_in_both_directions` **parses** rather than greps
(AST for Python, call-text for JS), so `health_check.py`, its test and
`docs/design/PIXEL_VERIFICATION_ON_THIS_MACHINE.md` — all of which discuss `headless=False` at
length — do not trip it. A fixture tree proves the partition is reachable before the live leg
asserts which side it is on: a detector that finds nothing passes the live leg on its own.

| Mutation | Result |
|---|---|
| Python detector blinded | fixture leg **REDS** |
| JS detector blinded | fixture leg **REDS** |
| `searchable()` dropped, raw source matched instead | fixture leg **REDS** — see below |
| `"chromium"` added with no consumer | live leg **REDS** (the false-red direction) |
| a real `launch(headless=False)` module added to `tools/` | live leg **REDS**, naming the file and the remedy |

An unparseable file falls back to the text scan rather than reading as innocent — another lane's
syntax error must not be able to switch the control off.

## 4a. The gate refused my first draft, and it was right

`tests/architecture/test_a_control_reads_python_as_code.py` reds `surgical_land` on a control that
reads Python source as text, and it named both of my new functions. That is not a formality here:
this control's own subject is the string `headless=False`, and `health_check.py`, its test and the
new design page all discuss it at length. **A raw-text version would have fired on its own
documentation.** The remedy already existed — `tools/python_code_text.searchable()`, which blanks
comments and prose strings — and the third mutation above is the proof it is load-bearing rather
than decorative: remove the routing and the fixture leg reds on the file that merely *describes* a
headed launch.

The second refusal was subtler. One walk with a suffix branch still reads `.py` as text as far as
the census is concerned, and the census is right: a branch is not a guarantee. Python and JS are now
walked by separate globs, so the text scan provably never receives Python.

## 5. Where it is written down

`docs/design/PIXEL_VERIFICATION_ON_THIS_MACHINE.md`: the measured launch table, the two conditions,
`DISPLAY=:0` as the thing to actually do, and the note that every committed door runs the page's JS
in node's `vm` and touches no browser at all. Pointed at from the constant's comment and from the
control's own failure message, so it is reachable from the red rather than only by search.

## 6. What is still open

`firefox` and `webkit` remain absent. Same rule, unchanged: nothing launches them, so nothing
requires them, and the control above now covers chromium only. If cross-browser rendering ever
becomes a door, that is a new consumer and a new measurement — not an extension of this one by
analogy.
