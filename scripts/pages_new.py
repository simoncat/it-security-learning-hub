"""Page bodies and side navigation for the four-core hub."""

import re

from content_decisions import NEEDS, PAGES, all_cards, cards_sorted
from content_qa import PACKS
from content_quizzes import QUIZZES
from content_sdlc import STAGES
from content_static import CHEATS, WALKS

ROLES = [
    ("1", "Elevated end user"),
    ("2", "System / LAN administrator"),
    ("3", "Application developer"),
    ("4", "IT security administrator / unit"),
    ("5", "Management support"),
]

SDLC = [
    ("01", "Project initiation"),
    ("02", "Design"),
    ("03", "Procurement"),
    ("04", "Build/Implementation"),
    ("05", "Testing"),
    ("06", "Go-live"),
    ("07", "Operations"),
    ("08", "Change"),
    ("09", "Decommissioning"),
]

APPC_SECTIONS = {"5", "7", "9", "11", "14", "16", "19", "20"}


def source_links(cites):
    """One source link for each policy cite, in the same order."""
    links = []
    for cite in cites:
        if cite == "G3 Appendix C":
            links.append(("core4/g3/appendix-c.html", cite))
            continue
        match = re.match(r"^(S17|G3) §(\d+)$", cite)
        if not match:
            continue
        doc = "s17" if match.group(1) == "S17" else "g3"
        links.append((f"core4/{doc}/s{int(match.group(2)):02d}.html", cite))
    return links


def side_groups(rel):
    if rel.startswith("core1/"):
        groups = {"Basics": [], "Controls by theme": [], "By need": []}
        groups["By need"].append(("core1/by-need.html", "I need to…"))
        for page in PAGES:
            groups.setdefault(page["group"], []).append((page["file"], page["title"]))
        ordered = []
        for name in ("Basics", "Controls by theme", "By need"):
            ordered.append((name, groups[name]))
        return ordered
    if rel.startswith("core2/"):
        links = [("core2/index.html", "All quizzes")]
        links += [(quiz["file"], quiz["title"]) for quiz in QUIZZES]
        return [("Quizzes", links)]
    if rel.startswith("core3/"):
        links = [("core3/index.html", "All enquiry packs")]
        links += [(pack["file"], pack["title"]) for pack in PACKS]
        return [("Enquiry packs", links)]
    if rel.startswith("core4/"):
        return [("Source", [
            ("core4/index.html", "Source home"),
            ("core4/s17/index.html", "S17 contents"),
            ("core4/g3/index.html", "G3 contents"),
            ("core4/g3/appendix-c.html", "Appendix C"),
        ])]
    if rel.startswith("path/") or rel.startswith("start/"):
        roles = [(f"path/role-{n}.html", label) for n, label in ROLES]
        stages = [(f"path/sdlc-{code}-{slug(name)}", f"{code} {name}") for code, name in SDLC]
        # files are explicit on STAGES
        stages = [(stage["file"], f"{stage['code']} {stage['name']}") for stage in STAGES]
        return [
            ("Audiences", [
                ("start/new-joiners.html", "New joiners"),
                ("start/current-staff.html", "Current staff"),
                ("path/foundation.html", "Fundamentals path"),
            ]),
            ("Roles", roles),
            ("SDLC stages", stages),
            ("Close gaps", [("path/apply.html", "Apply and close gaps")]),
        ]
    if rel == "spine.html":
        return [("On this page", [
            ("spine.html#layer-1", "Layer 1 · CIA"),
            ("spine.html#layer-2", "Layer 2 · Policy stack"),
            ("spine.html#layer-3", "Layer 3 · SDLC"),
        ])]
    return [("On this hub", [
        ("index.html", "Home"),
        ("spine.html", "Overview"),
        ("start/new-joiners.html", "New joiners"),
        ("start/current-staff.html", "Current staff"),
        ("core1/index.html", "Decision aids"),
        ("core2/index.html", "Quizzes"),
        ("core3/index.html", "Q&A"),
        ("core4/index.html", "Source"),
        ("app-c-matrix.html", "App C matrix"),
        ("gap-template.html", "Gap template"),
        ("cheatsheets/index.html", "Cheat sheets"),
        ("walkthroughs/index.html", "Walkthroughs"),
        ("governance.html", "Governance"),
    ])]


def slug(name):
    return name


def option_list(pairs, blank, selected=""):
    bits = [f'<option value="">{blank}</option>']
    for value, label in pairs:
        bits.append(f'<option value="{value}">{label}</option>')
    return "".join(bits)


def launcher_form(h, include_tier=True):
    role_opts = option_list(ROLES, "Any role")
    sdlc_opts = option_list(SDLC, "Any stage")
    need_opts = option_list(NEEDS, "Any need")
    tier = ""
    if include_tier:
        tier = """
        <label>Tier
          <select name="tier">
            <option value="">Any tier</option>
            <option value="1">Tier 1</option>
            <option value="2">Tier 2</option>
            <option value="3">Tier 3</option>
          </select>
        </label>
        <label>Modality
          <select name="mod">
            <option value="">Any modality</option>
            <option value="shall">Shall</option>
            <option value="should">Should</option>
            <option value="may">May</option>
          </select>
        </label>"""
    return f"""
<form class="launcher" id="staff-launcher" action="{h("start/current-staff.html")}" method="get">
  <div class="filter-grid">
    <label>Role
      <select name="role">{role_opts}</select>
    </label>
    <label>SDLC stage
      <select name="sdlc">{sdlc_opts}</select>
    </label>
    <label>Need
      <select name="need">{need_opts}</select>
    </label>
    {tier}
  </div>
  <p><button class="btn btn-primary" type="submit">Show matches</button></p>
  <p class="fine">The filter stays in the page link. Nothing is sent to a server.</p>
</form>
"""


