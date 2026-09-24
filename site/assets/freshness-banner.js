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
    if (cp.state === "publishing") {
      /* SILENCE IMPLIES CURRENCY, AND AT A WEEKLY CADENCE THAT IS A FALSE IMPRESSION.
         Director, 2026-09-04: "the staleness banner matters more, not less: a week-old site saying
         'as at Monday' is honest, one that implies currency is not." This returned "" — defensible
         when the site republished every half hour, and a lie the moment it publishes weekly, because
         a figure with nothing said about its age reads as now.
         So the healthy state now STATES the as-at date rather than saying nothing. It is not an
         alarm and must not look like one: the caller renders it in the ordinary state, and only the
         `stale` branch below carries the outage wording. */
      if (!cp.as_at_utc) { return ""; }
      var everyDays = Math.round((cp.cadence_seconds || 0) / 86400);
      return "Figures as at " + cp.as_at_utc.replace("T", " ") +
             (everyDays >= 1
               ? " — numbers and runs publish every " + (everyDays === 7 ? "week" : everyDays + " days") + "."
               : ".");
    }
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

  /* ------------------------------------------------------------------------
   * "NOT DUE YET" AND "TRIED AND FAILED" ARE DIFFERENT FACTS (2026-09-24).
   *
   * Everything above this point is an AGE against a threshold, and an age can
   * only become a fault when its threshold comes due. At the weekly cadence
   * that threshold is eight days, so on 2026-09-24 the banner rendered its
   * ordinary healthy branch -- "Figures as at 2026-09-21 18:15" -- while the
   * publisher had refused 45 consecutive attempts across 59 hours with a run
   * queued behind it. Nothing on the page was false. The "PUBLISHING IS DOWN"
   * wording simply could not fire for another five days, whatever happened in
   * between, because no sentence here was keyed to the publisher at all.
   *
   * A page confidently healthy about the one thing a reader can check without
   * us is worse than a page that says nothing. So the publisher's own refusal
   * record now has a sentence, and it does not wait for the cadence.
   *
   * THE AS-AT LINE STAYS. It is the half that is right: the figures ARE from
   * 2026-09-21 and a reader is entitled to that date. What was missing beside
   * it is that nothing is coming to replace it.
   * --------------------------------------------------------------------------*/
  function publisherIsFailing(hb) {
    var cp = (hb && hb.content_publish) || null;
    var p = (cp && cp.publisher) || null;
    /* FAILING is the only state that makes a claim here. `unknown` (absent or unreadable
       record) and `no_open_episode` are NOT evidence of health -- the record is the
       publisher's self-report, believed when it admits failure and worth nothing when it
       does not -- so neither is allowed to render a reassurance, and neither is allowed to
       render an alarm either. The content clocks above remain what establishes currency. */
    return !!p && p.state === "failing";
  }

  function publisherFailureSentence(hb) {
    if (!publisherIsFailing(hb)) { return ""; }
    var p = hb.content_publish.publisher;
    var n = typeof p.consecutive_failures === "number" ? p.consecutive_failures : null;
    var secs = typeof p.failing_for_seconds === "number" ? p.failing_for_seconds : null;
    /* Each clause is dropped rather than guessed when its number is missing, for the same
       reason the as-at line prints nothing without a date: a half-sentence with an invented
       count would be the fake-fresh sin pointed the other way. */
    return "PUBLISHING IS FAILING — " +
      (n === null ? "the publisher has recorded an open run of failed publish attempts"
                  : "the last " + n + " attempt" + (n === 1 ? "" : "s") + " to publish " +
                    (n === 1 ? "failed" : "all failed")) +
      (secs === null ? "" : ", over " + (secs / 3600).toFixed(1) + "h") +
      ". Nothing above this line will be replaced until that is fixed, whatever the " +
      "as-at date says." +
      publisherCauseSentence(p);
  }

  /* THE SECOND COMPOSER OF THE SAME SENTENCE (2026-09-24).
   *
   * What stood here was `p.cited_red_at_head === "dead" ? " The publisher names no live
   * cause for it." : ""`, and it was wrong the same two ways `publish_freshness._cause_clause`
   * was -- this is the visible half of that repair, landed behind it.
   *
   * FIRST, "names no live cause" was FALSE. On 2026-09-24 `.publish_gate_state.json` held
   * `liveness_surface_refusal: {"cause": "push_never_landed", "git_hash": "18cc753b7...",
   * "evidence": "... git ls-remote says origin did not advance to it (push rc=1, ...)"}`
   * while the field this clause read said there was nothing to cite. A cause was in hand.
   *
   * SECOND, it was keyed to ONE reading. `not_established` is what the citation field says
   * whenever no red is named at all -- every push failure, provenance refusal and
   * behind-origin refusal -- and on all of those this clause rendered nothing whatever.
   * The louder defect fired less often.
   *
   * So the branch is on whether the citation ANSWERS the question. Only "reproduces" does;
   * everything else sends the reader to the cause the record is already holding, which
   * `publisher.held_refusal` now carries in the heartbeat. A reader who is told publishing
   * is failing and given no cause goes and runs the suite by hand, which is exactly what
   * happened and exactly what this exists to stop.
   *
   * NO CAUSE AND NO EVIDENCE IS STILL SAID OUT LOUD -- a failure with no named cause is
   * worse news than one with a cause, which was the original clause's point and is kept.
   * The `held_refusal_reason` is NOT rendered here: it names internal state-file fields,
   * which belong in the log line and not on a page a customer may read. The page gets the
   * fact; `publish_freshness.describe()` gets the fields. */
  function publisherCauseSentence(p) {
    /* A citation that re-ran at HEAD and is still red IS the answer, and the health page
       carries the blocking list. Saying more here would give a reader two places to look. */
    if (p.cited_red_at_head === "reproduces") { return ""; }
    var held = p.held_refusal;
    if (held && typeof held.cause === "string" && held.cause) {
      var sha = typeof held.git_hash === "string" ? held.git_hash.slice(0, 9) : null;
      return " The publisher's own record names the cause: " + held.cause +
             (sha ? " at commit " + sha : "") + ".";
    }
    return " The publisher names no live cause for it.";
  }

  /* ------------------------------------------------------------------------
   * A FROZEN FEED CANNOT REPORT ITS OWN FRESHNESS (2026-09-24).
   *
   * Everything above this point -- the as-at line, the "PUBLISHING IS DOWN"
   * age, and the "PUBLISHING IS FAILING" refusal record landed earlier today
   * -- is read out of `tick_heartbeat.json`. That file reaches a reader only
   * when a publish SUCCEEDS. So the one outage none of them can see is the
   * one where publishing stops altogether: the browser keeps serving the last
   * copy that made it out, and every field in it is frozen at the values it
   * held at the last SUCCESSFUL publish -- `published_age_seconds` near zero,
   * `publisher.state` healthy, because at that instant they were.
   *
   * Reproduced against the real asset at origin/main on 2026-09-24, with a
   * feed frozen on 2026-09-01 (23 days):
   *
   *   state : verified
   *   text  : "Figures as at 2026-09-01 07:00Z -- numbers and runs publish
   *            every week."
   *
   * Not one of the three repairs above can fire there, however long the dark
   * runs, because each asks the frozen artefact how old the frozen artefact
   * is. Today's repair made the publisher's refusal VISIBLE; it did not make
   * it DELIVERABLE, and a banner that can only warn you while the channel it
   * warns through is working is fail-open exactly where it matters.
   *
   * So this one verdict is not read from the feed. `ts_iso` is stamped into
   * the file when it is WRITTEN; the clock in front of the reader is the one
   * thing the outage cannot freeze. Their difference is the true age of the
   * last known good publish, and it grows on its own whatever the feed says.
   * --------------------------------------------------------------------------*/

  /* The reader's clock minus the feed's own write stamp. `null` when the feed carries no
     readable stamp -- ABSENT IS NEVER ZERO here, because a missing stamp is precisely how a
     silent freeze would present if we let it default. */
  function observedFeedAgeSeconds(hb) {
    var stamp = hb && hb.ts_iso;
    if (typeof stamp !== "string" || !stamp) { return null; }
    var t = Date.parse(stamp);
    if (isNaN(t)) { return null; }
    return (Date.now() - t) / 1000;
  }

  /* What the feed itself says "too old" means. The heartbeat reaches the site on the PUBLISH
     cadence, not on the tick cadence it is written at, so its own `stale_after_seconds`
     (cadence + grace) is the right tolerance to hold it to -- and holding it to the feed's own
     declared number is what keeps this keyed to the property rather than to a literal here. */
  function declaredStaleAfterSeconds(cp) {
    if (!cp) { return null; }
    if (typeof cp.stale_after_seconds === "number" && cp.stale_after_seconds > 0) {
      return cp.stale_after_seconds;
    }
    if (typeof cp.cadence_seconds === "number" && cp.cadence_seconds > 0) {
      return cp.cadence_seconds;
    }
    return null;
  }

  /* A reader's clock can disagree with ours honestly -- a laptop an hour out is ordinary, and
     alarming on it would train readers to ignore this line. Beyond that the disagreement is
     itself the news, because it means no age on this page can be checked. */
  var CLOCK_SKEW_TOLERANCE_SECONDS = 3600;

  /* THIS CLAUSE SPEAKS ONLY WHEN IT CAN ESTABLISH SOMETHING, and that is a NARROWING worth
     naming rather than dressing up as fail-closed.
     The fail-closed instinct says an absent write stamp, an absent cadence or a reader's clock
     that disagrees should each get a sentence. Each was drafted here and each was wrong:
       - an absent heartbeat is ALREADY ruled on -- the layer is deliberately quiet, because one
         missing file suppressing a true banner trades a real signal for a theoretical one;
       - an absent cadence is the ordinary state of most fixtures and some pages, so a sentence
         there would fire on healthy pages and train readers past the line that matters --
         which is the 2026-08-24 noise ruling, arriving through its own repair.
     Both absences are defects in the feed's PRODUCER and belong on its surface, not shouted at
     a reader who can do nothing with them.
     The narrowing is therefore load-bearing, so the live path is held by a control rather than
     by this comment: `test_the_live_published_feed_carries_the_two_fields_this_check_needs`
     asks the artefact a browser actually fetches whether it can be graded at all. Without it a
     producer that quietly stopped emitting `ts_iso` would disable this sentence on the real
     site without reddening one fixture-driven test. */
  function feedNotArrivingSentence(hb) {
    var cp = (hb && hb.content_publish) || null;
    var age = observedFeedAgeSeconds(hb);
    if (age === null) { return ""; }
    /* A reader's clock behind the stamp cannot establish staleness -- and must not be read as
       freshness either, which is why it returns silence rather than a healthy verdict. */
    if (age < -CLOCK_SKEW_TOLERANCE_SECONDS) { return ""; }
    var limit = declaredStaleAfterSeconds(cp);
    if (limit === null) { return ""; }
    if (age <= limit) { return ""; }
    /* The number reported is the one the verdict rests on -- the reader's clock against the
       stamp -- and the sentence names that, because it will not agree with the age the feed
       reports about itself, and a reader meeting two ages deserves to know which is which. */
    return "THIS PAGE IS NOT ARRIVING — nothing has reached the site for " +
           (age / 86400).toFixed(1) + " days, measured on your clock against the feed's own " +
           "write stamp, and it is meant to publish at least every " +
           (limit / 86400).toFixed(1) + " days. Every age this page reports about itself " +
           "stopped moving then, so treat them all as at least that old.";
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
           (reds ? " and " + reds + " non-blocking test red" + (reds === 1 ? "" : "s") +
                   redTreeClause(a) + redAgeClause(a) : "") +
           " elsewhere in the repository — these are not defects in the figures above; " +
           "the suite that produces and renders them is green.";
  }

  /* WHEN the red count was taken, on the surface rather than in the JSON (2026-09-03).
     `checked_at` has been in this feed all along and no reader has ever met it. The count
     beside it is produced by a suite that runs inside whatever the publish path has left, so
     when that suite stops finishing, the annotation block simply stops moving — inside a file
     that is rewritten every cycle, which is what made it invisible. Observed: the live banner
     carried a red counted at 06:22Z on 2026-09-01 for two full days, next to a provenance file
     with that afternoon's mtime.

     THE TREE CLAUSE COULD NOT CATCH THIS. It names the commit the count was taken on, and a
     commit hash does not tell a reader it is two days old — a reader would have to go and look
     it up, which is the same as not being told. Age is a different question from tree and gets
     its own clause.

     Silent under a day, deliberately: the count is refreshed hourly at best and a "0 days old"
     on every page would be noise that trains readers to skip the sentence the one time it
     matters. An unreadable or absent `checked_at` says so rather than being dropped — this
     whole clause exists because an absent clock read as a current one. */
  function redAgeClause(a) {
    /* `nonblocking_reds_checked_at`, NOT `checked_at`. The two halves of this annotation have
       different freshness: findings are a directory listing refreshed on every path, reds come
       from a suite that has not finished since 2026-09-01. `checked_at` moves whenever EITHER
       half is written, so reading it here would report the cheap half's freshness as the
       expensive half's and this clause would never fire — which is precisely the defect it was
       added for, arriving through its own repair. */
    var at = a && a.nonblocking_reds_checked_at;
    if (!at) { return " (when it was counted is unrecorded)"; }
    var t = Date.parse(at);
    if (isNaN(t)) { return " (when it was counted is unreadable)"; }
    var days = Math.floor((Date.now() - t) / 86400000);
    if (days < 1) { return ""; }
    return " and last counted " + days + " day" + (days === 1 ? "" : "s") +
           " ago, so it may no longer be true";
  }

  /* WHICH TREE THE RED COUNT WAS TAKEN ON, on the surface rather than in the JSON (2026-08-31).
     The count is produced by a suite run in the shared working tree, which carries several
     lanes' uncommitted work; the banner beside it names the published COMMIT. A reader joined
     the two and got a number about neither. Observed on the live endpoint: 66 reds published
     next to git_commit d1ba6bd46, counted on a tree that also held an uncommitted change
     reddening ~1,760 tests.

     ABSENT reads as UNRECORDED, never as the commit. Every artefact written before today has no
     measured_on, and defaulting those to the commit would retro-fit a claim nobody made — the
     misattribution this whole change exists to remove, applied to the entire back catalogue. */
  function redTreeClause(a) {
    var m = a && a.nonblocking_reds_measured_on;
    if (!m || !m.tree_state || !m.git_commit) {
      return " (counted on an unrecorded tree)";
    }
    if (m.tree_state === "commit") {
      return " counted at " + m.git_commit;
    }
    return " counted on the working tree at " + m.git_commit +
           ", which carried uncommitted work — so the count is not a property of that commit";
  }

  /* THE VERDICT COMES FROM THE STATE, NEVER FROM WHETHER A SENTENCE WAS RENDERED.
     Until 2026-09-04 the caller used the truthiness of `stalenessSentence(...)` as the verdict:
     any sentence at all meant "stale". That held only while the healthy branch returned "", and it
     broke the moment the healthy branch had something honest to say -- an as-at date turned a
     perfectly healthy weekly publish into a rendered outage. A verdict derived from a presentation
     artefact is not a verdict; the state is the fact and the sentence is how it reads. */
  function isStalePublish(hb) {
    var cp = (hb && hb.content_publish) || null;
    return !!cp && (cp.state === "stale" || cp.state === "unpublished" || cp.state === "unknown");
  }

  function render(d, unknown, hb) {
    var noFigures = carriesNoFigures();
    var stale = (unknown || noFigures) ? "" : stalenessSentence(hb);
    var failing = (unknown || noFigures) ? "" : publisherFailureSentence(hb);
    /* The frozen-feed check is the only one that survives the channel going dark, so it is
       asked even though the two above have already been asked. A reference page still asserts
       no figure age -- but it IS still served by this publisher, so "nothing is arriving" is
       true there too and stays. */
    /* SCOPED EXACTLY LIKE THE OTHER TWO, and it is not obvious that it should be. A reference
       page served from a site that stopped publishing three weeks ago IS three weeks old, and
       the argument for telling its reader is the same argument as everywhere else.
       Against that stands the 2026-08-24 ruling that publishing status on a page carrying no
       simulation figure is noise which undermines the honest banners elsewhere -- and that
       ruling is recorded, while this reading of it is mine. Reversing it is a judgement about
       what a reference page is FOR, which is not this repair's subject, so it keeps the
       existing scope and the disagreement is filed rather than settled here. */
    var notArriving = (unknown || noFigures) ? "" : feedNotArrivingSentence(hb);
    /* THREE SUBJECTS, ONE VERDICT FOR THE BAR. The age says the deadline has not come; the
       refusal says the thing that would meet it is broken; the write stamp says nothing has
       reached the reader at all. Any of the three is enough to make the bar loud. */
    var publishIsDown = !(unknown || noFigures) &&
      (!!notArriving || isStalePublish(hb) || publisherIsFailing(hb));
    var bar = document.createElement("div");
    bar.className = "poesys-freshness";
    /* A stale publish OUTRANKS a green verification for the banner's state, because it outranks
       it for the reader: "verified" describes the run these figures came from, and "stale"
       describes whether the page is showing that run at all. */
    bar.setAttribute("data-freshness-state",
      unknown ? "unknown"
              : (noFigures ? "reference"
                           : (publishIsDown ? "stale" : ((d && d.verification_state) || "paused"))));
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

    /* The refusal goes ABOVE the as-at line, because it changes how that line should be read:
       "figures as at Monday" means one thing beside a working publisher and another beside one
       that has failed forty-five times since. */
    /* ABOVE the refusal, which is above the as-at line: same reasoning one turn further out.
       "The publisher has failed 52 times" is read differently once you know that this very
       page is a copy that stopped arriving three days ago -- including that sentence itself. */
    bar.innerHTML =
      '<span class="pf-line">' + line + "</span>" +
      (notArriving ? '<span class="pf-notarriving">' + esc(notArriving) + "</span>" : "") +
      (failing ? '<span class="pf-failing">' + esc(failing) + "</span>" : "") +
      (stale ? '<span class="pf-stale">' + esc(stale) + "</span>" : "") +
      (note ? '<span class="pf-note">' + esc(note) + "</span>" : "");

    var style = document.createElement("style");
    style.textContent =
      ".poesys-freshness{font-family:var(--font-house,system-ui);font-size:11.5px;line-height:1.5;" +
      "padding:8px 22px;border-bottom:1px solid var(--border,#ddd);color:var(--muted,#666);" +
      "background:var(--surface,#fff);display:block}" +
      ".poesys-freshness .pf-note{display:block;margin-top:3px}" +
      ".poesys-freshness .pf-stale{display:block;margin-top:3px;font-weight:700}" +
      ".poesys-freshness .pf-failing{display:block;margin-top:3px;font-weight:700}" +
      ".poesys-freshness .pf-notarriving{display:block;margin-top:3px;font-weight:700}" +
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
