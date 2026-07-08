# BACKGROUND_LANE_AND_WALL — held advisor batch (P2, post-continuation)

**Staged:** 2026-07-08 evening by advisor; director-approved earlier today.
**Tier:** 2. Does NOT interrupt Phase 2/4 — the build lane continues untouched.

## A. Background parallel lane (start now, alongside Phase 2/4)
A second lane for analytics/anchor work ONLY — never phase code. Coordination is
mechanical, not promised: each background job declares its file scope up front;
scopes must be disjoint from the active phase's tree (enforce via the existing
tree_lock); when a P1 or scope conflict arrives, DIVERT the lane to the next
disjoint job, PAUSE only if nothing disjoint remains. Single-writer rule holds
for the repo: background lane writes only to its own output dirs (data/lake/,
docs/market_research/, ASSUMPTIONS.md drafts staged for build-lane merge).

Ranked workloads (metric = anchors produced, NOT GPU utilisation; CPU is fine):
1. **HH load-shape clustering** — cluster real half-hourly profiles into
   candidate household archetypes; correlate with tariff/payment behaviour.
   Output feeds Phase 2 directly: data-derived segments mapped onto ONS/Ofgem
   anchors instead of invented ones.
2. **Latency/error distribution fitting** — fit real data-quality statistics
   (read-failure rates, estimation frequencies, response-time data where
   discoverable) to refine Phase 3's new physics parameters; register anchors.
3. **Qwen batch-summarisation** of discovery-agent fetches → draft
   ASSUMPTIONS.md anchor entries at zero API cost (think:False, num_predict
   bounded, as per risk-committee config).
4. **Hedge/forward-curve backtesting** on the Elexon SSP history → calibration
   bank for the parked hedge-outcome grading, ready when its entry gate opens.

## B. Design preference for new boundary work (Phase 2/4 onwards, no rework)
Where new work crosses the SIM/company seam, prefer the typed-flow-adapter
shape: crossings as versioned messages that a real protocol could carry, rather
than direct function calls. Do not rework Phase 3's shipped code for this — it
is a forward preference so new bricks are wall-compatible.

## C. Register for the director's next P-5 re-rank (do not start)
**WALLED_INTERFACES programme:** full enforcement of architectural law #2 — ALL
SIM/company crossings become typed, versioned messages through real-protocol-
shaped adapters: simulated industry D-flows (e.g. D0010 reads, rejections),
simulated DCC service request/response flows, customer message bus (contacts in
and out as messages). Strategic framing to record with it: the wall IS the
go-live seam — going live becomes swapping sim adapters for real endpoints
behind unchanged interfaces. Proposed sequencing: after the core-fidelity block,
before RY and scale-up. Add to PRIORITIES.md as a registered programme awaiting
director rank; prepare a one-page decomposition sketch (desk work, background
lane eligible) so the director ranks something concrete.

## Definition of done
Lane running with first workload started + scope declared; B noted in CLAUDE.md
design preferences; C registered in PRIORITIES.md with sketch queued. One NTFY.
Build lane (Phase 2/4) should not notice any of this happening.
