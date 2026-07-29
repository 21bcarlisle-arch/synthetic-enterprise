# PHONE_SIGNER_SETUP — sign a director ruling from your phone, no terminal

> **This is a document, not a console session.** The advisor relays it to you one numbered
> step at a time. You (the director) open no terminal for any of the *signing* steps. The two
> one-time setup steps that genuinely cannot be done from a chat window are named honestly in
> **Part A** and in the **Irreducible acts** section — they are "provisioning a secret onto your
> own device", which the ruling (`DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md` §0/§21)
> explicitly allows to be device-bound.

**Source:** `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md`, WORK-THIS-CREATES #1.
**Built against the existing, R15-proven mechanism** (2026-07-22 `41aaf4dfc`/`cd8b953ca`; worker-forgery
gap closed 2026-07-23 `6d81a7b08`). No new daemon mechanism is added here — this enumerates how you
*use* it from a phone. Every "expected result" below quotes the real function that produces it.
**Exit gate:** the sibling terminal-audit atom (`phone_signer_terminal_audit`, WORK-THIS-CREATES #3)
must pass before #1 is marked done. **Latency dep:** director acts already draw rung-zero
(`director_act_rung_zero_draw`, DONE) — a signature you send releases its atom on the *next* tick.

---

## What you are setting up (one sentence)

A ruling you send is a single line of text, posted to your ntfy topic like any steering message —
but with a signature on the end that proves it came from you. The daemon verifies the signature and
releases the named atom. **One tap = one authorised act.**

The line looks exactly like this:

```
RULING:<ACTION>:<atom>|<unix_seconds>|<64-hex-signature>
```

You never compute the signature by hand. A tiny offline page on your phone (Part A, step A3) does it.

---

## Part A — one-time setup (do once, ever)

### Step A1 — Confirm the daemon already holds the key
- **Action:** none for you. The signing key `SE_WAKE_HMAC_KEY` already exists on the daemon host,
  stored **out of the repository** (`~/.config/synthetic-enterprise/`, or the gitignored
  `background/.env.ntfy`), and is **stripped from every model-facing process** so the agent cannot
  sign as you.
- **Expected result:** the key is loaded only by daemon-side code that reads its *own* process env.
  Verified by: `background/secrets_location.py:40` (`MODEL_FACING_FORBIDDEN_SECRETS =
  frozenset({"SE_WAKE_HMAC_KEY"})`) and `scrub_model_facing_env()` (line 43), called by every
  spawner. `git check-ignore background/.env.ntfy` returns the path — it is not in the repo.

### Step A2 — Get the *same* key onto your phone (IRREDUCIBLE — device-bound, not a terminal)
The signature uses one symmetric key: whoever verifies can also sign, so your phone must hold the
identical `SE_WAKE_HMAC_KEY`. Getting a 32-byte secret onto a phone **without sending it through any
chat, writing it to the repo, or logging it** is an out-of-band transfer — the one act the ruling
says is legitimately device-bound.
- **Action (choose one, both out-of-band):**
  1. **QR scan (recommended, nothing typed):** on the daemon screen, render the key as a QR code
     shown *locally* (never posted anywhere) and scan it into the signer page below. The bytes travel
     screen→camera, not over any network or chat.
  2. **Manual entry:** read the hex key off the daemon screen and type it once into the signer page.
- **Expected result:** the key lives in your phone's signer page (browser local storage on your
  device) and nowhere else new. It is **never** pasted into a chat, an app you don't control, or a
  file that syncs. This is the "provisioning a secret onto the director's own device" carve-out
  (ruling §0/§21) — done once.
- **Honest note:** if you'd rather not store the key in a browser page, an offline standalone
  HMAC-SHA256 calculator app works too, but it means trusting a third-party app with the key. The
  self-contained page below keeps the key on a page whose source you can read in full.

### Step A3 — Save the offline signer page to your phone
The page below computes the signature entirely on your device (WebCrypto, **no network**). Save it as
a file / "Add to Home Screen" so it's one tap away. It matches the daemon's `sign_wake_message`
byte-for-byte: payload `text|ts`, `HMAC-SHA256`, output `text|ts|hexdigest`
(`background/ntfy_utils.py:51-63`).

```html
<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ruling signer</title>
<style>body{font:16px system-ui;margin:1.2em;max-width:38em}input,textarea,button{font:inherit;width:100%;
box-sizing:border-box;margin:.3em 0;padding:.5em}button{background:#0b5;color:#fff;border:0;border-radius:6px}
#out{user-select:all;word-break:break-all;background:#f2f2f2;padding:.6em;border-radius:6px;min-height:2em}
small{color:#666}</style>
<h3>Sign a director ruling</h3>
<label>Key (paste once; stored on this device only)<br><input id="k" type="password" autocomplete="off"></label>
<label>Action<br>
<select id="a">
 <option>BUILD_OPEN</option><option>LEVEL_UP_PROPOSED</option><option>FRONT_OPEN</option>
 <option>FRONT_CLOSE</option><option>GATE_CLEAR</option><option>HELD_PENDING_VERIFICATION</option>
 <option>GRADUATE</option>
</select></label>
<label>Atom id<br><input id="m" autocomplete="off" placeholder="e.g. privacy_policy_page"></label>
<button onclick="save()">Save key on this device</button>
<button onclick="sign()">Sign →</button>
<p><small>Copy the whole line below and send it to your ntfy topic.</small></p>
<div id="out"></div>
<script>
const enc=new TextEncoder();
function save(){localStorage.se_key=k.value.trim();k.value=localStorage.se_key?'':k.value;
 out.textContent=localStorage.se_key?'Key saved on this device.':'No key entered.';}
if(localStorage.se_key)k.placeholder='(key already saved on this device)';
async function sign(){
 const key=(k.value.trim()||localStorage.se_key||'');
 if(!key){out.textContent='No key. Enter it and tap "Save key".';return;}
 const text='RULING:'+a.value+':'+m.value.trim();
 const ts=Math.floor(Date.now()/1000);
 const payload=text+'|'+ts;
 const ck=await crypto.subtle.importKey('raw',enc.encode(key),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const sig=await crypto.subtle.sign('HMAC',ck,enc.encode(payload));
 const hex=[...new Uint8Array(sig)].map(b=>b.toString(16).padStart(2,'0')).join('');
 out.textContent=payload+'|'+hex;
}
</script>
```
- **Expected result:** typing an action + atom and tapping **Sign** produces a line
  `RULING:ACTION:atom|ts|hex`. This is exactly what `sign_wake_message("RULING:ACTION:atom")` emits;
  `verify_wake_message` (`ntfy_utils.py:66`) re-derives `hmac_sha256(key,"RULING:ACTION:atom|ts")` and
  compares with `hmac.compare_digest`. Same key → same hex → verifies.

