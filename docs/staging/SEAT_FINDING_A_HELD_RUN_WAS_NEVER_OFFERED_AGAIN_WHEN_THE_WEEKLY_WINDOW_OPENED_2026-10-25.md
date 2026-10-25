# SEAT FINDING: a run held mid-week was never offered again when the weekly window opened

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

## What was found (re-measured 25 Oct, against the shared tree)

The four 904a091f7b markers of 24-25 Oct sit in `docs/staging/done/`. Each was HELD by the weekly
window: they carry no did-not-land tag and no publish tag, and `staging/` holds no marker. Neither
`process_leftover_run_markers` nor anything else ever looked at them again. The premise was not
spent. 904a091f7b being on origin says nothing about whether its runs were offered.

## What landed

The HOLD branch tags the archived marker `publish-held`. The worker's sweep offers the newest held
run once, when the window is open and nothing is pending. Design and guards:
`docs/design/PUBLISH_DECOUPLING.md` "A HELD RUN WHEN THE WEEKLY WINDOW OPENS". Control:
`tests/background/test_a_held_run_is_offered_once_when_the_weekly_window_opens.py`. Four mutants
were tried and all four fire: the offer call removed, the once-only guard removed, the window
guard removed, and the hold tag write removed.

## Read at real inputs, and the one surprise

Run read-only over the shared done/, the selector refuses with "not held", because the legacy
markers predate the tag. Given a tagged copy of the 03:16Z marker and an open window, it still
refuses: **`run_output_latest.json` is not any 904a091f7b run.** It is byte-identical to
`run_output_b2bc3d8da5_20261025T1230Z.json` (13:31Z), and that run has no marker. This mechanism is
right to refuse, because offering the 03:16Z marker would publish a mix of two runs. For this
Monday, the one-shot timer `mondays-window-marker-20261026` keys on latest's own commit and stays
the route. Leave it armed.

## Still open, not fixed here

- The supersession frontier counts a held marker as published. That is harmless for ordering,
  because the newest marker dominates. It is not a true statement, and it shares a root with the
  re-arm doc's filed frontier fault.
- A run that writes `run_output_latest.json` without a marker is invisible to every publish route.