def catalogue():
    rows = []
    for page, card in all_cards():
        rows.append({
            "kind": "Decision aid",
            "title": card["title"],
            "detail": page["title"],
            "href": f"{page['file']}#{card['id']}",
            "roles": card["roles"],
            "sdlc": card["sdlc"],
            "needs": card["needs"],
            "tiers": card["tiers"],
            "mod": card["modality"],
            "appc": card["app_c_flag"],
        })
    for stage in STAGES:
        rows.append({
            "kind": "SDLC pack",
            "title": f"{stage['code']} {stage['name']}",
            "detail": stage["blurb"],
            "href": stage["file"],
            "roles": ["all"],
            "sdlc": [stage["code"]],
            "needs": {
                "01": ["tier", "design", "account"],
                "02": ["design", "crypto", "access"],
                "03": ["vendor", "procure"],
                "04": ["design", "privileged", "access"],
                "05": ["sra", "design"],
                "06": ["sra", "incident", "backup"],
                "07": ["patch", "backup", "access", "incident"],
                "08": ["change", "sra", "patch"],
                "09": ["retire", "classify", "vendor"],
            }.get(stage["code"], []),
            "tiers": ["1", "2", "3"],
            "mod": "",
            "appc": False,
        })
    for pack in PACKS:
        for item in pack["items"]:
            rows.append({
                "kind": "Enquiry Q&A",
                "title": item["question"],
                "detail": pack["title"],
                "href": f"{pack['file']}#{item['id']}",
                "roles": ["all"],
                "sdlc": ["all"],
                "needs": needs_for_pack(pack["id"]),
                "tiers": ["1", "2", "3"],
                "mod": item["modality"],
                "appc": "Appendix C" in " ".join(item["policy_cite"]),
            })
    for page, card in all_cards():
        for href, label in source_links(card["policy_cite"]):
            rows.append({
                "kind": "Source",
                "title": label,
                "detail": card["title"],
                "href": href,
                "roles": card["roles"],
                "sdlc": card["sdlc"],
                "needs": card["needs"],
                "tiers": card["tiers"],
                "mod": card["modality"],
                "appc": card["app_c_flag"],
            })
    return rows


def needs_for_pack(pack_id):
    return {
        "P-QA-ACCESS": ["access", "privileged", "mfa"],
        "P-QA-EMAIL": ["email", "classify"],
        "P-QA-DEVICE": ["device"],
        "P-QA-VENDOR": ["vendor", "procure"],
        "P-QA-PROJECT": ["design", "sra", "patch", "change"],
        "P-QA-IR": ["incident"],
        "P-QA-TIER": ["tier"],
        "P-QA-OTHER": [],
    }.get(pack_id, ["all"])


def home_page(h, esc, legend, guide):
    return f"""
<h1>IT Security Learning Hub</h1>
<p class="lede">A static aid for daily work with the Baseline IT Security Policy [S17] and the IT Security Guidelines [G3]. Pick a way in. Aids, quizzes, Q&amp;A, and source stay available from every page.</p>
<div class="audience-grid">
  <a class="audience audience-new" href="{h("start/new-joiners.html")}">
    <span class="audience-k">New joiners</span>
    <span class="audience-d">Fundamentals, then framework and accountability.</span>
  </a>
  <a class="audience audience-now" href="{h("start/current-staff.html")}">
    <span class="audience-k">Current staff</span>
    <span class="audience-d">Filter by role, system lifecycle, and the job in front of you.</span>
  </a>
  <a class="audience audience-spine" href="{h("spine.html")}">
    <span class="audience-k">Policy and System Lifecycle Overview</span>
    <span class="audience-d">CIA, then S17, G3, and departmental policy, then the system lifecycle.</span>
  </a>
</div>
<h2>Aids, quizzes, Q&amp;A, and source</h2>
<div class="tiles core-tiles">
  <a class="tile" href="{h("core1/index.html")}">Decision aids<span>One-glance answers with a policy cite</span></a>
  <a class="tile" href="{h("core2/index.html")}">Quizzes<span>Self-checks with a rationale for each answer</span></a>
  <a class="tile" href="{h("core3/index.html")}">Enquiry Q&amp;A<span>Sanitised departmental questions</span></a>
  <a class="tile" href="{h("core4/index.html")}">Source lookup<span>S17 and G3 section by section</span></a>
</div>
<h2>Open a current-staff task</h2>
{launcher_form(h, include_tier=False)}
<h2>Reading order</h2>
{guide}
<ol class="flow">
  <li class="flow-s17">S17<small>Mandatory minimum</small></li>
  <li class="flow-g3">G3<small>Implementation standard</small></li>
  <li class="flow-appc">App C<small>Tier 2 and Tier 3 only</small></li>
</ol>
{legend}
<p class="fine">Also: <a href="{h("app-c-matrix.html")}">Appendix C matrix</a> · <a href="{h("gap-template.html")}">Gap template</a> · <a href="{h("cheatsheets/index.html")}">Cheat sheets</a> · <a href="{h("walkthroughs/index.html")}">Walkthroughs</a></p>
"""


