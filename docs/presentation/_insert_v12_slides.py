"""Insert 2 v1.2-schema slides after slide 16 (setup_state) and before Part-2 divider.
Updates: total count /26 -> /28 ; renumber old 17-26 -> 19-28.
"""
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from pathlib import Path

HTML = Path(r"C:\Users\anton\PycharmProjects\peec-ai-skills\docs\presentation\peec-ai-skills-deck.html")

SLIDE_17 = """
<!-- ============ SLIDE 17 - V1.2 SCHEMA ============ -->
<div class="slide content">
  <div class="top-bar"></div><div class="top-bar-accent"></div>
  <div class="brand">peec-ai-skills</div><div class="slide-num">17 / 28</div>
  <div class="h-bar" style="margin-top:8mm;"></div>
  <h1 class="s-title">v1.2 schema &mdash; business type &amp; audience as first-class inputs.</h1>
  <h2 class="s-sub"><code>peec-setup</code> Phase 0.5 elicits three fields once and persists them. Every downstream content skill reads them. No more generic briefs.</h2>

  <div class="two-col">
    <div class="col col-l">
      <h3 class="s-h3">Three new fields in <code>setup_state.json</code></h3>
<pre class="light">{
  "setup_version": "1.2",

  "business_type": "b2b-service",
  // one of: b2b-service | b2c-ecommerce
  //       | b2b-saas | info-product
  //       | local-service | marketplace

  "audience": {
    "primary":         "Shop-Owner DACH 3-20 MA, Shopify,
                        500k-5M Umsatz, 2-3 SEO-Agenturen
                        gewechselt",
    "buyer_personas":  [
      "Shop-Owner Shopify DACH",
      "E-Commerce Decider 500k-5M",
      "SEO-fatigued Shop-Owner"
    ],
    "pain_points":     [
      "verbrennt Budget ohne Return",
      "Checklisten-SEO statt Strategie",
      "3 Agenturen gewechselt"
    ]
  },

  "page_type_taxonomy": [
    "pillar", "landing_page", "blog_post",
    "case_study", "comparison", "faq", "pricing"
  ]
  // auto-generated from business_type
}</pre>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">Phase 0.5 &mdash; ask once, persist once</h3>
      <ul>
        <li><strong>Never guessed.</strong> A <code>.de</code> shoe-shop is not a <code>b2b-service</code> even if the URL looks like a German agency.</li>
        <li><strong>One turn, three answers.</strong> Business type, audience sentence, pain-points &mdash; captured in a single elicitation.</li>
        <li><strong>Migration from v1.1.</strong> Reading a v1.1 state triggers Phase 0.5 on next <span class="tag">/peec-setup audit</span>.</li>
      </ul>

      <h3 class="s-h3">Downstream consumers</h3>
      <table class="data">
        <thead><tr><th>Skill</th><th>Reads</th></tr></thead>
        <tbody>
          <tr><td><span class="tag">/peec-content-intel</span></td><td><code>page_type</code> REQUIRED per brief &middot; <code>audience</code> feeds copy angles</td></tr>
          <tr><td><span class="tag">/peec-cluster</span></td><td>zone one-move must name a <code>page_type</code></td></tr>
          <tr><td><span class="tag">/peec-agent</span></td><td><code>audience.pain_points</code> become priors for Awareness content</td></tr>
          <tr><td><span class="tag">/peec-report</span></td><td>attributes visibility lift per <code>page_type</code></td></tr>
        </tbody>
      </table>

      <div class="info-box teal" style="margin-top:3mm;">
        Wrong <code>business_type</code> corrupts every brief that follows. Changing it later = content graveyard. Ask once, ask early.
      </div>
    </div>
  </div>

  <div class="footer"><div class="footer-l">Antonio Blago &middot; info@antonioblago.com</div><div class="footer-r">Part 1 &mdash; Pitch</div></div>
</div>
"""

