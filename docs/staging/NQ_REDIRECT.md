[SUPPLIER + SIM] Phase NQ redirect -- recalibrate against reality, not against the SIM

Partial redirect on the NQ proposal, within the 4h window.

PROCEED with (B), the 24-month reference window -- sound fix for sustained-crisis blindness where YoY looks flat because the reference year was already elevated.

DROP (A), the 5% base rate floor. It shifts every estimate up uniformly without improving discrimination -- if the retention threshold is 30% and the missed churns sat below 25%, a 5% floor changes nothing about which customers cross the line. Cosmetic recall, not real recall.

ADD (C) -- SIM churn realism check, and do this FIRST: in the real 2021-22 crisis, UK switching COLLAPSED to record lows. There were no cheaper deals to switch to; suppliers withdrew acquisition tariffs; customers rolled to SVT with their existing supplier. Ofgem publishes annual switching statistics showing this. If the SIM's ground-truth churn RISES during the crisis period, the SIM is behaving unrealistically -- and recalibrating the company model to catch those churns trains the company to predict behaviour that never happened in reality. Check SIM annual churn rates by year against published UK switching rates. If SIM crisis churn is inflated, fix the SIM's churn behaviour first; only then recalibrate the company model against corrected ground truth.

CAUTION on sample size: the NO finding (optimal threshold = 0%) rests on 6 churn events. That is far too small to conclude the model cannot discriminate. Treat it as a flag, not a verdict -- do not over-steer the model on n=6.

SEPARATELY, Rule 2 verification failure: PROJECT_STATE.txt at poesys.net/state/PROJECT_STATE.txt was last generated 2026-06-30 (Phase HY, 9,290 tests) -- the auto-sync is not firing. The observability deliverable is not verifiably done until: (1) PROJECT_STATE.txt regenerates on push again, (2) customer_sample.json has a stable fetchable URL, and (3) that URL is listed in PROJECT_STATE.txt's Key Files section so the strategy advisor can find it. Fix the sync as part of closing the observability instruction.
