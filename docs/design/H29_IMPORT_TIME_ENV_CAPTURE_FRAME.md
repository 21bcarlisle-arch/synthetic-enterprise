# H29 — import-time env capture / wake-key test isolation: FRAME

**Atom:** `H29_import_time_env_capture_test_isolation` (lane `H_harness`, dial 3, L0→L2, `loop_stage: idle`)
**Stage:** FRAME (fix design + blast radius). **BUILD is epoch-gated — this doc designs it, it does not build it.**
**Date:** 2026-07-29 (worker tick). Supersedes the REGISTERED note's mechanism; carries the DISCOVER refutation forward.

---

## 0. Why this doc exists

The DISCOVER and FRAME output for this atom previously lived inline in the maturity map's
`simplifications` list — buried in a YAML string, unreadable as a design artefact and, more
importantly, invisible to `supervisor._atom_has_frame_doc`. That function marks an idle atom
FRAME-saturated only when an `evidence` entry under `docs/design/` with `FRAME` in its filename
resolves to a real non-empty file. With the analysis trapped in YAML the atom read as
**un-saturated** and was re-handed to the idle DISCOVER/FRAME draw every tick — the exact treadmill
`H23_frame_saturation_draw_marker` exists to stop, reached through a missing artefact rather than a
missing marker. This doc is that artefact; the matching `evidence` pointer retires the re-hand.

---

## 1. What was claimed, and what is actually true

The original REGISTERED note blamed **import order** — "whichever test imports `ntfy_utils` first
freezes the value". **That story is REFUTED**, and the refutation matters because it would have
aimed BUILD at the wrong target.

`tests/conftest.py` (lines 11-12) does `os.environ.setdefault("SE_WAKE_HMAC_KEY", ...)` at conftest
**top level** — deliberately, per its own comment, so it runs before any collection-time import. The
key is therefore *always* present in `os.environ` before any test module imports `ntfy_utils`.
Import order alone **cannot** produce a `None` key.

## 2. The real culprit — observed, not inferred

Exactly **one** test: `tests/background/test_model_facing_secret_scrub.py::test_worker_env_forgery_is_structurally_impossible`.

Reproduced this tick in 0.29s with a two-selector run:

```
pytest tests/background/test_model_facing_secret_scrub.py::test_worker_env_forgery_is_structurally_impossible \
       tests/background/test_ntfy_utils.py -p no:randomly
=> 4 failed, 21 passed          (RuntimeError at background/ntfy_utils.py:56)
```

**Control** — its sibling `test_worker_tick_env_strips_inherited_wake_key` (identical
`monkeypatch.setenv`, **no reload**) against the same target file:

```
=> 25 passed
```

So the differentiator is **the reload**, not the env-patching and not import order.

### Exact mechanism

The culprit test deletes all of `os.environ`, sets a scrubbed env, and calls `importlib.reload(nu)`
so `WAKE_HMAC_KEY` becomes `None` — *that is its actual purpose*, proving the worker cannot forge a
wake message. Then, in a `finally:` block, it calls `importlib.reload(nu)` again to "restore module
state for other tests" (line 89).

But a `finally:` block runs while the test function is **still on the stack**, and `monkeypatch`
undoes env changes in a **fixture finalizer** — i.e. *after* the function returns. The restoring
reload therefore re-reads the **still-scrubbed** env and restores nothing. `os.environ` is repaired a
moment later, but the module constant stays `None` for the whole remaining session.

This teardown-ordering claim was **demonstrated, not asserted**: proven independently outside the
repo tree (`/tmp/h29probe`, scratch, not committed) — test A emulates the culprit and asserts
`os.environ.get("SE_WAKE_HMAC_KEY") is None` *inside its own finally-restore*; test B then asserts
`os.environ` is back to the real key **while** `nu.WAKE_HMAC_KEY` is still `None`. Both pass.

---

## 3. The class is THREE shapes — a fix aimed only at shape (1) leaves the bug alive

This is the R10 argument for why an instance fix does not close the atom. All three verified against
disk this tick.

