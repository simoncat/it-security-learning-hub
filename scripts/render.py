#!/usr/bin/env python3
"""Generate the static hub. Readers open hub/index.html; they do not run this."""

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_paths import APPLY, FOUNDATION, PACE, ROLES
from content_quizzes import QUIZZES
from content_static import CHEATS, MATRIX, WALKS
from figures import section_figure
from search_glossary import EQUIVALENTS
from pages_new import (
    PACKS,
    PAGES,
    STAGES,
    about_page,
    all_cards,
    appendix_page,
    catalogue,
    core1_index,
    core3_index,
    core4_index,
    current_staff_page,
    decision_page,
    glossary_page,
    glossary_term_id,
    gov_page,
    home_page,
    hub_glossary_terms,
    load_infosec_glossary,
    need_index,
    new_joiners_page,
    qa_page,
    sdlc_page,
    side_groups,
    source_links,
    source_page,
    spine_page,
    toc_page,
)

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "hub"
VERSION = (
    "Hub v0.1-MVP · Content aligned to S17 v8.2 / G3 v10.2 · Last reviewed: 2026-10-26"
)
REVIEWED = "2026-10-26"
DISCLAIMER = (
    "Learning aid only. Authoritative text remains S17, G3, Security Regulations, and B/D local policies."
)
CURRENT = "index.html"

# Scripts every page loads. Extra per-page scripts (e.g. quiz.js) still go through
# versioned_asset(), so their ?v= hash updates whenever the file bytes change.
CORE_SCRIPTS = (
    "assets/js/hub.js",
    "assets/js/hub-search-data.js",
    "assets/js/hub-search.js",
    "assets/js/source-search-data.js",
    "assets/js/source-search.js",
    "assets/js/glossary-terms-data.js",
    "assets/js/glossary-terms.js",
)

# Content-hash cache for one render run. Cleared at the start of main().
_ASSET_HASH: dict[str, str] = {}
# Render-wide stamp embedded in HTML and written to hub/build-id.txt.
BUILD_ID = ""


