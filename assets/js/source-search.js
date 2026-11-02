(function () {
  var form = document.querySelector("[data-source-search]");
  if (!form || !window.SOURCE_INDEX) return;
  var input = form.querySelector("input");
  var status = document.getElementById("source-search-status");
  var list = document.getElementById("source-search-results");
  var root = form.getAttribute("data-root") || "";

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

  function resultHref(row, query) {
    return root + row.href + "?find=" + encodeURIComponent(query);
  }

  function render(query) {
    list.replaceChildren();
    var parsed = parseQuery(query);
    if (parsed.q.length < 2) {
      status.textContent = parsed.q ? "Type at least two characters." : "";
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
    return hits;
  }

  input.addEventListener("input", function () {
    render(input.value);
  });
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var hits = render(input.value);
    if (hits.length === 1) window.location.href = resultHref(hits[0].row, hits[0].found.query);
  });
})();
