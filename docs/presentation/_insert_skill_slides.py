"""Insert 6 dedicated skill slides into peec-ai-skills-deck.html.

Old deck: 20 slides. Only 3 skills have dedicated pages (peec-start, peec-checkup, peec-agent).
Missing: peec-setup, peec-cluster, peec-content-intel, peec-outreach,
         peec-report, peec-learn.

Insertion: after slide 8 (peec-agent), before slide 9 (hooks).
Result: 26 slides. Old slides 9–20 renumbered to 15–26. Totals updated to `/ 26`.
"""
from pathlib import Path
import re

HTML_PATH = Path(__file__).with_name("peec-ai-skills-deck.html")

text = HTML_PATH.read_text(encoding="utf-8")


def slide_block(num: int, skill_tag: str, title_html: str, subtitle_html: str, body_html: str) -> str:
    return f'''
<!-- ============ SLIDE {num:02d} — {skill_tag.upper().replace("/", "")} ============ -->
<div class="slide content">
  <div class="top-bar"></div><div class="top-bar-accent"></div>
  <div class="brand">peec-ai-skills</div><div class="slide-num">{num:02d} / 26</div>
  <div class="h-bar" style="margin-top:8mm;"></div>
  <h1 class="s-title">{title_html}</h1>
  <h2 class="s-sub">{subtitle_html}</h2>

  {body_html}

  <div class="footer"><div class="footer-l">Antonio Blago · info@antonioblago.com</div><div class="footer-r">Part 1 — Pitch</div></div>
</div>
'''


# ---- Slide 09 · /peec-setup ----
s09 = slide_block(
    9, "/peec-setup",
    "/peec-setup &mdash; 9 phases, full-funnel coverage.",
    "Takes a Peec project from empty (or broken) to operator-ready. Owns <code>setup_state.json</code> &mdash; every other skill refuses to run without it.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>"Set up Peec for &lt;client&gt;"</li>
        <li>"My Peec competitors are wrong"</li>
        <li>"Design prompts for my customer journey"</li>
        <li>"Restructure topics / tags"</li>
        <li>Audit of an existing tracking setup</li>
      </ul>
      <h3 class="s-h3">Scope modes</h3>
<pre>scope=full                   # greenfield, all 9 phases
scope=audit                  # live-diff, re-run drifted phases
scope=partial:gsc_mapping    # jump to one phase
scope=import                 # brownfield reconstruction</pre>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">The 9 phases</h3>
      <ol>
        <li><strong>Phase 0</strong> &mdash; state check &amp; mode selection</li>
        <li><strong>Competitor discovery</strong> from real AI chats (not Google)</li>
        <li><strong>Customer-journey prompts</strong>: Awareness &rarr; Consideration &rarr; Decision &rarr; Retention</li>
        <li><strong>Topic taxonomy</strong> (one topic per prompt, funnel-aligned)</li>
        <li><strong>Tag taxonomy</strong> (cross-cut: branded/non-branded/informational/transactional/&hellip;)</li>
        <li><strong>GSC keyword mapping</strong> via Visibly</li>
        <li><strong>Forum pain-point mining</strong> (Reddit, Gutefrage, t3n, OMR)</li>
        <li><strong>Hero prompt</strong> definition</li>
        <li><strong>P0/P1/P2 backlog</strong> + state write</li>
      </ol>
      <div class="info-box teal" style="margin-top:3mm;">
        <strong>Never silently defaults to EN/en.</strong> Country + language travel through every downstream skill via <code>setup_state.json</code>.
      </div>
    </div>
  </div>
""")

# ---- Slide 12 · /peec-cluster ----
s12 = slide_block(
    12, "/peec-cluster",
    "/peec-cluster &mdash; zones, not keyword groups.",
    "Reduces a flat prompt set to 4–8 <strong>strategic zones</strong>, each with one structural weakness in competition and one measurable metric. Output is a strategic map &mdash; not a content calendar.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">A zone is valid only when all three axes line up</h3>
<pre>      Intent
       &uarr;
Visibility gap
       &uarr;
Demand signal</pre>
      <p class="legend" style="margin-top:2mm;">If a candidate zone fails any axis &rarr; merged or dropped.</p>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>&ge;20 Peec prompts &mdash; team has lost the overview</li>
        <li>Quarterly strategy refresh</li>
        <li>Before an investment conversation ("what is our AI content strategy?")</li>
      </ul>
      <p class="muted" style="font-size:9pt;">Do not use with &lt;10 prompts or when funnel stages aren't set.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; one zone map + Peec tags</h3>
      <ul>
        <li><strong>Markdown zone map</strong> &mdash; one zone per section, each with: structural weakness · measurable metric · exact next action</li>
        <li><strong>Peec tag per zone</strong> (<code>zone:&lt;slug&gt;</code>) &mdash; all prompts retagged so <span class="tag">/peec-report</span> can measure zone lift later</li>
      </ul>
      <h3 class="s-h3">Per-zone anatomy</h3>
<pre class="light">## Zone: KI-SEO Retainer Decision
Structural weakness:
  Competitors rank listicles with USP matrix,
  we have 1 case study, no comparison piece.
Metric (4 weeks):
  Zone visibility 3% &rarr; &gt;10%
Next action:
  /peec-content-intel pr_a38381d4
  &rarr; brief &rarr; publish pillar
Prompts (6):  pr_a38381d4, pr_c2..., ...
Evidence:     forum quotes &middot; SERP patterns</pre>
    </div>
  </div>
""")