def asset_version(rel: str) -> str:
    """Short sha256 of hub/<rel>. Used as ?v= so browsers fetch when the file changes."""
    cached = _ASSET_HASH.get(rel)
    if cached is not None:
        return cached
    path = HUB / rel
    if not path.is_file():
        raise FileNotFoundError(f"Cannot version missing hub asset: {rel}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    _ASSET_HASH[rel] = digest
    return digest


def versioned_asset(rel: str) -> str:
    """Href to a hub asset with a content-hash query string."""
    return f"{href(rel)}?v={asset_version(rel)}"


def compute_build_id() -> str:
    """Stamp that changes whenever any versioned hub asset bytes change."""
    digest = hashlib.sha256()
    for rel in ("assets/css/hub.css", *CORE_SCRIPTS, "assets/js/quiz.js"):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update((HUB / rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:12]


def write_cache_control_files(build_id: str) -> None:
    """Workers `_headers` + `build-id.txt` for HTML revalidation / soft reload."""
    (HUB / "build-id.txt").write_text(build_id + "\n", encoding="utf-8")
    # GitHub Pages ignores this file; Cloudflare Workers Assets applies it.
    (HUB / "_headers").write_text(
        """# HTML and non-fingerprinted files: revalidate on every F5 / navigation.
/
  Cache-Control: no-cache

/*
  Cache-Control: no-cache

# Fingerprinted CSS/JS (?v=content-hash): long-lived browser cache.
/assets/*
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

# Soft-reload stamp must stay revalidate-only (not under /assets immutable).
/build-id.txt
  ! Cache-Control
  Cache-Control: no-cache
""",
        encoding="utf-8",
    )


TOP = [
    ("index.html", "Home"),
    ("spine.html", "Overview"),
    ("start/new-joiners.html", "New joiners"),
    ("start/current-staff.html", "Current staff"),
    ("core1/index.html", "Aids"),
    ("core2/index.html", "Quizzes"),
    ("core3/index.html", "Q&A"),
    ("core4/index.html", "Source"),
    ("app-c-matrix.html", "App C"),
    ("glossary.html", "Glossary"),
    ("about.html", "About"),
]


def soften(text):
    if not text:
        return ""
    replacements = (
        ("Days 22–30", "the apply block"),
        ("Days 22–24", "the tier-mapping block"),
        ("Days 8–30", "the role path"),
        ("Days 8–21", "the role path"),
        ("Day 28", "the walkthrough"),
        ("Track A", "New joiners"),
        ("Track B", "Current staff"),
        ("Both tracks. ", ""),
        ("Track check-ins", "Check-ins"),
        ("around Day 14 and Day 21", "mid-path and at the end of the role path"),
        ("Day 14 and Day 21", "mid-path and end of path"),
        ("around Day 14", "mid-path"),
        ("around Day 21", "at the end of the role path"),
        ("optional Day 14", "optional mid-path"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def json_for_script(value):
    """Serialize JSON for embedding in HTML/JS without breaking out of a script tag."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def href(target):
    current_dir = Path(CURRENT).parent
    origin = Path(".") if str(current_dir) == "." else current_dir
    rel = Path(target)
    # os.path.relpath handles ".."
    import os
    return os.path.relpath(str(rel), str(origin) if str(origin) != "." else ".")


def asset(path):
    return href(path)


def legend_html():
    return """
<details class="legend-bar" open>
  <summary>Legend</summary>
  <div class="legend-row">
    <span><span class="badge badge-shall">Shall</span> mandatory — must do</span>
    <span><span class="badge badge-should">Should</span> best practice — implement whenever possible</span>
    <span><span class="badge badge-may">May</span> desirable best practice</span>
    <span><span class="badge badge-appc">App C</span> extra controls for Tier 2 or Tier 3. Tier 3 includes every Tier 2 control.</span>
    <span class="plain">Checkbox = optional self-progress tick. Stored only in this browser.</span>
  </div>
</details>
"""


def read_guide():
    return """
<div class="callout callout-read">
  <strong>Not every-word — S17 first, then G3; deep-read Shall and App C; Should = implement whenever possible.</strong>
  <p>Reading order: S17, then the same-theme G3 section, then Appendix C if the system is Tier 2 or Tier 3.</p>
</div>
"""


def toolbar(print_label):
    return f"""
<div class="toolbar no-print">
  <button type="button" class="btn btn-ghost" data-filter="all" aria-pressed="true">All items</button>
  <button type="button" class="btn btn-ghost" data-filter="flag" aria-pressed="false">Show only App C items</button>
  <button type="button" class="btn btn-ghost" data-filter="shall" aria-pressed="false">Shall only</button>
  <button type="button" class="btn btn-ghost" data-action="expand" data-open="true">Expand sections</button>
  <button type="button" class="btn btn-ghost" data-action="expand" data-open="false">Collapse sections</button>
  <button type="button" class="btn btn-primary" data-action="print">{esc(print_label)}</button>
  <button type="button" class="btn btn-ghost" data-action="clear-ticks">Clear ticks in this browser</button>
</div>
<p class="storage-note">Optional self-progress. Stored only in this browser.</p>
<p data-progress-readout></p>
"""


def chips(refs):
    parts = []
    for doc, label in refs:
        match = re.search(r"\d+", label)
        number = f"{int(match.group()):02d}" if match else ""
        if doc == "App C":
            anchor = f"area-{int(match.group())}" if match else "inheritance"
            url = href("core4/g3/appendix-c.html") + "#" + anchor
            cls = "chip chip-appc"
        elif doc == "S17":
            url = href(f"core4/s17/s{number}.html") if number else href("core4/s17/index.html")
            cls = "chip chip-s17"
        else:
            url = href(f"core4/g3/s{number}.html") if number else href("core4/g3/index.html")
            cls = "chip chip-g3"
        if parts:
            parts.append('<span class="chip-arrow" aria-hidden="true">→</span>')
        parts.append(f'<a class="{cls}" href="{url}">{esc(doc)} {esc(label)}</a>')
    return "".join(parts)


def item_html(item):
    flag = "1" if item["flag"] else "0"
    badges = f'<span class="badge badge-{esc(item["modality"])}">{esc(item["modality"].capitalize())}</span>'
    if item["flag"]:
        badges += ' <span class="badge badge-appc">App C</span>'
    note = soften(item.get("note") or PACE.get(item["pace"], ""))
    text = soften(item["text"])
    refs = f'<p class="refs">{chips(item["refs"])}</p>' if item.get("refs") else ""
    return f"""
<li class="item" id="{esc(item["id"])}" data-id="{esc(item["id"])}" data-modality="{esc(item["modality"])}" data-flag="{flag}" data-pace="{esc(item["pace"])}">
  <div class="item-row">
    <input type="checkbox" id="tick-{esc(item["id"])}" data-tick="{esc(item["id"])}" aria-describedby="note-{esc(item["id"])}">
    <div>
      <div class="item-meta">{badges}<span class="id-code">{esc(item["id"])}</span></div>
      <label for="tick-{esc(item["id"])}">{esc(text)}</label>
      <p class="item-note" id="note-{esc(item["id"])}">{esc(note)}</p>
      {refs}
    </div>
  </div>
</li>
"""


def days_html(days):
    blocks = []
    for day in days:
        pace = day.get("pace", "both")
        chip = ""
        if pace == "b-gap":
            chip = '<span class="pace-chip">Current staff: if gap</span>'
        order = ""
        if day.get("order"):
            order = f'<p class="order-line">Order: {esc(soften(day["order"]))}</p>'
        items = "\n".join(item_html(item) for item in day["items"])
        if day.get("focus"):
            label = day["focus"]
            title = ""
        elif str(day.get("label", "")).startswith("Day") and day.get("title"):
            label = day["title"]
            title = ""
        else:
            label = day.get("label") or day.get("days") or "Section"
            title = day.get("title") or day.get("focus") or ""
        label = soften(label)
        anchor = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        blocks.append(f"""
<details class="day" open data-pace="{esc(pace)}" id="{esc(anchor)}">
  <summary>
    <span class="day-kicker">{esc(label)}</span>
    <span class="day-title">{esc(title)}</span>
    {chip}
  </summary>
  <div class="day-body">
    {order}
    <ul class="items">{items}</ul>
  </div>
</details>
""")
    return "\n".join(blocks)


def blocks_html(blocks):
    out = []
    for block in blocks:
        kind = block["type"]
        if kind == "h2":
            out.append(f"<h2>{esc(block['text'])}</h2>")
        elif kind == "p":
            out.append(f"<p>{esc(block['text'])}</p>")
        elif kind == "callout":
            out.append(f'<div class="callout">{esc(block["text"])}</div>')
        elif kind == "ul":
            lis = "".join(f"<li>{esc(item)}</li>" for item in block["items"])
            out.append(f"<ul>{lis}</ul>")
        elif kind == "ol":
            lis = "".join(f"<li>{esc(item)}</li>" for item in block["items"])
            out.append(f"<ol>{lis}</ol>")
        elif kind == "flow":
            steps = []
            for index, step in enumerate(block["steps"], start=1):
                title, detail = step
                detail_html = f"<span>{esc(detail)}</span>" if detail else ""
                steps.append(
                    f'<li><span class="read-flow-step">{index}</span>'
                    f"<div><strong>{esc(title)}</strong>{detail_html}</div></li>"
                )
            out.append(f'<ol class="read-flow" aria-label="Reading flow">{"".join(steps)}</ol>')
        elif kind == "table":
            head = "".join(f"<th>{esc(cell)}</th>" for cell in block["headers"])
            rows = []
            for row in block["rows"]:
                rows.append("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>")
            out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>")
    return "\n".join(out)


def shell(rel, title, page_id, crumbs, source, main, scripts):
    global CURRENT
    CURRENT = rel
    depth_css = asset("hub/assets/css/hub.css")
    # asset() uses CURRENT which is the page rel, and target is from repo root.
    # Fix: assets live under hub/, pages live under hub/. So target should be assets/...
    # I'll pass paths relative to hub root.
    raise RuntimeError("use write_page")


def write_page(rel, title, page_id, crumbs, source, main, extra_scripts=None):
    global CURRENT
    CURRENT = rel
    css = versioned_asset("assets/css/hub.css")
    csp = (
        "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
        "form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; upgrade-insecure-requests"
    )
    top_links = []
    for target, label in TOP:
        target_path = target.split("#")[0]
        folder = str(Path(target_path).parent)
        in_section = folder not in (".", "") and Path(target_path).name == "index.html" and rel.startswith(folder + "/")
        current = ' aria-current="page"' if target_path == rel or in_section else ""
        top_links.append(f'<a href="{href(target)}"{current}>{esc(label)}</a>')
    side_html = []
    for group, links in side_groups(rel):
        side_html.append(f'<p class="nav-label">{esc(group)}</p>')
        for target, label in links:
            target_path = target.split("#")[0]
            current = ' aria-current="page"' if target_path == rel and "#" not in target else ""
            side_html.append(f'<a href="{href(target_path)}{("#" + target.split("#", 1)[1]) if "#" in target else ""}"{current}>{esc(label)}</a>')
    crumb_bits = []
    for index, (target, label) in enumerate(crumbs):
        if index == len(crumbs) - 1:
            crumb_bits.append(f"<li aria-current=\"page\">{esc(label)}</li>")
        else:
            crumb_bits.append(f'<li><a href="{href(target)}">{esc(label)}</a></li>')
    home = href("index.html")
    search_root = "" if home == "index.html" else home[: -len("index.html")]
    full_search_href = href("core4/index.html")
    script_rels = list(CORE_SCRIPTS)
    for extra in extra_scripts or []:
        if extra not in script_rels:
            script_rels.append(extra)
    scripts = "\n".join(f'<script src="{versioned_asset(path)}"></script>' for path in script_rels)
    icon = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' rx='6' fill='%230e2744'/%3E"
        "%3Ctext x='16' y='21' text-anchor='middle' font-size='11' fill='white' "
        "font-family='Arial' font-weight='700'%3EGS%3C/text%3E%3C/svg%3E"
    )
    search_icon = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" focusable="false" aria-hidden="true">'
        '<circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="2"></circle>'
        '<path d="M16.5 16.5L21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>'
        "</svg>"
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="{esc(csp)}">
  <meta name="referrer" content="no-referrer">
  <meta name="color-scheme" content="light">
  <title>{esc(title)} · HKSARG IT Security Learning Hub</title>
  <meta name="description" content="{esc(title)}. Static learning aid for S17 v8.2 and G3 v10.2.">
  <link rel="icon" href="{icon}">
  <link rel="stylesheet" href="{css}">
</head>
<body data-page-id="{esc(page_id)}" data-page="{esc(page_id)}" data-hub-build="{esc(BUILD_ID)}" data-source-sections="{esc(source)}" data-last-reviewed="{REVIEWED}" data-owner-role="Hub Content Owner" data-glossary-page="{href("glossary.html")}" data-search-root="{esc(search_root)}">
  <a class="skip" href="#main">Skip to content</a>
  <header class="mast">
    <div class="mast-inner">
      <a class="brand" href="{home}">
        <span class="brand-mark" aria-hidden="true">GS</span>
        <span>
          <strong>HKSARG IT Security Learning Hub</strong>
          <small>S17 + G3</small>
        </span>
      </a>
    </div>
  </header>
  <div class="version" role="note">{esc(VERSION)}</div>
  <nav class="topnav" aria-label="Primary">
    <div class="topnav-inner">
      <div class="topnav-links">{''.join(top_links)}</div>
      <div class="topnav-search no-print">
        <button type="button" class="topnav-search-trigger" data-hub-search-open aria-haspopup="dialog" aria-controls="hub-search-modal">
          <span class="topnav-search-icon" aria-hidden="true">{search_icon}</span>
          <span class="topnav-search-label">Search</span>
          <kbd class="topnav-search-kbd" data-search-shortcut-hint aria-hidden="true">Ctrl+K</kbd>
        </button>
      </div>
    </div>
  </nav>
  <nav class="crumb" aria-label="Breadcrumb"><ol>{''.join(crumb_bits)}</ol></nav>
  <div class="shell">
    <details class="sidenav" open>
      <summary>On this hub</summary>
      <nav aria-label="Section">{''.join(side_html)}</nav>
    </details>
    <main id="main">
      {main}
    </main>
  </div>
  <footer class="site-footer">
    <div class="site-footer-inner">
      <p>{esc(DISCLAIMER)}</p>
      <nav aria-label="Footer">
        <a href="{href("glossary.html")}">Glossary</a>
        <a href="{href("about.html")}">About and versions</a>
        <a href="{href("governance.html")}">Content governance</a>
        <a href="{href("start/new-joiners.html")}">New joiners</a>
      </nav>
      <div class="progress-transfer no-print">
        <p class="fine">Optional ticks and gap notes stay in this browser. Not a sign-off.</p>
        <button type="button" class="btn btn-ghost" data-action="export-progress">Export Progress</button>
        <button type="button" class="btn btn-ghost" data-action="import-progress">Import Progress</button>
        <input type="file" accept="application/json,.json" data-progress-import hidden>
      </div>
    </div>
  </footer>
  <div id="hub-search-modal" class="hub-search-modal" hidden>
    <div class="hub-search-backdrop" data-hub-search-close tabindex="-1"></div>
    <div class="hub-search-dialog" role="dialog" aria-modal="true" aria-labelledby="hub-search-title" data-hub-search-dialog>
      <div class="hub-search-bar">
        <span class="hub-search-bar-icon" aria-hidden="true">{search_icon}</span>
        <input id="hub-search-input" class="hub-search-input" type="search" autocomplete="off" spellcheck="false" placeholder="Search aids, quizzes, Q&amp;A, source, glossary…" data-hub-search-input aria-controls="hub-search-results">
        <button type="button" class="hub-search-clear" data-hub-search-clear hidden aria-label="Clear search">×</button>
        <kbd class="hub-search-esc" aria-hidden="true">Esc</kbd>
      </div>
      <div id="hub-search-results" class="hub-search-body" data-hub-search-body tabindex="-1">
        <h2 id="hub-search-title" class="hub-search-lead">Search decision aids, quizzes, Q&amp;A, source sections, and glossary terms</h2>
        <p class="hub-search-try-label">Try searching for</p>
        <div class="hub-search-try" data-hub-search-suggestions></div>
      </div>
      <div class="hub-search-footer">
        <p class="hub-search-hints">
          <kbd aria-hidden="true">↑</kbd><kbd aria-hidden="true">↓</kbd> navigate
          <kbd aria-hidden="true">↵</kbd> open
        </p>
        <a class="hub-search-full" href="{full_search_href}" data-hub-search-full>Full site search</a>
      </div>
    </div>
  </div>
  {scripts}
</body>
</html>
"""
    path = HUB / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html


def home_main():
    return home_page(href, esc, legend_html(), read_guide())


def start_main():
    index_groups = []
    for group, links in side_groups("index.html"):
        items = "".join(
            f'<li data-index-item><a href="{href(target)}">{esc(label)}</a></li>' for target, label in links
        )
        index_groups.append(f"<h3>{esc(group)}</h3><ul>{items}</ul>")
    return f"""
<h1>How to use this hub</h1>
<p class="lede">A 30-day reading path for B/D IT staff. Track A is induction. Track B is a refresh and a gap close. Both use the same role days and the same apply block.</p>
{read_guide()}
<h2>Four moves</h2>
<ol>
  <li>Pick a track and a role on the home page.</li>
  <li>Do Days 1–7 at your track’s pace. Days 4–7 are marked “B: if gap”.</li>
  <li>Follow your role on Days 8–21, then the shared apply block.</li>
  <li>Use a cheat sheet, one walkthrough, and a quiz when you want to check yourself.</li>
</ol>
<h2>Legend</h2>
{legend_html()}
<table>
  <caption>Words you will meet in S17 and G3</caption>
  <thead><tr><th>Marker</th><th>Meaning</th></tr></thead>
  <tbody>
    <tr><td>Shall</td><td>Mandatory requirement — must do</td></tr>
    <tr><td>Should</td><td>Best practice — implement whenever possible</td></tr>
    <tr><td>May</td><td>Desirable best practice</td></tr>
    <tr><td>Checkbox</td><td>Tick when you have done the learning step. Optional. This browser only.</td></tr>
    <tr><td>App C</td><td>Extra controls when the system is Tier 2 or Tier 3. Tier 3 also takes every Tier 2 App C control.</td></tr>
  </tbody>
</table>
<h2>Track comparison</h2>
<div class="track-split">
  <article class="track-card track-a">
    <h3>Track A — New joiners</h3>
    <ul>
      <li>Days 1–7: full foundation at induction pace.</li>
      <li>Days 8–21: steady role path. Optional buddy check-ins around Day 14 and Day 21.</li>
      <li>Days 22–30: buddy-assisted tier map, then one walkthrough.</li>
      <li>Optional coaching at Day 3, Day 7, Day 14, Day 21, and Day 30. Not gates.</li>
      <li>About 60–90 minutes a day.</li>
    </ul>
  </article>
  <article class="track-card track-b">
    <h3>Track B — Current staff</h3>
    <ul>
      <li>Days 1–3: refresh. Days 4–7 only if they are a gap.</li>
      <li>Days 8–21: move faster. For each item ask: evidence, or gap?</li>
      <li>Days 22–30: live systems and open findings, with owners.</li>
      <li>You may share the gap table with your manager or unit. That is optional.</li>
      <li>About 45–75 minutes on the gaps.</li>
    </ul>
  </article>
</div>
<h2>Weekly rhythm</h2>
<table>
  <thead><tr><th>Week</th><th>Days</th><th>Track A</th><th>Track B</th></tr></thead>
  <tbody>
    <tr><td>1</td><td>1–7</td><td>Full foundation. Optional check-ins at Day 3 and Day 7.</td><td>Days 1–3 refresh. Days 4–7 only if gap.</td></tr>
    <tr><td>2</td><td>8–14</td><td>Role path. Optional check-in around Day 14.</td><td>Accelerate. Note evidence or gap.</td></tr>
    <tr><td>3</td><td>15–21</td><td>Finish the role path. Optional check-in around Day 21.</td><td>Map App C controls you already run.</td></tr>
    <tr><td>4</td><td>22–30</td><td>Tier map, one walkthrough, optional Day 30 conversation.</td><td>Live systems, gap owners, optional handoff.</td></tr>
  </tbody>
</table>
<h2>Finding a page</h2>
<p>This release has a page index, not a generated search file. Type here to filter the index, or use Ctrl+F / Cmd+F on the page you opened. Nothing is sent over the network.</p>
<p class="no-print"><label for="page-filter">Filter the index</label> <input id="page-filter" type="search" placeholder="Try incident, tier, role 3"></p>
<div class="page-index">{''.join(index_groups)}</div>
"""


def path_index_main():
    cards = []
    for role in ROLES:
        cards.append(f"""
<a class="role-card" data-role="{role["n"]}" href="{href(f"path/role-{role["n"]}.html")}">
  <h3>{esc(role["title"])}</h3>
  <p>{esc(role["anchor"])}</p>
  <p>{esc(role["quick"])}</p>
</a>""")
    roles = []
    for role in ROLES:
        roles.append(
            f'<label class="choice"><input type="radio" name="role" value="{role["n"]}" required> <span class="choice-k">{esc(role["title"])}</span></label>'
        )
    return f"""
<h1>Learner path</h1>
<p data-context-banner class="context-banner">Select a track and role to highlight your path. All five roles stay on this page.</p>
<form class="launcher no-print" action="{href("path/index.html")}" method="get">
  <h2>Track and role</h2>
  <div class="choice-grid">
    <label class="choice choice-a"><input type="radio" name="track" value="A" required> <span class="choice-k">Track A — New joiners</span></label>
    <label class="choice choice-b"><input type="radio" name="track" value="B" required> <span class="choice-k">Track B — Current staff</span></label>
  </div>
  <div class="choice-grid roles">{''.join(roles)}</div>
  <p><button class="btn btn-primary" type="submit">Apply filter</button></p>
</form>
<div class="anatomy">
  <a class="an-fnd" href="{href("path/foundation.html")}"><strong>Days 1–7 Foundation</strong><span>Shared. Track A does every day. Track B refreshes Days 1–3.</span></a>
  <a class="an-role" id="role-jump" href="{href("path/role-1.html")}"><strong>Days 8–21 Role path</strong><span>Open the highlighted role. The other four stay available.</span></a>
  <a class="an-apply" href="{href("path/apply.html")}"><strong>Days 22–30 Apply</strong><span>Tier map, gaps, one walkthrough, close-out.</span></a>
</div>
<h2>Roles</h2>
<div class="role-grid">{''.join(cards)}</div>
<h2>Weekly rhythm</h2>
<table>
  <thead><tr><th></th><th>Track A</th><th>Track B</th></tr></thead>
  <tbody>
    <tr><td>Days 1–7</td><td>Full foundation</td><td>Days 1–3 refresh. Days 4–7 if gap.</td></tr>
    <tr><td>Days 8–21</td><td>Steady role path and optional check-ins</td><td>Faster. Evidence or gap on each item.</td></tr>
    <tr><td>Days 22–30</td><td>Tier map and a walkthrough</td><td>Live systems and owners</td></tr>
  </tbody>
</table>
"""


def foundation_main():
    exit_items = [
        {"id": "F-EXIT-01", "text": FOUNDATION["exit"][0], "modality": "shall", "pace": "both", "flag": False, "refs": [("G3", "§4")], "note": "Exit check"},
        {"id": "F-EXIT-02", "text": FOUNDATION["exit"][1], "modality": "shall", "pace": "both", "flag": False, "refs": [("G3", "§5")], "note": "Exit check"},
        {"id": "F-EXIT-03", "text": FOUNDATION["exit"][2], "modality": "shall", "pace": "both", "flag": False, "refs": [("G3", "§18")], "note": "Exit check"},
        {"id": "F-EXIT-04", "text": FOUNDATION["exit"][3], "modality": "shall", "pace": "both", "flag": False, "refs": [("G3", "§4"), ("App C", "§4")], "note": "Exit check"},
    ]
    return f"""
<h1>Fundamentals path</h1>
<p class="lede">New joiners work through this after the short phase list. Current staff can use it as a refresh. Themes replace a day count. Shall comes first inside each theme.</p>
<p data-context-banner class="context-banner">Reading order: S17, then G3, then Appendix C only for Tier 2 or Tier 3.</p>
{read_guide()}
{legend_html()}
{toolbar("Print this foundation")}
<div class="track-split">
  <article class="track-card track-a"><h3>New joiners</h3><p>Do every theme. Start from the <a href="{href("start/new-joiners.html")}">new-joiners phases</a> if you want the short path first.</p></article>
  <article class="track-card track-b"><h3>Current staff</h3><p>Use the themes marked “if gap”. For a live task, the <a href="{href("start/current-staff.html")}">role, stage, and need filter</a> is faster.</p></article>
</div>
<div data-checklist>
  {days_html(FOUNDATION["days"])}
  <h2>Foundation exit check</h2>
  <p>You can explain the path when you can do these four things. They are a self-check, not a form anyone files.</p>
  <ul class="items">{''.join(item_html(item) for item in exit_items)}</ul>
</div>
<p><a href="{href("core2/quiz-foundation.html")}">Fundamentals quiz</a> · <a href="{href("start/new-joiners.html")}">New-joiners phases</a></p>
"""


def role_main(role):
    clusters = days_html(role["clusters"])
    effort = f'<p>{esc(role["effort"])}</p>' if role.get("effort") else ""
    return f"""
<h1>{esc(role["title"])}</h1>
<p class="lede">Anchor: {esc(role["anchor"])}. New joiners use this as the bridge out of fundamentals. Current staff use it to see the Shall items for this job. It is not a calendar.</p>
{effort}
<p data-context-banner class="context-banner">Shall first. Appendix C rows apply only when the system is Tier 2 or Tier 3, and Tier 3 inherits Tier 2.</p>
{read_guide()}
{legend_html()}
{toolbar("Print this role path")}
<div class="quick"><strong>Quick win.</strong> {esc(role["quick"])}</div>
<div data-checklist>{clusters}</div>
<p>Suggested walkthrough: {esc(role["walk"])} <a href="{href(f"walkthroughs/role-{role['n']}.html")}">Open the step cards</a>.</p>
<p><a href="{href(f"core2/quiz-role-{role['n']}.html")}">Self-check</a> · <a href="{href("path/apply.html")}">Apply and close gaps</a> · <a href="{href("app-c-matrix.html")}">App C matrix</a> · <a href="{href(f"walkthroughs/role-{role['n']}.html")}">Walkthrough</a></p>
"""


def apply_main():
    rows = []
    for role in ROLES:
        rows.append(
            f"<tr><td>{esc(role['title'])}</td><td>{esc(role['walk'])}</td><td><a href=\"{href('walkthroughs/role-' + role['n'] + '.html')}\">Open walkthrough</a></td></tr>"
        )
    return f"""
<h1>Apply and close gaps</h1>
<p class="lede">Optional. Map a system to a tier, note Appendix C gaps, do one walkthrough, and keep owners on the gap template. Nothing here is submitted.</p>
<p data-context-banner class="context-banner">New joiners map a system to a tier. Current staff work from live systems and open findings.</p>
{read_guide()}
{legend_html()}
{toolbar("Print this apply block")}
<div class="callout">
  <strong>Close-out is not collected.</strong>
  <p>No learner signature, no supervisor or DITSO acknowledgement field, and no printable completion form. Ticks stay in this browser.</p>
</div>
<div data-checklist>{days_html(APPLY)}</div>
<h2>Walkthrough by role</h2>
<table>
  <thead><tr><th>Role</th><th>Suggested walkthrough</th><th>Page</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<p><a href="{href("app-c-matrix.html")}">App C matrix</a> · <a href="{href("gap-template.html")}">Gap template</a> · <a href="{href("core2/quiz-app-c.html")}">App C quiz</a></p>
"""


def cheat_index():
    cards = []
    for cheat in CHEATS:
        cards.append(f'<a class="info-card" href="{href(cheat["file"])}"><h3>{esc(cheat["title"])}</h3><p>{esc(cheat["source"])}</p></a>')
    return f"""
<h1>Cheat sheets</h1>
<p class="lede">One or two printed pages each. They cite section numbers. They are not extracts of the PDFs.</p>
<div class="card-grid">{''.join(cards)}</div>
"""


def cheat_page(cheat):
    return f"""
<h1>{esc(cheat["title"])}</h1>
<p class="fine">Source pointers: {esc(cheat["source"])}</p>
{blocks_html(cheat["blocks"])}
"""


def walk_index():
    cards = []
    for walk in WALKS:
        cards.append(f'<a class="info-card" href="{href(walk["file"])}"><h3>{esc(walk["title"])}</h3><p>{esc(walk["source"])}</p></a>')
    return f"""
<h1>Walkthroughs</h1>
<p>Each role has one suggested exercise. There is also a life-cycle walkthrough. Steps include what to keep and where a Should may wait. Do not invent a live incident, and do not run an intrusive test against a system you are not authorised to assess.</p>
<div class="card-grid">{''.join(cards)}</div>
"""


def walk_page(walk):
    steps = []
    for index, step in enumerate(walk["steps"], start=1):
        defer = f'<p class="defer">{esc(step["defer"])}</p>' if step.get("defer") else ""
        steps.append(f"""
<li class="step">
  <h3>Step {index}. {esc(step["title"])}</h3>
  <p>{esc(step["text"])}</p>
  <p class="keep">Artefacts to keep: {esc(step["keep"])}</p>
  {defer}
</li>""")
    return f"""
<h1>{esc(walk["title"])}</h1>
<p class="fine">Source pointers: {esc(walk["source"])}</p>
{read_guide()}
<p>Where a step is Should, you may defer it if you record why. Shall steps are the ones the policy treats as mandatory. App C steps apply when the system is Tier 2 or Tier 3.</p>
<p class="no-print"><button type="button" class="btn btn-primary" data-action="print">Print this walkthrough</button></p>
<ol class="steps">{''.join(steps)}</ol>
<details>
  <summary>Alternative exercise</summary>
  <p>{esc(walk["alt"])}</p>
</details>
<p><a href="{href("path/apply.html")}">Back to apply and close gaps</a></p>
"""


def quiz_index():
    cards = []
    for quiz in QUIZZES:
        cards.append(
            f'<a class="info-card" href="{href(quiz["file"])}"><h3>{esc(quiz["title"])}</h3><p>{len(quiz["questions"])} questions.</p></a>'
        )
    return f"""
<h1>Self-check quizzes</h1>
<p>Pick your answers and check your score to reveal detailed rationales. Reset anytime to try again. This quiz runs entirely in your browser—no score or attempt data is submitted or stored.</p>
<div class="card-grid">{''.join(cards)}</div>
"""


def quiz_page(quiz):
    payload = json_for_script({"questions": quiz["questions"]})
    return f"""
<h1>{esc(quiz["title"])}</h1>
<p>{esc(quiz["intro"])}</p>
<p class="fine">Source pointers: {esc(quiz["source"])}</p>
<div id="quiz-root"></div>
<script type="application/json" id="quiz-data">{payload}</script>
<noscript><p>This self-check needs JavaScript in the browser. The questions are not sent anywhere.</p></noscript>
"""


def matrix_main():
    rows = []
    for row in MATRIX:
        t2_flag = "0" if row["t2"] == "—" else "1"
        t3_flag = "0" if row["t3"] == "—" else "1"
        rows.append(
            f'<tr id="area-{row["section"]}" data-section="{row["section"]}" data-tier2="{t2_flag}" data-tier3="{t3_flag}">'
            f'<th scope="row">{esc(row["area"])}</th><td>{esc(row["t2"])}</td><td>{esc(row["t3"])}</td></tr>'
        )
    options = ['<option value="all">All sections</option>']
    for row in MATRIX:
        options.append(f'<option value="{row["section"]}">Section {row["section"]}</option>')
    return f"""
<h1>Appendix C — Tier 2 and Tier 3</h1>
<p class="lede" id="inheritance">Tier 3 includes Tier 2. Every Tier 2 Appendix C control also applies to Tier 3. Then add the Tier 3-only column. Always verify the row against the official G3 Appendix C text.</p>
<div class="callout">This is a learning map, not a reproduction of the appendix. Baseline S17/G3 still applies to Tier 1, and it still applies underneath Tier 2 and Tier 3.</div>
<div class="toolbar no-print">
  <button type="button" class="btn btn-ghost" data-tier-filter="all" aria-pressed="true">All rows</button>
  <button type="button" class="btn btn-ghost" data-tier-filter="2" aria-pressed="false">Tier 2 controls (also on Tier 3)</button>
  <button type="button" class="btn btn-ghost" data-tier-filter="3" aria-pressed="false">Tier 3 only</button>
  <label for="appc-section">Section</label>
  <select id="appc-section">{''.join(options)}</select>
  <button type="button" class="btn btn-primary" data-action="print">Print this matrix</button>
</div>
<table class="matrix" id="appc-matrix">
  <caption>G3 Appendix C learning map</caption>
  <thead><tr><th>Area</th><th>Tier 2 (also required for Tier 3)</th><th>Tier 3 only</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<p><a href="{href("core2/quiz-app-c.html")}">App C quiz</a> · <a href="{href("cheatsheets/tier.html")}">Tier cheat sheet</a> · <a href="{href("core4/g3/appendix-c.html")}">Appendix C source map</a></p>
"""


def gap_main():
    cells = "<td contenteditable=\"true\"></td>" * 5
    rows = "".join(f"<tr>{cells}</tr>" for _ in range(4))
    return f"""
<h1>Gap table</h1>
<p>Use this on a live system when a control has no evidence yet. New joiners can use it when a Tier 2 or Tier 3 control is still open. Columns: Control, Evidence, Gap, Owner, Due.</p>
<p class="storage-note">Edits are stored only in this browser. Download a CSV if you want a file of your own. This page does not submit the table.</p>
<div class="toolbar no-print">
  <button type="button" class="btn btn-ghost" data-action="add-gap">Add row</button>
  <button type="button" class="btn btn-primary" data-action="csv-gap">Download CSV</button>
  <button type="button" class="btn btn-ghost" data-action="print">Print this table</button>
  <button type="button" class="btn btn-ghost" data-action="clear-gap">Clear table</button>
</div>
<div class="gap-wrap">
  <table class="gap-table" id="gap-table">
    <caption>Control, evidence, gap, owner, due</caption>
    <thead><tr><th>Control</th><th>Evidence</th><th>Gap</th><th>Owner</th><th>Due</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
"""


MODAL_MEANING = {
    "shall": "Shall — mandatory — must do",
    "should": "Should — best practice — implement whenever possible",
    "may": "May — desirable best practice",
}


def mark_modals(text):
    def repl(match):
        word = match.group(0)
        kind = word.lower()
        return f'<span class="modal modal-{kind}" title="{esc(MODAL_MEANING[kind])}">{word}</span>'
    return re.sub(r"\b(shall|should|may)\b", repl, text, flags=re.I)


ROMAN_MARKS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}
MARKER_RANK = {"bullet": 6, "alpha": 7, "roman": 8}


def is_heading(text, body):
    # A dot inside a name or number (GovCERT.HK, Section 18.1) is not a sentence.
    sentence = re.search(r"[.!?]\s|[.!?]$", body)
    return len(text) <= 160 and sentence is None and ":" not in body and len(body.split()) <= 14


def parse_footnote(stripped):
    match = re.match(r"^(\d{1,2})(?:\s+|(?=[A-Z]))(\S.*)$", stripped)
    if not match or match.group(2).startswith("."):
        return None
    number, body = match.group(1), match.group(2)
    if is_heading(stripped, body):
        return None
    if "." not in body and len(stripped) <= 80:
        return None
    return number, body


def apply_fn_refs(html, notes, prefix, used):
    def repl(match):
        number = match.group(1)
        if number not in notes:
            return match.group(0)
        note_id = f"fn-{prefix}-{number}"
        if number in used:
            return f'<a class="fn-ref" href="#{note_id}"><sup>{number}</sup></a>'
        used.add(number)
        return f'<a class="fn-ref" id="fnref-{prefix}-{number}" href="#{note_id}"><sup>{number}</sup></a>'

    return re.sub(r"(?<=[A-Za-z)])(\d{1,2})(?=[,.;:\s]|$)", repl, html)


def sentence_open(text):
    return bool(text) and text.rstrip()[-1] not in ".!?"


def leading_marker(stripped):
    if stripped[:1] in {"\uf09f", "•", "\u2022"}:
        return "bullet", "•", stripped[1:].lstrip()
    match = re.match(r"^\(([a-z]{1,5})\)\s+(\S.*)$", stripped)
    if match:
        label = match.group(1)
        if label in ROMAN_MARKS:
            return "roman", f"({label})", match.group(2)
        if len(label) == 1:
            return "alpha", f"({label})", match.group(2)
        return None, None, stripped
    match = re.match(r"^([a-z])\)\s+(\S.*)$", stripped)
    if match:
        return "alpha", f"{match.group(1)})", match.group(2)
    return None, None, stripped


def nest_attr(item):
    nest = item.get("nest")
    if not nest:
        return ""
    attrs = f' data-nest="{nest["kind"]}"'
    if nest["kind"] == "clause" and nest.get("depth"):
        attrs += f' data-nest-depth="{nest["depth"]}"'
    return attrs


def marked_paragraph(ident, item, mark, prose, heading=False, inline=None):
    classes = ["policy-clause"]
    if heading:
        classes.append("policy-h")
    attrs = f' class="{" ".join(classes)}" data-mark="{item["kind"]}"'
    if item["kind"] == "clause" and item.get("depth"):
        attrs += f' data-depth="{item["depth"]}"'
    attrs += nest_attr(item)
    body = inline(prose) if inline else mark_modals(esc(prose))
    return (
        f"<p{ident}{attrs}>"
        f'<span class="clause-no">{esc(mark)}</span>'
        f'<span class="clause-body">{body}</span>'
        f"</p>"
    )


def follow_paragraph(text, item, inline):
    attrs = f' class="policy-prose policy-follow" data-follow="{item["kind"]}"'
    if item["kind"] == "clause" and item.get("depth"):
        attrs += f' data-depth="{item["depth"]}"'
    attrs += nest_attr(item)
    return f"<p{attrs}>{inline(text)}</p>"


def push_marker(stack, kind, depth, prose, heading):
    rank = depth if kind == "clause" else MARKER_RANK[kind]
    nest = None
    previous = None
    if kind == "bullet" and stack and stack[-1]["kind"] == "bullet" and stack[-1].get("nest"):
        previous = stack.pop()
        nest = previous["nest"]
    elif kind == "bullet" and stack and stack[-1]["kind"] in {"alpha", "roman", "clause"}:
        nest = {"kind": stack[-1]["kind"], "depth": stack[-1]["depth"]}
    else:
        if stack and stack[-1]["kind"] == kind and stack[-1]["depth"] == depth and not stack[-1].get("nest"):
            previous = stack[-1]
        while stack and stack[-1]["rank"] >= rank:
            stack.pop()
    plain = prose.rstrip(".;:")
    short = heading or (len(plain.split()) <= 18 and "." not in plain)
    run = previous["run"] + 1 if previous else 1
    stack.append({
        "kind": kind,
        "depth": depth,
        "rank": rank,
        "run": run,
        "short": short,
        "heading": heading,
        "open": sentence_open(prose),
        "nest": nest,
    })


def stays_with_item(item):
    if item["open"] or item["heading"]:
        return True
    if item["kind"] in {"alpha", "roman"} and item["run"] >= 2:
        return False
    if item["short"] and item["run"] >= 2:
        return False
    return True


def policy_paragraphs(blocks, prefix="fn"):
    notes = {}
    source_blocks = []
    external_refs = set()
    join_after_note = False
    for block in blocks:
        if isinstance(block, str):
            stripped_block = block.strip()
            parsed = parse_footnote(stripped_block)
            if parsed:
                notes[parsed[0]] = parsed[1]
                join_after_note = True
                continue
            if stripped_block.rstrip("0123456789") == "An Example Organisation Chart for Departmental IT Security Management":
                digit = stripped_block[len("An Example Organisation Chart for Departmental IT Security Management"):]
                if digit.isdigit():
                    external_refs.add(digit)
                join_after_note = False
                continue
        if (
            join_after_note
            and source_blocks
            and isinstance(source_blocks[-1], str)
            and isinstance(block, str)
            and sentence_open(source_blocks[-1].strip())
            and block.strip()[:1].islower()
        ):
            source_blocks[-1] = source_blocks[-1].rstrip() + " " + block.strip()
            join_after_note = False
            continue
        join_after_note = False
        source_blocks.append(block)
    used = set(external_refs)

    def inline(text):
        return apply_fn_refs(mark_modals(esc(text)), notes, prefix, used)

    parts = []
    stack = []
    follow = None
    for block in source_blocks:
        if isinstance(block, list) and block and block[0] == "note":
            parts.append(f'<p class="policy-note">{inline(block[1])}</p>')
            continue
        text = block if isinstance(block, str) else ""
        stripped = text.strip()
        kind, mark, prose = leading_marker(stripped)
        if kind:
            push_marker(stack, kind, None, prose, is_heading(text, prose))
            follow = None
            parts.append(marked_paragraph("", stack[-1], mark, prose, is_heading(text, prose), inline))
            continue
        clause_body = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", stripped)
        heading = is_heading(text, clause_body)
        match = re.match(r"^(\d+(?:\.\d+)*)(\.?)\s+(\S.*)$", stripped)
        ident = ""
        if match and (heading or len(text) <= 180):
            ident = f' id="c-{match.group(1).replace(".", "-")}"'
        if match and not heading:
            number = f"{match.group(1)}{match.group(2)}"
            depth = min(len(match.group(1).split(".")), 5)
            push_marker(stack, "clause", depth, match.group(3), False)
            follow = None
            parts.append(marked_paragraph(ident, stack[-1], number, match.group(3), inline=inline))
            continue
        if heading:
            stack.clear()
            follow = None
            parts.append(f'<p{ident} class="policy-h">{inline(text)}</p>')
            continue
        if follow is not None:
            item = follow
        elif stack and stays_with_item(stack[-1]):
            item = stack[-1]
            follow = item
        elif stack:
            stack.pop()
            item = stack[-1] if stack else None
            follow = item if item else False
        else:
            item = None
        if item:
            parts.append(follow_paragraph(text, item, inline))
        else:
            parts.append(f'<p class="policy-prose">{inline(text)}</p>')
    if notes:
        rendered = []
        for number in sorted(notes, key=int):
            note_id = f"fn-{prefix}-{number}"
            mark = f"<sup>{esc(number)}</sup>"
            if number in used:
                mark = f'<a class="fn-mark" href="#fnref-{prefix}-{number}">{mark}</a>'
            rendered.append(
                f'<p class="policy-footnote" id="{note_id}">'
                f'{mark}<span class="fn-body">{mark_modals(esc(notes[number]))}</span></p>'
            )
        parts.append(f'<div class="footnotes">{"".join(rendered)}</div>')
    return "\n".join(parts)


def block_text(block):
    if isinstance(block, str):
        return block
    if isinstance(block, list):
        if block and block[0] == "note":
            return ""
        return " ".join(block_text(part) for part in block)
    return ""


def write_source_index(sections):
    rows = []
    for section in sections:
        for doc, key in (("S17", "s17"), ("G3", "g3")):
            blocks = section[key]
            if section["id"] == "02" and key == "g3":
                blocks = [block for block in blocks if not (isinstance(block, list) and block and block[0] == "note")]
            text = " ".join(part for part in (block_text(block) for block in blocks) if part)
            rows.append({
                "doc": doc,
                "id": section["id"],
                "number": str(int(section["number"])),
                "title": section["title"],
                "href": f"core4/{key}/s{section['id']}.html",
                "text": text,
            })
    payload = json_for_script(rows)
    equivalents = json_for_script(EQUIVALENTS)
    path = HUB / "assets" / "js" / "source-search-data.js"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "window.SOURCE_INDEX = " + payload + ";\n"
        "window.SOURCE_EQUIVALENTS = " + equivalents + ";\n",
        encoding="utf-8",
    )


def write_glossary_terms_data():
    """Emit official glossary terms for client-side highlighting on hub pages."""
    terms = []
    for term, definition in load_infosec_glossary():
        terms.append({
            "term": term,
            "definition": definition,
            "id": glossary_term_id(term),
        })
    path = HUB / "assets" / "js" / "glossary-terms-data.js"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "window.GLOSSARY_TERMS = " + json_for_script(terms) + ";\n",
        encoding="utf-8",
    )


def write_hub_search_index(sections):
    """Emit categorised hub pages and source sections for the search modal."""
    rows = []

    def add(category, badge, badge_kind, title, href_path, text, meta=""):
        rows.append({
            "category": category,
            "badge": badge,
            "badgeKind": badge_kind,
            "title": title,
            "href": href_path,
            "meta": meta,
            "text": " ".join(str(text or "").split()),
        })

    for page in PAGES:
        card_text = " ".join(
            " ".join([
                card.get("title", ""),
                card.get("one_glance_answer", ""),
                card.get("implementation_guidance", ""),
            ])
            for card in page.get("cards", [])
        )
        add(
            "Decision aids",
            "Aid",
            "aid",
            page["title"],
            page["file"],
            f"{page.get('intro', '')} {card_text}",
            page.get("source", ""),
        )

    for quiz in QUIZZES:
        q_text = " ".join(
            " ".join([q.get("prompt", ""), q.get("rationale", "")] + list(q.get("choices", [])))
            for q in quiz.get("questions", [])
        )
        add(
            "Quizzes",
            "Quiz",
            "quiz",
            quiz["title"],
            quiz["file"],
            f"{quiz.get('intro', '')} {q_text}",
            quiz.get("source", ""),
        )

    for pack in PACKS:
        items_text = " ".join(
            " ".join([item.get("question", ""), item.get("answer", "")])
            for item in pack.get("items", [])
        )
        add(
            "Q&A",
            "Q&A",
            "qa",
            pack["title"],
            pack["file"],
            items_text,
            pack.get("source", ""),
        )

    for section in sections:
        for doc, key in (("S17", "s17"), ("G3", "g3")):
            blocks = section[key]
            if section["id"] == "02" and key == "g3":
                blocks = [block for block in blocks if not (isinstance(block, list) and block and block[0] == "note")]
            text = " ".join(part for part in (block_text(block) for block in blocks) if part)
            add(
                "Source",
                doc,
                "source",
                f"{doc} §{int(section['number'])} — {section['title']}",
                f"core4/{key}/s{section['id']}.html",
                text,
                f"{doc} §{int(section['number'])}",
            )

    for term, definition in load_infosec_glossary():
        add(
            "Glossary",
            "Glossary",
            "glossary",
            term,
            f"glossary.html#{glossary_term_id(term)}",
            definition,
            "Official InfoSec",
        )
    for term, meaning in hub_glossary_terms():
        add(
            "Glossary",
            "Glossary",
            "glossary",
            term,
            f"glossary.html#{glossary_term_id(term)}",
            meaning,
            "This hub",
        )

    for cheat in CHEATS:
        block_bits = []
        for block in cheat.get("blocks", []):
            if not isinstance(block, dict):
                continue
            if block.get("text"):
                block_bits.append(str(block["text"]))
            for row in block.get("rows", []) or []:
                block_bits.extend(str(cell) for cell in row)
            for step in block.get("steps", []) or []:
                if isinstance(step, (list, tuple)):
                    block_bits.extend(str(part) for part in step)
                elif isinstance(step, dict):
                    block_bits.append(str(step.get("text", "")))
        add(
            "Cheat sheets",
            "Sheet",
            "sheet",
            cheat["title"],
            cheat["file"],
            f"{cheat.get('source', '')} {' '.join(block_bits)}",
            cheat.get("source", ""),
        )

    for walk in WALKS:
        step_text = " ".join(
            " ".join([step.get("title", ""), step.get("text", "")])
            for step in walk.get("steps", [])
        )
        add(
            "Walkthroughs",
            "Walk",
            "walk",
            walk["title"],
            walk["file"],
            step_text,
            walk.get("source", ""),
        )

    for stage in STAGES:
        add(
            "Paths",
            "Path",
            "path",
            f"{stage['code']} · {stage['name']}",
            stage["file"],
            f"{stage.get('blurb', '')} {stage.get('themes', '')}",
            stage.get("source", "System lifecycle"),
        )

    for rel, title, text in (
        ("index.html", "Home", "HKSARG IT Security Learning Hub entry point"),
        ("spine.html", "Policy and System Lifecycle Overview", "CIA policy stack SDLC overview"),
        ("start/new-joiners.html", "New joiners", "Fundamentals path for new joiners"),
        ("start/current-staff.html", "Current staff", "Filter by role system lifecycle and need"),
        ("core1/index.html", "Decision aids", "One-glance answers with a policy cite"),
        ("core2/index.html", "Quizzes", "Self-checks with a rationale for each answer"),
        ("core3/index.html", "Q&A", "Enquiry-style answers"),
        ("core4/index.html", "Source lookup", "S17 and G3 section wording"),
        ("app-c-matrix.html", "Appendix C matrix", "Tier 2 and Tier 3 extra controls"),
        ("glossary.html", "Glossary", "Official InfoSec and hub terms A to Z"),
        ("about.html", "About this hub", "Versions accessibility and purpose"),
        ("governance.html", "Governance and updates", "How the hub is maintained"),
        ("path/foundation.html", "Fundamentals path", "New joiner fundamentals checklist"),
        ("path/apply.html", "Apply and close gaps", "Gap closing path"),
        ("cheatsheets/index.html", "Cheat sheets", "Short reference sheets"),
        ("walkthroughs/index.html", "Walkthroughs", "Role and SDLC walkthroughs"),
    ):
        add("Hub pages", "Page", "page", title, rel, text, "")

    for role in ROLES:
        add(
            "Paths",
            "Path",
            "path",
            role["title"],
            f"path/role-{role['n']}.html",
            role.get("walk", "") or role.get("title", ""),
            f"Role {role['n']}",
        )

    path = HUB / "assets" / "js" / "hub-search-data.js"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "window.HUB_SEARCH_INDEX = " + json_for_script(rows) + ";\n"
        "window.HUB_SEARCH_EQUIVALENTS = " + json_for_script(EQUIVALENTS) + ";\n",
        encoding="utf-8",
    )


