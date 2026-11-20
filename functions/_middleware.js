// Cloudflare Pages middleware: the password gate in front of every route of poesys.net,
// poesys-net.pages.dev and the preview addresses. Director ruling 19 Nov ("Website password"),
// addendum 20 Nov 07:00 GMT: Zero Trust asked for a card, so the gate is this function.
// K8 note, routes and reversal: docs/design/POESYS_NET_BEHIND_A_LOGIN_2026-11-19.md.
//
// The password is the Pages secret SITE_PASSWORD. It is never in this repository. With the
// secret unset the gate FAILS CLOSED: every route answers 503 rather than serving the site open.
// It stops casual visitors and search engines. The repository is public, so it does not make
// Poesys private, and no page may say it does.

const COOKIE = "poesys_gate";
const LOGIN_PATH = "/__gate";
// robots.txt stays open so a crawler can read its own refusal.
const OPEN_PATHS = new Set(["/robots.txt"]);
// Machine readers (the deploy check) send the password in this header instead of a cookie.
const READER_HEADER = "X-Poesys-Gate";
const MAX_AGE_SECONDS = 60 * 60 * 24 * 30;
const NOINDEX = { "X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store" };

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  if (OPEN_PATHS.has(url.pathname)) return next();

  const password = (env.SITE_PASSWORD || "").trim();
  if (!password) {
    return page(503, "The site's password gate has no password set, so it serves nothing.", null);
  }
  const token = await cookieToken(password);

  if (url.pathname === LOGIN_PATH) {
    if (request.method !== "POST") return page(401, null, "/");
    const form = await request.formData();
    const back = safeBack(form.get("next"));
    if (await same(String(form.get("password") || "").trim(), password)) {
      return new Response(null, {
        status: 303,
        headers: {
          Location: back,
          "Set-Cookie": `${COOKIE}=${token}; Path=/; Max-Age=${MAX_AGE_SECONDS}; HttpOnly; Secure; SameSite=Lax`,
          ...NOINDEX,
        },
      });
    }
    return page(401, "That password is not right.", back);
  }

  const given = request.headers.get(READER_HEADER);
  if (given !== null && (await same(given.trim(), password))) return next();
  if (await same(readCookie(request, COOKIE), token)) return next();
  return page(401, null, url.pathname + url.search);
}

// The cookie carries a keyed hash of the password, never the password. Changing the secret
// signs every reader out.
async function cookieToken(password) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(password), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode("poesys-gate-v1"));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Compares digests, so the time taken does not depend on where two strings first differ.
async function same(a, b) {
  const [x, y] = await Promise.all([a, b].map((s) =>
    crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(s)))));
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < u.length; i++) diff |= u[i] ^ v[i];
  return diff === 0 && String(a).length > 0;
}

function readCookie(request, name) {
  for (const part of (request.headers.get("Cookie") || "").split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return "";
}

// Only a same-site path: "//host" and absolute URLs would make the login an open redirect.
function safeBack(value) {
  const s = String(value || "/");
  return s.startsWith("/") && !s.startsWith("//") && !s.startsWith("/\\") ? s : "/";
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function page(status, message, back) {
  const form = back === null ? "" : `
  <form method="post" action="${LOGIN_PATH}">
    <input type="hidden" name="next" value="${escapeHtml(back)}">
    <label>Password <input type="password" name="password" autocomplete="current-password" autofocus required></label>
    <button type="submit">Enter</button>
  </form>`;
  const body = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Poesys: invited readers</title>
<style>body{font-family:system-ui,sans-serif;max-width:32rem;margin:4rem auto;padding:0 1rem;line-height:1.5}
input,button{font:inherit;padding:.4rem .6rem;margin:.3rem 0}</style></head>
<body><h1>Poesys</h1>
<p>This site is for invited readers. Enter the password you were given.</p>
${message ? `<p role="alert"><strong>${escapeHtml(message)}</strong></p>` : ""}${form}
</body></html>`;
  return new Response(body, {
    status,
    headers: { "Content-Type": "text/html; charset=utf-8", ...NOINDEX },
  });
}
