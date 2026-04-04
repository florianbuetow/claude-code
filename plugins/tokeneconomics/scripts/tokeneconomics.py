#!/usr/bin/env python3
"""
tokeneconomics.py — Claude Code session token usage analyzer.

Analyzes per-message token usage data from session logs to flag waste
risks and cost optimization opportunities.

Usage:
  python3 tokeneconomics.py [--project <name>] [--all] [--days 30]
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
GAP_THRESHOLD = 15 * 60  # 15 minutes — same as logbook.py

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

# Anthropic API pricing per 1M tokens (used as relative cost proxy)
MODEL_PRICING = {
    "opus": {
        "input": 15.00,
        "cache_read": 1.50,
        "cache_creation": 18.75,
        "output": 75.00,
    },
    "sonnet": {
        "input": 3.00,
        "cache_read": 0.30,
        "cache_creation": 3.75,
        "output": 15.00,
    },
    "haiku": {
        "input": 0.80,
        "cache_read": 0.08,
        "cache_creation": 1.00,
        "output": 4.00,
    },
}


# ── Naming (from logbook.py) ─────────────────────────────────────────


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


# ── Path resolution ──────────────────────────────────────────────────


def project_dir_for(f):
    for parent in f.parents:
        if parent.parent == PROJECTS_DIR:
            return parent
    return None


def cwd_to_project_slug():
    """Convert current working directory to the project slug Claude Code uses."""
    cwd = os.getcwd()
    slug = cwd.replace("/", "-")
    if slug.startswith("-"):
        slug = slug[1:]
    return slug


# ── Timestamp parsing ────────────────────────────────────────────────


def parse_timestamp(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


# ── Model tier detection ─────────────────────────────────────────────


def model_tier(model_id):
    """Map a model ID string to a pricing tier key."""
    if not model_id:
        return "sonnet"
    m = model_id.lower()
    if "opus" in m:
        return "opus"
    if "haiku" in m:
        return "haiku"
    return "sonnet"


def pricing_for(model_id):
    """Get pricing dict for a model ID."""
    return MODEL_PRICING[model_tier(model_id)]


# ── Time helpers (from logbook.py) ───────────────────────────────────


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


# ── Record loading ───────────────────────────────────────────────────


def load_records(project_filter=None, days=30):
    """Load JSONL records, optionally filtered to a project and time window.

    Args:
        project_filter: canonical project name to filter to, or None for all
        days: number of days to look back (0 = no limit)

    Yields:
        dict with original fields plus _project, _branch, _is_subagent,
        _session_file, _session_id
    """
    cutoff = None
    if days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

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
        if project_filter and canon != project_filter:
            continue
        branch = branch_label(raw)
        is_sub = "subagent" in str(f)
        session_id = f.stem

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

                    # Time filter
                    if cutoff:
                        ts = parse_timestamp(obj.get("timestamp"))
                        if ts and ts < cutoff:
                            continue

                    obj["_project"] = canon
                    obj["_branch"] = branch
                    obj["_is_subagent"] = is_sub
                    obj["_session_file"] = str(f)
                    obj["_session_id"] = session_id
                    yield obj
        except Exception:
            continue


# ── Usage extraction ─────────────────────────────────────────────────


def extract_usage(record):
    """Extract token usage from an assistant message record.

    Returns dict with input, output, cache_read, cache_creation, model,
    cost, and total_context fields, or None if not an assistant message
    with usage data.
    """
    if record.get("type") != "assistant":
        return None
    msg = record.get("message", {})
    usage = msg.get("usage")
    if not usage:
        return None

    model = msg.get("model", "")
    prices = pricing_for(model)
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    total_context = inp + cache_read + cache_create

    cost = (
        inp * prices["input"] / 1_000_000
        + out * prices["output"] / 1_000_000
        + cache_read * prices["cache_read"] / 1_000_000
        + cache_create * prices["cache_creation"] / 1_000_000
    )

    return {
        "input": inp,
        "output": out,
        "cache_read": cache_read,
        "cache_creation": cache_create,
        "total_context": total_context,
        "model": model,
        "tier": model_tier(model),
        "cost": cost,
        "timestamp": record.get("timestamp"),
        "session_id": record.get("_session_id"),
        "project": record.get("_project"),
        "branch": record.get("_branch"),
        "is_subagent": record.get("_is_subagent"),
    }


# ── Analysis Dimensions ──────────────────────────────────────────────


def analyze_cost(usages):
    """Dimension 1: Cost breakdown by project and session."""
    by_project = defaultdict(lambda: {"cost": 0, "input": 0, "output": 0,
                                       "cache_read": 0, "cache_creation": 0,
                                       "sessions": set(), "count": 0})
    by_session = defaultdict(lambda: {"cost": 0, "input": 0, "output": 0,
                                       "cache_read": 0, "cache_creation": 0,
                                       "project": "", "count": 0})

    for u in usages:
        proj = u["project"]
        sid = u["session_id"]
        for key in ("cost", "input", "output", "cache_read", "cache_creation"):
            by_project[proj][key] += u[key]
            by_session[sid][key] += u[key]
        by_project[proj]["sessions"].add(sid)
        by_project[proj]["count"] += 1
        by_session[sid]["project"] = proj
        by_session[sid]["count"] += 1

    projects = []
    for name, d in sorted(by_project.items(), key=lambda x: x[1]["cost"], reverse=True):
        projects.append({
            "project": name,
            "cost": d["cost"],
            "input": d["input"],
            "output": d["output"],
            "cache_read": d["cache_read"],
            "cache_creation": d["cache_creation"],
            "sessions": len(d["sessions"]),
            "turns": d["count"],
        })

    sessions = []
    for sid, d in sorted(by_session.items(), key=lambda x: x[1]["cost"], reverse=True):
        sessions.append({
            "session_id": sid[:8],
            "project": d["project"],
            "cost": d["cost"],
            "input": d["input"],
            "output": d["output"],
            "turns": d["count"],
        })

    total_cost = sum(p["cost"] for p in projects)
    return {
        "total_cost": total_cost,
        "projects": projects,
        "top_sessions": sessions[:10],
    }


def analyze_cache(usages):
    """Dimension 2: Cache efficiency analysis."""
    by_project = defaultdict(lambda: {"cache_read": 0, "input": 0,
                                       "cache_creation": 0, "sessions": set()})
    by_session = defaultdict(lambda: {"cache_read": 0, "input": 0,
                                       "cache_creation": 0, "project": ""})

    for u in usages:
        proj = u["project"]
        sid = u["session_id"]
        for key in ("cache_read", "input", "cache_creation"):
            by_project[proj][key] += u[key]
            by_session[sid][key] += u[key]
        by_project[proj]["sessions"].add(sid)
        by_session[sid]["project"] = proj

    def hit_rate(d):
        total = d["cache_read"] + d["input"] + d["cache_creation"]
        if total == 0:
            return 0
        return d["cache_read"] / total

    projects = []
    for name, d in sorted(by_project.items(), key=lambda x: hit_rate(x[1])):
        projects.append({
            "project": name,
            "hit_rate": hit_rate(d),
            "cache_read": d["cache_read"],
            "input": d["input"],
            "cache_creation": d["cache_creation"],
            "sessions": len(d["sessions"]),
        })

    worst_sessions = []
    for sid, d in sorted(by_session.items(), key=lambda x: hit_rate(x[1])):
        total = d["cache_read"] + d["input"] + d["cache_creation"]
        if total < 1000:
            continue
        worst_sessions.append({
            "session_id": sid[:8],
            "project": d["project"],
            "hit_rate": hit_rate(d),
            "cache_read": d["cache_read"],
            "input": d["input"],
        })

    overall_read = sum(d["cache_read"] for d in by_project.values())
    overall_input = sum(d["input"] for d in by_project.values())
    overall_create = sum(d["cache_creation"] for d in by_project.values())
    overall_total = overall_read + overall_input + overall_create
    overall_rate = overall_read / overall_total if overall_total > 0 else 0

    return {
        "overall_hit_rate": overall_rate,
        "projects": projects,
        "worst_sessions": worst_sessions[:10],
    }


def analyze_sprawl(usages):
    """Dimension 3: Context window inflation / sprawl tax."""
    sessions = defaultdict(list)
    for u in usages:
        sessions[u["session_id"]].append(u)

    sprawl_results = []
    total_sprawl_tax = 0

    for sid, turns in sessions.items():
        turns.sort(key=lambda x: x["timestamp"] or "")
        if len(turns) < 2:
            continue

        first_context = turns[0]["total_context"]
        last_context = turns[-1]["total_context"]
        turn_count = len(turns)

        tax = 0
        if turn_count > 15:
            for t in turns[15:]:
                tax += t["total_context"]
            total_sprawl_tax += tax

        growth = last_context / first_context if first_context > 0 else 0

        if turn_count >= 10 or growth > 3:
            sprawl_results.append({
                "session_id": sid[:8],
                "project": turns[0]["project"],
                "turns": turn_count,
                "first_context": first_context,
                "last_context": last_context,
                "growth_ratio": growth,
                "sprawl_tax_tokens": tax,
            })

    sprawl_results.sort(key=lambda x: x["sprawl_tax_tokens"], reverse=True)

    all_turn_counts = [len(t) for t in sessions.values()]
    avg_turns = sum(all_turn_counts) / len(all_turn_counts) if all_turn_counts else 0
    sprawling = sum(1 for c in all_turn_counts if c > 15)

    return {
        "avg_turns_per_session": avg_turns,
        "sprawling_sessions": sprawling,
        "total_sessions": len(sessions),
        "total_sprawl_tax_tokens": total_sprawl_tax,
        "worst_sessions": sprawl_results[:10],
    }


def analyze_models(usages):
    """Dimension 4: Model selection analysis."""
    tier_counts = defaultdict(int)
    tier_costs = defaultdict(float)
    by_session = defaultdict(lambda: {"tiers": set(), "cost": 0, "project": ""})

    for u in usages:
        tier = u["tier"]
        tier_counts[tier] += 1
        tier_costs[tier] += u["cost"]
        by_session[u["session_id"]]["tiers"].add(tier)
        by_session[u["session_id"]]["cost"] += u["cost"]
        by_session[u["session_id"]]["project"] = u["project"]

    total = sum(tier_counts.values())
    mix = {}
    for tier in ("opus", "sonnet", "haiku"):
        count = tier_counts.get(tier, 0)
        mix[tier] = {
            "count": count,
            "pct": count / total * 100 if total > 0 else 0,
            "cost": tier_costs.get(tier, 0),
        }

    opus_only = []
    for sid, d in by_session.items():
        if d["tiers"] == {"opus"} and d["cost"] > 0.01:
            opus_only.append({
                "session_id": sid[:8],
                "project": d["project"],
                "cost": d["cost"],
            })
    opus_only.sort(key=lambda x: x["cost"], reverse=True)

    opus_total_cost = mix.get("opus", {}).get("cost", 0)
    potential_savings = opus_total_cost * 0.80 if len(opus_only) > 0 else 0

    return {
        "mix": mix,
        "total_turns": total,
        "opus_only_sessions": opus_only[:10],
        "potential_savings_from_tiering": potential_savings,
    }


def analyze_output_efficiency(usages):
    """Dimension 5: Output tokens vs input tokens ratio."""
    by_session = defaultdict(lambda: {"input_total": 0, "output_total": 0,
                                       "project": ""})

    for u in usages:
        sid = u["session_id"]
        by_session[sid]["input_total"] += u["total_context"]
        by_session[sid]["output_total"] += u["output"]
        by_session[sid]["project"] = u["project"]

    results = []
    for sid, d in by_session.items():
        if d["input_total"] < 1000:
            continue
        ratio = d["output_total"] / d["input_total"] if d["input_total"] > 0 else 0
        results.append({
            "session_id": sid[:8],
            "project": d["project"],
            "ratio": ratio,
            "input_total": d["input_total"],
            "output_total": d["output_total"],
        })

    results.sort(key=lambda x: x["ratio"])

    total_in = sum(d["input_total"] for d in by_session.values())
    total_out = sum(d["output_total"] for d in by_session.values())
    overall_ratio = total_out / total_in if total_in > 0 else 0

    return {
        "overall_ratio": overall_ratio,
        "least_efficient": results[:10],
        "most_efficient": results[-5:] if len(results) >= 5 else results,
    }


def analyze_session_patterns(usages, all_records):
    """Dimension 6: Session-level patterns (duration, burn rate, delegation)."""
    session_timestamps = defaultdict(list)
    session_projects = {}
    subagent_sessions = set()

    for rec in all_records:
        ts = parse_timestamp(rec.get("timestamp"))
        if ts is None:
            continue
        sid = rec.get("_session_id", "")
        session_timestamps[sid].append(ts)
        session_projects[sid] = rec.get("_project", "")
        if rec.get("_is_subagent"):
            subagent_sessions.add(sid)

    session_tokens = defaultdict(int)
    for u in usages:
        session_tokens[u["session_id"]] += u["total_context"] + u["output"]

    results = []
    for sid, timestamps in session_timestamps.items():
        secs = active_seconds(timestamps)
        if secs < 60:
            continue
        tokens = session_tokens.get(sid, 0)
        burn_rate = tokens / (secs / 60) if secs > 0 else 0
        results.append({
            "session_id": sid[:8],
            "project": session_projects.get(sid, ""),
            "active_minutes": secs / 60,
            "tokens": tokens,
            "burn_rate": burn_rate,
            "is_subagent": sid in subagent_sessions,
        })

    results.sort(key=lambda x: x["burn_rate"], reverse=True)

    total_sessions = len(session_timestamps)
    subagent_count = len(subagent_sessions)
    delegation_rate = subagent_count / total_sessions if total_sessions > 0 else 0

    avg_duration = 0
    if results:
        avg_duration = sum(r["active_minutes"] for r in results) / len(results)

    return {
        "total_sessions": total_sessions,
        "subagent_sessions": subagent_count,
        "delegation_rate": delegation_rate,
        "avg_duration_minutes": avg_duration,
        "hottest_sessions": results[:10],
    }


# ── Scoring ──────────────────────────────────────────────────────────

DIMENSION_WEIGHTS = {
    "cost": 0.25,
    "cache": 0.25,
    "sprawl": 0.20,
    "models": 0.15,
    "output_efficiency": 0.10,
    "patterns": 0.05,
}


def score_cost(analysis):
    daily = analysis["total_cost"] / 30 if analysis["total_cost"] > 0 else 0
    if daily < 1:
        return 5
    if daily < 5:
        return 4
    if daily < 15:
        return 3
    if daily < 50:
        return 2
    return 1


def score_cache(analysis):
    rate = analysis["overall_hit_rate"]
    if rate >= 0.70:
        return 5
    if rate >= 0.55:
        return 4
    if rate >= 0.40:
        return 3
    if rate >= 0.25:
        return 2
    return 1


def score_sprawl(analysis):
    avg = analysis["avg_turns_per_session"]
    pct_sprawl = (analysis["sprawling_sessions"] / analysis["total_sessions"] * 100
                  if analysis["total_sessions"] > 0 else 0)
    if avg <= 10 and pct_sprawl < 5:
        return 5
    if avg <= 15 and pct_sprawl < 15:
        return 4
    if avg <= 20 and pct_sprawl < 30:
        return 3
    if avg <= 30 and pct_sprawl < 50:
        return 2
    return 1


def score_models(analysis):
    mix = analysis["mix"]
    opus_pct = mix.get("opus", {}).get("pct", 0)
    tiers_used = sum(1 for t in ("opus", "sonnet", "haiku") if mix.get(t, {}).get("count", 0) > 0)
    if tiers_used >= 3 and opus_pct < 50:
        return 5
    if tiers_used >= 2 and opus_pct < 50:
        return 4
    if opus_pct < 70:
        return 3
    if opus_pct < 90:
        return 2
    return 1


def score_output_efficiency(analysis):
    ratio = analysis["overall_ratio"]
    if ratio >= 0.30:
        return 5
    if ratio >= 0.20:
        return 4
    if ratio >= 0.10:
        return 3
    if ratio >= 0.05:
        return 2
    return 1


def score_patterns(analysis):
    delegation = analysis["delegation_rate"]
    avg_dur = analysis["avg_duration_minutes"]
    if delegation > 0.15 and avg_dur < 30:
        return 5
    if delegation > 0.05 and avg_dur < 60:
        return 4
    if avg_dur < 90:
        return 3
    if avg_dur < 120:
        return 2
    return 1


def overall_grade(scores):
    weighted = sum(scores[dim] * DIMENSION_WEIGHTS[dim] for dim in DIMENSION_WEIGHTS)
    if weighted >= 4.5:
        grade = "A"
    elif weighted >= 3.5:
        grade = "B"
    elif weighted >= 2.5:
        grade = "C"
    elif weighted >= 1.5:
        grade = "D"
    else:
        grade = "F"
    return weighted, grade


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_cost(c):
    if c >= 100:
        return f"${c:,.0f}"
    if c >= 1:
        return f"${c:.2f}"
    return f"${c:.3f}"


def fmt_pct(p):
    v = p * 100
    if v == 0:
        return "0%"
    if v < 1:
        return f"{v:.1f}%"
    return f"{v:.0f}%"


# ── Report Generation ────────────────────────────────────────────────


def generate_report(cost, cache, sprawl, models, output_eff, patterns, scores, weighted, grade, scope, days):
    lines = []
    scope_label = scope if scope != "all" else "All Projects"
    lines.append(f"# Token Economics Report — {scope_label} — Last {days} Days")
    lines.append("")
    lines.append(f"## Efficiency Score: {grade} ({weighted:.1f}/5.0)")
    lines.append("")

    # Executive summary
    opus_pct = models["mix"].get("opus", {}).get("pct", 0)
    sonnet_pct = models["mix"].get("sonnet", {}).get("pct", 0)
    haiku_pct = models["mix"].get("haiku", {}).get("pct", 0)
    lines.append(f"Analyzed **{sprawl['total_sessions']} sessions** across "
                 f"**{len(cost['projects'])} project(s)**. "
                 f"Estimated total cost: **{fmt_cost(cost['total_cost'])}**. "
                 f"Cache hit rate: **{fmt_pct(cache['overall_hit_rate'])}**. "
                 f"Avg session length: **{sprawl['avg_turns_per_session']:.0f} turns**. "
                 f"Model mix: {opus_pct:.0f}% Opus, "
                 f"{sonnet_pct:.0f}% Sonnet, "
                 f"{haiku_pct:.0f}% Haiku.")
    lines.append("")

    # Dimension scores
    lines.append("## Dimension Scores")
    lines.append("")
    lines.append("| Dimension | Score | Weight | Status |")
    lines.append("|-----------|-------|--------|--------|")
    dim_labels = {
        "cost": "Cost", "cache": "Cache Efficiency", "sprawl": "Conversation Sprawl",
        "models": "Model Selection", "output_efficiency": "Output Efficiency",
        "patterns": "Session Patterns",
    }
    for dim, weight in DIMENSION_WEIGHTS.items():
        s = scores[dim]
        status = ["", "Critical", "Poor", "Fair", "Good", "Excellent"][s]
        bar = "+" * s + "-" * (5 - s)
        lines.append(f"| {dim_labels[dim]} | {bar} {s}/5 | {weight:.0%} | {status} |")
    lines.append("")

    # Top Risks
    risks = []
    if cache["overall_hit_rate"] < 0.50:
        waste = cost["total_cost"] * (1 - cache["overall_hit_rate"]) * 0.5
        risks.append(("Low cache hit rate (" + fmt_pct(cache["overall_hit_rate"]) + ")",
                       fmt_cost(waste) + " potential savings",
                       f"{len(cache['worst_sessions'])} sessions"))
    if sprawl["sprawling_sessions"] > 0:
        risks.append((f"Conversation sprawl ({sprawl['sprawling_sessions']} sessions >15 turns)",
                       fmt_tokens(sprawl["total_sprawl_tax_tokens"]) + " sprawl tax",
                       f"{sprawl['sprawling_sessions']} sessions"))
    if models["mix"].get("opus", {}).get("pct", 0) > 80:
        risks.append(("Opus over-selection (" + f"{opus_pct:.0f}%" + " of turns)",
                       fmt_cost(models["potential_savings_from_tiering"]) + " potential savings",
                       f"{len(models['opus_only_sessions'])} Opus-only sessions"))
    if output_eff["overall_ratio"] < 0.10:
        risks.append(("Low output efficiency (" + fmt_pct(output_eff["overall_ratio"]) + " output/input)",
                       "High context overhead", f"{len(output_eff['least_efficient'])} sessions"))

    if risks:
        lines.append("## Top Risks")
        lines.append("")
        lines.append("| # | Risk | Impact | Sessions |")
        lines.append("|---|------|--------|----------|")
        for i, (risk, impact, sessions) in enumerate(risks[:5], 1):
            lines.append(f"| {i} | {risk} | {impact} | {sessions} |")
        lines.append("")

    # Top Opportunities
    opps = []
    if sprawl["avg_turns_per_session"] > 15:
        opps.append(("Restart sessions at 15 turns",
                      fmt_tokens(sprawl["total_sprawl_tax_tokens"]) + " tokens/month", "Low"))
    if models["potential_savings_from_tiering"] > 0.10:
        opps.append(("Use Sonnet for routine tasks",
                      fmt_cost(models["potential_savings_from_tiering"]) + "/month", "Medium"))
    if cache["overall_hit_rate"] < 0.50:
        opps.append(("Improve prompt caching",
                      "Up to 90% discount on cached context", "Medium"))
    if patterns["delegation_rate"] < 0.05:
        opps.append(("Delegate to subagents for independent tasks",
                      "Parallel work + smaller context windows", "Medium"))

    if opps:
        lines.append("## Top Opportunities")
        lines.append("")
        lines.append("| # | Opportunity | Potential Savings | Effort |")
        lines.append("|---|------------|-------------------|--------|")
        for i, (opp, savings, effort) in enumerate(opps[:5], 1):
            lines.append(f"| {i} | {opp} | {savings} | {effort} |")
        lines.append("")

    # Cost Breakdown
    lines.append("## Cost Breakdown")
    lines.append("")
    if cost["projects"]:
        lines.append("| Project | Est. Cost | Input | Output | Cache Read | Sessions |")
        lines.append("|---------|-----------|-------|--------|------------|----------|")
        for p in cost["projects"][:15]:
            lines.append(f"| {p['project']} | {fmt_cost(p['cost'])} | "
                         f"{fmt_tokens(p['input'])} | {fmt_tokens(p['output'])} | "
                         f"{fmt_tokens(p['cache_read'])} | {p['sessions']} |")
        lines.append("")

    if cost["top_sessions"]:
        lines.append("**Most expensive sessions:**")
        lines.append("")
        lines.append("| Session | Project | Est. Cost | Turns |")
        lines.append("|---------|---------|-----------|-------|")
        for s in cost["top_sessions"][:5]:
            lines.append(f"| {s['session_id']} | {s['project']} | "
                         f"{fmt_cost(s['cost'])} | {s['turns']} |")
        lines.append("")

    # Cache Efficiency
    lines.append("## Cache Efficiency")
    lines.append("")
    lines.append(f"Overall cache hit rate: **{fmt_pct(cache['overall_hit_rate'])}**")
    lines.append("")
    if cache["projects"]:
        lines.append("| Project | Hit Rate | Cache Read | Non-Cached Input | Sessions |")
        lines.append("|---------|----------|------------|------------------|----------|")
        for p in cache["projects"][:15]:
            lines.append(f"| {p['project']} | {fmt_pct(p['hit_rate'])} | "
                         f"{fmt_tokens(p['cache_read'])} | {fmt_tokens(p['input'])} | "
                         f"{p['sessions']} |")
        lines.append("")

    # Context Inflation
    lines.append("## Context Inflation")
    lines.append("")
    lines.append(f"Average turns/session: **{sprawl['avg_turns_per_session']:.0f}** | "
                 f"Sprawling (>15 turns): **{sprawl['sprawling_sessions']}** / "
                 f"{sprawl['total_sessions']} sessions | "
                 f"Sprawl tax: **{fmt_tokens(sprawl['total_sprawl_tax_tokens'])}** tokens")
    lines.append("")
    if sprawl["worst_sessions"]:
        lines.append("**Worst sprawling sessions:**")
        lines.append("")
        lines.append("| Session | Project | Turns | Context Growth | Sprawl Tax |")
        lines.append("|---------|---------|-------|----------------|------------|")
        for s in sprawl["worst_sessions"][:5]:
            lines.append(f"| {s['session_id']} | {s['project']} | {s['turns']} | "
                         f"{s['growth_ratio']:.1f}x | {fmt_tokens(s['sprawl_tax_tokens'])} |")
        lines.append("")

    # Model Selection
    lines.append("## Model Selection")
    lines.append("")
    lines.append("| Tier | Turns | % of Total | Est. Cost |")
    lines.append("|------|-------|------------|-----------|")
    for tier in ("opus", "sonnet", "haiku"):
        m = models["mix"].get(tier, {"count": 0, "pct": 0, "cost": 0})
        lines.append(f"| {tier.title()} | {m['count']:,} | {m['pct']:.0f}% | {fmt_cost(m['cost'])} |")
    lines.append("")
    if models["opus_only_sessions"]:
        lines.append(f"**{len(models['opus_only_sessions'])} Opus-only sessions** "
                     f"(potential savings from tiering: {fmt_cost(models['potential_savings_from_tiering'])})")
        lines.append("")

    # Output Efficiency
    lines.append("## Output Efficiency")
    lines.append("")
    lines.append(f"Overall output/input ratio: **{fmt_pct(output_eff['overall_ratio'])}**")
    lines.append("")

    # Session Patterns
    lines.append("## Session Patterns")
    lines.append("")
    lines.append(f"Total sessions: **{patterns['total_sessions']}** | "
                 f"Subagent sessions: **{patterns['subagent_sessions']}** "
                 f"({fmt_pct(patterns['delegation_rate'])}) | "
                 f"Avg duration: **{patterns['avg_duration_minutes']:.0f} min**")
    lines.append("")

    # Advisory Checklist
    lines.append("## Advisory Checklist")
    lines.append("")
    lines.append("These items can't be measured from session logs but are high-impact:")
    lines.append("")
    lines.append("- [ ] **Plugin barnacle audit:** Run `/cost` or check active MCP servers — "
                 "disable unused connectors that add silent context overhead")
    lines.append("- [ ] **File ingestion:** Convert PDFs and images to Markdown before feeding "
                 "to the model (20x token savings)")
    lines.append("- [ ] **Search efficiency:** Use dedicated search tools (Perplexity via MCP) "
                 "instead of native browsing (10-50K tokens saved per search)")
    lines.append("- [ ] **Fresh starts:** Summarize progress and start new sessions rather than "
                 "continuing 30+ turn threads")
    lines.append("")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code session token usage for waste and optimization opportunities"
    )
    parser.add_argument("--project", type=str, default=None,
                        help="Canonical project name to analyze (default: infer from cwd)")
    parser.add_argument("--all", action="store_true",
                        help="Analyze all projects")
    parser.add_argument("--days", type=int, default=30,
                        help="Number of days to look back (default: 30)")
    parser.add_argument("--report", type=str, default=None,
                        help="Save report to this directory (in addition to stdout)")
    args = parser.parse_args()

    # Determine scope
    if args.all:
        project_filter = None
        scope = "all"
    elif args.project:
        project_filter = args.project
        scope = args.project
    else:
        slug = cwd_to_project_slug()
        project_filter = None
        scope = "current project"
        # Find the longest matching canonical name (most specific match)
        best_match = None
        best_len = 0
        for d in PROJECTS_DIR.iterdir():
            if not d.is_dir():
                continue
            dirname = d.name
            if dirname.startswith("-private-tmp"):
                continue
            raw = strip_prefix(dirname)
            canon = canonical_name(raw)
            if not canon:
                continue
            # The directory name (minus prefix) should match end of slug
            if slug.endswith(raw) or slug.endswith(canon):
                if len(canon) > best_len:
                    best_match = canon
                    best_len = len(canon)
        if best_match:
            project_filter = best_match
            scope = best_match
        if project_filter is None:
            print("Could not determine project from cwd. Use --project <name> or --all.",
                  file=sys.stderr)
            sys.exit(1)

    # Load and analyze
    all_records = list(load_records(project_filter=project_filter, days=args.days))
    usages = [u for r in all_records if (u := extract_usage(r))]

    if not usages:
        print(f"No usage data found for scope '{scope}' in last {args.days} days.",
              file=sys.stderr)
        sys.exit(1)

    cost = analyze_cost(usages)
    cache = analyze_cache(usages)
    sprawl_data = analyze_sprawl(usages)
    model = analyze_models(usages)
    output_eff = analyze_output_efficiency(usages)
    session_pat = analyze_session_patterns(usages, all_records)

    scores = {
        "cost": score_cost(cost),
        "cache": score_cache(cache),
        "sprawl": score_sprawl(sprawl_data),
        "models": score_models(model),
        "output_efficiency": score_output_efficiency(output_eff),
        "patterns": score_patterns(session_pat),
    }
    weighted, grade = overall_grade(scores)

    report = generate_report(cost, cache, sprawl_data, model, output_eff, session_pat,
                             scores, weighted, grade, scope, args.days)
    print(report)

    if args.report:
        out_dir = Path(args.report)
        out_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        fname = f"{date_str}-tokeneconomics-{scope.replace(' ', '-')}.md"
        path = out_dir / fname
        path.write_text(report)
        print(f"\nReport saved to: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
