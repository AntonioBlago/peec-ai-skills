---
name: content-cluster-builder
description: Turns a Peec AI prompt set into strategic content zones — not keyword groups. Groups prompts by buyer intent + funnel stage + visibility gap + shared demand signals, producing 4-8 "content zones" with assigned competitive weaknesses to attack, supporting evidence (forum quotes, SERP patterns), and a rank-ordered next-move per zone. Use when a Peec project has 20+ prompts and needs a topic architecture — not a flat content calendar. Output is a strategic map, not a list.
user-invocable: true
---

# Content Cluster Builder — Strategic Topic Zones from Peec Prompts

Ein **Cluster ist kein Keyword-Thema** — es ist eine **strategische Angriffszone**: eine Gruppe von Peec-Prompts, die gemeinsam eine kauf-entscheidende Frage aus einem bestimmten Winkel beantwortet, bei der die eigene Marke einen spezifischen strukturellen Hebel hat.

Dieser Skill ersetzt das klassische „Keyword-Clustering" durch eine **dreidimensionale Gruppierung**:

```
      Intent
       ↑
Visibility-Gap
       ↑
Demand-Signal
```

Nur wenn eine Prompt-Gruppe auf allen drei Achsen kohärent ist, wird sie zu einer **Content-Zone** mit strategischem Wert.

---

## Wann einsetzen

