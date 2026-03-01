# Style Agent — Project Report

**Project Title:** Style Agent: A Hyper-Personalised AI Fashion Stylist for the Indian Market
**Technology Stack:** Python · Tkinter · SQLite · LangGraph · CrewAI · Ollama llama3
**Date:** March 2026
**Author:** Chitra Kulkarni

---

## 1. Executive Summary

Style Agent is a desktop AI application that recommends complete, coherent outfit looks personalised to each user's body type, skin undertone, occasion, gender, vibe preference, and budget. It combines a five-agent AI pipeline with a high-density SQLite product catalogue to deliver three outfit options — with matching jewellery, live shopping links, and a floating AI stylist chat — entirely offline.

The core problem it solves: generic online fashion filters return thousands of unrelated results. Style Agent narrows the search space to exactly three curated looks, each chosen for harmony of colour, formality, and cultural context (including Indian ethnic wear categories absent from most Western-focused tools).

---

## 2. Problem Statement

### 2.1 The Gap in Existing Solutions
Existing e-commerce recommendation systems operate on collaborative filtering ("users like you also bought…") and fail when:
- A user needs a culturally specific occasion outfit (e.g., Mehendi as a wedding guest)
- The user has a precise colour in mind (hex-level specificity)
- Formality must be matched across all pieces simultaneously (no heels with beach dresses, no sneakers with lehengas)
- Budget must be distributed intelligently across 5-6 outfit slots

### 2.2 Specific Technical Failures Addressed
| Problem | Root Cause | Fix Applied |
|---|---|---|
| Zero outfit results | Exact hex match against 116 items — always fails | 5-tier colour_family fallback + 1,185-item DB |
| Wrong garment types | Agent returned Western dresses for ethnic occasions | Gender-aware category router |
| Incoherent outfits | No formality check | OutfitCoherenceValidator class |
| Broken shopping links | Direct scraping of JS-heavy sites (Myntra/Ajio) | Google Shopping URL construction |
| No gender support | Single gender in inventory | Women / Men / Unisex columns + GUI toggle |

---

## 3. System Architecture

### 3.1 Pipeline Overview

```
User Input (GUI)
      │
      ▼
 LangGraph State Machine (workflow/langgraph_state.py)
      │
      ├─ Node 1: PersonaAgent
      │    Reads:  user_profile, purchase_history, browsing_logs (SQLite)
      │    Outputs: style_persona dict (risk_score, tier_affinity, palette_preference)
      │
      ├─ Node 2: ColourEngineAgent
      │    Takes:   user hex colour
      │    Outputs: 3 harmonious palettes (complementary, triadic, split-complementary)
      │             colour_family classification (warm/cool/neutral/earth/pastel/jewel)
      │
      ├─ Node 3: TrendScoutAgent
      │    Takes:   occasion, vibe
      │    Outputs: trend keywords, silhouette recommendations, fabric guidance
      │
      ├─ Node 4: WardrobeArchitectAgent
      │    Takes:   palettes + persona + trends + gender + formality
      │    Queries: current_inventory (5-tier SQL fallback)
      │    Outputs: 3 complete outfits with shopping links + match messages
      │
      └─ Node 5: JewelleryAgent
           Takes:   outfit + skin undertone + formality
           Queries: jewellery_inventory
           Outputs: jewellery kit per outfit (earrings, necklace, bangles, tikka)
```

### 3.2 Database Architecture

Six SQLite tables store all persistent data:

```
current_inventory   (1,185 rows)   ← clothing catalogue
jewellery_inventory (30 rows)      ← jewellery catalogue
user_profile        (1 row)        ← stored preferences
purchase_history    (seeded)       ← purchase signals
browsing_logs       (seeded)       ← view signals
outfit_history      (grows)        ← saved outfits
```

Key schema columns added in v5:

| Column | Type | Values | Purpose |
|---|---|---|---|
| `colour_family` | TEXT | warm/cool/neutral/earth/pastel/jewel | Fuzzy colour matching |
| `gender` | TEXT | Women/Men/Unisex | Gender-correct category routing |
| `formality_score` | INT | 1–5 | Coherence validation |
| `vibe_tags` | TEXT | comma-separated | Multi-vibe items |

---

## 4. Agent Design

### 4.1 Agent 1 — PersonaAgent

