**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] The four reserved questions: no GitHub link, keep the analytics with a notice, stay on £100, HF token deferred (2026-10-26)

**Type:** RULING, through the advisor channel. The director's words, from chat on Mon 26 Oct:

- 13:47 GMT: "Hide the GitHub link. Keep the tracker but but a footnote or whatever is necessary for this to be reasonable and normal practice. Stay on £100. Do we need HF?"

This rules the four items that `DIRECTOR_STEER_THE_SITE_IS_READ_BY_EXTERNALS_TOMORROW_2026-10-26.md` left on the director's list. It amends that steer: the "Waiting on the director" panel should now show none of these four as open.

## The rulings

1. **GitHub link: no.** Do not add a link to the repository from the front door, from How it builds itself, or from any other page. Close the 22 Oct item as *declined*. Then check the published pages for any existing link to `github.com/21bcarlisle-arch/synthetic-enterprise`, apart from any the code page needs to explain itself, and list in Done what you found. Remove those links. If a page needs one to make sense, ask through the advisor channel. Do not decide that yourself.
2. **Cloudflare Web Analytics: keep it, and say so.** Close the 23 Oct item as *ruled*. The advisor's reading of normal practice is as follows; it is not legal advice. Cloudflare Web Analytics sets no cookies and uses no local storage, and it does not fingerprint visitors or track them across sites. A short, plain disclosure in the footer of every page is therefore the usual practice, and no consent banner is needed. Do three things:
   - **Footer line on every page**, linked to a short `/privacy/` page:
     > "Poesys counts page views with Cloudflare Web Analytics. It sets no cookies and does not track you across sites. [Privacy]"
   - **`/privacy/` page**, plain and short, covering:
     - what is collected: page views, referrer, country, browser type and page load time, in aggregate;
     - who processes it: Cloudflare, with a link to its privacy policy;
     - that Poesys sets no cookies of its own and has no accounts, forms or tracking pixels;
     - that the site is a simulation and holds no real customer's data;
     - a contact route: use the project's existing contact if one is published; otherwise leave it out and say so in Done, and do not invent an address.
   - **The deploy check**, as the seat proposed on 23 Oct: allow exactly the one injected `cloudflareinsights` block, and stay red for anything else that is injected.
3. **Plan tier: stay on the £100 tier.** Close the 23 Oct item as *ruled*. The cheap levers the seat named stay enacted.
4. **HF token: not needed now.** Close the 25 Oct item as *deferred, not open*. The uk_pv metadata matters only to the PV roof distribution, and that sits in step 8 of `priority_order.yaml`, after the forward years. Until then the placeholder orientation shares remain a named assumption, and the terms acceptance of 25 Oct stands. When step 8 actually reaches PV, raise it again as one line saying the token is needed this week. Do not keep it on the waiting list until then.

## Done

Recorded 26 Oct 2026 by the delivery seat's Lane 0 worker.

1. **GitHub link: declined.** The 22 Oct item is closed as *declined*, with his words: **8be05177e**. Published pages checked for `github.com/21bcarlisle-arch/synthetic-enterprise` across every rendered page at origin and the raw bytes of `site/`: **no link anywhere**. The only hit is text, not a link: `site/data/delivery.json` quotes this ruling. `site/data/simplified.json` names a different repository (SmartDCCInnovation). Nothing to remove.
2. **Cloudflare Web Analytics: kept, with notice.** Item closed as *ruled*: **8be05177e**.
   - The footer line, verbatim, is on every served page (77) and links `/privacy/`. It is rendered from `site/ia_register.py`, and `site/test_every_served_page_carries_the_analytics_notice.py` holds it: **this commit**.
   - `/privacy/` opens with "Visitors to this website", which covers what is collected in aggregate, Cloudflare as processor with its policy linked, no cookies, accounts, forms or pixels of our own, and that this is a simulation that holds no real customer's data. The modelled customer notice stays below it, with UK supplier now GB, per the 16:20 chase: **this commit**.
   - **Contact: no contact address is published anywhere on the site, so the page says so and none was invented.**
   - The deploy check allows exactly one injected `cloudflareinsights` block and stays red for anything else: **75cc881dc** (23 Oct), unchanged.
3. **Plan tier: stay on £100.** Closed as *ruled*: **8be05177e**.
4. **HF token: deferred, not open.** Closed as *deferred*; raise again as one line when step 8 reaches PV: **8be05177e**.
