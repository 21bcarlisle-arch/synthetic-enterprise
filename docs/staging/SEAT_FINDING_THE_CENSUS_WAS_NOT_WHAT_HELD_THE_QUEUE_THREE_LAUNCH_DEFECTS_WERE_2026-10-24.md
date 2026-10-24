**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The census was not what held the queue: it ended at 06:18Z and every job then failed in minutes, for three separate reasons (2026-10-24)

## The premise, re-measured

The draw said the nightly HEAD-green census (pid 83098) was starving the queue, and asked whether
it could restart before the queue drained. Its journal says it cannot:

- `head-green-census.timer` fires once a day, `OnCalendar=*-*-* 03:30` with up to 10 min of random
  delay. The last seven runs took 3h19m to 4h50m of wall time, with a peak of 8.8 to 11.5 GB (the
  two 4-second runs on 20 and 22 Oct had nothing to do).
- This morning's run ended at 07:18:47 BST (06:18Z). The next starts at about 03:32 GMT on 25 Oct.

So the census holds the box for about 4 hours a night, and between runs it is about 20 hours away.
**Accepted, not changed.** Making it yield to queued experiments would buy at most four hours a
night, and would cost the only unscoped suite run. Nothing in `background/resource_headroom.py`
or `tools/head_green_census.py` was edited.

## What actually happened after 06:18Z

All the queued launches went ahead between 06:21 and 06:25Z. All of them died within minutes:

| Job | Died because | Whose |
|---|---|---|
| `s14clean-driver` (the section 14 thesis run) | `launch_long_job` refused all eight arms: a 75-minute arm is over the 60-minute line and `drive.sh` passed `--question` but no `--why-not-minutes` / `--would-change`. The driver exited with status 4: no rc, no grade. | the driver script |
| `c30-s61101..61103` A/B/C (nine arms) | `DwellingNotDrawn: 'SYN-2016-011' is supplied but the world drew no dwelling for it`. All nine arms, at worktree `0481ad381c` with `SE_POPULATION_SEED=611xx`: the cast and the dwelling draw disagree once the book seed is not the default. | world (`simulation.live_population.live_dwellings`) |
| `crisis-overlay-arm-70424-387e48132` | `SE_POPULATION_SEED=70424 refused`: the seed is not in `varied_population_draw_activation.json` (EP17, R13 curriculum, the director's to give). | refused by design |

The order the draw asked for was already set: `c30-seeds-out/chain.sh` waits on the driver's pid.
But the driver died at once, so the chain was released straight away. **The order held. The thesis
run never computed.**

## What was done

1. **`drive.sh` now states its case.** It passes `--why-not-minutes` and `--would-change` (from
   prereg §3) on each arm. The refused copy is kept as `drive.sh.0622-refused`, and its log as
   `drive.log.0622-refused`.
2. **The dead driver was relaunched** as `s14clean-driver`. The launch register had it as DIED, so
   this is a relaunch, not a second launch.
3. **A fourth defect, found while relaunching, is fixed in `tools/wait_for.py`.** The driver's
   `wait_for --pattern c30-seeds-out` matched no arm. It matched **two claude sessions whose
   prompts discussed those arms**: this worker, and the seat session that grades C30. So the
   driver would have waited until both sessions exited, and those can run for hours.
   `_is_probe_noise` now drops a process whose argv[0] is `claude`, because that argv is the
   prompt. Anything the session runs is its own process and still matches. The test is
   `test_an_agent_session_whose_PROMPT_names_the_pattern_is_not_the_subject`. The mutation
   (clause off) reds it.
4. At 06:29:31Z the driver passed both waits, found the prereg on origin (`6891c01e24`) and queued
   seed 2 `flat`. The only thing holding it was "landings come before experiments": another lane's
   commit gate, which is by design. It follows each arm in turn. The C30 arms do not compete,
   because all nine are dead.

## Still open

- **The C30 seeds cannot run on any non-default book until the dwelling draw covers the whole
  cast.** That is a world defect and needs its own atom: the cast at seed ≠ 20260724 supplies a
  founder that `live_dwellings()` did not draw. The seat session that grades
  `grade-c30-letter-refix-across-book-seeds` is waiting on artefacts that will never appear. Its
  DO NOT DRAW gate should cite this finding.
- **The crisis-overlay arm at seed 70424 needs the director's EP17 activation**, or a re-take on the
  default book.

## How to reverse

- `drive.sh`: `cp /var/tmp/se-s14clean-out/drive.sh.0622-refused /var/tmp/se-s14clean-out/drive.sh`,
  then `systemctl --user stop longjob-s14clean-driver`.
- `wait_for`: revert the `head == "claude"` clause and its test, in the commit that carries this
  finding.
