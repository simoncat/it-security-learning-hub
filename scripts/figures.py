"""Related figures for the Sections page.

Document stack, lifecycle chart, and organisation chart follow the figures in
S17 §2.3, G3 §2, and S17/G3 §5.2. The tier picture and the three objectives are
reading aids for definitions the text already states.
"""


def section_figure(section_id, fn_prefixes=None):
    return {
        "02": document_figure() + lifecycle_figure(),
        "04": tier_figure(),
        "05": org_figure(fn_prefixes),
        "06": cia_figure(),
        "18": incident_figure(),
    }.get(section_id, "")


def footnote_marks(prefixes, number):
    if not prefixes:
        return ""
    marks = []
    for index, prefix in enumerate(prefixes):
        extra = " fn-ref-alias" if index else ""
        marks.append(
            f'<a class="fn-ref{extra}" id="fnref-{prefix}-{number}" href="#fn-{prefix}-{number}"><sup>{number}</sup></a>'
        )
    return "".join(marks)


def document_figure():
    guides = [
        "IT Security Risk Management",
        "Security Risk Assessment & Audit",
        "Information Security Incident Handling",
        "IT Security Threat Management",
        "Cloud Computing Security",
        "Data Loss Prevention",
        "Internet Gateway Security",
        "Penetration Testing",
        "Website and Web Application Security",
        "…",
    ]
    local = [
        "Departmental IT Security Policies",
        "Information Security Incident Handling Procedure",
        "Standard Operating Procedures",
        "Guidelines",
        "…",
    ]
    guide_html = "".join(f"<li>{name}</li>" for name in guides)
    local_html = "".join(f"<li>{name}</li>" for name in local)
    return f"""
<figure class="figure">
  <figcaption>Relationship of IT security documents, as drawn in S17 §2.3 and G3 §2.3. The ellipsis is in the official figure: the tiles are examples, not a full catalogue.</figcaption>
  <div class="docfig">
    <div class="docfig-top">
      <div class="docfig-band docfig-sr">
        <p>Security Regulations</p>
        <div>Security Regulations (SR)</div>
      </div>
      <div class="docfig-band docfig-gov">
        <p>Government IT Security Policy and Guidelines</p>
        <div class="docfig-pair">
          <div>Baseline IT Security Policy (S17)</div>
          <div>IT Security Guidelines (G3)</div>
        </div>
      </div>
    </div>
    <div class="docfig-band docfig-guides">
      <p>Practice Guides</p>
      <ul>{guide_html}</ul>
    </div>
    <div class="docfig-band docfig-local">
      <p>Departmental IT Security Policies, Procedures and Guidelines</p>
      <ul>{local_html}</ul>
    </div>
  </div>
</figure>
"""


def lifecycle_figure():
    groups = [
        ("Project Initiation", [
            ("Project Initiation", ""),
        ]),
        ("Feasibility Study", [
            ("Stage 0 — Feasibility Study", ""),
        ]),
        ("System Analysis & Design", [
            ("Stage 1 — Investigation of Current Environment", ""),
            ("Stage 2 — Business System Options", ""),
            ("Stage 3 — Definition of Requirements", "Asset Management. Outsourcing Security."),
            ("Stage 4 — Technical System Options", "Communications Security. Operations Security."),
            ("Stage 5 — Logical System Design", "Asset Management. Access Control. System Acquisition, Development and Maintenance."),
        ]),
        ("Implementation", [
            ("Stage 6 — Physical System Design", "Physical and Environmental Security. Communications Security. Operations Security."),
            ("Program / System Development", "System Acquisition, Development and Maintenance."),
            ("System Integration Test", "System Acquisition, Development and Maintenance continues."),
            ("User Acceptance Test", "System Acquisition, Development and Maintenance continues."),
            ("System Installation & Production", "System Acquisition, Development and Maintenance. Communications Security. Operations Security."),
        ]),
        ("Post-Implementation Review", [
            ("Post Implementation Review", "Compliance. Security Incident Management."),
        ]),
    ]
    body = []
    for phase, stages in groups:
        for index, (stage, areas) in enumerate(stages):
            phase_cell = f'<th scope="rowgroup" rowspan="{len(stages)}">{phase}</th>' if index == 0 else ""
            body.append(f"<tr>{phase_cell}<td>{stage}</td><td>{areas}</td></tr>")
    return f"""
<figure class="figure">
  <figcaption>Security considerations by phase of the system development life cycle. G3 §2, the chart after the fourteen security areas. On the official chart a dotted line carries System Acquisition, Development and Maintenance from program development through user acceptance test.</figcaption>
  <div class="fig-scroll">
    <table class="life">
      <thead>
        <tr><th>Phase</th><th>Stage</th><th>Areas called out for special attention</th></tr>
      </thead>
      <tbody>
        {''.join(body)}
      </tbody>
    </table>
  </div>
</figure>
"""


