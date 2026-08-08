# [DIRECTOR-RULING] — Infrastructure posture: seat, standby, scale (2026-08-07)

**Type:** [DECISION]. Ratified in conversation 2026-08-07; the director's own sequence — "start with PC, no Qwen reliance, Oracle for recovery cut-over, proper scale later" — adopted verbatim as the posture. See-and-correct applies; the worker sequences everything below without approval loops.

## The three planes (the wall is the deployment boundary)
**Mind-plane** (seat: worker, advisor consumption, sim, daemons) — small boxes, never scales with customers. **Standby** — a cold rebirth target for the seat (cut-over proposal R1–R5). **Product-plane** (customer-facing SaaS: event spine, API/portal, ingest, billing, comms) — does not exist until Epoch 5, and scales alone.

## Ruling 1 — Qwen retired as a dependency
The GPU model was the only component pinning the seat to specific hardware, for token savings now measured in rounding error against a Max licence. Therefore: dispatcher/classification traffic re-points to a Haiku-class API call; adversarial/verification organs run as restricted-context Claude per the established cold-eyes doctrine (context isolation, not model foreignness, is the independence mechanism this project already trusts); GPU workloads (clustering, curve-fitting, batch summarisation) demote to opportunistic garnish whenever Skynet happens to be on — a nice-to-have, never a seat dependency. Effect: the seat becomes fully hardware-agnostic. Worker re-points the organs; the naive-organ output-budget work applies unchanged.

## Ruling 2 — Seat and standby
Seat now: the PC, Saturday wake unchanged. Standby: **Oracle Always Free, cold** — instance created once then STOPPED (allocation held), account upgraded to PAYG-at-$0 as the reclamation/capacity safety-catch. The R5 timed dead-box drill is the arbiter: if the drill exposes capacity pain at rebirth, fall back to the Hetzner-snapshot pattern (pennies/month) on evidence, not preference. Director's prep remains the 20-minute secrets escrow.

## Ruling 3 — Scale deferred, and the AWS account deliberately NOT opened yet
Product-plane default is pre-decided (AWS eu-west-2, proven-at-destination; managed Postgres event spine + object storage + stateless services + queue workers; the 10k probe's measurements become the migration spec). But the modern AWS free tier is a countdown, not a foundation: new accounts get $100 + up to $100 earned credits on a Free plan that **self-closes at 6 months or credit exhaustion** (90-day grace, then resources erased); upgrading preserves remaining credits ≤12 months from signup. Opening it now burns the clock years early. **The account is opened at Epoch-5 mobilisation and the ~$200 spent deliberately standing up the product skeleton.** Until then, "proper scale" work is exactly two things already in flight: the traffic-forecast seams and the probe.

— Ruled 2026-08-07; staged by the advisor. Revisable by later ruling; the drill result may revise Ruling 2's provider on evidence.

## Revision (2026-08-07 evening) — the cloud box is the SEAT, not the spare
Director's words: *"I want to actually use it. Not just DR. As per this week."* Ruling 2 is upgraded accordingly:
- **Seat destination = an always-on cloud box.** The PC is the *transitional* seat only — it hosts Saturday's wake and the batch consumption on known ground — after which the worker's top OPS project is building its own new home: the bootstrap script, then the **automated Oracle A1 acquisition loop** (retry the free-shape launch until capacity lands — the machine, not the director, is the retry mechanism), then a **graceful Class-A cut-over** per the staged proposal. Marker moves, PC's marker deleted, one seat on Earth.
- **Primary target: Oracle Always Free** (£0 forever once landed; the saved stack/VCN/keys from tonight are its ingredients). **Interim-or-fallback: Hetzner** — if Oracle's queue outlasts patience or the director prefers certainty, an 8 GB-class box (~€7–13/mo post-June-reset) becomes the seat by the same ceremony; 4 GB (€5.49–5.99) is workable-but-tight for full suite runs.
- **DR inverts and improves:** once the seat is cloud-resident, the standby becomes a snapshot of the cloud seat (pennies) — and the PC itself is a warm second fallback. Cut-over capability is now bidirectional by construction.
- **The PC's permanent role:** the director's desk machine plus opportunistic GPU garnish when powered — nothing load-bearing. The week's failure class (seat dies with the house) is retired structurally.
