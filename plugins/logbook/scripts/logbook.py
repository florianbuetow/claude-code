#!/usr/bin/env python3
"""
logbook.py — Claude Code session log analyzer.

Generates monthly and yearly markdown reports for time and messages,
broken down per project with branches grouped under their parent.

Usage:
  python3 logbook.py time   [--year YYYY] [--month MM] [--out DIR]
  python3 logbook.py messages [--year YYYY] [--month MM] [--out DIR]
  python3 logbook.py time   --preview
  python3 logbook.py messages --preview
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_OUT_DIR = Path("docs/reports")
GAP_THRESHOLD = 15 * 60  # 15 minutes

EXCLUDED = ["yakshop"]

_COMMON_PREFIXES = [
    "-Users-flo-Developer-github-",
    "-Users-flo-Developer-private-",
    "-Users-flo-Projects-",
    "-Users-flo-Desktop-",
    "-Users-flo-",
    "-Volumes-2TB-",
    "-Volumes-4TB-",
]


# ── Naming ────────────────────────────────────────────────────────────

def strip_prefix(dirname):
    for prefix in _COMMON_PREFIXES:
        if dirname.startswith(prefix):
            return dirname[len(prefix):]
    return dirname.lstrip("-")


def canonical_name(name):
    """Collapse worktree variants to base project name."""
    if "--claude-worktrees-" in name:
        return name.split("--claude-worktrees-")[0]
    if "-git-" in name:
        return name.split("-git-")[0]
    if name.endswith("-git"):
        return name[:-4]
    return name


def branch_label(name):
    """Extract the branch portion from a worktree name, or 'main'."""
    if "--claude-worktrees-" in name:
        return name.split("--claude-worktrees-", 1)[1]
    if "-git-" in name:
        return name.split("-git-", 1)[1]
    return "main"


def is_excluded(name):
    return any(ex in name.lower() for ex in EXCLUDED)


# ── Path resolution ───────────────────────────────────────────────────

def project_dir_for(f):
    for parent in f.parents:
        if parent.parent == PROJECTS_DIR:
            return parent
    return None


# ── Parsing ───────────────────────────────────────────────────────────

def is_human_typed(obj):
    content = obj.get("message", {}).get("content", "")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        types = {item.get("type") for item in content if isinstance(item, dict)}
        return "text" in types and "tool_result" not in types
    return False


def parse_timestamp(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def load_all_records():
    """Yield (project_canonical, branch, record_dict) for every JSONL line."""
    for f in PROJECTS_DIR.rglob("*.jsonl"):
        proj_dir = project_dir_for(f)
        if proj_dir is None:
            continue
        dirname = proj_dir.name
        if dirname.startswith("-private-tmp"):
            continue
        raw = strip_prefix(dirname)
        canon = canonical_name(raw)
        if is_excluded(canon):
            continue
        branch = branch_label(raw)
        is_sub = "subagent" in str(f)

        try:
            with open(f) as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    obj["_project"] = canon
                    obj["_branch"] = branch
                    obj["_is_subagent"] = is_sub
                    obj["_session_file"] = str(f)
                    yield obj
        except Exception:
            continue


# ── Time analysis ─────────────────────────────────────────────────────

def active_seconds(timestamps):
    if len(timestamps) < 2:
        return 0
    timestamps = sorted(timestamps)
    total = 0
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if delta <= GAP_THRESHOLD:
            total += delta
    return total


def fmt_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m}m"


def analyze_time(records, year=None, month=None):
    """Build time data grouped by project → branch."""
    # project → branch → [timestamps]
    data = defaultdict(lambda: defaultdict(list))
    sessions = defaultdict(lambda: defaultdict(set))

    for rec in records:
        ts = parse_timestamp(rec.get("timestamp"))
        if ts is None:
            continue
        if year and ts.year != year:
            continue
        if month and ts.month != month:
            continue
        proj = rec["_project"]
        branch = rec["_branch"]
        data[proj][branch].append(ts)
        sessions[proj][branch].add(rec["_session_file"])

    results = []
    for proj, branches in data.items():
        all_ts = []
        branch_rows = []
        for branch, timestamps in sorted(branches.items()):
            secs = active_seconds(timestamps)
            all_ts.extend(timestamps)
            branch_rows.append({
                "branch": branch,
                "seconds": secs,
                "sessions": len(sessions[proj][branch]),
            })
        proj_secs = active_seconds(all_ts)
        branch_rows.sort(key=lambda x: x["seconds"], reverse=True)
        results.append({
            "project": proj,
            "seconds": proj_secs,
            "sessions": sum(b["sessions"] for b in branch_rows),
            "branches": branch_rows,
        })

    results.sort(key=lambda x: x["seconds"], reverse=True)
    return results


# ── Message analysis ──────────────────────────────────────────────────

def _new_msg_bucket():
    return {"human": 0, "user_turns": 0, "assistant": 0, "sessions": set()}


def analyze_messages(records, year=None, month=None):
    """Build message data grouped by project → branch."""
    data = defaultdict(lambda: defaultdict(_new_msg_bucket))

    for rec in records:
        ts = parse_timestamp(rec.get("timestamp"))
        if ts is None:
            continue
        if year and ts.year != year:
            continue
        if month and ts.month != month:
            continue
        proj = rec["_project"]
        branch = rec["_branch"]
        t = rec.get("type")
        entry = data[proj][branch]
        entry["sessions"].add(rec["_session_file"])
        if t == "user":
            entry["user_turns"] += 1
            if is_human_typed(rec):
                entry["human"] += 1
        elif t == "assistant":
            entry["assistant"] += 1

    results = []
    for proj, branches in data.items():
        branch_rows = []
        total_human = total_user = total_asst = 0
        all_sessions = set()
        for branch, d in sorted(branches.items()):
            sess = d["sessions"]
            branch_rows.append({
                "branch": branch,
                "human": d["human"],
                "user_turns": d["user_turns"],
                "assistant": d["assistant"],
                "sessions": len(sess),
            })
            total_human += d["human"]
            total_user += d["user_turns"]
            total_asst += d["assistant"]
            all_sessions |= sess
        branch_rows.sort(key=lambda x: x["assistant"], reverse=True)
        results.append({
            "project": proj,
            "human": total_human,
            "user_turns": total_user,
            "assistant": total_asst,
            "sessions": len(all_sessions),
            "branches": branch_rows,
        })

    results.sort(key=lambda x: x["assistant"], reverse=True)
    return results


# ── Report generation ─────────────────────────────────────────────────

def period_label(year, month):
    if month:
        return f"{datetime(year, month, 1):%B %Y}"
    if year:
        return str(year)
    return "All-Time"


def report_filename(mode, year, month):
    if month:
        return f"{year}{month:02d}-logbook-{mode}.md"
    if year:
        return f"{year}-logbook-{mode}.md"
    return f"logbook-{mode}.md"


def generate_time_report(results, year, month):
    label = period_label(year, month)
    total_secs = sum(r["seconds"] for r in results)
    total_sessions = sum(r["sessions"] for r in results)
    lines = [
        f"# Time Report — {label}",
        "",
        "## Summary",
        "",
        f"- **Total active time:** {fmt_duration(total_secs)}",
        f"- **Projects active:** {len(results)}",
        f"- **Sessions:** {total_sessions}",
        "",
        "## Top 10 Projects",
        "",
        "| Project | Time |",
        "|---------|------|",
    ]
    for r in results[:10]:
        lines.append(f"| {r['project']} | {fmt_duration(r['seconds'])} |")

    lines += ["", "## Detailed Breakdown", ""]

    for r in results:
        if r["seconds"] < 60:
            continue
        lines.append(f"### {r['project']} ({fmt_duration(r['seconds'])})")
        lines.append("")
        if len(r["branches"]) > 1:
            lines.append("| Branch | Time | Sessions |")
            lines.append("|--------|------|----------|")
            for b in r["branches"]:
                if b["seconds"] < 60:
                    continue
                lines.append(f"| {b['branch']} | {fmt_duration(b['seconds'])} | {b['sessions']} |")
            lines.append("")
        else:
            lines.append(f"- Sessions: {r['sessions']}")
            lines.append("")

    return "\n".join(lines)


def generate_messages_report(results, year, month):
    label = period_label(year, month)
    total_human = sum(r["human"] for r in results)
    total_asst = sum(r["assistant"] for r in results)
    total_sessions = sum(r["sessions"] for r in results)
    lines = [
        f"# Messages Report — {label}",
        "",
        "## Summary",
        "",
        f"- **Your messages:** {total_human:,}",
        f"- **Agent messages:** {total_asst:,}",
        f"- **Sessions:** {total_sessions:,}",
        "",
        "## Top 10 Projects",
        "",
        "| Project | You | Agent | Sessions |",
        "|---------|-----|-------|----------|",
    ]
    for r in results[:10]:
        lines.append(f"| {r['project']} | {r['human']:,} | {r['assistant']:,} | {r['sessions']} |")

    lines += ["", "## Detailed Breakdown", ""]

    for r in results:
        if r["assistant"] == 0:
            continue
        lines.append(f"### {r['project']} ({r['human']:,} you / {r['assistant']:,} agent)")
        lines.append("")
        if len(r["branches"]) > 1:
            lines.append("| Branch | You | Agent | Sessions |")
            lines.append("|--------|-----|-------|----------|")
            for b in r["branches"]:
                if b["assistant"] == 0:
                    continue
                lines.append(f"| {b['branch']} | {b['human']:,} | {b['assistant']:,} | {b['sessions']} |")
            lines.append("")
        else:
            lines.append(f"- Sessions: {r['sessions']}")
            lines.append("")

    return "\n".join(lines)


# ── Preview (top 10 inline) ──────────────────────────────────────────

def preview_time(results):
    lines = [
        "",
        "Top 10 projects by time:",
        "",
        "| Project | Time |",
        "|---------|------|",
    ]
    for r in results[:10]:
        lines.append(f"| {r['project']} | {fmt_duration(r['seconds'])} |")
    total = sum(r["seconds"] for r in results)
    lines.append(f"| **TOTAL** | **{fmt_duration(total)}** |")
    return "\n".join(lines)


def preview_messages(results):
    lines = [
        "",
        "Top 10 projects by messages:",
        "",
        "| Project | You | Agent | Sessions |",
        "|---------|-----|-------|----------|",
    ]
    for r in results[:10]:
        lines.append(f"| {r['project']} | {r['human']:,} | {r['assistant']:,} | {r['sessions']} |")
    total_h = sum(r["human"] for r in results)
    total_a = sum(r["assistant"] for r in results)
    total_s = sum(r["sessions"] for r in results)
    lines.append(f"| **TOTAL** | **{total_h:,}** | **{total_a:,}** | **{total_s:,}** |")
    return "\n".join(lines)


# ── File output ───────────────────────────────────────────────────────

def write_reports(mode, records, out_dir, year_filter=None, month_filter=None):
    """Generate monthly + yearly files. Returns list of written paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    # Collect all (year, month) pairs present in data
    periods = set()
    for rec in records:
        ts = parse_timestamp(rec.get("timestamp"))
        if ts is None:
            continue
        if year_filter and ts.year != year_filter:
            continue
        if month_filter and ts.month != month_filter:
            continue
        periods.add((ts.year, ts.month))

    years = {y for y, _ in periods}

    # Monthly reports
    for y, m in sorted(periods):
        if mode == "time":
            results = analyze_time(records, year=y, month=m)
            content = generate_time_report(results, y, m)
        else:
            results = analyze_messages(records, year=y, month=m)
            content = generate_messages_report(results, y, m)
        fname = report_filename(mode, y, m)
        path = out_dir / fname
        path.write_text(content)
        written.append(path)

    # Yearly reports
    for y in sorted(years):
        if mode == "time":
            results = analyze_time(records, year=y)
            content = generate_time_report(results, y, None)
        else:
            results = analyze_messages(records, year=y)
            content = generate_messages_report(results, y, None)
        fname = report_filename(mode, y, None)
        path = out_dir / fname
        path.write_text(content)
        written.append(path)

    return written


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Claude Code logbook report generator")
    parser.add_argument("mode", choices=["time", "messages"], help="Report type")
    parser.add_argument("--year", type=int, help="Filter to specific year")
    parser.add_argument("--month", type=int, help="Filter to specific month (requires --year)")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory for reports")
    parser.add_argument("--preview", action="store_true", help="Print top-10 table only, no files")
    args = parser.parse_args()

    if args.month and not args.year:
        parser.error("--month requires --year")

    records = list(load_all_records())

    if args.preview:
        if args.mode == "time":
            results = analyze_time(records, year=args.year, month=args.month)
            print(preview_time(results))
        else:
            results = analyze_messages(records, year=args.year, month=args.month)
            print(preview_messages(results))
        return

    written = write_reports(args.mode, records, args.out,
                            year_filter=args.year, month_filter=args.month)
    # Print preview + file list
    if args.mode == "time":
        results = analyze_time(records, year=args.year, month=args.month)
        print(preview_time(results))
    else:
        results = analyze_messages(records, year=args.year, month=args.month)
        print(preview_messages(results))

    print(f"\nGenerated {len(written)} report(s):")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
