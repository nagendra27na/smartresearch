# 🔬 SmartResearch — Research Intelligence Platform

> A multi-language research intelligence tool that scrapes ArXiv papers, analyzes keyword trends, ranks papers by relevance, and visualizes everything in a live dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Java](https://img.shields.io/badge/Java-17+-orange?style=flat-square&logo=openjdk)
![C++](https://img.shields.io/badge/C++-17-blue?style=flat-square&logo=cplusplus)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=flat-square&logo=javascript)
![HTML](https://img.shields.io/badge/HTML5-Dashboard-red?style=flat-square&logo=html5)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🏗️ Architecture

```
smartresearch/
├── src/
│   ├── python/
│   │   ├── scraper.py          # Fetch papers from ArXiv
│   │   ├── summarizer.py       # Extract keywords & summaries
│   │   └── trend_analyzer.py  # Detect rising research trends
│   ├── java/
│   │   └── PaperRanker.java   # Score & rank papers by relevance
│   └── cpp/
│       └── keyword_engine.cpp # High-performance keyword co-occurrence
├── dashboard/
│   └── index.html             # Interactive research dashboard
├── data/                      # Generated JSON files
└── docs/
    └── RESEARCH_NOTES.md
```

---

## ✨ Features

| Module | Language | What it does |
|--------|----------|-------------|
| `scraper.py` | Python | Fetches papers from ArXiv API by topic |
| `summarizer.py` | Python | Extracts keywords, groups by topic |
| `trend_analyzer.py` | Python | Detects rising keywords & trends over time |
| `PaperRanker.java` | Java | Scores each paper by relevance (0–10) |
| `keyword_engine.cpp` | C++ | Fast keyword frequency + co-occurrence matrix |
| `dashboard/index.html` | JS + HTML | Live interactive dashboard |

---

## 🚀 Quick Start

### Step 1 — Scrape papers
```bash
cd src/python
python scraper.py
# Choose a topic (ML, LLMs, CV, RL, Transformers)
# → saves data/papers.json
```

### Step 2 — Summarize & extract keywords
```bash
python summarizer.py
# → saves data/summary_report.json
```

### Step 3 — Analyze trends
```bash
python trend_analyzer.py
# → saves data/trends.json
```

### Step 4 — Rank papers (Java)
```bash
cd src/java
javac PaperRanker.java
java PaperRanker
# → saves data/ranked_papers.json
```

### Step 5 — Keyword engine (C++)
```bash
cd src/cpp
g++ -o keyword_engine keyword_engine.cpp -std=c++17
./keyword_engine
# → saves data/keywords.json
```

### Step 6 — Open dashboard
```bash
open dashboard/index.html
# Click "Load Data Files" and select all JSON files from data/
```

---

## 📊 Dashboard

The HTML dashboard visualizes:
- 📊 **Keyword frequency** bar charts
- 🍩 **Topic distribution** donut chart
- 🔥 **Rising keywords** with delta indicators
- 📅 **Papers per month** timeline
- 🏆 **Ranked papers** table with search

---

## 📡 Data Sources

- [ArXiv.org](https://arxiv.org) — free preprint research papers
- No API key needed — uses the public ArXiv API

---

## ⭐ Star This Repo

If this helped your research workflow — a ⭐ goes a long way!

## 📄 License

MIT — free to use, modify, and share.
