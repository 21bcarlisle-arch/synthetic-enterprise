**Severity:** RECORDED · **Lane:** A_strategy_governance · **Authority:** the director's ruling, 19 Nov 14:07 ("Repo public. Website password")

# poesys.net goes behind a login: what is gated, what stays public, how to reverse it

The K8 note for `docs/staging/advisor/done/DIRECTOR_RULING_REPO_STAYS_PUBLIC_AND_THE_WEBSITE_GOES_BEHIND_A_LOGIN_2026-11-19.md`.
Written before any Cloudflare change.

## What the login does and does not do

**It stops casual visitors and search engines. It does not make Poesys private.** The repository
stays public by the same ruling, so every page the site serves is still readable in `site/` and
`docs/`, and on the github.io copy (`21bcarlisle-arch.github.io/synthetic-enterprise/`), which
this work does not touch. A determined reader is not stopped. No page may describe the login as
making Poesys private.

## What gets gated (every route to the same site)

| route | how it is reached today | gate |
|---|---|---|
| `poesys.net/*` | custom domain on the Pages project `poesys-net` | an Access self-hosted application on `poesys.net` |
| `poesys-net.pages.dev/*` | the production Pages address | a second Access application on that hostname. Gating only the custom domain leaves this side door open |
| `*.poesys-net.pages.dev/*` | per-deployment preview addresses | Pages' "access policy" setting for previews, or a wildcard Access application |
| Pages Functions | served under the same hostnames | covered by the hostname-level applications. `site/` has no `functions/` directory today |
| `www.poesys.net` | does not resolve (reading below) | nothing to gate. Adding it would be a DNS change, which is reserved |

Policy: allow by e-mail, with one-time PIN codes. The director's address is the first allowed
reader. Zero Trust Free covers up to 50 users.

**No DNS change is expected.** Access applications sit on hostnames already proxied in the zone.
If the API says otherwise, the change gets named and raised, not made.

## Belt and braces, live now

These landed in `site/robots.txt` and `site/_headers` in d3025b96d0:
`User-agent: * / Disallow: /` and `X-Robots-Tag: noindex, nofollow`. The AI-training blocks from
12 Jul stay, and user-directed fetch (`Claude-User`) stays allowed. Known limit: a crawler that
obeys the disallow never fetches a page, so it never sees the noindex header. A URL can still be
listed bare from inbound links until the gate is up. After that, the Access login page is what
any crawler gets.

## What is not known yet (GAP), and how it gets answered

- **GAP: whether the deploy token can configure Access.** The only Cloudflare credential this
  machine can use is the Actions secret `CLOUDFLARE_API_TOKEN`, minted 22 Jun for Pages deploys.
  The Cloudflare MCP from the 20 Aug grant is not loaded in headless runs. The read-only
  `.github/workflows/cloudflare-access-probe.yml` answers this. It checks whether a Zero Trust
  organisation exists, and whether the token can list Access apps, identity providers and the
  Pages project's domains. It prints status and error codes, never the token or account id.
  *Answered, 19 Nov 16:45Z (Actions run 44569003701): it cannot, because Access is not enabled on
  the account at all. All three Access endpoints answer 403 `access.api.error.not_enabled`, and
  the Zero Trust organisation endpoint answers 403. The token does read the Pages project, which
  serves exactly `poesys-net.pages.dev` and `poesys.net`, so the route table above is the whole
  scope. The first step is the director's Zero Trust sign-up, raised as `for_the_director` row
  `the-site-login-you-ruled-on-19`.*
- **GAP: whether Zero Trust sign-up asks for a payment card.** Sign-up chooses a team name and a
  plan in the dashboard. If it asks for a card, even on Free, that screen is the director's, and
  it is raised as one plain instruction.
- **If the token lacks Access permissions,** a token with *Access: Apps and Policies: Edit* and
  *Access: Organizations, Identity Providers, and Groups: Edit* is the director's to mint. That is
  a credential, and credentials stay his.

## What the gate breaks inside the project, to fix in the same change

Machine readers that fetch `https://poesys.net` unauthenticated will get the login page instead
of the content once the gate is up:

- the deploy workflow's "Assert the deployed commit is what a reader gets"
- `tools/assert_deployed_bytes_are_served.py`
- `tools/retired_paths_still_served.py`
- `background/process_run_complete.py`'s post-publish readers
- `tools/insight_challenge.py`, `tools/couple_w2_11_d5.py` and `tools/generate_project_state.py`

The fix is an Access **service token** (client id and secret headers) held as Actions and local
secrets. That keeps the checks able to fail for the right reason. Lifting the gate for machines
would be the side door the ruling forbids.

## Readings

Before the gate (19 Nov 15:58Z, unauthenticated `curl` with a cache-buster):

| route | status |
|---|---|
| `https://poesys.net/` | 200 |
| `https://poesys.net/data/dashboard.json` | 200 |
| `https://poesys-net.pages.dev/` | 200 |
| `https://www.poesys.net/` | no answer (does not resolve) |

Done means every one of these routes, plus a preview URL, refuses an unauthenticated fetch, and
the director reports one successful login.

## How to reverse it

Delete the Access applications for `poesys.net` and `poesys-net.pages.dev`, and turn off the
preview access policy in the Pages project. Revert the robots and `_headers` lines. Nothing else
changes.

