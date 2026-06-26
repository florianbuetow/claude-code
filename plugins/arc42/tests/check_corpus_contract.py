#!/usr/bin/env python3
"""Enforce the arc42 Corpus Derivation Contract (spec §8). Stdlib only."""
import argparse, pathlib, re, sys

VERBATIM_MIN_RUN = 8          # shared token run >= this many tokens => verbatim
VERBATIM_MAX_OVERLAP = 0.30   # token-overlap ratio > this => verbatim
SUPPORT_MIN_OVERLAP = 0.10    # grounding: a sampled statement should share >= this with its source

def tokens(text):
    return re.findall(r"[A-Za-z0-9]+", text.lower())

def enumerate_corpus(corpus_dir):
    root = pathlib.Path(corpus_dir)
    exts = {".md", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
    return {str(p.relative_to(root)) for p in root.rglob("*")
            if p.is_file() and p.suffix.lower() in exts and not p.name.startswith(".")}

def parse_coverage(path):
    """Lines like '`<src>` -> `<dest>`' or '`<src>` -> dropped: reason'. Returns {src: dest}."""
    mapping = {}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = re.search(r"`([^`]+)`\s*(?:->|→|=>)\s*(.+)", line)
        if m:
            mapping[m.group(1).strip()] = m.group(2).strip()
    return mapping

def max_ngram_overlap(derived, source):
    dt, st = tokens(derived), tokens(source)
    sset = set(st)
    overlap = (sum(1 for t in dt if t in sset) / len(dt)) if dt else 0.0
    # longest shared contiguous run
    longest, sjoined = 0, " ".join(st)
    i = 0
    while i < len(dt):
        j = i
        while j < len(dt) and " ".join(dt[i:j + 1]) in sjoined:
            j += 1
        longest = max(longest, j - i)
        i = max(i + 1, j)
    return longest, overlap

def source_files_of(text):
    out = []
    for line in text.splitlines():
        m = re.match(r"\s*Source:\s*(.+)", line)
        if m:
            out += [s.strip().strip("`") for s in re.split(r"[,\s]+", m.group(1)) if s.strip()]
    return out

def is_plugin_original(text):
    return re.search(r"^\s*Origin:\s*plugin-original", text, re.MULTILINE) is not None

def check(corpus, references, coverage_path):
    violations = []
    corpus_files = enumerate_corpus(corpus)
    cov = parse_coverage(coverage_path)
    # 1. 100% coverage accounting
    for src in sorted(corpus_files):
        if src not in cov:
            violations.append(f"coverage: corpus file not accounted for in COVERAGE.md: {src}")
    # 2/3. per derived reference file: Source: present, paths exist, not verbatim, grounded
    ref_root = pathlib.Path(references)
    for p in sorted(ref_root.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        if p.name == "COVERAGE.md" or is_plugin_original(text):
            continue
        srcs = source_files_of(text)
        if not srcs:
            violations.append(f"Source: line missing in arc42-derived file: {p}")
            continue
        for s in srcs:
            sp = pathlib.Path(corpus) / s
            if not sp.exists():
                violations.append(f"Source: cited path does not exist: {s} (in {p})")
                continue
            longest, overlap = max_ngram_overlap(text, sp.read_text(encoding="utf-8"))
            if longest >= VERBATIM_MIN_RUN and overlap > VERBATIM_MAX_OVERLAP:
                violations.append(f"verbatim: {p} shares a {longest}-token run / {overlap:.0%} overlap with {s}")
            if overlap < SUPPORT_MIN_OVERLAP:
                violations.append(f"grounding: {p} shows little support ({overlap:.0%}) from cited {s} — review")
    return violations

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--references", required=True)
    ap.add_argument("--coverage", required=True)
    a = ap.parse_args()
    v = check(a.corpus, a.references, a.coverage)
    if v:
        print("CORPUS CONTRACT FAILED:")
        for x in v:
            print("  -", x)
        sys.exit(1)
    print("Corpus contract OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
