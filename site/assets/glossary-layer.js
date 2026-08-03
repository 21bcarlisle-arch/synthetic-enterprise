/* ============================================================================
 * Poesys GLOSSARY LAYER  (SITE_CONSTITUTION.md migration item 8, "glossary layer")
 * ----------------------------------------------------------------------------
 * PURPOSE. The constitution's cross-cutting last-mile asks for a glossary LAYER,
 * not a glossary PAGE. The page already existed: 26 terms at /glossary/. What did
 * not exist was the layer -- the property that a term used ON a door is
 * inspectable FROM that door. A reader hitting "SSP" mid-sentence on /proof/ had
 * to know the glossary existed, leave the page, search it, and come back.
 *
 * WHAT THIS IS. One asset, one data source. A door opts in with two lines:
 *
 *     <script src="../assets/glossary-layer.js" defer></script>
 *     ... the company prices through the realised
 *     <span data-gloss="System Sell Price">SSP</span> path ...
 *
 * and every marked term becomes a permalink into the glossary card for that term,
 * carrying the definition as its native title so it is inspectable in place.
 *
 * WHY DATA-DRIVEN, NOT AUTHORED. site/data/glossary.json stays the single source
 * of every definition (binding rule 3: the site is a rendering, never an author).
 * A door never restates a definition in its own markup -- it names a term and the
 * layer resolves it. So a definition edited once is corrected everywhere, and a
 * door cannot drift its own private gloss of a term.
 *
 * FAIL-LOUD, NOT FAIL-SILENT (R15). The obvious failure mode here is silent: a
 * door marks up `data-gloss="Sytem Sell Price"`, the lookup misses, and the term
 * renders as ordinary text that nobody notices is dead. This layer therefore
 *   - records every unresolved term on `window.PoesysGlossary.unresolved`, and
 *   - marks the element `data-gloss-state="unresolved"` in the DOM,
 * so both a test and the R11 live verifier can assert the list is EMPTY. A layer
 * whose misses are invisible is worth less than no layer at all.
 *
 * SLUG CONTRACT. `slug()` below must produce the same id that
 * site/glossary/index.html renders on each term card. The rule is duplicated in
 * that page on purpose (it must stay self-contained for the live harness, which
 * evaluates inline scripts only) and the two are pinned together by
 * site/test_glossary_layer.py::test_slug_contract_matches_between_page_and_layer.
 * ==========================================================================*/
(function (global) {
  "use strict";

  var API = {
    /* term -> anchor id. Lower-case, unicode dashes normalised to ascii, every
     * run of non-alphanumerics collapsed to a single hyphen, ends trimmed. */
    slug: function (term) {
      return "t-" + String(term == null ? "" : term)
        .toLowerCase()
        .replace(/[‐-―]/g, "-")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
    },

    /* Index a glossary feed by every name a door may legitimately use: the full
     * term and its abbreviation, both case-folded. Returns a plain object so it
     * is inspectable from a test and from the console. */
    index: function (feed) {
      var byKey = {};
      var terms = (feed && feed.terms) || [];
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i];
        if (!t || !t.term) continue;
        byKey[String(t.term).toLowerCase()] = t;
        if (t.abbr) byKey[String(t.abbr).toLowerCase()] = t;
      }
      return byKey;
    },

    /* Populated by apply(); the door's own report card. */
    resolved: [],
    unresolved: [],
    ready: false,

    /* NO ORPHAN TRANSITIONS (R11). A non-anchor element cannot carry a real
     * `href`, so apply() records the permalink on `data-gloss-href` -- and an
     * attribute nothing acts on is precisely the "release whose effect is
     * nothing" R11 calls a defect. This is that effect: ONE delegated listener,
     * installed once, that makes the recorded permalink actually navigate.
     * Exposed by name so a test can invoke it rather than trusting that a click
     * would have worked. */
    handleClick: function (target) {
      var el = target;
      while (el && (!el.getAttribute || !el.getAttribute("data-gloss-href"))) {
        el = el.parentNode;
      }
      if (!el || !el.getAttribute) return null;
      var href = el.getAttribute("data-gloss-href");
      if (!href) return null;
      if (global.location) global.location.href = href;
      return href;
    },

    /* Decorate every [data-gloss] element in `root` against `feed`.
     * Returns {resolved, unresolved} so a caller can assert on it synchronously. */
    apply: function (feed, root, glossaryBase) {
      var doc = (root && root.ownerDocument) || global.document;
      var scope = root || (global.document && global.document.body);
      var base = glossaryBase || "../glossary/";
      var byKey = API.index(feed);
      var resolved = [];
      var unresolved = [];

      var nodes = (scope && scope.querySelectorAll)
        ? scope.querySelectorAll("[data-gloss]") : [];

      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        // The term may be named explicitly or taken from the visible text.
        var name = el.getAttribute("data-gloss");
        if (!name) name = el.textContent || "";
        name = String(name).trim();
        var hit = byKey[name.toLowerCase()];

        if (!hit) {
          unresolved.push(name);
          el.setAttribute("data-gloss-state", "unresolved");
          continue;
        }

        var href = base + "#" + API.slug(hit.term);
        // An <a> already in the markup is retargeted in place; anything else gets
        // the link behaviour without being restructured (doors keep their own DOM).
        if (el.tagName && String(el.tagName).toLowerCase() === "a") {
          el.setAttribute("href", href);
        } else {
          el.setAttribute("data-gloss-href", href);
          if (el.style) el.style.cursor = "help";
        }
        el.setAttribute("title", hit.term + " -- " + hit.definition);
        el.setAttribute("data-gloss-state", "resolved");
        if (el.classList && el.classList.add) el.classList.add("gloss-term");
        resolved.push(hit.term);
      }

      API.resolved = resolved;
      API.unresolved = unresolved;
      API.ready = true;
      if (doc && unresolved.length && global.console && global.console.warn) {
        global.console.warn("glossary layer: unresolved terms", unresolved);
      }
      return { resolved: resolved, unresolved: unresolved };
    },

    /* Fetch the feed and apply. Path is resolved from the script tag's own
     * data-glossary-src when present, so a door at a different depth can point it
     * at the right place without editing this file. */
    boot: function () {
      var doc = global.document;
      if (!doc) return;
      var tag = doc.querySelector ? doc.querySelector("script[data-glossary-src]") : null;
      var src = (tag && tag.getAttribute("data-glossary-src")) || "../data/glossary.json";
      var base = (tag && tag.getAttribute("data-glossary-base")) || "../glossary/";
      if (!global.fetch) return;
      global.fetch(src)
        .then(function (r) { return r.json(); })
        .then(function (feed) { API.apply(feed, doc.body, base); })
        .catch(function () {
          // Deliberately quiet in the DOM: a missing glossary feed must not paint
          // an error over a door whose own content loaded fine. It is still loud
          // where it counts -- `ready` stays false, which the tests assert on.
          API.ready = false;
        });
    },
  };

  global.PoesysGlossary = API;

  if (global.document && global.document.addEventListener) {
    global.document.addEventListener("DOMContentLoaded", API.boot);
    global.document.addEventListener("click", function (ev) {
      if (ev && ev.target) API.handleClick(ev.target);
    });
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
