#!/usr/bin/env python3
"""
SmartResearch — Paper Scraper
Fetches research papers from ArXiv RSS feeds by topic.
Saves results to papers.json for downstream processing.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────
OUTPUT_FILE  = "data/papers.json"
MAX_RESULTS  = 20

TOPICS = {
    "1": {"name": "Machine Learning",     "query": "machine+learning"},
    "2": {"name": "Large Language Models","query": "large+language+models"},
    "3": {"name": "Computer Vision",      "query": "computer+vision"},
    "4": {"name": "Reinforcement Learning","query": "reinforcement+learning"},
    "5": {"name": "Transformers",         "query": "transformer+neural+network"},
}

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def fetch_arxiv(query: str, max_results: int = 20) -> list[dict]:
    """Fetch papers from ArXiv API."""
    base = "http://export.arxiv.org/api/query"
    url  = f"{base}?search_query=all:{query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

    print(f"  {DIM}Fetching from ArXiv...{RESET}", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartResearch/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
        print(f"{GREEN}✅{RESET}")
    except Exception as e:
        print(f"\033[91m❌ {e}{RESET}")
        return []

    ns   = "http://www.w3.org/2005/Atom"
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall(f"{{{ns}}}entry"):
        title   = (entry.findtext(f"{{{ns}}}title") or "").strip().replace("\n", " ")
        summary = (entry.findtext(f"{{{ns}}}summary") or "").strip().replace("\n", " ")
        link    = (entry.findtext(f"{{{ns}}}id") or "").strip()
        published = (entry.findtext(f"{{{ns}}}published") or "")[:10]

        authors = [
            a.findtext(f"{{{ns}}}name") or ""
            for a in entry.findall(f"{{{ns}}}author")
        ]

        # Extract categories
        categories = [
            c.get("term", "")
            for c in entry.findall("{http://arxiv.org/schemas/atom}primary_category")
        ]

        if title:
            papers.append({
                "id":         link.split("/")[-1],
                "title":      title,
                "summary":    summary[:500],
                "authors":    authors[:3],
                "link":       link,
                "published":  published,
                "categories": categories,
                "scraped_at": datetime.now().isoformat(),
            })

    return papers


def save_papers(papers: list[dict], topic_name: str):
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            existing = json.load(f)

    # Deduplicate by ID
    existing_ids = {p["id"] for p in existing}
    new_papers   = [p for p in papers if p["id"] not in existing_ids]

    for p in new_papers:
        p["topic"] = topic_name

    all_papers = existing + new_papers
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_papers, f, indent=2)

    return len(new_papers)


def main():
    print(f"\n{BOLD}{CYAN}{'═'*50}")
    print(f"  🔬 SmartResearch — Paper Scraper")
    print(f"{'═'*50}{RESET}\n")

    print(f"  {BOLD}Select a research topic:\n{RESET}")
    for k, v in TOPICS.items():
        print(f"  {CYAN}{k}{RESET}  {v['name']}")
    print(f"  {CYAN}6{RESET}  Scrape ALL topics\n")

    choice = input("  → ").strip()

    topics_to_fetch = []
    if choice == "6":
        topics_to_fetch = list(TOPICS.values())
    elif choice in TOPICS:
        topics_to_fetch = [TOPICS[choice]]
    else:
        print(f"\033[91m  Invalid choice.\033[0m\n")
        return

    total_new = 0
    for topic in topics_to_fetch:
        print(f"\n  {BOLD}Topic: {topic['name']}{RESET}")
        papers = fetch_arxiv(topic["query"], MAX_RESULTS)
        if papers:
            new = save_papers(papers, topic["name"])
            total_new += new
            print(f"  {GREEN}✅ {len(papers)} fetched, {new} new papers saved{RESET}")
        time.sleep(1)

    print(f"\n  {BOLD}✨ Done! {total_new} new papers saved to {OUTPUT_FILE}{RESET}")
    print(f"  {DIM}Run summarizer.py next to generate summaries.\n{RESET}")


if __name__ == "__main__":
    main()
