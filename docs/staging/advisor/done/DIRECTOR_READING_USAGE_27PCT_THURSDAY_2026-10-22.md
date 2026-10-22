**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage 27% at 14:52 on Thursday (22 Oct 2026), and the site this week

**Type:** usage reading, relayed by the advisor. The director's words, from chat on Thu 22 Oct:

- 14:52 BST: "How is it progressing? Is it picking up.your stages? I'm keen the website gets updated this week. NB 27%."

**Pacing (P12, R1).** About 3.4 days of the week have gone and 27% is spent, roughly 8 points a day. The reset is Mon 26 Oct 04:00 BST, about 3.5 days away. Keeping about 6 points in reserve leaves about 67 points, roughly 19 a day: more than twice today's rate. Widen the work in parallel under the memory budget (R7). Don't wait for further readings.

**The site.** The front-door steer landed within the morning, and the director has been told so. Two items follow from his "keen the website gets updated this week":
- Three Cloudflare Pages deploys failed today, at `420a5b67d`, `989ce4f1c` and `02659d155`. The 13:48 UTC deploy at `e5d99e249` succeeded. Find the cause and fix the class so a site change cannot fail to deploy silently (P13). Say whether readers ever saw a broken page.
- The proof strip shows the 19 Oct run: 227 households in 2025. Make sure this week's publish carries the 400-household founder book through to it, so the front door's figures match the book the director ruled on. If the weekly publish cannot land before Monday, say so in the stretch log with the reason.

— Advisor, relaying the director's reading on the director's standing delegation of 15 Oct.

## Done

*Seat executor, 2026-10-22 ~16:30Z.*

- **The failed deploys.** There were five red runs today, not three: 07:32Z, 07:58Z (`420a5b67d`),
  09:49Z (`989ce4f1c`), 11:55Z (`02659d155`) and 16:07Z (`2406226c8`, this turn's own push). In
  every one, `wrangler pages deploy` completed. Only the check after it, served-bytes, went red,
  and always on `https://poesys.net/`. Every red run changed `site/index.html`, and no green run
  today did. **Readers never saw a broken page.** A Pages deployment is atomic. On this turn's push
  a UK fetch got the new front door within about 90 s, while the runner's edge served stale bytes
  at `/` for 8 minutes. So the window is refuted as the cause, and a per-edge cached `/` is the
  working hypothesis. The class fix is carried by continuation
  `the-front-door-banner-remainder-sweep-harness-status-and-deploy-window`. Full account:
  `docs/staging/SEAT_FINDING_THE_FAILING_LINE_WAS_A_LANDED_PUBLISH_ITS_EPISODE_NEVER_CLOSED_AND_THE_DEPLOYS_DID_NOT_FAIL_2026-10-22.md`.
- **The 400-household book.** HEAD carries the ruling: `docs/design/FOUNDER_BOOK.yaml` has
  `founder_unit: households` and `founder_accounts: 400`. **The weekly publish cannot land before
  Monday.** The weekly window holds it until Mon 2026-10-26 04:00, so that publish is the first
  that can carry the 400-household book to the proof strip. Until then the strip shows the
  19 Oct run (227 households in 2025), and it now says so in its own line: "Figures from the run
  of 19 Oct 2026 · published every Monday".
- **The site this week.** Three landings are live: `e825e8099` (no banner on the front door),
  `8bf9103a1` (the publisher no longer reads "failing" over a landed publish) and `bd2ec5e1b`
  (the "What has been built" strip, counted from git at publish). They were promoted together as
  `2406226c8`.
