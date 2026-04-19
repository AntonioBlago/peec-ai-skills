---
name: peec-content-intel
description: Content-Intelligence-Workflow für Peec-AI-Prompts. Verbindet Peec (Prompt-Sichtbarkeit, Source-URLs, Chat-Responses) mit Visibly AI (Backlinks, OnPage, Keywords, GSC) und Reddit/Forum-Scraping. Nutzt Query Fan-Out, um aus einem Peec-Prompt 5-8 semantische Sub-Queries zu generieren. Liefert Opportunity-Scores und konkrete Content-Briefs pro Prompt. Use when the user wants to find content opportunities, evaluate competitor content, build a content brief from Peec data, or discover what content wins specific AI prompts.
user-invocable: true
---

# Peec Content Intelligence — Prompt → Competitor Intel → Content Brief

Ein 6-Phasen-Workflow, der eine **Peec-AI-Sichtbarkeitslücke** in eine konkrete **Content-Strategie** übersetzt. Kombiniert Peec (AI-Visibility-Daten), Visibly AI (SEO-Daten: Backlinks, OnPage, GSC), Reddit/Forum-Scraping (Pain-Signals) und Query Fan-Out (semantische Query-Expansion).

**Trigger:**
- "Welche Inhalte brauche ich, um Prompt X zu gewinnen?"
- "Analysiere die Quellen, die meine Peec-Konkurrenten zitiert bekommen"
- "Was ist der Content-Gap zwischen mir und noahlutz.de für Prompt X?"
- "Erstelle einen Content-Brief basierend auf Peec-Daten"
- "Welche Backlinks haben die URLs, die für meinen Prompt zitiert werden?"
- "Query fan-out für Peec-Prompt X"

**Abgrenzung:** Dieses Skill läuft **nach** `ai-visibility-setup` (das Projekt muss existieren, Prompts müssen mind. 24h Daten haben).

---

## Phase 1 — Target-Prompt + URL-Gap bestimmen

Ziel: Identifizieren, welche URLs deine Konkurrenten zitiert bekommen — während du fehlst.

```
# 1a: Prompt-Visibility prüfen — ist die eigene Marke überhaupt abwesend?
mcp__peec-ai__get_brand_report(
  project_id,
  start_date, end_date,
  dimensions: ["prompt_id"],
  filters: [{field: "prompt_id", operator: "in", values: [<prompt_id>]}]
)

# 1b: URLs für den Prompt mit Gap > 0 (Konkurrenten da, eigene Marke nicht)
mcp__peec-ai__get_url_report(
  project_id,
  start_date, end_date,
  dimensions: ["prompt_id"],
  filters: [
    {field: "prompt_id", operator: "in", values: [<prompt_id>]},
    {field: "gap", operator: "gt", value: 0}
  ],
  limit: 25
)
```

**Output zurück:** bis zu 25 URLs, sortiert nach Retrieval-Frequenz, klassifiziert (LISTICLE, ARTICLE, COMPARISON, HOW_TO_GUIDE, PROFILE etc.).

**Interpretation:**
- **LISTICLE / COMPARISON** → meist die wichtigsten Ziele für Outreach (als Kandidat auflisten lassen)
- **HOW_TO_GUIDE / ARTICLE** → eigene Content-Ziele (was musst du selbst schreiben)
- **PROFILE / UGC (Reddit, YouTube)** → Community-Ziele (wo musst du dich platzieren)

---

## Phase 2 — Query Fan-Out (via Visibly AI `query_fanout`)

Ziel: Aus einem Parent-Prompt **semantisch verwandte Sub-Queries** generieren UND gleich gegen den Content einer Ziel-URL matchen. Diese Technik spiegelt, was Google AI Mode und Perplexity intern tun — sie zerlegen eine Query in mehrere Such-Perspektiven.

### Primäre Methode — MCP-Tool `mcp__visiblyai__query_fanout` (empfohlen, ab v0.6.0)

Visibly AI hat einen produktiven Query-Fan-Out-Analyzer (Gemini-grounded + semantic coverage matching):

```
mcp__visiblyai__query_fanout(
  url: "https://<own-or-competitor-domain>/<page>",
  keyword: "<focus_keyword>",
  data_source: "dataforseo",           // "dataforseo" | "gsc" | "both"
  gsc_property: null,                  // required wenn data_source="gsc"/"both"
  language: "de"                       // "en" | "de"
)
```

