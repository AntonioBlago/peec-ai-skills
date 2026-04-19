---
name: citation-outreach
description: Turns Peec AI's get_actions recommendations + forum/UGC discovery into a prioritized outreach pipeline with pitch templates, contact extraction, status tracking, and success metrics. Goes beyond "here is a list of domains" — produces ready-to-send pitches, handles the Reddit/Gutefrage/editorial/owned quadrants, and tracks citation gains week-over-week. Use when a Peec project has active competitor gaps and needs systematic off-site work, not just content production.
user-invocable: true
---

# Citation Outreach — From Actions to Actual Citations

Content zu schreiben reicht nicht. Der **Mehrheit der AI-Sichtbarkeits-Gewinne** kommt nicht aus einer neuen Seite auf der eigenen Domain, sondern aus **Zitaten auf Domains, die LLMs ohnehin crawlen**. Dieser Skill wandelt `get_actions`-Empfehlungen + aufgedeckte Forum-Threads in einen **systematischen Outreach-Prozess** — mit Pitch-Templates, Kontakt-Extraktion, Status-Tracking und Wirkungs-Messung.

Er ist die **Execution-Seite** der Growth-Loop, komplementär zu den Build-Seiten (`content-cluster-builder`, `content-write`).

---

## Wann einsetzen

- Nach `@ai-visibility-setup` Phase 8 oder `@peec-content-intel` Phase 6 — wenn die Opportunity-Liste steht
- Wöchentlich als Ritual: Top-3-Outreaches pro Woche, um beim Traffic nicht abhängig von Google zu bleiben
- Immer wenn Peec's `get_actions` hohe Opportunity-Scores für `editorial`, `ugc` oder `reference` ausgibt

Nicht einsetzen wenn:
- Keine Opportunity-Liste aus Peec vorliegt (erst `get_actions` laufen)
- Marke hat noch keine Referenz-Page / Case-Study, die man pitchen könnte (erst `content-write` für eigene Foundation)

---

## Eingaben

- **Pflicht:** Peec `project_id`
- **Optional:** `scope` — `editorial` / `ugc` / `reference` / `owned` / `all` (Default `all`)
- **Optional:** `weekly_cap` — wie viele Outreaches max pro Woche (Default 5)
- **Optional:** `own_asset_url` — eine eigene URL, die du aktiv pitchen willst (Case-Study, Pillar, Tool)

---

## Ablauf

### 1. Opportunity-Quellen aggregieren

Drei Peec-Calls parallel:

```
mcp__peec-ai__get_actions(project_id, scope="overview", start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="editorial", start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="reddit.com", start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="youtube.com", start_date, end_date)
```

Plus Gap-URLs aus dem Domain-Report:

```
mcp__peec-ai__get_domain_report(
    project_id, start_date, end_date,
    filters: [{field: "gap", operator: "gt", value: 0}],
    limit: 40
)
```

→ eine konsolidierte Kandidaten-Tabelle mit Spalten:
`target_url | domain | type | opportunity_score | retrieval % | citation_rate | mentioned_brand_ids`

### 2. Kandidaten in 4 Quadranten einsortieren

```
         │  Hoch Impact  │  Niedrig Impact
─────────┼───────────────┼──────────────────
Easy Ask │  QUICK WINS   │  SNACKABLE
         │  (Pitchen!)   │  (Wenn Zeit)
─────────┼───────────────┼──────────────────
Hard Ask │  STRATEGIC    │  DROP
         │  (Relationship│
         │   aufbauen)   │
```

**Impact-Signal:** `opportunity_score × retrieval_%`.
**Difficulty-Signal:**
- `easy` = Reddit-Thread (nur Antwort posten), Gutefrage, OMR-Forum
- `medium` = Editorial-Blog (Outreach-Email), LinkedIn-Autor
- `hard` = Major-Publikation, geschlossene Community

### 3. Kontakt-Extraktion pro Kandidat

Je nach Typ unterschiedliche Extraktion:

| Typ | Quelle für Kontakt |
|---|---|
| Editorial-Blog | `WebFetch(url)` → Autor-Box / LinkedIn-Link / Kontakt-Seite |
| Reddit-Thread | OP-Username sichtbar in `mcp__peec-ai__get_url_content` Output |
| YouTube | Channel-URL aus `channel_title` → `/about`-Seite für Kontakt |
| Gutefrage | kein Direkt-Kontakt (Antwort-Post direkt) |
| LinkedIn-Pulse | Autor-Profil im URL-Pfad |

Pro Kandidat strukturieren:
`target_url | target_type | contact_method | contact_handle | language | observed_topic_focus`

### 4. Pitch-Template-Auswahl

Pro Kandidaten-Typ einen Template-Typ:

#### Template: Editorial-Inclusion-Pitch (EN/DE)

```
Subject: Expert quote for your article on <thema> — <1-line angle>

Hi <Autor-Name>,

ich bin auf Ihren Artikel "<Title>" gestoßen, während ich recherchiert habe zu
<konkreter Bezug zum Artikel>. Eine Stelle würde aus meiner Praxis einen
zusätzlichen Winkel vertragen: <konkrete Stelle>.

Ich arbeite seit <N> Jahren als <Rolle> mit <Spezialisierung>. Kürzlich haben
wir bei einem <Projekt-Kontext> beobachtet, dass <konkrete Zahl / Erkenntnis>.

Hätten Sie Interesse an einem 2-3-Satz-Zitat oder einem kurzen Kasten mit
meinem Take? Ich liefere Text + Name + Headshot innerhalb von 48 Stunden.

<Signatur mit antonioblago.de + 1 Referenz-URL>
```

**Regel:** Konkrete Stelle zitieren, konkrete Ergänzung anbieten, kein generisches
„ich würde gerne kooperieren".

