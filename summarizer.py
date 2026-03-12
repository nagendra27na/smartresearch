#!/usr/bin/env python3
"""
SmartResearch — Summarizer
Reads papers.json and generates keyword summaries,
topic clusters, and saves a summary report.
"""

import json
import os
import re
from collections import Counter
from datetime import datetime

OUTPUT_SUMMARY = "data/summary_report.json"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","this","that","these","those","we",
    "our","their","which","from","by","as","it","its","into","also","can",
    "have","has","been","not","more","using","based","paper","show","shows",
    "proposed","method","model","models","data","results","approach","new",
    "used","use","two","one","three","first","second","both","each","all",
}


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    return [w for w, _ in Counter(filtered).most_common(top_n)]


def summarize_papers(papers: list[dict]) -> dict:
    topic_groups = {}
    all_keywords = []

    for p in papers:
        topic = p.get("topic", "General")
        topic_groups.setdefault(topic, []).append(p)

        kw = extract_keywords(p["title"] + " " + p["summary"])
        all_keywords.extend(kw)
        p["keywords"] = kw

    top_global_keywords = [w for w, _ in Counter(all_keywords).most_common(20)]

    topic_summaries = {}
    for topic, group in topic_groups.items():
        topic_kw = []
        for p in group:
            topic_kw.extend(p.get("keywords", []))
        topic_summaries[topic] = {
            "count":    len(group),
            "keywords": [w for w, _ in Counter(topic_kw).most_common(10)],
            "latest":   sorted(group, key=lambda x: x.get("published",""), reverse=True)[:3],
        }

    return {
        "generated_at":      datetime.now().isoformat(),
        "total_papers":      len(papers),
        "total_topics":      len(topic_groups),
        "top_keywords":      top_global_keywords,
        "topic_summaries":   topic_summaries,
    }


def print_report(report: dict):
    print(f"\n{BOLD}{CYAN}{'═'*50}")
    print(f"  📊 Research Summary Report")
    print(f"{'═'*50}{RESET}\n")
    print(f"  {BOLD}Total Papers:{RESET}  {report['total_papers']}")
    print(f"  {BOLD}Topics:{RESET}        {report['total_topics']}")
    print(f"  {BOLD}Top Keywords:{RESET}")
    print(f"  {DIM}{', '.join(report['top_keywords'][:10])}{RESET}\n")

    for topic, data in report["topic_summaries"].items():
        print(f"  {CYAN}{topic}{RESET} ({data['count']} papers)")
        print(f"  {DIM}Keywords: {', '.join(data['keywords'][:5])}{RESET}")
        for p in data["latest"]:
            print(f"    • {p['title'][:70]}...")
        print()


def main():
    print(f"\n{BOLD}{CYAN}  🔬 SmartResearch — Summarizer{RESET}\n")

    if not os.path.exists("data/papers.json"):
        print(f"  \033[91m❌ No papers.json found. Run scraper.py first.\033[0m\n")
        return

    with open("data/papers.json") as f:
        papers = json.load(f)

    print(f"  {DIM}Analysing {len(papers)} papers...{RESET}\n")
    report = summarize_papers(papers)

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_SUMMARY, "w") as f:
        json.dump(report, f, indent=2)

    # Also update papers.json with keywords
    with open("data/papers.json", "w") as f:
        json.dump(papers, f, indent=2)

    print_report(report)
    print(f"  {GREEN}✅ Summary saved to {OUTPUT_SUMMARY}{RESET}")
    print(f"  {DIM}Open dashboard/index.html to explore results.\n{RESET}")


if __name__ == "__main__":
    main()