def tier_figure():
    return """
<figure class="figure">
  <figcaption>How the three tiers sit inside each other. Reading aid for the definitions in §4.1. Tier 2 is a kind of Tier 1 system. Tier 3 is a kind of Tier 2 system. Appendix C applies to Tier 2, and Tier 3 takes every Tier 2 Appendix C control as well as its own.</figcaption>
  <div class="tiers" aria-hidden="false">
    <div class="tier tier-1">
      <strong>Tier 1</strong>
      <span>Ordinary information systems. The baseline in S17 and G3.</span>
      <div class="tier tier-2">
        <strong>Tier 2</strong>
        <span>Crucial to government or society. Serious impact if disrupted. Baseline plus Appendix C.</span>
        <div class="tier tier-3">
          <strong>Tier 3</strong>
          <span>A Tier 2 system directly related to an essential service. Appendix C, including the Tier 3-only controls.</span>
        </div>
      </div>
    </div>
  </div>
</figure>
"""


def org_figure(fn_prefixes=None):
    mark = footnote_marks(fn_prefixes, "1")
    return f"""
<figure class="figure" id="org-chart">
  <figcaption>Example organisation chart for departmental IT security management{mark}. S17 §5.2 and G3 §5.2. The chart in the official text is an example. The structure may vary.</figcaption>
  <div class="org">
    <div class="org-apex">
      <div class="org-box org-main">Departmental IT Security Officer</div>
      <span class="org-dash" aria-hidden="true"></span>
      <div class="org-box org-side">Departmental Security Officer</div>
    </div>
    <ul class="org-tree">
      <li><div class="org-box">Information Security Steering Committee *</div></li>
      <li><div class="org-box">IT Security Management Unit</div></li>
      <li><div class="org-box">Departmental ISIRT Commander</div></li>
      <li><div class="org-box">IT Security Administrators</div></li>
      <li><div class="org-box">Information Owners</div></li>
      <li><div class="org-box">LAN / System Administrators</div></li>
      <li><div class="org-box">Application Development &amp; Maintenance Team</div></li>
      <li><div class="org-box">Users</div></li>
    </ul>
  </div>
  <p class="fig-note">Solid lines show the sample framework. The steering committee and the IT security management unit report to the Departmental IT Security Officer. The dashed line means the DITSO collaborates with the Departmental Security Officer, who may be the same person.</p>
  <p class="fig-note">* The Information Security Steering Committee is a mandatory requirement for B/Ds with Tier 3 information systems.</p>
</figure>
"""


def cia_figure():
    return """
<figure class="figure">
  <figcaption>The three information-system security objectives named in §6, using the §4.1 definitions.</figcaption>
  <ul class="cia">
    <li><strong>Confidentiality</strong> Only authorised persons and information systems are allowed to know or gain access to the information.</li>
    <li><strong>Integrity</strong> Only authorised persons and information systems are allowed to make changes to the information.</li>
    <li><strong>Availability</strong> The information system is accessible and usable on demand by authorised persons and information systems.</li>
  </ul>
</figure>
"""


def incident_figure():
    return """
<figure class="figure">
  <figcaption>Reporting path drawn from G3 §18.1. It is a reading aid, not a separate figure in the PDF. Follow the departmental procedure and the current official text for the exact steps.</figcaption>
  <ol class="incident">
    <li><strong>Aware</strong><span>A person is reasonably aware of harm to confidentiality, integrity, availability, or operations. Do not wait to be certain.</span></li>
    <li><strong>ISIRT</strong><span>The departmental ISIRT is the handling team.</span></li>
    <li><strong>GIRO</strong><span>Phone the GIRO Standing Office within 60 minutes. Send the preliminary form within 48 hours.</span></li>
    <li><strong>Sharing</strong><span>Only the ISIRT Commander authorises sharing outside the handling team.</span></li>
  </ol>
</figure>
"""
