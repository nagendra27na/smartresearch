import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * SmartResearch — Paper Ranker (Java)
 * Ranks papers by relevance score based on keyword frequency,
 * recency, and citation signals in the abstract.
 *
 * Compile: javac PaperRanker.java
 * Run:     java PaperRanker
 */
public class PaperRanker {

    static final String GREEN  = "\033[92m";
    static final String CYAN   = "\033[96m";
    static final String YELLOW = "\033[93m";
    static final String BOLD   = "\033[1m";
    static final String DIM    = "\033[2m";
    static final String RESET  = "\033[0m";

    // Simple JSON paper structure
    static class Paper {
        String id, title, summary, published, topic, link;
        List<String> authors  = new ArrayList<>();
        List<String> keywords = new ArrayList<>();
        double score;

        @Override
        public String toString() {
            return String.format("[%.2f] %s (%s)", score, title.substring(0, Math.min(60, title.length())), published);
        }
    }

    // ─── SCORING ──────────────────────────────────────────
    static double scoreKeywords(Paper p) {
        String[] highValue = {
            "large language", "transformer", "attention", "neural", "deep learning",
            "gpt", "bert", "diffusion", "reinforcement", "zero-shot", "few-shot",
            "foundation model", "generative", "multimodal", "vision language"
        };
        String combined = (p.title + " " + p.summary).toLowerCase();
        double score = 0;
        for (String kw : highValue) {
            if (combined.contains(kw)) score += 2.0;
        }
        return score;
    }

    static double scoreRecency(Paper p) {
        if (p.published == null || p.published.isEmpty()) return 0;
        try {
            int year  = Integer.parseInt(p.published.substring(0, 4));
            int month = Integer.parseInt(p.published.substring(5, 7));
            return (year - 2020) * 2.0 + (month / 12.0);
        } catch (Exception e) { return 0; }
    }

    static double scoreAbstractQuality(Paper p) {
        if (p.summary == null) return 0;
        double score = 0;
        String s = p.summary.toLowerCase();
        if (s.contains("state-of-the-art") || s.contains("state of the art")) score += 3;
        if (s.contains("outperform"))  score += 2;
        if (s.contains("benchmark"))   score += 1.5;
        if (s.contains("novel"))       score += 1;
        if (s.contains("propose"))     score += 1;
        if (s.contains("demonstrate")) score += 0.5;
        if (p.summary.length() > 300)  score += 1;
        return score;
    }

    static void scorePapers(List<Paper> papers) {
        for (Paper p : papers) {
            p.score = scoreKeywords(p) * 0.4
                    + scoreRecency(p)  * 0.3
                    + scoreAbstractQuality(p) * 0.3;
        }
        papers.sort((a, b) -> Double.compare(b.score, a.score));
    }

    // ─── NAIVE JSON PARSER ────────────────────────────────
    static List<Paper> parseJson(String json) {
        List<Paper> papers = new ArrayList<>();
        String[] entries = json.split("\\{");
        for (String entry : entries) {
            if (!entry.contains("\"title\"")) continue;
            Paper p = new Paper();
            p.title     = extractField(entry, "title");
            p.summary   = extractField(entry, "summary");
            p.published = extractField(entry, "published");
            p.topic     = extractField(entry, "topic");
            p.id        = extractField(entry, "id");
            p.link      = extractField(entry, "link");
            if (p.title != null && !p.title.isEmpty()) papers.add(p);
        }
        return papers;
    }

    static String extractField(String json, String key) {
        String pattern = "\"" + key + "\":";
        int idx = json.indexOf(pattern);
        if (idx == -1) return "";
        int start = json.indexOf("\"", idx + pattern.length());
        if (start == -1) return "";
        int end = json.indexOf("\"", start + 1);
        while (end > 0 && json.charAt(end - 1) == '\\') end = json.indexOf("\"", end + 1);
        if (end == -1) return "";
        return json.substring(start + 1, end).replace("\\n", " ").replace("\\\"", "\"");
    }

    // ─── SAVE RANKED JSON ─────────────────────────────────
    static void saveRanked(List<Paper> papers) throws IOException {
        StringBuilder sb = new StringBuilder("[\n");
        for (int i = 0; i < papers.size(); i++) {
            Paper p = papers.get(i);
            sb.append("  {\n");
            sb.append(String.format("    \"rank\": %d,\n", i + 1));
            sb.append(String.format("    \"score\": %.2f,\n", p.score));
            sb.append(String.format("    \"id\": \"%s\",\n", p.id));
            sb.append(String.format("    \"title\": \"%s\",\n", p.title.replace("\"", "\\\"")));
            sb.append(String.format("    \"published\": \"%s\",\n", p.published));
            sb.append(String.format("    \"topic\": \"%s\",\n", p.topic));
            sb.append(String.format("    \"link\": \"%s\"\n", p.link));
            sb.append(i < papers.size() - 1 ? "  },\n" : "  }\n");
        }
        sb.append("]");
        Files.writeString(Path.of("data/ranked_papers.json"), sb.toString());
    }

    // ─── MAIN ─────────────────────────────────────────────
    public static void main(String[] args) throws Exception {
        System.out.println("\n" + BOLD + CYAN +
            "  🏆 SmartResearch — Paper Ranker (Java)" + RESET + "\n");

        File f = new File("data/papers.json");
        if (!f.exists()) {
            System.out.println("  \033[91m❌ Run scraper.py first to fetch papers.\033[0m\n");
            return;
        }

        String json = Files.readString(f.toPath());
        List<Paper> papers = parseJson(json);
        System.out.println("  " + DIM + "Scoring " + papers.size() + " papers..." + RESET);

        scorePapers(papers);
        saveRanked(papers);

        System.out.println("\n  " + BOLD + CYAN + "🏆 Top 10 Ranked Papers" + RESET + "\n");
        for (int i = 0; i < Math.min(10, papers.size()); i++) {
            Paper p = papers.get(i);
            String medal = i == 0 ? "🥇" : i == 1 ? "🥈" : i == 2 ? "🥉" : "  " + (i+1) + ".";
            System.out.printf("  %s %s%s%s%n", medal, BOLD, p.title.substring(0, Math.min(65, p.title.length())), RESET);
            System.out.printf("     %sScore: %.2f  |  %s  |  %s%s%n", DIM, p.score, p.published, p.topic, RESET);
        }

        System.out.println("\n  " + GREEN + "✅ Ranked list saved to data/ranked_papers.json" + RESET);
        System.out.println("  " + DIM + "Open dashboard/index.html to visualize.\n" + RESET);
    }
}
