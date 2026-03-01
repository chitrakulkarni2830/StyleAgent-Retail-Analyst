# 🌟 Style Agent — Hyper-Personalised AI Fashion Stylist

> **An end-to-end AI agent pipeline** that analyses your body type, skin undertone, occasion, vibe, and budget to generate three complete, coherent outfits — each with live Google Shopping links, colour-matched jewellery, and stylist-quality notes.

<br>

## 📸 What It Does

Style Agent acts as your personal AI stylist. You fill in a few details on the left panel, click **Generate My Outfits**, and within seconds receive:

- **3 complete outfit looks** — clothing, footwear, bag, and matching jewellery
- Outfits correct for your **gender** (Women / Men), **vibe** (Ethnic, Modern, Boho…), and **occasion** (Wedding, Office, Brunch…)
- **HSL-based colour palette** — three harmonious suggestions (complementary, triadic, split-complementary)
- **Real shopping links** — 3 clickable pill buttons per item opening Google Shopping, Myntra, and Ajio
- **Formality scoring** — no sneakers with a bridal lehenga
- **AI Chat Stylist** — a floating ChatGPT-style dialog powered by Ollama llama3

<br>

## 🏗️ Architecture

```
run.py
  └─ LangGraph workflow (workflow/langgraph_state.py)
       ├─ Node 1: PersonaAgent         ← builds user style profile from DB history
       ├─ Node 2: ColourEngineAgent    ← HSL palette math, hex→colour family mapping
       ├─ Node 3: TrendScoutAgent      ← occasion & vibe trend analysis
       ├─ Node 4: WardrobeArchitectAgent ← 5-tier DB query, outfit assembly
       └─ Node 5: JewelleryAgent       ← matches jewellery to skin tone & outfit
```

All agents run in a **LangGraph state machine**. The CrewAI crew (`workflow/crewai_crew.py`) wraps them in a multi-agent task collaboration layer.

<br>

## ✨ Key Features

| Feature | Detail |
|---|---|
| **5-Tier Colour Matching** | `colour_family` (warm/cool/neutral/earth/pastel/jewel) fallback so the DB always yields results |
| **Dense Inventory** | 1,185 auto-generated items — Women, Men, Unisex × 17 colours × all vibes |
| **Formality Scoring** | Every occasion scored 1-5; footwear & bag picked to match |
| **Gender Filter** | 👩 Women / 👨 Men toggle routes to correct Indian garment categories |
| **Indian Ethnic Garments** | Lehenga, Sharara, Gharara, Anarkali, Saree, Sherwani, Bandhgala, Kurta, Mojari |
| **Outfit Coherence Validator** | Flags mismatches (sneakers with lehenga, missing dupatta) |
| **Google Shopping Links** | 3 pill buttons per item (Google Shopping · Myntra · Ajio) — always work |
| **Match Transparency** | Pale yellow notice if colour was approximated (explains tier used) |
| **AI Chat Stylist** | Floating ChatGPT-style dialog driven by Ollama llama3 |
| **Hex Colour Picker** | 24-swatch grid + OS colour wheel + manual hex input |
| **Vibe Tiles** | 8 vibes with accent colours and emoji — click to select |

<br>

## 📁 Project Structure

```
StyleAgentRetailAnalyst/
│
├── run.py                        # 🚀 Entry point — python run.py
│
├── agents/
│   ├── persona_agent.py          # Agent 1: user style profile
│   ├── colour_engine_agent.py    # Agent 2: palette math + hex→family
│   ├── trend_scout_agent.py      # Agent 3: vibe & occasion trends
│   ├── wardrobe_architect_agent.py # Agent 4: 5-tier DB query + outfit assembly
│   └── jewellery_agent.py        # Agent 5: jewellery matching
│
├── workflow/
│   ├── langgraph_state.py        # LangGraph state machine (agent pipeline)
│   └── crewai_crew.py            # CrewAI multi-agent task crew
│
├── database/
│   ├── setup_database.py         # Creates + seeds all 6 SQLite tables
│   ├── inventory.db              # The live SQLite database (auto-created)
│   └── sql_queries.py            # Query helpers
│
├── gui/
│   └── tkinter_app.py            # Full Tkinter GUI (1,400+ lines)
│
├── scraper/
│   └── live_link_scraper.py      # Builds Google Shopping / Myntra / Ajio URLs
│
├── requirements.txt
└── setup_guide.txt
```

