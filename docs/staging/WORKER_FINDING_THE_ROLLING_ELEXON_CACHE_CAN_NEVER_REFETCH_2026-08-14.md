# [WORKER FINDING] The rolling Elexon cache can never re-fetch, so the correction it says wins never arrives

**Severity:** LATENT · **Lane:** W4_the_wall
**Found:** 2026-08-14 worker tick, EP7 DISCOVER/FRAME (`docs/design/EP7_ELEXON_INSIGHTS_DISCOVER_FRAME.md` §2)
**Subject:** `background/refresh_elexon_ssp_rolling.py`

## What was found

`refresh()` computes its fetch window as `start_date = last_covered + 1 day`, so the window is strictly
forward of every date already on disk. Twenty-odd lines later it merges:

```python
# Merge: drop any existing rows for the dates we just re-fetched (D+1 corrections win),
refetched_dates = {r["settlementDate"] for r in fresh}
merged = [r for r in existing if r.get("settlementDate") not in refetched_dates] + fresh
```

`refetched_dates` and the existing dates are disjoint by construction, so the drop can never remove a
row. The correction path the comment describes is unreachable.

## Evidence — falsified, not read

Injected fetcher, scratch cache file, the real `refresh()`:

| call | `today` | window asked for | cache after |
|---|---|---|---|
| 1 | 2025-06-09 | `2025-06-08 … 2025-06-08` | `2025-06-08` @ 100.0 |
| 2 | 2025-06-10 | `2025-06-09 … 2025-06-09` | `2025-06-08` @ 100.0, `2025-06-09` @ 200.0 |

Windows produced after `2025-06-08` was first covered that include `2025-06-08`: **none**. A restated
value for an already-covered date has no path into the file, whatever the platform serves.

## Live blast radius

`sim/cache/elexon_ssp_live_rolling.json` holds **20,736 records covering 2025-06-08 … 2026-08-13** —
432 days × 48 settlement periods, complete, no gaps. Every record is the value fetched on the day after
delivery (`end_date = today - 1`). `tools/live_market.py` merges this file into the **live decision
path**, so the extension past the frozen decade is fourteen months of day-after figures.

## Why LATENT and not higher

Nothing published is shown to be wrong by this. Whether the SSP series itself moves between D+1 and the
later settlement runs is a fact about Elexon that cannot be checked from this sandbox (no network in
autonomous runs), so the finding stops at what is observable in the tree: a code path that cannot
execute, and a stored series that cannot be corrected if it ever needs to be.

What *is* observable is that the repo contradicts itself about the world. The comment says

```python
end_date = today - dt.timedelta(days=1)  # settlement data is final at D+1
```

while `simulation/settlement_timetable.py` and `company/regulatory/settlement_reconciliation.py` — both
Elexon-anchored, with a test asserting their constants never drift apart — model revision at R1 ~1 month,
R2 ~3, R3 ~5 and RF ~28 months after delivery. The atom's own `name:` field agrees with the second pair:
*"indicative settlement prices … with a D+1 refresh; Settlement messages give early warnings on
calculation accuracy."*

## The measurement that closes it, and its cost

One GET: re-fetch `2025-06-08` (fourteen months and three settlement runs old) and diff against the
stored record.

* **Differs** → the correction is real, the window should look back over the revision horizon rather than
  only forward, and EP7's belief-vs-truth gap has its first number.
* **Identical** → the "final at D+1" comment holds for the price series, and the unreachable merge line
  should be deleted rather than repaired.

Key-free public endpoint, already on the egress allowlist, and it belongs in the background pipeline
where the network exists. **Not gated by EP7's epoch block** — it is a measurement, not an integration.

## Not fixed here

The fix is a change to a live background job on the world's data path, and either shape of it (widen the
window, or delete the dead line) depends on the measurement above. Queued per SELF-INTERRUPT DISCIPLINE:
the machine is not blocked.
