# Learner-path source data. Item IDs match the build brief §4.

def I(id, text, modality, pace="both", flag=False, refs=None, note=""):
    return {
        "id": id,
        "text": text,
        "modality": modality,
        "pace": pace,
        "flag": flag,
        "refs": refs or [],
        "note": note,
    }


PACE = {
    "both": "New joiners and current staff",
    "a-required": "New joiners: do this",
    "b-required": "Current staff: confirm the live detail",
    "b-focus": "Current staff: focus",
    "b-gap": "New joiners: do this · Current staff: only if it is a gap",
}

FOUNDATION = {
    "exit": [
        "Explain Shall, Should, and May in your own words.",
        "Name your security contacts (DITSO, security unit, ISIRT, line manager).",
        "Say how you would report an incident without waiting to be certain.",
        "State whether Tier 2/3 and App C might apply to a system you use.",
    ],
    "days": [
        {
            "label": "Day 1",
            "title": "What / why / who",
            "pace": "both",
            "items": [
                I("F-D1-01", "Read S17 §1–2 and G3 §1–2 (purpose, scope, applicability).", "shall", refs=[("S17", "§1"), ("G3", "§1")]),
                I("F-D1-02", "Note the stack: Security Regulations, then S17, then G3, then practice guides, then local B/D policy.", "shall", refs=[("G3", "§2")]),
                I("F-D1-03", "Identify contacts: DITSO, IT Security Management Unit, ISIRT Commander, and your line manager.", "shall", refs=[("G3", "§5")]),
                I("F-D1-04", "Locate the local IT security policy and end-user instructions. G3 Appendix A is only a sample shape.", "shall", "a-required", refs=[("G3", "§8")], note="New joiners: required"),
                I("F-D1-05", "Confirm the current local policy links, including version and date.", "shall", "b-required", refs=[("G3", "§8")], note="Current staff: required"),
            ],
        },
        {
            "label": "Day 2",
            "title": "Conventions and organisation",
            "pace": "both",
            "items": [
                I("F-D2-01", "Memorise the modality words: Shall, Should, and May (S17/G3 §4.2).", "shall", refs=[("S17", "§4"), ("G3", "§4")]),
                I("F-D2-02", "Skim S17/G3 §5: ISMC, ITSWG, GIRO, GovCERT.HK, and your departmental structure.", "should", refs=[("S17", "§5"), ("G3", "§5")]),
                I("F-D2-03", "Find your role in G3 §5.2–5.3 and tick the duties that apply to you.", "shall", refs=[("G3", "§5")]),
                I("F-D2-04", "Find the DITSO, security unit, ISIRT contact, and line manager in the reporting procedure.", "shall", "a-required", refs=[("G3", "§5"), ("G3", "§18")], note="New joiners: required."),
            ],
        },
        {
            "label": "Day 3",
            "title": "Core principles",
            "pace": "both",
            "items": [
                I("F-D3-01", "Read S17/G3 §6: CIA, risk-based decisions, security-by-design, and prevent / detect / respond / recover.", "shall", refs=[("S17", "§6"), ("G3", "§6")]),
                I("F-D3-02", "Write one sentence each for confidentiality, integrity, and availability on a system you use.", "should", refs=[("G3", "§6")]),
                I("F-D3-04", "List two or three pain points (audit, near-miss, or App C doubts) to carry into Days 8–30.", "should", "b-focus", note="Current staff"),
            ],
        },
        {
            "label": "Day 4",
            "title": "Management, policy, persons",
            "pace": "b-gap",
            "items": [
                I("F-D4-01", "S17/G3 §7 management responsibilities, including the overview of risk and classified protection.", "shall", "b-gap", refs=[("S17", "§7"), ("G3", "§7")], note="New joiners: all. Current staff: if gap."),
                I("F-D4-02", "S17/G3 §8 IT security policies. Departmental policy aligns with S17 and G3.", "shall", "b-gap", refs=[("S17", "§8"), ("G3", "§8")], note="New joiners: all. Current staff: if gap."),
                I("F-D4-03", "S17/G3 §9 human resource security: joiners, leavers, and awareness.", "shall", "b-gap", refs=[("S17", "§9"), ("G3", "§9")], note="New joiners: read carefully. Current staff: if gap."),
                I("F-D4-04", "Know your B/D security awareness and training requirement.", "shall", "b-gap", refs=[("G3", "§9")], note="Current staff: if this day is a gap."),
            ],
        },
        {
            "label": "Day 5",
            "title": "Assets and access",
            "pace": "b-gap",
            "items": [
                I("F-D5-01", "S17/G3 §10 asset management: ownership, classification, and media.", "shall", "b-gap", refs=[("S17", "§10"), ("G3", "§10")]),
                I("F-D5-02", "S17/G3 §11 access control at a high level: least privilege, passwords, mobile and remote access, IoT.", "shall", "b-gap", refs=[("S17", "§11"), ("G3", "§11")]),
                I("F-D5-03", "Practice: list assets you handle and their classification. Ask the Information Owner if you are unsure.", "should", "b-gap", refs=[("G3", "§10")]),
            ],
        },
        {
            "label": "Day 6",
            "title": "Operations lite, incidents, continuity",
            "pace": "b-gap",
            "items": [
                I("F-D6-01", "Skim S17/G3 §14 (malware, backup, logging, vulnerabilities, threats). Depth comes in the role path.", "should", "b-gap", refs=[("S17", "§14"), ("G3", "§14")]),
                I("F-D6-02", "S17/G3 §18 incident management: how to report. Do not wait until you are sure.", "shall", "b-gap", refs=[("S17", "§18"), ("G3", "§18")]),
                I("F-D6-03", "S17/G3 §19 continuity: plans exist. Note where your B/D keeps them.", "shall", "b-gap", refs=[("S17", "§19"), ("G3", "§19")]),
                I("F-D6-04", "Confirm the ISIRT and incident contacts in the reporting procedure, including after-hours numbers.", "shall", "a-required", refs=[("G3", "§18")], note="New joiners"),
            ],
        },
        {
            "label": "Day 7",
            "title": "Compliance, tier, and wrap",
            "pace": "b-gap",
            "items": [
                I("F-D7-01", "S17/G3 §20 compliance: security risk assessment, audit, and technical review, at awareness level.", "shall", "b-gap", refs=[("S17", "§20"), ("G3", "§20")]),
                I("F-D7-02", "Learn Tier 1, Tier 2, and Tier 3 (G3 §4.1). Tier 2 and Tier 3 also take Appendix C.", "shall", "b-gap", refs=[("G3", "§4"), ("App C", "§4")]),
                I("F-D7-03", "Note which of your systems might be Tier 2 or Tier 3. Confirm that on Days 22–24. Do not self-finalise the tier.", "shall", "b-gap", True, refs=[("G3", "§4"), ("App C", "§7")], note="App C may apply."),
                I("F-D7-05", "Foundation refresh done. Continue the role path with your gap list.", "should", "b-focus", note="Current staff"),
            ],
        },
    ],
}

