(function () {
  var CTX = "hksarg-hub:context";
  var TICK_PREFIX = "hksarg-hub:ticks:";
  var GAP_KEY = "hksarg-hub:gap-table";
  var MAX_FIND = 200;
  var MAX_FROM = 500;
  var MAX_LABEL = 90;

  function readJson(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw || raw.length > 200000) return fallback;
      var parsed = JSON.parse(raw);
      return parsed == null ? fallback : parsed;
    } catch (err) {
      return fallback;
    }
  }

  function allow(value, pattern) {
    var text = String(value || "");
    return pattern.test(text) ? text : "";
  }

  (function dropTrackParam() {
    var params = new URLSearchParams(location.search);
    if (!params.has("track")) return;
    params.delete("track");
    var query = params.toString();
    history.replaceState(null, "", location.pathname + (query ? "?" + query : "") + location.hash);
  })();

  function qs() {
    var params = new URLSearchParams(location.search);
    return {
      role: allow(params.get("role"), /^[1-5]$/),
      sdlc: allow(params.get("sdlc"), /^0[1-9]$/),
      need: allow(params.get("need"), /^[a-z][a-z0-9_-]{0,31}$/),
      tier: allow(params.get("tier"), /^[123]$/),
      mod: allow(params.get("mod"), /^(shall|should|may)$/)
    };
  }

  var filters = qs();
  var role = filters.role;

  var roleNames = {
    "1": "Elevated end user",
    "2": "System / LAN administrator",
    "3": "Application developer",
    "4": "IT security administrator / unit",
    "5": "Management support"
  };

  var sdlcNames = {
    "01": "Project initiation",
    "02": "Design",
    "03": "Procurement",
    "04": "Build/Implementation",
    "05": "Testing",
    "06": "Go-live",
    "07": "Operations",
    "08": "Change",
    "09": "Decommissioning"
  };

  function isSourceLink(href) {
    return !!href && href.indexOf("core4/") !== -1;
  }

  function safeInternalHref(href) {
    if (!href) return "";
    var value = String(href).trim();
    if (!value || value.length > MAX_FROM) return "";
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(value) || value.indexOf("//") === 0) return "";
    if (value.indexOf("\\") !== -1 || /%2e%2e/i.test(value)) return "";
    try {
      var url = new URL(value, location.href);
      if (url.protocol !== "http:" && url.protocol !== "https:" && url.protocol !== "file:") return "";
      if (url.username || url.password) return "";
      if (!/\.html$/i.test(url.pathname)) return "";
      if (url.protocol === "file:") {
        // file:// origins vary by browser; keep a same-folder relative target only.
        if (/^(?:\.\/|\.\.\/|[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.html(?:[?#].*)?$/.test(value) ||
            /^\/(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.html(?:[?#].*)?$/.test(value)) {
          return value;
        }
        return "";
      }
      if (url.origin !== location.origin) return "";
      return url.pathname + url.search + url.hash;
    } catch (err) {
      return "";
    }
  }

  function safeReturn(href) {
    return safeInternalHref(href);
  }

  function placeLabel(item) {
    var heading = document.querySelector("main h1");
    var page = heading ? heading.textContent.replace(/\s+/g, " ").trim() : "previous page";
    if (item) {
      var code = item.querySelector(".id-code");
      if (code && code.textContent.trim()) return (page + " · " + code.textContent.trim()).slice(0, 90);
    }
    if (location.hash) {
      var here = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (here) {
        var clause = here.querySelector("h2, h3");
        if (!clause && /^H[1-6]$/.test(here.tagName)) clause = here;
        if (clause && clause.textContent.trim()) return clause.textContent.replace(/\s+/g, " ").trim().slice(0, 90);
      }
    }
    return page.slice(0, 90);
  }

  document.querySelectorAll("a[href]").forEach(function (anchor) {
    var href = anchor.getAttribute("href");
    if (!isSourceLink(href)) return;
    var item = anchor.closest(".item");
    var retHash = item && item.id ? "#" + item.id : location.hash;
    var ret = location.pathname + location.search + retHash;
    if (!safeReturn(ret)) return;
    try {
      var url = new URL(href, location.href);
      url.searchParams.set("from", ret);
      url.searchParams.set("fromLabel", placeLabel(item));
      anchor.setAttribute("href", url.pathname + url.search + url.hash);
    } catch (err) {}
  });

  document.querySelectorAll("form.launcher").forEach(function (form) {
    if (!role) return;
    var roleInput = form.querySelector('input[name="role"][value="' + role + '"]');
    if (roleInput) roleInput.checked = true;
  });

  var banner = document.querySelector("[data-context-banner]");
  if (banner && (role || filters.sdlc || filters.need)) {
    var bits = [];
    if (role && roleNames[role]) bits.push(roleNames[role]);
    if (filters.sdlc) bits.push(sdlcNames[filters.sdlc] || "Stage " + filters.sdlc);
    if (filters.need) bits.push(filters.need);
    banner.textContent = "Filter in the link: " + bits.join(" · ") + ". Optional ticks on this page are stored only in this browser.";
  }

  document.querySelectorAll(".role-card").forEach(function (card) {
    if (role && card.getAttribute("data-role") === role) card.classList.add("is-selected");
  });

  var roleJump = document.getElementById("role-jump");
  if (roleJump && role) {
    var roleLabel = roleJump.querySelector("span");
    if (roleLabel && roleNames[role]) {
      roleLabel.textContent = roleNames[role] + ". S17, then G3, then App C.";
    }
  }

  var pageId = document.body.getAttribute("data-page-id") || "page";
  var tickKey = TICK_PREFIX + pageId;
  var ticks = readJson(tickKey, {});

  function countTicks() {
    var boxes = document.querySelectorAll("[data-tick]");
    var visible = 0;
    var done = 0;
    boxes.forEach(function (box) {
      var item = box.closest(".item");
      if (item && item.offsetParent === null) return;
      visible += 1;
      if (box.checked) done += 1;
    });
    var readout = document.querySelector("[data-progress-readout]");
    if (readout && boxes.length) {
      readout.textContent = done + " of " + boxes.length + " optional ticks on this page are marked in this browser.";
    }
    return { done: done, visible: visible };
  }

  function persistTicks() {
    try {
      localStorage.setItem(tickKey, JSON.stringify(ticks));
    } catch (err) {}
    countTicks();
  }

  document.querySelectorAll("[data-tick]").forEach(function (box) {
    var id = box.getAttribute("data-tick");
    box.checked = !!ticks[id];
    box.addEventListener("change", function () {
      if (box.checked) ticks[id] = true;
      else delete ticks[id];
      persistTicks();
    });
  });
  countTicks();

  var list = document.querySelector("[data-checklist]");
  document.querySelectorAll("[data-filter]").forEach(function (button) {
    button.addEventListener("click", function () {
      var mode = button.getAttribute("data-filter");
      document.querySelectorAll("[data-filter]").forEach(function (other) {
        other.setAttribute("aria-pressed", other === button ? "true" : "false");
      });
      if (!list) return;
      list.classList.remove("is-filtered-flag", "is-filtered-shall");
      if (mode === "flag") list.classList.add("is-filtered-flag");
      if (mode === "shall") list.classList.add("is-filtered-shall");
      countTicks();
    });
  });

  document.querySelectorAll("[data-action='print']").forEach(function (button) {
    button.addEventListener("click", function () { window.print(); });
  });

  document.querySelectorAll("[data-action='clear-ticks']").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!window.confirm("Clear optional ticks on this page in this browser?")) return;
      ticks = {};
      document.querySelectorAll("[data-tick]").forEach(function (box) { box.checked = false; });
      persistTicks();
    });
  });

  document.querySelectorAll("[data-action='expand']").forEach(function (button) {
    button.addEventListener("click", function () {
      var open = button.getAttribute("data-open") !== "false";
      document.querySelectorAll("main details.day").forEach(function (day) { day.open = open; });
    });
  });

  window.addEventListener("beforeprint", function () {
    document.querySelectorAll("details").forEach(function (details) {
      details.dataset.wasOpen = details.open ? "1" : "0";
      details.open = true;
    });
  });
  window.addEventListener("afterprint", function () {
    document.querySelectorAll("details").forEach(function (details) {
      if (details.dataset.wasOpen === "0") details.open = false;
    });
  });

  var gapBody = document.querySelector("#gap-table tbody");
  function gapRows() {
    if (!gapBody) return [];
    return Array.prototype.map.call(gapBody.querySelectorAll("tr"), function (row) {
      return Array.prototype.map.call(row.querySelectorAll("td"), function (cell) {
        return cell.textContent || "";
      });
    });
  }
  function writeGap(rows) {
    if (!gapBody) return;
    gapBody.innerHTML = "";
    rows.forEach(addGapRow);
  }
  function plainText(value) {
    return String(value == null ? "" : value).replace(/\s+/g, " ").trim().slice(0, 2000);
  }

  function bindGapCell(cell) {
    cell.contentEditable = "true";
    cell.addEventListener("input", function () {
      if (cell.querySelector("*")) cell.textContent = cell.textContent || "";
      saveGap();
    });
    cell.addEventListener("paste", function (event) {
      event.preventDefault();
      var text = "";
      try {
        text = (event.clipboardData || window.clipboardData).getData("text/plain") || "";
      } catch (err) {}
      text = plainText(text);
      if (document.queryCommandSupported && document.queryCommandSupported("insertText")) {
        document.execCommand("insertText", false, text);
      } else {
        cell.textContent = (cell.textContent || "") + text;
      }
      saveGap();
    });
  }

  function addGapRow(values) {
    var row = document.createElement("tr");
    for (var i = 0; i < 5; i += 1) {
      var cell = document.createElement("td");
      cell.textContent = values && values[i] ? plainText(values[i]) : "";
      bindGapCell(cell);
      row.appendChild(cell);
    }
    gapBody.appendChild(row);
  }
  function saveGap() {
    try { localStorage.setItem(GAP_KEY, JSON.stringify(gapRows())); } catch (err) {}
  }
  if (gapBody) {
    var existing = readJson(GAP_KEY, null);
    function bindExisting() {
      gapBody.querySelectorAll("td").forEach(bindGapCell);
    }
    if (Array.isArray(existing) && existing.length) {
      writeGap(existing.filter(Array.isArray).map(function (row) {
        return Array.isArray(row) ? row.slice(0, 5).map(plainText) : [];
      }).slice(0, 100));
    } else if (!gapBody.querySelector("tr")) {
      addGapRow(); addGapRow(); addGapRow(); addGapRow();
    } else {
      bindExisting();
    }
    var addBtn = document.querySelector("[data-action='add-gap']");
    if (addBtn) addBtn.addEventListener("click", function () { addGapRow(); saveGap(); });
    var clearGap = document.querySelector("[data-action='clear-gap']");
    if (clearGap) {
      clearGap.addEventListener("click", function () {
        if (!window.confirm("Clear the gap table stored in this browser?")) return;
        writeGap([[], [], [], []]);
        try { localStorage.removeItem(GAP_KEY); } catch (err) {}
      });
    }
    var csvBtn = document.querySelector("[data-action='csv-gap']");
    if (csvBtn) {
      csvBtn.addEventListener("click", function () {
        function cell(value) {
          var text = String(value || "").replace(/\r?\n/g, " ").trim();
          if (/[",]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
          return text;
        }
        var lines = [["Control", "Evidence", "Gap", "Owner", "Due"].join(",")];
        gapRows().forEach(function (row) {
          lines.push(row.map(cell).join(","));
        });
        var blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
        var link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "gap-table.csv";
        link.click();
        setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
      });
    }
  }

  var matrix = document.getElementById("appc-matrix");
  if (matrix) {
    var sectionFilter = document.getElementById("appc-section");
    function applyMatrix() {
      var mode = document.querySelector("[data-tier-filter][aria-pressed='true']");
      var tier = mode ? mode.getAttribute("data-tier-filter") : "all";
      var section = sectionFilter ? sectionFilter.value : "all";
      matrix.querySelectorAll("tbody tr").forEach(function (row) {
        var show = true;
        if (tier === "2" && row.getAttribute("data-tier2") !== "1") show = false;
        if (tier === "3" && row.getAttribute("data-tier3") !== "1") show = false;
        if (section !== "all" && row.getAttribute("data-section") !== section) show = false;
        row.classList.toggle("is-hidden", !show);
      });
    }
    document.querySelectorAll("[data-tier-filter]").forEach(function (button) {
      button.addEventListener("click", function () {
        document.querySelectorAll("[data-tier-filter]").forEach(function (other) {
          other.setAttribute("aria-pressed", other === button ? "true" : "false");
        });
        applyMatrix();
      });
    });
    if (sectionFilter) sectionFilter.addEventListener("change", applyMatrix);
  }

  var indexFilter = document.getElementById("page-filter");
  if (indexFilter) {
    indexFilter.addEventListener("input", function () {
      var query = indexFilter.value.trim().toLowerCase();
      document.querySelectorAll("[data-index-item]").forEach(function (item) {
        var hay = (item.textContent || "").toLowerCase();
        item.hidden = query && hay.indexOf(query) === -1;
      });
    });
  }

  if (window.matchMedia("(max-width: 900px)").matches) {
    var drawer = document.querySelector(".sidenav");
    if (drawer && drawer.tagName === "DETAILS") drawer.open = false;
  }

  var fromParams = new URLSearchParams(location.search);
  var fromHref = safeReturn(fromParams.get("from") || "");
  if (fromHref) {
    var fromLabel = (fromParams.get("fromLabel") || "where you were")
      .replace(/[\u0000-\u001f\u007f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, MAX_LABEL) || "where you were";
    var back = document.createElement("a");
    back.className = "return-float no-print";
    back.href = fromHref;
    back.setAttribute("aria-label", "Back to " + fromLabel);
    var kicker = document.createElement("span");
    kicker.className = "return-kicker";
    kicker.textContent = "Back";
    var label = document.createElement("span");
    label.className = "return-label";
    label.textContent = fromLabel;
    back.appendChild(kicker);
    back.appendChild(label);
    document.body.appendChild(back);
  }

  document.querySelectorAll("[data-aid-filter]").forEach(function (button) {
    button.addEventListener("click", function () {
      var mode = button.getAttribute("data-aid-filter");
      var root = document.querySelector("[data-aid-root]");
      document.querySelectorAll("[data-aid-filter]").forEach(function (other) {
        other.setAttribute("aria-pressed", other === button ? "true" : "false");
      });
      if (!root) return;
      root.classList.remove("is-aid-shall", "is-aid-flag");
      if (mode === "shall") root.classList.add("is-aid-shall");
      if (mode === "flag") root.classList.add("is-aid-flag");
    });
  });

  var launcherNode = document.getElementById("launcher-data");
  var launcherRoot = document.getElementById("launcher-results");
  if (launcherNode && launcherRoot) {
    var catalogue = [];
    try {
      var parsedCatalogue = JSON.parse(launcherNode.textContent);
      if (Array.isArray(parsedCatalogue)) catalogue = parsedCatalogue;
    } catch (err) {
      catalogue = [];
    }
    var cssHref = document.querySelector('link[rel="stylesheet"]').getAttribute("href") || "";
    var prefix = cssHref.replace(/assets\/css\/hub\.css.*$/, "");
    var form = document.getElementById("staff-launcher");
    if (form) {
      ["role", "sdlc", "need", "tier", "mod"].forEach(function (name) {
        var field = form.querySelector('[name="' + name + '"]');
        if (field && filters[name]) field.value = filters[name];
      });
    }
    function listed(values, selected) {
      if (!selected) return true;
      if (!values || !values.length) return false;
      return values.indexOf("all") !== -1 || values.indexOf(selected) !== -1;
    }
    var matched = catalogue.filter(function (row) {
      if (!listed(row.roles, filters.role)) return false;
      if (!listed(row.sdlc, filters.sdlc)) return false;
      if (!listed(row.needs, filters.need)) return false;
      if (!listed(row.tiers, filters.tier)) return false;
      if (filters.mod && row.mod && row.mod !== filters.mod) return false;
      return true;
    });
    var order = ["Decision aid", "SDLC pack", "Enquiry Q&A", "Source"];
    var seen = {};
    launcherRoot.innerHTML = "";
    var heading = document.createElement("h2");
    var active = ["role", "sdlc", "need", "tier", "mod"].some(function (name) { return filters[name]; });
    heading.textContent = active ? "Matches for this filter" : "Cross-section — narrow it with role, stage, or need";
    launcherRoot.appendChild(heading);
    order.forEach(function (kind) {
      var groupRows = [];
      matched.forEach(function (row) {
        if (row.kind !== kind) return;
        var key = kind + "|" + row.href;
        if (seen[key]) return;
        seen[key] = true;
        groupRows.push(row);
      });
      if (!active && kind === "Decision aid") groupRows = groupRows.slice(0, 8);
      if (!active && kind === "Enquiry Q&A") groupRows = groupRows.slice(0, 4);
      if (!active && kind === "Source") groupRows = groupRows.slice(0, 6);
      var block = document.createElement("section");
      block.className = "result-group";
      var title = document.createElement("h3");
      title.textContent = kind;
      block.appendChild(title);
      if (!groupRows.length) {
        var empty = document.createElement("p");
        empty.textContent = "No matches in this group.";
        block.appendChild(empty);
      } else {
        var list = document.createElement("ul");
        list.className = "result-list";
        groupRows.forEach(function (row) {
          var item = document.createElement("li");
          var kindLabel = document.createElement("span");
          kindLabel.className = "result-kind";
          kindLabel.textContent = row.mod ? row.mod : kind;
          var link = document.createElement("a");
          var target = safeInternalHref(prefix + String(row.href || ""));
          if (!target) return;
          link.href = target;
          link.textContent = String(row.title || "");
          item.appendChild(kindLabel);
          item.appendChild(link);
          if (row.detail) {
            item.appendChild(document.createTextNode(" — " + row.detail));
          }
          list.appendChild(item);
        });
        block.appendChild(list);
      }
      launcherRoot.appendChild(block);
    });
  }

  (function highlightFind() {
    var params = new URLSearchParams(location.search);
    var query = (params.get("find") || "").replace(/\s+/g, " ").trim().slice(0, MAX_FIND);
    if (query.length < 2) return;
    var focusOcc = parseInt(params.get("n") || "1", 10);
    if (!isFinite(focusOcc) || focusOcc < 1) focusOcc = 1;
    var root = document.querySelector(".policy-text");
    if (!root) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    var nodes = [];
    var raw = "";
    var current;
    while ((current = walker.nextNode())) {
      nodes.push({ node: current, start: raw.length });
      raw += current.nodeValue;
    }
    var norm = "";
    var map = [];
    var spaced = false;
    for (var i = 0; i < raw.length; i++) {
      if (/\s/.test(raw.charAt(i))) {
        if (!spaced && norm.length) {
          norm += " ";
          map.push(i);
          spaced = true;
        }
        continue;
      }
      spaced = false;
      norm += raw.charAt(i);
      map.push(i);
    }
    var needle = query.toLowerCase();
    var ranges = [];
    if (query.indexOf(" ") === -1) {
      var escaped = needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      var re = new RegExp("(^|[^A-Za-z0-9/.])(" + escaped + ")(?![A-Za-z0-9/.])", "gi");
      var match;
      while ((match = re.exec(norm)) !== null) {
        ranges.push({
          at: match.index + match[1].length,
          length: match[2].length
        });
        if (!match[0].length) re.lastIndex += 1;
      }
    } else {
      var from = 0;
      var lower = norm.toLowerCase();
      while (from <= lower.length - needle.length) {
        var at = lower.indexOf(needle, from);
        if (at < 0) break;
        ranges.push({ at: at, length: needle.length });
        from = at + Math.max(1, needle.length);
      }
    }
    if (!ranges.length) return;
    var marks = [];
    for (var r = ranges.length - 1; r >= 0; r -= 1) {
      var span = ranges[r];
      if (span.at + span.length - 1 >= map.length) continue;
      var rawStart = map[span.at];
      var rawEnd = map[span.at + span.length - 1] + 1;
      var created = [];
      nodes.forEach(function (item) {
        if (!item.node.parentNode) return;
        var nodeStart = item.start;
        var nodeEnd = nodeStart + item.node.nodeValue.length;
        if (nodeEnd <= rawStart || nodeStart >= rawEnd) return;
        var localStart = Math.max(0, rawStart - nodeStart);
        var localEnd = Math.min(item.node.nodeValue.length, rawEnd - nodeStart);
        if (localStart >= localEnd) return;
        try {
          var range = document.createRange();
          range.setStart(item.node, localStart);
          range.setEnd(item.node, localEnd);
          var mark = document.createElement("mark");
          mark.className = "find-hit";
          range.surroundContents(mark);
          created.push(mark);
        } catch (err) {}
      });
      if (created.length) marks.unshift(created[0]);
    }
    if (!marks.length) return;
    var focus = marks[Math.min(focusOcc, marks.length) - 1] || marks[0];
    focus.id = "find-hit";
    window.setTimeout(function () { focus.scrollIntoView({ block: "center" }); }, 0);
  })();

  if (location.hash) {
    var landed = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (landed) {
      landed.classList.add("is-return-target");
      if (!landed.hasAttribute("tabindex")) landed.setAttribute("tabindex", "-1");
      window.setTimeout(function () {
        try { landed.focus({ preventScroll: true }); } catch (err) { landed.focus(); }
      }, 0);
      window.setTimeout(function () { landed.classList.remove("is-return-target"); }, 2600);
    }
  }

  (function progressTransfer() {
    var FORMAT = "hksarg-hub-progress";
    var VERSION = 1;
    var MAX_PAYLOAD = 500000;
    var importInput = document.querySelector("[data-progress-import]");

    function isProgressKey(key) {
      return key === GAP_KEY || (key && key.indexOf(TICK_PREFIX) === 0);
    }

    function collectProgress() {
      var items = {};
      for (var i = 0; i < localStorage.length; i += 1) {
        var key = localStorage.key(i);
        if (!isProgressKey(key)) continue;
        var raw = localStorage.getItem(key);
        if (raw == null) continue;
        if (raw.length > 200000) continue;
        try {
          items[key] = JSON.parse(raw);
        } catch (err) {
          items[key] = raw;
        }
      }
      return items;
    }

    function stampName() {
      var now = new Date();
      var y = now.getFullYear();
      var m = String(now.getMonth() + 1).padStart(2, "0");
      var d = String(now.getDate()).padStart(2, "0");
      return "hub-progress-" + y + m + d + ".json";
    }

    function exportProgress() {
      var payload = {
        format: FORMAT,
        version: VERSION,
        exportedAt: new Date().toISOString(),
        items: collectProgress()
      };
      var text = JSON.stringify(payload, null, 2);
      if (text.length > MAX_PAYLOAD) {
        window.alert("Progress is too large to export from this browser.");
        return;
      }
      var blob = new Blob([text], { type: "application/json;charset=utf-8" });
      var link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = stampName();
      link.click();
      window.setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
    }

    function clearProgressKeys() {
      var doomed = [];
      for (var i = 0; i < localStorage.length; i += 1) {
        var key = localStorage.key(i);
        if (isProgressKey(key)) doomed.push(key);
      }
      doomed.forEach(function (key) {
        try { localStorage.removeItem(key); } catch (err) {}
      });
    }

    function normalizeItemValue(value) {
      if (typeof value === "string") {
        if (value.length > 200000) return null;
        JSON.parse(value);
        return value;
      }
      var text = JSON.stringify(value);
      if (!text || text.length > 200000) return null;
      return text;
    }

    function applyImport(payload) {
      if (!payload || typeof payload !== "object") throw new Error("bad payload");
      if (payload.format !== FORMAT || payload.version !== VERSION) throw new Error("bad format");
      if (!payload.items || typeof payload.items !== "object" || Array.isArray(payload.items)) {
        throw new Error("bad items");
      }
      var keys = Object.keys(payload.items);
      if (keys.length > 500) throw new Error("too many keys");
      var prepared = {};
      var total = 0;
      keys.forEach(function (key) {
        if (!isProgressKey(key)) throw new Error("bad key");
        if (key.indexOf(TICK_PREFIX) === 0 && key.length > 120) throw new Error("bad key");
        var stored = normalizeItemValue(payload.items[key]);
        if (stored == null) throw new Error("bad value");
        prepared[key] = stored;
        total += key.length + stored.length;
      });
      if (total > MAX_PAYLOAD) throw new Error("too large");
      clearProgressKeys();
      Object.keys(prepared).forEach(function (key) {
        localStorage.setItem(key, prepared[key]);
      });
    }

    document.querySelectorAll("[data-action='export-progress']").forEach(function (button) {
      button.addEventListener("click", function () {
        try {
          exportProgress();
        } catch (err) {
          window.alert("Could not export progress from this browser.");
        }
      });
    });

    document.querySelectorAll("[data-action='import-progress']").forEach(function (button) {
      button.addEventListener("click", function () {
        if (!importInput) return;
        var ok = window.confirm(
          "Importing will clear and replace the optional progress stored in this browser. Continue?"
        );
        if (!ok) return;
        importInput.value = "";
        importInput.click();
      });
    });

    if (importInput) {
      importInput.addEventListener("change", function () {
        var file = importInput.files && importInput.files[0];
        if (!file) return;
        if (file.size > MAX_PAYLOAD) {
          window.alert("That file is too large to import.");
          importInput.value = "";
          return;
        }
        var reader = new FileReader();
        reader.onload = function () {
          try {
            var payload = JSON.parse(String(reader.result || ""));
            applyImport(payload);
            location.reload();
          } catch (err) {
            window.alert("Could not import that file. Progress in this browser was not changed.");
          } finally {
            importInput.value = "";
          }
        };
        reader.onerror = function () {
          window.alert("Could not read that file. Progress in this browser was not changed.");
          importInput.value = "";
        };
        reader.readAsText(file);
      });
    }
  })();
})();
