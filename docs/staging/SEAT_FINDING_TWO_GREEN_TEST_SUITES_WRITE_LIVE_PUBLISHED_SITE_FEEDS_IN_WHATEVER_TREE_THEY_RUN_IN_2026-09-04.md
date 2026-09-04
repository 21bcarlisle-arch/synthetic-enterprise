**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — two green test suites write LIVE published site feeds in whatever tree they run in

**Found:** 2026-09-04, delivery seat, by accident: `promote_worktree_landing` refused my landing
because the worktree had uncommitted tracked changes I had not made. The refusal named the four
files. **A refusal that names its subject is how this was found** — the same property the commit
this sits beside was repairing, one layer down.

LATENT and not higher, and I checked rather than assumed: **nothing published is wrong.** See
"What did NOT happen" below.

---

## What they write

Reproduced in a clean `git archive HEAD` extract, checksums before and after, `python3 -B`:

| suite | verdict | live files it rewrote |
|---|---|---|
| `tests/background/test_process_run_complete.py` | **83 passed, 1 skipped** | `site/data/explore_carbon.json`, `site/data/weather.json` |
| `tests/background/test_publish_gate_alert.py` | **green** | `site/data/director_reserved.json` |

Both suites pass. Nothing in either result says a published feed was overwritten. The write is a
side effect of the module under test doing its real job — `process_run_complete` genuinely
generates those feeds (`process_run_complete.py:6752`, *"Generated site/data/explore_carbon.json"*),
and the tools it calls resolve their output from `__file__`:

```python
# tools/generate_explore_carbon.py
INTENSITY_FEED = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"
OUT_PATH       = PROJECT / "site" / "data" / "explore_carbon.json"
```

So the suite writes the real feed of whichever tree it is run from.

## The shape, and it is the catalogued one

`test_process_run_complete.py` **already knows about this hazard** and already fixed it — once:

```python
# generate_dashboard_json writes to the REAL site/data/dashboard.json (hardcoded path
# inside generate_dashboard_data.py) — mock it to avoid corrupting the live dashboard
monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
```

One live-writing generator identified, understood, mocked, and commented. **Its three siblings on
the same publish path were left live.** That is this repo's own *"a fix that removes one cause of a
silent absence leaves the absence itself"*, and the sibling-grep rule it has already paid for:
when one call site is guarded because it writes a live artefact, every call site that writes a live
artefact needs the same question asked of it.

`test_publish_gate_alert.py` is the same shape one layer up. It **does** redirect the register:

```python
monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
```

— and the *site feed generated downstream of the register* is still the live one. The guard was
placed at the layer the author was thinking about, and the published surface is one layer past it.

## What the fixture text actually looks like when it lands

From my worktree's `site/data/director_reserved.json`, written 11:47:40Z by that suite. This is the
**director-reserved feed** — the page that tells the director what is waiting on him:

```
"item_id": "publish_gate_wedged",
"what": "... (rc=77, git=abc1234). EPISODE: wedged since 1970-01-01T00:00 UTC -- 0h00m
         and 3 consecutive failures in THIS episode ... Markers pending: 0."
"how":  "... BLOCKING TEST (gate subject abc1234): FAILED tests/background/
         test_derived_artefact_register.py::TestStaleness::test_staleness_fires_for_
         EVERY_registered_artefact ..."
```

`git=abc1234`. Wedged since **1970-01-01** — epoch zero rendered as a date. Two named "blocking
tests" that are fixtures. Had this been committed, the director's own reserved-items page would
have carried a fabricated wedge, an invented commit hash, and two innocent test node ids, in the
confident register of a real alarm.

## What did NOT happen, checked rather than assumed

**The fixture text is not in the shared tree and not in history.** Both checked directly:

```
$ grep -o "abc1234\|1970-01-01" site/data/director_reserved.json          # shared working copy
$ git show HEAD:site/data/director_reserved.json | grep -o "abc1234..."   # committed
(both empty)
$ python3 -c "...open_count 1; ['executor-wall_escalated-f13e76f1']"       # a real item
```

So **no published figure is wrong and no reader saw this.** The blast radius was my own isolated
worktree, which is exactly what the isolation is for.

## Why it is still worth a finding, given that

Because what stopped it was arrangement, not a control:

- the publish gate runs its suite in a **throwaway checkout** (the worker log for this cycle says
  so explicitly), so the gate's own runs cannot corrupt the shared tree — a real mitigation, and
  it covers the highest-frequency caller;
- but `CLAUDE.md` instructs every lane to pre-run gates in the shared tree before committing, and
  `test_process_run_complete.py` sits inside the publish gate's own 198-file blocking set;
- and the publish daemon regenerates and commits `site/` output that it did not produce, which is
  already a filed finding in this repo.

Compose those three and there is a route from *"a lane ran the tests before committing"* to
*"fixture text is committed to a published feed"*, with nothing in between that would go red. No
suite reports it, because both suites pass.

## What I could NOT attribute, and am not claiming

My worktree's `docs/market_data/grid_intensity_feed.json` also lost **288 records (1247 → 959)**
during this turn. I could not reproduce that from any of the eleven suites I ran — in the clean
extract the feed was byte-identical after all of them. More than one thing was running in that
tree, so **I cannot yet say** what truncated it. Recorded as an open observation, not attributed,
and deliberately not folded into the reproduced result above. The file was restored from HEAD
(1247 records) before landing; nothing was lost.

## Recommended repair — NOT done here, and why

The honest fix is a `tmp_path` redirect for the three unmocked generators in
`test_process_run_complete.py`, and for the site-feed writer downstream of the register in
`test_publish_gate_alert.py`. But the *class* fix is the one worth having, and it is the one this
repo would ask for: `background/live_ledger_guard.py` already exists to refuse un-guarded writes to
live ledgers, and its ratchet is what caught the 75th observability writer. `site/data/` and
`docs/market_data/` are published surfaces with no equivalent, and a per-suite mock is exactly the
"fix the instance" move that leaves the next generator unguarded.

Not attempted in this turn: it needs a decision about whether the guard refuses or redirects under
pytest, which changes behaviour for every suite on the publish path, and that is more than can be
gated and landed safely alongside an unrelated repair. **Filed rather than half-built.**
