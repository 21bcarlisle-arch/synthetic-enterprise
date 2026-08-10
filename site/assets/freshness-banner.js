/* ============================================================================
 * Poesys FRESHNESS BANNER LAYER
 * DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10, properties 1 and 3.
 * ----------------------------------------------------------------------------
 * WHAT A VISITOR MUST ALWAYS BE ABLE TO TELL: what they are looking at, and how
 * current it is. Before this, a door rendered live figures with no statement of
 * when those figures were last VERIFIED -- so a site frozen because verification
 * was paused looked exactly like a site that was up to date. It stayed that way
 * for 25 hours.
 *
 * ONE ASSET, ONE DATA SOURCE, the same shape as glossary-layer.js. A door opts in
 * with one line:
 *
 *     <script src="../assets/freshness-banner.js" defer></script>
 *
 * and gets a banner injected at the top of <body>, driven entirely by
 * site/data/publish_provenance.json. A door never authors its own freshness
 * sentence -- the site is a rendering, never an author -- so a door cannot drift
 * its own private (and stale) claim about how fresh it is.
 *
 * THE BANNER IS LOUDEST WHEN PAUSED, PRESENT WHEN VERIFIED. A verified site still
 * states its verification time and run id, quietly. That is deliberate: a banner
 * that only appears when something is wrong trains a reader to read its ABSENCE
 * as "fine", which makes the layer failing to load indistinguishable from good
 * news. Presence is the signal that the layer is alive.
 *
 * FAIL-LOUD, NOT FAIL-SILENT (R15). The failure mode of a freshness widget is
 * silent: the fetch 404s, nothing renders, and the page looks confidently
 * current. So a fetch/parse failure renders an UNKNOWN banner ("freshness
 * unknown -- provenance unavailable") rather than nothing, and records the fault
 * on window.PoesysFreshness.error so both a test and the R11 live verifier can
 * assert it is null. An unavailable check is a FAILED check; the page says so.
 * ==========================================================================*/
(function () {
  "use strict";

  var STATE = { data: null, error: null, rendered: false };
  window.PoesysFreshness = STATE;

  function dataUrl() {
    /* Doors live at varying depths (/, /company/, /proof/). Resolve against the
       document's own base rather than guessing a relative hop count -- a wrong
       hop count is exactly the silent 404 this layer must not have. */
    return new URL("/data/publish_provenance.json", window.location.origin).href;
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function sentence(d) {
    /* Kept in lockstep with background/publish_provenance.py::banner_line -- the
       publisher logs that sentence, this renders it, and a test asserts the two
       carry the same facts so the log can never describe a page that says
       something else. */
    var showing = (d && d.showing_run) || {};
    var run = showing.run_id || "unknown";
    if (d && d.verification_state === "verified") {
      return "Verified " + esc(showing.verified_at || "unknown") +
             " · showing run " + esc(run);
    }
    var lastVerified = (d && d.last_verified) || {};
    return "Verification paused since " + esc((d && d.paused_since) || "unknown") +
           " · showing run " + esc(run) +
           " (last verified " + esc(lastVerified.verified_at || "never") + ")";
  }

  function annotationSentence(d) {
    var a = (d && d.annotation) || {};
    var findings = a.open_findings || 0;
    var reds = a.nonblocking_reds_total != null
      ? a.nonblocking_reds_total
      : ((a.nonblocking_reds || []).length);
    if (!findings && !reds) { return ""; }
    /* The ruling's own words: "published with N open findings -- see health".
       Stated as a fact about the REPO, never about these figures: these figures
       passed the suite that produces and renders them, which is precisely what
       the scoped gate means and precisely what a reader should take from it. */
    return "Published with " + findings + " open finding" + (findings === 1 ? "" : "s") +
           (reds ? " and " + reds + " non-blocking test red" + (reds === 1 ? "" : "s") : "") +
           " elsewhere in the repository — these are not defects in the figures above; " +
           "the suite that produces and renders them is green.";
  }

  function render(d, unknown) {
    var bar = document.createElement("div");
    bar.className = "poesys-freshness";
    bar.setAttribute("data-freshness-state",
      unknown ? "unknown" : ((d && d.verification_state) || "paused"));
    bar.setAttribute("role", "status");

    var line = unknown
      ? "Freshness unknown — provenance unavailable. Treat every figure on this page as of unknown age."
      : sentence(d);
    var note = unknown ? "" : annotationSentence(d);

    bar.innerHTML =
      '<span class="pf-line">' + line + "</span>" +
      (note ? '<span class="pf-note">' + esc(note) + "</span>" : "");

    var style = document.createElement("style");
    style.textContent =
      ".poesys-freshness{font-family:var(--font-house,system-ui);font-size:11.5px;line-height:1.5;" +
      "padding:8px 22px;border-bottom:1px solid var(--border,#ddd);color:var(--muted,#666);" +
      "background:var(--surface,#fff);display:block}" +
      ".poesys-freshness .pf-note{display:block;margin-top:3px}" +
      '.poesys-freshness[data-freshness-state="paused"],' +
      '.poesys-freshness[data-freshness-state="unknown"]' +
      "{background:var(--amber-soft,#fdf3e0);color:var(--text,#111);font-weight:600}";

    document.head.appendChild(style);
    document.body.insertBefore(bar, document.body.firstChild);
    STATE.rendered = true;
  }

  function boot() {
    fetch(dataUrl(), { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) { throw new Error("HTTP " + r.status); }
        return r.json();
      })
      .then(function (d) { STATE.data = d; render(d, false); })
      .catch(function (e) { STATE.error = String(e); render(null, true); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
