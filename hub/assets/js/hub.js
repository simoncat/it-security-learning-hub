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


(function () {
  var KEY = "hksarg-hub:saved-cart";
  var MAX_ITEMS = 80;
  var HREF_OK = /^core4\/(?:s17|g3)\/(?:index|appendix-c|s\d{2})\.html$/;
  var items = [];

  function cleanText(value, max) {
    return String(value == null ? "" : value)
      .replace(/[\u0000-\u001f\u007f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, max);
  }

  function cleanItem(raw) {
    if (!raw || typeof raw !== "object") return null;
    var href = String(raw.href || "");
    if (!HREF_OK.test(href)) return null;
    var find = cleanText(raw.find, 200);
    var query = cleanText(raw.query, 200);
    var title = cleanText(raw.title, 180);
    var snippet = cleanText(raw.snippet, 700);
    var clauseText = cleanText(raw.clauseText, 1500);
    var clause = cleanText(raw.clause, 24);
    if (clause && !/^[0-9A-Za-z().]+$/.test(clause)) clause = "";
    var anchor = String(raw.anchor || "");
    if (!/^[A-Za-z0-9_-]{1,64}$/.test(anchor)) anchor = "";
    var docRaw = cleanText(raw.doc, 8).toUpperCase();
    var doc = docRaw === "G3" ? "G3" : (docRaw === "S17" ? "S17" : "");
    if (!doc || !title) return null;
    var number = cleanText(raw.number, 8);
    if (number && !/^\d{1,2}$/.test(number)) number = "";
    var n = String(raw.n || "");
    if (n && !/^\d{1,3}$/.test(n)) n = "";
    return {
      id: [
        href,
        find.toLowerCase(),
        n,
        clause.toLowerCase(),
        anchor,
        String(snippet.length)
      ].join("\u001f"),
      href: href,
      find: find,
      n: n,
      title: title,
      snippet: snippet,
      query: query,
      clause: clause,
      clauseText: clauseText,
      anchor: anchor,
      doc: doc,
      number: number
    };
  }

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw || raw.length > 500000) return [];
      var parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      var out = [];
      var seen = {};
      parsed.slice(0, MAX_ITEMS).forEach(function (row) {
        var item = cleanItem(row);
        if (!item || seen[item.id]) return;
        seen[item.id] = true;
        out.push(item);
      });
      return out;
    } catch (err) {
      return [];
    }
  }

  function persist() {
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
    } catch (err) {}
  }

  function hubRoot() {
    var script = document.querySelector("script[src*='assets/js/hub.js']");
    if (!script) return "";
    var src = script.getAttribute("src") || "";
    var at = src.indexOf("assets/js/hub.js");
    return at >= 0 ? src.slice(0, at) : "";
  }

  function itemUrl(item) {
    var url = hubRoot() + item.href;
    var params = [];
    if (item.find) params.push("find=" + encodeURIComponent(item.find));
    if (item.n) params.push("n=" + encodeURIComponent(item.n));
    if (params.length) url += "?" + params.join("&");
    if (item.anchor) url += "#" + item.anchor;
    return url;
  }

  function absoluteUrl(item) {
    try {
      return new URL(itemUrl(item), location.href).href;
    } catch (err) {
      return itemUrl(item);
    }
  }

  items = load();

  var root = document.createElement("div");
  root.className = "saved-cart no-print";
  root.innerHTML =
    '<section class="saved-cart-panel" id="saved-cart-panel" hidden aria-labelledby="saved-cart-title">' +
      '<div class="saved-cart-print-head">' +
        '<h1>Saved clauses</h1>' +
        '<p>HKSARG IT Security Learning Hub. Learning aid only. Authoritative text remains S17, G3, Security Regulations, and B/D local policies.</p>' +
      '</div>' +
      '<div class="saved-cart-head">' +
        '<h2 id="saved-cart-title">Saved clauses</h2>' +
        '<button type="button" class="btn btn-ghost" data-cart-close>Close</button>' +
      '</div>' +
      '<p class="fine">Saved passages stay in this browser. On a source page, highlight a word or sentence and choose Add to cart. Drag a handle, or use Up and Down, to reorder.</p>' +
      '<p class="visually-hidden" data-cart-status aria-live="polite"></p>' +
      '<p class="saved-cart-empty" data-cart-empty>Nothing saved yet. Save a search result, or highlight source text and right-click.</p>' +
      '<ol class="saved-cart-list" data-cart-list></ol>' +
      '<div class="saved-cart-actions">' +
        '<button type="button" class="btn btn-primary" data-cart-pdf>Print PDF</button>' +
        '<button type="button" class="btn btn-ghost" data-cart-csv>Download CSV</button>' +
        '<button type="button" class="btn btn-ghost" data-cart-import>Import CSV</button>' +
      '</div>' +
      '<input type="file" accept=".csv,text/csv" data-cart-import-file hidden>' +
      '<p class="fine saved-cart-export-note">Print opens the browser dialog. Choose Save as PDF there. Import CSV reads a file this cart exported.</p>' +
    '</section>' +
    '<button type="button" class="saved-cart-toggle" aria-expanded="false" aria-controls="saved-cart-panel">' +
      '<span>Cart</span><span class="saved-cart-count" data-cart-count>0</span>' +
    '</button>';
  document.body.appendChild(root);

  var selectMenu = document.createElement("div");
  selectMenu.className = "cart-select-menu no-print";
  selectMenu.hidden = true;
  selectMenu.setAttribute("role", "menu");
  selectMenu.innerHTML =
    '<button type="button" class="btn btn-primary" role="menuitem" data-cart-add-selection>Add highlight to cart</button>' +
    '<p class="fine" data-cart-selection-note></p>';
  document.body.appendChild(selectMenu);

  var panel = root.querySelector(".saved-cart-panel");
  var toggle = root.querySelector(".saved-cart-toggle");
  var list = root.querySelector("[data-cart-list]");
  var empty = root.querySelector("[data-cart-empty]");
  var count = root.querySelector("[data-cart-count]");
  var status = root.querySelector("[data-cart-status]");
  var closeBtn = root.querySelector("[data-cart-close]");
  var pdfBtn = root.querySelector("[data-cart-pdf]");
  var csvBtn = root.querySelector("[data-cart-csv]");
  var importBtn = root.querySelector("[data-cart-import]");
  var importInput = root.querySelector("[data-cart-import-file]");
  var selectAdd = selectMenu.querySelector("[data-cart-add-selection]");
  var selectNote = selectMenu.querySelector("[data-cart-selection-note]");
  var dragFrom = -1;
  var pendingSelection = null;
  var suspendMenuDismiss = false;

  function indexOf(id) {
    for (var i = 0; i < items.length; i += 1) {
      if (items[i].id === id) return i;
    }
    return -1;
  }

  function announce(text) {
    status.textContent = "";
    window.setTimeout(function () { status.textContent = text; }, 30);
  }

  function changed() {
    document.dispatchEvent(new Event("hub-cart-change"));
  }

  function syncChrome() {
    count.textContent = String(items.length);
    var noun = items.length === 1 ? "item" : "items";
    var action = panel.hidden ? "Show" : "Hide";
    toggle.setAttribute("aria-expanded", panel.hidden ? "false" : "true");
    toggle.setAttribute("aria-label", action + " saved clauses cart, " + items.length + " " + noun);
    pdfBtn.disabled = items.length === 0;
    csvBtn.disabled = items.length === 0;
    empty.hidden = items.length !== 0;
  }

  function focusRow(index) {
    var row = list.querySelector('[data-cart-index="' + index + '"]');
    if (!row) return;
    var target = row.querySelector(".saved-cart-up:not(:disabled)") ||
      row.querySelector(".saved-cart-down:not(:disabled)") ||
      row.querySelector(".saved-cart-remove");
    if (target) target.focus();
  }

  function move(from, to) {
    if (from < 0 || to < 0 || from >= items.length || to >= items.length || from === to) return;
    var next = items.slice();
    var row = next.splice(from, 1)[0];
    next.splice(to, 0, row);
    items = next;
    persist();
    render();
    changed();
    announce("Moved “" + row.title + "” to position " + (to + 1) + " of " + items.length + ".");
    focusRow(to);
  }

  function highlightText(parent, text, needles) {
    var source = String(text || "");
    var ranges = [];
    needles.forEach(function (needle) {
      var key = String(needle || "").trim();
      if (key.length < 2) return;
      var lower = source.toLowerCase();
      var look = key.toLowerCase();
      var from = 0;
      while (from <= lower.length - look.length) {
        var at = lower.indexOf(look, from);
        if (at < 0) break;
        ranges.push([at, at + key.length]);
        from = at + look.length;
      }
    });
    ranges.sort(function (a, b) { return a[0] - b[0] || b[1] - a[1]; });
    var merged = [];
    ranges.forEach(function (range) {
      var last = merged[merged.length - 1];
      if (!last || range[0] > last[1]) merged.push([range[0], range[1]]);
      else if (range[1] > last[1]) last[1] = range[1];
    });
    var cursor = 0;
    merged.forEach(function (range) {
      if (range[0] > cursor) parent.appendChild(document.createTextNode(source.slice(cursor, range[0])));
      var mark = document.createElement("mark");
      mark.className = "find-hit";
      mark.textContent = source.slice(range[0], range[1]);
      parent.appendChild(mark);
      cursor = range[1];
    });
    if (cursor < source.length) parent.appendChild(document.createTextNode(source.slice(cursor)));
  }

  function render() {
    list.replaceChildren();
    items.forEach(function (item, index) {
      var li = document.createElement("li");
      li.className = "saved-cart-item";
      li.setAttribute("data-cart-index", String(index));

      var handle = document.createElement("button");
      handle.type = "button";
      handle.className = "saved-cart-handle";
      handle.draggable = true;
      handle.setAttribute("aria-label", "Drag to reorder “" + item.title + "”");
      handle.textContent = "↕";

      var body = document.createElement("div");
      body.className = "saved-cart-body";
      var kicker = document.createElement("p");
      kicker.className = "saved-cart-kicker";
      kicker.textContent = String(index + 1) + ". " + item.doc +
        (item.number ? " §" + item.number : "") +
        (item.clause ? " · " + item.clause : "");
      var link = document.createElement("a");
      link.href = itemUrl(item);
      highlightText(link, item.title, [item.find, item.query]);
      body.appendChild(kicker);
      body.appendChild(link);
      var samePassage = item.clauseText &&
        item.clauseText.toLowerCase() === String(item.snippet || "").toLowerCase();
      if (item.snippet && !samePassage) {
        var snippet = document.createElement("p");
        snippet.className = item.clauseText ? "saved-cart-snippet is-quote" : "saved-cart-snippet";
        highlightText(snippet, item.snippet, [item.find, item.query]);
        body.appendChild(snippet);
      }
      if (item.clauseText) {
        var clause = document.createElement("p");
        clause.className = "saved-cart-clause";
        var label = document.createElement("span");
        label.className = "saved-cart-clause-label";
        label.textContent = "Clause" + (item.clause ? " " + item.clause : "") + ": ";
        clause.appendChild(label);
        highlightText(clause, item.clauseText, [item.find, item.query]);
        body.appendChild(clause);
      }

      var actions = document.createElement("div");
      actions.className = "saved-cart-item-actions";
      var up = document.createElement("button");
      up.type = "button";
      up.className = "btn btn-ghost saved-cart-up";
      up.textContent = "Up";
      up.disabled = index === 0;
      up.setAttribute("aria-label", "Move “" + item.title + "” up");
      var down = document.createElement("button");
      down.type = "button";
      down.className = "btn btn-ghost saved-cart-down";
      down.textContent = "Down";
      down.disabled = index === items.length - 1;
      down.setAttribute("aria-label", "Move “" + item.title + "” down");
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "btn btn-ghost saved-cart-remove";
      remove.textContent = "Remove";
      remove.setAttribute("aria-label", "Remove “" + item.title + "”");
      actions.append(up, down, remove);

      up.addEventListener("click", function () { move(index, index - 1); });
      down.addEventListener("click", function () { move(index, index + 1); });
      remove.addEventListener("click", function () {
        var title = item.title;
        items = items.filter(function (row) { return row.id !== item.id; });
        persist();
        render();
        changed();
        announce("Removed “" + title + "”.");
        if (!items.length) closeBtn.focus();
        else focusRow(Math.min(index, items.length - 1));
      });

      handle.addEventListener("dragstart", function (event) {
        dragFrom = index;
        if (event.dataTransfer) {
          event.dataTransfer.effectAllowed = "move";
          try { event.dataTransfer.setData("text/plain", String(index)); } catch (err) {}
        }
        li.classList.add("is-dragging");
      });
      handle.addEventListener("dragend", function () {
        li.classList.remove("is-dragging");
        dragFrom = -1;
      });
      li.addEventListener("dragover", function (event) {
        if (dragFrom < 0) return;
        event.preventDefault();
        if (event.dataTransfer) event.dataTransfer.dropEffect = "move";
      });
      li.addEventListener("drop", function (event) {
        event.preventDefault();
        var from = dragFrom;
        dragFrom = -1;
        move(from, index);
      });

      li.append(handle, body, actions);
      list.appendChild(li);
    });
    syncChrome();
  }

  function openPanel() {
    panel.hidden = false;
    syncChrome();
    closeBtn.focus();
  }

  function closePanel() {
    if (panel.hidden) return;
    panel.hidden = true;
    syncChrome();
    toggle.focus();
  }

  function add(raw) {
    var item = cleanItem(raw);
    if (!item) return false;
    if (indexOf(item.id) >= 0) {
      announce("“" + item.title + "” is already in the cart.");
      return false;
    }
    if (items.length >= MAX_ITEMS) {
      window.alert("The cart holds " + MAX_ITEMS + " results. Remove one before saving another.");
      return false;
    }
    items.push(item);
    persist();
    render();
    changed();
    announce("Saved “" + item.title + "”.");
    return true;
  }

  function remove(id) {
    var at = indexOf(id);
    if (at < 0) return false;
    var title = items[at].title;
    items.splice(at, 1);
    persist();
    render();
    changed();
    announce("Removed “" + title + "”.");
    return true;
  }

  function csvCell(value) {
    var text = String(value == null ? "" : value);
    if (/^[=+\-@\t\r]/.test(text)) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
  }

  function downloadCsv() {
    if (!items.length) return;
    var header = ["Order", "Document", "Section", "Clause", "Title", "Highlight", "Snippet", "Clause text", "Search", "Link"];
    var lines = [header.map(csvCell).join(",")];
    items.forEach(function (item, index) {
      lines.push([
        String(index + 1),
        item.doc,
        item.number ? "§" + item.number : "",
        item.clause || "",
        item.title,
        item.find,
        item.snippet,
        item.clauseText || "",
        item.query,
        absoluteUrl(item)
      ].map(csvCell).join(","));
    });
    var now = new Date();
    var stamp = now.getFullYear() +
      String(now.getMonth() + 1).padStart(2, "0") +
      String(now.getDate()).padStart(2, "0");
    var blob = new Blob(["\uFEFF" + lines.join("\r\n")], { type: "text/csv;charset=utf-8" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "hub-saved-clauses-" + stamp + ".csv";
    link.click();
    window.setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
  }

  function printPdf() {
    if (!items.length) return;
    var wasHidden = panel.hidden;
    panel.hidden = false;
    document.body.classList.add("is-cart-print");
    function cleanup() {
      document.body.classList.remove("is-cart-print");
      panel.hidden = wasHidden;
      syncChrome();
      window.removeEventListener("afterprint", cleanup);
    }
    window.addEventListener("afterprint", cleanup);
    window.print();
  }

  function parseCsv(text) {
    var source = String(text || "").replace(/^\uFEFF/, "");
    var rows = [];
    var row = [];
    var cell = "";
    var quoted = false;
    for (var i = 0; i < source.length; i += 1) {
      var ch = source.charAt(i);
      if (quoted) {
        if (ch === '"') {
          if (source.charAt(i + 1) === '"') {
            cell += '"';
            i += 1;
          } else {
            quoted = false;
          }
        } else {
          cell += ch;
        }
      } else if (ch === '"') {
        quoted = true;
      } else if (ch === ",") {
        row.push(cell);
        cell = "";
      } else if (ch === "\n") {
        row.push(cell);
        rows.push(row);
        row = [];
        cell = "";
      } else if (ch !== "\r") {
        cell += ch;
      }
    }
    if (cell.length || row.length) {
      row.push(cell);
      rows.push(row);
    }
    return rows.filter(function (entry) {
      return entry.some(function (value) { return String(value || "").trim() !== ""; });
    });
  }

  function csvValue(map, row, names) {
    for (var i = 0; i < names.length; i += 1) {
      var at = map[names[i]];
      if (at == null || at >= row.length) continue;
      return row[at];
    }
    return "";
  }

  function unguardCsv(value) {
    var text = String(value == null ? "" : value).trim();
    if (text.charAt(0) === "'" && /^[=+\-@]/.test(text.charAt(1))) return text.slice(1);
    return text;
  }

  function sectionNumber(value) {
    var match = String(value || "").match(/(\d{1,2})/);
    return match ? String(parseInt(match[1], 10)) : "";
  }

  function fromCsvLink(link) {
    var text = unguardCsv(link);
    if (!text) return null;
    try {
      var url = new URL(text, location.href);
      var path = decodeURIComponent(url.pathname).replace(/\\/g, "/");
      var match = path.match(/(core4\/(?:s17|g3)\/(?:index|appendix-c|s(\d{2}))\.html)$/i);
      if (!match) return null;
      var hash = (url.hash || "").replace(/^#/, "");
      try { hash = decodeURIComponent(hash); } catch (err) {}
      return {
        href: match[1].toLowerCase(),
        find: url.searchParams.get("find") || "",
        n: url.searchParams.get("n") || "",
        anchor: hash,
        number: match[2] ? String(parseInt(match[2], 10)) : "",
        doc: /\/g3\//i.test(match[1]) ? "G3" : "S17"
      };
    } catch (err) {
      return null;
    }
  }

  function importCsvText(text) {
    var rows = parseCsv(text);
    if (rows.length < 2) return { added: 0, duplicate: 0, skipped: 0, empty: true };
    var map = {};
    rows[0].forEach(function (header, index) {
      map[String(header || "").trim().toLowerCase()] = index;
    });
    var known = ["document", "doc", "title", "link", "snippet", "highlight", "section", "clause", "clause text", "search"];
    var recognized = known.some(function (name) { return map[name] != null; });
    if (!recognized) throw new Error("header");
    var added = 0;
    var duplicate = 0;
    var skipped = 0;
    rows.slice(1).forEach(function (row) {
      var linked = fromCsvLink(csvValue(map, row, ["link"]));
      var highlight = unguardCsv(csvValue(map, row, ["highlight"]));
      var search = unguardCsv(csvValue(map, row, ["search"]));
      var snippet = unguardCsv(csvValue(map, row, ["snippet"]));
      var clause = unguardCsv(csvValue(map, row, ["clause"]));
      var clauseText = unguardCsv(csvValue(map, row, ["clause text", "clausetext"]));
      var title = unguardCsv(csvValue(map, row, ["title"]));
      var doc = unguardCsv(csvValue(map, row, ["document", "doc"]));
      var number = sectionNumber(csvValue(map, row, ["section"]));
      if (linked) {
        doc = linked.doc;
        number = linked.number || number;
      }
      if (!title) {
        title = [doc, number ? "§" + number : "", clause].filter(Boolean).join(" ");
      }
      var item = cleanItem({
        href: linked ? linked.href : "",
        find: highlight || (linked && linked.find) || search,
        n: linked ? linked.n : "",
        anchor: linked ? linked.anchor : "",
        title: title,
        snippet: snippet || highlight || clauseText,
        query: search,
        clause: clause,
        clauseText: clauseText,
        doc: doc,
        number: number
      });
      if (!item) {
        skipped += 1;
        return;
      }
      if (indexOf(item.id) >= 0) {
        duplicate += 1;
        return;
      }
      if (items.length >= MAX_ITEMS) {
        skipped += 1;
        return;
      }
      items.push(item);
      added += 1;
    });
    if (added) {
      persist();
      render();
      changed();
    }
    return { added: added, duplicate: duplicate, skipped: skipped, empty: false };
  }

  function reportImport(result) {
    if (result.empty) {
      window.alert("That CSV has no clauses to import. The cart was not changed.");
      return;
    }
    var parts = [];
    if (result.added) {
      parts.push("Imported " + result.added + (result.added === 1 ? " clause." : " clauses."));
    }
    if (result.duplicate) {
      parts.push(result.duplicate + (result.duplicate === 1 ? " was" : " were") + " already in the cart.");
    }
    if (result.skipped) {
      parts.push(result.skipped + (result.skipped === 1 ? " row was" : " rows were") + " skipped.");
    }
    if (!parts.length) parts.push("Nothing in that CSV could be added. The cart was not changed.");
    if (result.added) openPanel();
    window.alert(parts.join(" "));
  }

  function plainText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function elementOf(node) {
    if (!node) return null;
    return node.nodeType === 1 ? node : node.parentElement;
  }

  function directChild(el, className) {
    if (!el || !el.children) return null;
    for (var i = 0; i < el.children.length; i += 1) {
      if (el.children[i].classList.contains(className)) return el.children[i];
    }
    return null;
  }

  function clauseNoOf(el) {
    if (!el) return "";
    var no = directChild(el, "clause-no");
    if (no) {
      var text = plainText(no.textContent).replace(/\.$/, "");
      if (!text || text === "•" || text === "-" || text === "–") return "";
      return /^[0-9A-Za-z().]+$/.test(text) ? text : "";
    }
    if (el.classList.contains("policy-h")) {
      var match = plainText(el.textContent).match(/^(\d+(?:\.\d+)*)\b/);
      return match ? match[1] : "";
    }
    return "";
  }

  function clauseTextOf(el) {
    if (!el) return "";
    var body = directChild(el, "clause-body");
    return plainText((body || el).textContent);
  }

  function previousPassage(el) {
    var prev = el ? el.previousElementSibling : null;
    while (prev) {
      if (prev.classList.contains("policy-clause") || prev.classList.contains("policy-h")) return prev;
      prev = prev.previousElementSibling;
    }
    return null;
  }

  function anchorOf(el, policy) {
    var cur = el;
    while (cur && cur !== policy) {
      if (cur.id && /^[A-Za-z0-9_-]{1,64}$/.test(cur.id)) return cur.id;
      cur = cur.previousElementSibling;
    }
    return "";
  }

  function pageIdentity() {
    var path = "";
    try { path = decodeURIComponent(location.pathname); } catch (err) { path = location.pathname; }
    path = String(path || "").replace(/\\/g, "/");
    var match = path.match(/(core4\/(s17|g3)\/(?:index|appendix-c|s(\d{2}))\.html)$/i);
    if (!match) return null;
    return {
      href: match[1].toLowerCase(),
      doc: match[2].toLowerCase() === "g3" ? "G3" : "S17",
      number: match[3] ? String(parseInt(match[3], 10)) : ""
    };
  }

  function passageFor(block, policy) {
    var own = clauseNoOf(block);
    var number = own;
    var previous = previousPassage(block);
    var guard = 0;
    while (!number && previous && guard < 12) {
      number = clauseNoOf(previous);
      if (number) break;
      previous = previousPassage(previous);
      guard += 1;
    }
    var anchor = anchorOf(block, policy);
    if (!anchor && previous) anchor = anchorOf(previous, policy);
    return {
      number: own || number,
      text: clauseTextOf(block),
      anchor: anchor
    };
  }

  function selectedPassage() {
    var policy = document.querySelector(".policy-text");
    var page = pageIdentity();
    if (!policy || !page) return null;
    var sel = window.getSelection();
    if (!sel || !sel.rangeCount || sel.isCollapsed) return null;
    var range = sel.getRangeAt(0);
    if (!policy.contains(range.startContainer) || !policy.contains(range.endContainer)) return null;
    var text = plainText(sel.toString());
    if (text.length < 2) return null;
    var startEl = elementOf(range.startContainer);
    var block = startEl && startEl.closest ? startEl.closest("p") : null;
    if (!block || !policy.contains(block)) return null;
    var passage = passageFor(block, policy);
    if (!passage.text) return null;
    var title = passage.number ? passage.number + " — " + passage.text : passage.text;
    return cleanItem({
      href: page.href,
      find: text,
      title: title,
      snippet: text,
      clause: passage.number,
      clauseText: passage.text,
      anchor: passage.anchor,
      doc: page.doc,
      number: page.number
    });
  }

  function hideSelectMenu() {
    selectMenu.hidden = true;
    pendingSelection = null;
  }

  function showSelectMenu(event, item) {
    pendingSelection = item;
    var saved = indexOf(item.id) >= 0;
    selectAdd.textContent = saved ? "Already in the cart" : "Add highlight to cart";
    selectAdd.disabled = saved;
    selectNote.textContent = item.clause
      ? "Saves the highlight with clause " + item.clause + "."
      : "Saves the highlight with this passage.";
    selectMenu.hidden = false;
    selectMenu.style.left = "0px";
    selectMenu.style.top = "0px";
    var rect = selectMenu.getBoundingClientRect();
    var x = Math.max(8, Math.min(event.clientX, window.innerWidth - rect.width - 8));
    var y = Math.max(8, Math.min(event.clientY, window.innerHeight - rect.height - 8));
    selectMenu.style.left = x + "px";
    selectMenu.style.top = y + "px";
    suspendMenuDismiss = true;
    try { selectAdd.focus({ preventScroll: true }); } catch (err) { selectAdd.focus(); }
    window.setTimeout(function () { suspendMenuDismiss = false; }, 200);
  }

  function bindSourceHint() {
    var policy = document.querySelector(".policy-text");
    if (!policy || !pageIdentity() || document.querySelector(".cart-select-hint")) return;
    var hint = document.createElement("p");
    hint.className = "fine cart-select-hint no-print";
    hint.textContent = "Highlight a word or sentence in this section, then choose Add to cart. The clause is saved with those words highlighted.";
    policy.parentNode.insertBefore(hint, policy);
  }

  var addFloat = null;
  var pendingHighlight = null;
  var skipAddClick = false;
  var addFloatTimer = 0;

  function syncAddFloat() {
    if (!addFloat) return;
    var item = selectedPassage();
    pendingHighlight = item;
    if (!item) {
      addFloat.classList.remove("is-ready");
      addFloat.textContent = "Add to cart";
      addFloat.setAttribute("aria-label", "Highlight a word or sentence in the source text, then add that clause to the cart");
      return;
    }
    var saved = indexOf(item.id) >= 0;
    addFloat.classList.toggle("is-ready", !saved);
    addFloat.textContent = saved ? "In cart" : "Add to cart";
    addFloat.setAttribute("aria-label", saved
      ? "This highlight is already in the cart"
      : "Add the highlighted text with clause " + (item.clause || "text") + " to the cart");
  }

  function commitHighlight() {
    var item = pendingHighlight || selectedPassage();
    if (!item) {
      if (!addFloat) return;
      addFloat.textContent = "Highlight text first";
      window.clearTimeout(addFloatTimer);
      addFloatTimer = window.setTimeout(syncAddFloat, 1400);
      return;
    }
    if (add(item)) openPanel();
    syncAddFloat();
  }

  function bindAddFloat() {
    var policy = document.querySelector(".policy-text");
    if (!policy || !pageIdentity() || document.querySelector(".cart-add-float")) return;
    addFloat = document.createElement("button");
    addFloat.type = "button";
    addFloat.className = "cart-add-float no-print";
    addFloat.hidden = true;
    addFloat.textContent = "Add to cart";
    document.body.appendChild(addFloat);
    syncAddFloat();
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        var visible = false;
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible = true;
        });
        addFloat.hidden = !visible;
      }, { threshold: 0 });
      observer.observe(policy);
    } else {
      addFloat.hidden = false;
    }
    document.addEventListener("selectionchange", syncAddFloat);
    addFloat.addEventListener("pointerdown", function (event) {
      if (event.button !== 0) return;
      event.preventDefault();
      pendingHighlight = selectedPassage();
    });
    addFloat.addEventListener("pointerup", function (event) {
      if (event.button !== 0) return;
      var rect = addFloat.getBoundingClientRect();
      var inside = event.clientX >= rect.left && event.clientX <= rect.right &&
        event.clientY >= rect.top && event.clientY <= rect.bottom;
      if (!inside) return;
      skipAddClick = true;
      commitHighlight();
      window.setTimeout(function () { skipAddClick = false; }, 0);
    });
    addFloat.addEventListener("pointercancel", function () {
      skipAddClick = true;
    });
    addFloat.addEventListener("click", function () {
      if (skipAddClick) {
        skipAddClick = false;
        return;
      }
      commitHighlight();
    });
  }

  importBtn.addEventListener("click", function () {
    importInput.click();
  });
  importInput.addEventListener("change", function () {
    var file = importInput.files && importInput.files[0];
    importInput.value = "";
    if (!file) return;
    if (file.size > 500000) {
      window.alert("That file is too large to import. The cart was not changed.");
      return;
    }
    var reader = new FileReader();
    reader.onload = function () {
      try {
        reportImport(importCsvText(String(reader.result || "")));
      } catch (err) {
        window.alert("Could not import that CSV. The cart was not changed.");
      }
    };
    reader.onerror = function () {
      window.alert("Could not read that file. The cart was not changed.");
    };
    reader.readAsText(file);
  });
  selectAdd.addEventListener("click", function () {
    var item = pendingSelection;
    hideSelectMenu();
    if (!item) return;
    if (add(item)) openPanel();
  });
  document.addEventListener("contextmenu", function (event) {
    if (selectMenu.contains(event.target)) return;
    var item = selectedPassage();
    if (!item) {
      hideSelectMenu();
      return;
    }
    event.preventDefault();
    showSelectMenu(event, item);
  });
  document.addEventListener("pointerdown", function (event) {
    if (selectMenu.hidden || selectMenu.contains(event.target)) return;
    hideSelectMenu();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !selectMenu.hidden) hideSelectMenu();
  });
  window.addEventListener("scroll", function () {
    if (!suspendMenuDismiss) hideSelectMenu();
  }, true);
  window.addEventListener("resize", function () {
    if (!suspendMenuDismiss) hideSelectMenu();
  });
  bindSourceHint();
  bindAddFloat();

  toggle.addEventListener("click", function () {
    if (panel.hidden) openPanel();
    else closePanel();
  });
  closeBtn.addEventListener("click", closePanel);
  pdfBtn.addEventListener("click", printPdf);
  csvBtn.addEventListener("click", downloadCsv);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden && selectMenu.hidden) closePanel();
  });
  document.addEventListener("pointerdown", function (event) {
    if (panel.hidden || root.contains(event.target)) return;
    if (event.target.closest && event.target.closest("[data-cart-save], .source-search, .topnav-search-panel, .cart-select-menu, .cart-add-float")) return;
    panel.hidden = true;
    syncChrome();
  });

  window.HubCart = {
    key: function (raw) {
      var item = cleanItem(raw);
      return item ? item.id : "";
    },
    has: function (id) { return indexOf(id) >= 0; },
    add: add,
    remove: remove
  };

  render();
})();