Reads the three user history tables to construct a **style persona** with three parameters:
- **risk_score** (0–1): how adventurous the user's past choices are
- **tier_affinity**: budget / mid / premium preference inferred from price history
- **palette_preference**: warm vs cool based on browsing patterns

### 4.2 Agent 2 — ColourEngineAgent

Implements full **HSL/HSV colour theory** using Python's `colorsys` module:
1. Converts user hex → RGB → HSV
2. Classifies into one of 6 colour families using hue angle and saturation/value thresholds
3. Rotates the hue wheel 180° (complementary), 120° + 240° (triadic), and 150° + 210° (split-complementary)
4. Maps each generated hex back to a descriptive colour name

New in v5: `get_search_colours_for_hex()` returns `(family_name, [colour_names])` — enabling DB queries against the `colour_family` column rather than exact hex matching.

### 4.3 Agent 3 — TrendScoutAgent

Given the occasion and vibe, outputs:
- Silhouette recommendation (e.g., "A-line flared lehenga for weddings")
- Fabric suggestion (silk/georgette for formal, cotton for casual)
- Embellishment guidance (zari for sangeet, mirror work for mehendi)

### 4.4 Agent 4 — WardrobeArchitectAgent

The core agent. Key systems:

**5-Tier SQL Fallback** — guarantees results even for unusual combinations:
```
Tier 1: colour_family + vibe + occasion + gender + formality ±1
Tier 2: colour_family + vibe + gender
Tier 3: colour_family + gender
Tier 4: gender + formality + price
Tier 5: gender + price                     ← always returns something
```

**Gender-Aware Category Router** — maps gender × vibe × occasion to correct Indian garment categories:
```python
Women + Ethnic + Wedding  → [lehenga, saree, sharara, anarkali]
Men   + Ethnic + Wedding  → [sherwani, bandhgala, kurta_pyjama]
Women + Modern + Office   → [top_or_dress, top, bottom]
```

**OutfitCoherenceValidator** — three rule checks post-assembly:
1. Footwear formality (no sneakers for formality ≥ 4)
2. Bag formality (clutch/potli for formal, tote for casual)
3. Dupatta presence for lehenga/sharara/salwar

**Match Transparency** — when tier > 1, attaches a human-readable explanation to the outfit card:
```
"✓ Colour family matched — exact shade unavailable in this vibe.
 Your chosen colour (#8B4513) is in the 'warm' family — showing
 best 'warm' alternatives available."
```

### 4.5 Agent 5 — JewelleryAgent

Selects jewellery by:
1. **Metal tone**: gold for warm/earth skin undertones, silver for cool undertones
2. **Occasion formality**: kundan/polki sets for wedding (score 5), jhumkas for casual (score 2)
3. **Outfit category**: bangles + maang tikka only for ethnic categories

---

## 5. Data Design

### 5.1 Inventory Generation Strategy

The v5 inventory is programmatically generated (not hand-entered):

```
70 item templates
×  17 colour variants (warm×3, cool×3, neutral×3, earth×2, pastel×3, jewel×3)
−  excluded combinations (no pastel formal menswear)
+  5 priority high-specificity items
= 1,185 total items
```

This approach guarantees that every query tier finds at least one result for any combination of gender × vibe × colour_family.

### 5.2 Template Coverage

| Category | Women | Men | Unisex |
|---|---|---|---|
| Indian ethnic main (lehenga/saree/sherwani…) | 9 templates | 6 templates | — |
| Western clothing (shirt/trouser/dress…) | 10 templates | 6 templates | 2 |
| Footwear | 7 templates | 5 templates | — |
| Bags & accessories | 5 templates | 3 templates | — |

---

## 6. GUI Design

### 6.1 Layout
Three-column layout (1,400 × 900 minimum window):
- **Left sidebar** (260px): all user inputs
- **Centre column** (flexible): vibe tiles, occasion dropdown, colour picker, budget slider
- **Right results panel** (460px): scrollable outfit cards

### 6.2 Key UI Components

**Vibe Tiles** — 8 clickable tiles with emoji and accent colours:
`Ethnic (magenta) · Modern (navy) · Classic (burgundy) · Boho (forest) · Indo-Western · Formal · Casual · Streetwear`

**Gender Toggle** (new in v5) — two styled buttons under "SHOPPING FOR":
`👩 Women (dark + gold when active) · 👨 Men (muted when inactive)`