**(1) MODULE-LEVEL CAPTURE.** A full sweep of `background/*.py` for module-level env binds returns
exactly **four** sites:

| Site | Constant |
|---|---|
| `background/ntfy_utils.py:35` | `NTFY_TOPIC` |
| `background/ntfy_utils.py:44` | `NTFY_AUTH_TOKEN` |
| `background/ntfy_utils.py:45` | `WAKE_HMAC_KEY` |
| `background/file_api.py:48` | `_API_KEY` |

`file_api.py:48` is the **sibling half of the class** (checked at `:52` and `:300`) — same
rotate-needs-restart defect, currently unexercised by this failure, flagged per the standing
audit-the-sibling rule.

**(2) FROM-IMPORT VALUE COPY.** `background/director_input_log.py:44` does
`from background.ntfy_utils import NTFY_TOPIC, WAKE_HMAC_KEY, verify_wake_message`, taking its **own
frozen copy**, used at `:117` and `:175`. `background/ntfy_responder.py:82` from-imports
`NTFY_TOPIC`/`NTFY_AUTH_TOKEN` the same way. **A reload of `ntfy_utils` does not update these
copies, and a lazy accessor added to `ntfy_utils` alone would NOT fix `director_input_log`** —
precisely why the instance fix fails the R10 bar.

Every other `background/` consumer already lazily imports the *functions*
(`action_needed`, `inbound_ratification`, `gate_authorization`, `director_authority_channels`,
`reconcile_watch`, `supervisor`, `run_queued_tasks`) and is unaffected.

**(3) TEST-SIDE OVERRIDE.** **24** call sites across exactly **five** test files
(`test_director_authority_channels`, `test_ntfy_responder`, `test_director_input_log`,
`test_gate_authorization`, `test_ntfy_utils`) do `monkeypatch.setattr(<module>, "WAKE_HMAC_KEY", ...)`.

> A **pure** lazy accessor that reads `os.environ` at call time would silently **ignore all 24** of
> those `setattr` overrides. The tests would not error — they would just stop testing what they
> claim to. That is a **fail-open per R15**, and strictly worse than the current loud failure.

---

## 4. Recommended shape

A module-level accessor (e.g. `_wake_key()`) that **prefers an explicit module-level override when
one is set** and otherwise reads `os.environ` at **call** time — with `director_input_log` switched
from a value from-import to calling that accessor.

This keeps all 24 `setattr` sites meaningful, removes the need for any `importlib.reload` in tests,
and makes the culprit test's `finally:` block **deletable rather than reordered**.

## 5. R15 requirement for BUILD — the control must be able to FAIL

The named defect is *"the 4 wake-signing tests pass alone and fail after the scrub test."* The
mutation test is therefore the **two-selector command in §2**, which must go **RED on the pre-fix
tree and GREEN after**.

> A fix verified only by a full-suite green is **NOT acceptable evidence** — full-suite ordering is
> exactly what is in question.

## 6. SAFETY — the one wall here

**Do NOT weaken the not-set guard in `sign_wake_message`, nor the fail-closed `None` return in
`verify_wake_message`.** Those are real safety controls — they are what makes worker-side wake
forgery structurally impossible, and the culprit test exists to prove it.

This stays a **TEST-VISIBILITY defect, not a live-signing defect**: the live daemons each import
`ntfy_utils` in their own process *after* `.env.ntfy` is loaded, and never reload, so no running
signer is affected.

---

## 7. State after this FRAME

DISCOVER and FRAME are both complete. The only remaining path to `level_target: 2` is **BUILT code
the epoch gate defers**, so the atom is now intrinsically FRAME-saturated (this doc, listed in
`evidence`) and will not be re-handed to the idle draw. It re-enters via the BUILD draw when its
gate opens and `loop_stage` flips off `idle` — no orphan transition, no permanent hold.

`level_current` stays **0**: the L1/L2 maturity bar is *built in some real form* / *mechanically real
and mutation-tested*, and nothing is built. Claiming L2 for analysis alone would be an unearned
level.
