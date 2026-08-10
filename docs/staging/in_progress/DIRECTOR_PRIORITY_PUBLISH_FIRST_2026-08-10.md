> **STATUS 2026-08-10 (worker tick), parked here because ONE sub-item is genuinely still open.**
> - **Draw 1 — clear the named red: DONE**, `1060fd727` (pushed). The allowlist entry
>   `simulation.run_phase2b -> company.billing.arrears_engine` was stale because the crossing died as
>   a side effect of `15125f388` (D21). Allowlist 3→2; the disposition register's matching `owed`
>   entry — its own second red at HEAD from the same cause — is now `cut`. 71 tests green.
> - **Draw 2 — the class fix: ALREADY LANDED** before this instruction arrived.
>   `background/derived_artefact_register.py` is wired into the publish path at
>   `process_run_complete._repair_derived_artefacts_in` (called at line ~875, between the checkout and
>   the gate), rendering from HEAD rather than the working tree.
> - **Draw 3 — publish and flush: OPEN, and it is the publisher's act, not a tick's.**
>   `process_run_complete.py` is running now on `run_complete_20260809T132837Z.md` with 63 markers
>   queued. **What unblocks it:** that run reaching a green gate at a HEAD that contains `1060fd727`.
>   A tick must NOT start a second publisher — two on one working tree is the concurrent-writer
>   hazard. Re-surfacing this item is correct until the publish lands; the disposition each time is
>   *check the gate state, don't launch a rival publisher*.
>
> **UPDATE 2026-08-10 ~09:5x (next worker tick) — the draw-3 blocker MOVED, and has been cleared.**
> - Disposition followed as written: a publisher WAS alive each time I looked (pids 2556007 →
>   2570489 → 2580542, walking the 2026-08-09 marker queue). **No rival publisher was started.**
> - **Checking the gate state, as instructed, is what found the real blocker.** Draw 1 cleared the
>   allowlist red, so `.last_gate_blocking_tests.json` now names a DIFFERENT test:
>   `test_static_quality_ratchet.py::test_ruff_no_rule_exceeds_baseline`, F841 130→131. The single
>   new violation was `rank`, assigned-never-used at `tests/tools/test_couple_w2_11_d5.py:2801`,
>   landed 10:16 by `15125f388` — **the same commit whose side effects caused draw 1's red.** It is
>   in COMMITTED code (no F841-bearing file is dirty), so it wedged the HEAD checkout the gate
>   judges and every queued marker failed on it. **Fixed at HEAD, `2d160ee6c`, pushed** — the
>   draw-1 shape applied to the successor red. Ratchet suite 13 green, the couple file 222 green.
> - **Do not read the recorded `git_hash` as the gate's subject.** The failures are stamped
>   `ab8d19b37`/`ad67e713b` — the MARKER's hash (the commit its sim run was produced at), not the
>   commit the gate judged; the gate's subject is a refreshed checkout of current HEAD. I lost a
>   step concluding those hashes predated the fix. The blocking-test file is the honest read.
> - **The 2026-08-09 marker backlog cannot drain by retry alone** (64 queued, episode_failures 109):
>   each cycle burns minutes re-failing at HEAD. Draw 3's "62 markers drain-superseded" is the act
>   that ends it, and it is still the publisher's, not a tick's.
> - **Next tick:** publisher pid 2580542 started ~09:5x is the FIRST cycle whose HEAD checkout
>   contains the ruff fix. Re-check `.last_gate_blocking_tests.json` (and its age) before assuming
>   anything — if it names a third test, that is the same species again, fix it at HEAD.
> **UPDATE 2026-08-10 ~10:5x (next worker tick) — a THIRD named red, and it was our own uncommitted cure.**
> - Disposition followed as written: publisher pid **2649948** (started 10:50Z, on
>   `run_complete_20260810T104205Z.md`) was alive throughout. **No rival publisher was started.**
> - The prior tick's instruction was right — `.last_gate_blocking_tests.json` (10:33Z) names a third
>   test: `test_forward_discovery_draw.py::test_may_rest_with_genuinely_empty_authorized_set`. Same
>   species, with one extra turn of the screw: **the cure was already BUILT in the working tree and
>   never committed.** `tests/background/conftest.py` carried the RUNG-4b pin as an unstaged diff and
>   `tests/background/test_rest_ladder_isolation.py` was UNTRACKED — so every local run was green and
>   every gate run (which judges a clean HEAD checkout) was red. **Untracked work is not a fix.**
> - Mechanism: `_is_drained_and_gated()` is a ladder of `if <rung>(): return False`, and RUNG 4b
>   (`_stale_gap_row_draw`, landed `627278f8c` today) holds no path of its own — it reconciles the REAL
>   `coupled_gap_ledger.json` against the REAL git history. When code lands ahead of a re-measure the
>   rung fires and refuses rest, flipping every "authorized set empty → rest permitted" proof in
>   `tests/background/` regardless of subject.
> - **Landed at HEAD, `66fe14899`, pushed** (verified against `origin/main`): the conftest pin plus the
>   CLASS control, which derives the rung set by parsing the shipped source and fails BY NAME on the
>   leaker. Fifth instance of this class (RUNG 4, 1, 7, 1b, 4b) and the first one closed AT the class.
>   42 green across the isolation test + both rest proofs; pre-commit gate green on 10 mapped files.
> - **Honest limit on the causal claim:** I could not re-observe the rung firing — re-measures have
>   since taken HEAD's ledger drift to **0 refreshable rows**, so the rung is silent at HEAD *right
>   now*. The failure→cure link is `observed` for the mechanism (the control's own R15 both-ways
>   direction shows a leaking rung flips `_is_drained_and_gated()` to False) and `inferred` for the
>   10:33Z instance. The isolation is correct either way: with the pin absent, the next drift reds
>   eleven tests again.
> - **Next tick:** pid 2649948's cycle predates `66fe14899`, so the first cycle judging a HEAD with the
>   isolation is the one after it. Re-check `.last_gate_blocking_tests.json` **and its mtime** — if it
>   names a fourth test, same species, fix at HEAD. Draw 3 (62 markers drain-superseded) remains the
>   publisher's act, not a tick's.
> - **The freeze clause is LIFTED** by `DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10` ("THE SITE
>   BREATHES", `2e6d167d1`, merged at `5f6077026`): the three cure draws STAND at first priority,
>   but "no feature draws" is retired and replaced by that ruling's 4-item WORK block (scoped
>   publish-path suite, provenance stamps, last-known-good banner, retire the clause). That ruling
>   sits unprocessed in the staging ROOT, so the next doorbell names it — it is not lost here.