Returnt strukturiert:
- `fanout_queries[]` — Gemini-generierte Sub-Queries aus dem Fokus-Keyword
- `coverage_score` — 0-1, wie gut die URL die Sub-Queries inhaltlich abdeckt
- `covered_count` / `total_count` — Zähler der abgedeckten Sub-Queries
- `gaps[]` — Sub-Queries, die auf der URL NICHT adressiert sind → direkt dein Content-Backlog
- `coverage_details[]` — pro Sub-Query: `best_match`, `match_type` (content/heading/faq), `matching_chunk`

**Credits:** ~3-5 dynamisch (je nach data_source). URL + Keyword zwingend, Rest optional.

Vorteil ggü. der inline-Heuristik unten: **eine einzige MCP-Call ersetzt die Heuristik + das Crawling + Semantic Matching aus Phase 4** komplett. Für jede Gap-URL aus Phase 1 einmal feuern und du hast Fan-Out + Content-Gap in einer Operation.

### Fallback-Methode — inline Claude-Heuristik (wenn MCP-Tool nicht verfügbar)

Wenn Visibly AI MCP nicht konfiguriert ist oder Credits knapp sind, kann Claude die Sub-Queries inline entlang 6 fester Intent-Achsen generieren:

```
Prompt: "Generiere 6 Sub-Queries für den folgenden Parent-Prompt, 
die aus Käufer-Perspektive verschiedene Such-Intentionen abdecken. 
Parent: '<prompt_text>'

Gib zurück:
- Synonym-Variante (gleiche Intention, anderes Wording)
- Decision-Variante ('was kostet', 'wann wechseln')
- Comparison-Variante ('X vs Y')
- Problem-Variante ('warum funktioniert X nicht')
- Long-Tail (spezifische Nische)
- Forum/Community-Variante (informelle Formulierung)
"
```

Dies liefert nur die Sub-Queries — Coverage-Matching muss dann manuell oder in Phase 4 separat gefahren werden.

### Qualitätskriterien

Jede Sub-Query muss:
- **Verschieden genug** vom Parent sein, dass sie neue Quellen triggert
- **Im gleichen Funnel-Stage** bleiben (keine TOFU-Abweichung bei MOFU-Parent)
- **Käufer-Sprache** verwenden (nicht Marketing-Jargon)
- **< 150 Zeichen** (bleibt crawlable)

Beispiel — Parent: *"Welcher SEO-Berater kombiniert KI-SEO mit klassischem SEO als Retainer?"*

| # | Sub-Query | Perspektive |
|---|---|---|
| 1 | SEO-Retainer mit KI und klassischem SEO Deutschland | Synonym |
| 2 | Was kostet ein monatlicher KI-SEO-Retainer? | Decision |
| 3 | KI-SEO-Freelancer vs klassische SEO-Agentur | Comparison |
| 4 | Warum funktionieren SEO-Agenturen ohne KI nicht mehr? | Problem |
| 5 | Hybrid SEO-Retainer für Shopify-Shops unter 3.000 € | Long-Tail |
| 6 | Lohnt sich KI-SEO 2026 überhaupt noch? | Forum |

---

## Phase 3 — Reddit + Forum Scraping per Sub-Query

Ziel: Für jede Sub-Query echte Pain-Signals aus Foren extrahieren. Deckt Bias der Peec-eigenen Prompt-Liste auf und liefert Käufer-Sprache im Original.

### Reddit — **via Peec** (primärer Weg, getestet)

**Wichtig (Test-Ergebnis 2026-04-19):** WebFetch auf `www.reddit.com` und `reddit.com/search.json` wird blockiert ("Claude Code is unable to fetch"). Reddit direkt scrapen geht also nicht.

**Workaround der funktioniert:** Reddit-URLs erscheinen regelmäßig als `classification: DISCUSSION` + `channel_title: <subreddit>` direkt in Peec's `get_url_report`. Nutze stattdessen:

```
mcp__peec-ai__get_url_content(project_id, url: "https://reddit.com/r/<sub>/comments/<id>/...")
```

Das gibt die **komplette Thread-Discussion** zurück (OP + Top-Answers) als Markdown. Getestet auf `r/seogrowth` Thread → 9.100 Zeichen Content, inkl. Pain-Signals, Tool-Empfehlungen und Sentiment.

