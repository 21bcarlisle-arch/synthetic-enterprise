**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Zero Trust on Free or a password gate; D11 for invited readers; SPAR as a range

**Type:** RULING, through the advisor channel. It answers three `for_the_director` rows. The director's words, from chat, Fri 20 Nov 06:59 GMT, to the advisor's three recommendations in order:

- "Yes, yes, range"

## 1. `the-site-login-you-ruled-on-19`: yes

- **The director does the Cloudflare Zero Trust sign-up himself, on the Free plan.** The advisor has given him the steps. **If the sign-up insists on a card, he declines.** You then build the Pages-Function password gate, which needs no card, without a further ask.
- Wait for his report through the advisor. Do not re-probe Access on every tick: the 05:15 commit already stopped that. When he reports that Zero Trust is on, re-run the read-only probe once, then build the Access policy as the K8 note planned.
- The advisor's view, which he accepted: a per-person login is nicer, but a password page is enough for a site read by him and a few invited people.

## 2. `canon-d11-says-the-public-site-exists`: yes

- Add the one sentence to D11 saying the site is for invited readers, and keep the newcomer test for them. Land it with `Director-doc: his-words` citing this ruling.
- Then update page copy that calls the site public to match.

## 3. `the-bsc-smoothing-parameter-spar-value-it`: range

- He does not offer a value. **Build the blend at both ends of [0.5, 3] and publish the range**, as the row proposed. The hold is beaten everywhere in that range.
- Do not seek MDD access, which is G5.
- Mark SPAR as a GAP with the range on the knowledge page. If a primary source turns up later, narrow it.

Close all three rows with these resolutions.

## Addendum, Fri 20 Nov 07:00 GMT: Zero Trust asked for a card, so build the password gate

The director's words: "Card"

The Zero Trust sign-up asked for a card, and he declined, as ruled in point 1. **Build the Pages-Function password gate now, with no further ask.** Requirements:

- Every route is covered, as listed in the K8 note.
- robots and noindex stay.
- The deploy check reads through the gate.
- The password is never committed, logged or printed. It lives as a Cloudflare secret.
- **How the director gets the password:** generate it on the box and put it in a file under `~/.config/synthetic-enterprise/` with mode 600. Tell the advisor the file's path, never its value. The advisor will tell him how to read it.
- Write down how to reverse it.

Close `the-site-login-you-ruled-on-19` once the gate is live and checked from outside.

## Done

*Delivery seat, executor lane, 20 Nov.*

1. **The site login is a password gate, and it is live.** `functions/_middleware.js` landed in
   ff5b0224b and deployed in run 44699369741 on 40afd359d. Read from outside at 08:10Z:
   - An anonymous fetch is refused (401) on `poesys.net/`, `/data/dashboard.json`, `/proof/`,
     `/api/query`, `poesys-net.pages.dev/` and the deploy's own preview address.
   - `robots.txt` stays open (200), and noindex stays on.
   - The deploy check reads through the gate. Its step was green on that run.
   - With no secret, the gate fails closed (503).

   **For the advisor:** the password is in the file `~/.config/synthetic-enterprise/site_password`
   on the box, mode 600. It is never committed, logged or printed. The reversal is in
   `docs/design/POESYS_NET_BEHIND_A_LOGIN_2026-11-19.md`, under "Amendment, 20 Nov".

   Row `the-site-login-you-ruled-on-19` is closed. The 19 Nov ruling stays open on one step: his
   first successful login.

   *Correction:* the first password was rotated before the gate went live, because a test printed a
   fragment of it into a local log.
2. **D11 carries the sentence**, landed in 1195f44a5 with `Director-doc: his-words`. No page copy
   needed changing. The only page that calls the site public is `site/harness/index.html`'s list
   of principles, which is rendered from D11 itself. Row `canon-d11-says-the-public-site-exists`
   is closed.
3. **SPAR is a range.** Row `the-bsc-smoothing-parameter-spar-value-it` is closed. The build at
   both ends of [0.5, 3] is handed on as continuation `the-spar-blend-at-both-ends-of-the-range`
   (due 27 Nov). It covers the published range and SPAR as a GAP on the knowledge page. There is
   no MDD access.

Five other machine readers of poesys.net will now read the password page. They are filed as
`docs/staging/SEAT_FINDING_FIVE_MACHINE_READERS_OF_POESYS_NET_READ_THE_PASSWORD_PAGE_2026-11-20.md`.

Decision: none -- his words answer three for_the_director rows, each coded on its row (g5 yes, strategy yes, outside_source yes); coding this file as well would count them twice
