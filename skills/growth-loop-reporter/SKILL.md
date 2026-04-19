---
name: growth-loop-reporter
description: Weekly / monthly closed-loop reporter for Peec AI visibility growth. Measures what actually moved (visibility per prompt, cluster, zone) against what was invested (content published, pitches sent, forum answers), detects winning patterns, and outputs a ranked next-actions list — not a dashboard. This is the "Adaptive Learning + Reporting" closer of the growth agent loop. Use weekly for active projects or monthly for maintenance-mode projects.
user-invocable: true
---

# Growth Loop Reporter — What Worked, What Didn't, What's Next

Das ist der **Loop-Closer**. Er nimmt die kumulative Historie aus Content-Cluster-Builder + Content-Write + Citation-Outreach und beantwortet drei Fragen:

1. **Was hat sich bewegt?** (Visibility-Trend pro Prompt / Cluster / Zone)
2. **Warum?** (Welche spezifische Investition hat welchen Lift verursacht?)
3. **Was als Nächstes?** (Priorisierte Next-Actions, nicht abstrakter Insight)

Output ist **keine Dashboard** und **keine Datenauflistung** — sondern eine **kurze Narrative + Action-Liste**, die ein Mensch in 3 Minuten liest und direkt umsetzen kann.

---

## Wann einsetzen

- **Wöchentlich** bei aktiven Projekten mit laufendem Content + Outreach
- **Monatlich** bei Retainer-Projekten in Maintenance-Mode
- **Quartalsweise** als Strategie-Review — feeds in den nächsten `content-cluster-builder`-Run
- Nach großen Aktionen: ein Launch, eine Publikation, eine neue Zone

Nicht einsetzen wenn:
- Projekt hat noch keine 4-Wochen-Historie (zu wenig Signal)
- Keine Content- oder Outreach-Aktionen im Zeitraum (nichts zu lernen)

---

## Eingaben

- **Pflicht:** Peec `project_id`
- **Pflicht:** `reporting_window` — `weekly` / `monthly` / `quarterly`
- **Optional:** `baseline_date` — Default 28/90/180 Tage zurück
- **Optional:** `include_clusters` — wenn `content-cluster-builder` gelaufen ist und Zonen als Tags existieren (automatisch erkannt über `tag:zone:*`)

---

## Ablauf

### 1. Zeitreihe der Kern-Metriken ziehen

Drei Peec-Calls mit `dimensions=["date"]`:

```
# Overall brand-Visibility-Trend
mcp__peec-ai__get_brand_report(
    project_id, start_date=baseline, end_date=now,
    dimensions: ["date"],
    filters: [{field: "brand_id", operator: "in", values: [<own_brand_id>]}]
)

# Pro Prompt (für die Top-N nach Gewicht)
mcp__peec-ai__get_brand_report(
    project_id, start_date=baseline, end_date=now,
    dimensions: ["prompt_id", "date"],
    filters: [{field: "brand_id", operator: "in", values: [<own>]}]
)

# Pro Zone (wenn zone:*-Tags existieren)
Für jeden zone:*-Tag:
    mcp__peec-ai__get_brand_report(
        project_id, start_date=baseline, end_date=now,
        dimensions: ["tag_id", "date"],
        filters: [{field: "tag_id", values: [<zone_tag_id>]}]
    )
```

Pro Bucket (Prompt oder Zone) drei Werte errechnen:
- `visibility_t0` (Anfang Zeitraum)
- `visibility_t1` (Ende Zeitraum)
- `delta` = t1 - t0
- `trend` = linear regression slope über alle Daten im Zeitraum

### 2. Investitions-Log zusammenstellen

Alle Aktionen im Zeitraum sammeln:

```
# Neuer Content
git log --since=<baseline> --author=<user> -- "Content Automation/blog/"
# oder: file-system scan nach blog/YYYY-MM-DD_*/

# Outreach
Read: <project>/outreach/*_outreach_log.md
  → alle Pitches im Zeitraum mit status != 'queued'

# Prompt / Brand / Tag Änderungen in Peec
mcp__peec-ai__list_prompts + list_brands + list_tags
  → vergleiche mit Snapshot vom Anfang des Zeitraums (wenn vorhanden)
```

Ergebnis: eine Liste aller "Investments" mit:
`date | type (content/outreach/taxonomy) | target (prompt_id oder url) | description`

### 3. Correlation zwischen Investment und Lift

Pro Investment: welche Prompts / Zonen wären theoretisch gelift worden?

- **Content-Investition** → Prompts, deren focus_keyword im HTML-Body referenziert ist
  - Extrahiere Focus-KW aus `publish_<slug>.py` (`RANK_MATH_FOCUS`)
  - Match gegen `list_prompts` via Embedding/String-Contains

- **Outreach-Investition (Citation live)** → Prompts, für die die target_url in `get_url_report` als Source erscheint
  - `mcp__peec-ai__get_url_report(filters: [url in [<target_url>]])`

- **Zone-Intervention** → alle Prompts mit dem Zone-Tag

### 4. Attribution-Score pro Investment

```
attribution_score = 
    sum(affected_prompts[p].delta for p in matched_prompts)
    - baseline_drift  # was hätte sich ohne die Intervention bewegt?
```

**Baseline-Drift** = der Median-Delta der NICHT-betroffenen Prompts im selben Zeitraum. Das isoliert den Effekt der Intervention.

### 5. Pattern-Detection

Lektionen in 3 Buckets suchen:

