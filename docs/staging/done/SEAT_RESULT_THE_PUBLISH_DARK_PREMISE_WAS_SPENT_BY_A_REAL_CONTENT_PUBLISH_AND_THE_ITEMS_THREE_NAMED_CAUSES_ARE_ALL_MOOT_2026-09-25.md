**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** unminted

# RESULT — the publish-is-dark premise was spent by a real content publish 34 minutes before the draw

The drawn LANE 0 item was *"publish-is-dark-until-a-clean-publish-is-recorded"*. It named its own
finish condition and it is met. Nothing was built this turn, because the work it asked for does
not exist any more.

## The item's own exit test, re-measured before any work

The item opened with an instruction I followed literally: *"FIRST read `last_clean_publish` in
`docs/observability/.publish_gate_state.json`: if it has advanced past 2026-09-21T18:15:57Z this
item is FINISHED."*

| the item's claim | measured 2026-09-25T10:2x UTC | verdict |
|---|---|---|
| `last_clean_publish` stuck at 2026-09-21T18:15:57Z | `1790329710.204636` = **2026-09-25T09:48:30Z** | **spent** (+87.5h) |
| `episode_failures` 60 and climbing | `episode_failures: 0` | **spent** |
| the gate holds a named red | `total_red: 0`, `blocking_tests: []`, `wedge_since: None`, `alerted_at: None` | **spent** |

The item was explicit that it had *"twice graded this by whether a named test went green and been
wrong twice"*, so I did not stop at the state file. Three independent oracles agree:

- `publish_freshness.is_publishing_down()` → **False**; `describe()` → *"content publishing: live
  — figures reached origin 0.6h ago"*; `snapshot()` → `state: publishing`, `queue_depth: 0`,
  `consecutive_failures: 0`, `as_at_utc: 2026-09-25T09:48Z`.
- `process_run_complete.pending_run_complete_markers()` → **0**. The *"four completed runs queued
  behind this"* have drained.
- The publish is a real commit, not a heartbeat: `19e60c443` *"Auto-process run complete: report +
  LATEST.md + site/ (git=33650edec, net=£166,705)"*, 2026-09-25 10:48:27 +0100, and
  `git merge-base --is-ancestor 19e60c443 origin/main` → **YES**.

The third is the one that matters, because the surrounding commits are
`chore(liveness): publish heartbeat while sim output unchanged` and a queue that only ever
heartbeats would satisfy the first two oracles while publishing nothing a reader can check.
`site/data/dashboard.json` carries `git_hash: 33650edec` and `net_margin_gbp: 166705.24`, which
is the same run and the same figure as the commit subject. **Figures reached the reader.**

I also read `liveness_surface_refusal` (`None`) rather than the `held_refusal` summary, because
this state file has two refusal fields and the stale one is the one readers believe.

## The item's three named causes are all moot, and one of them was never a defect

1. **The module-snapshot restart.** No restart was needed and none was performed: the recorder's
   `cause: unattributed` claim cannot be tested against a cycle that did not refuse.
   `.last_publish_cause.json` still holds `gate_refusal` against `7ef75772d` at
   2026-09-25T08:48:43Z — an hour BEFORE the clean publish, so the last recorded cause simply
   predates the success rather than contradicting it.
2. **The `commit-msg does not exist in the resulting tree` sweep.** Moot for this item's purpose.
   It is a real class question and is not discharged here — it is left for the lane that owns
   `tools/surgical_land.py`, stated rather than quietly dropped.
3. **`[startup-anchors] REFUSED`.** Did not refuse the cycle that published.

## One thing I checked and did NOT file as a finding

`.last_content_publish.json` still stamps `1790014556` = 2026-09-21T18:15:56Z, i.e. it did **not**
advance when content reached origin this morning. That reads like the classic stale-stamp defect
and it is not one. `publish_freshness.last_published_ts` takes `max(on_origin, stamped)` over two
sources and documents why: *"each can only MISS a publish, never invent one."* Git's answer won,
the verdict is correct, and the missed stamp changes no reader's number. Recording the negative so
the next session does not pay to re-derive it.

## Disposition

`--premise-spent` against `19e60c443`, then `--release`. The PATH CHECK's own reading agreed in
advance: four of the item's five paths were already `already landed`, and the fifth
(`.publish_gate_state.json`) is daemon-written state, not work to land.

The class this is the Nth instance of: **a drawn item's every claim about the tree is an
un-re-asked prediction**, and here the premise expired 34 minutes before the draw was handed out.
