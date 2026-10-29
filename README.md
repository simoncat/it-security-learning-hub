# HKSARG IT Security Learning Hub

Static learning aid for bureau and department staff. Content is aligned to Baseline IT Security Policy [S17] v8.2 and IT Security Guidelines [G3] v10.2 (Digital Policy Office, April 2025). Those versions are marked assumed when the PDFs were not re-checked for the build.

The hub has four cores: decision aids, quizzes, enquiry Q&A, and source lookup. New joiners move from fundamentals to framework and accountability. Current staff filter by role, life-cycle stage, and need. A spine shows CIA, then S17, G3, and departmental policy, then nine life-cycle stages.

It does not log anyone in, track completion on a server, or collect a signature.

## Open it

From this folder:

```bash
python3 -m http.server 8080 --directory hub
```

Then open http://localhost:8080

Or open `hub/index.html` directly. Links are relative. Core journeys do not call a network API. Core text uses the system font stack.

## What is in v0.1-MVP

- Home, spine, new-joiners path, and current-staff filters
- Decision aids with relevance, applicability, modality, and a section cite
- Quizzes with a local score, rationale, and reset
- Placeholder enquiry packs, marked as departmental records still to be supplied
- S17 and G3 section pages, plus an Appendix C map
- Role paths, nine stage packs, cheat sheets, and walkthroughs
- Who-to-call card and gap template

Optional ticks are stored in `localStorage` for that page. They are disposable and are not a sign-off.

## Editing

Decision aids live in `scripts/content_decisions.py`. Enquiry packs are in `scripts/content_qa.py`. Stage packs are in `scripts/content_sdlc.py`. Quizzes are in `scripts/content_quizzes.py`. Regenerate with:

```bash
python3 scripts/render.py
```

Cite sections. Do not invent clause numbers. Core 4 repeats section text already extracted from the official PDFs; curated pages stay the way in.

## Authority

Learning aid only. Authoritative text remains S17, G3, the Security Regulations, and local B/D policy.
