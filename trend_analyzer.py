#!/usr/bin/env python3
"""
SmartResearch — Trend Analyzer
Analyzes keyword frequency over time, detects rising topics,
and saves trend data for the dashboard.
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime

TREND_FILE = "data/trends.json"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def analyze_trends(papers: list[dict]) -> dict:
    # Group papers by month
    monthly = defaultdict(list)
    for p in papers:
        month = p.get("published", "")[:7]  # YYYY-MM
        if month:
            monthly[month].append(p)

    # Keyword frequency per month
    monthly_keywords = {}
    for month, group in sorted(monthly.items()):
        kw_list = []
        for p in group:
            kw_list.extend(p.get("keywords", []))
        monthly_keywords[month] = dict(Counter(kw_list).most_common(15))

    # All-time top keywords
    all_kw = []
    for p in papers:
        all_kw.extend(p.get("keywords", []))
    top_keywords = dict(Counter(all_kw).most_common(20))

    # Rising keywords (appeared more in recent months)
    months = sorted(monthly_keywords.keys())
    rising = {}
    if len(months) >= 2:
        recent = months[-1]
        older  = months[-2]
        for kw, count in monthly_keywords.get(recent, {}).items():
            old_count = monthly_keywords.get(older, {}).get(kw, 0)
            if count > old_count:
                rising[kw] = {"recent": count, "previous": old_count, "delta": count - old_count}

    # Papers per month
    papers_per_month = {m: len(g) for m, g in sorted(monthly.items())}

    # Topic distribution
    topic_dist = Counter(p.get("topic", "General") for p in papers)

    return {
        "generated_at":      datetime.now().isoformat(),
        "total_papers":      len(papers),
        "months_covered":    len(monthly),
        "top_keywords":      top_keywords,
        "rising_keywords":   dict(sorted(rising.items(), key=lambda x: x[1]["delta"], reverse=True)[:10]),
        "monthly_keywords":  monthly_keywords,
        "papers_per_month":  papers_per_month,
        "topic_distribution": dict(topic_dist),
    }


def print_trends(trends: dict):
    print(f"\n{BOLD}{CYAN}{'═'*50}")
    print(f"  📈 Research Trend Analysis")
    print(f"{'═'*50}{RESET}\n")
    print(f"  {BOLD}Papers Analysed:{RESET} {trends['total_papers']}")
    print(f"  {BOLD}Months Covered:{RESET}  {trends['months_covered']}\n")

    print(f"  {BOLD}{CYAN}🔥 Rising Keywords{RESET}")
    for kw, data in list(trends["rising_keywords"].items())[:8]:
        delta = data["delta"]
        bar   = "▲" * min(delta, 10)
        print(f"  {GREEN}{bar}{RESET} {kw:<20} {DIM}+{delta} mentions{RESET}")

    print(f"\n  {BOLD}{CYAN}📊 Topic Distribution{RESET}")
    total = sum(trends["topic_distribution"].values())
    for topic, count in sorted(trends["topic_distribution"].items(), key=lambda x: -x[1]):
        pct  = round(count / total * 100)
        bar  = "█" * (pct // 5)
        print(f"  {CYAN}{bar:<20}{RESET} {topic:<25} {DIM}{count} papers ({pct}%){RESET}")
    print()


def main():
    print(f"\n{BOLD}{CYAN}  📈 SmartResearch — Trend Analyzer{RESET}\n")

    if not os.path.exists("data/papers.json"):
        print(f"  \033[91m❌ Run scraper.py then summarizer.py first.\033[0m\n")
        return

    with open("data/papers.json") as f:
        papers = json.load(f)

    print(f"  {DIM}Analyzing trends in {len(papers)} papers...{RESET}\n")
    trends = analyze_trends(papers)

    os.makedirs("data", exist_ok=True)
    with open(TREND_FILE, "w") as f:
        json.dump(trends, f, indent=2)

    print_trends(trends)
    print(f"  {GREEN}✅ Trend data saved to {TREND_FILE}{RESET}")
    print(f"  {DIM}Open dashboard/index.html to visualize.\n{RESET}")


if __name__ == "__main__":
    main()
