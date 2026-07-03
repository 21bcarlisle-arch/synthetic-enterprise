[PROJECT] Observability: customer-level data + shadow HTML view -- both mission-critical

Rich (strategy advisor's principal) has confirmed this is mission-critical: the strategy advisor must be able to independently verify what's actually running, not rely on phase-close prose descriptions or a UI it cannot render. Two separate deliverables, same root cause -- neither should be dropped for the other.

DELIVERABLE 1 -- Customer-level ground truth (raw JSON, permanent)
Same mechanism as PROJECT_STATE.txt (auto-sync on push, plain fetchable JSON, no auth). 
Build: site/data/customer_sample.json, auto-regenerated every sim run, published to a stable URL (e.g. poesys.net/state/customer_sample.json). ~15-20 real customer records from the segment model, each with: customer_id, segment, full life event history, income_stress trajectory, satisfaction_score trajectory, payment_behaviour_analytics (score/on_time_rate/trend), enriched_churn_estimate inputs and output at last renewal, basis_risk vs SIM ground truth.
This proves the human simulation layer (Phases MV-NH) produces real individual-level output, not just aggregate churn numbers.

DELIVERABLE 2 -- Shadow HTML view of the live site (static, no JS framework)
poesys.net/customers/, /supplier/, /project/, /sim/ are JS-rendered SPAs. The strategy advisor's fetch tool retrieves raw HTML only -- it cannot execute JavaScript, so these pages are currently completely invisible to it, working or not.
Build: a parallel static-HTML mirror (no React/JS framework, server-rendered or pre-built plain HTML) showing the same underlying data as each of the four site sections. Doesn't need real styling -- functional and complete beats polished. Published alongside the real site, e.g. poesys.net/shadow/ or a subdomain. Purpose is machine-readability for audit, not human UX -- the real site remains the human-facing product.

BOTH should be added to the mandatory session-startup protocol: PROJECT_OVERVIEW.md -> LATEST.md/ASSUMPTIONS.md -> customer_sample.json -> shadow site, every session, not requested ad hoc.

Report back what already exists before building new -- the portal or parts of the shadow view may be closer to done than expected.