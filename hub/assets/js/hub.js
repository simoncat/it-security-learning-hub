(function () {
  var CTX = "hksarg-hub:context";
  var TICK_PREFIX = "hksarg-hub:ticks:";
  var GAP_KEY = "hksarg-hub:gap-table";

  function readJson(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (err) {
      return fallback;
    }
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
      role: params.get("role") || "",
      sdlc: params.get("sdlc") || "",
      need: params.get("need") || "",
      tier: params.get("tier") || "",
      mod: params.get("mod") || ""
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

  function safeReturn(href) {
    if (!href || href.indexOf("://") !== -1 || href.indexOf("\\") !== -1 || href.indexOf("..") !== -1) return "";
    if (!/\.html([?#]|$)/.test(href)) return "";
    return href;
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
    if (role) {
      var roleInput = form.querySelector('input[name="role"][value="' + role + '"]');
      if (roleInput) roleInput.checked = true;
    }
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
  function addGapRow(values) {
    var row = document.createElement("tr");
    for (var i = 0; i < 5; i += 1) {
      var cell = document.createElement("td");
      cell.contentEditable = "true";
      cell.textContent = values && values[i] ? values[i] : "";
      cell.addEventListener("input", saveGap);
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
      gapBody.querySelectorAll("td").forEach(function (cell) {
        cell.addEventListener("input", saveGap);
      });
    }
    if (existing && existing.length) writeGap(existing);
    else if (!gapBody.querySelector("tr")) {
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
    var fromLabel = (fromParams.get("fromLabel") || "where you were").replace(/\s+/g, " ").trim();
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
    var catalogue = JSON.parse(launcherNode.textContent);
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
          link.href = prefix + row.href;
          link.textContent = row.title;
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
    var query = (params.get("find") || "").replace(/\s+/g, " ").trim();
    if (query.length < 2) return;
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
    var at = -1;
    var length = needle.length;
    if (query.indexOf(" ") === -1) {
      var escaped = needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      var match = new RegExp("(^|[^A-Za-z0-9/.])(" + escaped + ")(?![A-Za-z0-9/.])", "i").exec(norm);
      if (!match) return;
      at = match.index + match[1].length;
      length = match[2].length;
    } else {
      at = norm.toLowerCase().indexOf(needle);
      if (at < 0) return;
    }
    if (at + length - 1 >= map.length) return;
    var rawStart = map[at];
    var rawEnd = map[at + length - 1] + 1;
    var first = null;
    nodes.forEach(function (item) {
      var nodeStart = item.start;
      var nodeEnd = nodeStart + item.node.nodeValue.length;
      if (nodeEnd <= rawStart || nodeStart >= rawEnd) return;
      var localStart = Math.max(0, rawStart - nodeStart);
      var localEnd = Math.min(item.node.nodeValue.length, rawEnd - nodeStart);
      if (localStart >= localEnd) return;
      var range = document.createRange();
      range.setStart(item.node, localStart);
      range.setEnd(item.node, localEnd);
      var mark = document.createElement("mark");
      mark.className = "find-hit";
      range.surroundContents(mark);
      if (!first) first = mark;
    });
    if (!first) return;
    first.id = "find-hit";
    window.setTimeout(function () { first.scrollIntoView({ block: "center" }); }, 0);
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
})();