def sections_main():
    payload = json.loads((Path(__file__).resolve().parent / "policy_sections.json").read_text(encoding="utf-8"))
    notice = (
        "Sections 1 to 20 below are the text of the Baseline IT Security Policy [S17] version 8.2, April 2025, "
        "and the IT Security Guidelines [G3] version 10.2, April 2025, issued by the Digital Policy Office. "
        "This copy is not for sale. Appendices remain in the official PDFs."
    )
    permission = (
        "copied/distributed with the permission of the Government of the Hong Kong Special Administrative Region "
        "of the People's Republic of China. All rights reserved."
    )
    parts = [f"""
<h1 id="top">Sections, §1 to §20</h1>
<p class="lede">Original wording from S17 and G3, so the strength of each line stays visible. <span class="modal modal-shall">Shall</span> is mandatory and must be done. <span class="modal modal-should">Should</span> is best practice — implement whenever possible. <span class="modal modal-may">May</span> is a desirable best practice. S17 and G3 §4.2 use these words in that sense.</p>
<p class="copy-notice">{esc(notice)}</p>
<p class="copy-notice">{esc(permission)}</p>
"""]
    for item in payload:
        g3_blocks = item["g3"]
        if item["id"] == "02":
            g3_blocks = [block for block in g3_blocks if not (isinstance(block, list) and block and block[0] == "note")]
        parts.append(f"""
<article id="s{esc(item["id"])}">
  <h2>§{esc(item["number"])} {esc(item["title"])}</h2>
  {section_figure(item["id"], [f"s17-{item['id']}", f"g3-{item['id']}"] if item["id"] == "05" else None)}
  <section class="policy-src policy-s17" aria-label="S17 section {esc(item["number"])}">
    <h3>Baseline IT Security Policy [S17] v8.2</h3>
    <div class="policy-text">{policy_paragraphs(item["s17"], f"s17-{item['id']}")}</div>
  </section>
  <section class="policy-src policy-g3" aria-label="G3 section {esc(item["number"])}">
    <h3>IT Security Guidelines [G3] v10.2</h3>
    <div class="policy-text">{policy_paragraphs(g3_blocks, f"g3-{item['id']}")}</div>
  </section>
</article>""")
    parts.append(f'<p class="copy-notice">{esc(notice)}</p>\n<p class="copy-notice">{esc(permission)}</p>')
    return "\n".join(parts)


