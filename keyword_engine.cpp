/*
 * SmartResearch — Keyword Frequency Engine (C++)
 * High-performance keyword extraction and co-occurrence matrix
 * from the scraped papers dataset.
 *
 * Compile: g++ -o keyword_engine keyword_engine.cpp -std=c++17
 * Run:     ./keyword_engine
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <regex>
#include <iomanip>

using namespace std;

const string GREEN  = "\033[92m";
const string CYAN   = "\033[96m";
const string YELLOW = "\033[93m";
const string RED    = "\033[91m";
const string BOLD   = "\033[1m";
const string DIM    = "\033[2m";
const string RESET  = "\033[0m";

// ─── STOPWORDS ────────────────────────────────────────────
const set<string> STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","this","that","these","those","we",
    "our","their","which","from","by","as","it","its","into","also","can",
    "have","has","not","more","using","based","paper","show","shows","model",
    "models","data","results","approach","new","used","use","two","one","all",
    "each","both","such","than","then","than","when","where","while","though"
};

// ─── TEXT PROCESSING ──────────────────────────────────────
string toLower(string s) {
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

vector<string> tokenize(const string& text) {
    vector<string> tokens;
    regex word_re("[a-z]{4,}");
    string lower = toLower(text);
    auto begin = sregex_iterator(lower.begin(), lower.end(), word_re);
    auto end   = sregex_iterator();
    for (auto it = begin; it != end; ++it) {
        string w = it->str();
        if (STOPWORDS.find(w) == STOPWORDS.end()) {
            tokens.push_back(w);
        }
    }
    return tokens;
}

// ─── EXTRACT TEXT FROM JSON ───────────────────────────────
string extractBetween(const string& s, const string& key) {
    string pattern = "\"" + key + "\": \"";
    size_t start = s.find(pattern);
    if (start == string::npos) return "";
    start += pattern.size();
    size_t end = s.find("\"", start);
    while (end != string::npos && s[end-1] == '\\') end = s.find("\"", end+1);
    if (end == string::npos) return "";
    return s.substr(start, end - start);
}

vector<string> extractAllTexts(const string& json) {
    vector<string> texts;
    size_t pos = 0;
    while ((pos = json.find("\"title\":", pos)) != string::npos) {
        string title   = extractBetween(json.substr(pos), "title");
        size_t sum_pos = json.find("\"summary\":", pos);
        string summary = (sum_pos != string::npos) ? extractBetween(json.substr(sum_pos), "summary") : "";
        if (!title.empty()) texts.push_back(title + " " + summary);
        pos++;
    }
    return texts;
}

// ─── MAIN ANALYSIS ────────────────────────────────────────
int main() {
    cout << "\n" << BOLD << CYAN
         << "  🔠 SmartResearch — Keyword Engine (C++)\n" << RESET << "\n";

    // Read papers
    ifstream file("data/papers.json");
    if (!file.is_open()) {
        cout << RED << "  ❌ data/papers.json not found. Run scraper.py first.\n" << RESET;
        return 1;
    }

    stringstream buffer;
    buffer << file.rdbuf();
    string json = buffer.str();
    file.close();

    cout << DIM << "  Parsing papers...\n" << RESET;
    vector<string> texts = extractAllTexts(json);
    cout << GREEN << "  ✅ " << texts.size() << " papers loaded\n\n" << RESET;

    // Count keyword frequency
    map<string, int> freq;
    map<pair<string,string>, int> cooccur;

    for (const auto& text : texts) {
        vector<string> tokens = tokenize(text);

        for (const auto& t : tokens) freq[t]++;

        // Co-occurrence (within same paper)
        set<string> unique(tokens.begin(), tokens.end());
        vector<string> uv(unique.begin(), unique.end());
        for (size_t i = 0; i < uv.size(); i++) {
            for (size_t j = i+1; j < uv.size() && j < i+5; j++) {
                auto key = make_pair(uv[i], uv[j]);
                cooccur[key]++;
            }
        }
    }

    // Sort by frequency
    vector<pair<string,int>> sorted_freq(freq.begin(), freq.end());
    sort(sorted_freq.begin(), sorted_freq.end(),
         [](const auto& a, const auto& b){ return a.second > b.second; });

    // Print top keywords
    cout << BOLD << "  📊 Top 25 Keywords\n\n" << RESET;
    int max_count = sorted_freq.empty() ? 1 : sorted_freq[0].second;

    for (size_t i = 0; i < min((size_t)25, sorted_freq.size()); i++) {
        auto [word, count] = sorted_freq[i];
        int bar_len = max(1, (count * 30) / max_count);
        string bar(bar_len, '█');
        cout << "  " << CYAN << left << setw(22) << word << RESET
             << GREEN << bar << RESET
             << DIM << " " << count << "\n" << RESET;
    }

    // Top co-occurrences
    vector<pair<pair<string,string>,int>> sorted_co(cooccur.begin(), cooccur.end());
    sort(sorted_co.begin(), sorted_co.end(),
         [](const auto& a, const auto& b){ return a.second > b.second; });

    cout << "\n" << BOLD << "  🔗 Top 10 Keyword Co-occurrences\n\n" << RESET;
    for (size_t i = 0; i < min((size_t)10, sorted_co.size()); i++) {
        auto [[w1, w2], count] = sorted_co[i];
        cout << "  " << CYAN << left << setw(18) << w1 << RESET
             << " + " << CYAN << setw(18) << w2 << RESET
             << DIM << " ×" << count << "\n" << RESET;
    }

    // Save results to JSON
    ofstream out("data/keywords.json");
    out << "{\n  \"top_keywords\": [\n";
    for (size_t i = 0; i < min((size_t)30, sorted_freq.size()); i++) {
        auto [word, count] = sorted_freq[i];
        out << "    {\"word\": \"" << word << "\", \"count\": " << count << "}";
        if (i < min((size_t)29, sorted_freq.size()-1)) out << ",";
        out << "\n";
    }
    out << "  ],\n  \"cooccurrences\": [\n";
    for (size_t i = 0; i < min((size_t)20, sorted_co.size()); i++) {
        auto [[w1, w2], count] = sorted_co[i];
        out << "    {\"word1\": \"" << w1 << "\", \"word2\": \"" << w2 << "\", \"count\": " << count << "}";
        if (i < min((size_t)19, sorted_co.size()-1)) out << ",";
        out << "\n";
    }
    out << "  ]\n}\n";
    out.close();

    cout << "\n  " << GREEN << "✅ Keywords saved to data/keywords.json\n" << RESET;
    cout << "  " << DIM << "Run the dashboard to visualize everything.\n\n" << RESET;
    return 0;
}
