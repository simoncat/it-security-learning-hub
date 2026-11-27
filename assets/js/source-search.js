(function () {
  var MAX_QUERY = 200;

  function parseQuery(query) {
    var raw = String(query || "").trim().slice(0, MAX_QUERY);
    var quoted = /^["“”'].+["“”']$/.test(raw);
    var q = raw.replace(/^["“”']+|["“”']+$/g, "").replace(/\s+/g, " ").trim().slice(0, MAX_QUERY);
    return { q: q, quoted: quoted };
  }

  function safeResultHref(root, href, query) {
    var path = String(href || "");
    if (path !== "core4/index.html" &&
        !/^core4\/(?:s17|g3)\/(?:index|appendix-c|s\d{2})\.html$/.test(path)) {
      return "";
    }
    var candidate = String(root || "") + path + "?find=" + encodeURIComponent(String(query || "").slice(0, MAX_QUERY));
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(candidate) || candidate.indexOf("//") === 0) return "";
    try {
      var url = new URL(candidate, location.href);
      if (url.protocol !== "http:" && url.protocol !== "https:" && url.protocol !== "file:") return "";
      if (url.protocol === "file:") return candidate;
      if (url.origin !== location.origin) return "";
      return url.pathname + url.search + url.hash;
    } catch (err) {
      return "";
    }
  }

  function escapeReg(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function locateAllForms(hay, q) {
    if (!q || q.length < 2) return [];
    var out = [];
    if (/\s/.test(q)) {
      var lower = hay.toLowerCase();
      var needle = q.toLowerCase();
      var from = 0;
      while (from <= lower.length - needle.length) {
        var at = lower.indexOf(needle, from);
        if (at < 0) break;
        out.push({
          hay: hay,
          at: at,
          length: q.length,
          query: hay.slice(at, at + q.length)
        });
        from = at + Math.max(1, needle.length);
      }
      return out;
    }
    var re = new RegExp("(^|[^A-Za-z0-9/.])(" + escapeReg(q) + ")(?![A-Za-z0-9/.])", "gi");
    var match;
    while ((match = re.exec(hay)) !== null) {
      out.push({
        hay: hay,
        at: match.index + match[1].length,
        length: match[2].length,
        query: match[2]
      });
      if (!match[0].length) re.lastIndex += 1;
    }
    return out;
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

  function matchSectionAll(text, parsed) {
    var hay = text.replace(/\s+/g, " ").trim();
    var directs = locateAllForms(hay, parsed.q);
    if (directs.length) {
      return directs.map(function (found) {
        return { found: found, via: "" };
      });
    }
    if (parsed.quoted) return [];
    var group = groupFor(parsed.q);
    if (!group) return [];
    for (var i = 0; i < group.length; i++) {
      if (group[i].toLowerCase() === parsed.q.toLowerCase()) continue;
      var founds = locateAllForms(hay, group[i]);
      if (!founds.length) continue;
      return founds.map(function (found) {
        return { found: found, via: parsed.q };
      });
    }
    return [];
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

    function resultHref(row, query, occ) {
      var href = safeResultHref(root, row && row.href, query);
      if (!href || !occ || occ < 2) return href;
      return href + (href.indexOf("?") >= 0 ? "&" : "?") + "n=" + encodeURIComponent(String(occ));
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
      var sectionIds = {};
      window.SOURCE_INDEX.forEach(function (row, index) {
        var matches = matchSectionAll(row.text, parsed);
        matches.forEach(function (hit, matchIndex) {
          hit.row = row;
          hit.index = index;
          hit.occ = matchIndex + 1;
          hit.occTotal = matches.length;
          hits.push(hit);
        });
        if (matches.length) sectionIds[row.doc + ":" + row.id] = true;
      });
      hits.sort(function (a, b) {
        if (!a.via !== !b.via) return a.via ? 1 : -1;
        if (a.index !== b.index) return a.index - b.index;
        return a.occ - b.occ;
      });
      if (!hits.length) {
        status.textContent = "No section contains that " + (/\s/.test(parsed.q) ? "phrase." : "word.");
        setPanel(true);
        return hits;
      }
      var sectionCount = Object.keys(sectionIds).length;
      status.textContent =
        hits.length + (hits.length === 1 ? " match" : " matches") +
        " in " + sectionCount + (sectionCount === 1 ? " section." : " sections.");
      hits.forEach(function (hit) {
        var item = document.createElement("li");
        var link = document.createElement("a");
        link.className = "source-hit";
        var href = resultHref(hit.row, hit.found.query, hit.occ);
        if (!href) return;
        link.href = href;
        var title = document.createElement("strong");
        title.textContent = hit.row.doc + " §" + hit.row.number + " — " + hit.row.title;
        if (hit.occTotal > 1) title.textContent += " (match " + hit.occ + " of " + hit.occTotal + ")";
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
        item.className = "source-result";
        item.append(link);
        if (window.HubCart) {
          var record = {
            href: hit.row.href,
            find: hit.found.query,
            n: hit.occ > 1 ? String(hit.occ) : "",
            title: title.textContent,
            snippet: parts.before + parts.mid + parts.after,
            query: parsed.q,
            doc: hit.row.doc,
            number: String(hit.row.number || "")
          };
          var cartId = window.HubCart.key(record);
          if (cartId) {
            var save = document.createElement("button");
            save.type = "button";
            save.className = "btn btn-ghost source-save";
            save.setAttribute("data-cart-save", "");
            save.setAttribute("data-cart-id", cartId);
            save.setAttribute("data-cart-title", record.title);
            save.addEventListener("click", function () {
              if (window.HubCart.has(cartId)) window.HubCart.remove(cartId);
              else window.HubCart.add(record);
            });
            item.append(save);
          }
        }
        list.append(item);
      });
      document.dispatchEvent(new Event("hub-cart-change"));
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
        var only = resultHref(hits[0].row, hits[0].found.query, hits[0].occ);
        if (only) window.location.assign(only);
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

  function refreshCartButtons() {
    if (!window.HubCart) return;
    document.querySelectorAll("[data-cart-save]").forEach(function (button) {
      var id = button.getAttribute("data-cart-id") || "";
      var saved = window.HubCart.has(id);
      var title = button.getAttribute("data-cart-title") || "result";
      button.textContent = saved ? "Remove" : "Save";
      button.setAttribute("aria-pressed", saved ? "true" : "false");
      button.setAttribute("aria-label", (saved ? "Remove " : "Save ") + title + (saved ? " from the cart" : " to the cart"));
    });
  }

  document.addEventListener("hub-cart-change", refreshCartButtons);

  function isMacPlatform() {
    var platform = navigator.platform || "";
    var ua = navigator.userAgent || "";
    return /Mac|iPhone|iPad|iPod/.test(platform) || /Mac OS X/.test(ua);
  }

  function bindHeaderSearchShortcut() {
    var headerInput = document.querySelector("#header-source-query");
    if (!headerInput) return;
    var hint = document.querySelector("[data-search-shortcut-hint]");
    if (hint) hint.textContent = isMacPlatform() ? "⌘K" : "Ctrl+K";
    document.addEventListener("keydown", function (event) {
      var key = String(event.key || "").toLowerCase();
      if (key !== "k") return;
      if (!(event.metaKey || event.ctrlKey) || event.altKey || event.shiftKey) return;
      event.preventDefault();
      try {
        headerInput.focus({ preventScroll: false });
      } catch (err) {
        headerInput.focus();
      }
      if (typeof headerInput.select === "function") headerInput.select();
    });
  }

  function start() {
    document.querySelectorAll("[data-source-search]").forEach(bindForm);
    bindHeaderSearchShortcut();
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
    bindHeaderSearchShortcut();
    document.querySelectorAll("[data-source-search-status]").forEach(function (el) {
      if (!el.textContent) el.textContent = "Search index did not load. Open Source and try again.";
    });
  }, 50);
})();
