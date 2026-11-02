(function () {
  function parseQuery(query) {
    var raw = query.trim();
    var quoted = /^["“”'].+["“”']$/.test(raw);
    var q = raw.replace(/^["“”']+|["“”']+$/g, "").replace(/\s+/g, " ").trim();
    return { q: q, quoted: quoted };
  }

  function escapeReg(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function locateForm(hay, q) {
    if (!q || q.length < 2) return null;
    if (/\s/.test(q)) {
      var at = hay.toLowerCase().indexOf(q.toLowerCase());
      if (at < 0) return null;
      return { hay: hay, at: at, length: q.length, query: hay.slice(at, at + q.length) };
    }
    var match = new RegExp("(^|[^A-Za-z0-9/.])(" + escapeReg(q) + ")(?![A-Za-z0-9/.])", "i").exec(hay);
    if (!match) return null;
    return {
      hay: hay,
      at: match.index + match[1].length,
      length: match[2].length,
      query: match[2]
    };
  }

  function groupFor(q) {
    var groups = window.SOURCE_EQUIVALENTS || [];
    var key = q.toLowerCase();
    for (var i = 0; i < groups.length; i++) {
      for (var j = 0; j < groups[i].length; j++) {
        if (groups[i][j].toLowerCase() === key) return groups[i];
      }
    }
    return null;
  }

  function matchSection(text, parsed) {
    var hay = text.replace(/\s+/g, " ").trim();
    var direct = locateForm(hay, parsed.q);
    if (direct) return { found: direct, via: "" };
    if (parsed.quoted) return null;
    var group = groupFor(parsed.q);
    if (!group) return null;
    for (var i = 0; i < group.length; i++) {
      if (group[i].toLowerCase() === parsed.q.toLowerCase()) continue;
      var found = locateForm(hay, group[i]);
      if (found) return { found: found, via: parsed.q };
    }
    return null;
  }

  function snippet(found) {
    var start = Math.max(0, found.at - 48);
    var end = Math.min(found.hay.length, found.at + found.length + 48);
    return {
      before: (start ? "…" : "") + found.hay.slice(start, found.at),
      mid: found.hay.slice(found.at, found.at + found.length),
      after: found.hay.slice(found.at + found.length, end) + (end < found.hay.length ? "…" : "")
    };
  }

  function bindForm(form) {
    var wrap = form.closest(".topnav-search, .source-search-block") || form.parentElement;
    var input = form.querySelector('input[name="q"], input[type="search"]');
    var status = wrap.querySelector("[data-source-search-status]");
    var list = wrap.querySelector("[data-source-search-results]");
    var panel = wrap.querySelector("[data-source-search-panel]");
    if (!input || !status || !list) return;
    var root = form.getAttribute("data-root") || "";

    function resultHref(row, query) {
      return root + row.href + "?find=" + encodeURIComponent(query);
    }

    function setPanel(open) {
      if (!panel) return;
      if (open) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
    }

    function render(query) {
      list.replaceChildren();
      var parsed = parseQuery(query);
      if (parsed.q.length < 2) {
        status.textContent = parsed.q
          ? "Type at least two characters."
          : "Type a word or phrase to search S17 and G3.";
        setPanel(true);
        return [];
      }
      if (!window.SOURCE_INDEX) {
        status.textContent = "Search is still loading. Try again in a moment.";
        setPanel(true);
        return [];
      }
      var hits = [];
      window.SOURCE_INDEX.forEach(function (row, index) {
        var hit = matchSection(row.text, parsed);
        if (!hit) return;
        hit.row = row;
        hit.index = index;
        hits.push(hit);
      });
      hits.sort(function (a, b) {
        if (!a.via !== !b.via) return a.via ? 1 : -1;
        return a.index - b.index;
      });
      if (!hits.length) {
        status.textContent = "No section contains that " + (/\s/.test(parsed.q) ? "phrase." : "word.");
        setPanel(true);
        return hits;
      }
      status.textContent = hits.length + (hits.length === 1 ? " section." : " sections.");
      hits.forEach(function (hit) {
        var item = document.createElement("li");
        var link = document.createElement("a");
        link.className = "source-hit";
        link.href = resultHref(hit.row, hit.found.query);
        var title = document.createElement("strong");
        title.textContent = hit.row.doc + " §" + hit.row.number + " — " + hit.row.title;
        var text = document.createElement("span");
        var parts = snippet(hit.found);
        var mark = document.createElement("mark");
        mark.textContent = parts.mid;
        text.append(document.createTextNode(parts.before), mark, document.createTextNode(parts.after));
        link.append(title, text);
        if (hit.via) {
          var note = document.createElement("span");
          note.className = "via";
          note.textContent = "Matched “" + hit.found.query + "” for " + hit.via + ".";
          link.append(note);
        }
        item.append(link);
        list.append(item);
      });
      setPanel(true);
      return hits;
    }

    function runSearch(fromSubmit) {
      var hits = render(input.value);
      var parsed = parseQuery(input.value);
      if (!fromSubmit) return hits;
      if (parsed.q.length < 2 || !window.SOURCE_INDEX) {
        status.setAttribute("tabindex", "-1");
        try { status.focus({ preventScroll: true }); } catch (err) { status.focus(); }
        return hits;
      }
      if (hits.length === 1) {
        window.location.href = resultHref(hits[0].row, hits[0].found.query);
        return hits;
      }
      setPanel(true);
      if (hits.length > 1) {
        var first = list.querySelector("a");
        if (first) {
          try { first.focus({ preventScroll: false }); } catch (err) { first.focus(); }
        }
      } else {
        status.setAttribute("tabindex", "-1");
        try { status.focus({ preventScroll: true }); } catch (err) { status.focus(); }
      }
      return hits;
    }

    input.addEventListener("input", function () {
      if (!parseQuery(input.value).q) {
        list.replaceChildren();
        status.textContent = "";
        setPanel(false);
        return;
      }
      render(input.value);
    });
    input.addEventListener("focus", function () {
      if (parseQuery(input.value).q.length >= 2) render(input.value);
    });
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      runSearch(true);
    });

    if (panel) {
      document.addEventListener("pointerdown", function (event) {
        if (!wrap.contains(event.target)) setPanel(false);
      });
      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
          setPanel(false);
          input.focus();
        }
      });
    }

    form._sourceSearchRun = runSearch;
  }

  function start() {
    document.querySelectorAll("[data-source-search]").forEach(bindForm);
    var initial = (new URLSearchParams(location.search).get("q") || "").trim();
    if (!initial) return;
    var preferred =
      document.querySelector(".source-search-block [data-source-search]") ||
      document.querySelector("[data-source-search]");
    if (!preferred || !preferred._sourceSearchRun) return;
    var input = preferred.querySelector('input[name="q"], input[type="search"]');
    if (!input) return;
    input.value = initial;
    preferred._sourceSearchRun(true);
  }

  if (window.SOURCE_INDEX) {
    start();
    return;
  }

  var tries = 0;
  var timer = window.setInterval(function () {
    tries += 1;
    if (window.SOURCE_INDEX) {
      window.clearInterval(timer);
      start();
      return;
    }
    if (tries < 100) return;
    window.clearInterval(timer);
    document.querySelectorAll("[data-source-search]").forEach(bindForm);
    document.querySelectorAll("[data-source-search-status]").forEach(function (el) {
      if (!el.textContent) el.textContent = "Search index did not load. Open Source and try again.";
    });
  }, 50);
})();