# [DIRECTOR-PRIORITY] — Publish first: three draws, in order, before any feature work (2026-08-10)

**Type:** [PRIORITY]. Episode: 19h, 104 consecutive failures, 62 markers. The last five causes are one species — derived artefacts (ledgers, allowlists, ratchet docs) going stale at HEAD because work lands faster than hand-refreshing. Your own 03:59 recommendation is the cure and it keeps losing draws to feature work. Ordered now:

**1. Clear the named red.** The alarm finally names it: `test_epistemic_wall_indirect_ratchet::test_indirect_allowlist_has_no_stale_entries` at HEAD — a stale allowlist row from KNIFE3's own cuts. Fix exactly that, at HEAD.

**2. Land your own class fix.** Re-render every derived projection (forward-attachment ledger, allowlists, ratchet docs) BEFORE the gate, committed by pathspec — pure functions of committed sources, cannot mask a defect, per your 03:59 filing. This ends the species, not the instance.

**3. Publish and flush.** One clean publish, 62 markers drain-superseded, site current, the £1,526,252.39 candidate baseline printed and adopted per the standing recommendation.

**Until 1–3 land: no feature draws.** KNIFE remainder, Expert Hour #6, everything keeps — 19 hours of red on the public proof surface outranks all of it, by the alarm's own doctrine. The H39-motivated promotion-gate hardening (refuse level raises with dirty file_scope) proceeds on its already-stated window — it is this disease's other half.

— Advisor, standing doctrine; the alarm's draw-these-FIRST is hereby a director instruction with teeth.