ROLES = [
    {
        "n": "1",
        "title": "Elevated end user / general IT with elevated duties",
        "anchor": "G3 §5 theme, plus admin tasks you actually hold",
        "quick": "One-page personal SOP: login, classify, share, report.",
        "walk": "Tabletop a security event on the ISIRT path, or a joiner/leaver check for an elevated account.",
        "clusters": [
            {
                "days": "Days 8–9",
                "focus": "Access and user duties",
                "order": "S17 §11 → G3 §11",
                "items": [
                    I("R1-D89-01", "Read S17, then G3 §11: user responsibilities, passwords, and mobile or remote access.", "shall", refs=[("S17", "§11"), ("G3", "§11")]),
                    I("R1-D89-02", "Confirm elevated accounts are still justified, and that MFA is used where it is required.", "shall", refs=[("G3", "§11")]),
                    I("R1-D89-03", "Review the local acceptable-use rules and end-user instructions.", "shall", refs=[("G3", "§8")]),
                ],
            },
            {
                "days": "Days 10–11",
                "focus": "Assets and handling",
                "order": "S17 §10 → G3 §10",
                "items": [
                    I("R1-D1011-01", "Read S17/G3 §10 on assets you create or handle.", "shall", refs=[("S17", "§10"), ("G3", "§10")]),
                    I("R1-D1011-02", "Apply classification labels on documents you create.", "shall", refs=[("G3", "§10")]),
                    I("R1-D1011-03", "Follow media, USB, and disposal rules.", "shall", refs=[("G3", "§10")]),
                ],
            },
            {
                "days": "Days 12–13",
                "focus": "Cryptography and physical security, light pass",
                "order": "S17 §12 → G3 §12, then S17 §13 → G3 §13",
                "items": [
                    I("R1-D1213-01", "High-level pass of S17/G3 §12: when encryption is required.", "shall", refs=[("S17", "§12"), ("G3", "§12")]),
                    I("R1-D1213-02", "S17/G3 §13: clear desk, clear screen, and secure areas.", "shall", refs=[("S17", "§13"), ("G3", "§13")]),
                ],
            },
            {
                "days": "Days 14–15",
                "focus": "Operations hygiene and malware",
                "order": "S17 §14 → G3 §14",
                "items": [
                    I("R1-D1415-01", "S17/G3 §14.2–14.4 themes: malware, backup, and logging, at user level.", "shall", refs=[("S17", "§14"), ("G3", "§14")]),
                    I("R1-D1415-02", "Act on patch prompts, suspicious mail, and USB discipline.", "shall", refs=[("G3", "§14")]),
                    I("R1-D1415-03", "Know the backup expectation for data you own.", "should", refs=[("G3", "§14")]),
                ],
            },
            {
                "days": "Days 16–17",
                "focus": "Communications",
                "order": "S17 §15 → G3 §15",
                "items": [
                    I("R1-D1617-01", "S17/G3 §15.2: classified transfer, email, and external parties.", "shall", refs=[("S17", "§15"), ("G3", "§15")]),
                    I("R1-D1617-02", "Practice: encrypt, mark, and choose the channel the way local rules require.", "should", refs=[("G3", "§15")]),
                ],
            },
            {
                "days": "Days 18–19",
                "focus": "Incidents and an HR refresh",
                "order": "S17 §18 → G3 §18, and §9 if you supervise others",
                "items": [
                    I("R1-D1819-01", "Dry-run S17/G3 §18 reporting. Use a tabletop, not a fabricated live incident.", "shall", refs=[("S17", "§18"), ("G3", "§18")]),
                    I("R1-D1819-02", "If you supervise temps or contractors, refresh §9 on leavers and transfers.", "should", refs=[("G3", "§9")]),
                ],
            },
            {
                "days": "Days 20–21",
                "focus": "Compliance and wrap",
                "order": "S17 §20 → G3 §20 → App C access control if Tier 2/3",
                "items": [
                    I("R1-D2021-01", "Elevated access may be audited (§20, and App C access checks where Tier 2 applies).", "may", refs=[("G3", "§20"), ("App C", "§11")]),
                    I("R1-D2021-02", "If you are admin-adjacent to a Tier 2 or Tier 3 system, read the App C access-control bullets.", "shall", flag=True, refs=[("App C", "§11")], note="App C"),
                ],
            },
        ],
    },
    {
        "n": "2",
        "title": "System / LAN administrator",
        "anchor": "G3 §5 theme",
        "quick": "Privileged-account and patch-SLA one-pager for one production system.",
        "walk": "Patch or vulnerability handling for one host, or privileged access from request to grant to review.",
        "clusters": [
            {
                "days": "Days 8–10",
                "focus": "Access and privileged operations",
                "order": "S17 §11 → G3 §11 → App C §11 if Tier 2/3",
                "items": [
                    I("R2-D810-01", "Read S17, then G3 §11 in full for administration, not only end-user duties.", "shall", refs=[("S17", "§11"), ("G3", "§11")]),
                    I("R2-D810-02", "Build or refresh the privileged-account inventory for systems you run.", "shall", refs=[("G3", "§11")]),
                    I("R2-D810-03", "Apply the strong-password expectation and MFA where it is required.", "shall", refs=[("G3", "§11")]),
                    I("R2-D810-04", "App C §11: an independent privileged-account check at least every six months, and MFA for interactive privileged logon where feasible.", "shall", flag=True, refs=[("App C", "§11")], note="Tier 2, and therefore also Tier 3."),
                ],
            },
            {
                "days": "Days 11–13",
                "focus": "Operations security",
                "order": "S17 §14 → G3 §14 → App C §14 if Tier 2/3",
                "items": [
                    I("R2-D1113-01", "Read S17, then G3 §14.", "shall", refs=[("S17", "§14"), ("G3", "§14")]),
                    I("R2-D1113-02", "Malware protection on servers, not only on workstations.", "shall", refs=[("G3", "§14")]),
                    I("R2-D1113-03", "Backups: local and off-site.", "shall", refs=[("G3", "§14")]),
                    I("R2-D1113-04", "Logging that you can actually use in an incident.", "shall", refs=[("G3", "§14")]),
                    I("R2-D1113-05", "Hardening and change control.", "shall", refs=[("G3", "§14")]),
                    I("R2-D1113-06", "Patch and vulnerability process, including who is told if a fix slips.", "shall", refs=[("G3", "§14")]),
                    I("R2-D1113-07", "App C §14: off-site backup, a capacity plan, an end-of-support migration plan at least six months ahead, and patching typically within a month, with DITSO visibility if it slips.", "shall", flag=True, refs=[("App C", "§14")]),
                    I("R2-D1113-08", "Tier 3 only: 24×7 monitoring of a SIEM class, drawing on more than one source.", "shall", flag=True, refs=[("App C", "§14")], note="Tier 3 only, on top of the Tier 2 App C controls."),
                ],
            },
            {
                "days": "Days 14–16",
                "focus": "Network and communications",
                "order": "S17 §15 → G3 §15, with G3 §11.5 for admin access",
                "items": [
                    I("R2-D1416-01", "Read S17, then G3 §15.", "shall", refs=[("S17", "§15"), ("G3", "§15")]),
                    I("R2-D1416-02", "Segmentation, gateway, wireless, and Internet-facing exposure.", "shall", refs=[("G3", "§15")]),
                    I("R2-D1416-03", "Admin jump hosts and remote desktop inside the rules of G3 §11.5.", "shall", refs=[("G3", "§11")]),
                ],
            },
            {
                "days": "Days 17–18",
                "focus": "Physical security and cryptography",
                "order": "S17 §13 → G3 §13, and S17 §12 → G3 §12",
                "items": [
                    I("R2-D1718-01", "S17/G3 §13: equipment and secure areas you rely on.", "shall", refs=[("S17", "§13"), ("G3", "§13")]),
                    I("R2-D1718-02", "S17/G3 §12: cryptography in transit and at rest for data you administer.", "shall", refs=[("S17", "§12"), ("G3", "§12")]),
                ],
            },
            {
                "days": "Days 19–20",
                "focus": "Outsourcing and cloud",
                "order": "S17 §17 → G3 §17",
                "items": [
                    I("R2-D1920-01", "If a vendor runs the system or it sits in a cloud, read S17/G3 §17.", "shall", refs=[("S17", "§17"), ("G3", "§17")], note="Skip the deep read only when no provider is in the path. Record that."),
                    I("R2-D1920-02", "Write the shared-responsibility split in one paragraph: what you still own, and what the provider owns.", "shall", refs=[("G3", "§17")]),
                ],
            },
            {
                "days": "Day 21",
                "focus": "Incidents, continuity, compliance",
                "order": "S17 §18 → §19 → §20, then App C §19–20 if Tier 2/3",
                "items": [
                    I("R2-D21-01", "§18 runbook: how this system is reported and who is on the 7×24 path.", "shall", refs=[("G3", "§18")]),
                    I("R2-D21-02", "§19 contingency touchpoints for the system.", "shall", refs=[("G3", "§19")]),
                    I("R2-D21-03", "§20 vulnerability-scan and penetration-test cadence.", "shall", refs=[("G3", "§20")]),
                    I("R2-D21-04", "App C §19–20 for Tier 2/3: tested contingency, and the scan and pen-test expectations.", "shall", flag=True, refs=[("App C", "§19"), ("App C", "§20")]),
                    I("R2-D21-06", "Current staff: map each App C control you touch to evidence or a gap.", "shall", "b-focus", True, refs=[("App C", "§14")]),
                ],
            },
        ],
    },
    {
        "n": "3",
        "title": "Application developer / maintenance",
        "anchor": "G3 §5 and §16 themes",
        "quick": "Put a security-requirements checklist into your SDLC template.",
        "walk": "Security requirement, then a design note, then a test case. Or a test-data protection check.",
        "clusters": [
            {
                "days": "Days 8–10",
                "focus": "Security requirements and design",
                "order": "S17 §16 → G3 §16.1 → App C §16 if Tier 2/3",
                "items": [
                    I("R3-D810-01", "S17 then G3 §16.1: security-by-design, specifications, secure coding, and testing.", "shall", refs=[("S17", "§16"), ("G3", "§16")]),
                    I("R3-D810-02", "App C §16: shift-left, a pre-production security risk assessment that checks design-review follow-ups, and hardening before the production baseline.", "shall", flag=True, refs=[("App C", "§16")]),
                ],
            },
            {
                "days": "Days 11–12",
                "focus": "Development and support processes",
                "order": "G3 §16.2",
                "items": [
                    I("R3-D1112-01", "G3 §16.2: secure environment, source control, change control, and integrity.", "shall", refs=[("G3", "§16")]),
                    I("R3-D1112-02", "Segregation: development administration is not production administration where that split is required.", "shall", refs=[("G3", "§16"), ("G3", "§7")]),
                ],
            },
            {
                "days": "Days 13–14",
                "focus": "Test data",
                "order": "G3 §16.3",
                "items": [
                    I("R3-D1314-01", "G3 §16.3: protect production-like data and anonymise it where the rule requires.", "shall", refs=[("G3", "§16")]),
                ],
            },
            {
                "days": "Days 15–16",
                "focus": "Access and cryptography in applications",
                "order": "S17 §11.4 → G3 §11.4, and S17 §12 → G3 §12",
                "items": [
                    I("R3-D1516-01", "S17/G3 §11.4 application access control.", "shall", refs=[("S17", "§11"), ("G3", "§11")]),
                    I("R3-D1516-02", "§12 cryptography at rest and in transit.", "shall", refs=[("G3", "§12")]),
                    I("R3-D1516-03", "Session handling, authentication, authorisation, and secrets. Secrets do not live in source.", "shall", refs=[("G3", "§11"), ("G3", "§16")]),
                ],
            },
            {
                "days": "Days 17–18",
                "focus": "Operations handoff and vulnerabilities",
                "order": "G3 §14.6 and §14.4",
                "items": [
                    I("R3-D1718-01", "§14.6 technical vulnerabilities for your stack, including libraries.", "shall", refs=[("G3", "§14")]),
                    I("R3-D1718-02", "Logging under §14.4: what the app must emit for an incident.", "shall", refs=[("G3", "§14")]),
                ],
            },
            {
                "days": "Days 19–20",
                "focus": "Outsourcing, libraries, and APIs",
                "order": "S17 §17 → G3 §17",
                "items": [
                    I("R3-D1920-01", "§17 if the product is SaaS or built by a contractor.", "shall", refs=[("G3", "§17")]),
                    I("R3-D1920-02", "Know that contracts carry security clauses. Point to the owner of those clauses.", "should", refs=[("G3", "§17")]),
                ],
            },
            {
                "days": "Day 21",
                "focus": "Incidents, compliance, App C",
                "order": "S17 §18 → G3 §18, then §20, then App C if Tier 2/3",
                "items": [
                    I("R3-D21-01", "§18: what a secure-coding incident teaches, and how you would report one.", "shall", refs=[("G3", "§18")]),
                    I("R3-D21-02", "§20: security risk assessment, penetration test, and code review in the assurance path.", "shall", refs=[("G3", "§20")]),
                    I("R3-D21-03", "Tier 2/3: walk the App C development and compliance rows for your system.", "shall", flag=True, refs=[("App C", "§16"), ("App C", "§20")]),
                ],
            },
        ],
    },
    {
        "n": "4",
        "title": "IT security administrator / unit",
        "anchor": "G3 §5 theme",
        "quick": "A living dashboard: privileged-review dates, patch-SLA breaches, open SRA items, and App C evidence links.",
        "walk": "A privileged-account review sample, or an alert-to-triage-to-escalate drill.",
        "clusters": [
            {
                "days": "Days 8–9",
                "focus": "Mandate and segregation",
                "order": "G3 §5.3.1 and §5.2.5",
                "items": [
                    I("R4-D89-01", "Read the mandate in G3 §5.3.1 and the security-unit role in §5.2.5.", "shall", refs=[("G3", "§5")]),
                    I("R4-D89-02", "The security administrator should not be the same person as the system administrator.", "should", refs=[("G3", "§5"), ("G3", "§7")]),
                    I("R4-D89-03", "Protect audit-log integrity. Reviewers should not be able to quietly rewrite the record.", "shall", refs=[("G3", "§14")]),
                ],
            },
            {
                "days": "Days 10–12",
                "focus": "Access-control operations",
                "order": "S17 §11 → G3 §11 → App C §11 if Tier 2/3",
                "items": [
                    I("R4-D1012-01", "S17/G3 §11 end to end, from join to review to removal.", "shall", refs=[("S17", "§11"), ("G3", "§11")]),
                    I("R4-D1012-02", "Privilege reviews and joiner-mover-leaver.", "shall", refs=[("G3", "§11"), ("G3", "§9")]),
                    I("R4-D1012-03", "App C §11: independent privileged-account audits for Tier 2 and Tier 3.", "shall", flag=True, refs=[("App C", "§11")]),
                ],
            },
            {
                "days": "Days 13–15",
                "focus": "Operations oversight",
                "order": "S17 §14 → G3 §14.2, 14.4, 14.6, 14.7 → App C §14 for Tier 3",
                "items": [
                    I("R4-D1315-01", "S17/G3 §14.2, 14.4, 14.6, and 14.7: malware, logging, vulnerabilities, and threats.", "shall", refs=[("G3", "§14")]),
                    I("R4-D1315-02", "Patch governance: what “typically within a month” means, and when DITSO must see a delay.", "shall", refs=[("G3", "§14"), ("App C", "§14")]),
                    I("R4-D1315-03", "Threat intelligence through GIRO and GovCERT.HK.", "shall", refs=[("G3", "§5"), ("G3", "§14")]),
                    I("R4-D1315-04", "Tier 3 monitoring under App C §14: 24×7, multi-source, SIEM-class.", "shall", flag=True, refs=[("App C", "§14")]),
                ],
            },
            {
                "days": "Days 16–17",
                "focus": "Network and cryptography assurance",
                "order": "S17 §15 → G3 §15, and S17 §12 → G3 §12",
                "items": [
                    I("R4-D1617-01", "Review §15 and §12 with LAN administrators. Keep the segregation of duties intact.", "shall", refs=[("G3", "§15"), ("G3", "§12")]),
                ],
            },
            {
                "days": "Days 18–19",
                "focus": "Incident and continuity support",
                "order": "S17 §18 → G3 §18, and S17 §19 → G3 §19",
                "items": [
                    I("R4-D1819-01", "§18 with the ISIRT: your part of detection, escalation, and the record.", "shall", refs=[("G3", "§18")]),
                    I("R4-D1819-02", "§19: the security inputs a continuity plan needs.", "shall", refs=[("G3", "§19")]),
                ],
            },
            {
                "days": "Days 20–21",
                "focus": "Compliance engine",
                "order": "S17 §20 → G3 §20 → App C §5 and §20, and App D when Tier 2/3",
                "items": [
                    I("R4-D2021-01", "§20: security risk assessment, audit, and technical compliance.", "shall", refs=[("G3", "§20")]),
                    I("R4-D2021-02", "G3 Appendix D when the system is Tier 2 or Tier 3. Learn what is submitted; do not invent a filing.", "shall", refs=[("G3", "§20")], note="Applies when the tier is 2 or 3."),
                    I("R4-D2021-03", "App C §5: a Tier 3 security unit has at least one member with a recognised certification.", "shall", flag=True, refs=[("App C", "§5")]),
                ],
            },
        ],
    },
    {
        "n": "5",
        "title": "Management support (DITSO support)",
        "anchor": "G3 §5 and §7 themes",
        "quick": "A one-page B/D security governance map.",
        "effort": "About 45–60 minutes a day. Oversight fluency, not deep admin how-to.",
        "walk": "A management paper: draft tier inventory, top three risks, and an App C red/amber/green view.",
        "clusters": [
            {
                "days": "Days 8–9",
                "focus": "Accountability and governance",
                "order": "S17 §5 → G3 §5.2 → App C §5 for Tier 3",
                "items": [
                    I("R5-D89-01", "S17/G3 §5.2.1: what the DITSO is accountable for.", "shall", refs=[("S17", "§5"), ("G3", "§5")]),
                    I("R5-D89-02", "§5.2.2 information security steering committee.", "shall", refs=[("G3", "§5")]),
                    I("R5-D89-03", "App C §5: a B/D with Tier 3 systems shall have a steering committee, and at least one certified member in the security unit.", "shall", flag=True, refs=[("App C", "§5")]),
                ],
            },
            {
                "days": "Days 10–11",
                "focus": "Risk and classified protection",
                "order": "S17 §7 → G3 §7 → App B, and App C §7 for Tier 3",
                "items": [
                    I("R5-D1011-01", "§7 risk management and who owns the tier decision.", "shall", refs=[("G3", "§7")]),
                    I("R5-D1011-02", "Use G3 Appendix B as guidance when someone proposes a tier. You still confirm with the owner.", "should", refs=[("G3", "§7")]),
                    I("R5-D1011-03", "Tier 3 risk registers under App C §7: risks, likelihood, severity, mitigation, and monitoring.", "shall", flag=True, refs=[("App C", "§7")]),
                ],
            },
            {
                "days": "Days 12–13",
                "focus": "Policy and persons",
                "order": "S17 §8 → G3 §8, and S17 §9 → G3 §9 → App C §9 for Tier 3",
                "items": [
                    I("R5-D1213-01", "§8: is departmental policy current and aligned?", "shall", refs=[("G3", "§8")]),
                    I("R5-D1213-02", "§9 training and awareness coverage.", "shall", refs=[("G3", "§9")]),
                    I("R5-D1213-03", "App C §9: Tier 3 structured training, including vendors where feasible, or a contractual training duty.", "shall", flag=True, refs=[("App C", "§9")]),
                ],
            },
            {
                "days": "Days 14–15",
                "focus": "What good looks like",
                "order": "Executive skim of §11 and §14, plus App C",
                "items": [
                    I("R5-D1415-01", "Executive skim of §11 and §14 plus App C. Ask the unit for a red/amber/green view, not for packet captures.", "should", flag=True, refs=[("G3", "§11"), ("G3", "§14"), ("App C", "§14")]),
                ],
            },
            {
                "days": "Days 16–17",
                "focus": "Incident and continuity governance",
                "order": "S17 §18 → G3 §18, and S17 §19 → G3 §19",
                "items": [
                    I("R5-D1617-01", "§18 reporting path toward the Director and GIRO. Know who speaks externally.", "shall", refs=[("G3", "§18")]),
                    I("R5-D1617-02", "§19: plans are tested, not only filed.", "shall", refs=[("G3", "§19")]),
                ],
            },
            {
                "days": "Days 18–19",
                "focus": "Assurance",
                "order": "S17 §20 → G3 §20, and Appendix D for Tier 2/3",
                "items": [
                    I("R5-D1819-01", "§20 security risk assessment and audit cadence.", "shall", refs=[("G3", "§20")]),
                    I("R5-D1819-02", "Appendix D submissions for Tier 2 and Tier 3. Know that they exist and who files them.", "shall", refs=[("G3", "§20")]),
                ],
            },
            {
                "days": "Days 20–21",
                "focus": "Resource and culture",
                "order": "Close the oversight pass",
                "items": [
                    I("R5-D2021-01", "Check awareness coverage: who has not had the required training.", "should", refs=[("G3", "§9")]),
                    I("R5-D2021-02", "One decision to prepare: fund or fix the top residual risk. Bring evidence, not a slogan.", "should", refs=[("G3", "§7")]),
                ],
            },
        ],
    },
]