def gov_main():
    return gov_page(href)


def about_main():
    return about_page(esc, VERSION, DISCLAIMER)


def clause_index(blocks):
    found = []
    seen = set()
    for block in blocks:
        if not isinstance(block, str) or parse_footnote(block.strip()):
            continue
        match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(\S.*)$", block.strip())
        if not match:
            continue
        ident, rest = match.group(1), match.group(2)
        if len(block) > 180 and not (len(block) <= 160 and "." not in rest and ":" not in rest):
            continue
        if ident in seen:
            continue
        seen.add(ident)
        label = rest if len(rest) <= 90 else rest[:87] + "…"
        found.append((f"c-{ident.replace('.', '-')}", ident, label))
    return found


def curated_links(path):
    found = []
    seen = set()
    for page, card in all_cards():
        for link, _label in source_links(card["policy_cite"]):
            if link.split("#")[0] == path and card["id"] not in seen:
                seen.add(card["id"])
                found.append((f"{page['file']}#{card['id']}", card["title"]))
    number = re.search(r"/s(\d+)\.html$", path)
    if number:
        pattern = re.compile(rf"§0*{int(number.group(1))}(?!\d)")
        for quiz in QUIZZES:
            if pattern.search(quiz["source"]):
                found.append((quiz["file"], quiz["title"]))
    if path.endswith("appendix-c.html"):
        for quiz in QUIZZES:
            if "Appendix C" in quiz["source"] or "App C" in quiz["source"]:
                found.append((quiz["file"], quiz["title"]))
    return found


