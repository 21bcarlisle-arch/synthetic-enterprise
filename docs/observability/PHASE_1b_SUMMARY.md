# Phase 1b Summary — Weather Data Capture

## What Was Built
- `docs/data-sources/weather.md` — decision record for Open-Meteo's Historical Weather Archive API: endpoint shape, params, a real probed sample response, grid-snapping behaviour, and the Open-Meteo→project schema field-name mapping
- `sim/weather_ingestor.py` — `get_daily_weather(location_id, latitude, longitude, start_date, end_date)` (single ranged request, returns a flat list of `{date, location_id, temperature_max_c, temperature_min_c, temperature_mean_c, wind_speed_mean_ms, cloud_cover_pct, precipitation_mm}` dicts) and `write_weather_csv(records, output_path)` (fixed-fieldname `csv.DictWriter`, writes a header even for empty input)
- `simulation/run_phase1b_weather_pull.py` — orchestration script: loops the four `saas.customers.CUSTOMERS` locations, pulls the full sim window in one request per location, writes one CSV per customer to `sim/weather_data/`
- `sim/weather_data/{C1,C2,C3,C4}.csv` — **13,784 real daily records** (3,446 days × 4 locations: London, Manchester, Glasgow, Cotswolds), each spanning exactly 2016-01-01 → 2025-06-07, schema-correct and CSV-round-trip verified by spot-checking head/tail/sample rows and exact row counts

## Key Findings
- **Open-Meteo needed no day-by-day looping** — unlike Elexon, its Archive API accepts an arbitrary `[start_date, end_date]` range in a single request, so the whole 9.5-year pull for all four locations completed in four HTTP calls total
- The API **grid-snaps requested coordinates to its nearest reanalysis cell** and echoes the actual coordinates used in the response (e.g. requesting 51.5074/-0.1278 for London returns 51.4938/-0.1630) — normal ERA5/ERA5-Land behaviour, not a bug, and worth remembering when correlating later
- Coverage was **directly probe-confirmed** to span at least 2015-11-01 → 2025-06-07, comfortably bracketing the sim window with margin either side — Historical Ground Truth law satisfied with real, citable, reproducible data (no synthetic weather)
- **A second instance of the exact same docstring-placement defect** appeared in this phase (see Notes) — strong enough signal (2-for-2) to call it a named pattern rather than noise

## Key Decisions Made
- Chose Open-Meteo over alternatives because it's free, key-free, reliably available, and (crucially) supports arbitrary-range single requests — a major operational simplification over Elexon's day-range-at-a-time convention
- Stored data **flat, per-location, uncorrelated** — exactly per the Master Backlog brief ("store it, do not correlate yet"); weather↔consumption correlation is explicit future backlog, not pulled forward
- Kept the schema field names independent of Open-Meteo's variable names (`temperature_2m_mean` → `temperature_mean_c`, etc.) so the storage layer isn't coupled to one provider's naming conventions
- Used the now-standard "probe the real API first, hand the model only verified facts" pattern — prevented any endpoint or response-shape hallucination in the generated ingestor

## Open Questions
- Should `tools/delegate_ollama.py` post-process generated Python to strip markdown fences and detect/relocate misplaced module docstrings automatically, given these are now repeat (5/5 and 2/2 respectively) failure modes rather than one-offs?
- When correlation work begins (future backlog), will daily-resolution weather be sufficient against half-hourly settlement data, or will sub-daily weather be needed — and does Open-Meteo's archive support that resolution for historical dates?

## Token Efficiency
- **Local model calls (Phase 1b only):** 3 — `qwen2.5-coder:14b` via `tools/delegate_ollama.py`, total 6,279 local tokens (prompt_eval + eval):
  - weather data-source doc, from probed-facts spec (prompt_eval=1572, eval=1625) — correct first try
  - `sim/weather_ingestor.py`, from probed-facts spec + sibling-file style reference (prompt_eval=1191, eval=747) — functionally correct first try; one defect (see Notes)
  - `simulation/run_phase1b_weather_pull.py`, from spec with exact upstream signatures (prompt_eval=752, eval=392) — functionally correct first try; the same defect recurred (see Notes)
- **Frontier tokens:** the work spanning the MASTER_BACKLOG.md authoring + Phase 1a + Phase 1b ran as one continuous session with no clean per-phase breakpoint in the transcript, so frontier usage is reported combined rather than split: **282,635 headline tokens** (in: 222, out: 90,508, cache-create: 191,905 | cache-read: 14,285,069), computed directly from the session's `usage` blocks from the point the user issued the MASTER_BACKLOG instruction onward. Phase 1a did not get its own token-log entry — this entry retroactively covers it. Future phases should each get a clean entry as long as natural phase-boundary breakpoints exist in the transcript.
- **Notes:** The same exact defect — a module docstring written as a dangling string statement *after* the code rather than as the file's first statement (syntactically valid, functionally inert: never becomes `__doc__`) — appeared in **both** Phase 1b code generations (`sim/weather_ingestor.py` after both functions; `simulation/run_phase1b_weather_pull.py` right after `import os`). Both hand-patched by relocating the docstring text to the top of the file. Two-for-two in the same phase is enough to name this explicitly in delegation prompts going forward: *tell Qwen exactly where the docstring goes — first line of the file, before any import — don't assume "write a docstring" implies correct placement.* The familiar markdown-fence-wrapping defect also recurred on all three generations and was stripped the same way as in prior phases.
