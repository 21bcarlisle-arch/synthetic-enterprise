
---

## ADDENDUM (same evening) — the mechanical finding: the parked-into-blind-spot bug

Advisor-verified from the ledger: at 20:00Z the campaign's remaining items were parked into `docs/staging/in_progress/` — **the directory the work scanner deliberately excludes** — after which the scanner found "nothing drawable" and the tick idled 56+ minutes with an open campaign. The system filed its own to-do list into its own blind spot. This is tonight's named failing test alongside the hierarchy R15s: **parked-campaign-with-open-items must be drawable** (either the classifier reads open items wherever they are parked, or open campaign items are never parked into the excluded directory — pick the mechanism, prove it both ways). Additionally: full-day utilisation computed at ~26% (3.9h active / 15.3h, seven >45-min idle windows) — tonight's note reports its own number against this baseline.

---

## SAFETY RAILS (director + advisor, added before the granted-turn revival) — how tonight's odds get improved

The night's largest risk is precisely the ordered work: the hierarchy build modifies find_work — **the component that just crash-looped from its own last self-edit.** Four rails, mandatory tonight:

**RAIL 1 — Shadow-then-swap for ANY scanner/draw edit.** The new hierarchy draw logic is built as a parallel module, never an in-place edit. Each tick runs the OLD scanner for real draws and the NEW one in dry-run, logging divergence. Swap only after ≥10 clean shadow cycles AND the R15s pass; keep the previous scanner file for one-command revert. If shadow shows divergence that can't be resolved quickly: **HOLD on the old scanner overnight** — seeds and campaign remain drawable on it — and swap at coffee. A held swap is a pass, not a miss.

**RAIL 2 — Crash-loop immunity in the tick.** Wrap the scanner call: on exception, (a) page immediately — "SCANNER EXCEPTION: <error>" — and (b) fall back to the last-known-good scanner copy for that tick. Tonight's silent hour becomes a loud minute, and a bad edit degrades to noise instead of death. Build this BEFORE touching the scanner.

**RAIL 3 — Advisor-checkable heartbeat.** Every tick writes one line (timestamp · drew/rested/exception · the whole-set enumeration) to a status file **shipped by the existing auto-publish** — so liveness is verifiable from origin every ~6 minutes without SSH, by director or advisor. The supervisor pages if the heartbeat stalls or shows exceptions for >5 min.

**RAIL 4 — Risk-first sequencing.** Rails 2–3, then the shadow build, all in the FIRST hours while the director and advisor are still on watch; one NTFY when the shadow verdict is in ("shadow clean, swapped" or "divergent, holding on old scanner"). Routine work (seeds, campaign) fills the rest of the night on whichever scanner is live. Nothing structural after that NTFY until morning.

— Addendum 2, same evening.