<br>

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running locally (for AI chat only)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Pull the Ollama model (for AI chat)
```bash
ollama pull llama3
```

### 3. Run the app
```bash
python run.py
```

> The database is created automatically on first run — no manual setup needed.

<br>

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **GUI** | Tkinter (built-in) |
| **Database** | SQLite via `sqlite3` (built-in) |
| **Agent Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) + [CrewAI](https://github.com/joaomdmoura/crewai) |
| **Local LLM** | [Ollama](https://ollama.ai) — llama3 |
| **Colour Math** | `colorsys` (built-in) — HSL/HSV analysis |
| **HTTP** | `requests` + `beautifulsoup4` (trend data) |
| **Shopping Links** | Google Shopping URL construction (no scraping) |

<br>

## 🗃️ Database Schema

The SQLite database (`database/inventory.db`) contains 6 tables:

| Table | Purpose | Rows |
|---|---|---|
| `current_inventory` | Full fashion catalogue — programmatically generated | **1,185** |
| `jewellery_inventory` | Jewellery pieces matched to skin tone | 30 |
| `user_profile` | Stored style preferences | 1 (sample) |
| `purchase_history` | Past purchases for persona analysis | seeded |
| `browsing_logs` | Viewed items for personalisation | seeded |
| `outfit_history` | Generated outfits (saved by app) | starts empty |

### `current_inventory` key columns
| Column | Type | Description |
|---|---|---|
| `colour_family` | TEXT | `warm / cool / neutral / earth / pastel / jewel` |
| `gender` | TEXT | `Women / Men / Unisex` |
| `formality_score` | INTEGER | 1 (casual) → 5 (black tie) |
| `vibe_tags` | TEXT | comma-separated e.g. `"ethnic,classic"` |
| `occasion_tags` | TEXT | comma-separated e.g. `"wedding,sangeet,festive"` |
| `category` | TEXT | `lehenga / saree / sharara / kurta_pyjama / top / bottom / footwear / bag …` |

<br>

## 🤖 Agent Pipeline Detail

### Agent 1 — PersonaAgent
Reads `user_profile`, `purchase_history`, and `browsing_logs` to build a style persona. Outputs comfort level, brand tier affinity, and risk score.

### Agent 2 — ColourEngineAgent
Uses `colorsys.rgb_to_hsv()` to map any hex code to one of **6 colour families**, then generates 3 harmonious palettes (complementary, triadic, split-complementary). New in v5: `get_search_colours_for_hex()` for DB-compatible colour lookups.

### Agent 3 — TrendScoutAgent
Analyses the occasion and vibe to output relevant trend keywords, silhouette guidance, and fabric suggestions. Checks live trend data where available.

### Agent 4 — WardrobeArchitectAgent *(core)*
Builds 3 complete outfits using a **5-tier SQL fallback system**:
1. `colour_family + vibe + occasion + gender + formality ±1`
2. `colour_family + vibe + gender`
3. `colour_family + gender`
4. `gender + formality`
5. `gender + price` *(guaranteed result)*

Also runs the `OutfitCoherenceValidator` to catch formality mismatches.

### Agent 5 — JewelleryAgent
Picks earrings, necklace, bangles, and optional maang tikka based on the outfit's metal tone (gold for warm skin, silver for cool) and occasion formality.

<br>

## 📈 v5 Upgrades (7-Fix Series)

| # | Fix | Impact |
|---|---|---|
| 6 | Dense inventory generator | 1,185 items from 70 templates × 17 colours |
| 1 | Colour family matching | No more "0 results" — hex → family → 5-tier fallback |
| 7 | Formality scoring | Correct footwear/bags for every occasion type |
| 4 | Outfit coherence validator | Flags sneakers-with-lehenga, missing dupattas |
| 3 | Gender filter | Correct Indian garments for Women vs Men |
| 2 | Google Shopping links | 3 pill buttons per item — always clickable |
| 5 | Match transparency messages | Explains any colour approximation to user |

<br>

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built with ❤️ by Chitra Kulkarni — [GitHub](https://github.com/chitrakulkarni2830/StyleAgent-Retail-Analyst)*
