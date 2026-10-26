**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-CHASE] What is left of the externals steer at 16:20, in the order to land it (2026-10-26)

**Type:** CHASE, through the advisor channel. This chases `DIRECTOR_STEER_THE_SITE_IS_READ_BY_EXTERNALS_TOMORROW_2026-10-26.md` and `DIRECTOR_RULING_THE_FOUR_RESERVED_QUESTIONS_2026-10-26.md`. The director's words, from chat on Mon 26 Oct:

- 13:27 GMT: "I am expecting externals to look at the website tomorrow so really want the website looking good and up to date today."

## What the advisor's re-render at 28398fcd shows

**Landed, and confirmed in the render:**

- The queue now holds only reserved actions.
- "Built by" is gone from Knowledge (0 of 62).
- The census has moved to "How these pages are checked".
- No page scrolls sideways at 390 px.

Your pushback on the classifier clause is reasonable. Leave it raised as you filed it.

**Not yet visible, in the order to land:**

1. **Explore still shows "Unit rate 6.27 p/kWh"** on a Standard Variable tariff. That is the energy component. An energy reader will spot it first.
2. **Privacy for site visitors (ruled by the director at 13:47).**
   - The footer reads only "© 2026 Poesys Platforms. All rights reserved. · Privacy".
   - `/privacy/` is the modelled customer notice and does not mention the analytics.
   - Add the footer line from the ruling.
   - Add a short "Visitors to this website" section at the **top** of `/privacy/`, covering what Cloudflare Web Analytics collects, that it sets no cookies, and Cloudflare's policy link.
   - Keep the modelled notice below that section.
   - The modelled notice says "UK energy supplier". Make it GB.
3. **Home copy.**
   - "62 published knowledge pages on how the GB market and its households work" still counts the 8 other-market pages as GB.
   - "New this week" still carries "in the director's points" and "a hand-drawn file".
   - The drafted wording is in the steer.
4. **Capabilities** is still 25,263 words. Open it with the value-test paragraph, collapse the rest, and strip the paths and hashes.
5. **The three data files** still carry 8b6fea024:
   - `capabilities_door.json` (1 reference),
   - `dashboard.json` (1),
   - `delivery.json` (1).
6. **The home diagram** still shows internal codes.

If 4 or 6 cannot land safely tonight, say so in Done. Items 1–3 can.
