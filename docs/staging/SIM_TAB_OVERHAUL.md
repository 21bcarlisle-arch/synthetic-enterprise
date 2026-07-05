[SIM + PROJECT] SIM TAB OVERHAUL -- director critique. This tab's job (WEBSITE_AS_SHOWCASE tab 1): bring the world to life -- physics, event frequencies, behaviours, INTERRELATIONSHIPS. Strong raw material, specific failures.

CRITIQUE FINDINGS (Rich's screenshots, 05 Jul):
- PRICES: crisis spike crushes the y-axis -- decade reads as a flat line. Needs log scale or linked zoom band; crisis spikes expand INLINE to that day's HH profile. Negative-price lows present but unexplained (they are a discovery -- tell it). No correlation panels anywhere.
- WEATHER: 10-year temperature spaghetti chart unreadable -- replace with 10-yr envelope band + one highlighted/selectable year. Weather presented as trivia, not as link 1 of the demand->price chain.
- BM SETTLEMENT: best tab. But the 2021-22 crisis paradox (system flips NET LONG while prices explode) sits uncommented in the table -- surface it as a finding card with the explanation. Dual-axis chart unreadable at mobile scale.
- CUSTOMERS (weakest, live bugs): cards say "MODERATE STRESS: 0" while the table shows C7+C8 moderate -- cross-element inconsistency ON ONE PAGE (gate case). Table full of dashes (tenure --, satisfaction --, most life events --) when customer_sample.json demonstrably CONTAINS satisfaction trajectories and life events -- the page is not wired to existing data. Nothing from the QL journey state machine appears.

THE REBUILD -- the tab tells the causal chain at WORLD level (weather -> demand -> price -> settlement -> customer behaviour), per the site-wide grammar:

1. CHART CRAFT RULES (standing, all tabs): no spaghetti (envelope + highlight); log/zoom for spiky series; every chart answers a stated question written above it; dual-axis only with clear pairing; crisis periods bannered consistently.
2. CORRELATION PANELS as first-class content (Rich's core ask): HDD vs demand vs price (the physics chain); price vs system short%; income stress vs payment delay; price/crisis vs in-market entries. Each panel = scatter or paired series + one-line stated relationship + inline expand to the underlying data.
3. EVENT-FREQUENCY PANELS (the world's pulse): life events/yr, bill shocks/yr, complaints, switches, review events (when built) -- rates over time with crisis banding. The world breathing in numbers.
4. JOURNEY FLOWS (QL is live -- show it): population by journey stage (content/irritated/in-market/comparing) over time; stage-transition rates; funnel view once acquisition lands. This is behaviour made visible.
5. CUSTOMERS TAB REWIRE: bind to customer_sample.json fully -- tenure, satisfaction trajectory sparkline per customer, life events, journey stage; fix the cards-vs-table inconsistency; income-stress distribution over time from real data (crisis years should visibly shift the mix). Link each row to its Customer 360 page.
6. FINDINGS SURFACED: the BM crisis paradox, negative-price hours, price-elasticity disconfirmation -- each as a finding card with its evidence expansion. Discoveries belong on the world page where they happened.

STANDING RULES (same as Project tab): derive-or-die (no hand-written numbers), consistency gate covers sim/ pages INCLUDING intra-page card-vs-table agreement, freshness stamps, design laws v4 (light, progressive disclosure inline, no popups, UK lens). Acceptance: Rich's eyes; report awaiting-review.
