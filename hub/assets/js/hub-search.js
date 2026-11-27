(function () {
  var MAX_QUERY = 120;
  var MAX_PER_CATEGORY = 6;
  var CATEGORY_ORDER = [
    "Decision aids",
    "Quizzes",
    "Q&A",
    "Source",
    "Glossary",
    "Cheat sheets",
    "Walkthroughs",
    "Paths",
    "Hub pages"
  ];

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function isMacPlatform() {
    var platform = navigator.platform || "";
    var ua = navigator.userAgent || "";
    return /Mac|iPhone|iPad|iPod/.test(platform) || /Mac OS X/.test(ua);
  }

  function parseQuery(value) {
    return String(value || "")
      .trim()
      .replace(/\s+/g, " ")
      .slice(0, MAX_QUERY);
  }

  function escapeReg(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function resolveHref(path) {
    var root = document.body.getAttribute("data-search-root") || "";
    var href = String(path || "");
    if (!href) return "";
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(href) || href.indexOf("//") === 0) return "";
    try {
      var url = new URL(root + href, location.href);
      if (url.protocol !== "http:" && url.protocol !== "https:" && url.protocol !== "file:") return "";
      if (url.protocol !== "file:" && url.origin !== location.origin) return "";
      return url.pathname + url.search + url.hash;
    } catch (err) {
      return "";
    }
  }

  function matchIndex(hay, needle) {
    if (!needle || needle.length < 2) return -1;
    return String(hay || "").toLowerCase().indexOf(needle.toLowerCase());
  }

  function highlightText(text, query) {
    var frag = document.createDocumentFragment();
    var raw = String(text || "");
    if (!query || query.length < 2) {
      frag.appendChild(document.createTextNode(raw));
      return frag;
    }
    var re = new RegExp(escapeReg(query), "ig");
    var last = 0;
    var match;
    while ((match = re.exec(raw))) {
      if (match.index > last) {
        frag.appendChild(document.createTextNode(raw.slice(last, match.index)));
      }
      var mark = document.createElement("mark");
      mark.textContent = match[0];
      frag.appendChild(mark);
      last = match.index + match[0].length;
      if (match[0].length === 0) re.lastIndex += 1;
    }
    if (last < raw.length) frag.appendChild(document.createTextNode(raw.slice(last)));
    return frag;
  }

  function snippetAround(text, query) {
    var hay = String(text || "");
    var at = matchIndex(hay, query);
    if (at < 0) {
      return hay.slice(0, 140) + (hay.length > 140 ? "…" : "");
    }
    var start = Math.max(0, at - 48);
    var end = Math.min(hay.length, at + query.length + 72);
    return (start ? "…" : "") + hay.slice(start, end) + (end < hay.length ? "…" : "");
  }

  function relatedForms(query) {
    var q = query.toLowerCase();
    var out = [];
    var groups = window.HUB_SEARCH_EQUIVALENTS || [];
    groups.forEach(function (group) {
      var hit = group.some(function (form) {
        return form.toLowerCase() === q || form.toLowerCase().indexOf(q) >= 0 || q.indexOf(form.toLowerCase()) >= 0;
      });
      if (!hit) return;
      group.forEach(function (form) {
        if (form.toLowerCase() === q) return;
        if (out.indexOf(form) < 0) out.push(form);
      });
    });
    return out.slice(0, 6);
  }

  function search(query) {
    var index = window.HUB_SEARCH_INDEX || [];
    var q = parseQuery(query);
    if (q.length < 2) return { total: 0, groups: {}, related: [] };
    var related = relatedForms(q);
    var needles = [q].concat(related);
    var scored = [];
    index.forEach(function (row, i) {
      var hay = (row.title || "") + "\n" + (row.meta || "") + "\n" + (row.text || "");
      var best = -1;
      var via = "";
      needles.forEach(function (needle, n) {
        var at = matchIndex(hay, needle);
        if (at < 0) return;
        var rank = at + (n ? 1000 : 0) + (matchIndex(row.title || "", needle) < 0 ? 200 : 0);
        if (best < 0 || rank < best) {
          best = rank;
          via = n ? needle : "";
        }
      });
      if (best < 0) return;
      scored.push({ row: row, rank: best, via: via, index: i });
    });
    scored.sort(function (a, b) {
      if (a.rank !== b.rank) return a.rank - b.rank;
      return a.index - b.index;
    });
    var groups = {};
    scored.forEach(function (hit) {
      var cat = hit.row.category || "Hub pages";
      if (!groups[cat]) groups[cat] = [];
      if (groups[cat].length >= MAX_PER_CATEGORY) return;
      groups[cat].push(hit);
    });
    return { total: scored.length, groups: groups, related: related };
  }

  function emptyState() {
    var wrap = document.createElement("div");
    var lead = document.createElement("h2");
    lead.id = "hub-search-title";
    lead.className = "hub-search-lead";
    lead.textContent = "Search decision aids, quizzes, Q&A, source sections, and glossary terms";
    var label = document.createElement("p");
    label.className = "hub-search-try-label";
    label.textContent = "Try searching for";
    var suggestions = document.createElement("div");
    suggestions.className = "hub-search-try";
    suggestions.setAttribute("data-hub-search-suggestions", "");
    wrap.append(lead, label, suggestions);
    return wrap;
  }

  function renderResults(query) {
    var body = $("[data-hub-search-body]");
    var clearBtn = $("[data-hub-search-clear]");
    var full = $("[data-hub-search-full]");
    if (!body) return;
    var q = parseQuery(query);
    if (clearBtn) clearBtn.hidden = !q;
    if (full) {
      var base = full.getAttribute("data-base-href") || full.getAttribute("href") || "";
      if (!full.getAttribute("data-base-href")) full.setAttribute("data-base-href", base.split("?")[0]);
      var href = full.getAttribute("data-base-href");
      full.href = q ? href + "?q=" + encodeURIComponent(q) : href;
    }
    body.replaceChildren();
    if (!q) {
      body.appendChild(emptyState());
      return;
    }
    if (q.length < 2) {
      var need = document.createElement("p");
      need.className = "hub-search-status";
      need.textContent = "Type at least two characters.";
      body.appendChild(need);
      return;
    }
    if (!window.HUB_SEARCH_INDEX) {
      var loading = document.createElement("p");
      loading.className = "hub-search-status";
      loading.textContent = "Search is still loading. Try again in a moment.";
      body.appendChild(loading);
      return;
    }
    var result = search(q);
    var status = document.createElement("p");
    status.className = "hub-search-status";
    if (!result.total) {
      status.textContent = "No pages match that wording.";
      body.appendChild(status);
      return;
    }
    var statusText = result.total + (result.total === 1 ? " result" : " results");
    if (result.related.length) {
      statusText += " · Also matching: " + result.related.join(", ");
    }
    status.textContent = statusText;
    body.appendChild(status);

    CATEGORY_ORDER.forEach(function (category) {
      var hits = result.groups[category];
      if (!hits || !hits.length) return;
      var section = document.createElement("section");
      section.className = "hub-search-group";
      var heading = document.createElement("h3");
      heading.textContent = category;
      section.appendChild(heading);
      var list = document.createElement("ul");
      list.className = "hub-search-list";
      hits.forEach(function (hit) {
        var row = hit.row;
        var href = resolveHref(row.href);
        if (!href) return;
        var item = document.createElement("li");
        var link = document.createElement("a");
        link.className = "hub-search-hit";
        link.href = href;
        link.setAttribute("data-hub-search-hit", "");
        var badge = document.createElement("span");
        badge.className = "hub-search-badge hub-search-badge-" + (row.badgeKind || "page");
        badge.textContent = row.badge || category;
        var meta = document.createElement("span");
        meta.className = "hub-search-meta";
        meta.textContent = row.meta || "";
        var title = document.createElement("strong");
        title.className = "hub-search-hit-title";
        title.appendChild(highlightText(row.title, q));
        var snip = document.createElement("span");
        snip.className = "hub-search-hit-snip";
        snip.appendChild(highlightText(snippetAround(row.text, hit.via || q), hit.via || q));
        var arrow = document.createElement("span");
        arrow.className = "hub-search-hit-arrow";
        arrow.setAttribute("aria-hidden", "true");
        arrow.textContent = "→";
        var top = document.createElement("div");
        top.className = "hub-search-hit-top";
        top.append(badge);
        if (row.meta) top.append(meta);
        link.append(top, title, snip, arrow);
        item.appendChild(link);
        list.appendChild(item);
      });
      section.appendChild(list);
      body.appendChild(section);
    });
    setActive(0);
  }

  function hits() {
    return $all("[data-hub-search-hit]");
  }

  function setActive(index) {
    var items = hits();
    if (!items.length) return;
    var next = Math.max(0, Math.min(index, items.length - 1));
    items.forEach(function (el, i) {
      el.classList.toggle("is-active", i === next);
      if (i === next) el.setAttribute("aria-selected", "true");
      else el.removeAttribute("aria-selected");
    });
    items[next].scrollIntoView({ block: "nearest" });
  }

  function activeIndex() {
    var items = hits();
    for (var i = 0; i < items.length; i += 1) {
      if (items[i].classList.contains("is-active")) return i;
    }
    return 0;
  }

  function openModal() {
    var modal = $("#hub-search-modal");
    var input = $("[data-hub-search-input]");
    if (!modal || !input) return;
    modal.hidden = false;
    document.documentElement.classList.add("hub-search-open");
    renderResults(input.value);
    window.setTimeout(function () {
      try {
        input.focus({ preventScroll: true });
      } catch (err) {
        input.focus();
      }
      if (typeof input.select === "function" && input.value) input.select();
    }, 0);
  }

  function closeModal() {
    var modal = $("#hub-search-modal");
    var openBtn = $("[data-hub-search-open]");
    if (!modal) return;
    modal.hidden = true;
    document.documentElement.classList.remove("hub-search-open");
    if (openBtn) {
      try {
        openBtn.focus({ preventScroll: true });
      } catch (err) {
        openBtn.focus();
      }
    }
  }

  function isOpen() {
    var modal = $("#hub-search-modal");
    return modal && !modal.hidden;
  }

  function start() {
    var openBtn = $("[data-hub-search-open]");
    var input = $("[data-hub-search-input]");
    var clearBtn = $("[data-hub-search-clear]");
    var hint = $("[data-search-shortcut-hint]");
    if (hint) hint.textContent = isMacPlatform() ? "⌘K" : "Ctrl+K";
    if (!openBtn || !input) return;

    openBtn.addEventListener("click", function () {
      openModal();
    });
    $all("[data-hub-search-close]").forEach(function (el) {
      el.addEventListener("click", closeModal);
    });
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        input.value = "";
        renderResults("");
        input.focus();
      });
    }
    input.addEventListener("input", function () {
      renderResults(input.value);
    });

    document.addEventListener("keydown", function (event) {
      var key = String(event.key || "");
      if ((event.metaKey || event.ctrlKey) && !event.altKey && !event.shiftKey && key.toLowerCase() === "k") {
        event.preventDefault();
        if (isOpen()) {
          input.focus();
          if (typeof input.select === "function") input.select();
        } else {
          openModal();
        }
        return;
      }
      if (!isOpen()) return;
      if (key === "Escape") {
        event.preventDefault();
        closeModal();
        return;
      }
      var items = hits();
      if (!items.length) return;
      if (key === "ArrowDown") {
        event.preventDefault();
        setActive(activeIndex() + 1);
      } else if (key === "ArrowUp") {
        event.preventDefault();
        setActive(activeIndex() - 1);
      } else if (key === "Enter" && document.activeElement === input) {
        var active = items[activeIndex()];
        if (active && active.href) {
          event.preventDefault();
          window.location.assign(active.href);
        }
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
