(function () {
  "use strict";

  var terms = window.GLOSSARY_TERMS;
  if (!terms || !terms.length) return;

  var path = (location.pathname || "").replace(/\\/g, "/");
  if (/\/glossary\.html$/i.test(path) || /\/glossary$/i.test(path)) return;

  var main = document.getElementById("main");
  if (!main) return;

  var glossaryPage = document.body.getAttribute("data-glossary-page") || "glossary.html";

  var byLower = Object.create(null);
  var sorted = terms.slice().sort(function (a, b) {
    return b.term.length - a.term.length;
  });
  sorted.forEach(function (item) {
    byLower[item.term.toLowerCase()] = item;
  });

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  var pattern = new RegExp(
    "\\b(" + sorted.map(function (item) { return escapeRegExp(item.term); }).join("|") + ")\\b",
    "gi"
  );

  var SKIP = {
    SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEXTAREA: 1, INPUT: 1, SELECT: 1,
    OPTION: 1, BUTTON: 1, CODE: 1, PRE: 1, KBD: 1, SAMP: 1, SVG: 1
  };

  function shouldSkip(node) {
    var el = node.parentElement;
    while (el && el !== main) {
      if (SKIP[el.tagName]) return true;
      if (el.classList && (el.classList.contains("glossary-term") || el.classList.contains("glossary-term-pop"))) {
        return true;
      }
      if (el.getAttribute && el.getAttribute("contenteditable") === "true") return true;
      el = el.parentElement;
    }
    return false;
  }

  var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, null);
  var textNodes = [];
  var node;
  while ((node = walker.nextNode())) {
    if (!node.nodeValue || !node.nodeValue.trim()) continue;
    if (shouldSkip(node)) continue;
    if (!pattern.test(node.nodeValue)) {
      pattern.lastIndex = 0;
      continue;
    }
    pattern.lastIndex = 0;
    textNodes.push(node);
  }

  textNodes.forEach(function (textNode) {
    var text = textNode.nodeValue;
    pattern.lastIndex = 0;
    var match;
    var last = 0;
    var frag = document.createDocumentFragment();
    var found = false;
    while ((match = pattern.exec(text))) {
      found = true;
      if (match.index > last) {
        frag.appendChild(document.createTextNode(text.slice(last, match.index)));
      }
      var raw = match[0];
      var item = byLower[raw.toLowerCase()];
      if (!item) {
        frag.appendChild(document.createTextNode(raw));
      } else {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "glossary-term";
        btn.textContent = raw;
        btn.setAttribute("aria-label", raw + ", glossary term");
        btn.setAttribute("data-glossary-id", item.id);
        btn.setAttribute("data-glossary-term", item.term);
        btn.setAttribute("data-glossary-def", item.definition);
        frag.appendChild(btn);
      }
      last = match.index + raw.length;
    }
    if (!found) return;
    if (last < text.length) {
      frag.appendChild(document.createTextNode(text.slice(last)));
    }
    textNode.parentNode.replaceChild(frag, textNode);
  });

  var pop = document.createElement("div");
  pop.className = "glossary-term-pop";
  pop.hidden = true;
  pop.setAttribute("role", "dialog");
  pop.setAttribute("aria-label", "Glossary definition");
  document.body.appendChild(pop);

  var openBtn = null;

  function closePop() {
    pop.hidden = true;
    pop.innerHTML = "";
    if (openBtn) {
      openBtn.setAttribute("aria-expanded", "false");
      openBtn = null;
    }
  }

  function openPop(btn) {
    var term = btn.getAttribute("data-glossary-term") || "";
    var def = btn.getAttribute("data-glossary-def") || "";
    var id = btn.getAttribute("data-glossary-id") || "";
    closePop();
    openBtn = btn;
    btn.setAttribute("aria-expanded", "true");
    pop.innerHTML = "";
    var title = document.createElement("p");
    title.className = "glossary-term-pop-term";
    title.textContent = term;
    var body = document.createElement("p");
    body.className = "glossary-term-pop-def";
    body.textContent = def;
    var link = document.createElement("a");
    link.href = glossaryPage + (id ? "#" + id : "");
    link.textContent = "Open in Glossary";
    pop.appendChild(title);
    pop.appendChild(body);
    pop.appendChild(link);
    pop.hidden = false;

    var rect = btn.getBoundingClientRect();
    var popWidth = Math.min(360, window.innerWidth - 24);
    pop.style.width = popWidth + "px";
    var left = rect.left + window.scrollX;
    if (left + popWidth > window.scrollX + window.innerWidth - 12) {
      left = window.scrollX + window.innerWidth - popWidth - 12;
    }
    if (left < window.scrollX + 12) left = window.scrollX + 12;
    var top = rect.bottom + window.scrollY + 8;
    pop.style.left = left + "px";
    pop.style.top = top + "px";
  }

  main.addEventListener("click", function (event) {
    var btn = event.target.closest(".glossary-term");
    if (!btn || !main.contains(btn)) return;
    event.preventDefault();
    if (openBtn === btn && !pop.hidden) {
      closePop();
      return;
    }
    openPop(btn);
  });

  document.addEventListener("click", function (event) {
    if (pop.hidden) return;
    if (event.target.closest(".glossary-term-pop")) return;
    if (event.target.closest(".glossary-term")) return;
    closePop();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closePop();
  });
})();
