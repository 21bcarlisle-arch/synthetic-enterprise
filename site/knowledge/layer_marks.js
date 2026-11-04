// A MARK ON EACH SECTION SAYING WHETHER IT IS KNOWLEDGE OR OUR INSIGHT (director, 4 Nov: "A page
// that mixes the two marks each section"). The marks come from site/data/knowledge_facets.json,
// the same record the index cards and what-we-think.html read: a section named by one of the
// page's insight rows (its `section` field) is marked Insight with that row's status; every other
// section on a mixed page is marked Knowledge, and on an insight page, Insight. A knowledge page
// gets no marks, because its card already says what it is.
//
// The page calls layerMarks("<its directory>") after its own render script. Section headings are
// found by id: the shared Knowledge template's `r-headline` and `h-*` headings, or `k-sec-N` on a
// page that writes its headings in static markup. A heading matches a row when the row's section
// is in the heading's text (the headline's text is its bold lead, not the body after it).
//
// The page renders after its own fetch, and that render overwrites the headings, so the marks
// wait until a heading has text. If the record cannot be read the first heading says so,
// rather than leaving every section unmarked as though it had been checked.
var LAYER_MARK_IDS = ["r-headline", "h-plain", "h-theory", "h-shape", "h-evidence", "h-residuals",
  "h-scope", "h-pain", "k-sec-1", "k-sec-2", "k-sec-3", "k-sec-4", "k-sec-5", "k-sec-6"];

function layerMarkText(html){
  var lead = /^\s*<b>([\s\S]*?)<\/b>/.exec(html);
  return String(lead ? lead[1] : html).replace(/<[^>]*>/g, "")
    .replace(/&mdash;/g, "—").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"');
}

function layerMarkBadge(kind, label, title){
  var colour = kind === "insight" ? "var(--amber)" : "var(--muted)";
  return '<a class="layer-mark layer-' + kind + '" href="../what-we-think.html" title="' +
    String(title).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;") +
    '" style="display:inline-block;margin-right:8px;font-size:9px;font-weight:700;letter-spacing:.05em;' +
    "text-transform:uppercase;text-decoration:none;border-radius:4px;padding:1px 6px;vertical-align:middle;" +
    "color:" + colour + ";border:1px solid " + colour + '">' + label + "</a>";
}

function layerMarkPage(page, els){
  var rows = page.insights || [];
  var fallback = page.layer === "insight" ? "insight" : "knowledge";
  var matched = {};
  els.forEach(function(el){
    if (el.innerHTML.indexOf("layer-mark") >= 0) return;
    var text = layerMarkText(el.innerHTML);
    var mine = rows.filter(function(r){ return r.section && text.indexOf(r.section) >= 0; });
    mine.forEach(function(r){ matched[r.section] = 1; });
    var marks = mine.length
      ? mine.map(function(r){
          var due = !r.review_by || r.review_by < new Date().toISOString().slice(0, 10);
          return layerMarkBadge("insight", "Our insight · " + r.status + (due ? " · review overdue" : ""),
            r.claim + " | Would be shown wrong by: " + r.falsified_by + " | Next review: " + (r.review_by || "none set"));
        }).join("")
      : layerMarkBadge(fallback, fallback === "insight" ? "Our insight" : "Knowledge",
          fallback === "insight" ? "This page is our interpretation, not an outside source."
                                 : "What outside sources state, or what we derive from outside data.");
    el.insertAdjacentHTML("afterbegin", marks);
  });
  // A row whose section names no heading on the page would otherwise vanish silently.
  var lost = rows.filter(function(r){ return !matched[r.section]; });
  if (lost.length && els.length) {
    els[0].insertAdjacentHTML("afterbegin", layerMarkBadge("insight",
      lost.length + (lost.length === 1 ? " insight" : " insights") + " not placed on a section",
      lost.map(function(r){ return r.section + ": " + r.claim; }).join(" | ")));
  }
}

function layerMarks(slug){
  function whenRendered(then){
    var tries = 0;
    (function wait(){
      var els = LAYER_MARK_IDS.map(function(id){ return document.getElementById(id); })
        .filter(function(el){ return el && String(el.innerHTML).trim(); });
      if (els.length) return then(els);
      if (++tries < 100) setTimeout(wait, 100);
    })();
  }
  fetch("../../data/knowledge_facets.json?t=" + Date.now()).then(function(r){ return r.json(); })
    .then(function(facets){
      var page = ((facets || {}).pages || {})[slug];
      if (!page) throw new Error("no facet record for " + slug);
      if (page.layer !== "knowledge") whenRendered(function(els){ layerMarkPage(page, els); });
    })
    .catch(function(e){
      whenRendered(function(els){
        if (els[0].innerHTML.indexOf("layer-mark") >= 0) return;
        els[0].insertAdjacentHTML("afterbegin", layerMarkBadge("insight",
          "Knowledge or insight: the record could not be loaded", String(e)));
      });
    });
}