- Peec-Projekt hat ≥ 20 Prompts und das Team verliert den Überblick
- Nach einem `@ai-visibility-setup`-Lauf, bevor `@content-write` pro Artikel gestartet wird
- Quartalsweise als Strategie-Refresh, wenn neue Prompts + Pain-Points dazukommen
- Vor einem Investment-Gespräch („Was ist unsere AI-Content-Strategie?")

Nicht einsetzen wenn:
- < 10 Prompts (zu wenig Masse für echte Zonen)
- Prompts sind noch nicht getrennt in Awareness/Consideration/Decision/Retention (dann erst `@ai-visibility-setup` laufen)

---

## Eingaben

- **Pflicht:** Peec `project_id`
- **Optional:** `date_range` (Default letzte 30 Tage — für Visibility + Retrieval-Zahlen)
- **Optional:** `target_zones` (Default 4-8 Zonen — der Skill wählt selbst die Auflösung)
- **Optional:** `focus_funnel_stage` — wenn du nur EINE Stufe clustern willst

---

## Ablauf

### 1. Prompt-Inventar + Visibility-Lage ziehen

```
mcp__peec-ai__list_prompts(project_id)                          # Prompt-Text + Topic + Tags
mcp__peec-ai__get_brand_report(
    project_id,
    start_date, end_date,
    dimensions: ["prompt_id"],
    filters: [{field: "brand_id", operator: "in", values: [<own_brand_id>]}]
)                                                                # Visibility pro Prompt für die eigene Marke
mcp__peec-ai__get_url_report(
    project_id,
    start_date, end_date,
    dimensions: ["prompt_id"],
    filters: [{field: "gap", operator: "gt", value: 0}]
)                                                                # Gap-Signal pro Prompt
```

Merge in eine einzige Prompt-Tabelle mit Spalten:
`prompt_id | text | funnel_stage | topic | tags | own_visibility | gap_size | top_competitor_url | top_competitor_classification`

### 2. Dimensions-Scoring (3 Achsen pro Prompt)

Pro Prompt drei numerische Signale:

- **Intent-Density** (0-1): wie stark überlappt der Prompt semantisch mit anderen Prompts derselben Funnel-Stufe?
  - Verwende Embedding-Cosine (z. B. OpenAI `text-embedding-3-small` oder `mcp__visiblyai__classify_keywords` für regex-basierte Topics)
  - Hoch = Prompt ist ein "Zentrum einer Cluster-Region"

- **Visibility-Gap** (0-1): `1 - own_visibility`, gewichtet mit `gap_size / max_gap_size_in_project`
  - Hoch = dort ist viel zu holen

- **Demand-Density** (0-1): gibt es Reddit/Forum-Threads, die zu diesem Prompt matchen?
  - Aus Peec `get_url_report` mit `classification=DISCUSSION`: zähle wie viele Thread-URLs in den Chat-Sources für diesen Prompt auftauchten
  - Hoch = echte Käufer stellen die Frage wirklich

**Score pro Prompt:** `intent_density × visibility_gap × demand_density` (multiplikativ, weil alle drei Achsen nötig sind).

### 3. Clustering (embedding-basiert, nicht regex-basiert)

Zwei Optionen je nach Verfügbarkeit:

**A. Visibly AI `query_fanout` als semantische Brücke** (ab v0.6.0):

```
Für jeden Prompt mit Score > Median:
    mcp__visiblyai__query_fanout(url=<own_domain>, keyword=<prompt_keyword>, language=<lang>)
    → fanout_queries[] wird zum semantischen Fingerabdruck des Prompts
```

Zwei Prompts gehören in dieselbe Zone, wenn ihre Fan-Out-Queries ≥ 40% Overlap haben.

**B. Fallback — Claude-basiertes Intent-Clustering:**

Claude direkt instruieren, die Prompt-Liste in N strategische Zonen zu teilen. Eingabe-Prompt-Skelett:

```
Gegeben diese <N> Prompts mit ihren Metadaten (Funnel-Stage, Tags, Visibility-Gap, 
Demand-Signal), gruppiere sie in 4-8 strategische Content-Zonen nach folgenden Kriterien:

1. Gleiche Kauf-Entscheidungsfrage (nicht nur ähnliche Keywords)
2. Gleiche Funnel-Stufe (oder angrenzende)
3. Geteiltes Demand-Signal (gleiche Pain-Points aus Forum-Daten)
4. Gemeinsamer struktureller Hebel (gleicher Typ Konkurrent den wir schlagen können)

Für jede Zone: Name, 2-Satz-Thesis, Prompt-IDs, gemeinsamer Konkurrenten-Schwachpunkt, 
eine einzige „Mach genau das jetzt"-Aktion.
```

### 4. Zonen validieren

Jede Kandidaten-Zone muss vier Checks bestehen:

1. **Kohärenz-Check:** ≥ 3 Prompts mit ≥ 0.4 embedding-similarity zum Zone-Zentroid
2. **Funnel-Check:** maximal 1 Funnel-Stufe Spannweite (Awareness + Consideration ok, Awareness + Decision nicht)
3. **Gap-Check:** durchschnittlicher `visibility_gap` der Zone > 0.3
4. **Uniqueness-Check:** jede Zone hat einen Konkurrenten-Typ, der NICHT von einer anderen Zone gewonnen wird

Zonen, die scheitern, werden zu ihrem nächsten Nachbar gemerged oder gedroppt.

### 5. Pro Zone: strategische Komponenten extrahieren

Pro valide Zone 6 Komponenten erzeugen:

| Komponente | Quelle |
|---|---|
| **Zone-Name** (max 40 Z.) | Claude synthesisiert aus den Prompts |
| **Thesis** (2 Sätze) | Warum diese Zone existiert + warum du hier gewinnst |
| **Funnel-Spannweite** | TOFU / MOFU / BOFU / Retention |
| **Top-5 Peec-Prompts** | sortiert nach dem kombinierten Score |
| **Strukturelle Schwäche der Konkurrenz** | aus `peec-content-intel` Competitor-Analysis: was fehlt bei allen Konkurrenten in dieser Zone |
| **One-Move-Action** | eine konkrete, direkt ausführbare Aktion — kein „Analysiere X", sondern „Schreibe Artikel Y mit Struktur Z und pitche ihn bei Z1, Z2" |

### 6. Zonen-Ranking + Output

Zonen nach **potential_impact** sortieren:

```
potential_impact = sum(prompts.visibility_gap × prompts.demand_density × funnel_value_weight)

wobei:
  funnel_value_weight = {Awareness: 0.6, Consideration: 1.0, Decision: 1.5, Retention: 1.2}
```

Output-Format (Markdown, direkt in einen Notion-/Slite-Brief kopierbar):

```markdown
# Content-Zonen für <Projekt-Name> (Stand YYYY-MM-DD)

## Zone 1 (Score 0.85): <Name>

**Thesis:** <2 Sätze>
**Funnel:** Consideration → Decision
**Prompts:** 7 Peec-Prompts (siehe Appendix A)

**Strukturelle Schwäche der Konkurrenz:**
- Keine der Top-5-Konkurrenz-URLs adressiert <Thema X>
- 4 von 5 schweigen über <Preis / Retainer / Methode>

**ONE MOVE JETZT:**
> Schreibe einen HOW-TO-GUIDE mit Title "<konkret>", H2-Gliederung <konkret>,
> publiziere als `/blog/<slug>`, pitche danach innerhalb von 7 Tagen bei
> <Domain 1 aus get_actions>, <Domain 2>, und beantworte <Reddit-URL>.

**Success-Metrik (zu messen nach 6 Wochen):**
Peec-Visibility für die 7 Prompts von durchschnittlich X% → Y%.

---

## Zone 2 (Score 0.78): ...
```

### 7. Persistence + Next-Run-Hook

Wenn `mcp__peec-ai__create_tag` verfügbar: pro Zone einen Tag in Peec anlegen (z. B. `zone:retainer-decision`) und alle Prompts der Zone damit taggen. Das macht die Zone später messbar:

```
mcp__peec-ai__get_brand_report(
    project_id, start_date, end_date,
    filters: [{field: "tag_id", operator: "in", values: [<zone_tag_id>]}]
)
```

Das ist der Hook, den `growth-loop-reporter` später braucht, um Zone-Performance über Zeit zu messen.

---

## Quick Command Reference

| Schritt | Tool |
|---|---|
| Prompts + Topics + Tags laden | `mcp__peec-ai__list_prompts` / `list_topics` / `list_tags` |
| Visibility pro Prompt | `mcp__peec-ai__get_brand_report(dimensions=["prompt_id"])` |
| Gap pro Prompt | `mcp__peec-ai__get_url_report(filters: gap>0)` |
| Semantische Cluster-Signale | `mcp__visiblyai__query_fanout` oder `classify_keywords` |
| Pain-Signal-Density | `mcp__peec-ai__get_url_content` auf Reddit-Threads |
| Zone als Tag persistieren | `mcp__peec-ai__create_tag` + `update_prompt` |

---

## Output-Qualitäts-Kriterien (selbst-check vor Rückgabe)

Eine Zonen-Map ist NUR dann fertig, wenn:

1. **Jede Zone hat eine One-Move-Action.** Kein „Analysiere", „Prüfe", „Erwäge" — es muss ein konkretes, ausführbares Verb stehen.
2. **Jede Zone hat einen strukturellen Angriffspunkt.** Nicht „Konkurrenten haben schwachen Content" — sondern „Konkurrent X fehlt Preisangabe, Konkurrent Y fehlt FAQ-Block".
3. **Jede Zone ist messbar.** Ein Peec-Tag oder eine explizite Liste von Prompt-IDs, deren Visibility in 4-8 Wochen gemessen wird.
4. **Maximal 8 Zonen.** Wenn der Algorithmus 12 liefert, werden die schwächsten 4 gemerged oder gedroppt — Fokus gewinnt.

---

## Häufige Fehler

- **Keyword-Cluster statt Intent-Cluster:** „Neuro-SEO Blog" + „Neuro-SEO Shop" zu einem Cluster zusammenziehen, obwohl sie verschiedene Funnel-Stufen + Käufer adressieren.
- **Alle Zonen sind Awareness:** dann fehlt der Funnel-Check. Dezidierter Decision-Cluster ist oft wertvoller als fünf Awareness-Cluster.
- **Zonen ohne Angriffspunkt:** „Diese Zone ist wichtig" reicht nicht. Was machen die Konkurrenten falsch? Wenn man nicht antworten kann, ist die Zone keine.
- **Zu viele Zonen:** 12 Zonen = 12 halb-bearbeitete Themen. 5 Zonen = 5 Themen, in denen du gewinnst.
