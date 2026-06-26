#!/usr/bin/env python3
"""Validate a generated docs/arc42 tree (spec §10). Stdlib only."""
import pathlib, re, sys

REQUIRED_FM = ["arc42_section", "source_commit", "generated_at", "arc42_kb_version", "upstream_hash"]
SECTION_RE = re.compile(r"^\d{2}-.*\.md$")

def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None

def validate(tree):
    v = []
    root = pathlib.Path(tree)
    if not root.is_dir():
        return [f"not a directory: {tree}"]
    sections = sorted(p for p in root.glob("*.md") if SECTION_RE.match(p.name))
    nums = {p.name[:2] for p in sections}
    for n in [f"{i:02d}" for i in range(1, 13)]:
        if n not in nums:
            v.append(f"missing section file: {n}-*.md")
    for f in ["index.md", "_evidence.md", "_gaps.md"]:
        if not (root / f).exists():
            v.append(f"missing output file: {f}")
    for p in sections:
        text = p.read_text(encoding="utf-8")
        fm = front_matter(text)
        if fm is None:
            v.append(f"{p.name}: missing file-level front-matter")
        else:
            for k in REQUIRED_FM:
                if not re.search(rf"^{k}:", fm, re.M):
                    v.append(f"{p.name}: front-matter missing '{k}'")
        if "<!-- arc42-meta " not in text:
            v.append(f"{p.name}: no <!-- arc42-meta … --> block")
        # never-fabricate: any gap-human subsection must carry a GAP flag
        for meta in re.findall(r"<!-- arc42-meta ([^>]*)-->", text):
            if "provenance:gap-human" in meta and "<!-- GAP:human-input" not in text:
                v.append(f"{p.name}: gap-human provenance without a GAP:human-input flag (possible fabrication)")
        # mermaid fences balanced
        if text.count("```mermaid") and text.count("```mermaid") > text.count("```") // 2:
            v.append(f"{p.name}: unbalanced mermaid fences")
    return v

def main():
    if len(sys.argv) != 2:
        print("usage: validate_output.py <docs/arc42 dir>"); sys.exit(2)
    v = validate(sys.argv[1])
    if v:
        print("OUTPUT VALIDATION FAILED:")
        for x in v:
            print("  -", x)
        sys.exit(1)
    print("Output OK"); sys.exit(0)

if __name__ == "__main__":
    main()