## Amendment, 20 Nov: the gate is a password function, not Access

The director's addendum, Fri 20 Nov 07:00 GMT ("Card"): the Zero Trust sign-up asked for a card
and he declined it, so Access is never enabled and the Access design above is not built. What is
built instead, with no further ask:

- **`functions/_middleware.js`**, a Pages Function in front of every route the Pages project
  serves: `poesys.net`, `poesys-net.pages.dev`, the preview addresses, and `/api/query`. A reader
  without the cookie gets a password page (401, `noindex`, `no-store`). The right password sets an
  HttpOnly cookie for 30 days. The cookie holds a keyed hash of the password, so changing the
  password signs everyone out. Only `/robots.txt` is open, so a crawler can read its own refusal.
- **Fails closed.** With no `SITE_PASSWORD` secret, every route answers 503 and serves nothing.
  A preview deployment that lacks the secret serves nothing for the same reason.
- **The password** is the Pages secret `SITE_PASSWORD`, set on each deploy from the Actions secret
  of the same name, by stdin. The deploy refuses by name if the Actions secret is unset. On this
  box it is in `~/.config/synthetic-enterprise/site_password`, mode 600. It is never committed,
  logged or printed.
- **Machine readers** send it in the `X-Poesys-Gate` header: `reader_headers()` in
  `tools/assert_deployed_bytes_are_served.py` (the deploy check), and
  `tools/retired_paths_still_served.py`. The other readers named above still read as strangers
  and will see the password page. That is a known gap, filed with this change, not a silent one.
- **robots and noindex stay** as landed in d3025b96d0.
- **The github.io copy and the repository are untouched and public.** Pages Functions run only on
  Cloudflare. A password page is enough for the director and a few invited readers (the advisor's
  view, which he accepted). It is not per-person, and a password shared on is not revocable per
  reader. Change the password to revoke everyone.

### How to reverse the password gate

Delete `functions/_middleware.js` and the "Set the site password gate's secret" step in
`.github/workflows/deploy-pages.yml`, then deploy. Optionally delete the Pages secret
(`npx wrangler pages secret delete SITE_PASSWORD --project-name=poesys-net`), the Actions secret
(`gh secret delete SITE_PASSWORD`) and the file on this box. To change the password, overwrite the
file, run `gh secret set SITE_PASSWORD < ~/.config/synthetic-enterprise/site_password`, and
dispatch the deploy workflow.

### Readings after the gate (20 Nov 08:10Z, from outside, cache-busted)

Deploy run 44699369741 on 40afd359d was green on every step, including the secret step and the
post-deploy check reading through the gate.

| route | anonymous | with `X-Poesys-Gate` |
|---|---|---|
| `https://poesys.net/` | 401, the password page | 200 |
| `https://poesys.net/data/dashboard.json` | 401 | 200 |
| `https://poesys.net/proof/` | 401 | not read |
| `https://poesys.net/api/query` | 401 | not read |
| `https://poesys-net.pages.dev/` | 401 | 200 |
| `https://42c9e199.poesys-net.pages.dev/` (this deploy's own address) | 401 | not read |
| `/robots.txt` on both hostnames | 200, by design | |
| a wrong password in the header | 401 | |

A branch preview (a deploy from any branch but `main`) has no production secret, so it fails
closed with a 503. Nothing deploys from another branch today.

*Correction, 20 Nov 08:25Z, beside the table above:* "every route refuses" was read on the newest
deployment only. Every Pages deployment keeps its own immutable `<hash>.poesys-net.pages.dev`
address, serving the files and functions it was built with, so every deployment made before the
gate landed still serves the whole site to anyone. Read from outside: `c156dcf3` (deploy run
44695253280, 07:28Z) and `09a031ce` (run 44588286175, 19 Nov) answered **200** anonymously, beside
`42c9e199` (401). That is the side door the ruling names. The remedy is
`.github/workflows/pages-close-open-deployments.yml`, dispatched by hand: it reads every
deployment's own address anonymously, deletes the ones that answer 200, then re-reads what is left
and fails if any still serves. It is keyed to that property, not to a date. The deleted
deployments can be rebuilt from git (`site/` at the commit each one names). The cost is losing
one-click rollback to a pre-gate deployment, and a rollback to one would take the gate down anyway.
*Swept, 20 Nov 09:01Z:* the read-only run (44701674785) read 3,668 deployments: 3,667 answered 200
anonymously and 2 answered 401. The delete run (44702018437) deleted 3,667 and refused 0. Its re-read
found every remaining deployment refusing an anonymous fetch. Read from outside afterwards:
`c156dcf3` and `09a031ce` answer 404, `42c9e199` 401, and `poesys.net` and `poesys-net.pages.dev` 401.
*Re-read, 21 Nov 06:56Z:* read-only run 44877870397 found 11 deployments, every address 401, none open.
The deletion cannot be undone in Cloudflare. It is rebuildable from git, so no evidence is lost.

The Actions log was searched for every 6-character fragment of the password, and none was found.
*Correction, recorded beside the claim:* the first password was rotated before it went live. A
pre-existing test's assertion diff printed a fragment of it into a local gate log on this box,
because `reader_headers()` read the real file during the test. That test is now isolated from the
file, the log is deleted, and the live password has never been printed.
