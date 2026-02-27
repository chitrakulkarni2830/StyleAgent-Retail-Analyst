"""
=============================================================
database/setup_database.py — Style Agent Gold Standard Edition
=============================================================
PURPOSE:
  This file creates the SQLite database (inventory.db) and fills
  it with sample data. Run this ONCE before launching the app.

  It creates 6 tables:
    1. user_profile        — your personal style settings
    2. purchase_history    — past purchases for persona analysis
    3. browsing_logs       — items you've viewed online
    4. current_inventory   — the full fashion catalogue (50+ items)
    5. jewellery_inventory — the jewellery catalogue (30+ pieces)
    6. outfit_history      — saves outfits you generate (starts empty)

HOW TO RUN:
  python3 database/setup_database.py
=============================================================
"""

import sqlite3   # built-in Python library — no install needed
import os        # built-in — for file path handling
import json      # built-in — for storing fabric preferences as JSON text

# ── Where should the database file be saved? ──────────────────
# os.path.dirname(__file__) gives us the folder this script is in
# Then we go one level up (the project root) so we can find database/
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))          # e.g. /path/to/StyleAgentRetailAnalyst/database
DB_PATH     = os.path.join(THIS_FOLDER, "inventory.db")           # final path: database/inventory.db


# =============================================================
# FUNCTION: create_all_tables
# Creates the 6 tables if they don't already exist.
# "IF NOT EXISTS" means it's safe to run this script multiple times.
# =============================================================
def create_all_tables(connection):
    """
    Takes a live database connection and creates all 6 tables.
    We use triple-quoted strings (''') to write multi-line SQL clearly.
    """
    cursor = connection.cursor()  # a cursor is like a "pen" for the database

    # ── Table 1: user_profile ─────────────────────────────────
    # Stores one row per user with their style preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            user_id           INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique ID auto-assigned
            name              TEXT NOT NULL,                      -- the user's name
            body_type         TEXT,                               -- e.g. Hourglass, Pear, Apple
            skin_undertone    TEXT,                               -- warm / cool / neutral
            size              TEXT,                               -- XS / S / M / L / XL / XXL
            budget_min        REAL,                               -- minimum budget in rupees
            budget_max        REAL,                               -- maximum budget in rupees
            preferred_fabrics TEXT,                               -- stored as comma-separated text
            date_created      TEXT DEFAULT CURRENT_TIMESTAMP      -- when was this profile made?
        )
    ''')

    # ── Table 2: purchase_history ─────────────────────────────
    # Every item this user has bought — used by Persona Agent
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_history (
            purchase_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER,                               -- links to user_profile
            item_name      TEXT,                                  -- what was bought
            category       TEXT,                                  -- Top / Bottom / Dress / etc.
            colour         TEXT,                                  -- colour of the item
            fabric         TEXT,                                  -- Silk / Cotton / Georgette etc.
            price          REAL,                                  -- how much they paid
            occasion       TEXT,                                  -- wedding / office / casual etc.
            vibe           TEXT,                                  -- Ethnic / Modern / Boho etc.
            date_purchased TEXT,                                  -- when they bought it
            rating_given   INTEGER                               -- 1 to 5 stars
        )
    ''')

    # ── Table 3: browsing_logs ─────────────────────────────────
    # Items the user looked at online — used by Persona Agent
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS browsing_logs (
            log_id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER,
            item_viewed        TEXT,                              -- name of what they looked at
            category           TEXT,
            colour             TEXT,
            time_spent_seconds INTEGER,                           -- how long they spent looking
            saved_to_wishlist  INTEGER DEFAULT 0,                 -- 1 = yes, 0 = no (SQLite has no BOOLEAN)
            date_viewed        TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ── Table 4: current_inventory ────────────────────────────
    # The full clothing catalogue — 50+ rows of outfits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_inventory (
            item_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name         TEXT NOT NULL,                      -- full descriptive name
            category          TEXT,                               -- Top / Bottom / Dress / Outerwear / Footwear / Bag
            colour            TEXT,                               -- main colour
            colour_hex        TEXT,                               -- HEX code e.g. #8B0000
            fabric            TEXT,                               -- Silk / Cotton / Chiffon etc.
            silhouette        TEXT,                               -- A-Line / Straight / Flared etc.
            cut               TEXT,                               -- Anarkali / Crop / Wrap etc.
            fit               TEXT,                               -- Regular / Slim / Relaxed etc.
            vibe              TEXT,                               -- Ethnic / Modern / Boho etc.
            size_available    TEXT,                               -- comma-separated: "S,M,L"
            price             REAL,                               -- price in Indian Rupees
            brand_tier        TEXT,                               -- Budget / Mid-range / Designer
            occasion_tags     TEXT,                               -- comma-separated occasions
            stock_count       INTEGER DEFAULT 10,
            image_url         TEXT DEFAULT ""
        )
    ''')

    # ── Table 5: jewellery_inventory ──────────────────────────
    # All jewellery pieces — 30+ rows
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jewellery_inventory (
            jewellery_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name             TEXT NOT NULL,                  -- full descriptive name
            jewellery_type        TEXT,                           -- Earrings / Necklace / Bangles / Ring / Tikka
            metal                 TEXT,                           -- Gold / Silver / Rose Gold / Platinum
            stones                TEXT,                           -- Kundan / Pearl / Ruby / None
            style_tags            TEXT,                           -- Traditional / Minimalist / Statement
            occasion_tags         TEXT,                           -- wedding / office / casual etc.
            price                 REAL,
            skin_undertone_fit    TEXT,                           -- warm / cool / neutral / all
            neckline_suitable     TEXT                            -- V-neck / high-neck / off-shoulder / all
        )
    ''')

    # ── Table 6: outfit_history ────────────────────────────────
    # Saves generated outfits — filled by the app, starts empty
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outfit_history (
            outfit_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER,
            outfit_json    TEXT,                                  -- the full outfit stored as JSON text
            occasion       TEXT,
            vibe           TEXT,
            colour_palette TEXT,                                  -- name of the palette used
            date_generated TEXT DEFAULT CURRENT_TIMESTAMP,
            user_rating    INTEGER,                               -- rating the user gives 1-5
            saved          INTEGER DEFAULT 0                      -- 1 = saved, 0 = not saved
        )
    ''')

    connection.commit()  # "commit" means save all the table creations permanently
    print("  ✅ Tables created successfully")


# =============================================================
# FUNCTION: seed_inventory
# Inserts 50+ clothing items into current_inventory.
# Covers all 8 vibes: Ethnic / Modern / Boho / Indo-Western /
#   Classic / Formal / Casual / Streetwear
# =============================================================
def seed_inventory(connection):
    """
    Inserts detailed, realistic clothing inventory rows.
    Each row has a full item name plus all style attributes.
    """
    cursor = connection.cursor()

    # First, remove old data so we don't get duplicates
    cursor.execute("DELETE FROM current_inventory")

    # Each tuple represents one clothing item.
    # Column order: item_name, category, colour, colour_hex, fabric, silhouette,
    #               cut, fit, vibe, size_available, price, brand_tier, occasion_tags
    inventory_rows = [

        # ── ETHNIC ────────────────────────────────────────────────
        (
            "Powder blue silk-georgette A-line kurta with gold zari border",
            "Top", "Powder Blue", "#B0C4DE",
            "Silk Georgette", "A-Line", "Anarkali", "Regular",
            "Ethnic", "XS,S,M,L,XL", 4500, "Mid-range",
            "wedding,sangeet,pooja,festival"
        ),
        (
            "Wide-leg ivory palazzo in lightweight crepe with gold tassels",
            "Bottom", "Ivory", "#FFFFF0",
            "Crepe", "Wide Leg", "Palazzo", "Relaxed",
            "Ethnic", "XS,S,M,L,XL,XXL", 2800, "Mid-range",
            "wedding,sangeet,festival,mehendi"
        ),
        (
            "Deep burgundy Banarasi silk saree with antique gold zari border",
            "Dress", "Burgundy", "#800020",
            "Banarasi Silk", "Draped", "Saree", "Draped",
            "Ethnic", "Free Size", 12500, "Designer",
            "wedding,reception,diwali,sangeet"
        ),
        (
            "Terracotta hand-block-printed A-line kurta with mirror embroidery",
            "Top", "Terracotta", "#C67C5A",
            "Cotton", "A-Line", "Straight", "Regular",
            "Ethnic", "XS,S,M,L,XL,XXL", 3200, "Mid-range",
            "festival,diwali,navratri,pooja,casual"
        ),
        (
            "Emerald green chanderi kurta with fine chikankari embroidery",
            "Top", "Emerald Green", "#046307",
            "Chanderi", "Straight", "Straight", "Regular",
            "Ethnic", "XS,S,M,L,XL", 5500, "Mid-range",
            "eid,festival,wedding,sangeet"
        ),
        (
            "Blush pink organza lehenga choli with sequin embellishments",
            "Dress", "Blush Pink", "#FFB6C1",
            "Organza", "Flared", "Lehenga", "Flared",
            "Ethnic", "XS,S,M,L", 18000, "Designer",
            "sangeet,mehendi,wedding,reception"
        ),
        (
            "Cobalt blue raw silk anarkali with gota patti hem",
            "Dress", "Cobalt Blue", "#0047AB",
            "Raw Silk", "Flared", "Anarkali", "Flared",
            "Ethnic", "S,M,L,XL", 7800, "Mid-range",
            "eid,festival,wedding,sangeet"
        ),
        (
            "Mustard yellow patiala salwar with hand-embroidered yoke",
            "Bottom", "Mustard Yellow", "#FFDB58",
            "Cotton Silk", "Patiala", "Patiala", "Relaxed",
            "Ethnic", "XS,S,M,L,XL,XXL", 2200, "Budget",
            "festival,navratri,mehendi,casual"
        ),
        (
            "Deep maroon velvet shawl collar blouse with antique gold buttons",
            "Top", "Maroon", "#800000",
            "Velvet", "Structured", "Blouse", "Regular",
            "Ethnic", "XS,S,M,L,XL", 3800, "Mid-range",
            "wedding,reception,diwali"
        ),
        (
            "Sage green cotton kurta set with hand-block tulip print",
            "Top", "Sage Green", "#B2AC88",
            "Cotton", "Straight", "Straight", "Regular",
            "Ethnic", "XS,S,M,L,XL,XXL", 1800, "Budget",
            "casual,pooja,festival,college"
        ),

        # ── MODERN ────────────────────────────────────────────────
        (
            "Navy blazer in stretch wool with satin lapel trim",
            "Outerwear", "Navy", "#000080",
            "Stretch Wool", "Structured", "Blazer", "Slim",
            "Modern", "XS,S,M,L,XL", 6500, "Mid-range",
            "office,client_meeting,conference,business_lunch"
        ),
        (
            "Crisp ivory button-down shirt in anti-wrinkle cotton poplin",
            "Top", "Ivory", "#FFFFF0",
            "Cotton Poplin", "Straight", "Shirt", "Regular",
            "Modern", "XS,S,M,L,XL,XXL", 2200, "Budget",
            "office,work_from_home,client_meeting,casual"
        ),
        (
            "High-waist tailored trousers in caramel ponte fabric",
            "Bottom", "Camel", "#C19A6B",
            "Ponte", "Straight", "Trousers", "Slim",
            "Modern", "XS,S,M,L,XL,XXL", 3200, "Mid-range",
            "office,conference,business_lunch,client_meeting"
        ),
        (
            "Cobalt blue wrap midi dress in fluid crepe de chine",
            "Dress", "Cobalt Blue", "#0047AB",
            "Crepe de Chine", "Wrap", "Wrap Dress", "Fitted",
            "Modern", "XS,S,M,L,XL", 5800, "Mid-range",
            "date_night,anniversary_dinner,birthday_party,girls_night_out"
        ),
        (
            "Sleek black A-line midi skirt in heavy duchess satin",
            "Bottom", "Black", "#000000",
            "Duchess Satin", "A-Line", "Skirt", "Slim",
            "Modern", "XS,S,M,L,XL", 4200, "Mid-range",
            "black_tie,formal_dinner,theatre,award_ceremony"
        ),
        (
            "Burgundy velvet blazer dress with gold button accents",
            "Dress", "Burgundy", "#800020",
            "Velvet", "Structured", "Blazer Dress", "Fitted",
            "Modern", "XS,S,M,L", 8900, "Mid-range",
            "black_tie,award_ceremony,formal_dinner,anniversary_dinner"
        ),
        (
            "Terracotta linen co-ord set — boxy top and flared trouser",
            "Dress", "Terracotta", "#C67C5A",
            "Linen", "Flared", "Co-ord", "Relaxed",
            "Modern", "XS,S,M,L,XL", 4800, "Mid-range",
            "brunch,birthday_party,shopping_trip,girls_night_out"
        ),
        (
            "Rose blush slip dress in bias-cut silk charmeuse",
            "Dress", "Rose", "#FFB6C1",
            "Silk Charmeuse", "Bias Cut", "Slip Dress", "Relaxed",
            "Modern", "XS,S,M,L", 7200, "Mid-range",
            "date_night,anniversary_dinner,girls_night_out"
        ),

        # ── BOHO ──────────────────────────────────────────────────
        (
            "Burnt orange peasant blouse with tassel trim and embroidery",
            "Top", "Burnt Orange", "#CC5500",
            "Cotton Voile", "Flowy", "Peasant", "Relaxed",
            "Boho", "XS,S,M,L,XL,XXL", 1800, "Budget",
            "festival,college,casual,shopping_trip"
        ),
        (
            "Sage green maxi skirt in crinkle fabric with tiered hem",
            "Bottom", "Sage Green", "#B2AC88",
            "Crinkle Cotton", "Maxi", "Tiered Skirt", "Flowy",
            "Boho", "XS,S,M,L,XL,XXL", 2200, "Budget",
            "casual,brunch,shopping_trip,travel"
        ),
        (
            "Ivory crochet beach cover-up with fringe hem",
            "Dress", "Ivory", "#FFFFF0",
            "Crochet Cotton", "Flowy", "Cover-up", "Relaxed",
            "Boho", "XS,S,M,L,XL", 3200, "Mid-range",
            "travel,casual,brunch,festival"
        ),
        (
            "Deep burgundy velvet off-shoulder maxi dress with bell sleeves",
            "Dress", "Burgundy", "#800020",
            "Velvet", "Maxi", "Off-shoulder", "Relaxed",
            "Boho", "XS,S,M,L", 5800, "Mid-range",
            "date_night,birthday_party,girls_night_out,festival"
        ),

        # ── INDO-WESTERN ──────────────────────────────────────────
        (
            "Steel grey relaxed sharara pants in georgette with silver trim",
            "Bottom", "Steel Grey", "#71797E",
            "Georgette", "Flared", "Sharara", "Relaxed",
            "Indo-Western", "XS,S,M,L,XL", 3800, "Mid-range",
            "sangeet,wedding,birthday_party,date_night"
        ),
        (
            "Soft peach cape-style Indo-western top in organza with ruffle panels",
            "Top", "Peach", "#FFCBA4",
            "Organza", "Structured", "Cape Top", "Regular",
            "Indo-Western", "XS,S,M,L,XL", 4200, "Mid-range",
            "sangeet,birthday_party,date_night,anniversary_dinner"
        ),
        (
            "Ivory dhoti pants in silk with gold ankle chain detail",
            "Bottom", "Ivory", "#FFFFF0",
            "Silk", "Dhoti", "Dhoti", "Relaxed",
            "Indo-Western", "S,M,L,XL", 4500, "Mid-range",
            "sangeet,mehendi,wedding,date_night"
        ),
        (
            "Cobalt blue short anarkali top with draped jacket overlay",
            "Top", "Cobalt Blue", "#0047AB",
            "Chanderi", "Structured", "Jacket Kurta", "Regular",
            "Indo-Western", "XS,S,M,L,XL", 6800, "Mid-range",
            "sangeet,wedding,birthday_party"
        ),

        # ── CLASSIC ───────────────────────────────────────────────
        (
            "Crisp white cotton-linen blend shirt with mother-of-pearl buttons",
            "Top", "White", "#FFFFFF",
            "Cotton-Linen Blend", "Straight", "Shirt", "Regular",
            "Classic", "XS,S,M,L,XL,XXL", 2800, "Mid-range",
            "office,casual,brunch,client_meeting,networking_event"
        ),
        (
            "Navy straight-cut trousers in performance stretch fabric",
            "Bottom", "Navy", "#000080",
            "Stretch Fabric", "Straight", "Trousers", "Slim",
            "Classic", "XS,S,M,L,XL,XXL", 3500, "Mid-range",
            "office,client_meeting,job_interview,conference"
        ),
        (
            "Camel trench coat in water-resistant gabardine with tie belt",
            "Outerwear", "Camel", "#C19A6B",
            "Gabardine", "Structured", "Trench Coat", "Regular",
            "Classic", "XS,S,M,L,XL", 8500, "Mid-range",
            "office,networking_event,conference,casual"
        ),
        (
            "Little black dress in matte jersey with three-quarter sleeves",
            "Dress", "Black", "#000000",
            "Matte Jersey", "Fitted", "LBD", "Fitted",
            "Classic", "XS,S,M,L,XL", 5200, "Mid-range",
            "black_tie,formal_dinner,date_night,anniversary_dinner"
        ),

        # ── FORMAL ────────────────────────────────────────────────
        (
            "Deep charcoal double-breasted blazer in Italian wool blend",
            "Outerwear", "Charcoal", "#36454F",
            "Italian Wool Blend", "Structured", "Blazer", "Slim",
            "Formal", "XS,S,M,L,XL", 9800, "Mid-range",
            "job_interview,conference,client_meeting,black_tie"
        ),
        (
            "Powder blue silk blouse with pussy-bow tie and French cuffs",
            "Top", "Powder Blue", "#B0C4DE",
            "Pure Silk", "Structured", "Blouse", "Regular",
            "Formal", "XS,S,M,L,XL", 4800, "Mid-range",
            "client_meeting,conference,job_interview,office"
        ),
        (
            "Black wide-leg formal trousers in crepe with pressed centre crease",
            "Bottom", "Black", "#000000",
            "Crepe", "Wide Leg", "Trousers", "Wide",
            "Formal", "XS,S,M,L,XL,XXL", 3800, "Mid-range",
            "office,conference,job_interview,black_tie"
        ),
        (
            "Emerald column gown in stretch satin with slit detail",
            "Dress", "Emerald Green", "#046307",
            "Stretch Satin", "Column", "Gown", "Fitted",
            "Formal", "XS,S,M,L", 12500, "Designer",
            "black_tie,award_ceremony,formal_dinner,reception"
        ),

        # ── CASUAL ────────────────────────────────────────────────
        (
            "Coral linen drop-shoulder tee with raw hem finish",
            "Top", "Coral", "#FF6B6B",
            "Linen", "Relaxed", "T-shirt", "Relaxed",
            "Casual", "XS,S,M,L,XL,XXL", 1200, "Budget",
            "college,shopping_trip,casual,sunday_outing"
        ),
        (
            "Light wash denim straight jeans with faded knee detail",
            "Bottom", "Light Blue", "#ADD8E6",
            "Denim", "Straight", "Jeans", "Regular",
            "Casual", "XS,S,M,L,XL,XXL", 2500, "Budget",
            "college,casual,shopping_trip,movie_date,brunch"
        ),
        (
            "Olive green utility jacket with multiple pockets",
            "Outerwear", "Olive Green", "#556B2F",
            "Canvas", "Relaxed", "Utility Jacket", "Regular",
            "Casual", "XS,S,M,L,XL", 3200, "Budget",
            "college,casual,shopping_trip,travel"
        ),
        (
            "Rust checked flannel shirt — double-wear as top or overshirt",
            "Top", "Rust", "#B7410E",
            "Flannel", "Relaxed", "Shirt", "Oversized",
            "Casual", "XS,S,M,L,XL,XXL", 1800, "Budget",
            "casual,college,sunday_outing,shopping_trip"
        ),
        (
            "Dusty lavender linen wide-leg trousers with elastic waist",
            "Bottom", "Lavender", "#B57EDC",
            "Linen", "Wide Leg", "Trousers", "Relaxed",
            "Casual", "XS,S,M,L,XL,XXL", 2200, "Budget",
            "casual,brunch,travel,college"
        ),

        # ── STREETWEAR ────────────────────────────────────────────
        (
            "White graphic crop hoodie with abstract print — oversized fit",
            "Top", "White", "#FFFFFF",
            "French Terry", "Oversized", "Hoodie", "Oversized",
            "Streetwear", "XS,S,M,L,XL,XXL", 2800, "Budget",
            "college,casual,shopping_trip,sunday_outing"
        ),
        (
            "Black wide-leg cargo pants with pockets and contrast panel",
            "Bottom", "Black", "#000000",
            "Cotton Twill", "Wide Leg", "Cargo Pants", "Oversized",
            "Streetwear", "XS,S,M,L,XL,XXL", 3200, "Budget",
            "casual,college,shopping_trip"
        ),
        (
            "Cobalt blue bomber jacket in nylon with rib cuff and hem",
            "Outerwear", "Cobalt Blue", "#0047AB",
            "Nylon", "Relaxed", "Bomber Jacket", "Regular",
            "Streetwear", "XS,S,M,L,XL", 4500, "Mid-range",
            "casual,college,shopping_trip,sunday_outing"
        ),
        (
            "Terracotta orange co-ord set — sport bra and high-waist flare pants",
            "Dress", "Terracotta", "#C67C5A",
            "Scuba", "Flared", "Co-ord Set", "Fitted",
            "Streetwear", "XS,S,M,L,XL", 3800, "Mid-range",
            "casual,brunch,shopping_trip,birthday_party"
        ),

        # ── FOOTWEAR ──────────────────────────────────────────────
        (
            "Block heel ankle boots in espresso leather — 5cm heel",
            "Footwear", "Brown", "#8B4513",
            "Leather", "Block Heel", "Ankle Boot", "Regular",
            "Classic", "All Sizes", 4800, "Mid-range",
            "office,client_meeting,date_night,casual"
        ),
        (
            "Gold embroidered juttis with mirror work toe cap",
            "Footwear", "Gold", "#D4AF37",
            "Silk & Leather", "Flat", "Jutti", "Regular",
            "Ethnic", "All Sizes", 2200, "Mid-range",
            "wedding,festival,mehendi,sangeet,diwali"
        ),
        (
            "Classic nude strappy heels — 8cm stiletto in suede",
            "Footwear", "Nude", "#F5DEB3",
            "Suede", "Stiletto", "Strappy Heels", "Slim",
            "Modern", "All Sizes", 3800, "Mid-range",
            "date_night,black_tie,formal_dinner,anniversary_dinner"
        ),
        (
            "White leather chunky platform sneakers with silver sole",
            "Footwear", "White", "#FFFFFF",
            "Leather", "Platform", "Sneaker", "Regular",
            "Streetwear", "All Sizes", 5200, "Mid-range",
            "casual,college,shopping_trip,brunch"
        ),

        # ── BAGS ──────────────────────────────────────────────────
        (
            "Ivory textured leather structured tote bag with gold-tone hardware",
            "Bag", "Ivory", "#FFFFF0",
            "Textured Leather", "Structured", "Tote", "Regular",
            "Classic", "One Size", 6800, "Mid-range",
            "office,client_meeting,conference,brunch"
        ),
        (
            "Gold metallic potli bag with intricate zardozi embroidery",
            "Bag", "Gold", "#D4AF37",
            "Brocade", "Drawstring", "Potli", "Regular",
            "Ethnic", "One Size", 3200, "Mid-range",
            "wedding,sangeet,festival,diwali,reception"
        ),
        (
            "Burgundy velvet envelope clutch with pearl clasp",
            "Bag", "Burgundy", "#800020",
            "Velvet", "Envelope", "Clutch", "Regular",
            "Modern", "One Size", 2800, "Mid-range",
            "date_night,black_tie,anniversary_dinner,formal_dinner"
        ),
        (
            "Tan leather crossbody sling bag with braided strap",
            "Bag", "Tan", "#D2B48C",
            "Leather", "Sling", "Crossbody", "Regular",
            "Casual", "One Size", 3500, "Mid-range",
            "casual,shopping_trip,brunch,college,travel"
        ),
    ]

    # Insert all rows into the current_inventory table
    cursor.executemany('''
        INSERT INTO current_inventory
        (item_name, category, colour, colour_hex, fabric, silhouette,
         cut, fit, vibe, size_available, price, brand_tier, occasion_tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', inventory_rows)  # executemany inserts all rows at once efficiently

    connection.commit()
    print(f"  ✅ Inventory seeded: {len(inventory_rows)} items")


# =============================================================
# FUNCTION: seed_jewellery
# Inserts 30+ jewellery pieces into jewellery_inventory
# =============================================================
def seed_jewellery(connection):
    """
    Seeds the jewellery catalogue with 30+ detailed pieces.
    """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM jewellery_inventory")  # clear old data first

    # Column order: item_name, jewellery_type, metal, stones, style_tags,
    #               occasion_tags, price, skin_undertone_fit, neckline_suitable
    jewellery_rows = [

        # ── EARRINGS ──────────────────────────────────────────────
        ("Polki-studded gold jhumkas with a small ruby drop and pearl tip",
         "Earrings", "Gold", "Ruby, Pearl", "Traditional, Statement",
         "wedding,reception,sangeet,festival", 4500, "warm", "all"),

        ("Oxidised silver chandbalis with turquoise enamel drops",
         "Earrings", "Silver", "Turquoise", "Ethnic, Statement",
         "festival,mehendi,casual,navratri", 1800, "cool", "all"),

        ("Rose gold tiny hoop earrings with pearl charm",
         "Earrings", "Rose Gold", "Pearl", "Minimalist, Modern",
         "office,brunch,casual,date_night", 2200, "warm", "all"),

        ("Silver tassel drop earrings with amethyst stone",
         "Earrings", "Silver", "Amethyst", "Statement, Boho",
         "festival,date_night,birthday_party", 2800, "cool", "all"),

        ("Gold ear cuffs with delicate vine pattern and seed pearls",
         "Earrings", "Gold", "Pearl", "Modern, Indo-Western",
         "sangeet,date_night,anniversary", 3200, "warm", "off-shoulder"),

        ("Diamond-look crystal stud earrings in sterling silver",
         "Earrings", "Silver", "Crystal", "Minimalist, Modern",
         "office,conference,date_night", 1500, "cool", "all"),

        ("Gold chandeliers with emerald drops and beaded fringe",
         "Earrings", "Gold", "Emerald", "Statement, Traditional",
         "wedding,reception,black_tie", 6800, "warm", "v-neck,boat-neck"),

        # ── NECKLACES ─────────────────────────────────────────────
        ("Kundan floral choker set with matching maang tikka in gold",
         "Necklace", "Gold", "Kundan", "Traditional, Royal",
         "wedding,reception,sangeet", 8500, "warm", "all"),

        ("Delicate gold chain with a single polki pendant — 16 inch",
         "Necklace", "Gold", "Polki Diamond", "Minimalist, Modern",
         "date_night,office,casual", 3500, "warm", "v-neck"),

        ("Silver layered moon-and-star chain necklace — 18 inch + 20 inch",
         "Necklace", "Silver", "None", "Boho, Modern",
         "casual,brunch,college,date_night", 1800, "cool", "v-neck,open-neck"),

        ("Pearl strand choker in 14K gold with ruby clasp",
         "Necklace", "Gold", "Pearl, Ruby", "Classic, Formal",
         "black_tie,formal_dinner,office,conference", 7200, "all", "boat-neck,high-neck"),

        ("Statement collar necklace — oxidised silver with lapis lazuli stones",
         "Necklace", "Silver", "Lapis Lazuli", "Statement, Ethnic",
         "festival,date_night,girls_night_out", 3200, "cool", "boat-neck,open-neck"),

        ("Rose gold layered necklace with rose quartz teardrop pendant",
         "Necklace", "Rose Gold", "Rose Quartz", "Romantic, Modern",
         "date_night,anniversary,birthday_party", 4200, "warm", "v-neck"),

        ("Heavy gold temple necklace with Lakshmi pendant and red enamel",
         "Necklace", "Gold", "Enamel", "Traditional, Ethnic",
         "wedding,reception,diwali,festival", 9800, "warm", "all"),

        # ── BANGLES & BRACELETS ───────────────────────────────────
        ("Set of 12 glass bangles in terracotta and gold — 2.4 size",
         "Bangles", "Gold", "Glass", "Traditional",
         "festival,navratri,mehendi,casual", 450, "warm", "all"),

        ("Broad gold cuff bangle with floral kundan setting",
         "Bangles", "Gold", "Kundan", "Traditional, Statement",
         "wedding,reception,sangeet", 5500, "warm", "all"),

        ("Silver oxidised mesh bangle bracelet with turquoise beads",
         "Bangles", "Silver", "Turquoise", "Boho, Ethnic",
         "casual,festival,brunch", 1200, "cool", "all"),

        ("Slim rose gold bangle with a row of pavé diamonds",
         "Bangles", "Rose Gold", "Diamond", "Minimalist",
         "office,date_night,conference", 3200, "warm", "all"),

        ("Stack of 3 twisted gold wire bracelets with tiny star charms",
         "Bangles", "Gold", "None", "Minimalist, Modern",
         "casual,brunch,shopping_trip", 2200, "warm", "all"),

        # ── RINGS ─────────────────────────────────────────────────
        ("Cocktail ring — 22K gold dome with emerald centre stone",
         "Ring", "Gold", "Emerald", "Statement, Traditional",
         "wedding,reception,formal_dinner", 7800, "warm", "all"),

        ("Stackable set of 5 silver midi rings — geometric shapes",
         "Ring", "Silver", "None", "Minimalist, Modern",
         "casual,brunch,college,date_night", 1200, "cool", "all"),

        ("Rose gold solitaire ring with 0.5ct lab diamond",
         "Ring", "Rose Gold", "Lab Diamond", "Classic, Minimalist",
         "date_night,office,formal_dinner", 5800, "warm", "all"),

        ("Traditional gold with enamel toe rings — pair, adjustable",
         "Ring", "Gold", "Enamel", "Traditional",
         "wedding,mehendi,festival", 800, "warm", "all"),

        # ── MAANG TIKKA & HAIR ────────────────────────────────────
        ("Jadau gold maang tikka with pearl drops and ruby centrepiece",
         "Tikka", "Gold", "Ruby, Pearl", "Traditional, Bridal",
         "wedding,reception,sangeet", 6500, "warm", "all"),

        ("Oxidised silver maang tikka with peacock motif and turquoise",
         "Tikka", "Silver", "Turquoise", "Ethnic, Casual",
         "festival,mehendi,navratri", 1800, "cool", "all"),

        ("Tiny crystal hair pin set — set of 8 in silver tones",
         "Tikka", "Silver", "Crystal", "Minimalist",
         "brunch,office,date_night,casual", 850, "cool", "all"),

        # ── OPTIONAL EXTRAS ───────────────────────────────────────
        ("Gold Kamarbandh (waist belt) with kundan flowers — adjustable",
         "Extras", "Gold", "Kundan", "Traditional",
         "wedding,sangeet,reception", 4200, "warm", "all"),

        ("Silver anklet with tiny ghungroo bells — pair",
         "Extras", "Silver", "None", "Traditional, Casual",
         "festival,casual,mehendi,navratri", 950, "cool", "all"),

        ("Antique gold brooch with peacock design and emerald eye",
         "Extras", "Gold", "Emerald", "Statement, Classic",
         "black_tie,formal_dinner,reception,conference", 3800, "warm", "all"),

        ("Rose gold layered body chain — shoulder to waist",
         "Extras", "Rose Gold", "None", "Bohemian, Statement",
         "sangeet,date_night,birthday_party", 3500, "warm", "off-shoulder"),
    ]

    cursor.executemany('''
        INSERT INTO jewellery_inventory
        (item_name, jewellery_type, metal, stones, style_tags,
         occasion_tags, price, skin_undertone_fit, neckline_suitable)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', jewellery_rows)

    connection.commit()
    print(f"  ✅ Jewellery seeded: {len(jewellery_rows)} pieces")


# =============================================================
# FUNCTION: seed_user_data
# Adds a sample user, purchase history, and browsing logs
# =============================================================
def seed_user_data(connection):
    """
    Seeds realistic data for user_id = 1 (Priya Sharma).
    This is the "test user" the Persona Agent will analyse.
    """
    cursor = connection.cursor()

    # Clear old user data
    cursor.execute("DELETE FROM user_profile")
    cursor.execute("DELETE FROM purchase_history")
    cursor.execute("DELETE FROM browsing_logs")

    # ── Sample User ───────────────────────────────────────────
    cursor.execute('''
        INSERT INTO user_profile
        (name, body_type, skin_undertone, size, budget_min, budget_max, preferred_fabrics)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("Priya Sharma", "Hourglass", "warm", "M", 2000, 20000, "Silk,Georgette,Cotton"))

    # ── Sample Purchase History (20 rows) ─────────────────────
    purchase_rows = [
        (1, "Banarasi silk saree in deep burgundy", "Dress", "Burgundy", "Silk", 12500, "wedding", "Ethnic", "2025-01-15", 5),
        (1, "Gold embroidered juttis", "Footwear", "Gold", "Leather", 2200, "wedding", "Ethnic", "2025-01-15", 5),
        (1, "Terracotta cotton kurta with mirror work", "Top", "Terracotta", "Cotton", 3200, "festival", "Ethnic", "2025-02-10", 4),
        (1, "Cobalt blue wrap dress in crepe", "Dress", "Cobalt Blue", "Crepe", 5800, "date_night", "Modern", "2025-03-05", 5),
        (1, "Ivory palazzo in crepe", "Bottom", "Ivory", "Crepe", 2800, "wedding", "Ethnic", "2025-03-22", 4),
        (1, "Navy stretch wool blazer", "Outerwear", "Navy", "Wool", 6500, "office", "Modern", "2025-04-01", 4),
        (1, "Block heel ankle boots in brown leather", "Footwear", "Brown", "Leather", 4800, "office", "Classic", "2025-04-01", 5),
        (1, "Blush pink organza lehenga", "Dress", "Blush Pink", "Organza", 18000, "sangeet", "Ethnic", "2025-05-14", 5),
        (1, "Emerald green anarkali in cobalt blue chanderi", "Dress", "Cobalt Blue", "Chanderi", 7800, "eid", "Ethnic", "2025-06-02", 4),
        (1, "Mustard patiala salwar", "Bottom", "Mustard Yellow", "Cotton Silk", 2200, "navratri", "Ethnic", "2025-10-01", 3),
        (1, "Camel ponte trousers", "Bottom", "Camel", "Ponte", 3200, "office", "Modern", "2025-09-12", 4),
        (1, "Rose blush silk charmeuse slip dress", "Dress", "Rose", "Silk", 7200, "date_night", "Modern", "2025-09-28", 5),
        (1, "Sage green kurta set with block print", "Top", "Sage Green", "Cotton", 1800, "casual", "Ethnic", "2025-10-20", 3),
        (1, "Gold metallic potli bag with zardozi", "Bag", "Gold", "Brocade", 3200, "wedding", "Ethnic", "2025-11-08", 5),
        (1, "Classic little black dress in matte jersey", "Dress", "Black", "Jersey", 5200, "formal_dinner", "Classic", "2025-11-25", 5),
        (1, "Ivory textured leather tote bag", "Bag", "Ivory", "Leather", 6800, "office", "Classic", "2025-12-02", 4),
        (1, "Coral linen drop-shoulder tee", "Top", "Coral", "Linen", 1200, "casual", "Casual", "2025-12-15", 3),
        (1, "Powder blue silk georgette kurta", "Top", "Powder Blue", "Silk Georgette", 4500, "festival", "Ethnic", "2026-01-05", 5),
        (1, "Polki gold jhumkas with ruby drop", "Accessory", "Gold", "Metal", 4500, "wedding", "Ethnic", "2026-01-20", 5),
        (1, "Crisp ivory cotton poplin shirt", "Top", "Ivory", "Cotton Poplin", 2200, "office", "Modern", "2026-02-10", 4),
    ]

    cursor.executemany('''
        INSERT INTO purchase_history
        (user_id, item_name, category, colour, fabric, price, occasion, vibe, date_purchased, rating_given)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', purchase_rows)

    # ── Browsing Logs ─────────────────────────────────────────
    browsing_rows = [
        (1, "Pastel pink lehenga with resham embroidery", "Dress", "Blush Pink", 180, 1, "2026-02-15"),
        (1, "Terracotta block-printed co-ord set", "Dress", "Terracotta", 95, 0, "2026-02-16"),
        (1, "Gold temple necklace with ruby pendant", "Accessory", "Gold", 240, 1, "2026-02-17"),
        (1, "Cobalt blue silk two-piece kurta sharara", "Dress", "Cobalt Blue", 310, 1, "2026-02-18"),
        (1, "Ivory dress with slip-style satin detail", "Dress", "Ivory", 60, 0, "2026-02-18"),
        (1, "Nude block heels in suede", "Footwear", "Nude", 140, 1, "2026-02-19"),
        (1, "Sage green maxi skirt with tiered hem", "Bottom", "Sage Green", 75, 0, "2026-02-20"),
    ]

    cursor.executemany('''
        INSERT INTO browsing_logs
        (user_id, item_viewed, category, colour, time_spent_seconds, saved_to_wishlist, date_viewed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', browsing_rows)

    connection.commit()
    print("  ✅ Sample user, purchase history, and browsing logs inserted")


# =============================================================
# MAIN — runs when you type: python3 database/setup_database.py
# =============================================================
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  Style Agent — Database Setup")
    print("=" * 55)

    # Create (or open) the database file
    connection = sqlite3.connect(DB_PATH)

    # Run all our setup functions in order
    create_all_tables(connection)
    seed_inventory(connection)
    seed_jewellery(connection)
    seed_user_data(connection)

    # Always close the connection when done
    connection.close()

    print("=" * 55)
    print(f"  ✅ Database ready at: {DB_PATH}")
    print("=" * 55 + "\n")
