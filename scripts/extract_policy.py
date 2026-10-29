#!/usr/bin/env python3
"""Extract S17 and G3 sections 1–20 for the hub Sections page.

The figure on G3 §2 is not turned into fake sentences. Everything else is the
PDF text, with running headers removed and wrapped lines joined.
"""

import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "policy_sections.json"

TITLES = {
    1: "Purpose",
    2: "Scope",
    3: "Normative references",
    4: "Definitions and conventions",
    5: "Organisation",
    6: "Core security principles",
    7: "Management responsibilities",
    8: "IT security policies",
    9: "Human resource security",
    10: "Asset management",
    11: "Access control",
    12: "Cryptography",
    13: "Physical and environmental security",
    14: "Operations security",
    15: "Communications security",
    16: "System acquisition, development and maintenance",
    17: "Outsourcing security",
    18: "Security incident management",
    19: "Continuity",
    20: "Compliance",
}

FIGURE_NOTE = (
    "G3 §2 contains a diagram titled “Security Considerations Related to "
    "Different Phases of System Development Life Cycle”. It maps lifecycle "
    "stages to security areas. That figure stays in the official PDF. It is "
    "not rewritten here as sentences."
)


def page_lines(text, figure=False):
    if figure:
        return ["[[FIGURE]]"]
    lines = text.splitlines()
    started = False
    out = []
    for line in lines:
        if not started:
            if re.search(r"Ref\.\s*No", line):
                started = True
            continue
        clean = re.sub(r"\s+", " ", line).strip()
        if re.fullmatch(r"\d{1,3}", clean):
            continue
        out.append(clean)
    return out


def parse_top(line):
    match = re.match(r"^(\d{1,2})(?:\.)?\s+(.+)$", line.strip())
    if not match:
        return None
    number = int(match.group(1))
    rest = match.group(2).strip()
    if not 1 <= number <= 21:
        return None
    if re.match(r"^\d", rest):
        return None
    letters = re.sub(r"[^A-Za-z]", "", rest)
    if not letters or letters != letters.upper():
        return None
    return number, rest


def caps_continuation(line):
    text = line.strip()
    if not text or parse_top(text) or re.match(r"^\d", text):
        return False
    letters = re.sub(r"[^A-Za-z]", "", text)
    return bool(letters) and letters == letters.upper() and len(text) < 90


def is_structural(line):
    if parse_top(line):
        return True
    if re.match(r"^\d+\.\d+(?:\.\d+)*\.?\s+\S", line):
        return True
    if re.match(r"^(?:\([A-Za-z0-9]+\)|[A-Za-z]\))\s+\S", line):
        return True
    if re.match(r"^[•▪●]\s*\S", line):
        return True
    return False


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def join_wrap(chunk, nxt):
    if chunk.endswith("-") and nxt[:1].islower():
        return chunk[:-1] + nxt
    return chunk + " " + nxt


def join_paragraphs(lines):
    blocks = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "":
            index += 1
            continue
        if line == "[[FIGURE]]":
            blocks.append(("note", FIGURE_NOTE))
            index += 1
            continue
        if is_structural(line):
            chunk = line
            index += 1
            while index < len(lines):
                nxt = lines[index]
                if not nxt or nxt == "[[FIGURE]]" or is_structural(nxt):
                    break
                chunk = join_wrap(chunk, nxt)
                index += 1
            blocks.append(squash(chunk))
            continue
        chunk = line
        index += 1
        while index < len(lines):
            nxt = lines[index]
            if not nxt or nxt == "[[FIGURE]]" or is_structural(nxt):
                break
            chunk = join_wrap(chunk, nxt)
            index += 1
        blocks.append(squash(chunk))
    return blocks


def extract(path, start, end, figure_indexes):
    reader = PdfReader(path)
    lines = []
    for index in range(start, end):
        text = reader.pages[index].extract_text() or ""
        lines.extend(page_lines(text, figure=index in figure_indexes))
        lines.append("")
    sections = {n: [] for n in range(1, 21)}
    current = None
    index = 0
    while index < len(lines):
        line = lines[index]
        top = parse_top(line) if line else None
        if top and top[0] <= 20:
            current = top[0]
            heading = line.strip()
            index += 1
            while index < len(lines) and caps_continuation(lines[index]):
                heading = heading.rstrip() + " " + lines[index].strip()
                index += 1
            sections[current].append(re.sub(r"\s+", " ", heading).strip())
            continue
        if top and top[0] > 20:
            break
        if current:
            sections[current].append(line)
        index += 1
    return {n: join_paragraphs(sections[n]) for n in range(1, 21)}


def main():
    s17 = extract("/Users/sec41/Downloads/S17_EN.pdf", 6, 45, set())
    g3 = extract("/Users/sec41/Downloads/G3_EN.pdf", 11, 133, {13})
    missing = []
    payload = []
    for number in range(1, 21):
        if len(s17[number]) < 2 or len(g3[number]) < 2:
            missing.append((number, len(s17[number]), len(g3[number])))
        payload.append(
            {
                "id": f"{number:02d}",
                "number": str(number),
                "title": TITLES[number],
                "s17": s17[number],
                "g3": g3[number],
            }
        )
    if missing:
        raise SystemExit(f"Short sections: {missing}")
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    for item in payload:
        s17_chars = sum(len(x if isinstance(x, str) else x[1]) for x in item["s17"])
        g3_chars = sum(len(x if isinstance(x, str) else x[1]) for x in item["g3"])
        print(f"§{item['number']:>2} {item['title']:<48} S17 {s17_chars:6}  G3 {g3_chars:6}")
        print("   S17:", item["s17"][0][:110])
        print("   G3:", item["g3"][0][:110])


if __name__ == "__main__":
    main()