---

## Part B — sign and send a ruling (repeat per act; all phone-only)

### Step B1 — Open the signer page
- **Action:** tap the signer page icon on your home screen.
- **Expected result:** the form appears; your key is already saved (placeholder says so). Offline is
  fine — nothing here needs the network.

### Step B2 — Enter the action and atom
- **Action:** pick the **Action** from the dropdown and type the **atom id** exactly (copy it from
  the advisor's [ACT] message — e.g. `LEVEL_UP_PROPOSED` / `privacy_policy_page`).
- **Expected result:** only the seven allowlisted actions are offered. The daemon default-denies
  anything else: `director_authority_channels.py:65` `ROUTINE_ACTIONS = {BUILD_OPEN, FRONT_OPEN,
  FRONT_CLOSE, GATE_CLEAR, LEVEL_UP_PROPOSED, HELD_PENDING_VERIFICATION, GRADUATE}` and `_routine()`
  (line 91) rejects the rest. A one-way-door act is **not** on this channel and never will be.

### Step B3 — Tap Sign
- **Action:** tap **Sign →**, then tap-hold the output line and **Copy** (the box is `user-select:all`).
- **Expected result:** you hold the full `RULING:...|ts|hex` line. The `(action, atom)` are *inside*
  the signed bytes, so this signature cannot be lifted onto a different atom — `_bound_signed_text`
  (`director_authority_channels.py:97`) binds them; a mismatched replay fails
  `is_valid_director_ntfy` (line 104).

### Step B4 — Send it to your ntfy topic (one tap)
- **Action:** open the **ntfy** app you already use for steering, select your topic, paste the line,
  send. (Same topic as `SE_NTFY_TOPIC` → `https://ntfy.sh/<topic>`.)
- **Expected result:** the message lands as an ordinary inbound. `ntfy_responder.check_once` calls
  `_maybe_ledger_director_ruling(message)` (`ntfy_responder.py:451`) on **every** inbound; for a
  valid signed ruling it calls `record_director_ntfy_ruling` (`gate_authorization.py`), which
  **fail-closed** verifies the HMAC is fresh (within `NTFY_MAX_AGE_SECONDS = 3600`, i.e. send within
  **1 hour** of signing), bound, and allowlisted, then writes one authority ledger entry. An
  unverifiable/stale/reserved/malformed line ledgers **nothing** and is simply staged as an ordinary
  note — no false authority.

### Step B5 — Confirm it was accepted
- **Action:** watch for the responder's echo reply on the topic and the advisor's confirmation.
- **Expected result:** the responder logs
  `[DIRECTOR-RULING ledgered] director_ntfy <action>:<atom> — HMAC-verified inbound; gate authority
  recorded` (`ntfy_responder.py` `_maybe_ledger_director_ruling`) and sends a `director_echo` reply
  (line 455). The ledger entry is what the gate reads; because director acts are **rung-zero**
  (`director_act_rung_zero_draw`, DONE), the atom releases on the **next tick** — you do not wait
  behind cooldown re-stamps.
- **If nothing releases:** the line was rejected (bad key, stale >1h, wrong action, or a typo in the
  atom). Re-sign in the page (Step B3 stamps a fresh `ts`) and resend. Nothing is half-applied — the
  ledger write is all-or-nothing.

---

## Irreducible acts, named honestly (ruling §21 — no console padded back in)

| Step | Phone-doable? | Terminal needed? |
|---|---|---|
| A1 confirm daemon key | n/a (already provisioned daemon-side) | No director act at all |
| **A2 get key onto phone** | Yes (QR scan / one-time manual entry) | **No terminal** — an out-of-band *device* transfer, which the ruling §0/§21 explicitly allows as device-bound |
| A3 save signer page | Yes | No |
| B1–B5 sign & send | Yes (offline page + ntfy app) | No |

**The only genuinely non-chat act is A2** — moving one secret onto your own device, once. It is *not*
a terminal step: no command line, on the daemon or the phone. Everything repeatable (B1–B5) is
phone-only. Daemon-side key provisioning (A1) is a machine act you never perform. This table is the
input to the sibling audit (`phone_signer_terminal_audit`, #3), which will try to trip any hidden
terminal step; if it finds one this table is wrong and must say so.

---

## Reverse / undo
This is a document plus a self-contained HTML snippet — `git revert` of the commit removes it; no
external state is touched, no secret is handled by the agent (the key lives only on the daemon and,
after A2, on your phone). Retract by follow-up NTFY if the walkthrough needs correction.
