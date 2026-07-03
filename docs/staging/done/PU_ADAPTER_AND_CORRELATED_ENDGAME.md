[SUPPLIER + PROJECT] Phase PU steer + correlated-simulation endgame roadmap note

PART 1 -- PU SHADOW LIVE: proceed with frozen 2025-12-31 portfolio (the reversible choice). But the key architectural requirement is this:

BUILD THE MARKET FEED AS A SWAPPABLE ADAPTER. The shadow-live company layer must be AGNOSTIC to its market source. Frozen-2025 historical data, fresh-2026 data, and (eventually) a pure synthetic correlated weather+market generator must all be interchangeable adapters behind one stable interface. The company's daily decision loop -- renewal queue, hedge rec, acquisition pricing -- consumes a market-data port; what sits behind that port (historical replay vs synthetic generator) is a swap, not a rewrite.

Rationale: frozen-2025 is a stepping stone, NOT the destination. Do not over-invest in historical-replay plumbing as if it's the endpoint. The durable, reusable asset is the decision architecture and the market-source interface. Build PU so the correlated generator (Part 2) drops in later with zero rework to the company layer.

PART 2 -- ROADMAP DESIGN NOTE (capture, don't build yet): THE ENDGAME IS A PURE CORRELATED SIMULATION.
The long-term destination is a free-running energy-market + weather simulation with NO historical replay -- generated correlates only, so it can run open-ended (run and run, infinite scenarios, true Digital Darwinism with induced crises that never actually happened). Historical data stops being the thing replayed and becomes the thing VALIDATED AGAINST.

Building blocks already exist: regime-switching AR(1) weather with Cholesky cross-location correlation; price engine with volatility premia; synthetic forward curve. What's missing is the CALIBRATION GATE.

The non-negotiable design principle for this endgame: the free-running generator's discoveries only carry weight once its synthetic output is statistically indistinguishable from the real series. Gate it behind a statistical-equivalence test against held-out real data:
- generated weather must match real distributional moments AND tail/cold-snap frequencies (not just mean/variance)
- generated prices must reproduce stylised facts: seasonal shape, negative-price hour frequency, crisis fat tails, gas-power correlation, bimodal distribution at high renewables
Only output that passes the gate is trusted. This is population-anchoring discipline moved up from the customer layer to the market layer.

SEQUENCING: this comes AFTER observability + billing land. Keep the historical run as calibration ground truth. Build the correlated engine alongside it, gated. Do NOT start it now -- this note is to queue it in PRIORITIES.md backlog so it's not lost, not to redirect current work.
