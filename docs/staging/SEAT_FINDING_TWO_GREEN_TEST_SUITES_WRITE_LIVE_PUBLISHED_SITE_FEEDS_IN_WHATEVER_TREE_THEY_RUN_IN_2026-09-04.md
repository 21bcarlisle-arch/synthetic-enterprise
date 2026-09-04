**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

> **CORRECTED ON THE SAME DAY, BY ME, ONE COMMIT LATER — read the correction at the bottom
> before acting on anything above. The observations hold; the FINDING does not. `site/data/`
> being writable by tests is a measured and deliberate decision from 2026-08-10, and I filed
> this without looking for it. Downgraded LATENT → RECORDED.**

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


---

# CORRECTION — this re-litigates a settled measurement, and I should have found it first

**Written 2026-09-04, by the seat that filed the above, ~20 minutes after landing it, before any
other lane had to spend time on it.** Kept beside the claim rather than deleted: a finding whose
withdrawal is visible is worth more than one quietly removed, and the reason it was filed is the
more useful half.

## What refutes it

`tests/production_surface_guard.py` — THE SINK GUARD, written to the director's own instruction
*"the tests-writing-into-production-surfaces class ... that's three instances I know of. Fix the
class."* Its docstring answers this document directly:

> **`site/data/` stays file-scoped, on purpose.** The 2026-08-10 entry measured the blast radius
> and found that several generator tests legitimately rewrite `site/data/*.json`; protecting the
> directory would red them for nothing. That measurement still holds and is not re-litigated
> here — `publish_provenance.json` remains the one file in there that is a public claim rather
> than a regenerable artefact.

So the central recommendation above — guard `site/data/` as a surface, the way `docs/staging/` and
`docs/status/` are guarded — **is the exact option that was measured and deliberately rejected**,
with the blast radius counted. Not an oversight; a decision.

## Which specific claims die

- **"The catalogued shape / one sibling fixed, three left live."** Wrong, and unfairly so. The
  siblings were not missed. `generate_dashboard_json` is mocked in that suite because
  `site/data/dashboard.json`'s guard status differs, and the others are left live because the
  measurement said leaving them live is correct. I read a deliberate boundary as an incomplete fix.
- **"What stopped it was arrangement, not a control."** Wrong. `tests/production_surface_guard.py`
  IS the control, it is closed over primitives (`builtins.open`, `os.open`, `os.replace`,
  `shutil.*`, the three `Path` methods), and `site/data/` is outside it by measurement.
- **The recommended repair.** Withdrawn entirely.

## What still stands, and it is only this

The *observations* are reproduced and correct: those two suites do rewrite those files, the
promote refusal does name them, and the `git=abc1234` / epoch-0 payload is really what lands in
the worktree copy. All of that is **known and expected behaviour**, not a defect. The operational
consequence is already recorded as such: run broad suites BEFORE `surgical_land`, not between
landing and promoting.

## The one question I am leaving open, stated as a question

`_PROTECTED_WRITE_PATHS` protects `publish_provenance.json` in `site/data/` because it is *"a
public claim rather than a regenerable artefact"*. `director_reserved.json` carries what is
waiting on the director, and what a test writes into it is not a regenerated view of real data —
it is a **fabricated alarm** (`git=abc1234`, wedged since `1970-01-01`, two innocent test node ids
named as blockers). That may put it on the public-claim side of the same line the existing rule
already draws.

I am **not** filing that as a finding. I have not shown it can reach a reader, the shared tree and
HEAD are both clean of it, and the honest move is to extend an existing measurement rather than
open a second front on a question that already has one. If a lane picks it up, the subject is one
line in `_PROTECTED_WRITE_PATHS`, not a new guard.

## Why it happened, which is the part worth keeping

`CLAUDE.md`: *"Look for the parked atom before minting a new one. The thing you are about to file
is usually already on the map."* I did not. I found the behaviour by accident mid-landing,
reproduced it cleanly, and went straight from a good measurement to a filed finding without ever
asking whether the question was already answered — and it was answered, in a module whose
docstring names this exact directory and this exact reason.

**The reproduction was not wasted; the framing was.** Measuring first is right and I would do it
again. What I skipped was the cheap step between measuring and filing: grep for who already owns
the question. Roughly ten seconds, against a finding that would have cost another lane an hour to
re-refute.