#### Template: Reddit-Thread-Antwort

Kein klassischer Pitch — direkte, substanzielle Antwort (150-300 Wörter) auf die OP-Frage. Regeln:

1. **Erste 2 Sätze:** direkte Antwort auf die Frage, keine Einleitung.
2. **Mittelteil:** konkrete Methode / Zahl / Beispiel aus eigener Praxis.
3. **Optional am Ende:** 1 eigene Quelle, nur wenn sie die Antwort vervollständigt — niemals als Call-to-Action.
4. **Sprache:** die Sprache des Original-Posts.
5. **Username:** authentischer Account, keine Brand-Accounts (Reddit-Policy).

#### Template: Gutefrage/Forum-Antwort

Identisch zu Reddit-Template, aber 100-200 Wörter reichen — Gutefrage-User bevorzugen kompakte Antworten.

#### Template: YouTube-Kommentar / Pin-Pitch

Zweistufig:
1. **Substanzieller Kommentar** unter dem Video (300-500 Zeichen, Frage + Ergänzung)
2. **Nach 48h ohne Response:** Email an Channel-Owner mit Referenz zu 3 eigenen Videos / Blog-Inhalten, die zum Channel-Thema passen

### 5. Pitch-Template mit Projekt-Kontext befüllen

```
mcp__peec-ai__get_project(project_id) / mcp__visiblyai__get_project(project_id)
  → brand_name, unique_selling_points, custom_content_prompt, crawl_summary
```

Falls nur Claude Code MCP verfügbar (kein Visibly):
  → Projekt-Kontext aus bestehenden Chat-Infos + `get_brand_report` aggregieren

Claude füllt jetzt pro Kandidat das passende Template mit **spezifischen** Details:
- statt `<konkrete Stelle>` → echtes Quote aus der Target-URL
- statt `<konkrete Zahl>` → echte Zahl aus dem eigenen Projekt (Retainer-Client-Fall, Traffic-Lift, Case-Study)
- statt `<Projekt-Kontext>` → konkrete Branche des Target-Autors

### 6. Outreach-Tracker (persistent)

Neue Datei im Projekt-Workspace:
```
<project>/outreach/YYYY-Wkk_outreach_log.md
```

Format:

```markdown
# Outreach Log — Week <ISO-Week>

| # | Target | Type | Status     | Sent      | Replied | Citation | Notes |
|---|--------|------|-----------|-----------|---------|----------|-------|
| 1 | evergreen.media/ratgeber/ki-seo | editorial | sent | 2026-04-22 | pending | — | Pitched expert quote on retainer-pricing |
| 2 | r/selbststaendig/comments/xyz | reddit | posted | 2026-04-22 | — | answer_score=12 | — |
| 3 | ... |
```

Status-Werte: `queued` → `sent` / `posted` → `replied` → `citation_live` / `declined` / `ignored`

### 7. Success-Metrik + Re-Feed in Growth-Loop

Nach 4 Wochen pro Target:

```
Für jede target_url mit status=citation_live:
    mcp__peec-ai__get_url_report(filters: [{field: "url", values: [<target_url>]}])
    → retrievals vorher vs nachher messen
    → aus get_brand_report: ist die own-brand-visibility für Prompts
       gestiegen, die diese URL als Source hatten?
```

Gewinner (Citation-Gain > Baseline) werden im `growth-loop-reporter`-Skill als
"funktionierendes Hebel-Muster" gemerkt → zukünftige Pitches priorisieren ähnliche Ziele.

---

## Quick Command Reference

| Schritt | Tool |
|---|---|
| Opportunity-Quellen | `mcp__peec-ai__get_actions(scope=overview/editorial/ugc)` |
| Gap-URLs (Konkurrenten drin, du nicht) | `mcp__peec-ai__get_domain_report(filters: gap>0)` |
| Thread-Kontext + OP | `mcp__peec-ai__get_url_content` |
| Kontakt-Extraktion | `WebFetch` auf Target-URL |
| Projekt-Frame für Pitch | `mcp__peec-ai__list_projects` + `get_project` |
| Citation-Messung | `mcp__peec-ai__get_url_report(dimensions=["date"])` |

---

## Output-Qualitäts-Kriterien

Ein Outreach-Batch ist NUR dann fertig, wenn:

1. **Maximal `weekly_cap` Pitches.** 5 hochwertige Pitches schlagen 20 generische.
2. **Jeder Pitch hat ein konkretes Quote.** Kein „interessanter Artikel" — ein Satz aus dem Target wird direkt zitiert.
3. **Jeder Pitch bietet etwas Spezifisches.** Kein „ich habe Expertise in X" — „ich liefere <konkretes Asset> bis <Datum>".
4. **Tracker ist aktiv.** Alle Pitches in der Log-Datei, mit `status=sent` / `posted` nach Versand.
5. **Success-Kriterium pro Pitch klar.** „Ich erwarte eine Erwähnung in der <Sektion>, messbar via Peec `get_url_report` binnen 6 Wochen."

---

## Häufige Fehler

- **Generische Pitches:** „ich würde gerne zu Ihrem Blog beitragen" ignoriert wird jedes Mal. Spezifisch zitieren oder weglassen.
- **Reddit/Gutefrage mit Brand-Account:** bannt dich aus der Community. Nur persönliche Accounts, keine Firmen.
- **Kein Follow-up-Tracking:** 30-50% aller Editorial-Citations kommen aus Follow-ups nach 7-10 Tagen. Ohne Tracker verloren.
- **Zu viel auf einmal:** 3 gute Pitches pro Woche, die durchdacht sind, schlagen 15 Massen-Pitches. Capacity > Volumen.
- **Kein Measurement-Loop:** wer seine Citation-Gewinner nicht trackt, kann das nächste Mal nicht priorisieren.