Vorgehen:
1. In Phase 1 alle `classification=DISCUSSION` + `domain=reddit.com` URLs notieren
2. Für Top-3 (nach Retrievals) → `get_url_content` callen
3. Content analysieren: verbatim Pain-Quotes, Tool-Mentions, Competitor-Mentions, Sentiment

### Reddit — direct (deprecated, nur bei anderen MCP-Harnessen)

Falls ein anderer MCP-Harness Reddit erlaubt (nicht Claude Code):
```
WebFetch("https://www.reddit.com/search.json?q=<encoded-query>&sort=top&t=year&limit=15")
```

Relevante Subreddits für DACH-Service-Business: `r/de`, `r/selbststaendig`, `r/kmu`, `r/Unternehmer`, `r/SEO`, `r/shopify`, `r/ecommerce`, `r/Finanzen`.

### Gutefrage / t3n / OMR (via WebSearch + WebFetch)

```
WebSearch("site:gutefrage.net <query>")
WebSearch("site:t3n.de/forum <query>")
WebSearch("site:omr.com <query>")
```

Fetch Top-Threads mit:
```
WebFetch(url, "Extract the original question verbatim, plus top 3 answers. Note frustrations, decision triggers, competitor/brand mentions.")
```

**Note:** Gutefrage.net blockt WebFetch mit 403. Alternativen: Google-Cache, archive.org, oder Google-Search-Snippet als Fallback.

### Output aggregieren

Pro Sub-Query:
- 3-5 Pain-Point-Quotes (verbatim)
- Competitor/Brand-Mentions mit Sentiment
- Top 2-3 Thread-URLs für späteres Engagement

---

## Phase 4 — Visibly AI Tiefenanalyse pro Competitor-URL

Ziel: Für jede in Phase 1 gefundene Competitor-URL die SEO-Signale erheben, die sie stark machen.

### Pro URL: Backlinks (Domain-Level)

```
mcp__visiblyai__get_backlinks(domain: "<competitor-domain>", limit: 10, location: "Germany")
```

**Wichtig (Test 2026-04-19):** `get_backlinks` kann >260.000 Zeichen zurückgeben (2.836 Backlinks für noahlutz.de → 260 KB Output). Das sprengt den Context. **Immer `limit: 10-20`** setzen, oder die Response in einem Subagent konsumieren. Für Kernmetriken (total_count, rank, domain_from_rank) reicht `limit=1`.

Output-Schlüsselfelder:
- `total_count` → gesamte Backlink-Anzahl (z.B. 2.836 für noahlutz, 21.367 für suchhelden)
- pro Item: `rank` (0-100, entspricht DR), `page_from_rank`, `domain_from_rank`
- `anchor_text`, `url_from`, `url_to`, `is_new`, `is_lost`

**Kurzform** für schnellen Vergleich — nur top-Metriken:
```
result[0].total_count           # Gesamt-Backlinks
result[0].items[0].rank         # DR des Top-Backlinks
result[0].items[*].domain_from_rank  # DR der linkenden Domains
```

**Interpretation:**
- **DR < 20** → organische Autorität, Content-Gewinn ist realistisch
- **DR 20-50** → etabliert, braucht 6-12 Monate Content + gezielte Links
- **DR > 50** → schwer zu schlagen direkt, besser flankieren (ähnlicher Long-Tail-Content)

### Pro URL: OnPage-Audit (15 Credits!)

```
mcp__visiblyai__onpage_analysis(url: "<competitor-url>", keyword: "<focus-keyword>")
```

Output: 24-Punkte-Audit — Title-Tag-Länge, H1-H6-Struktur, Keyword-Density, internal links, schema, word count, LCP-Hinweise.

**Wichtig:** Nur für Top-3-Competitor-URLs pro Prompt ausführen (Credit-Budget). Priorisiere URLs mit höchster Retrieval-Frequenz aus Phase 1.

### Pro URL: Content-Content-Comparison via Peec

```
mcp__peec-ai__get_url_content(project_id, url: "<competitor-url>")
```

