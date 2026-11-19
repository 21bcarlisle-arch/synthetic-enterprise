**Severity:** LATENT · **Lane:** B_commercial · **Atom:** `unminted`

# The book builds again, on a commit that carries c71d2521d (19 Nov, about 19:15Z)

Claim `the-book-builds-once-the-primary-checkout-rejoins-origin`. Its done condition is met. It was not met by
this turn's work: the fork landing that the item named had already finished.

## What was read

- **The fork is closed.** `git rev-list --left-right --count HEAD...origin/main` gives `0 0` after a fetch.
  `a2ed7654e0` is an ancestor of origin/main. The surgical_land that the item named (pid 2812152) is gone. It
  landed as `67d454905c` ("The fork with origin is closed").
- **sim-runner stopped deferring.** At 18:34Z it deferred for a pending landing. At 18:40Z it deferred because
  the skip-pair read had not landed; `2701c80e96` removed that row. At 18:45:02Z it logged
  `Starting run — git=67d454905c, json=run_output_67d454905c_20261119T184502Z.json`, pid 3127319.
  `c71d2521d` (W3_3) is an ancestor of `67d454905c`.
- **The 0.12 pair's watcher is waiting for this book.** `vtc-cut012-watch` is active
  (`/var/tmp/box-plan/arm_cut012.sh`). Leg 1, skip0's read, passed at 10:31Z. Leg 2 polls
  `docs/observability/.sim_producer_state.json` every 600 s for a success after arming whose `git` carries
  `c71d2521d`. sim-runner writes that file's `git` from HEAD at completion. HEAD is on main, so any HEAD from now
  on carries c71d2521d. When this book succeeds, leg 2 passes and the watcher waits for `box_free.py`. Its deadline
  is 2026-11-24T00:00Z.
- **Not a new fault:** the `[ERROR] Committee invocation failed: the live risk committee is retired` lines in this
  run also appear 28 times in the 18 Nov books.

## What is still open (not this claim's)

The book has to finish, and then the box has to come free before 24 Nov. Both are watched by `vtc-cut012-watch`,
which gives up with a named reason. Its log is `/var/tmp/box-plan/vtc-cut012-watch.log`.

## Draw-time checks, answered

- `land-the-era5-store-increments` is different work. It shares the redesign page, but not this subject.
- The continuation `d48-the-182-day-estimate-hold-gets-a-source-or-goes` is different work, and another lane is
  landing it now. It does not carry the rest of this item.
- The advisor ruling `DIRECTOR_RULING_REPO_STAYS_PUBLIC_AND_THE_WEBSITE_GOES_BEHIND_A_LOGIN_2026-11-19.md` stays
  in the advisor root on purpose. Its record
  (`SEAT_RECORD_THE_SITE_LOGIN_WHAT_LANDED_AND_WHAT_STAYS_PUBLIC_2026-11-19.md`) keeps it open until the gate is
  proved. The steps left are the director's Zero Trust sign-up and his answer on D11. Both are raised in
  `for_the_director`.