APPLY = [
    {
        "label": "Days 22–24",
        "title": "Map systems to a tier",
        "pace": "both",
        "items": [
            I("A-D22-01", "List the systems and services you own, administer, develop, or heavily use.", "shall"),
            I("A-D22-02", "Propose Tier 1, 2, or 3 using G3 §4.1 and Appendix B: impact, interdependency, and essential services.", "shall", refs=[("G3", "§4"), ("G3", "§7")]),
            I("A-D22-03", "Confirm the proposal with the Information Owner or the DITSO unit. Do not self-finalise Tier 2 or Tier 3.", "shall", refs=[("G3", "§7")]),
            I("A-D22-04", "Mark every Tier 2 or Tier 3 row: App C applies. Tier 3 includes every Tier 2 App C control, plus the Tier 3-only rows.", "shall", flag=True, refs=[("App C", "§4")]),
        ],
    },
    {
        "label": "Days 25–27",
        "title": "App C and local-policy gap pass",
        "pace": "both",
        "items": [
            I("A-D25-01", "If any system is Tier 2 or 3, walk G3 Appendix C for the sections you touch: §5, 7, 9, 11, 14, 16, 19, and 20.", "shall", flag=True, refs=[("App C", "§11")], note="Open the App C matrix."),
            I("A-D25-02", "Fill a gap table: Control, Evidence, Gap, Owner, Due.", "shall", refs=[("G3", "§20")], note="Use the gap template."),
            I("A-D25-03", "Re-read the local B/D policy and note any rule that is stricter than S17/G3.", "shall", refs=[("G3", "§8")]),
            I("A-D25-04", "Attach audit or security-risk-assessment finding identifiers you already have.", "should", "b-focus", note="Current staff"),
            I("A-D25-05", "If nothing is Tier 2 or 3: do the local-policy pass and a Tier 1 self-check on one system.", "shall"),
        ],
    },
    {
        "label": "Days 28–29",
        "title": "One walkthrough",
        "pace": "both",
        "items": [
            I("A-D28-01", "Document the steps and the artefacts you kept. An informal note is enough. This hub does not collect it.", "should"),
            I("A-D28-02", "Note any Shall you met and any Should you deferred, and why.", "shall"),
        ],
    },
    {
        "label": "Day 30",
        "title": "Close-out",
        "pace": "both",
        "items": [
            I("A-D30-01", "Optional: tick foundation, role, and apply self-progress, or note deferrals with dates.", "may", note="Self-ticks only."),
            I("A-D30-02", "Keep for yourself: the tier-list draft, the App C gap table if you have one, the walkthrough note, and the contacts from the reporting procedure.", "should"),
            I("A-D30-04", "Current staff: you may share the gap table with your line manager or security unit so remediation owners can be booked.", "may", "b-focus", note="Optional handoff. Not a mandatory acknowledgement."),
            I("A-D30-05", "Optional: skim one practice guide for your role on ITG InfoStation.", "may"),
        ],
    },
]