def new_joiners_page(h, esc, legend, guide):
    phases = [
        ("NJ0", "Overview", "High-level overview of IT Security, documents and System Lifecycle.", [
            ("spine.html", "Policy and System Lifecycle Overview"),
        ]),
        ("NJ1", "Government IT Security Documents", "Introduction of IT Security Documents in the Government.", [
            ("core1/cia.html", "Confidentiality, integrity, and availability"),
            ("cheatsheets/modality.html", "Shall, Should, May, and the reading flow"),
            ("core1/policy-stack.html", "IT Security Documents"),
            ("core2/quiz-foundation.html", "Quiz on Fundamental IT Security concepts in the Government"),
        ]),
        ("NJ2", "Organisation Structure and Accountability", "Organisation, who is accountable, and management responsibilities.", [
            ("core1/org-structure.html", "Organisation"),
            ("core1/accountability.html", "Accountability"),
            ("core1/management.html", "Management and risk"),
            ("core2/quiz-framework.html", "Framework quiz"),
        ]),
        ("NJ3", "Operational Safeguards and Incident Handling", "How to report, access basics, and awareness.", [
            ("core1/access-control.html", "Access"),
            ("core1/hr-security.html", "Persons and training"),
            ("core1/incident.html", "Incidents"),
            ("cheatsheets/incident.html", "Incident cheat sheet"),
        ]),
        ("NJ4", "Tiered Security Controls", "Tier 1, 2, and 3, and when Appendix C appears.", [
            ("core1/tier-appc.html", "Tier and App C"),
            ("app-c-matrix.html", "App C matrix (skim)"),
            ("core2/quiz-app-c.html", "App C quiz"),
        ]),
        ("NJ5", "Role", "Pick the role closest to the work you will do, then one walkthrough.", [
            (f"path/role-{n}.html", label) for n, label in ROLES
        ]),
        ("NJ6", "Consolidate", "A quiz battery, then a first look at the source text.", [
            ("core2/index.html", "All quizzes"),
            ("core4/index.html", "Source lookup"),
        ]),
        ("NJ7", "Apply (optional)", "Close a gap or finish one walkthrough.", [
            ("path/apply.html", "Apply"),
            ("gap-template.html", "Gap template"),
        ]),
    ]
    blocks = []
    for code, title, text, links in phases:
        lis = "".join(f'<li><a href="{h(target)}">{esc(label)}</a></li>' for target, label in links)
        blocks.append(f"""
<li class="item" data-modality="shall" data-flag="0">
  <div class="item-row">
    <input type="checkbox" id="tick-{code}" data-tick="{code}" aria-describedby="note-{code}">
    <div>
      <div class="item-meta"><span class="id-code">{code}</span></div>
      <label for="tick-{code}">{esc(title)}</label>
      <p class="item-note" id="note-{code}">{esc(text)}</p>
      <ul>{lis}</ul>
    </div>
  </div>
</li>""")
    return f"""
<h1>New joiners</h1>
<p class="lede">Start with an overview, then framework and accountability.</p>
{guide}
{legend}
<p class="storage-note">Optional self-progress. Stored only in this browser.</p>
<ol class="items phase-list">{''.join(blocks)}</ol>
<p><a href="{h("path/foundation.html")}">Open the fundamentals checklist</a></p>
"""


def current_staff_page(h, esc, legend, guide, payload):
    return f"""
<h1>Current staff</h1>
<p class="lede">Filter by role, system lifecycle, and the need in front of you. Matches are decision aids, the stage pack, enquiry answers, and the source section they cite.</p>
{guide}
{legend}
{launcher_form(h, include_tier=True)}
<div id="launcher-results" aria-live="polite">
  <h2>Matches</h2>
  <p class="fine">Choose a role, a stage, or a need. With nothing selected, the list shows a cross-section you can still print.</p>
</div>
<noscript>
  <p>Filtering uses a script in this page. The nine stage packs, aids, quizzes, Q&amp;A, and source are linked above and in the side list. No data is sent anywhere.</p>
</noscript>
<script type="application/json" id="launcher-data">{payload}</script>
"""


