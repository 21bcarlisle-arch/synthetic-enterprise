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

  /* THE INCLUDING SCRIPT TAG, captured at load because `document.currentScript` is null by the
     time a deferred callback runs. A REFERENCE page -- one that publishes no simulation figure
     -- opts out of the figure-freshness half of this banner with one attribute:

         <script src="../../assets/freshness-banner.js" data-figures="none" defer></script>

     Director, 2026-08-24, on /knowledge/price-cap/: "its own footer says no simulation figure
     appears there, so a freshness warning about figures is noise that undermines the honest
     banners elsewhere. Reference pages shouldn't carry publishing status."

     It is an OPT-OUT FROM A CLAIM, NOT FROM THE BANNER. The layer still renders, because this
     file's own doctrine is that presence is how a reader tells the layer is alive from the
     layer having failed to load -- it just stops asserting an age for figures the page does
     not have. */
  var SELF = document.currentScript;
  function carriesNoFigures() {
    return !!(SELF && SELF.getAttribute("data-figures") === "none");
  }

  function dataUrl() {
    /* Doors live at varying depths (/, /company/, /proof/). Resolve against the
       document's own base rather than guessing a relative hop count -- a wrong
       hop count is exactly the silent 404 this layer must not have. */
    return new URL("/data/publish_provenance.json", window.location.origin).href;
  }

  function heartbeatUrl() {
    return new URL("/data/tick_heartbeat.json", window.location.origin).href;
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

  /* ------------------------------------------------------------------------
   * ALIVE-BUT-UNCHANGED IS NOT ALIVE-AND-PUBLISHING (director, 2026-08-13).
   *
   * The three states above -- verified / paused / unknown -- are all about the
   * GATE, and on 2026-08-13 the gate was GREEN while the publish path had not
   * landed for 21.7 hours: the commit was dying on the pre-commit hook deadline.
   * The banner therefore read "Verified 2026-08-13T17:17:05Z" over figures from
   * the previous day, which is the fake-fresh sin the provenance module names as
   * cardinal -- reached not through a bug in that module but through a deadline
   * the liveness commit could meet and the content commit could not.
   *
   * WHY THE HEARTBEAT AND NOT THE PROVENANCE FILE. The publish-freshness block
   * lives on the LIVENESS surface, which is the surface that keeps publishing
   * precisely when content does not (that is what Fault #1's decoupling bought).
   * A staleness statement carried by the file that freezes with the content
   * could only ever be as current as the freeze it is trying to report.
   *
   * FAIL-SILENT, NOT FAIL-LOUD, on THIS fetch specifically, and the asymmetry is
   * deliberate: a missing provenance file renders UNKNOWN because the page then
   * has no freshness claim at all, whereas a missing heartbeat leaves the
   * verified/paused sentence intact and standing on its own. Escalating a
   * heartbeat 404 to a page-wide alarm would let one absent file blank out a
   * banner that is still telling the truth about verification.
   * --------------------------------------------------------------------------*/
  function stalenessSentence(hb) {
    var cp = (hb && hb.content_publish) || null;
    if (!cp || !cp.state) { return ""; }
    if (cp.state === "publishing") { return ""; }
    if (cp.state === "unknown") {
      return "Publishing status unknown — the age of these figures could not be measured.";
    }
    if (cp.state === "unpublished") {
      return "No verified publish is on record — the age of these figures is unestablished.";
    }
    /* THE VERDICT AND THE NUMBER MUST COME FROM THE SAME CLOCK.
       `publish_freshness.snapshot()` decides `stale` on the OLDER of two ages -- the push
       (`published_age_seconds`) and the last time the figures themselves moved in git
       (`committed_age_seconds`) -- precisely so "a push landed" cannot pass for "the figures
       moved". This sentence then printed the YOUNGER one, and on 2026-08-24 the director was
       shown "PUBLISHING IS DOWN — the figures on this page last reached the site 0.3h ago":
       down on one clock and eighteen minutes fresh on the other, in one sentence.
       It now reports the age the verdict rests on, and names which clock that is. */
    var pubAge = cp.published_age_seconds;
    var comAge = cp.committed_age_seconds;
    var decided = Math.max(
      typeof pubAge === "number" ? pubAge : 0,
      typeof comAge === "number" ? comAge : 0
    );
    var figuresAreOlder = typeof comAge === "number" && comAge >= (pubAge || 0);
    return "PUBLISHING IS DOWN — the figures on this page last " +
           (figuresAreOlder ? "changed " : "reached the site ") +
           (decided / 3600).toFixed(1) + "h ago. Anything above this line is that old, " +
           "whatever the verification line says." +
           (cp.committed_but_unpublished
             ? " (Content is still being committed; the publish path is what stopped.)"
             : "");
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

  function render(d, unknown, hb) {
    var noFigures = carriesNoFigures();
    var stale = (unknown || noFigures) ? "" : stalenessSentence(hb);
    var bar = document.createElement("div");
    bar.className = "poesys-freshness";
    /* A stale publish OUTRANKS a green verification for the banner's state, because it outranks
       it for the reader: "verified" describes the run these figures came from, and "stale"
       describes whether the page is showing that run at all. */
    bar.setAttribute("data-freshness-state",
      unknown ? "unknown"
              : (noFigures ? "reference"
                           : (stale ? "stale" : ((d && d.verification_state) || "paused"))));
    bar.setAttribute("role", "status");

    var line = unknown
      ? "Freshness unknown — provenance unavailable. Treat every figure on this page as of unknown age."
      : (noFigures
          ? "Reference page — nothing here is produced by the simulation, so no figure on it " +
            "has a publish age. Sourced and dated in the page itself."
          : sentence(d));
    /* The open-findings note is about the REPOSITORY, not about these figures, so it stays on
       a reference page: it is the one part of the banner that is still true there. */
    var note = unknown ? "" : annotationSentence(d);

    bar.innerHTML =
      '<span class="pf-line">' + line + "</span>" +
      (stale ? '<span class="pf-stale">' + esc(stale) + "</span>" : "") +
      (note ? '<span class="pf-note">' + esc(note) + "</span>" : "");

    var style = document.createElement("style");
    style.textContent =
      ".poesys-freshness{font-family:var(--font-house,system-ui);font-size:11.5px;line-height:1.5;" +
      "padding:8px 22px;border-bottom:1px solid var(--border,#ddd);color:var(--muted,#666);" +
      "background:var(--surface,#fff);display:block}" +
      ".poesys-freshness .pf-note{display:block;margin-top:3px}" +
      ".poesys-freshness .pf-stale{display:block;margin-top:3px;font-weight:700}" +
      '.poesys-freshness[data-freshness-state="paused"],' +
      '.poesys-freshness[data-freshness-state="unknown"]' +
      "{background:var(--amber-soft,#fdf3e0);color:var(--text,#111);font-weight:600}" +
      /* Louder than paused. A paused site is serving its last verified figures on purpose; a
         stale one is serving figures it believes it has already replaced. */
      '.poesys-freshness[data-freshness-state="stale"]' +
      "{background:var(--red-soft,#fdecea);color:var(--text,#111);font-weight:600;" +
      "border-bottom:2px solid var(--red,#c0392b)}";

    document.head.appendChild(style);
    document.body.insertBefore(bar, document.body.firstChild);
    STATE.rendered = true;
  }

  function heartbeat() {
    /* Resolves to null on any failure -- see stalenessSentence for why this one fetch is allowed
       to be quiet where the provenance fetch is not. */
    return fetch(heartbeatUrl(), { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }

  function boot() {
    Promise.all([
      fetch(dataUrl(), { cache: "no-store" }).then(function (r) {
        if (!r.ok) { throw new Error("HTTP " + r.status); }
        return r.json();
      }),
      heartbeat(),
    ])
      .then(function (both) {
        STATE.data = both[0];
        STATE.heartbeat = both[1];
        render(both[0], false, both[1]);
      })
      .catch(function (e) { STATE.error = String(e); render(null, true, null); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