**Colour Picker** — 24-swatch grid covering all 6 colour families + "Pick Any Colour" (OS wheel) + manual hex input field

**Outfit Cards** — per look:
- Palette name + 3 colour swatches with hex names
- Match transparency notice (pale yellow banner, if applicable)
- Clothing items with category icon + price
- 3 shopping pill buttons per item (🛒 Google Shopping · Myntra · Ajio)
- Jewellery kit breakdown

**AI Stylist Chat** — floating `Toplevel` popup:
- Dark header with gold avatar
- Scrollable message area (user right-aligned, AI left-aligned)
- Animated "thinking…" indicator
- Ollama llama3 called in background thread (non-blocking)

---

## 7. Shopping Link Strategy

### v1–v4 (abandoned): Direct scraping
- Attempted `requests` + `BeautifulSoup` against Myntra and Ajio
- Problem: both sites render product listings via JavaScript — BeautifulSoup sees blank `<div>`s

### v5 (current): Google Shopping URL construction
- No HTTP requests at startup or during outfit generation
- `build_google_shopping_url()` constructs a pre-filtered URL:
  `https://www.google.com/search?tbm=shop&q={colour}+{item}+{gender}+India&tbs=p_ord:rv,mr:1,price:1,ppr_max:{price}`
- Direct retailer search URLs for Myntra and Ajio also constructed (fallbacks)
- **Guaranteed to open** — URL construction never fails or times out

---

## 8. Formality System

40+ occasions are mapped to a 1–5 formality score:

| Score | Example Occasions | Footwear Allowed |
|---|---|---|
| 5 | Wedding, Black Tie Gala, Award Ceremony | Block heels, stiletto, oxford, mojari |
| 4 | Sangeet, Formal Dinner, Interview, Date Night | Block heels, kitten heel, loafer |
| 3 | Diwali, Birthday Party, Office, Business Lunch | Flat sandal, mule heel, kitten heel |
| 2 | Haldi, Brunch, Pooja, Movie Date | Flat sandal, kolhapuri, sneaker |
| 1 | Work From Home, Travel, Grocery | Sneaker, flat sandal |

Footwear from the DB is matched using `silhouette` substring checks against the formality tier's allowed list.

---

## 9. Results and Validation

### 9.1 Syntax Validation
All 5 modified files pass Python's `py_compile.compile()`:
```
OK  database/setup_database.py
OK  agents/colour_engine_agent.py
OK  agents/wardrobe_architect_agent.py
OK  scraper/live_link_scraper.py
OK  gui/tkinter_app.py
```

### 9.2 Database Validation
```
Total items:       1,185
Women:               837 items
Men:                 314 items
Unisex:               34 items

colour_family:
  cool:     215
  neutral:  214
  jewel:    214
  warm:     213
  pastel:   187
  earth:    142

New columns present: colour_family ✓  gender ✓  formality_score ✓  vibe_tags ✓
```

### 9.3 Colour Engine Validation
```python
get_search_colours_for_hex('#8B0000')  → ('warm', ['terracotta', 'rust', ...])
get_search_colours_for_hex('#FFFFFF')  → ('neutral', ['ivory', 'charcoal grey', ...])
get_search_colours_for_hex('#1A5276')  → ('cool', ['cobalt blue', 'emerald green', ...])
```

---

## 10. Limitations and Future Work

| Limitation | Proposed Solution |
|---|---|
| Inventory is static (no DB-live product data) | Integrate Myntra/Flipkart product APIs when available |
| Ollama llama3 requires local GPU/CPU; slow on low-end hardware | Add OpenAI API fallback |
| Outfit generation does not use image-based similarity | Integrate CLIP embeddings for visual similarity |
| No user account system | Add SQLite-backed multi-profile support |
| Shopping links open Google, not product pages | Add Selenium-based deep scraping with caching |

---

## 11. Conclusion

Style Agent demonstrates that an offline, privacy-preserving AI stylist can match the recommendation quality of cloud-based fashion AI — without sending user data to external servers. The 5-tier colour fallback system ensures the app never returns empty results. The gender-aware routing and formality validator produce culturally accurate, coherent outfits for the Indian market specifically. The system is modular: each agent can be improved or replaced independently without affecting the others.

---

*Report compiled: March 2026 | GitHub: [chitrakulkarni2830/StyleAgent-Retail-Analyst](https://github.com/chitrakulkarni2830/StyleAgent-Retail-Analyst)*