def spine_page(h, esc):
    cia = [
        ("Confidentiality", "Only authorised persons and information systems are allowed to know or gain access to the information stored or processed by information systems in any aspect.", "core1/cia.html#DEC-CIA-01"),
        ("Integrity", "Only authorised persons and information systems are allowed to make changes to the information stored or processed by information systems in any aspect.", "core1/cia.html#DEC-CIA-02"),
        ("Availability (service availability)", "Information System is accessible and usable upon demand by authorised persons and information systems.", "core1/cia.html#DEC-CIA-03"),
    ]
    cia_html = []
    for title, text, href in cia:
        cia_html.append(f"""
<details class="spine-node">
  <summary>{esc(title)}</summary>
  <p>{esc(text)}</p>
  <p><a href="{h(href)}">Open the decision aid</a></p>
</details>""")
    layer2 = f"""
<div class="spine-stack">
  <a href="{h("core1/policy-stack.html")}">S17<small>Mandatory minimum requirements</small></a>
  <span aria-hidden="true">↔</span>
  <a href="{h("core4/g3/index.html")}">G3<small>Implementation standards</small></a>
  <span aria-hidden="true">↔</span>
  <a href="{h("core1/policy-stack.html#DEC-STACK-02")}">Departmental policies and procedures<small>Apply after S17 and G3. May be stricter.</small></a>
</div>
<ul class="spine-pills">
  <li><a href="{h("core1/modality.html")}">Shall · must do</a></li>
  <li><a href="{h("core1/modality.html#DEC-MOD-02")}">Should · implement whenever possible</a></li>
  <li><a href="{h("core1/modality.html#DEC-MOD-03")}">May · desirable</a></li>
  <li><a href="{h("core1/tier-appc.html")}">Tier 1 · Tier 2 · Tier 3</a></li>
  <li><a href="{h("app-c-matrix.html")}"><span class="badge badge-appc">App C</span> Tier 2 and Tier 3 · Tier 3 inherits Tier 2</a></li>
</ul>
"""
    stages = []
    for stage in STAGES:
        stages.append(
            f'<li><a href="{h(stage["file"])}"><span>{esc(stage["code"])}</span>{esc(stage["name"])}</a></li>'
        )
    return f"""
<h1>Policy and System Lifecycle Overview</h1>
<p class="lede">Three layers. Layer 1 is why controls exist. Layer 2 is which document binds. Layer 3 is where you are in the life of a system. Each control opens a decision aid or a stage pack.</p>
<section id="layer-1" class="spine-layer" aria-labelledby="layer-1-title">
  <h2 id="layer-1-title">Layer 1 — Information System Security Objective (CIA)</h2>
  <div class="spine-nodes">{''.join(cia_html)}</div>
</section>
<section id="layer-2" class="spine-layer" aria-labelledby="layer-2-title">
  <h2 id="layer-2-title">Layer 2 — S17, G3, and departmental policy</h2>
  {layer2}
</section>
<section id="layer-3" class="spine-layer" aria-labelledby="layer-3-title">
  <h2 id="layer-3-title">Layer 3 — system lifecycle</h2>
  <ol class="spine-sdlc">{''.join(stages)}</ol>
</section>
"""


def role_phrase(codes):
    names = [dict(ROLES).get(code, code) for code in codes]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def expand_role_numbers(text):
    def repl(match):
        codes = re.findall(r"\d", match.group(1))
        return role_phrase(codes)

    return re.sub(r"\bRoles?\s+(\d+(?:,\s*\d+)*(?:,?\s+and\s+\d+)?)", repl, text, flags=re.I)


def role_line(card):
    """Roles line names persons. Stages and tiers stay on their own lines."""
    roles = "All roles" if card["roles"] == ["all"] else role_phrase(card["roles"])
    person = r"roles?|administrators?|management|developers?|elevated|owners?|staff|users?|people|others"
    text = expand_role_numbers(card["applicability_text"]).strip()
    kept = []
    for sentence in re.split(r"(?<=[.])\s+", text):
        if not re.search(rf"\b(?:{person})\b", sentence, flags=re.I):
            continue
        if re.match(r"(?i)see\b", sentence.strip()):
            continue
        cleaned = sentence
        cleaned = re.sub(r"(?i),?\s*\band\s+tiers?\b", "", cleaned)
        cleaned = re.sub(r"(?i)\b(?:all|every|any|on every|for every)\s+tiers?\b", "", cleaned)
        cleaned = re.sub(r"(?i)\btiers?\s+\d+(?:\s*,\s*\d+)*(?:\s*,?\s*and\s+\d+)?\b", "", cleaned)
        cleaned = re.sub(r"(?i)\btier\s+\d+\b", "", cleaned)
        cleaned = re.sub(r"(?i)\bthese roles apply\b", "", cleaned)
        cleaned = re.sub(r"(?i),?\s*\bany (?:life-cycle stage|system lifecycle)\b", "", cleaned)
        cleaned = re.sub(r"(?i)\s+\band\s+stages\b", "", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,.])", r"\1", cleaned)
        cleaned = cleaned.strip(" .,;")
        if cleaned and re.search(rf"\b(?:{person})\b", cleaned, flags=re.I):
            kept.append(cleaned)
    if not kept:
        return roles
    return ". ".join(kept)


def aid_applicability_html(esc, card):
    """Roles, stages, and tiers, each on its own line with a bold label."""
    who = role_line(card)
    stages = "Any stage" if card["sdlc"] == ["all"] else ", ".join(
        f"{code} {dict(SDLC).get(code, code)}" for code in card["sdlc"]
    )
    tiers = ", ".join(f"Tier {tier}" for tier in card["tiers"])
    rows = (("Roles", who), ("Stages", stages), ("Tiers", tiers))
    return "".join(f"<span><strong>{label}:</strong> {esc(value)}.</span>" for label, value in rows)


def aid_glance_html(esc, card):
    """Plain glance text, with an optional external {link} placeholder."""
    text = card["one_glance_answer"]
    link = card.get("glance_link")
    if not link:
        return esc(text)
    label, url = link
    anchor = f'<a href="{esc(url)}" rel="noopener noreferrer">{esc(label)}</a>'
    if "{link}" in text:
        parts = text.split("{link}")
        return esc(parts[0]) + anchor + esc("".join(parts[1:]))
    return esc(text) + " " + anchor