SLIDE_18 = """
<!-- ============ SLIDE 18 - BUSINESS TYPE PAGE TYPE MATRIX ============ -->
<div class="slide content">
  <div class="top-bar"></div><div class="top-bar-accent"></div>
  <div class="brand">peec-ai-skills</div><div class="slide-num">18 / 28</div>
  <div class="h-bar" style="margin-top:8mm;"></div>
  <h1 class="s-title">Business-type &rarr; page-type matrix.</h1>
  <h2 class="s-sub">Every content move names a page type. The allowed set is not your preference &mdash; it is a constraint derived from what actually wins for your business model in AI answers.</h2>

  <table class="data" style="margin-top:2mm;">
    <thead>
      <tr>
        <th style="width:30mm;">business_type</th>
        <th>Allowed <code>page_type</code> values</th>
        <th style="width:60mm;">Typical winning combo</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>b2b-service</strong><br><span class="muted" style="font-size:8pt;">freelancer, agency, consulting</span></td>
        <td><code>pillar</code> &middot; <code>landing_page</code> &middot; <code>blog_post</code> &middot; <code>case_study</code> &middot; <code>comparison</code> &middot; <code>faq</code> &middot; <code>pricing</code></td>
        <td>Decision &rarr; <code>landing_page</code> + <code>case_study</code><br>Awareness &rarr; <code>pillar</code> + <code>blog_post</code></td>
      </tr>
      <tr>
        <td><strong>b2c-ecommerce</strong><br><span class="muted" style="font-size:8pt;">D2C shop, Shopify</span></td>
        <td><code>pdp</code> &middot; <code>collection</code> &middot; <code>pillar</code> &middot; <code>blog_post</code> &middot; <code>guide</code> &middot; <code>category_page</code> &middot; <code>faq</code></td>
        <td>Decision &rarr; <code>pdp</code><br>Consideration &rarr; <code>collection</code> + <code>comparison</code><br>Awareness &rarr; <code>guide</code> + <code>blog_post</code></td>
      </tr>
      <tr>
        <td><strong>b2b-saas</strong><br><span class="muted" style="font-size:8pt;">subscription software</span></td>
        <td><code>landing_page</code> &middot; <code>integration</code> &middot; <code>use_case</code> &middot; <code>blog_post</code> &middot; <code>comparison</code> &middot; <code>docs</code> &middot; <code>pricing</code></td>
        <td>Decision &rarr; <code>landing_page</code> + <code>use_case</code><br>Retention &rarr; <code>docs</code> + <code>integration</code></td>
      </tr>
      <tr>
        <td><strong>info-product</strong><br><span class="muted" style="font-size:8pt;">courses, memberships</span></td>
        <td><code>sales_page</code> &middot; <code>webinar_lp</code> &middot; <code>blog_post</code> &middot; <code>case_study</code> &middot; <code>faq</code> &middot; <code>lead_magnet</code></td>
        <td>Decision &rarr; <code>sales_page</code><br>Awareness &rarr; <code>blog_post</code> + <code>lead_magnet</code></td>
      </tr>
      <tr>
        <td><strong>local-service</strong><br><span class="muted" style="font-size:8pt;">catchment-area</span></td>
        <td><code>local_landing</code> &middot; <code>landing_page</code> &middot; <code>case_study</code> &middot; <code>blog_post</code> &middot; <code>faq</code></td>
        <td>Decision &rarr; <code>local_landing</code><br>Awareness &rarr; <code>blog_post</code></td>
      </tr>
      <tr>
        <td><strong>marketplace</strong><br><span class="muted" style="font-size:8pt;">multi-seller platform</span></td>
        <td><code>collection</code> &middot; <code>pdp</code> &middot; <code>category_page</code> &middot; <code>pillar</code> &middot; <code>blog_post</code></td>
        <td>Most queries &rarr; <code>collection</code><br>Long-tail &rarr; <code>pdp</code></td>
      </tr>
    </tbody>
  </table>

  <div class="two-col" style="margin-top:4mm;">
    <div class="col col-l">
      <h3 class="s-h3">Peec <code>url_classification</code> mapping</h3>
<pre class="light" style="font-size:8.5pt;">pillar, blog_post, guide     -> ARTICLE | HOW_TO_GUIDE
landing_page, sales_page,    -> PRODUCT_PAGE | HOMEPAGE
pricing, local_landing
pdp                          -> PRODUCT_PAGE
collection, category_page    -> CATEGORY_PAGE
case_study                   -> ARTICLE
comparison                   -> COMPARISON | LISTICLE
faq                          -> ARTICLE | OTHER</pre>
      <p class="legend">Maps your taxonomy to what Peec actually observes in competitor URLs.</p>
    </div>
    <div class="col col-r">
      <h3 class="s-h3">The auto-fallback rule</h3>
      <div class="info-box">
        If zone competitors dominate with a URL class your <code>business_type</code> cannot produce (e.g. LISTICLE for a <code>b2b-service</code>), <span class="tag">/peec-cluster</span> <strong>switches the zone's one-move from content to outreach</strong>. No content is written that can't win.
      </div>
      <div class="info-box dark" style="margin-top:3mm;">
        <div class="info-box-title">Meta-rule</div>
        If <em>every</em> zone ends up with "switch to outreach" &rarr; taxonomy mismatch P0. That signals a wrong <code>business_type</code> in state. Re-run Phase 0.5.
      </div>
    </div>
  </div>

  <div class="footer"><div class="footer-l">Antonio Blago &middot; info@antonioblago.com</div><div class="footer-r">Part 1 &mdash; Pitch</div></div>
</div>
"""

text = HTML.read_text(encoding="utf-8")

# Find anchor: the Part-2 section divider (was 17, now should remain 17 until we insert + renumber)
anchor = '<!-- ============ SLIDE 17 - SECTION DIVIDER ============ -->'
if anchor not in text:
    # Accept the em-dash variant too
    anchor = '<!-- ============ SLIDE 17 — SECTION DIVIDER ============ -->'
if anchor not in text:
    raise SystemExit("Part-2 divider anchor not found")

# Insert the 2 new slides BEFORE the anchor
text = text.replace(anchor, SLIDE_17 + SLIDE_18 + "\n" + anchor)

# Update total count from /26 to /28 EVERYWHERE
text = text.replace("/ 26</div>", "/ 28</div>")

# Now renumber old slides 17-26 -> 19-28 (shift by +2).
# We already set "17 / 28" and "18 / 28" for the new slides (in the SLIDE_17/18 templates above).
# The old slides still carry "17 / 28" ... "26 / 28" and must become 19 / 28 ... 28 / 28.
#
# Trick to avoid stomping the new slides: split by anchor again and renumber only the tail.

head, _, tail = text.partition(anchor)

# Now tail starts with Part-2 divider and contains old slides 17..26 (as /28).
# Shift from highest first.
for old_n in range(26, 16, -1):
    new_n = old_n + 2
    old_tok = f'{old_n:02d} / 28</div>'
    new_tok = f'{new_n:02d} / 28</div>'
    tail = tail.replace(old_tok, new_tok)

# Also update the HTML comment labels in tail
for old_n in range(26, 16, -1):
    new_n = old_n + 2
    for variant in (
        f'<!-- ============ SLIDE {old_n} ',
        f'<!-- ============ SLIDE {old_n:02d} ',
    ):
        tail = tail.replace(variant, f'<!-- ============ SLIDE {new_n} ')

text = head + tail

HTML.write_text(text, encoding="utf-8")
print("inserted 2 slides, total 28, renumbered 17-26 -> 19-28")