**A. Gewinner-Muster** (hohe attribution_scores):
- Welcher Content-Typ (HOW_TO / COMPARISON / PILLAR) hat am meisten gelift?
- Welche Outreach-Target-Domain-Class (EDITORIAL / UGC / REFERENCE) am meisten Citations gebracht?
- Welche Zone ist am schnellsten gewachsen?

**B. Verlierer-Muster** (negative attribution oder Null-Delta trotz Investment):
- Content, der trotz Publish nicht indexiert/zitiert wurde
- Pitches ohne Response nach 14 Tagen
- Zonen, die trotz Content stagnieren (→ Content trifft nicht die Intent-Ebene)

**C. Überraschungen** (positive Delta ohne direktes Investment):
- Prompts, die ohne direkte Aktion gewonnen haben (organischer Spillover einer anderen Seite?)
- Plötzliche Einbrüche (Wettbewerber-Aktion? Algorithm-Änderung?)

### 6. Narrative-Generierung

Claude synthesisiert eine **maximal 400-Wort-Narrative** mit diesem Aufbau:

```markdown
# Growth Loop — <Projekt> (<Zeitraum>)

## Schlagzeile
<1 Satz: Was ist die wichtigste Erkenntnis dieser Woche / dieses Monats?>

## Was sich bewegt hat
- Visibility gesamt: X% → Y% (<N Prozentpunkte>)
- Stärkste Zone: <Name> (+Z%)
- Schwächste Zone: <Name> (flat oder -)
- Top-3 Einzel-Prompts mit größtem Lift: <Liste>

## Was das bewirkt hat (was nachweisbar wirkte)
<2-3 Sätze. Nicht "Content-Plan" — sondern: "Der Artikel X ist in 11 von 15 Ziel-Prompts
als Citation aufgetaucht; der Retainer-Pitch bei evergreen.media hat Y Citations
binnen 10 Tagen gebracht; die Shopify-Zone ist organisch gewachsen, obwohl dort
noch kein neuer Content lief — wahrscheinlich Spillover von Zone Z.">

## Was NICHT funktioniert hat
<1-2 Sätze: welches Investment hatte 0-Effekt, und warum wahrscheinlich>

## MACH JETZT (priorisiert, max. 3)
1. <Konkrete Action mit Deadline>
2. <Konkrete Action>
3. <Konkrete Action>

## MACH NICHT MEHR
- <Falls ein Muster als Zeitverschwendung identifiziert wurde>
```

### 7. Lern-Persistenz (für den nächsten Loop)

```
<project>/growth_loop/YYYY-MM-DD_learnings.json
```

JSON-Schema:

```json
{
  "period": {"start": "...", "end": "...", "window": "weekly"},
  "overall_visibility_delta": 0.04,
  "winners": {
    "content_types": [{"type": "HOW_TO_GUIDE", "avg_lift": 0.08, "n": 2}],
    "outreach_domains": [{"domain": "evergreen.media", "citations_gained": 5}],
    "zones": [{"zone_tag": "retainer-decision", "lift": 0.12}]
  },
  "losers": {
    "content_types": [],
    "outreach_domains": [{"domain": "<...>", "response_rate": 0.0}]
  },
  "surprises": [],
  "next_actions": ["..."],
  "stop_doing": ["..."]
}
```

Die next-run-Instanz von `content-cluster-builder` und `citation-outreach` lesen diese Datei als Priors: höher gewichtete Content-Typen, höher gewichtete Outreach-Domains.

---

## Quick Command Reference

| Schritt | Tool |
|---|---|
| Visibility-Trend gesamt | `mcp__peec-ai__get_brand_report(dimensions=["date"])` |
| Pro Prompt | `mcp__peec-ai__get_brand_report(dimensions=["prompt_id", "date"])` |
| Pro Zone (wenn getaggt) | `mcp__peec-ai__get_brand_report(dimensions=["tag_id", "date"])` |
| Citation-Source-Check | `mcp__peec-ai__get_url_report(filters: url in [...])` |
| Content-Log | git-log auf Content-Automation-Pfad |
| Outreach-Log | lokale `<project>/outreach/*.md` |

---

## Output-Qualitäts-Kriterien

Ein Growth-Report ist NUR dann fertig, wenn:

1. **Narrative ≤ 400 Wörter.** Längere Reports werden nicht gelesen und sind meist voller Hedging.
2. **Attribution ist begründet, nicht geraten.** Jeder Gewinner/Verlierer muss einen konkreten Kausal-Mechanismus haben, nicht nur Korrelation.
3. **Genau 3 Next-Actions.** Nicht 7, nicht 1. Drei ist die Capacity-Grenze einer Woche.
4. **Mindestens 1 "STOP DOING".** Der Mut, etwas zu verwerfen, ist wertvoller als neue Ideen.
5. **Learnings-JSON persistiert.** Ohne das ist kein Loop.

---

## Häufige Fehler

- **Dashboard statt Narrative:** 15 Charts werden nicht gelesen. 400 Wörter werden gelesen.
- **Korrelation als Kausalität verkaufen:** Visibility ist gestiegen, also hat der Content funktioniert. Vielleicht. Der Wettbewerber hatte SSL-Ausfall.
- **Baseline-Drift ignoriert:** ohne Vergleichsgruppe ist jeder Lift verdächtig.
- **Keine STOP-DOING-Liste:** man addiert, aber subtrahiert nie. Energie fragmentiert.
- **Report ohne Persistenz:** der nächste Lauf lernt nicht.