def aid_article(h, esc, card):
    links = " ".join(f'<a href="{h(href)}">{esc(label)}</a>' for href, label in source_links(card["policy_cite"]))
    extra = []
    if card.get("related_quiz"):
        extra.append(f'<a href="{h(card["related_quiz"])}">Related quiz</a>')
    if card.get("related_qa"):
        extra.append(f'<a href="{h(card["related_qa"])}">Related enquiry pack</a>')
    flag = "1" if card["app_c_flag"] else "0"
    badge = f'<span class="badge badge-{esc(card["modality"])}">{esc(card["modality"].capitalize())}</span>'
    if card["app_c_flag"]:
        badge += ' <span class="badge badge-appc">App C</span>'
    extras = " · ".join(extra)
    return f"""
<article class="aid" id="{esc(card["id"])}" data-modality="{esc(card["modality"])}" data-flag="{flag}" data-roles="{" ".join(card["roles"])}" data-sdlc="{" ".join(card["sdlc"])}" data-needs="{" ".join(card["needs"])}" data-tiers="{" ".join(card["tiers"])}">
  <div class="item-row">
    <input type="checkbox" id="tick-{esc(card["id"])}" data-tick="{esc(card["id"])}" aria-label="Optional tick for {esc(card["title"])}">
    <div>
      <div class="item-meta">{badge}<span class="id-code">{esc(card["id"])}</span></div>
      <h2>{esc(card["title"])}</h2>
      <p class="glance">{aid_glance_html(esc, card)}</p>
      <dl class="aid-fields">
        <div><dt>Relevance</dt><dd>{esc(card["relevance"])}</dd></div>
        <div><dt>Applicability</dt><dd class="aid-lines">{aid_applicability_html(esc, card)}</dd></div>
        <div><dt>Prerequisites</dt><dd>{esc(card["prerequisites"])}</dd></div>
        <div><dt>Implementation guidance</dt><dd>{esc(card["implementation_guidance"])}</dd></div>
        <div><dt>Source</dt><dd>{links}</dd></div>
      </dl>
      <p class="fine">{extras}</p>
    </div>
  </div>
</article>
"""


def decision_page(h, esc, page, legend, guide):
    cards = "".join(aid_article(h, esc, card) for card in cards_sorted(page["cards"]))
    return f"""
<h1>{esc(page["title"])}</h1>
<p class="lede">{esc(page["intro"])}</p>
{guide}
{legend}
<div class="toolbar no-print">
  <button type="button" class="btn btn-ghost" data-aid-filter="all" aria-pressed="true">All items</button>
  <button type="button" class="btn btn-ghost" data-aid-filter="shall" aria-pressed="false">Shall only</button>
  <button type="button" class="btn btn-ghost" data-aid-filter="flag" aria-pressed="false">Show only App C items</button>
  <button type="button" class="btn btn-primary" data-action="print">Print this decision aid</button>
</div>
<p class="storage-note">Optional self-progress. Stored only in this browser.</p>
<div data-aid-root data-checklist>{cards}</div>
"""


def core1_index(h, esc):
    groups = []
    current = None
    bucket = []
    for page in PAGES:
        if page["group"] != current:
            if bucket:
                groups.append((current, bucket))
            current = page["group"]
            bucket = []
        bucket.append(page)
    if bucket:
        groups.append((current, bucket))
    html = []
    for name, pages in groups:
        cards = []
        for page in pages:
            cards.append(
                f'<a class="info-card" href="{h(page["file"])}"><h3>{esc(page["title"])}</h3><p>{esc(page["audience"])} · {len(page["cards"])} cards · {esc(page["source"])}</p></a>'
            )
        html.append(f"<h2>{esc(name)}</h2><div class=\"card-grid\">{''.join(cards)}</div>")
    html.append(f'<h2>By need</h2><p><a href="{h("core1/by-need.html")}">Open the “I need to…” index</a></p>')
    return f"""
<h1>Decision aids</h1>
<p class="lede">One-glance answers. Each card states relevance, applicability, prerequisites, modality, and a section-level cite, and it links to the source text. Shall is listed first on every page.</p>
{''.join(html)}
"""


def need_index(h, esc):
    blocks = []
    for slug, label in NEEDS:
        hits = []
        for page, card in all_cards():
            if slug in card["needs"]:
                hits.append(
                    f'<li><a href="{h(page["file"])}#{esc(card["id"])}">{esc(card["title"])}</a> <span class="fine">{esc(page["title"])}</span></li>'
                )
        if not hits:
            continue
        blocks.append(f"<h2>{esc(label)}</h2><ul>{''.join(hits)}</ul>")
    return f"""
<h1>I need to…</h1>
<p class="lede">Pick the job in front of you. Each link opens a decision-aid card.</p>
{''.join(blocks)}
"""


