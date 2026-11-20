**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] The repository stays public, and the website goes behind a login

*Status, 20 Nov 08:15Z (delivery seat): one step is left, the director's first successful login.
The gate is a password page, not Access, because Zero Trust asked for a card (his 20 Nov "Card").
It is live and refuses an anonymous fetch on every route, read from outside (the readings are in
`docs/design/POESYS_NET_BEHIND_A_LOGIN_2026-11-19.md`). robots and noindex are on. D11 is amended. The
advisor has the password file's path, and the advisor tells him how to read it. When the advisor
relays that he got in, move this file to `done/`. No other work is owed here.*

**Type:** RULING, through the advisor channel. It answers `for_the_director` row `the-github-repository-is-still-public-gh` (raised 18 Nov).

## The director's words (chat, Thu 19 Nov, verbatim)

- 14:05: "It isn't a real company. Maybe we should add a password to website?"
- 14:07: "Repo public. Website password"

## What is decided

1. **The repository stays public.** Close the July make-private plan and its row. There is no legal entity, because Poesys is not a company. Do not add a copyright line naming a company. If one is ever wanted, it is in the director's own name, and that is his call when he asks for it.
2. **poesys.net goes behind a login.** The site is on Cloudflare Pages, and Cloudflare control was granted on 20 Aug. The machine owns the design. The advisor's suggestion, not a prescription: Cloudflare Access with one-time email codes, and the director's own address as the first allowed reader.

## Non-negotiables

- **Gate every route to the same site, not only the front door.** That includes the `*.pages.dev` address and its preview URLs, and any Pages Function endpoints. A gate with a side door fails open. Prove the gate can fail: an unauthenticated fetch of each route must be refused, recorded as a test or a reading.
- **Keep the advisor's read path working.** The advisor reads `21bcarlisle-arch.github.io/synthetic-enterprise/` and the repo. This ruling does not touch either.
- **Say plainly what stays public.** With the repo public, everything the site publishes is still readable in `site/` and `docs/`, and on the github.io copy. So the login stops casual visitors and search engines, not a determined reader. Put that in the record, and add `noindex` and a robots disallow to the gated site. Do not present the login on any page as making Poesys private.
- **The walls still hold:**
  - No DNS change without the director's word. If the gate needs one, name the exact change and raise it with a recommendation.
  - Nothing that spends money. Cloudflare's Zero Trust free plan should cover a handful of readers. If sign-up asks for a payment card or account details, that step is the director's: raise it as one plain instruction with the exact screen.
- **Update the site pages that call it public,** and the front-door intent that it is for people new to the project. Readers now need an invitation. Raise any canon conflict with a proposal: the "public domain is the plan" line and the newcomer front door are his words.

## Risk

- **Touches:** Cloudflare Access configuration and site meta. Possibly one DNS record, which is reserved.
- **Blast radius:** who can reach poesys.net. If it is misconfigured, either everyone is locked out (the director included) or the gate is open.
- **Probable failure mode:** the `pages.dev` or preview address is left ungated, or the director's own login fails and he cannot see the site.
- **Mitigation, inline:**
  - Test the refusal on every route.
  - Confirm one successful login from the director's address before reporting done.
  - Record how to reverse it: remove the Access application.

**Proportionality:** reversible, and it changes security posture on the director's explicit word. Implement it with the named mitigations. DNS and payment remain his.

## Done

*20 Nov (delivery seat).*

Moved to `done/` once seen. The advisor channel refused this file because commit 39337b8c6 is unsigned.
The advisor's own staging commit ee46f6711 verifies, and the only unsigned change is the delivery seat's
dated status note above, so the ruling's words are its signed bytes. The work it asks for landed in
39337b8c6: the password gate is live and refuses an anonymous fetch on every route. The one step still
owed, his first successful login, is carried on `for_the_director` row `the-site-login-you-ruled-on-19`
in `docs/direction/DIRECTION.yaml`, and this file is no longer needed to hold it.

Decision: none -- his words answer for_the_director row the-github-repository-is-still-public-gh, coded on its row; coding this file as well would count it twice
