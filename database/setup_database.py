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
    # The full clothing catalogue — rebuilt programmatically (500+ items)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_inventory (
            item_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name        TEXT NOT NULL,          -- full descriptive name
            category         TEXT,                   -- lehenga / top / bottom / footwear / bag etc.
            colour           TEXT,                   -- colour name e.g. "cobalt blue"
            colour_hex       TEXT,                   -- HEX code e.g. "#1A5276"
            colour_family    TEXT,                   -- warm / cool / neutral / earth / pastel / jewel
            fabric           TEXT,                   -- Silk / Cotton / Georgette etc.
            silhouette       TEXT,                   -- A-line / Flared / Straight etc.
            size_available   TEXT,                   -- comma-separated: "XS,S,M,L,XL,XXL"
            price            REAL,                   -- price in Indian Rupees
            brand_tier       TEXT,                   -- budget / mid / premium
            vibe_tags        TEXT,                   -- comma-separated: "ethnic,classic"
            occasion_tags    TEXT,                   -- comma-separated: "wedding,sangeet,festive"
            gender           TEXT DEFAULT "Women",   -- Women / Men / Unisex
            formality_score  INTEGER DEFAULT 3,      -- 1 (very casual) to 5 (black tie)
            stock_count      INTEGER DEFAULT 20,
            image_url        TEXT DEFAULT ""
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
# FUNCTION: seed_inventory_with_full_coverage
# Adds 40+ extra items so EVERY colour family + vibe + occasion
# combination always finds at least one match.
# Run this after seed_inventory() to ensure broad coverage.
# =============================================================
def seed_inventory_with_full_coverage(connection):
    """
    Inserts coverage items that cover every combination of:
    - 8 vibes: Ethnic, Modern, Boho, Indo-Western, Classic, Formal, Casual, Streetwear
    - Colour families: warm, cool, neutral, earth, pastel, jewel
    - Occasion groups: wedding/festive, professional, social/party, casual
    Uses INSERT OR IGNORE so safe to run multiple times.
    """
    cursor = connection.cursor()

    # Column order matches current_inventory schema:
    # item_name, category, colour, colour_hex, fabric, silhouette, cut, fit,
    # vibe, size_available, price, brand_tier, occasion_tags
    coverage_rows = [

        # ── ETHNIC TOPS — all colour families ──────────────────
        ("Terracotta hand-embroidered anarkali kurta",
         "Top","Terracotta","#C67C5A","Cotton","Anarkali","Anarkali","Regular",
         "Ethnic","XS,S,M,L,XL,XXL",1800,"Mid-range","wedding,mehendi,festive,pooja,navratri"),

        ("Rust silk A-line kurta with mirror work",
         "Top","Rust","#B7410E","Silk","A-Line","A-Line","Regular",
         "Ethnic","XS,S,M,L,XL,XXL",2200,"Mid-range","sangeet,diwali,navratri,festive,eid"),

        ("Deep red Banarasi silk kurta",
         "Top","Deep Red","#8B0000","Silk","Straight","Straight","Regular",
         "Ethnic","XS,S,M,L,XL",3200,"Mid-range","wedding,pooja,festive,reception,diwali"),

        ("Cobalt blue Chanderi silk kurta with zari border",
         "Top","Cobalt Blue","#0047AB","Chanderi Silk","Straight","Straight","Regular",
         "Ethnic","XS,S,M,L,XL,XXL",1600,"Mid-range","wedding,sangeet,festive,eid,diwali"),

        ("Emerald green velvet anarkali top",
         "Top","Emerald Green","#046307","Velvet","Anarkali","Anarkali","Regular",
         "Ethnic","XS,S,M,L,XL",2800,"Mid-range","wedding,sangeet,festive,reception"),

        ("Lavender georgette kurta with thread embroidery",
         "Top","Lavender","#B57EDC","Georgette","A-Line","A-Line","Regular",
         "Ethnic","XS,S,M,L,XL,XXL",1400,"Mid-range","mehendi,haldi,festive,casual,pooja"),

        ("Blush pink silk kurta with pintuck detail",
         "Top","Blush Pink","#FFB6C1","Silk-Cotton","Straight","Straight","Regular",
         "Ethnic","S,M,L,XL",1300,"Mid-range","mehendi,haldi,pooja,festive,sangeet"),

        ("Powder blue mul-cotton chikankari kurta",
         "Top","Powder Blue","#B0C4DE","Mul-Cotton","Straight","Straight","Regular",
         "Ethnic","XS,S,M,L,XL,XXL",990,"Budget","casual,pooja,mehendi,festive"),

        ("Ivory silk straight kurta with gold zari",
         "Top","Ivory","#FFFFF0","Silk","Straight","Straight","Regular",
         "Ethnic","XS,S,M,L,XL",2400,"Mid-range","wedding,pooja,festive,formal,reception"),

        ("Beige linen kurta with minimal embroidery",
         "Top","Beige","#F5F0E8","Linen","Straight","Straight","Regular",
         "Ethnic","S,M,L,XL",1100,"Mid-range","office,casual,pooja,mehendi"),

        # ── MODERN TOPS — all colour families ──────────────────
        ("Royal blue crepe wrap dress",
         "Dress","Royal Blue","#2471A3","Crepe","Wrap","Wrap Dress","Fitted",
         "Modern","XS,S,M,L,XL,XXL",1800,"Mid-range","office,client_meeting,birthday_party,date_night"),

        ("Steel blue linen relaxed shirt",
         "Top","Steel Blue","#4682B4","Linen","Relaxed","Shirt","Regular",
         "Modern","XS,S,M,L,XL",1200,"Mid-range","office,brunch,casual,networking_event"),

        ("Burnt orange shift dress in crepe",
         "Dress","Burnt Orange","#CC5500","Crepe","Shift","Shift Dress","Regular",
         "Modern","XS,S,M,L,XL",1700,"Mid-range","brunch,birthday_party,girls_night_out,casual"),

        ("Coral linen co-ord top",
         "Top","Coral","#FF6B6B","Linen","Relaxed","Top","Relaxed",
         "Modern","XS,S,M,L,XL",1400,"Mid-range","brunch,shopping_trip,casual,travel"),

        ("Mustard yellow structured blazer dress",
         "Dress","Mustard Yellow","#FFDB58","Polyester-Blend","Blazer-Dress","Blazer Dress","Regular",
         "Modern","XS,S,M,L,XL",2600,"Mid-range","office,conference,networking_event,formal_dinner"),

        ("White cotton poplin relaxed shirt",
         "Top","White","#FFFFFF","Cotton","Relaxed","Shirt","Regular",
         "Modern","XS,S,M,L,XL,XXL",700,"Budget","office,job_interview,casual,brunch"),

        ("Black fitted rib-knit top",
         "Top","Black","#1A1A1A","Rib-Knit","Fitted","Top","Fitted",
         "Modern","XS,S,M,L,XL",900,"Budget","office,date_night,party,casual,birthday_party"),

        ("Sage green cotton maxi dress with smocking",
         "Dress","Sage Green","#B2AC88","Cotton","Maxi","Maxi Dress","Relaxed",
         "Boho","XS,S,M,L,XL,XXL",1600,"Mid-range","brunch,shopping_trip,travel,casual,date_night"),

        ("Dusty rose tiered ruffle midi dress",
         "Dress","Dusty Rose","#C9A898","Rayon","Tiered","Tiered Dress","Relaxed",
         "Boho","XS,S,M,L,XL",1800,"Mid-range","date_night,brunch,birthday_party,casual,girls_night_out"),

        ("Olive green linen co-ord top",
         "Top","Olive Green","#556B2F","Linen","Relaxed","Top","Relaxed",
         "Boho","XS,S,M,L,XL,XXL",1400,"Mid-range","travel,shopping_trip,casual,brunch,sunday_outing"),

        # ── FORMAL OUTERWEAR ───────────────────────────────────
        ("Navy blue structured blazer",
         "Outerwear","Navy","#000080","Stretch Wool","Structured","Blazer","Slim",
         "Formal","XS,S,M,L,XL",2500,"Mid-range","office,job_interview,conference,formal_dinner,networking_event"),

        ("Charcoal grey tailored blazer",
         "Outerwear","Charcoal","#36454F","Wool-Blend","Structured","Blazer","Tailored",
         "Formal","XS,S,M,L,XL",2800,"Mid-range","job_interview,conference,client_meeting,black_tie,office"),

        ("Ivory single-button linen blazer",
         "Outerwear","Ivory","#FFFFF0","Linen","Structured","Blazer","Regular",
         "Modern","XS,S,M,L,XL",2200,"Mid-range","office,networking_event,brunch,conference"),

        ("Olive green denim jacket oversized",
         "Outerwear","Olive Green","#556B2F","Denim","Oversized","Jacket","Oversized",
         "Casual","XS,S,M,L,XL,XXL",2000,"Mid-range","shopping_trip,travel,casual,brunch,college"),

        # ── BOTTOMS — broad coverage ───────────────────────────
        ("Cream linen wide-leg trousers",
         "Bottom","Cream","#F5F0E8","Linen","Wide-Leg","Trousers","Relaxed",
         "Modern","XS,S,M,L,XL,XXL",1400,"Mid-range","office,brunch,casual,travel"),

        ("Camel cotton-blend straight trousers",
         "Bottom","Camel","#C19A6B","Cotton-Blend","Straight","Trousers","Regular",
         "Classic","XS,S,M,L,XL",1600,"Mid-range","office,client_meeting,brunch,casual"),

        ("Brown faux-suede midi skirt",
         "Bottom","Brown","#8B4513","Faux Suede","Midi A-Line","Skirt","Regular",
         "Modern","XS,S,M,L,XL",1900,"Mid-range","date_night,brunch,shopping_trip,casual"),

        ("Terracotta A-line midi skirt",
         "Bottom","Terracotta","#C67C5A","Cotton","A-Line","Skirt","Regular",
         "Boho","XS,S,M,L,XL,XXL",1100,"Mid-range","brunch,shopping_trip,casual,date_night,sunday_outing"),

        ("Cobalt blue flared palazzo",
         "Bottom","Cobalt Blue","#0047AB","Georgette","Flared","Palazzo","Relaxed",
         "Ethnic","XS,S,M,L,XL,XXL",950,"Mid-range","festive,sangeet,casual,party,birthday_party"),

        ("White linen straight trousers",
         "Bottom","White","#FFFFFF","Linen","Straight","Trousers","Regular",
         "Modern","XS,S,M,L,XL,XXL",1100,"Budget","office,brunch,casual,travel,networking_event"),

        ("Ivory palazzo in chanderi silk",
         "Bottom","Ivory","#FFFFF0","Chanderi","Wide-Leg","Palazzo","Relaxed",
         "Ethnic","XS,S,M,L,XL,XXL",900,"Mid-range","wedding,festive,office,formal,reception"),

        # ── FOOTWEAR — all occasions ───────────────────────────
        ("Gold block-heel sandals",
         "Footwear","Gold","#D4AF37","Faux Leather","Block Heel","Sandals","Regular",
         "Ethnic","All Sizes",1400,"Mid-range","wedding,festive,party,date_night,sangeet"),

        ("Nude pointed-toe kitten heels",
         "Footwear","Nude","#F5DEB3","Faux Leather","Kitten Heel","Heels","Slim",
         "Modern","All Sizes",1600,"Mid-range","office,job_interview,formal_dinner,networking_event,conference"),

        ("Black block-heel ankle boots",
         "Footwear","Black","#1A1A1A","Faux Leather","Block Heel","Ankle Boot","Regular",
         "Classic","All Sizes",2200,"Mid-range","office,date_night,party,casual,birthday_party"),

        ("White chunky sneakers",
         "Footwear","White","#FFFFFF","Mesh/Rubber","Platform","Sneakers","Regular",
         "Streetwear","All Sizes",1800,"Mid-range","shopping_trip,brunch,travel,casual,college"),

        ("Silver strappy heeled sandals",
         "Footwear","Silver","#C0C0C0","Metallic Faux Leather","Stiletto","Heels","Slim",
         "Modern","All Sizes",1900,"Mid-range","wedding,sangeet,party,formal_dinner,date_night"),

        ("Tan kolhapuri flat chappals",
         "Footwear","Tan","#D2B48C","Leather","Flat","Chappals","Regular",
         "Ethnic","All Sizes",800,"Budget","casual,mehendi,pooja,shopping_trip,festive"),

        # ── BAGS — all occasions ───────────────────────────────
        ("Ivory potli bag with gold embroidery",
         "Bag","Ivory","#FFFFF0","Silk","Potli","Potli","Regular",
         "Ethnic","One Size",600,"Mid-range","wedding,festive,party,sangeet,reception"),

        ("Black structured office tote",
         "Bag","Black","#1A1A1A","Faux Leather","Structured","Tote","Regular",
         "Modern","One Size",1500,"Mid-range","office,job_interview,conference,casual,client_meeting"),

        ("Tan woven straw tote",
         "Bag","Tan","#D2B48C","Straw","Tote","Tote","Regular",
         "Boho","One Size",900,"Mid-range","brunch,shopping_trip,travel,casual,beach"),

        ("Gold metallic evening clutch",
         "Bag","Gold","#D4AF37","Metallic Faux Leather","Clutch","Clutch","Regular",
         "Modern","One Size",850,"Mid-range","party,wedding,date_night,festive,formal_dinner"),

        ("Nude mini crossbody bag",
         "Bag","Nude","#F5DEB3","Faux Leather","Crossbody","Crossbody","Regular",
         "Modern","One Size",1200,"Mid-range","office,brunch,date_night,shopping_trip,casual"),

        # ── ETHNIC DUPATTAS / OUTERWEAR ────────────────────────
        ("Ivory organza dupatta with gold border",
         "Outerwear","Ivory","#FFFFF0","Organza","Dupatta","Dupatta","Free",
         "Ethnic","Free Size",600,"Mid-range","wedding,festive,formal,pooja,reception"),

        ("Blush pink chiffon dupatta with silver threadwork",
         "Outerwear","Blush Pink","#FFB6C1","Chiffon","Dupatta","Dupatta","Free",
         "Ethnic","Free Size",550,"Mid-range","mehendi,sangeet,festive,casual,haldi"),

        ("Cobalt blue georgette dupatta with zari trim",
         "Outerwear","Cobalt Blue","#0047AB","Georgette","Dupatta","Dupatta","Free",
         "Ethnic","Free Size",500,"Mid-range","wedding,sangeet,festive,eid,diwali"),
    ]

    # Use INSERT OR IGNORE so this is safe to run multiple times
    cursor.executemany("""
        INSERT OR IGNORE INTO current_inventory
        (item_name, category, colour, colour_hex, fabric, silhouette,
         cut, fit, vibe, size_available, price, brand_tier, occasion_tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, coverage_rows)

    connection.commit()
    print(f"  ✅ Coverage items added: {len(coverage_rows)} items covering all colours, vibes, and occasions")



def seed_indian_ethnic_garments(connection):
    """
    UPGRADE 4 — Adds proper Indian garment types to the inventory.
    These use the correct Indian clothing categories (lehenga, sharara, etc.)
    instead of generic 'Top' or 'Dress' so ethnic occasion filtering works correctly.
    Safe to run multiple times — uses INSERT OR IGNORE.
    """
    cursor = connection.cursor()

    # Each row: (item_name, category, colour, colour_hex, fabric, silhouette,
    #            cut, fit, vibe, size_available, price, brand_tier, occasion_tags)
    indian_items = [

        # ── LEHENGAS ──────────────────────────────────────────────────────────────
        ("Crimson red silk lehenga set with gold zari embroidery — choli, skirt, net dupatta",
         "lehenga", "crimson red", "#8B0000", "Silk", "Flared", "Flared Lehenga", "Regular",
         "Ethnic,Classic", "XS,S,M,L,XL", 8000, "Premium",
         "wedding,sangeet,festive,diwali,reception"),

        ("Royal blue tissue silk lehenga with silver gota patti — 3-piece set",
         "lehenga", "royal blue", "#000080", "Tissue Silk", "Flared", "Flared Lehenga", "Regular",
         "Ethnic,Classic", "XS,S,M,L,XL", 6500, "Premium",
         "sangeet,wedding,festive,reception"),

        ("Dusty rose organza lehenga with mirror and thread embroidery — 3-piece",
         "lehenga", "dusty rose", "#FFB6C1", "Organza", "Flared", "Flared Lehenga", "Regular",
         "Ethnic,Indo-Western", "XS,S,M,L,XL,XXL", 5000, "Mid-range",
         "mehendi,sangeet,festive,haldi"),

        ("Ivory and gold Banarasi silk lehenga — heavy gold zari weave, bridal quality",
         "lehenga", "ivory", "#FFFFF0", "Banarasi Silk", "Flared", "Flared Lehenga", "Regular",
         "Ethnic,Classic", "XS,S,M,L,XL", 12000, "Premium",
         "wedding,festive,reception"),

        ("Sage green georgette lehenga with resham embroidery — lightweight all-day wear",
         "lehenga", "sage green", "#B2AC88", "Georgette", "A-Line", "A-Line Lehenga", "Regular",
         "Ethnic,Indo-Western", "XS,S,M,L,XL,XXL", 4200, "Mid-range",
         "mehendi,haldi,sangeet,festive"),

        ("Cobalt blue velvet lehenga with kundan and pearl embellishment",
         "lehenga", "cobalt blue", "#0047AB", "Velvet", "Flared", "Flared Lehenga", "Regular",
         "Ethnic,Classic", "XS,S,M,L,XL", 7500, "Premium",
         "wedding,sangeet,festive,diwali"),

        # ── SHARARAS ──────────────────────────────────────────────────────────────
        ("Terracotta silk sharara set — straight kurta, wide flared sharara, organza dupatta",
         "sharara", "terracotta", "#C67C5A", "Silk", "Wide-Flared", "Sharara", "Regular",
         "Ethnic", "XS,S,M,L,XL,XXL", 3800, "Mid-range",
         "wedding,sangeet,festive,navratri"),

        ("Mint green chiffon sharara with delicate chikankari embroidery",
         "sharara", "mint green", "#98D8C8", "Chiffon", "Wide-Flared", "Sharara", "Regular",
         "Ethnic,Indo-Western", "XS,S,M,L,XL,XXL", 2800, "Mid-range",
         "mehendi,haldi,festive,casual"),

        ("Lavender georgette sharara with gold sequin border and matching dupatta",
         "sharara", "lavender", "#B57EDC", "Georgette", "Wide-Flared", "Sharara", "Regular",
         "Ethnic", "XS,S,M,L,XL,XXL", 3200, "Mid-range",
         "sangeet,mehendi,festive,navratri"),

        ("Deep burgundy raw silk sharara — embroidered kurta with resham thread work",
         "sharara", "burgundy", "#800020", "Raw Silk", "Wide-Flared", "Sharara", "Regular",
         "Ethnic,Classic", "XS,S,M,L,XL", 4500, "Mid-range",
         "wedding,sangeet,diwali,festive"),

        # ── GHARARAS ──────────────────────────────────────────────────────────────
        ("Pastel pink mul-cotton gharara set with gota embroidery — Lucknowi style",
         "gharara", "pastel pink", "#FFB6C1", "Mul-Cotton", "Pleated", "Gharara", "Regular",
         "Ethnic", "XS,S,M,L,XL,XXL", 2200, "Mid-range",
         "mehendi,haldi,eid,festive,casual"),

        ("Off-white chanderi gharara with blue block print — casual ethnic festive",
         "gharara", "off-white", "#FFFFF0", "Chanderi", "Pleated", "Gharara", "Regular",
         "Ethnic,Casual", "XS,S,M,L,XL,XXL", 1800, "Mid-range",
         "mehendi,pooja,casual,festive"),

        # ── ANARKALIS ──────────────────────────────────────────────────────────────
        ("Floor-length emerald green Anarkali suit with dupatta — silk georgette",
         "anarkali", "emerald green", "#046307", "Silk Georgette", "Floor-Length Flared",
         "Anarkali", "Regular",
         "Ethnic,Classic,Indo-Western", "XS,S,M,L,XL,XXL", 3500, "Mid-range",
         "wedding,sangeet,diwali,festive,formal"),

        ("Peacock blue printed Anarkali with contrast palazzo and dupatta",
         "anarkali", "peacock blue", "#0047AB", "Chiffon", "Knee-Length Flared",
         "Anarkali", "Regular",
         "Ethnic,Indo-Western", "XS,S,M,L,XL,XXL", 2400, "Mid-range",
         "wedding,festive,casual,brunch"),

        ("Rust orange cotton Anarkali with mirror embroidery — daily ethnic wear",
         "anarkali", "rust orange", "#CC5500", "Cotton", "Knee-Length Flared",
         "Anarkali", "Regular",
         "Ethnic,Casual", "XS,S,M,L,XL,XXL", 1400, "Budget",
         "pooja,casual,college,festive"),

        # ── SAREES ────────────────────────────────────────────────────────────────
        ("Deep red Kanjeevaram silk saree with gold zari border — classic bridal look",
         "saree", "deep red", "#8B0000", "Kanjeevaram Silk", "6-Yard Drape",
         "Draped", "Free Size",
         "Ethnic,Classic", "free size", 15000, "Premium",
         "wedding,pooja,festive,formal dinner,reception"),

        ("Teal blue georgette saree with silver border and blouse piece",
         "saree", "teal blue", "#008080", "Georgette", "6-Yard Drape",
         "Draped", "Free Size",
         "Ethnic,Classic,Formal", "free size", 2200, "Mid-range",
         "office,wedding,festive,formal dinner"),

        # ── INDO-WESTERN SETS ─────────────────────────────────────────────────────
        ("Navy blue crop top and dhoti skirt set — heavy embroidery, premium indo-western",
         "dhoti_skirt", "navy blue", "#000080", "Raw Silk", "Dhoti Drape",
         "Dhoti Skirt", "Regular",
         "Indo-Western,Modern", "XS,S,M,L,XL", 4800, "Premium",
         "sangeet,party,date night,festive"),

        ("Ivory cape set — long embroidered cape over straight trousers and crop top",
         "cape_set", "ivory", "#FFFFF0", "Georgette", "Cape and Trouser",
         "Cape Set", "Regular",
         "Indo-Western,Modern,Classic", "XS,S,M,L,XL", 5200, "Premium",
         "sangeet,wedding guest,formal,party"),

        ("Dusty pink palazzo suit — embroidered kurta, wide palazzo, sheer dupatta",
         "palazzo_set", "dusty pink", "#FFB6C1", "Chiffon", "Wide-Leg",
         "Palazzo Set", "Regular",
         "Ethnic,Indo-Western,Casual", "XS,S,M,L,XL,XXL", 2600, "Mid-range",
         "casual,mehendi,brunch,festive,pooja"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO current_inventory
        (item_name, category, colour, colour_hex, fabric, silhouette,
         cut, fit, vibe, size_available, price, brand_tier, occasion_tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, indian_items)

    connection.commit()
    print(f"  ✅ Indian ethnic garments added: {len(indian_items)} items "
          f"(lehengas, shararas, ghararas, anarkalis, sarees, indo-western sets)")



# =============================================================
# FIX 6 — DENSE INVENTORY GENERATOR
# Generates 425+ items programmatically from templates.
# This replaces all previous seed_inventory functions.
# =============================================================

def fabric_from_template(name_template):
    """
    Extracts or infers a fabric name from the item template name string.
    Checks for fabric keywords and returns a sensible default if none match.
    """
    n = name_template.lower()   # lowercase the name for easy keyword checks
    if "silk" in n:        return "silk"
    if "georgette" in n:   return "georgette"
    if "chiffon" in n:     return "chiffon"
    if "cotton" in n:      return "cotton"
    if "linen" in n:       return "linen"
    if "velvet" in n:      return "velvet"
    if "organza" in n:     return "organza"
    if "crepe" in n:       return "crepe"
    if "denim" in n:       return "denim"
    if "leather" in n:     return "faux leather"
    if "knit" in n:        return "rib-knit"
    if "chanderi" in n:    return "chanderi"
    if "chikankari" in n:  return "mul-cotton"
    return "polyester-blend"   # safe default for anything not listed


def generate_full_inventory(conn):
    """
    Generates 425+ inventory items programmatically using templates.
    Each template is combined with 6 colour families to produce
    multiple items automatically. This guarantees the database
    is dense enough to always find a match for any user input.
    """
    import random   # for slight price variation between items
    random.seed(42)   # fixed seed so the DB is the same every time we run

    cursor = conn.cursor()   # cursor is the 'pen' for writing to the DB

    # ── ITEM TEMPLATES ────────────────────────────────────────────────────────
    # Each row: (name_template, category, silhouette, brand_tier,
    #            vibe_tags, occasion_tags, gender, formality_score,
    #            base_price, price_variance)
    # {colour} is a placeholder replaced with each colour name below.

    ITEM_TEMPLATES = [

        # ══ WOMEN — INDIAN ETHNIC ═══════════════════════════════════════════
        ("{colour} silk lehenga set — gold zari embroidery, choli, skirt, dupatta",
         "lehenga", "flared lehenga", "premium",
         "ethnic,classic", "wedding,sangeet,festive,diwali,reception",
         "Women", 5, 7000, 3000),

        ("{colour} georgette lehenga with resham thread work — 3-piece set",
         "lehenga", "a-line lehenga", "mid",
         "ethnic,indo-western", "sangeet,mehendi,festive,party",
         "Women", 4, 4000, 2000),

        ("{colour} organza lehenga with mirror embroidery — bridal ready",
         "lehenga", "flared lehenga", "premium",
         "ethnic,classic", "wedding,festive,reception",
         "Women", 5, 9000, 4000),

        ("{colour} cotton lehenga with block print — casual festive",
         "lehenga", "a-line lehenga", "budget",
         "ethnic,boho,casual", "mehendi,haldi,casual,navratri",
         "Women", 3, 2000, 1000),

        ("{colour} silk sharara set — straight kurta, wide sharara, organza dupatta",
         "sharara", "wide-flared sharara", "mid",
         "ethnic", "wedding,sangeet,festive,navratri,eid",
         "Women", 4, 3500, 1500),

        ("{colour} chiffon sharara with chikankari embroidery — ethereal drape",
         "sharara", "wide-flared sharara", "mid",
         "ethnic,indo-western", "mehendi,haldi,festive,casual",
         "Women", 3, 2800, 1200),

        ("{colour} georgette sharara with sequin border — party ready",
         "sharara", "wide-flared sharara", "mid",
         "ethnic", "sangeet,party,festive,navratri",
         "Women", 4, 3200, 1000),

        ("{colour} mul-cotton gharara with gota embroidery — Lucknowi style",
         "gharara", "pleated gharara", "mid",
         "ethnic", "mehendi,haldi,eid,festive,casual",
         "Women", 3, 2200, 800),

        ("{colour} chanderi gharara with block print — casual ethnic",
         "gharara", "pleated gharara", "budget",
         "ethnic,casual", "mehendi,pooja,casual,festive",
         "Women", 2, 1600, 700),

        ("{colour} floor-length Anarkali suit with dupatta — silk georgette",
         "anarkali", "floor-length flared", "mid",
         "ethnic,classic,indo-western", "wedding,sangeet,diwali,festive,formal dinner",
         "Women", 4, 3200, 1500),

        ("{colour} printed Anarkali with contrast palazzo — everyday ethnic",
         "anarkali", "knee-length flared", "mid",
         "ethnic,indo-western,casual", "office,festive,casual,brunch",
         "Women", 2, 1800, 800),

        ("{colour} cotton Anarkali with mirror embroidery — casual daily wear",
         "anarkali", "knee-length flared", "budget",
         "ethnic,casual", "pooja,casual,college,festive",
         "Women", 2, 1200, 500),

        ("{colour} straight-cut salwar suit — dupatta and churidar",
         "salwar_suit", "straight cut", "mid",
         "ethnic,classic", "office,pooja,casual,festive,mehendi",
         "Women", 3, 2000, 800),

        ("{colour} Kanjeevaram silk saree with gold zari border",
         "saree", "6-yard drape", "premium",
         "ethnic,classic,formal", "wedding,pooja,festive,formal dinner",
         "Women", 5, 12000, 5000),

        ("{colour} georgette saree with embroidered border and blouse",
         "saree", "6-yard drape", "mid",
         "ethnic,classic,formal", "office,wedding,festive,formal dinner",
         "Women", 4, 2200, 1000),

        ("{colour} Chanderi saree with block print — light summer festive",
         "saree", "6-yard drape", "mid",
         "ethnic,boho,casual", "pooja,festive,mehendi,casual brunch",
         "Women", 3, 1800, 700),

        ("{colour} cotton saree with contrast border — office appropriate",
         "saree", "6-yard drape", "budget",
         "ethnic,classic", "office,casual,pooja",
         "Women", 3, 900, 400),

        ("{colour} crop top and dhoti skirt set with heavy embroidery",
         "dhoti_skirt", "dhoti drape skirt", "premium",
         "indo-western,modern", "sangeet,party,date night,festive",
         "Women", 4, 4500, 2000),

        ("{colour} cape set — embroidered cape over straight trousers",
         "cape_set", "cape and trouser", "premium",
         "indo-western,modern,classic", "sangeet,wedding guest,formal,party",
         "Women", 4, 5000, 2000),

        # ══ WOMEN — WESTERN / MODERN ══════════════════════════════════════
        ("{colour} cotton poplin shirt — relaxed collar and cuffs",
         "top", "relaxed fit shirt", "budget",
         "modern,classic,formal,casual", "office,interview,casual,brunch",
         "Women", 2, 700, 300),

        ("{colour} fitted turtleneck top — ribbed knit",
         "top", "fitted", "budget",
         "modern,classic,streetwear", "office,date night,party,casual",
         "Women", 2, 900, 400),

        ("{colour} chiffon flowy blouse with tie detail",
         "top", "flowy", "mid",
         "modern,boho,casual", "brunch,date night,party,casual",
         "Women", 3, 1200, 500),

        ("{colour} structured peplum top",
         "top", "peplum", "mid",
         "modern,formal,classic", "office,interview,formal dinner,party",
         "Women", 3, 1400, 600),

        ("{colour} crop top with square neckline",
         "top", "cropped", "mid",
         "modern,casual,streetwear", "brunch,party,casual,date night",
         "Women", 2, 800, 400),

        ("{colour} wide-leg crepe trousers — high waist",
         "bottom", "wide-leg trouser", "mid",
         "modern,formal,classic", "office,formal,party,casual",
         "Women", 3, 1200, 500),

        ("{colour} cigarette trousers — tailored slim",
         "bottom", "cigarette trouser", "mid",
         "modern,formal,classic", "office,interview,networking,formal dinner",
         "Women", 4, 1500, 600),

        ("{colour} A-line midi skirt — polyester blend",
         "bottom", "midi a-line skirt", "mid",
         "modern,classic,boho", "office,date night,brunch,casual",
         "Women", 3, 1100, 500),

        ("{colour} wide-leg palazzo — flowing drape",
         "bottom", "palazzo", "mid",
         "modern,casual,ethnic,boho", "office,casual,festive,travel",
         "Women", 2, 900, 400),

        ("{colour} linen straight-cut trousers",
         "bottom", "straight cut trouser", "budget",
         "modern,casual,formal,boho", "office,brunch,casual,travel",
         "Women", 3, 1100, 400),

        ("{colour} wrap dress — midi length crepe",
         "top_or_dress", "midi wrap dress", "mid",
         "modern,classic", "office,client meeting,birthday party,date night",
         "Women", 3, 1800, 800),

        ("{colour} shift dress — knee length",
         "top_or_dress", "shift dress", "mid",
         "modern,casual,formal", "brunch,birthday party,casual,date night",
         "Women", 3, 1600, 700),

        ("{colour} blazer dress — single button",
         "top_or_dress", "blazer dress", "mid",
         "modern,formal,classic", "office,conference,networking,formal dinner",
         "Women", 4, 2500, 1000),

        ("{colour} maxi dress with smocking detail",
         "top_or_dress", "maxi dress", "mid",
         "boho,casual,modern", "brunch,shopping trip,travel,casual,date night",
         "Women", 2, 1600, 700),

        ("{colour} structured blazer — notch lapel",
         "outerwear", "tailored blazer", "mid",
         "modern,formal,classic", "office,interview,conference,formal dinner",
         "Women", 4, 2500, 1000),

        ("{colour} oversized linen blazer — casual",
         "outerwear", "oversized blazer", "mid",
         "modern,casual,boho", "brunch,casual,shopping trip,travel",
         "Women", 2, 2000, 800),

        ("{colour} organza dupatta with gold border",
         "outerwear", "dupatta", "mid",
         "ethnic,indo-western,classic", "wedding,festive,formal,pooja",
         "Women", 4, 600, 300),

        ("{colour} chiffon dupatta with silver threadwork",
         "outerwear", "dupatta", "mid",
         "ethnic,indo-western", "mehendi,sangeet,festive,casual",
         "Women", 3, 500, 250),

        # ══ WOMEN — FOOTWEAR ════════════════════════════════════════════════
        ("{colour} block-heel sandals — 3 inch",
         "footwear", "block heel sandal", "mid",
         "ethnic,indo-western,classic,modern", "wedding,festive,party,date night",
         "Women", 4, 1400, 600),

        ("{colour} pointed-toe kitten heels — 2 inch",
         "footwear", "kitten heel", "mid",
         "modern,formal,classic", "office,interview,formal dinner,networking",
         "Women", 4, 1600, 700),

        ("{colour} block-heel ankle boots",
         "footwear", "ankle boot", "mid",
         "modern,formal,streetwear,classic", "office,date night,party,casual",
         "Women", 3, 2200, 900),

        ("{colour} flat strappy sandals",
         "footwear", "flat sandal", "budget",
         "casual,boho,ethnic,indo-western", "casual,mehendi,brunch,shopping trip",
         "Women", 1, 700, 300),

        ("{colour} chunky sneakers",
         "footwear", "flatform sneaker", "mid",
         "casual,streetwear,modern", "shopping trip,brunch,travel,casual,college",
         "Women", 1, 1800, 700),

        ("{colour} kolhapuri flats — handcrafted leather",
         "footwear", "kolhapuri flat", "budget",
         "ethnic,boho,casual,indo-western", "casual,mehendi,pooja,shopping trip",
         "Women", 2, 800, 300),

        ("{colour} heeled mules — square toe",
         "footwear", "mule heel", "mid",
         "modern,casual,boho", "brunch,casual,date night,shopping trip",
         "Women", 2, 1500, 600),

        # ══ WOMEN — BAGS ════════════════════════════════════════════════════
        ("{colour} potli bag with gold embroidery",
         "bag", "potli", "mid",
         "ethnic,indo-western,classic", "wedding,festive,party,sangeet",
         "Women", 4, 600, 300),

        ("{colour} structured tote bag — faux leather",
         "bag", "tote", "mid",
         "modern,formal,classic", "office,interview,conference,casual",
         "Women", 3, 1500, 600),

        ("{colour} mini crossbody bag — chain strap",
         "bag", "crossbody", "mid",
         "modern,casual,classic,formal", "office,brunch,date night,party",
         "Women", 3, 1200, 500),

        ("{colour} envelope clutch — faux leather",
         "bag", "clutch", "mid",
         "modern,ethnic,classic,indo-western",
         "party,wedding,date night,festive,formal dinner",
         "Women", 4, 850, 400),

        ("{colour} woven straw tote",
         "bag", "tote", "budget",
         "boho,casual,modern", "brunch,shopping trip,travel,casual",
         "Women", 1, 900, 400),

        # ══ MEN — INDIAN ETHNIC ════════════════════════════════════════════
        ("{colour} kurta pyjama set — straight cut, mandarin collar",
         "kurta_pyjama", "straight kurta", "mid",
         "ethnic,classic,casual",
         "wedding,sangeet,pooja,diwali,eid,festive,casual",
         "Men", 3, 2200, 1000),

        ("{colour} silk kurta pyjama — heavy embroidery for weddings",
         "kurta_pyjama", "straight kurta", "premium",
         "ethnic,classic", "wedding,sangeet,festive",
         "Men", 5, 5000, 2500),

        ("{colour} cotton pathani suit — full length",
         "kurta_pyjama", "pathani full", "mid",
         "ethnic,classic", "eid,pooja,casual,festive",
         "Men", 3, 2800, 1200),

        ("{colour} Nehru jacket — wear over white kurta for indo-western",
         "nehru_jacket", "nehru jacket", "mid",
         "indo-western,ethnic,classic",
         "wedding,sangeet,festive,formal dinner",
         "Men", 4, 3500, 1500),

        ("{colour} bandhgala suit — Jodhpuri style",
         "bandhgala", "jodhpuri bandhgala", "premium",
         "ethnic,classic,formal",
         "wedding,sangeet,formal dinner,award ceremony",
         "Men", 5, 7000, 3000),

        ("{colour} sherwani with churidar — embroidered collar and cuffs",
         "sherwani", "sherwani full", "premium",
         "ethnic,classic", "wedding,festive",
         "Men", 5, 10000, 5000),

        # ══ MEN — WESTERN / MODERN ═════════════════════════════════════════
        ("{colour} formal dress shirt — slim fit Oxford",
         "top", "slim fit shirt", "mid",
         "modern,formal,classic",
         "office,interview,conference,formal dinner,networking",
         "Men", 4, 900, 400),

        ("{colour} linen shirt — relaxed fit, casual",
         "top", "relaxed linen shirt", "mid",
         "modern,casual,boho", "brunch,casual,travel,shopping trip",
         "Men", 2, 1200, 500),

        ("{colour} structured blazer — two button",
         "outerwear", "two-button blazer", "mid",
         "modern,formal,classic",
         "office,interview,conference,formal dinner",
         "Men", 4, 3000, 1200),

        ("{colour} chino trousers — slim tapered",
         "bottom", "slim chino", "mid",
         "modern,casual,formal",
         "office,casual,brunch,networking,date night",
         "Men", 3, 1400, 600),

        ("{colour} formal trousers — flat front",
         "bottom", "flat front trouser", "mid",
         "modern,formal,classic",
         "office,interview,conference,formal dinner",
         "Men", 4, 1600, 700),

        ("{colour} slim jeans — dark wash",
         "bottom", "slim straight jeans", "mid",
         "casual,modern,streetwear",
         "casual,brunch,date night,party,college",
         "Men", 2, 1500, 600),

        # ══ MEN — FOOTWEAR ══════════════════════════════════════════════════
        ("{colour} leather Oxford shoes — formal",
         "footwear", "oxford formal", "mid",
         "modern,formal,classic",
         "office,interview,wedding,formal dinner",
         "Men", 5, 2500, 1000),

        ("{colour} loafers — penny strap",
         "footwear", "penny loafer", "mid",
         "modern,casual,classic", "office,brunch,casual,date night",
         "Men", 3, 2000, 800),

        ("{colour} leather kolhapuri chappals — ethnic",
         "footwear", "kolhapuri flat", "budget",
         "ethnic,casual,boho", "casual,pooja,mehendi,festive",
         "Men", 2, 600, 300),

        ("{colour} white sneakers — low top clean",
         "footwear", "low sneaker", "mid",
         "casual,modern,streetwear",
         "casual,college,brunch,shopping trip",
         "Men", 1, 1800, 700),

        ("{colour} mojari — embroidered ethnic shoes",
         "footwear", "mojari", "mid",
         "ethnic,indo-western,classic", "wedding,sangeet,festive,pooja",
         "Men", 4, 1200, 500),

        # ══ MEN — BAGS ══════════════════════════════════════════════════════
        ("{colour} leather belt — pin buckle",
         "bag", "belt", "mid",
         "modern,formal,classic,casual",
         "office,interview,casual,formal dinner",
         "Men", 3, 800, 300),

        ("{colour} potli / jhola bag — cotton",
         "bag", "jhola bag", "budget",
         "ethnic,boho,casual", "festive,casual,travel,shopping trip",
         "Men", 2, 400, 200),

        ("{colour} formal messenger bag — faux leather",
         "bag", "messenger bag", "mid",
         "modern,formal", "office,conference,networking",
         "Men", 3, 1800, 700),

        # ══ UNISEX ══════════════════════════════════════════════════════════
        ("{colour} oversized denim jacket",
         "outerwear", "oversized jacket", "mid",
         "casual,streetwear,modern",
         "casual,travel,shopping trip,brunch,college",
         "Unisex", 1, 2000, 800),

        ("{colour} trench coat — belted midi length",
         "outerwear", "trench coat", "mid",
         "modern,classic,formal", "office,formal dinner,casual,travel",
         "Unisex", 4, 3500, 1500),
    ]

    # ── COLOUR FAMILIES ───────────────────────────────────────────────────────
    # Each family has one representative colour that will be used for templates.
    # The agent uses colour_family for fuzzy matching so exact shades vary.
    COLOUR_FAMILIES = [
        # (family_name, colour_name, colour_hex)
        ("warm",    "terracotta",       "#C07A5A"),
        ("warm",    "rust",             "#B5451B"),
        ("warm",    "mustard yellow",   "#D4A017"),
        ("cool",    "cobalt blue",      "#1A5276"),
        ("cool",    "emerald green",    "#1E8449"),
        ("cool",    "teal blue",        "#008080"),
        ("neutral", "ivory",            "#FFFFF0"),
        ("neutral", "charcoal grey",    "#36454F"),
        ("neutral", "black",            "#1A1A1A"),
        ("earth",   "camel",            "#C19A6B"),
        ("earth",   "olive green",      "#556B2F"),
        ("pastel",  "blush pink",       "#FFB6C1"),
        ("pastel",  "powder blue",      "#B0D0E8"),
        ("pastel",  "dusty rose",       "#DCAE96"),
        ("jewel",   "deep burgundy",    "#800020"),
        ("jewel",   "sapphire blue",    "#0F52BA"),
        ("jewel",   "ruby red",         "#9B1B30"),
    ]

    # ── GENERATE ALL ITEMS ────────────────────────────────────────────────────
    all_items = []   # list to collect every generated item tuple

    for template in ITEM_TEMPLATES:
        (name_tpl, category, silhouette, brand_tier,
         vibe_tags, occasion_tags, gender, formality_score,
         base_price, price_variance) = template

        # Combine each template with each colour family
        for family_name, colour_name, colour_hex in COLOUR_FAMILIES:

            # Skip obviously mismatched combinations
            # (e.g., don't put 'blush pink' on men's formal trousers)
            if gender == "Men" and family_name == "pastel" and formality_score >= 4:
                continue   # skip pastel formal men's — not a realistic match

            # Slightly vary the price so not all items cost exactly the same
            actual_price = base_price + random.randint(0, price_variance)

            # Fill in the colour placeholder in the name template
            item_name = name_tpl.replace("{colour}", colour_name.capitalize())

            # Infer fabric from the item name
            fabric = fabric_from_template(name_tpl)

            # Build the sizes string depending on gender
            if gender == "Women":
                sizes = "XS,S,M,L,XL,XXL"
            elif gender == "Men":
                sizes = "S,M,L,XL,XXL"
            else:
                sizes = "XS,S,M,L,XL,XXL"   # Unisex

            # Full item tuple — matches INSERT column order below
            item = (
                item_name,        # item_name
                category,         # category
                colour_name,      # colour (text name)
                colour_hex,       # colour_hex
                family_name,      # colour_family
                fabric,           # fabric
                silhouette,       # silhouette
                sizes,            # size_available
                actual_price,     # price
                brand_tier,       # brand_tier
                vibe_tags,        # vibe_tags
                occasion_tags,    # occasion_tags
                gender,           # gender
                formality_score,  # formality_score
                20,               # stock_count
                "",               # image_url (empty — filled later by scraper)
            )
            all_items.append(item)

    # ── SPECIFIC HIGH-PRIORITY ITEMS ─────────────────────────────────────────
    # These exact items fill the most common search: Ethnic + Wedding
    PRIORITY_ITEMS = [
        ("Crimson red Banarasi silk lehenga — gold zari weave, bridal quality, 3-piece",
         "lehenga", "crimson red", "#C0392B", "jewel", "banarasi silk",
         "flared lehenga", "XS,S,M,L,XL", 12000, "premium",
         "ethnic,classic", "wedding,festive,reception", "Women", 5, 10, ""),

        ("Royal blue Kanjeevaram silk saree — temple border, with unstitched blouse",
         "saree", "royal blue", "#2471A3", "cool", "kanjeevaram silk",
         "6-yard drape", "free size", 8000, "premium",
         "ethnic,classic,formal", "wedding,pooja,festive,formal dinner",
         "Women", 5, 8, ""),

        ("Ivory raw silk sherwani — gold zari collar and cuffs, full length",
         "sherwani", "ivory", "#FFFFF0", "neutral", "raw silk",
         "sherwani full", "S,M,L,XL,XXL", 9000, "premium",
         "ethnic,classic", "wedding,festive", "Men", 5, 6, ""),

        ("Dusty rose organza lehenga — subtle mirror work, perfect wedding guest",
         "lehenga", "dusty rose", "#DCAE96", "pastel", "organza",
         "a-line lehenga", "XS,S,M,L,XL,XXL", 5500, "mid",
         "ethnic,indo-western", "wedding,sangeet,festive", "Women", 4, 12, ""),

        ("Sage green bandhani sharara set — cotton silk, summer festive",
         "sharara", "sage green", "#8FAF8B", "cool", "cotton silk",
         "wide-flared sharara", "XS,S,M,L,XL,XXL", 2800, "mid",
         "ethnic,indo-western", "mehendi,haldi,festive,navratri",
         "Women", 3, 15, ""),
    ]

    # ── INSERT EVERYTHING INTO THE DATABASE ───────────────────────────────────
    # INSERT OR IGNORE means this function is safe to run multiple times
    cursor.executemany("""
        INSERT OR IGNORE INTO current_inventory
        (item_name, category, colour, colour_hex, colour_family, fabric, silhouette,
         size_available, price, brand_tier, vibe_tags, occasion_tags, gender,
         formality_score, stock_count, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, PRIORITY_ITEMS)   # priority items first — inserted at lower item_id

    cursor.executemany("""
        INSERT OR IGNORE INTO current_inventory
        (item_name, category, colour, colour_hex, colour_family, fabric, silhouette,
         size_available, price, brand_tier, vibe_tags, occasion_tags, gender,
         formality_score, stock_count, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, all_items)   # then the 420+ generated items

    conn.commit()   # save all inserts to disk
    total = len(PRIORITY_ITEMS) + len(all_items)
    print(f"  ✅ Generated and inserted {total} inventory items.")
    print(f"     Covers: all genders, all vibes, 17 colours, all occasion tiers.")


# =============================================================
# MAIN — runs when you type: python3 database/setup_database.py
# =============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Style Agent v5 — Database Setup")
    print("=" * 60)

    # Create (or open) the database file
    connection = sqlite3.connect(DB_PATH)

    # Step 1: Create all table structures
    create_all_tables(connection)

    # Step 2: Generate 425+ programmatic inventory items (Fix 6)
    generate_full_inventory(connection)

    # Step 3: Seed jewellery and user data (unchanged)
    seed_jewellery(connection)
    seed_user_data(connection)

    # Always close the connection when done
    connection.close()

    print("=" * 60)
    print(f"  ✅ Database ready at: {DB_PATH}")
    print("=" * 60 + "\n")
