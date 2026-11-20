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
