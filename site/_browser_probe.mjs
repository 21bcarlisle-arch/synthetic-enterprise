// THE READER-SIDE PROBE: what a person with a browser actually meets on a page.
//
// WHY THIS EXISTS BESIDE `_render_harness.mjs` RATHER THAN REPLACING IT. The vm harness runs the
// page's own render function against a real feed and reports the string it wrote into an element.
// That is strong evidence about the FEED and the WIRING and none at all about RENDERING: its
// `document` mints an element for any id asked of it, its `style` is a plain bag nothing reads,
// its `classList` methods are no-ops, it parses no CSS, and its regex takes only the FIRST inline
// `<script>`. Three constructed breakages that leave a reader looking at nothing all pass it --
// measured 2026-09-17, see docs/design/WHAT_THE_VM_DOORS_GRADE.md.
//
// So this probe answers the other half, and only that half: the element EXISTS, is VISIBLE, has
// BOX, and carries the words. It loads over http from a directory of PUBLISHED bytes (see
// `site/_browser_reading.py`) because a probe pointed at the working tree cannot tell "the reader
// can see this" from "someone in this tree has fixed it and not landed it".
//
// IT IS NOT LIMITED TO LOCALHOST. `site/live_pixel_verify.py` points it at the LIVE deployed host
// (`https://poesys.net/<door>`), which is the one subject no other control in this repository
// reaches with a browser -- the vm verifier proves the live host served the bytes, this proves a
// person can read what they became. When the target IS a live origin, set
// POESYS_BROWSER_CACHE_BUST: see the route handler below for why the page URL alone is not enough.
//
// Usage: node _browser_probe.mjs <url> <elementId> [<elementId> ...]   -> JSON on stdout.
//    or: node _browser_probe.mjs --jobs    with [{url, ids}, ...] on stdin, ONE launch for all.
//
// WHY THE SECOND FORM EXISTS. A chromium launch is ~1.5s and dwarfs the page load that follows it,
// so a control whose subject is EVERY published door pays that cost twenty-two times to ask
// twenty-two questions. `site/test_every_door_element_a_reader_meets.py` is that control and it
// runs in the commit path, where a minute matters; the per-page form above is a door-close tool
// and does not. Same browser, same reading, same `elements` payload per page -- the only thing
// shared between jobs is the process.
import fs from "node:fs";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

// WHY PLAYWRIGHT IS NOT A PLAIN `import`. `node_modules/` is gitignored, so it exists only in the
// MAIN checkout -- and node's ESM resolution walks up from THIS FILE, not from `cwd`. In a linked
// worktree (which is where every autonomous executor turn and every isolated seat invocation
// runs) nothing above this file has a `node_modules`, so `import ... from "playwright"` threw
// ERR_MODULE_NOT_FOUND and the whole browser leg skipped -- reporting "playwright is not
// installed" on a machine that has had it installed throughout. Measured 2026-09-17: 7 of the 8
// browser legs skipped from a worktree, and setting `cwd` fixes the CJS probe while leaving the
// ESM import failing exactly as before, because `cwd` is not what ESM resolves against.
//
// So the caller passes the directory to resolve against in `POESYS_PLAYWRIGHT_BASE` (see
// `site/test_the_browser_reading.py`, which derives it from `git rev-parse --git-common-dir`).
// Plain resolution is tried FIRST so the main checkout needs no environment at all.
async function loadPlaywright() {
  const attempts = [];
  try {
    const ns = await import("playwright");
    return ns.chromium ? ns : ns.default;
  } catch (err) {
    attempts.push(`resolving from ${import.meta.url}: ${err.message}`);
  }
  const base = process.env.POESYS_PLAYWRIGHT_BASE;
  if (base) {
    try {
      // `playwright/index.js` is CJS, so the ESM namespace puts it under `default` -- asking for
      // `ns.chromium` alone returned undefined and failed one call later with a message naming
      // neither playwright nor resolution.
      const resolved = createRequire(base.replace(/\/?$/, "/") + "noop.js").resolve("playwright");
      const ns = await import(pathToFileURL(resolved).href);
      return ns.chromium ? ns : ns.default;
    } catch (err) {
      attempts.push(`resolving from POESYS_PLAYWRIGHT_BASE=${base}: ${err.message}`);
    }
  } else {
    attempts.push("POESYS_PLAYWRIGHT_BASE is unset, so no second location was tried");
  }
  // FAIL CLOSED AND NAME THE REASON. Returning a null browser here would make every leg below
  // report "the element is not visible", which reads as a broken PAGE rather than a missing tool.
  throw new Error(`playwright could not be loaded. ${attempts.join(" | ")}`);
}