def core3_index(h, esc):
    cards = []
    for pack in PACKS:
        cards.append(
            f'<a class="info-card" href="{h(pack["file"])}"><h3>{esc(pack["title"])}</h3><p>{esc(pack["audience"])} · {len(pack["items"])} placeholders</p></a>'
        )
    return f"""
<h1>Enquiry Q&amp;A</h1>
<p class="lede">These packs are shaped like sanitised departmental questions. Replace the placeholders with real enquiry records owned by the IT Security Unit. Do not add clause numbers that are not in the official text.</p>
<p>Each answer says it is derived from departmental enquiry records (anonymised), states a modality, and links to the source text.</p>
<div class="card-grid">{''.join(cards)}</div>
<h2>Suggest a new enquiry</h2>
<p>This hub has no mailbox and no backend. Hand a sanitised question to your IT Security Unit on paper or through the channel your unit already uses.</p>
<form class="offline-form" action="#" onsubmit="return false;">
  <label for="suggest-q">Question to hand over (not submitted)</label>
  <textarea id="suggest-q" rows="4" placeholder="Write the question here, then copy it into your unit’s own channel."></textarea>
  <p class="fine">Nothing on this form is stored or sent.</p>
</form>
"""


def qa_page(h, esc, pack):
    blocks = []
    for item in pack["items"]:
        links = " ".join(f'<a href="{h(href)}">{esc(label)}</a>' for href, label in source_links(item["policy_cite"]))
        related = ""
        if item.get("related_dec"):
            related = f'<p><a href="{h(item["related_dec"])}">Related decision aid</a></p>'
        blocks.append(f"""
<article class="aid" id="{esc(item["id"])}">
  <h2>{esc(item["question"])}</h2>
  <p class="glance">{esc(item["answer"])}</p>
  <dl class="aid-fields">
    <div><dt>Source note</dt><dd>{esc(item["source_note"])}</dd></div>
    <div><dt>Modality</dt><dd><span class="badge badge-{esc(item["modality"])}">{esc(item["modality"].capitalize())}</span></dd></div>
    <div><dt>Source</dt><dd>{links}</dd></div>
  </dl>
  {related}
</article>""")
    return f"""
<h1>{esc(pack["title"])}</h1>
<p class="lede">Placeholder enquiry pack for {esc(pack["audience"]).lower()}. {esc(pack["source"])}.</p>
<p>Derived from departmental enquiry records (anonymised). The IT Security Unit replaces these pairs with real records.</p>
{''.join(blocks)}
"""


def source_search_box(h):
    home = h("index.html")
    root = "" if home == "index.html" else home[: -len("index.html")]
    return f"""
<div class="source-search-block no-print">
<form class="source-search" role="search" data-source-search data-root="{root}" action="{h("core4/index.html")}" method="get">
  <label for="source-query">Search the wording in S17 and G3
    <input id="source-query" type="search" name="q" autocomplete="off" spellcheck="false" placeholder="A word or an exact phrase">
  </label>
</form>
<p class="fine">A single word matches that word. More than one word matches the exact phrase. Listed abbreviations and their full names are searched together. Choose a section to open it.</p>
<p class="fine" data-source-search-status aria-live="polite"></p>
<ul class="result-list" data-source-search-results></ul>
</div>
"""


def core4_index(h, esc):
    return f"""
<h1>Source lookup</h1>
<p class="lede">Original section text, with the document title, version, and section id on every page. Curated pages stay the way in. This is not the home page, and it is not a single dump of both policies.</p>
{source_search_box(h)}
<p>Versions are S17 v8.2 and G3 v10.2 (assumed if the PDFs were not re-checked for this build). Last reviewed 2026-10-26. Hub Content Owner.</p>
<div class="card-grid">
  <a class="info-card" href="{h("core4/s17/index.html")}"><h3>Baseline IT Security Policy [S17] v8.2</h3><p>Sections 1 to 20.</p></a>
  <a class="info-card" href="{h("core4/g3/index.html")}"><h3>IT Security Guidelines [G3] v10.2</h3><p>Sections 1 to 20.</p></a>
  <a class="info-card" href="{h("core4/g3/appendix-c.html")}"><h3>G3 Appendix C</h3><p>Tier 2 and Tier 3. The appendix wording stays in the official PDF. This page is the clause map.</p></a>
</div>
"""


def toc_page(h, esc, doc_code, doc_title, version, sections):
    rows = []
    for section in sections:
        number = section["number"]
        target = f"core4/{doc_code}/s{section['id']}.html"
        rows.append(
            f'<li><a href="{h(target)}">§{esc(number)} {esc(section["title"])}</a></li>'
        )
    other = "g3" if doc_code == "s17" else "s17"
    other_name = "G3" if doc_code == "s17" else "S17"
    return f"""
<h1>{esc(doc_title)}</h1>
<p class="lede">{esc(version)}. April 2025. Digital Policy Office. Last reviewed 2026-10-26.</p>
{source_search_box(h)}
<ol class="toc">{''.join(rows)}</ol>
<p><a href="{h(f"core4/{other}/index.html")}">{other_name} contents</a> · <a href="{h("core4/g3/appendix-c.html")}">Appendix C</a></p>
"""


