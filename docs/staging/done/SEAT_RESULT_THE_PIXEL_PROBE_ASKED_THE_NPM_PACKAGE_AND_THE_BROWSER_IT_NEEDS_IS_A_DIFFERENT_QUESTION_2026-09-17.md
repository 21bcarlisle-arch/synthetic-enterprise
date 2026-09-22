**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-pixel-probe-is-version-only-so-it-cannot-see-a-missing-browser-binary`)

# The pixel probe asked the npm package, and the browser it needs is a different question

**Filed 2026-09-17, delivery seat.** Prediction registered before the measurement:
`docs/staging/records/WORKER_PREREGISTRATION_WHICH_BROWSER_BINARIES_THE_PIXEL_PROBE_MUST_REQUIRE_2026-09-17.md`.
Follows `SEAT_RESULT_THE_MACHINE_NEVER_LOST_PLAYWRIGHT_..._2026-09-17.md` (landed `a689e9884`),
which established the previous alarm was a worktree-locality artefact and not a real loss.

---

## 1. The fail-open

`background/health_check.py::_check_pixel_verification_capability` ran:

```
npx --no-install playwright --version   ->   Version 1.62.0
```

That answers from the **npm package**. The npm package is not the browser, and only the browser
renders a pixel. Empty `~/.cache/ms-playwright` and the probe still reported "available" while every
real pixel check failed — a fail-open in a control CLAUDE.md treats as load-bearing (*"done means
the rendered value changed"*).

The gap was **live on this machine, latently**. Checked rather than assumed:

| Browser | `browsers.json` | On disk |
|---|---|---|
| `chromium` 1234 | `installByDefault: true` | **ABSENT** |
| `chromium-headless-shell` 1234 | `installByDefault: true` | present |
| `firefox` 1538 | `installByDefault: true` | **ABSENT** |
| `webkit` 2336 | `installByDefault: true` | **ABSENT** |
| `ffmpeg` 1011 | `installByDefault: true` | present |

## 2. The definition had to come first, and it is where the trap was

CLAUDE.md: *before measuring a thing, say what it is.* The obvious required set — `installByDefault`
— would have reddened the health check **today**, on a machine whose pixel checks all pass. That is
the same false-red class that had just cost a full Lane 0 item. So "required" is defined as **what
the pixel-verification path actually launches**, measured two ways:

- A tree-wide grep for `playwright` returns **three** files: `background/health_check.py`, its test,
  and `tests/background/test_egress_allowlist.py`. **No committed door launches a browser through
  Playwright** — pixel verification is done ad-hoc by sessions via `chromium.launch()`, headless.
- Live launch on this machine, with `chromium-1234` absent:

```
headless=true:  OK rendered=42
headless=false: FAIL browserType.launch: Executable doesn't exist at
                .../ms-playwright/chromium-1234/chrome-linux64/chrome
```

Both pre-registered predictions held. **Required set = `chromium-headless-shell` alone.** `ffmpeg`
is video recording, not pixel verification, and is excluded *despite being present* — requiring a
browser because it happens to be on disk is keying the control to today's answer.

## 3. The headed gap is real, and deliberately not alarmed

A **headed** launch fails on this machine today. Nothing in the tree asks for one, so it is LATENT,
not live. It is recorded here and in the constant's own comment rather than wired into the alarm:
asserting a capability nothing consumes manufactures exactly the red this lane has already paid for
twice. The remedy if it ever becomes live is one line — add `"chromium"` to
`REQUIRED_PIXEL_BROWSERS` — and `npx playwright install chromium` fixes the machine.

## 4. The fix

The probe now runs `playwright install --dry-run` and **stats the browser directory** Playwright
itself resolves. This respects the docstring's no-launch rule rather than working around it: no
socket, no browser, **0.6s measured** — the same order as the version check it replaces. It
subsumes the old check, because the package must resolve before the subcommand runs at all.

Playwright's own resolved path is parsed rather than re-derived. The cache root moves with
`PLAYWRIGHT_BROWSERS_PATH`, and the directory name is not the browser name
(`chromium-headless-shell` → `chromium_headless_shell-1234`, underscores, plus a revision that
changes on every version bump). A second implementation of that logic would be wrong the first time
either changed, and wrong in the direction that reports a present browser missing.

## 5. The control, over the whole partition, mutation-proven

`PLAYWRIGHT_BROWSERS_PATH` relocates the cache, so **both legs run for real — neither is mocked**:

- **missing leg:** empty tmpdir cache → reports unavailable, naming the browser and the path.
- **available leg:** the real cache → reports available.

A guard that refuses everything passes the missing leg alone, which is why the pair is one control.
Both directions fire:

| Mutation | Result |
|---|---|
| invocation reverted to `playwright --version` | missing leg **REDS** (version answers `1.62.0` whatever the cache holds) |
| `REQUIRED_PIXEL_BROWSERS` widened to include absent `chromium` | available leg **REDS** |

A third leg asserts every required name is one Playwright still reports on — the fail-closed
"absent from `--dry-run`" branch is correct when a browser is dropped and indistinguishable from a
typo or a rename, either of which would wedge the health check permanently red for a reason no
reader could act on.

`tests/background/test_health_check.py`: **46 passed.**

## 6. Method note, filed against myself

The first draft of this change was written to `/home/rich/synthetic-enterprise` — the shared tree —
because bare-path greps in a linked worktree resolved against the main checkout, and the edit
followed the grep's path without re-anchoring. Caught by a line-number mismatch between two reads of
"the same" file: **the two copies were at different commits**, which is what made the discrepancy
visible at all. Reverted before anything was staged; the shared tree's `health_check.py` went back
to clean. The general shape — *a linked worktree makes every unanchored path ambiguous, and the tell
is two reads of one file disagreeing about line numbers* — is worth more than the instance.