def appendix_rows():
    rows = []
    for row in MATRIX:
        rows.append(
            f'<tr id="area-{esc(row["section"])}">'
            f'<th scope="row">{esc(row["area"])}</th>'
            f'<td>{esc(row["t2"])}</td><td>{esc(row["t3"])}</td></tr>'
        )
    return (
        '<table class="matrix"><caption>Appendix C learning map. Tier 3 inherits every Tier 2 control.</caption>'
        "<thead><tr><th>Area</th><th>Tier 2 (also required for Tier 3)</th><th>Tier 3 only</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def collect_ids():
    ids = []
    for day in FOUNDATION["days"]:
        ids.extend(item["id"] for item in day["items"])
    for role in ROLES:
        for cluster in role["clusters"]:
            ids.extend(item["id"] for item in cluster["items"])
    for day in APPLY:
        ids.extend(item["id"] for item in day["items"])
    return ids


def soften_obj(value):
    if isinstance(value, str):
        return soften(value)
    if isinstance(value, list):
        return [soften_obj(item) for item in value]
    if isinstance(value, dict):
        return {key: soften_obj(item) for key, item in value.items()}
    return value


def paths_payload():
    return {
        "version": "0.1-MVP",
        "alignedTo": {"s17": "8.2", "g3": "10.2", "lastReviewed": "2026-10-26", "assumed": True},
        "foundation": FOUNDATION,
        "roles": ROLES,
        "apply": APPLY,
    }


def main():
    pages = []
    sections = json.loads((Path(__file__).resolve().parent / "policy_sections.json").read_text(encoding="utf-8"))
    write_source_index(sections)
    write_glossary_terms_data()
    write_hub_search_index(sections)
    # Hash after generated *.js data files are on disk so ?v= matches final bytes.
    global BUILD_ID
    _ASSET_HASH.clear()
    BUILD_ID = compute_build_id()
    write_cache_control_files(BUILD_ID)
    copy_notice = (
        "The section text is from the named official document, April 2025, issued by the Digital Policy Office. "
        "This copy is not for sale."
    )
    permission = (
        "copied/distributed with the permission of the Government of the Hong Kong Special Administrative Region "
        "of the People's Republic of China. All rights reserved."
    )

    def emit(rel, title, page_id, crumbs, source, builder, extra=None):
        global CURRENT
        CURRENT = rel
        main_html = builder() if callable(builder) else builder
        write_page(rel, title, page_id, crumbs, source, main_html, extra)
        pages.append(rel)

    home = [("index.html", "Home")]
    emit("index.html", "Home", "P-HOME", home, "Hub map §2", home_main)
    emit("spine.html", "Policy and System Lifecycle Overview", "P-SPINE", home + [("spine.html", "Policy and System Lifecycle Overview")], "Hub map §3", lambda: spine_page(href, esc))
    emit(
        "start/new-joiners.html",
        "New joiners",
        "P-START-NEW",
        home + [("start/new-joiners.html", "New joiners")],
        "Hub map §6.1",
        lambda: new_joiners_page(href, esc, legend_html(), read_guide()),
    )
    emit(
        "start/current-staff.html",
        "Current staff",
        "P-START-CURRENT",
        home + [("start/current-staff.html", "Current staff")],
        "Hub map §6.2",
        lambda: current_staff_page(
            href,
            esc,
            legend_html(),
            read_guide(),
            json_for_script(catalogue()),
        ),
    )
    emit(
        "glossary.html",
        "Glossary",
        "P-GLOSSARY",
        home + [("glossary.html", "Glossary")],
        "S17 §4 · G3 §4 · Hub map",
        lambda: glossary_page(href, esc),
    )
    emit("about.html", "About", "P-ABOUT", home + [("about.html", "About")], "S17 v8.2; G3 v10.2", about_main)
    emit("governance.html", "Governance", "P-GOV", home + [("governance.html", "Governance")], "Hub map §7", gov_main)

    core1 = home + [("core1/index.html", "Aids")]
    emit("core1/index.html", "Decision aids", "P-CORE1-INDEX", core1, "Hub map §5.1", lambda: core1_index(href, esc))
    emit("core1/by-need.html", "I need to…", "P-DEC-NEED-INDEX", core1 + [("core1/by-need.html", "By need")], "Hub map §6.2", lambda: need_index(href, esc))
    for page in PAGES:
        emit(
            page["file"],
            page["title"],
            page["id"],
            core1 + [(page["file"], page["title"])],
            page["source"],
            lambda page=page: decision_page(href, esc, page, legend_html(), read_guide()),
        )

    core2 = home + [("core2/index.html", "Quizzes")]
    emit("core2/index.html", "Quizzes", "P-CORE2-INDEX", core2, "Hub map §5.2", quiz_index)
    for quiz in QUIZZES:
        emit(
            quiz["file"],
            quiz["title"],
            quiz["id"],
            core2 + [(quiz["file"], quiz["title"])],
            quiz["source"],
            lambda quiz=quiz: quiz_page(quiz),
            extra=["assets/js/quiz.js"],
        )

    core3 = home + [("core3/index.html", "Q&A")]
    emit("core3/index.html", "Enquiry Q&A", "P-CORE3-INDEX", core3, "Hub map §5.3", lambda: core3_index(href, esc))
    for pack in PACKS:
        emit(
            pack["file"],
            pack["title"],
            pack["id"],
            core3 + [(pack["file"], pack["title"])],
            pack["source"],
            lambda pack=pack: qa_page(href, esc, pack),
        )

    core4 = home + [("core4/index.html", "Source")]
    search_scripts = ["assets/js/source-search-data.js", "assets/js/source-search.js"]
    emit(
        "core4/index.html",
        "Source lookup",
        "P-CORE4-INDEX",
        core4,
        "S17 v8.2; G3 v10.2",
        lambda: core4_index(href, esc),
        extra=search_scripts,
    )
    emit(
        "core4/s17/index.html",
        "S17 contents",
        "P-SRC-S17-TOC",
        core4 + [("core4/s17/index.html", "S17")],
        "S17 v8.2",
        lambda: toc_page(href, esc, "s17", "Baseline IT Security Policy [S17]", "v8.2", sections),
        extra=search_scripts,
    )
    emit(
        "core4/g3/index.html",
        "G3 contents",
        "P-SRC-G3-TOC",
        core4 + [("core4/g3/index.html", "G3")],
        "G3 v10.2",
        lambda: toc_page(href, esc, "g3", "IT Security Guidelines [G3]", "v10.2", sections),
        extra=search_scripts,
    )
    for section in sections:
        for doc_code, key, doc_title, version, page_prefix in (
            ("s17", "s17", "Baseline IT Security Policy [S17]", "v8.2", "P-SRC-S17"),
            ("g3", "g3", "IT Security Guidelines [G3]", "v10.2", "P-SRC-G3"),
        ):
            rel = f"core4/{doc_code}/s{section['id']}.html"
            blocks = section[key]
            if section["id"] == "02" and key == "g3":
                blocks = [block for block in blocks if not (isinstance(block, list) and block and block[0] == "note")]
            emit(
                rel,
                f"{doc_code.upper()} §{int(section['number'])} {section['title']}",
                f"{page_prefix}-{section['id']}",
                core4 + [(f"core4/{doc_code}/index.html", doc_code.upper()), (rel, f"§{int(section['number'])}")],
                f"{doc_code.upper()} v{version[1:]} §{int(section['number'])}",
                lambda rel=rel, doc_code=doc_code, doc_title=doc_title, version=version, section=section, blocks=blocks: source_page(
                    href,
                    esc,
                    doc_code,
                    doc_title,
                    version,
                    section,
                    policy_paragraphs(blocks, f"{doc_code}-{section['id']}"),
                    section_figure(section["id"], [f"{doc_code}-{section['id']}"] if section["id"] == "05" else None),
                    clause_index(blocks),
                    curated_links(rel),
                    copy_notice,
                    permission,
                ),
            )
    emit(
        "core4/g3/appendix-c.html",
        "G3 Appendix C",
        "P-SRC-G3-APPC",
        core4 + [("core4/g3/index.html", "G3"), ("core4/g3/appendix-c.html", "Appendix C")],
        "G3 v10.2 Appendix C",
        lambda: appendix_page(href, esc, appendix_rows(), curated_links("core4/g3/appendix-c.html")),
    )

    emit(
        "path/foundation.html",
        "Fundamentals path",
        "P-PATH-FND",
        home + [("start/new-joiners.html", "New joiners"), ("path/foundation.html", "Fundamentals")],
        "S17/G3 §1–§11, §14, §18–§20",
        foundation_main,
    )
    for role in ROLES:
        rel = f"path/role-{role['n']}.html"
        emit(
            rel,
            role["title"],
            f"P-PATH-R{role['n']}",
            home + [("start/current-staff.html", "Current staff"), (rel, role["title"])],
            role["anchor"],
            lambda role=role: role_main(role),
        )
    for stage in STAGES:
        emit(
            stage["file"],
            stage["name"],
            stage["id"],
            home + [("start/current-staff.html", "Current staff"), (stage["file"], stage["name"])],
            stage["source"],
            lambda stage=stage: sdlc_page(
                href,
                esc,
                stage,
                f'<ul class="items">{"".join(item_html(item) for item in stage["items"])}</ul>',
                legend_html(),
                read_guide(),
            ),
        )
    emit(
        "path/apply.html",
        "Apply and close gaps",
        "P-PATH-APPLY",
        home + [("start/current-staff.html", "Current staff"), ("path/apply.html", "Apply")],
        "G3 §4 · G3 §7 · Appendix C",
        apply_main,
    )

    emit("app-c-matrix.html", "App C matrix", "P-APPC", home + [("app-c-matrix.html", "App C")], "G3 Appendix C", matrix_main)
    emit("gap-template.html", "Gap template", "P-GAP", home + [("gap-template.html", "Gap template")], "Hub map §3.6", gap_main)

    cheats = home + [("cheatsheets/index.html", "Cheat sheets")]
    emit("cheatsheets/index.html", "Cheat sheets", "P-CHEAT-INDEX", cheats, "S17/G3 §4 · §6 · §11 · §14 · §18", cheat_index)
    for cheat in CHEATS:
        emit(cheat["file"], cheat["title"], cheat["id"], cheats + [(cheat["file"], cheat["title"])], cheat["source"], lambda cheat=cheat: cheat_page(cheat))
    walks = home + [("walkthroughs/index.html", "Walkthroughs")]
    emit("walkthroughs/index.html", "Walkthroughs", "P-WALK-INDEX", walks, "Hub map §3.6", walk_index)
    for walk in WALKS:
        emit(walk["file"], walk["title"], walk["id"], walks + [(walk["file"], walk["title"])], walk["source"], lambda walk=walk: walk_page(walk))

    data_dir = HUB / "assets" / "data"
    qa_dir = data_dir / "qa"
    quiz_dir = data_dir / "quizzes"
    qa_dir.mkdir(parents=True, exist_ok=True)
    quiz_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "infosec-glossary.csv", data_dir / "infosec-glossary.csv")
    (data_dir / "paths.json").write_text(json.dumps(soften_obj(paths_payload()), ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "quizzes.json").write_text(json.dumps(QUIZZES, ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "decision-aids.json").write_text(
        json.dumps([{"page": page["id"], "file": page["file"], "cards": page["cards"]} for page in PAGES], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for pack in PACKS:
        (qa_dir / f"{pack['id'].lower()}.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    for quiz in QUIZZES:
        (quiz_dir / f"{quiz['id'].lower()}.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    search_rows = [{"id": page_id, "title": title, "href": rel} for rel, title, page_id, *_rest in []]
    # Filled from pages after titles are known via the written list below.
    search_rows = []
    for rel in pages:
        text = (HUB / rel).read_text(encoding="utf-8")
        title_match = re.search(r"<title>(.*?) ·", text)
        id_match = re.search(r'data-page-id="([^"]+)"', text)
        search_rows.append({
            "href": rel,
            "title": title_match.group(1) if title_match else rel,
            "id": id_match.group(1) if id_match else "",
        })
    (data_dir / "search-index.json").write_text(json.dumps(search_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    written = set(pages)
    for path in HUB.rglob("*.html"):
        rel = path.relative_to(HUB).as_posix()
        if rel not in written:
            path.unlink()

    # Workers not_found_handling uses 404.html; write after orphan cleanup.
    (HUB / "404.html").write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Not found</title>
</head>
<body>
  <p>This address is not a page.</p>
  <p><a href="/">Home</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )

    found = collect_ids()
    dupes = sorted({item for item in found if found.count(item) > 1})
    if dupes:
        raise SystemExit("Duplicate checklist IDs: " + ", ".join(dupes))
    card_ids = [card["id"] for _page, card in all_cards()]
    if len(card_ids) != len(set(card_ids)):
        raise SystemExit("Duplicate decision-aid IDs")
    for quiz in QUIZZES:
        minimum = 8 if quiz["id"] == "P-QUIZ-FND" else 6
        if len(quiz["questions"]) < minimum:
            raise SystemExit(f"{quiz['id']} has too few questions")
        for question in quiz["questions"]:
            if len(question["choices"]) != 4 or not 0 <= question["answerIndex"] <= 3:
                raise SystemExit(f"{question['id']} is not a four-choice question")
    for rel in pages:
        body = (HUB / rel).read_text(encoding="utf-8")
        if VERSION not in body or DISCLAIMER not in body or "data-page-id=" not in body:
            raise SystemExit(f"Banner, disclaimer, or page id missing on {rel}")
        if "cdn" in body.lower() or "fonts.googleapis" in body:
            raise SystemExit(f"External font or CDN in {rel}")
        for match in re.finditer(r'assets/(?:css|js)/[^"\']+\?v=([0-9a-f]+)', body):
            if len(match.group(1)) != 10:
                raise SystemExit(f"Non-hash asset version on {rel}: ?v={match.group(1)}")
    tracked = ["assets/css/hub.css", *CORE_SCRIPTS, "assets/js/quiz.js"]
    versions = ", ".join(f"{Path(rel).name}={asset_version(rel)}" for rel in tracked)
    if not (HUB / "build-id.txt").is_file() or not (HUB / "_headers").is_file():
        raise SystemExit("build-id.txt or _headers missing after render")
    if (HUB / "build-id.txt").read_text(encoding="utf-8").strip() != BUILD_ID:
        raise SystemExit("build-id.txt does not match BUILD_ID")
    sample = (HUB / "index.html").read_text(encoding="utf-8")
    if f'data-hub-build="{BUILD_ID}"' not in sample:
        raise SystemExit("index.html missing data-hub-build stamp")
    print(f"Wrote {len(pages)} pages.")
    print(f"Build id: {BUILD_ID}")
    print(f"Asset versions: {versions}")


if __name__ == "__main__":
    main()