Gibt Markdown-Inhalt zurück, den die AI-Engine gelesen hat. Nutze das, um:
- **Content-Länge** vs deine Seite zu vergleichen
- **Headings / Themen-Struktur** zu extrahieren
- **Semantische Entities** (Marken, Produkte, Konzepte) zu identifizieren
- **Tonalität** zu checken

### Keyword-Universum

Parallel: für jede Competitor-Domain die organischen Keywords ziehen:

```
mcp__visiblyai__get_keywords(domain: "<competitor-domain>", limit: 200, location: "Germany")
```

Cross-Reference mit eigenen Keywords (`get_keywords` für antonioblago.de) → **Keyword-Gap** identifizieren.

---

## Phase 5 — Opportunity Scoring

Ziel: Pro Competitor-URL einen objektiven Score berechnen, der die Schwierigkeit des Angriffs (Übernahme oder Verdrängung) bewertet.

### Scoring-Formel

```
Opportunity_Score = (Retrieval_Frequency × Gap_Size × Forum_Pain_Density) 
                    / (Domain_DR × (1 + Content_Quality_Diff))
```

Variablen:
- **Retrieval_Frequency**: aus `get_url_report` → wie oft wird die URL pro Prompt zitiert
- **Gap_Size**: wie viele Chats zitieren den Competitor, aber nicht dich
- **Forum_Pain_Density**: wie viele unique Pain-Points aus Phase 3 zum Thema passen
- **Domain_DR**: aus Visibly `get_backlinks`
- **Content_Quality_Diff**: Heuristik (0-1) — wie überlegen ist deren Content ggü. deinem aktuellen?

### Opportunity-Tiers

- **Tier 1 (Score > 50)**: sofort angreifen — Content schreiben + Outreach
- **Tier 2 (Score 20-50)**: mittelfristig, 3-6 Monate
- **Tier 3 (Score < 20)**: parken, evtl. flankierender Long-Tail

---

## Phase 6 — Content Brief Output

Ziel: Pro Prompt ein strukturierter Brief, den du direkt in den Blog-/LinkedIn-/YouTube-Workflow geben kannst.

### Brief-Template

```markdown
## Content Brief: [Prompt-Text]

### Ziel
Peec-Prompt zu gewinnen: "<prompt_text>"
Funnel-Stage: Awareness / Consideration / Decision / Retention
Eigene Sichtbarkeit heute: X%  →  Ziel: Y% in 90 Tagen

### Käufer-Sprache (aus Forums)
- [Verbatim Pain Point 1]  (Quelle: r/selbststaendig, 2026-03)
- [Verbatim Pain Point 2]  (Quelle: Gutefrage)
- [Decision Trigger]

### Sub-Queries (Query Fan-Out)
1. [Sub-Query 1]
2. [Sub-Query 2]
3. ...

### Competitor-Landschaft
| URL | Class | Retrieval | DR | Opp-Score | Notiz |
|---|---|---|---|---|---|
| evergreen.media/ki-seo | ARTICLE | 22% | 47 | 35 | Starker DR, Kooperations-Pitch |
| noahlutz.de/ki-seo | LISTICLE | 9% | 22 | 68 | Direkt angreifbar, ähnlicher DR |

### Empfohlenes Format
[LISTICLE / COMPARISON / HOW-TO / DEFINITION] basierend auf dominanter URL-Klasse

### Title (Entwurf)
[Title, ≤ 60 Zeichen]

### Meta Description (≤ 155 Z.)
[Description mit Käufer-Sprache]

### Outline (H2/H3)
1. [Opening Pain]
2. [Definition / Framework]
3. [Decision Matrix oder Checkliste]
4. [Praxis-Beispiele]
5. [Fallstricke]
6. [CTA zum Retainer]

### Fokus-Keyword + Sekundäre
- Focus: [keyword]  (Volume Z., Intent: X)
- Sekundär: [kw2], [kw3], [kw4]  (aus Keyword-Gap)

### Backlink-Strategie
- [Domain 1]: Pitch per E-Mail (Template referenzieren)
- [Subreddit]: Thread teilnehmen (URL)
- [Editorial]: Contribution zu existierendem Artikel pitchen

### KPI
- Ziel-Prompt-Visibility nach 90 Tagen: Y%
- Ziel-GSC-Position für Focus-KW: Top 10
- Min. 3 Backlinks von DR > 30
```

### Datei-Ablage