def source_page(h, esc, doc_code, doc_title, version, section, body_html, figure_html, clause_links, back_links, copy_notice, permission):
    number = str(int(section["number"]))
    paired = "g3" if doc_code == "s17" else "s17"
    paired_name = "G3" if doc_code == "s17" else "S17"
    cross = [f'<a href="{h(f"core4/{paired}/s{section["id"]}.html")}">{paired_name} §{number}</a>']
    if number in APPC_SECTIONS:
        cross.append(f'<a href="{h("core4/g3/appendix-c.html")}#area-{number}">G3 Appendix C · §{number}</a>')
    clauses = "".join(f'<li><a href="#{esc(anchor)}">{esc(ident)} {esc(label)}</a></li>' for anchor, ident, label in clause_links)
    clause_block = f"<h2>Clause ids in this section</h2><ul>{clauses}</ul>" if clauses else ""
    backs = "".join(f'<li><a href="{h(href)}">{esc(label)}</a></li>' for href, label in back_links)
    back_block = f"<h2>Back to curated pages</h2><ul>{backs}</ul>" if backs else "<h2>Back to curated pages</h2><p><a href=\"" + h("core1/index.html") + "\">Decision aids</a></p>"
    return f"""
<header class="source-head">
  <p class="kicker">{esc(doc_title)} · {esc(version)}</p>
  <h1>{esc(doc_code.upper())} §{esc(number)} — {esc(section["title"])}</h1>
  <dl class="source-meta">
    <div><dt>Document</dt><dd>{esc(doc_title)}</dd></div>
    <div><dt>Version</dt><dd>{esc(version)} · April 2025 · Digital Policy Office</dd></div>
    <div><dt>Section</dt><dd>{esc(doc_code.upper())} §{esc(number)}</dd></div>
    <div><dt>Last reviewed</dt><dd>2026-10-26</dd></div>
    <div><dt>Owner</dt><dd>Hub Content Owner</dd></div>
  </dl>
  <p class="fine">Assumed if the PDFs were not re-checked for this build. Authoritative text remains the official PDF.</p>
</header>
<p class="crosswalk">Paired section: {" · ".join(cross)}</p>
{clause_block}
{back_block}
{figure_html}
<p class="copy-notice">{esc(copy_notice)}</p>
<p class="copy-notice">{esc(permission)}</p>
<div class="policy-text">{body_html}</div>
<p class="copy-notice">{esc(permission)}</p>
"""


def appendix_page(h, esc, rows_html, back_links):
    backs = "".join(f'<li><a href="{h(href)}">{esc(label)}</a></li>' for href, label in back_links)
    return f"""
<header class="source-head">
  <p class="kicker">IT Security Guidelines [G3] · Appendix C</p>
  <h1>G3 Appendix C — Tier 2 and Tier 3</h1>
  <dl class="source-meta">
    <div><dt>Document</dt><dd>IT Security Guidelines [G3], Appendix C</dd></div>
    <div><dt>Version</dt><dd>v10.2 · April 2025 · Digital Policy Office</dd></div>
    <div><dt>Section</dt><dd>G3 Appendix C</dd></div>
    <div><dt>Last reviewed</dt><dd>2026-10-26</dd></div>
    <div><dt>Owner</dt><dd>Hub Content Owner</dd></div>
  </dl>
  <p class="fine">Assumed if the PDFs were not re-checked for this build. This page lists the areas. It does not invent clause numbers inside the appendix.</p>
</header>
<p id="inheritance" class="callout"><strong>Tier 3 includes Tier 2.</strong> Every Tier 2 Appendix C control also applies to Tier 3.</p>
<p>The official appendix text stays in the G3 PDF. The matrix is a learning map of those areas. Confirm a row against the PDF before you quote it.</p>
{rows_html}
<h2>Back to curated pages</h2>
<ul>{backs}</ul>
<p><a href="{h("app-c-matrix.html")}">Open the filterable matrix</a></p>
"""


def sdlc_page(h, esc, stage, items_html, legend, guide):
    aids = " · ".join(f'<a href="{h(href)}">Decision aid</a>' if False else f'<a href="{h(href)}">{esc(href.split("/")[-1])}</a>' for href in stage["aids"])
    # clearer labels
    labels = {
        "core1/management.html": "Management",
        "core1/sdlc-security.html": "Acquisition and development",
        "core1/tier-appc.html": "Tier and App C",
        "core1/access-control.html": "Access",
        "core1/cryptography.html": "Cryptography",
        "core1/outsourcing.html": "Outsourcing",
        "core1/operations.html": "Operations",
        "core1/privileged.html": "Privileged access",
        "core1/compliance.html": "Compliance",
        "core1/incident.html": "Incidents",
        "core1/asset.html": "Assets",
    }
    aid_links = " · ".join(
        f'<a href="{h(href)}">{esc(labels.get(href, "Decision aid"))}</a>' for href in stage["aids"]
    )
    prev_next = []
    index = STAGES.index(stage)
    if index > 0:
        prev_stage = STAGES[index - 1]
        prev_next.append(f'<a href="{h(prev_stage["file"])}">Previous · {esc(prev_stage["name"])}</a>')
    if index < len(STAGES) - 1:
        nxt = STAGES[index + 1]
        prev_next.append(f'<a href="{h(nxt["file"])}">Next · {esc(nxt["name"])}</a>')
    return f"""
<h1>{esc(stage["code"])} · {esc(stage["name"])}</h1>
<p class="lede">{esc(stage["blurb"])}</p>
<p>Typical themes, at section level: {esc(stage["themes"])}.</p>
{guide}
{legend}
<p class="storage-note">Optional self-progress. Stored only in this browser.</p>
<div data-checklist>{items_html}</div>
<p>{aid_links}</p>
<p>{" · ".join(prev_next)} · <a href="{h("cheatsheets/sdlc.html")}">SDLC cheat sheet</a> · <a href="{h("core4/s17/s16.html")}">S17 §16</a> · <a href="{h("core4/g3/s16.html")}">G3 §16</a></p>
"""


