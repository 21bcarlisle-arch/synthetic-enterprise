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
// Usage: node _browser_probe.mjs <url> <elementId> [<elementId> ...]   -> JSON on stdout.
import { chromium } from "playwright";

const url = process.argv[2];
const ids = process.argv.slice(3);
if (!url || ids.length === 0) {
  console.error("usage: node _browser_probe.mjs <url> <elementId> [...]");
  process.exit(2);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const pageErrors = [];
page.on("pageerror", (e) => pageErrors.push(String(e.message)));
try {
  await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  // The page's sections render from `fetch(...).then(...)`, so networkidle is necessary but not
  // sufficient -- a render scheduled on the microtask queue after the last response can still be
  // pending. This settles it without pinning a selector the probe is supposed to be neutral about.
  await page.waitForTimeout(800);

  const elements = await page.evaluate((wanted) => {
    const out = {};
    for (const id of wanted) {
      const el = document.getElementById(id);
      if (!el) { out[id] = { exists: false }; continue; }
      const cs = getComputedStyle(el);
      const box = el.getBoundingClientRect();
      out[id] = {
        exists: true,
        // VISIBLE means the reader meets it, which is a conjunction and not a single property:
        // `display:none` on any ancestor, `visibility:hidden`, zero opacity and a collapsed box
        // are four different ways to publish nothing, and each has been a real defect somewhere.
        visible: !!(el.offsetParent !== null || cs.position === "fixed") &&
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

  console.log(JSON.stringify({ ok: true, url, elements, pageErrors }));
} catch (err) {
  console.log(JSON.stringify({ ok: false, url, error: String(err && err.message), pageErrors }));
  process.exitCode = 1;
} finally {
  await browser.close();
}