Pro Prompt einen eigenen Ordner:
```
C:/Users/anton/OneDrive/Mabya/Dokumente/Claude/Content Automation/briefs/
  YYYY-MM-DD_<prompt-slug>/
    brief.md                         # strukturiertes Markdown wie oben
    competitor-urls.json             # Rohdaten von Peec/Visibly
    forum-pains.json                 # gesammelte Reddit/Gutefrage-Extrakte
    scoring.json                     # Opportunity-Scores pro URL
```

---

## Quick Command Reference

| Schritt | Tool |
|---|---|
| Gap-URLs finden | `mcp__peec-ai__get_url_report(filters: gap > 0)` |
| AI-Response + Quellen inspizieren | `mcp__peec-ai__list_chats` → `get_chat` |
| Scraped Content der Competitor-URL | `mcp__peec-ai__get_url_content` |
| Reddit direkt | `WebFetch("https://www.reddit.com/search.json?q=...")` |
| Gutefrage / t3n / OMR | `WebSearch("site:...")` → `WebFetch(url)` |
| Query Fan-Out + Coverage | `mcp__visiblyai__query_fanout(url, keyword)` — ab Visibly MCP v0.6.0 |
| Backlink-Profil | `mcp__visiblyai__get_backlinks` |
| 24-Punkt-OnPage-Audit | `mcp__visiblyai__onpage_analysis` (15 Cr.) |
| Competitor-Keywords | `mcp__visiblyai__get_keywords` |
| Keyword-Intent-Check | `mcp__visiblyai__classify_keywords` |
| Competitor-Discovery via Keywords | `mcp__visiblyai__get_competitors` |
| Full-Site-Crawl | `mcp__visiblyai__crawl_website` (15-60 Cr.) |

---

## Credit-Strategie (Visibly AI)

Pro Prompt-Analyse ca. 45-75 Credits verbrauchen:
- 1× `get_backlinks` pro Top-3-Competitor-Domain (~0 Credits, meist günstig)
- 3× `onpage_analysis` pro Top-3-URL → 45 Credits
- 1× `get_keywords` pro Top-2-Competitor → ~0 Credits (DataForSEO wenn kein GSC)

Für Batch über 10 Prompts: ~500-750 Credits.

---

## Häufige Fehler

- **Prompts ohne 24h-Datenhistorie analysieren** — keine Chats/Sources vorhanden, Phase 1 gibt leer zurück. Mindestens 1-3 Tage warten.
- **Gutefrage via WebFetch versuchen** — blockt mit 403. Nutze WebSearch + Google-Snippets als Fallback.
- **Zu viele `onpage_analysis`-Calls** — jede kostet 15 Credits. Priorisiere nach Retrieval-Frequenz.
- **Query Fan-Out nicht Funnel-konsistent** — Awareness-Sub-Queries zu MOFU-Parent hinzufügen verwässert den Brief.
- **Content-Gap ignorieren** — nur auf Backlinks schauen, ohne den Content selbst zu lesen, führt zu „DR zu hoch, ignoriere" — oft ist es die schwache Content-Qualität, die den Konkurrenten schlagbar macht.
- **Skill ohne vorherigen `ai-visibility-setup`-Lauf starten** — setzt voraus, dass Brands/Prompts/Topics korrekt strukturiert sind.

---

## Automatisierung (optional)

Die 6 Phasen lassen sich als Python-Pipeline abbilden. Empfohlener Ort:
`C:/Users/anton/OneDrive/Mabya/Dokumente/Claude/claude_tools/seo/peec_content_intel.py`

Pipeline-Skizze (pseudo):
```python
def run_intel(project_id, prompt_id, start_date, end_date):
    gap_urls = peec.get_url_report(gap>0, prompt_id)
    subqueries = claude.fanout(prompt_text, n=6)
    forum_pains = [reddit.search(q) for q in subqueries] + [gutefrage.search(q) for q in subqueries]
    per_url = {}
    for u in gap_urls[:5]:
        per_url[u] = {
            "backlinks": visibly.backlinks(domain_of(u)),
            "onpage":    visibly.onpage(u, focus_keyword),
            "content":   peec.get_url_content(u),
        }
    scored = score(per_url, forum_pains)
    brief  = render_brief(prompt_text, scored, forum_pains, subqueries)
    save_to(f"briefs/{today}_{slug}/brief.md", brief)
```