# ---- Slide 13 · /peec-content-intel ----
s13 = slide_block(
    13, "/peec-content-intel",
    "/peec-content-intel &mdash; one prompt in, one brief out.",
    "For one Peec prompt the brand is losing: sub-queries (Query Fan-Out), verbatim buyer pains, competitor URL scoring, outline, focus keywords, outreach targets. Publish-ready.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Data sources (combined)</h3>
      <ul>
        <li><strong>Peec</strong> &mdash; prompt visibility, source URLs, scraped chats</li>
        <li><strong>Visibly AI</strong> &mdash; backlinks, onpage, keywords, GSC, <strong>Query Fan-Out</strong></li>
        <li><strong>Forum mining</strong> &mdash; Reddit, Gutefrage, t3n, OMR (country-filtered)</li>
      </ul>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>"Which content wins Peec prompt X?"</li>
        <li>"Analyze the sources competitors get cited for"</li>
        <li>"What's the gap between me and competitor.de?"</li>
      </ul>
      <p class="muted" style="font-size:9pt;">Requires &ge;24h of Peec data on the target prompt.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; <code>briefs/YYYY-MM-DD_&lt;slug&gt;/</code></h3>
<pre class="light">brief.md                 &larr; publish-ready brief
competitor-urls.json     &larr; scored attackability
forum-pains.json         &larr; verbatim quotes
scoring.json             &larr; raw Query Fan-Out scores</pre>

      <h3 class="s-h3">Query Fan-Out in practice</h3>
      <div class="info-box">
        Your page "<em>antonioblago.de</em>" on seed <em>"SEO Freelancer"</em>:<br>
        Coverage <strong>53.3%</strong> &middot; 8 of 15 sub-queries covered<br>
        <strong>7 concrete gaps</strong>: "Aufgabenbereiche eines SEO Freelancers" &middot; "Welche SEO Tools nutzen Freelancer?" &middot; "Preise und Leistungen Vergleich" &hellip;
      </div>
      <p class="legend">Each gap maps 1:1 to an H2/H3 in the brief outline.</p>
    </div>
  </div>
""")

# ---- Slide 15 · /peec-outreach ----
s15 = slide_block(
    15, "/peec-outreach",
    "/peec-outreach &mdash; off-page pipeline, not a domain list.",
    "Most AI-visibility lift comes from citations on domains LLMs already crawl. Turns <code>get_actions</code> + UGC discovery into a prioritized pipeline with concrete, target-specific pitches &mdash; capped at 5/week.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Four quadrants, one pipeline</h3>
      <table class="data">
        <thead><tr><th>Quadrant</th><th>Example</th><th>Deliverable</th></tr></thead>
        <tbody>
          <tr><td><span class="pill orange">OWNED</span></td><td>Own site</td><td>Content update</td></tr>
          <tr><td><span class="pill">EDITORIAL</span></td><td>t3n, OMR</td><td>Pitch + contact</td></tr>
          <tr><td><span class="pill navy">REFERENCE</span></td><td>Wikipedia</td><td>Edit request</td></tr>
          <tr><td><span class="pill teal">UGC</span></td><td>Reddit, Gutefrage</td><td>Answer draft</td></tr>
        </tbody>
      </table>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>After <span class="tag">/peec-content-intel</span> &mdash; opportunity list is in</li>
        <li>Weekly ritual: 3–5 quality pitches</li>
        <li>When <code>get_actions</code> surfaces high-opportunity rows</li>
      </ul>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Per-target output</h3>
      <ul>
        <li>Domain + contact (author, editor, admin)</li>
        <li>Pitch text, tonality-matched to target</li>
        <li>Concrete quote + concrete offer (case study, data, expert quote)</li>
        <li>Status tracker: <code>queued &rarr; sent &rarr; replied &rarr; cited | rejected</code></li>
      </ul>

      <h3 class="s-h3">Measurement loop (4 weeks)</h3>
<pre class="light">Week 0  baseline: citations from Peec
Week 1  send 5 pitches
Week 2  send 5 pitches
Week 3  send 5 pitches
Week 4  re-pull Peec &rarr; citations delta

Attribution summary feeds into
/peec-report as a scored
outreach channel.</pre>
      <p class="legend">Tracker lives at <code>&lt;project&gt;/outreach/YYYY-Wkk_outreach_log.md</code>.</p>
    </div>
  </div>
""")