def about_page(esc, version, disclaimer):
    return f"""
<h1>About this hub</h1>
<p>The HKSARG IT Security Learning Hub is a static learning aid for bureau and department staff. It is aligned to Baseline IT Security Policy [S17] version 8.2 and IT Security Guidelines [G3] version 10.2, issued by the Digital Policy Office in April 2025.</p>
<p>{esc(version)}</p>
<h2>How to use it</h2>
<ol>
  <li>New joiners follow fundamentals, then framework and accountability.</li>
  <li>Current staff filter by role, system lifecycle, and need.</li>
  <li>Read a decision aid before the long text. Open the source pages when you need the section itself.</li>
  <li>Order is S17, then G3, then Appendix C only for Tier 2 or Tier 3. Shall first. Not every word.</li>
</ol>
<h2>Versions</h2>
<ul>
  <li>Hub v0.1-MVP, last reviewed 2026-10-26.</li>
  <li>S17 v8.2 and G3 v10.2, April 2025. Assumed if the PDFs were not re-checked for this build.</li>
</ul>
<h2>Accessibility</h2>
<p>The target is WCAG 2.1 AA: text contrast, visible focus, a logical heading order, and keyboard access to the overview, filters, and quizzes. Pages are English only.</p>
<h2>What this hub will not do</h2>
<ul>
  <li>No login, no staff roster, and no completion record on a server.</li>
  <li>A tick is a private note in one browser. It is not evidence and not a signature.</li>
</ul>
<p>{esc(disclaimer)}</p>
"""


def gov_page(h):
    return f"""
<h1>Governance and updates</h1>
<p>This page is for persons who maintain the hub when S17 or G3 is revised. It is not a learner completion record.</p>
<h2>Roles</h2>
<table>
  <thead><tr><th>Role</th><th>Who</th><th>What they do</th></tr></thead>
  <tbody>
    <tr><td>Hub Content Owner</td><td>IT Security Management Unit lead, or a DITSO delegate. Name to be filled by the B/D.</td><td>Diff a new S17 or G3, update the source pages, the version banner, and this log.</td></tr>
    <tr><td>Technical Publisher</td><td>Whoever copies the static files to the intranet or a shared folder.</td><td>Publish the files. No account system is required.</td></tr>
    <tr><td>Role SME</td><td>Security admin for incidents, a development lead for §16, and so on.</td><td>Patch the decision aid, quiz, or Q&amp;A pack when a practice guide changes.</td></tr>
  </tbody>
</table>
<h2>When S17 or G3 changes</h2>
<table>
  <thead><tr><th>Trigger</th><th>Owner</th><th>Action</th><th>SLA</th></tr></thead>
  <tbody>
    <tr><td>DPO issues a new S17 or G3</td><td>Hub Content Owner</td><td>Re-extract the affected sections into the source pages. Update decision-aid cites, the version banner, and this log. Do not invent clause numbers.</td><td>Start within 10 working days of circulation.</td></tr>
    <tr><td>Practice guide update</td><td>Role SME</td><td>Patch the affected decision aid, cheat sheet, or quiz only.</td><td>15 working days.</td></tr>
    <tr><td>Local B/D policy change</td><td>Local policy owner</td><td>Update any local wording on the policy-stack card.</td><td>10 working days.</td></tr>
    <tr><td>Enquiry records curated</td><td>IT Security Unit</td><td>Replace Q&amp;A placeholders with sanitised records. Keep section-level cites.</td><td>As records are cleared.</td></tr>
    <tr><td>Quarterly hygiene</td><td>Hub Content Owner</td><td>Link check and a log line even when nothing changed.</td><td>Once a quarter.</td></tr>
  </tbody>
</table>
<h2>Revision log</h2>
<table>
  <caption>Date, policy versions, summary, editor</caption>
  <thead><tr><th>Date</th><th>S17 / G3</th><th>Summary</th><th>Editor</th></tr></thead>
  <tbody>
    <tr><td>2026-10-23</td><td>S17 v8.2 / G3 v10.2 (April 2025)</td><td>First static hub. Checklists, quizzes, Appendix C matrix, and gap table.</td><td>Initial build. Content Owner to confirm the named editor.</td></tr>
    <tr><td>2026-10-26</td><td>S17 v8.2 / G3 v10.2 (assumed if PDFs not re-checked)</td><td>Hub v0.1-MVP. Aids, quizzes, Q&amp;A, and source, plus the Policy and System Lifecycle Overview, new-joiners path, and current-staff filters by role, stage, and need. Source holds section text. Q&amp;A is still placeholder enquiry text.</td><td>Rebuild against the site map. Content Owner to confirm the named editor.</td></tr>
  </tbody>
</table>
<p>Pages carry <code>data-source-sections</code>, <code>data-last-reviewed</code>, and <code>data-owner-role</code> for this maintenance loop. Learner ticks stay in the browser.</p>
<p><a href="{h("core4/index.html")}">Source lookup</a></p>
"""