const { chromium } = await loadPlaywright();

// THE TWO CALLING FORMS RESOLVE TO ONE LIST OF JOBS, so there is exactly one reading routine below
// and no chance of the batch form and the single form drifting into answering differently.
let jobs;
const batch = process.argv[2] === "--jobs";
if (batch) {
  jobs = JSON.parse(fs.readFileSync(0, "utf8"));
  if (!Array.isArray(jobs) || jobs.length === 0) {
    console.error("usage: node _browser_probe.mjs --jobs   with [{url, ids}, ...] on stdin");
    process.exit(2);
  }
  for (const j of jobs) {
    if (!j || typeof j.url !== "string" || !Array.isArray(j.ids) || j.ids.length === 0) {
      console.error(`every job needs a url and a non-empty ids list; got ${JSON.stringify(j)}`);
      process.exit(2);
    }
  }
} else {
  const url = process.argv[2];
  const ids = process.argv.slice(3);
  if (!url || ids.length === 0) {
    console.error("usage: node _browser_probe.mjs <url> <elementId> [...]");
    process.exit(2);
  }
  jobs = [{ url, ids }];
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
let pageErrors = [];
page.on("pageerror", (e) => pageErrors.push(String(e.message)));

// EVERY SUBRESOURCE IS CACHE-BUSTED, NOT JUST THE PAGE, and that is a property of what THIS probe
// concludes rather than tidiness. `live_pixel_verify.cache_bust` records the incident: the edge
// served deleted pages `200` for eight hours, immune to purge, and a check that concludes
// something is ABSENT or NOT VISIBLE through a cached copy cannot tell absence from staleness.
//
// The page URL is busted by the caller. That is enough for G1/G2/G3, which conclude about the HTML
// and the feeds -- but VISIBILITY is decided by the STYLESHEET, and a stale `assets/*.css` can only
// ever make an element look visible that the current one hides. A false GREEN, which is the
// direction that matters. So the busting happens here, inside the browser, where every request the
// page makes passes through.
//
// FALLS BACK TO THE UNTOUCHED REQUEST ON ANY ERROR. A route handler that throws leaves the request
// hanging until the navigation times out, and the probe would report "the live page did not load"
// on a page that is perfectly fine -- turning a rewriting bug into a false RED on the live site.
const cacheBust = process.env.POESYS_BROWSER_CACHE_BUST;
if (cacheBust) {
  await page.route("**/*", async (route) => {
    try {
      const u = new URL(route.request().url());
      if (u.protocol === "http:" || u.protocol === "https:") {
        u.searchParams.set("cb", cacheBust);
        await route.continue({ url: u.toString() });
        return;
      }
    } catch { /* fall through to the untouched request */ }
    await route.continue();
  });
}

const readings = [];
for (const job of jobs) {
  const { url, ids } = job;
  pageErrors = [];
  try {
  // The RESPONSE is kept: a live origin answering 404 or 503 still produces a DOM, and every
  // element would then read `exists: false` -- which describes a broken page rather than a missing
  // one. The caller gets the status and can say which it met.
  const response = await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  const status = response ? response.status() : null;
  // The page's sections render from `fetch(...).then(...)`, so networkidle is necessary but not
  // sufficient -- a render scheduled on the microtask queue after the last response can still be
  // pending. This settles it without pinning a selector the probe is supposed to be neutral about.
  await page.waitForTimeout(800);

  const elements = await page.evaluate((wanted) => {
    const out = {};
    for (const id of wanted) {
      // `:body` IS THE WHOLE-PAGE READING, and it exists because a door with no client render has
      // no element id to ask about. Without it a STATIC door -- the Front Door, /privacy/ -- would
      // have no reader-side subject at all, and "this control does not cover those" is a hole
      // rather than a design. A shell served by a broken build has a body and no words in it,
      // which is exactly what this reading catches.
      const el = id === ":body" ? document.body : document.getElementById(id);
      if (!el) { out[id] = { exists: false }; continue; }
      const cs = getComputedStyle(el);
      const box = el.getBoundingClientRect();
      out[id] = {
        exists: true,
        // VISIBLE means the reader meets it, which is a conjunction and not a single property:
        // `display:none` on any ancestor, `visibility:hidden`, zero opacity and a collapsed box
        // are four different ways to publish nothing, and each has been a real defect somewhere.
        //
        // `document.body` IS CARVED OUT OF THE offsetParent CLAUSE, not exempted from the others.
        // `offsetParent` is specified to return null for the body element and for the root, the
        // same answer it gives for `display:none` -- so without this the whole-page reading would
        // report every healthy page as invisible, and a control that fires on everything is not a
        // control. `visibility`, `opacity` and the box are all still judged on it.
        //
        // A `cs.display !== "none"` clause was written here to stop that carve-out becoming a
        // blanket exemption, and then DELETED: removing it changed no verdict, because a
        // `display:none` body still collapses its box to 0x0 and the box clause catches it.
        // Mutation-checked 2026-09-17 rather than assumed -- an unfiring mutation is an
        // equivalence or a missing test and must be established, and the flattering answer is
        // not the default. `test_the_WHOLE_PAGE_reading_is_a_real_reading_and_not_a_carve_out`
        // is what holds this, in a real browser, on a real hidden page.
        visible: !!(el.offsetParent !== null || cs.position === "fixed" || el === document.body) &&
                 cs.visibility !== "hidden" && cs.opacity !== "0" &&
                 box.width > 0 && box.height > 0,
        display: cs.display,
        visibility: cs.visibility,
        opacity: cs.opacity,
        width: Math.round(box.width),
        height: Math.round(box.height),
        innerLength: el.innerHTML.length,
        // innerText, NOT textContent: innerText is what the layout engine says is shown, so a
        // CSS-hidden CHILD contributes nothing to it.
        //
        // BUT `text` ALONE IS NOT A VISIBILITY TEST, and the difference was measured rather than
        // assumed (2026-09-17). When the element ITSELF is not rendered, innerText is specified to
        // fall back to textContent -- so a `display:none` on `#deployment` returned the full
        // sentence here while the reader met a zero-height nothing. `visible` above is what
        // catches that; `text` answers only "which words", never "can anyone read them".
        text: el.innerText || "",
      };
    }
    return out;
  }, ids);

  readings.push({ ok: true, url, status, elements, pageErrors });
  } catch (err) {
    // ONE UNREADABLE PAGE MUST NOT COST THE OTHERS THEIR READING, and it must not be reported as a
    // reading either. The job gets `ok: false` with its own error and the loop carries on, so the
    // caller sees which page could not be read AND every verdict it was going to make about the
    // rest. `process.exitCode` is still set, so a caller that only checks the exit code fails
    // closed rather than reading a partial list as a complete one.
    readings.push({ ok: false, url, error: String(err && err.message), pageErrors });
    process.exitCode = 1;
  }
}
await browser.close();

// The single-url form keeps the payload it has always had -- `live_pixel_verify` and the door legs
// read `payload["elements"]` directly, and a wrapper object would break them silently.
console.log(JSON.stringify(
  batch ? { ok: readings.every((r) => r.ok), pages: readings } : readings[0]));
