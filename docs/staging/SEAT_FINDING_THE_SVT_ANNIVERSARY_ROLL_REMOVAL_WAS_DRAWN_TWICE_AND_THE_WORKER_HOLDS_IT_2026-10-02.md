**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `EP1_clv_three_horizon` (upstream world fidelity)

# The SVT anniversary roll removal was drawn twice, and the worker holds it

Claim `remove-the-svt-anniversary-routes-departure-roll-now-the-pb4-swap-is-on-origin`. The isolated
seat executor (pid 110615, started 00:49) drew it. The scheduled worker (pid 110335, started 00:48)
had already drawn the same change as `remove-the-svt-anniversary-departure-roll`, one minute earlier.
The worker confirmed by cross-session message that it is building it on the shared tree.

**The premise is not spent.** c3939e7b1 (the PB4 swap) and 7f4cb24a9 (the worker's pre-registration
and decided design, `docs/staging/records/WORKER_PREREG_THE_SVT_ANNIVERSARY_CARRIES_NO_DEPARTURE_ROLL_2026-10-01.md`)
are both on origin. The roll itself is still in `simulation/renewals.py` at origin/main 89a4611e2.
The PATH CHECK graded two paths `already landed`, but those are the item's INPUTS (the finding and
the unchanged module), not what it is meant to produce.

**Disposition:** `--release` on the seat id. The work stays with the worker's id. No world code was
touched here, and no run was launched, so the worker's one-variable pair cannot pick up a second
change from this lane.

**The shape again.** This is the third time on 2026-10-01/02 that one LANE 0 item has been minted
under two ids, and both a tick and the seat executor drew it within minutes. See the two PB4 swap
notes beside this one. The duplicate-work check caught it each time, and each time it cost a turn
to read.
