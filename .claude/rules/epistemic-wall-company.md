---
paths:
  - "company/**/*.py"
  - "saas/**/*.py"
---

# You are editing the COMPANY side of the epistemic wall

This code operates under the SAME information constraints as a real UK energy supplier. It cannot
see simulation internals — churn parameters, forward curve construction, weather engine outputs, VaR
internals, or any full historical dataset read without an as-of/bisect bound. It discovers the world
through observable interfaces only: market data feeds, meter reads, customer interactions, its own
bills and payments, regulatory publications.

**Before writing or editing anything here, ask: "Could a real UK energy supplier know this?"** If the
answer requires reading simulation internals, it is a violation — not a style issue, a Tier-1
epistemic-law concern.

- The SIM/company seam is `company/interfaces/sim_interface.py` — it exposes observables only, never
  internals. New crossings should prefer a typed, versioned-message adapter shape over a direct
  function call (the wall IS the future go-live seam).
- Point-in-time discipline: use `company/interfaces/point_in_time_view.py` /
  `bitemporal_event_log.py` for anything that needs "what did we know when" — never read a full
  historical dataset without an as-of/bisect bound. `.claude/hooks/block_point_in_time_read.py`
  flags exactly this pattern.
- Run `python3 -m tools.epistemic_verifier` before committing anything in this path — it scans for
  data-flow/timing violations, not just literal `simulation.*` imports.
- The company's models are approximations built from observed outcomes, not reads from ground truth.
  That imperfection is the point — do not "fix" it by giving the company more visibility than a real
  supplier would have.