# ---- Slide 16 · /peec-report ----
s16 = slide_block(
    16, "/peec-report",
    "/peec-report &mdash; 400 words beats 15 charts.",
    "Closes the feedback loop every week. Three questions per cycle, answered in ≤400 words &mdash; plus a <code>learnings.json</code> that feeds the next orchestrator run as priors.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Three questions, one narrative</h3>
      <ol>
        <li><strong>What moved?</strong> &mdash; visibility trend per prompt / cluster / zone</li>
        <li><strong>Why?</strong> &mdash; which specific investment caused which lift</li>
        <li><strong>What next?</strong> &mdash; 3 prioritized actions + 1 stop-doing</li>
      </ol>
      <p class="legend" style="margin-top:2mm;">Fifteen charts don't get read. 400 words do.</p>

      <h3 class="s-h3">Cadence</h3>
      <ul>
        <li><strong>Weekly</strong> &mdash; active projects with running content + outreach</li>
        <li><strong>Monthly</strong> &mdash; retainer projects in maintenance</li>
        <li><strong>Quarterly</strong> &mdash; strategy review &mdash; feeds next cluster run</li>
      </ul>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; <code>&lt;project&gt;/growth_loop/YYYY-MM-DD_report.md</code></h3>
<pre style="font-size:7.5pt;line-height:1.4;">
## What moved
Brand visibility 8% &rarr; 12% in 14d.
Decision stage 3% &rarr; 9% (+200%).
Awareness flat at 24%.

## Why
+ Published pillar "KI-SEO Retainer"  → +6%
+ Reddit answer on r/selbststaendig   → +3 citations
- t3n editorial pitch: no reply

## Next
1. Clone pillar pattern for Awareness hero
2. Double down on Reddit (weekly cadence)
3. STOP t3n pitches — audience fit low
</pre>
      <div class="info-box teal" style="margin-top:2mm;">
        <code>learnings.json</code> &rarr; consumed by next <span class="tag">/peec-cluster</span> &amp; <span class="tag">/peec-outreach</span> run as priors.
      </div>
    </div>
  </div>
""")

# ---- Slide 17 · /peec-learn ----
s17 = slide_block(
    17, "/peec-learn",
    "/peec-learn &mdash; cross-project memory layer.",
    "Project-local learnings live in <code>growth_loop/learnings.json</code>. This skill <strong>promotes</strong> them across projects: lessons from project A become priors for project B.",
    """
  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Two modes</h3>
      <ul>
        <li><strong>Write</strong> &mdash; extract 1–3 patterns from a just-produced artifact (decision, brief, zone map, outreach log, learnings.json) and persist to SkillMind.</li>
        <li><strong>Read</strong> &mdash; on orchestrator start, recall patterns matching gap type / project / skill &rarr; hand back as priors.</li>
      </ul>

      <h3 class="s-h3">Pattern quality bar</h3>
      <ul>
        <li><strong>Causal</strong> &mdash; X caused Y, not correlation</li>
        <li><strong>Falsifiable</strong> &mdash; states the condition for being wrong</li>
        <li><strong>Evidence-backed</strong> &mdash; links the artifact that produced it</li>
      </ul>
      <p class="muted" style="font-size:9pt;">No speculation. Artifact must have a measured outcome.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Backend</h3>
      <div class="info-box blue">
        Pinecone-backed semantic memory via <code>mcp__skillmind__*</code>.<br>
        Fallback when MCP unavailable: append to <code>&lt;project&gt;/growth_loop/patterns.md</code>.
      </div>

      <h3 class="s-h3">Example pattern (write mode)</h3>
<pre class="light" style="font-size:8.5pt;">{
  "title":
    "DE B2B: UGC beats editorial 8× on AI citations",
  "tags": ["peec", "DE", "outreach", "UGC"],
  "summary":
    "On DE B2B SEO projects, Reddit + Gutefrage
     answers produced 40% reply rate and +3
     citations per week. Editorial pitches to
     t3n/OMR: 5% reply, 0 citations in 4 weeks.",
  "provenance": {
    "project_id": "or_bf5b...",
    "source_skill": "peec-report",
    "date": "2026-04-23"
  }
}</pre>
      <p class="legend">On next project, <span class="tag">/peec-outreach</span> recalls this as a prior before building the pipeline.</p>
    </div>
  </div>
""")

# ---- Compose insertion blocks ----
# After slide 8 (peec-agent), before slide 9 (hooks), we insert slides 09-14:
# 09 peec-setup
# 10 peec-checkup (already exists — we reuse by moving)  ← but we also want new slides
#
# Simpler layout: keep existing slides 6,7,8 for the three "hero" skills (peec-start, peec-checkup,
# peec-agent), then insert 6 more dedicated slides directly after slide 8:
#   09 peec-setup
#   10 peec-cluster
#   11 peec-content-intel
#   12 peec-outreach
#   13 peec-report
#   14 peec-learn
# After these, existing slides 9..20 become 15..26.

new_slides = "\n".join([
    slide_block(9,  "/peec-setup",
                "/peec-setup &mdash; 9 phases, full-funnel coverage.",
                "Takes a Peec project from empty (or broken) to operator-ready. Owns <code>setup_state.json</code> &mdash; every other skill refuses to run without it.",
                s09.split('<h2 class="s-sub">')[1].split('</h2>')[1].split('<div class="footer">')[0].strip()),
])

# Actually the split is too hacky. Rebuild cleanly using concatenation.

def mk(n, tag, title, sub, body):
    return f'''
<!-- ============ SLIDE {n:02d} — {tag.upper().replace("/", "").strip()} ============ -->
<div class="slide content">
  <div class="top-bar"></div><div class="top-bar-accent"></div>
  <div class="brand">peec-ai-skills</div><div class="slide-num">{n:02d} / 26</div>
  <div class="h-bar" style="margin-top:8mm;"></div>
  <h1 class="s-title">{title}</h1>
  <h2 class="s-sub">{sub}</h2>

{body}

  <div class="footer"><div class="footer-l">Antonio Blago · info@antonioblago.com</div><div class="footer-r">Part 1 — Pitch</div></div>
</div>
'''

BODY_AVS = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>"Set up Peec for &lt;client&gt;"</li>
        <li>"My Peec competitors are wrong"</li>
        <li>"Design prompts for my customer journey"</li>
        <li>"Restructure topics / tags"</li>
        <li>Audit of an existing tracking setup</li>
      </ul>
      <h3 class="s-h3">Scope modes</h3>
<pre>scope=full                   # greenfield, all 9 phases
scope=audit                  # live-diff, re-run drifted phases
scope=partial:gsc_mapping    # jump to one phase
scope=import                 # brownfield reconstruction</pre>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">The 9 phases</h3>
      <ol>
        <li><strong>Phase 0</strong> &mdash; state check &amp; mode selection</li>
        <li><strong>Competitor discovery</strong> from real AI chats (not Google)</li>
        <li><strong>Customer-journey prompts</strong>: Awareness &rarr; Consideration &rarr; Decision &rarr; Retention</li>
        <li><strong>Topic taxonomy</strong> (one topic per prompt, funnel-aligned)</li>
        <li><strong>Tag taxonomy</strong> (cross-cut: branded/non-branded/informational/transactional/&hellip;)</li>
        <li><strong>GSC keyword mapping</strong> via Visibly</li>
        <li><strong>Forum pain-point mining</strong> (Reddit, Gutefrage, t3n, OMR)</li>
        <li><strong>Hero prompt</strong> definition</li>
        <li><strong>P0/P1/P2 backlog</strong> + state write</li>
      </ol>
      <div class="info-box teal" style="margin-top:3mm;">
        <strong>Never silently defaults to EN/en.</strong> Country + language travel through every downstream skill via <code>setup_state.json</code>.
      </div>
    </div>
  </div>"""

BODY_CCB = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">A zone is valid only when all three axes line up</h3>
<pre>      Intent
       &uarr;
Visibility gap
       &uarr;
Demand signal</pre>
      <p class="legend" style="margin-top:2mm;">If a candidate zone fails any axis &rarr; merged or dropped.</p>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>&ge;20 Peec prompts &mdash; team has lost the overview</li>
        <li>Quarterly strategy refresh</li>
        <li>Before an investment conversation ("what is our AI content strategy?")</li>
      </ul>
      <p class="muted" style="font-size:9pt;">Do not use with &lt;10 prompts or when funnel stages aren't set.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; one zone map + Peec tags</h3>
      <ul>
        <li><strong>Markdown zone map</strong> &mdash; one zone per section, each with: structural weakness · measurable metric · exact next action</li>
        <li><strong>Peec tag per zone</strong> (<code>zone:&lt;slug&gt;</code>) &mdash; all prompts retagged so <span class="tag">/peec-report</span> can measure zone lift later</li>
      </ul>
      <h3 class="s-h3">Per-zone anatomy</h3>
<pre class="light">## Zone: KI-SEO Retainer Decision
Structural weakness:
  Competitors rank listicles with USP matrix,
  we have 1 case study, no comparison piece.
Metric (4 weeks):
  Zone visibility 3% &rarr; &gt;10%
Next action:
  /peec-content-intel pr_a38381d4
  &rarr; brief &rarr; publish pillar
Prompts (6):  pr_a38381d4, pr_c2..., ...
Evidence:     forum quotes &middot; SERP patterns</pre>
    </div>
  </div>"""

BODY_PCI = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Data sources (combined)</h3>
      <ul>
        <li><strong>Peec</strong> &mdash; prompt visibility, source URLs, scraped chats</li>
        <li><strong>Visibly AI</strong> &mdash; backlinks, onpage, keywords, GSC, <strong>Query Fan-Out</strong></li>
        <li><strong>Forum mining</strong> &mdash; Reddit, Gutefrage, t3n, OMR (country-filtered)</li>
      </ul>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>"Which content wins Peec prompt X?"</li>
        <li>"Analyze the sources competitors get cited for"</li>
        <li>"What's the gap between me and competitor.de?"</li>
      </ul>
      <p class="muted" style="font-size:9pt;">Requires &ge;24h of Peec data on the target prompt.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; <code>briefs/YYYY-MM-DD_&lt;slug&gt;/</code></h3>
<pre class="light">brief.md                 &larr; publish-ready brief
competitor-urls.json     &larr; scored attackability
forum-pains.json         &larr; verbatim quotes
scoring.json             &larr; raw Query Fan-Out scores</pre>

      <h3 class="s-h3">Query Fan-Out in practice</h3>
      <div class="info-box">
        Your page "<em>antonioblago.de</em>" on seed <em>"SEO Freelancer"</em>:<br>
        Coverage <strong>53.3%</strong> &middot; 8 of 15 sub-queries covered<br>
        <strong>7 concrete gaps</strong>: "Aufgabenbereiche eines SEO Freelancers" &middot; "Welche SEO Tools nutzen Freelancer?" &middot; "Preise und Leistungen Vergleich" &hellip;
      </div>
      <p class="legend">Each gap maps 1:1 to an H2/H3 in the brief outline.</p>
    </div>
  </div>"""

BODY_CO = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Four quadrants, one pipeline</h3>
      <table class="data">
        <thead><tr><th>Quadrant</th><th>Example</th><th>Deliverable</th></tr></thead>
        <tbody>
          <tr><td><span class="pill orange">OWNED</span></td><td>Own site</td><td>Content update</td></tr>
          <tr><td><span class="pill">EDITORIAL</span></td><td>t3n, OMR</td><td>Pitch + contact</td></tr>
          <tr><td><span class="pill navy">REFERENCE</span></td><td>Wikipedia</td><td>Edit request</td></tr>
          <tr><td><span class="pill teal">UGC</span></td><td>Reddit, Gutefrage</td><td>Answer draft</td></tr>
        </tbody>
      </table>

      <h3 class="s-h3">When to invoke</h3>
      <ul>
        <li>After <span class="tag">/peec-content-intel</span> &mdash; opportunity list is in</li>
        <li>Weekly ritual: 3–5 quality pitches</li>
        <li>When <code>get_actions</code> surfaces high-opportunity rows</li>
      </ul>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Per-target output</h3>
      <ul>
        <li>Domain + contact (author, editor, admin)</li>
        <li>Pitch text, tonality-matched to target</li>
        <li>Concrete quote + concrete offer (case study, data, expert quote)</li>
        <li>Status tracker: <code>queued &rarr; sent &rarr; replied &rarr; cited | rejected</code></li>
      </ul>

      <h3 class="s-h3">Measurement loop (4 weeks)</h3>
<pre class="light">Week 0  baseline: citations from Peec
Week 1  send 5 pitches
Week 2  send 5 pitches
Week 3  send 5 pitches
Week 4  re-pull Peec &rarr; citations delta

Attribution summary feeds into
/peec-report as a scored
outreach channel.</pre>
      <p class="legend">Tracker lives at <code>&lt;project&gt;/outreach/YYYY-Wkk_outreach_log.md</code>.</p>
    </div>
  </div>"""

BODY_GLR = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Three questions, one narrative</h3>
      <ol>
        <li><strong>What moved?</strong> &mdash; visibility trend per prompt / cluster / zone</li>
        <li><strong>Why?</strong> &mdash; which specific investment caused which lift</li>
        <li><strong>What next?</strong> &mdash; 3 prioritized actions + 1 stop-doing</li>
      </ol>
      <p class="legend" style="margin-top:2mm;">Fifteen charts don't get read. 400 words do.</p>

      <h3 class="s-h3">Cadence</h3>
      <ul>
        <li><strong>Weekly</strong> &mdash; active projects with running content + outreach</li>
        <li><strong>Monthly</strong> &mdash; retainer projects in maintenance</li>
        <li><strong>Quarterly</strong> &mdash; strategy review &mdash; feeds next cluster run</li>
      </ul>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Output &mdash; <code>&lt;project&gt;/growth_loop/YYYY-MM-DD_report.md</code></h3>
<pre style="font-size:7.5pt;line-height:1.4;">
## What moved
Brand visibility 8% &rarr; 12% in 14d.
Decision stage 3% &rarr; 9% (+200%).
Awareness flat at 24%.

## Why
+ Published pillar "KI-SEO Retainer"  &rarr; +6%
+ Reddit answer on r/selbststaendig   &rarr; +3 citations
- t3n editorial pitch: no reply

## Next
1. Clone pillar pattern for Awareness hero
2. Double down on Reddit (weekly cadence)
3. STOP t3n pitches &mdash; audience fit low
</pre>
      <div class="info-box teal" style="margin-top:2mm;">
        <code>learnings.json</code> &rarr; consumed by next <span class="tag">/peec-cluster</span> &amp; <span class="tag">/peec-outreach</span> run as priors.
      </div>
    </div>
  </div>"""

BODY_SML = """  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Two modes</h3>
      <ul>
        <li><strong>Write</strong> &mdash; extract 1–3 patterns from a just-produced artifact (decision, brief, zone map, outreach log, learnings.json) and persist to SkillMind.</li>
        <li><strong>Read</strong> &mdash; on orchestrator start, recall patterns matching gap type / project / skill &rarr; hand back as priors.</li>
      </ul>

      <h3 class="s-h3">Pattern quality bar</h3>
      <ul>
        <li><strong>Causal</strong> &mdash; X caused Y, not correlation</li>
        <li><strong>Falsifiable</strong> &mdash; states the condition for being wrong</li>
        <li><strong>Evidence-backed</strong> &mdash; links the artifact that produced it</li>
      </ul>
      <p class="muted" style="font-size:9pt;">No speculation. Artifact must have a measured outcome.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Backend</h3>
      <div class="info-box blue">
        Pinecone-backed semantic memory via <code>mcp__skillmind__*</code>.<br>
        Fallback when MCP unavailable: append to <code>&lt;project&gt;/growth_loop/patterns.md</code>.
      </div>

      <h3 class="s-h3">Example pattern (write mode)</h3>
<pre class="light" style="font-size:8.5pt;">{
  "title":
    "DE B2B: UGC beats editorial 8× on AI citations",
  "tags": ["peec", "DE", "outreach", "UGC"],
  "summary":
    "On DE B2B SEO projects, Reddit + Gutefrage
     answers produced 40% reply rate and +3
     citations per week. Editorial pitches to
     t3n/OMR: 5% reply, 0 citations in 4 weeks.",
  "provenance": {
    "project_id": "or_bf5b...",
    "source_skill": "peec-report",
    "date": "2026-04-23"
  }
}</pre>
      <p class="legend">On next project, <span class="tag">/peec-outreach</span> recalls this as a prior before building the pipeline.</p>
    </div>
  </div>"""

new_block = "\n".join([
    mk(9,  "/peec-setup",   "/peec-setup &mdash; 9 phases, full-funnel coverage.",
       "Takes a Peec project from empty (or broken) to operator-ready. Owns <code>setup_state.json</code> &mdash; every other skill refuses to run without it.", BODY_AVS),
    mk(10, "/peec-cluster", "/peec-cluster &mdash; zones, not keyword groups.",
       "Reduces a flat prompt set to 4&ndash;8 <strong>strategic zones</strong>, each with one structural weakness in competition and one measurable metric. Output is a strategic map &mdash; not a content calendar.", BODY_CCB),
    mk(11, "/peec-content-intel", "/peec-content-intel &mdash; one prompt in, one brief out.",
       "For one Peec prompt the brand is losing: sub-queries (Query Fan-Out), verbatim buyer pains, competitor URL scoring, outline, focus keywords, outreach targets. Publish-ready.", BODY_PCI),
    mk(12, "/peec-outreach", "/peec-outreach &mdash; off-page pipeline, not a domain list.",
       "Most AI-visibility lift comes from citations on domains LLMs already crawl. Turns <code>get_actions</code> + UGC discovery into a prioritized pipeline with concrete, target-specific pitches &mdash; capped at 5/week.", BODY_CO),
    mk(13, "/peec-report", "/peec-report &mdash; 400 words beats 15 charts.",
       "Closes the feedback loop every week. Three questions per cycle, answered in &le;400 words &mdash; plus a <code>learnings.json</code> that feeds the next orchestrator run as priors.", BODY_GLR),
    mk(14, "/peec-learn", "/peec-learn &mdash; cross-project memory layer.",
       "Project-local learnings live in <code>growth_loop/learnings.json</code>. This skill <strong>promotes</strong> them across projects: lessons from project A become priors for project B.", BODY_SML),
])

# ---- Find insertion point: right before the existing slide 9 (hooks) ----
anchor = "<!-- ============ SLIDE 9 — HOOKS ============ -->"
if anchor not in text:
    raise SystemExit("Anchor for SLIDE 9 — HOOKS not found")

text = text.replace(anchor, new_block + "\n" + anchor)

# ---- Update total count from /20 to /26 across all slides ----
text = text.replace("/ 20</div>", "/ 26</div>")

# ---- Renumber existing slides 9..20 → 15..26 ----
# We changed `XX / 26` for what was originally 09..20 to reflect their new position.
# After our insert and the previous replace, they currently read as e.g. "09 / 26" for hooks — wrong.
# The new slides we inserted use 09..14 correctly. The old slides that were 09..20 now need to show 15..26.
# We already have 6 new slides with numbers 09..14 as correct strings.
# Old slides still say 09..20 — we must bump them by +6.

# Process from highest to lowest to avoid cascade renames.
renames = [
    ("19 / 26", "25 / 26"),  # old 19 → 25
    ("18 / 26", "24 / 26"),
    ("17 / 26", "23 / 26"),
    ("16 / 26", "22 / 26"),
    ("15 / 26", "21 / 26"),
    ("14 / 26", "20 / 26"),
    ("13 / 26", "19 / 26"),
    ("12 / 26", "18 / 26"),
    ("11 / 26", "17 / 26"),
    ("10 / 26", "16 / 26"),
    ("09 / 26", "15 / 26"),
]

# BUT — our NEW slides use 09..14 which would be affected by the renames for 09..14.
# To protect the new numbers we first swap them to unique sentinels, rename the old, then restore.

SENTINEL_MAP = {
    "09 / 26": "§§S09§§",
    "10 / 26": "§§S10§§",
    "11 / 26": "§§S11§§",
    "12 / 26": "§§S12§§",
    "13 / 26": "§§S13§§",
    "14 / 26": "§§S14§§",
}

# Count occurrences before sentinel: new slides have 1 each (09..14), old slides also have 1 each (09..14).
# We need to distinguish. Trick: new slides appear BEFORE the anchor (SLIDE 9 — HOOKS) in the file,
# old slides appear AFTER. Since we inserted `new_block + "\n" + anchor`, split at anchor.

head, _, tail = text.partition(anchor)

# In `head`, slides 09..14 are the NEW ones → protect with sentinels.
for k, v in SENTINEL_MAP.items():
    head = head.replace(k, v, 1)  # only the first occurrence in each slide block

# Tail still contains old slides with numbers 09..20 (as /26). Apply renames on tail.
# Need to rename 20 → 26, 19 → 25, ... 09 → 15.
tail_renames = [
    ("20 / 26", "26 / 26"),  # old 20 → 26 (CTA)
    ("19 / 26", "25 / 26"),
    ("18 / 26", "24 / 26"),
    ("17 / 26", "23 / 26"),
    ("16 / 26", "22 / 26"),
    ("15 / 26", "21 / 26"),
    ("14 / 26", "20 / 26"),
    ("13 / 26", "19 / 26"),
    ("12 / 26", "18 / 26"),
    ("11 / 26", "17 / 26"),
    ("10 / 26", "16 / 26"),
    ("09 / 26", "15 / 26"),
]

for old, new in tail_renames:
    tail = tail.replace(old, new)

# Restore sentinels in head
for k, v in SENTINEL_MAP.items():
    head = head.replace(v, k)

text = head + anchor + tail

# ---- Update cover total indicator if present ("/ 20" in any remaining text — there shouldn't be any now) ----
# Save
HTML_PATH.write_text(text, encoding="utf-8")
print(f"Wrote updated deck: {HTML_PATH}")
print(f"Total slides now: 26 (was 20)")
