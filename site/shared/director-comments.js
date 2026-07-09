/* Director page comments -- DIRECTOR_COMMENTS_BOX.md.
 *
 * A small floating feedback affordance on every primary site page. Submits
 * directly to a dedicated, comments-only ntfy.sh topic (write-only from this
 * page's perspective -- the site never reads from it). The topic name below
 * is INTENTIONALLY public: an anonymous browser has to know where to POST,
 * so it can provide no protection on its own. The real authentication is the
 * PIN, entered once here and checked SERVER-SIDE by background/
 * director_comments.py before anything is ever staged for review -- this
 * script never validates anything itself, it only collects and sends.
 */
(function () {
  "use strict";

  var COMMENTS_TOPIC = "se-comments-6holneh4HU_fKF2SXcu7FsfwN4arICIk";
  var PIN_STORAGE_KEY = "se_director_comment_pin";

  function currentState() {
    // Best-effort: not every page exposes the same globals, so each lookup
    // is defensive. Covers the common patterns already used across this
    // site (a loaded-data global named D with a meta.generated_at/
    // git_commit, and a highlighted "active" tab/nav element).
    var parts = [];
    try {
      if (typeof window.D === "object" && window.D && window.D.meta) {
        if (window.D.meta.generated_at) parts.push("data=" + window.D.meta.generated_at);
        if (window.D.meta.git_commit) parts.push("commit=" + window.D.meta.git_commit);
      }
    } catch (e) { /* ignore -- best effort only */ }
    try {
      var active = document.querySelector(".active");
      if (active && active.textContent) {
        parts.push("active=" + active.textContent.trim().slice(0, 60));
      }
    } catch (e) { /* ignore */ }
    return parts.join(", ");
  }

  function buildPayload(pin, comment) {
    return (
      "PIN:" + pin + "\n" +
      "PAGE:" + window.location.pathname + window.location.hash + "\n" +
      "STATE:" + currentState() + "\n" +
      "DATA_TS:" + (window.D && window.D.meta ? (window.D.meta.git_commit || window.D.meta.generated_at || "") : "") + "\n" +
      "---\n" + comment
    );
  }

  function submit(pin, comment, onDone) {
    fetch("https://ntfy.sh/" + COMMENTS_TOPIC, {
      method: "POST",
      body: buildPayload(pin, comment),
    })
      .then(function () { onDone(true); })
      .catch(function () { onDone(false); });
  }

  function injectStyles() {
    var style = document.createElement("style");
    style.textContent =
      ".se-comments-fab { position: fixed; bottom: 20px; left: 20px; width: 46px; height: 46px;" +
      " border-radius: 50%; background: #2a6fd6; color: #fff; border: none; font-size: 20px;" +
      " cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,.25); z-index: 9998; }" +
      ".se-comments-fab:hover { background: #1e5fb0; }" +
      ".se-comments-panel { position: fixed; bottom: 76px; left: 20px; width: 320px; max-width: 90vw;" +
      " background: #fff; color: #1a1a1a; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,.3);" +
      " padding: 14px; z-index: 9999; display: none; font-family: system-ui, sans-serif; font-size: 13px; }" +
      ".se-comments-panel.open { display: block; }" +
      ".se-comments-panel h4 { margin: 0 0 8px; font-size: 13px; }" +
      ".se-comments-panel input, .se-comments-panel textarea {" +
      " width: 100%; box-sizing: border-box; margin-bottom: 8px; padding: 6px 8px;" +
      " border: 1px solid #ccc; border-radius: 6px; font-size: 13px; font-family: inherit; }" +
      ".se-comments-panel textarea { min-height: 70px; resize: vertical; }" +
      ".se-comments-panel button.se-submit {" +
      " background: #2a6fd6; color: #fff; border: none; border-radius: 6px; padding: 6px 14px;" +
      " cursor: pointer; font-size: 13px; }" +
      ".se-comments-status { margin-top: 6px; font-size: 12px; color: #555; }";
    document.head.appendChild(style);
  }

  function init() {
    injectStyles();

    var fab = document.createElement("button");
    fab.className = "se-comments-fab";
    fab.title = "Leave a comment (director only)";
    fab.textContent = "💬"; // speech balloon emoji

    var panel = document.createElement("div");
    panel.className = "se-comments-panel";
    var savedPin = "";
    try { savedPin = window.localStorage.getItem(PIN_STORAGE_KEY) || ""; } catch (e) { /* ignore */ }
    panel.innerHTML =
      "<h4>Leave a comment</h4>" +
      "<input type=\"password\" class=\"se-pin\" placeholder=\"PIN\" value=\"" + savedPin.replace(/"/g, "&quot;") + "\">" +
      "<textarea class=\"se-comment\" placeholder=\"What did you notice?\"></textarea>" +
      "<button class=\"se-submit\">Send</button>" +
      "<div class=\"se-comments-status\"></div>";

    document.body.appendChild(fab);
    document.body.appendChild(panel);

    fab.addEventListener("click", function () {
      panel.classList.toggle("open");
    });

    panel.querySelector(".se-submit").addEventListener("click", function () {
      var pinInput = panel.querySelector(".se-pin");
      var commentInput = panel.querySelector(".se-comment");
      var statusEl = panel.querySelector(".se-comments-status");
      var pin = pinInput.value.trim();
      var comment = commentInput.value.trim();
      if (!pin || !comment) {
        statusEl.textContent = "Enter a PIN and a comment.";
        return;
      }
      statusEl.textContent = "Sending...";
      submit(pin, comment, function (ok) {
        if (ok) {
          try { window.localStorage.setItem(PIN_STORAGE_KEY, pin); } catch (e) { /* ignore */ }
          statusEl.textContent = "Sent.";
          commentInput.value = "";
          setTimeout(function () { panel.classList.remove("open"); statusEl.textContent = ""; }, 1200);
        } else {
          statusEl.textContent = "Failed to send -- try again.";
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
