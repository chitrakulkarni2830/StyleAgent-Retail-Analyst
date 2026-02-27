"""
setup_db.py — Database Initialization & Seed Data
Creates SQLite database with current_inventory, purchase_history, browsing_logs,
and user_preferences tables. Seeds with 100+ Indian fashion items and 3 mock users.
"""

import sqlite3
import os
import urllib.parse
import random
from datetime import datetime, timedelta

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "style_engine.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS current_inventory (
        sku TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,       -- Top / Bottom / Accessory / Footwear / Jewelry / Layer / Full
        brand TEXT,
        price REAL NOT NULL,
        color_family TEXT,
        color_hex TEXT,
        fabric TEXT,
        occasion_tags TEXT,           -- comma-separated: "wedding,sangeet,reception"
        silhouette TEXT,
        gender TEXT DEFAULT 'unisex', -- male / female / unisex
        region_suitability TEXT,      -- comma-separated: "pune,mumbai,delhi,chennai"
        image_url TEXT DEFAULT '',
        product_url TEXT DEFAULT '',          -- live link to product page
        stock_status TEXT DEFAULT 'in_stock',
        weight_category TEXT DEFAULT 'medium'  -- light / medium / heavy
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sku TEXT NOT NULL,
        purchase_date TEXT,
        category TEXT,
        color TEXT,
        style_tag TEXT,
        price REAL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS browsing_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sku TEXT NOT NULL,
        view_count INTEGER DEFAULT 1,
        last_viewed TEXT,
        dwell_time_sec REAL DEFAULT 0
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        preferred_colors TEXT,      -- comma-separated
        preferred_fabrics TEXT,     -- comma-separated
        size TEXT,
        skin_tone TEXT,             -- warm / cool / neutral
        budget_range TEXT,          -- "5000-15000"
        saved_style_dna TEXT
    )""")

    conn.commit()


# ═══════════════════════════════════════════════════════════════
#  SEED DATA — 100+ Indian Fashion Inventory Items
# ═══════════════════════════════════════════════════════════════

INVENTORY_DATA = [
    # ─── WOMEN'S SAREES ───
    ("SKU-W-SAR-001", "Royal Kanjeevaram Silk Saree", "Full", "Nalli Silks", 28500, "Maroon", "#800020", "Kanjeevaram Silk", "wedding,reception", "Draped", "female", "chennai,bangalore,mumbai", "heavy"),
    ("SKU-W-SAR-002", "Emerald Banarasi Brocade Saree", "Full", "Ekaya Banaras", 22000, "Emerald Green", "#046307", "Banarasi Silk", "wedding,reception,diwali", "Draped", "female", "delhi,lucknow,varanasi", "heavy"),
    ("SKU-W-SAR-003", "Paithani Saree — Purple & Gold", "Full", "Yeola Weavers", 18500, "Royal Purple", "#6A0DAD", "Paithani Silk", "wedding,reception", "Draped", "female", "pune,mumbai,nashik", "heavy"),
    ("SKU-W-SAR-004", "Lavender Chanderi Silk Saree", "Full", "FabIndia", 6500, "Lavender", "#B57EDC", "Chanderi Silk", "festival,corporate,haldi", "Draped", "female", "pune,indore,bhopal", "light"),
    ("SKU-W-SAR-005", "Mint Organza Saree with Sequin Border", "Full", "Sabyasachi", 35000, "Mint", "#98FF98", "Organza", "sangeet,cocktail,reception", "Draped", "female", "mumbai,delhi,bangalore", "light"),
    ("SKU-W-SAR-006", "Navy Blue Tussar Silk Saree", "Full", "Raw Mango", 15000, "Navy Blue", "#000080", "Tussar Silk", "corporate,date_night,diwali", "Draped", "female", "mumbai,delhi,pune", "medium"),
    ("SKU-W-SAR-007", "Peach Chiffon Saree — Floral", "Full", "Anita Dongre", 12000, "Peach", "#FFDAB9", "Chiffon", "haldi,mehendi,day_wedding", "Draped", "female", "all", "light"),
    ("SKU-W-SAR-008", "Red Bandhani Silk Saree", "Full", "Asha Gautam", 9800, "Red", "#D2042D", "Bandhani Silk", "navratri,wedding,festival", "Draped", "female", "jaipur,ahmedabad,udaipur", "medium"),
    ("SKU-W-SAR-009", "Cobalt Blue Silk Saree", "Full", "Raw Mango", 14500, "Cobalt Blue", "#0047AB", "Silk", "sangeet,reception,eid", "Draped", "female", "all", "medium"),
    ("SKU-W-SAR-010", "Ivory Linen Saree — Chikankari", "Full", "FabIndia", 5500, "Ivory", "#FFFFF0", "Linen", "festival,puja,corporate", "Draped", "female", "lucknow,delhi,pune", "light"),

    # ─── WOMEN'S LEHENGAS ───
    ("SKU-W-LEH-001", "Deep Wine Velvet Lehenga", "Full", "Manish Malhotra", 45000, "Deep Wine", "#722F37", "Velvet", "wedding,reception,sangeet", "Flared", "female", "delhi,mumbai,bangalore", "heavy"),
    ("SKU-W-LEH-002", "Champagne Gold Lehenga — Mirror Work", "Full", "Sabyasachi", 55000, "Gold", "#D4AF37", "Raw Silk", "wedding,sangeet", "Flared", "female", "all", "heavy"),
    ("SKU-W-LEH-003", "Pastel Pink Organza Lehenga", "Full", "Anita Dongre", 32000, "Pastel Pink", "#FFD1DC", "Organza", "sangeet,cocktail,mehendi", "Flared", "female", "all", "light"),
    ("SKU-W-LEH-004", "Teal Silk Lehenga — Zardozi", "Full", "Tarun Tahiliani", 38000, "Teal", "#008080", "Silk", "wedding,reception", "A-Line", "female", "all", "medium"),
    ("SKU-W-LEH-005", "Emerald Green Georgette Lehenga", "Full", "Biba", 12500, "Emerald Green", "#50C878", "Georgette", "wedding,sangeet,festival", "Flared", "female", "all", "medium"),
    ("SKU-W-LEH-006", "Navy Blue Semi-Stitched Lehenga", "Full", "Utsav Fashion", 3500, "Navy Blue", "#000080", "Art Silk", "wedding,sangeet,festival", "Flared", "female", "all", "medium"),
    ("SKU-W-LEH-007", "Maroon Unstitched Lehenga", "Full", "Kalki Fashion", 4800, "Maroon", "#800000", "Velvet", "wedding,reception", "A-Line", "female", "all", "heavy"),
    ("SKU-W-LEH-008", "Yellow Printed Unstitched Lehenga", "Full", "Biba", 2800, "Yellow", "#FFFF00", "Cotton", "haldi,festival", "Flared", "female", "all", "light"),
    ("SKU-W-LEH-009", "Peach Net Semi-Stitched Lehenga", "Full", "Koskii", 4200, "Peach Fuzz", "#FFCBA4", "Net", "sangeet,cocktail,mehendi", "Flared", "female", "all", "medium"),

    # ─── WOMEN'S KURTAS / SUITS ───
    ("SKU-W-KUR-001", "White Chikankari Anarkali", "Top", "FabIndia", 4500, "White", "#FFFFFF", "Cotton", "festival,puja,eid,casual", "Anarkali", "female", "lucknow,delhi,all", "light"),
    ("SKU-W-KUR-002", "Mustard Yellow Straight Kurta", "Top", "W", 2800, "Mustard Yellow", "#E1A95F", "Cotton Silk", "festival,haldi,mehendi,casual", "Straight", "female", "all", "light"),
    ("SKU-W-KUR-003", "Bottle Green Silk Kurta — Gota Patti", "Top", "Biba", 3500, "Bottle Green", "#006A4E", "Silk", "diwali,eid,festival", "Straight", "female", "jaipur,delhi,all", "medium"),
    ("SKU-W-KUR-004", "Coral Georgette Kurta Set", "Top", "Global Desi", 3200, "Coral", "#FF7F50", "Georgette", "haldi,mehendi,casual", "A-Line", "female", "all", "light"),
    ("SKU-W-KUR-005", "Royal Blue Velvet Kurta", "Top", "Ritu Kumar", 6800, "Royal Blue", "#002366", "Velvet", "diwali,reception,corporate", "Straight", "female", "delhi,mumbai", "medium"),

    # ─── WOMEN'S BOTTOMS ───
    ("SKU-W-BOT-001", "Gold Brocade Palazzo", "Bottom", "FabIndia", 3200, "Gold", "#D4AF37", "Brocade", "festival,diwali,wedding", "Wide Leg", "female", "all", "medium"),
    ("SKU-W-BOT-002", "Ivory Silk Sharara", "Bottom", "Biba", 4500, "Ivory", "#FFFFF0", "Silk", "eid,wedding,sangeet", "Flared", "female", "all", "medium"),
    ("SKU-W-BOT-003", "Black Churidar", "Bottom", "W", 1800, "Black", "#000000", "Cotton Lycra", "corporate,casual,festival", "Slim Fit", "female", "all", "light"),
    ("SKU-W-BOT-004", "Neutral Grey Trousers", "Bottom", "AND", 2500, "Neutral Grey", "#808080", "Cotton Blend", "corporate,date_night,casual", "Straight", "female", "all", "light"),
    ("SKU-W-BOT-005", "Maroon Silk Dhoti Pants", "Bottom", "Global Desi", 2800, "Maroon", "#800000", "Silk", "sangeet,cocktail,festival", "Draped", "female", "all", "light"),

    # ─── WOMEN'S JEWELRY ───
    ("SKU-W-JEW-001", "Antique Gold Temple Necklace Set", "Jewelry", "Tanishq", 18000, "Gold", "#D4AF37", "Gold", "wedding,reception,diwali", "Traditional", "female", "chennai,bangalore,all", "medium"),
    ("SKU-W-JEW-002", "Kundan Choker & Jhumka Set", "Jewelry", "Amrapali", 12500, "Gold", "#D4AF37", "Kundan", "wedding,sangeet,reception", "Traditional", "female", "jaipur,delhi,all", "medium"),
    ("SKU-W-JEW-003", "Rose Gold Minimal Stack Bracelet", "Jewelry", "CaratLane", 8500, "Rose Gold", "#B76E79", "Rose Gold", "date_night,corporate,cocktail,casual", "Modern", "female", "all", "light"),
    ("SKU-W-JEW-004", "Polki Maang Tikka", "Jewelry", "Amrapali", 6500, "Gold", "#D4AF37", "Polki", "wedding,reception", "Traditional", "female", "all", "light"),
    ("SKU-W-JEW-005", "Silver Oxidized Jhumkas", "Jewelry", "Tribe by Amrapali", 3200, "Silver", "#C0C0C0", "Silver", "festival,casual,boho", "Ethnic", "female", "all", "light"),
    ("SKU-W-JEW-006", "Baroque Pearl Drop Earrings", "Jewelry", "Swarovski", 7800, "Pearl White", "#FDEEF4", "Pearls", "cocktail,date_night,corporate", "Modern", "female", "all", "light"),
    ("SKU-W-JEW-007", "Emerald & Diamond Statement Necklace", "Jewelry", "Tanishq", 35000, "Emerald Green", "#046307", "Gold & Emerald", "wedding,reception", "Traditional", "female", "all", "medium"),
    ("SKU-W-JEW-008", "Ruby Stud Earrings — 22K Gold", "Jewelry", "Kalyan Jewellers", 15000, "Ruby Red", "#9B111E", "Gold & Ruby", "wedding,diwali,reception", "Traditional", "female", "all", "light"),

    # ─── WOMEN'S ACCESSORIES ───
    ("SKU-W-ACC-001", "Embroidered Potli Bag — Maroon", "Accessory", "Nappa Dori", 3500, "Maroon", "#800000", "Silk", "wedding,sangeet,reception", "Ethnic", "female", "all", "light"),
    ("SKU-W-ACC-002", "Gold Structured Clutch", "Accessory", "Hidesign", 4500, "Gold", "#D4AF37", "Leather", "cocktail,date_night,reception", "Modern", "female", "all", "light"),
    ("SKU-W-ACC-003", "Dupatta — Cobalt Blue Georgette", "Accessory", "FabIndia", 1800, "Cobalt Blue", "#0047AB", "Georgette", "festival,casual,eid", "Ethnic", "female", "all", "light"),
    ("SKU-W-ACC-004", "Silk Stole — Teal with Zari Border", "Accessory", "Good Earth", 4200, "Teal", "#008080", "Silk", "corporate,diwali,date_night", "Modern", "female", "all", "light"),

    # ─── WOMEN'S FOOTWEAR ───
    ("SKU-W-FTW-001", "Gold Kolhapuri Chappals", "Footwear", "Kolhapuri House", 2200, "Gold", "#D4AF37", "Leather", "festival,casual,haldi", "Ethnic", "female", "pune,mumbai,all", "light"),
    ("SKU-W-FTW-002", "Embroidered Juttis — Magenta", "Footwear", "Needledust", 3800, "Magenta", "#FF00FF", "Silk", "wedding,sangeet,mehendi", "Ethnic", "female", "all", "light"),
    ("SKU-W-FTW-003", "Nude Block Heels", "Footwear", "Charles & Keith", 4500, "Nude", "#E8CCBF", "Leather", "cocktail,date_night,corporate,reception", "Modern", "female", "all", "light"),
    ("SKU-W-FTW-004", "Black Stiletto Sandals", "Footwear", "Jimmy Choo", 12000, "Black", "#000000", "Leather", "cocktail,date_night,reception", "Modern", "female", "all", "light"),

    # ─── MEN'S SHERWANIS / KURTAS ───
    ("SKU-M-SHR-001", "Ivory Silk Sherwani — Gold Embroidery", "Top", "Manyavar", 18000, "Ivory", "#FFFFF0", "Raw Silk", "wedding,reception", "Structured", "male", "all", "heavy"),
    ("SKU-M-SHR-002", "Emerald Velvet Sherwani", "Top", "Sabyasachi", 45000, "Emerald Green", "#046307", "Velvet", "wedding,sangeet,reception", "Structured", "male", "all", "heavy"),
    ("SKU-M-SHR-003", "Navy Bandhgala Suit", "Top", "Raymond", 12000, "Navy Blue", "#000080", "Wool Blend", "corporate,reception,date_night", "Structured", "male", "all", "medium"),
    ("SKU-M-SHR-004", "Maroon Nehru Jacket", "Layer", "FabIndia", 4500, "Maroon", "#800000", "Silk", "diwali,sangeet,corporate,festival", "Structured", "male", "all", "medium"),
    ("SKU-M-KUR-001", "White Lucknowi Chikan Kurta", "Top", "FabIndia", 3500, "White", "#FFFFFF", "Cotton", "eid,puja,festival,casual", "Straight", "male", "lucknow,delhi,all", "light"),
    ("SKU-M-KUR-002", "Mustard Silk Kurta — Gota Patti", "Top", "Manyavar", 5500, "Mustard Yellow", "#E1A95F", "Silk", "haldi,mehendi,diwali,navratri", "Straight", "male", "jaipur,all", "medium"),
    ("SKU-M-KUR-003", "Black Silk Kurta — Minimalist", "Top", "Raw Mango", 6800, "Black", "#000000", "Silk", "diwali,cocktail,reception,date_night", "Straight", "male", "all", "medium"),
    ("SKU-M-KUR-004", "Cobalt Blue Linen Kurta", "Top", "FabIndia", 3200, "Cobalt Blue", "#0047AB", "Linen", "festival,casual,eid,haldi", "Straight", "male", "all", "light"),
    ("SKU-M-KUR-005", "Coral Short Kurta", "Top", "Biba Men", 2800, "Coral", "#FF7F50", "Cotton", "mehendi,haldi,casual", "Short", "male", "all", "light"),
    ("SKU-M-KUR-006", "Bottle Green Velvet Sherwani", "Top", "Manyavar", 22000, "Bottle Green", "#006A4E", "Velvet", "wedding,reception,sangeet", "Structured", "male", "all", "heavy"),

    # ─── MEN'S BOTTOMS ───
    ("SKU-M-BOT-001", "Ivory Churidar", "Bottom", "Manyavar", 2200, "Ivory", "#FFFFF0", "Cotton Silk", "wedding,festival,eid", "Slim Fit", "male", "all", "light"),
    ("SKU-M-BOT-002", "Black Slim-Fit Trousers", "Bottom", "Raymond", 3500, "Black", "#000000", "Wool Blend", "corporate,reception,date_night", "Slim Fit", "male", "all", "light"),
    ("SKU-M-BOT-003", "Beige Linen Pants", "Bottom", "FabIndia", 2800, "Beige", "#F5F5DC", "Linen", "casual,haldi,vacation", "Straight", "male", "all", "light"),
    ("SKU-M-BOT-004", "White Dhoti Pants", "Bottom", "FabIndia", 2500, "White", "#FFFFFF", "Cotton", "puja,wedding,festival", "Draped", "male", "chennai,all", "light"),
    ("SKU-M-BOT-005", "Navy Formal Trousers", "Bottom", "Van Heusen", 3200, "Navy Blue", "#000080", "Cotton Blend", "corporate,date_night", "Straight", "male", "all", "light"),
    ("SKU-M-BOT-006", "Neutral Grey Chinos", "Bottom", "Levi's", 2800, "Neutral Grey", "#808080", "Cotton", "casual,corporate,date_night", "Slim Fit", "male", "all", "light"),

    # ─── MEN'S FOOTWEAR ───
    ("SKU-M-FTW-001", "Tan Mojris — Embroidered", "Footwear", "Needledust", 3200, "Tan", "#D2B48C", "Leather", "wedding,sangeet,diwali", "Ethnic", "male", "all", "light"),
    ("SKU-M-FTW-002", "Black Leather Loafers", "Footwear", "Cole Haan", 8500, "Black", "#000000", "Leather", "corporate,reception,date_night", "Modern", "male", "all", "light"),
    ("SKU-M-FTW-003", "Brown Brogue Oxfords", "Footwear", "Clarks", 7500, "Brown", "#8B4513", "Leather", "corporate,reception,date_night", "Modern", "male", "all", "light"),
    ("SKU-M-FTW-004", "Gold Juttis — Mirror Work", "Footwear", "Fizzy Goblet", 4500, "Gold", "#D4AF37", "Silk & Leather", "wedding,sangeet", "Ethnic", "male", "all", "light"),
    ("SKU-M-FTW-005", "Navy Suede Loafers", "Footwear", "Aldo", 6500, "Navy Blue", "#000080", "Suede", "cocktail,date_night,corporate", "Modern", "male", "all", "light"),

    # ─── MEN'S ACCESSORIES ───
    ("SKU-M-ACC-001", "Gold Brooch — Maharaja Style", "Accessory", "Tanishq", 8500, "Gold", "#D4AF37", "Gold", "wedding,reception", "Ethnic", "male", "all", "light"),
    ("SKU-M-ACC-002", "Silk Pocket Square — Paisley Maroon", "Accessory", "The Tie Hub", 1200, "Maroon", "#800000", "Silk", "corporate,reception,date_night,cocktail", "Modern", "male", "all", "light"),
    ("SKU-M-ACC-003", "Printed Safa — Red & Gold", "Accessory", "Manyavar", 3500, "Red", "#D2042D", "Cotton Silk", "wedding", "Ethnic", "male", "jaipur,all", "light"),
    ("SKU-M-ACC-004", "Leather Belt — Black", "Accessory", "Tommy Hilfiger", 3200, "Black", "#000000", "Leather", "corporate,date_night,casual", "Modern", "male", "all", "light"),
    ("SKU-M-ACC-005", "Premium Watch — Rose Gold", "Accessory", "Titan", 12000, "Rose Gold", "#B76E79", "Metal", "corporate,date_night,reception,cocktail", "Modern", "male", "all", "light"),
    ("SKU-M-ACC-006", "Stole — Pashmina Beige", "Accessory", "FabIndia", 4500, "Beige", "#F5F5DC", "Pashmina", "wedding,reception,diwali", "Ethnic", "male", "all", "light"),

    # ─── MEN'S SHIRTS FOR FUSION ───
    ("SKU-M-SHI-001", "Cobalt Blue Silk Shirt", "Top", "Zara", 4500, "Cobalt Blue", "#0047AB", "Silk", "cocktail,date_night,sangeet", "Slim Fit", "male", "all", "light"),
    ("SKU-M-SHI-002", "White Crisp Formal Shirt", "Top", "Van Heusen", 2500, "White", "#FFFFFF", "Cotton", "corporate,reception,date_night", "Classic", "male", "all", "light"),
    ("SKU-M-SHI-003", "Peach Linen Shirt", "Top", "Linen Club", 3200, "Peach", "#FFDAB9", "Linen", "vacation,haldi,casual,mehendi", "Relaxed", "male", "all", "light"),
    ("SKU-M-SHI-004", "Black Mandarin Collar Shirt", "Top", "Jack & Jones", 3800, "Black", "#000000", "Cotton", "cocktail,date_night,reception", "Mandarin", "male", "all", "light"),

    # ─── UNISEX / LAYERS ───
    ("SKU-U-LAY-001", "Pashmina Shawl — Deep Wine", "Layer", "Kashmir Loom", 8500, "Deep Wine", "#722F37", "Pashmina", "wedding,reception,diwali", "Draped", "unisex", "delhi,kashmir,all", "light"),
    ("SKU-U-LAY-002", "Khadi Jacket — Olive Green", "Layer", "Khadi Gram Udyog", 3200, "Olive Green", "#556B2F", "Khadi", "casual,corporate,festival", "Straight", "unisex", "all", "medium"),
    ("SKU-U-LAY-003", "Silk Dupatta — Magenta & Gold", "Layer", "FabIndia", 2800, "Magenta", "#FF00FF", "Silk", "festival,wedding,sangeet", "Draped", "female", "all", "light"),
    ("SKU-U-LAY-004", "Linen Nehru Vest — Beige", "Layer", "FabIndia", 3500, "Beige", "#F5F5DC", "Linen", "corporate,casual,festival", "Structured", "male", "all", "light"),

    # ─── ADDITIONAL WOMEN'S TOPS ───
    ("SKU-W-TOP-001", "Cobalt Blue Silk Blouse — Zari", "Top", "Raw Mango", 5500, "Cobalt Blue", "#0047AB", "Silk", "wedding,sangeet,reception,diwali", "Structured", "female", "all", "medium"),
    ("SKU-W-TOP-002", "Peach Crop Top — Sequins", "Top", "Indya", 2800, "Peach", "#FFDAB9", "Georgette", "sangeet,cocktail,mehendi", "Crop", "female", "all", "light"),
    ("SKU-W-TOP-003", "Neutral Grey Silk Top", "Top", "AND", 3500, "Neutral Grey", "#808080", "Silk", "corporate,date_night,casual", "Straight", "female", "all", "light"),
    ("SKU-W-TOP-004", "Black Bandhgala Jacket — Women's", "Layer", "Raymond", 8500, "Black", "#000000", "Wool Blend", "corporate,reception,cocktail", "Structured", "female", "all", "medium"),

    # ─── ADDITIONAL FESTIVAL / DIWALI SPECIFIC ───
    ("SKU-W-SAR-011", "Electric Indigo Banarasi Saree", "Full", "Ekaya Banaras", 19500, "Electric Indigo", "#6F00FF", "Banarasi Silk", "diwali,eid,wedding,reception", "Draped", "female", "all", "heavy"),
    ("SKU-M-KUR-007", "Deep Teal Jacquard Kurta", "Top", "Manyavar", 4800, "Teal", "#008080", "Jacquard", "diwali,eid,festival", "Straight", "male", "all", "medium"),
    ("SKU-W-KUR-006", "Lavender Chikankari Kurta Set", "Top", "FabIndia", 4200, "Lavender", "#B57EDC", "Cotton", "festival,casual,puja", "A-Line", "female", "lucknow,all", "light"),

    # ─── VACATION / CASUAL ───
    ("SKU-W-DRS-001", "White Linen Maxi Dress", "Full", "Zara", 5500, "White", "#FFFFFF", "Linen", "vacation,casual,brunch", "A-Line", "female", "goa,maldives,all", "light"),
    ("SKU-M-SHI-005", "Tropical Print Resort Shirt", "Top", "H&M", 2200, "Teal", "#008080", "Rayon", "vacation,casual", "Relaxed", "male", "goa,maldives,all", "light"),
    ("SKU-W-DRS-002", "Indigo Block Print Kaftan", "Full", "Good Earth", 6800, "Indigo", "#3F00FF", "Cotton", "vacation,casual,brunch", "Relaxed", "female", "all", "light"),

    # ─── PREMIUM DATE NIGHT ───
    ("SKU-W-SAR-012", "Black Sequin Pre-Draped Saree", "Full", "Ridhi Mehra", 24000, "Black", "#000000", "Sequin Georgette", "date_night,cocktail,reception", "Pre-Draped", "female", "mumbai,delhi,all", "medium"),
    ("SKU-M-BLZ-001", "Charcoal Slim-Fit Blazer", "Layer", "Zara", 8500, "Charcoal", "#36454F", "Wool Blend", "date_night,cocktail,corporate,reception", "Slim Fit", "male", "all", "medium"),

    # ─── HIGH-END WEDDING ADDITIONS ───
    ("SKU-W-JEW-009", "Jadau Rani Haar — Bridal", "Jewelry", "Tribhovandas Bhimji Zaveri", 85000, "Gold", "#D4AF37", "Gold & Precious Stones", "wedding", "Traditional", "female", "all", "heavy"),
    ("SKU-W-FTW-005", "Embroidered Wedge Heels — Gold", "Footwear", "Fizzy Goblet", 5500, "Gold", "#D4AF37", "Silk", "wedding,sangeet,reception", "Ethnic", "female", "all", "light"),
    ("SKU-M-ACC-007", "Diamond Brooch — Solitaire", "Accessory", "Tanishq", 25000, "Diamond", "#B9F2FF", "Platinum & Diamond", "wedding,reception", "Modern", "male", "all", "light"),
]


# ═══════════════════════════════════════════════════════════════
#  PRODUCT URL MAPPING — Live links to shopping sites
# ═══════════════════════════════════════════════════════════════

def get_live_product_url(brand: str, name: str) -> str:
    """Generates a dynamic Google Shopping aggregator link for the specific item."""
    query = f"{brand} {name}".strip()
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?tbm=shop&q={encoded}"


# Realistic Unsplash Image placeholders for different categories (using standard Unsplash Source or direct image IDs with sizing)
CATEGORY_IMAGES = {
    "Saree": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&q=80&fit=crop",
    "Lehenga": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&q=80&fit=crop",
    "Kurta_female": "https://images.unsplash.com/photo-1605763240000-7e93b172d754?w=400&q=80&fit=crop",
    "Kurta_male": "https://images.unsplash.com/photo-1596484552834-6a58f850d0a1?w=400&q=80&fit=crop",
    "Top_female": "https://images.unsplash.com/photo-1515347619152-ed249219b16e?w=400&q=80&fit=crop",
    "Top_male": "https://images.unsplash.com/photo-1594938298596-70f56f0c2e15?w=400&q=80&fit=crop",
    "Bottom_female": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&q=80&fit=crop",
    "Bottom_male": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400&q=80&fit=crop",
    "Jewelry": "https://images.unsplash.com/photo-1599643478524-fb5244585141?w=400&q=80&fit=crop",
    "Accessory": "https://images.unsplash.com/photo-1584916201218-f4242ceb4809?w=400&q=80&fit=crop",
    "Footwear": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&q=80&fit=crop",
    "Default": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&q=80&fit=crop"
}


def get_image_url_for_item(item_name: str, category: str, gender: str) -> str:
    """Assigns an appropriate image from the CATEGORY_IMAGES dict based on the item details."""
    name_low = item_name.lower()
    if "saree" in name_low:
        return CATEGORY_IMAGES["Saree"]
    if "lehenga" in name_low:
        return CATEGORY_IMAGES["Lehenga"]
    if "kurta" in name_low or "anarkali" in name_low:
        return CATEGORY_IMAGES.get(f"Kurta_{gender}", CATEGORY_IMAGES["Default"])
    if category == "Top" or category == "Full":
        return CATEGORY_IMAGES.get(f"Top_{gender}", CATEGORY_IMAGES["Default"])
    if category == "Bottom":
        return CATEGORY_IMAGES.get(f"Bottom_{gender}", CATEGORY_IMAGES["Default"])
    if category == "Jewelry":
        return CATEGORY_IMAGES["Jewelry"]
    if category == "Accessory":
        return CATEGORY_IMAGES["Accessory"]
    if category == "Footwear":
        return CATEGORY_IMAGES["Footwear"]
    return CATEGORY_IMAGES["Default"]


def seed_inventory(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM current_inventory")
    for item in INVENTORY_DATA:
        sku = item[0]
        name = item[1]
        category = item[2]
        brand = item[3]
        gender = item[10]
        
        product_url = get_live_product_url(brand, name)
        image_url = get_image_url_for_item(name, category, gender)
        
        cursor.execute("""
            INSERT INTO current_inventory
            (sku, name, category, brand, price, color_family, color_hex, fabric,
             occasion_tags, silhouette, gender, region_suitability, stock_status, weight_category, product_url, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_stock', ?, ?, ?)
        """, item + (product_url, image_url))
    conn.commit()
    print(f"  ✓ Seeded {len(INVENTORY_DATA)} inventory items (with product links and images)")


def create_user(
    name: str,
    preferred_colors: list[str],
    preferred_fabrics: list[str],
    size: str,
    skin_tone: str,
    budget_range: str,
    style_dna: str = "",
) -> int:
    """
    Create a new user profile dynamically.
    Returns the user_id of the created user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    colors_str = ",".join(preferred_colors) if preferred_colors else ""
    fabrics_str = ",".join(preferred_fabrics) if preferred_fabrics else ""

    cursor.execute("""
        INSERT INTO user_preferences (name, preferred_colors, preferred_fabrics,
        size, skin_tone, budget_range, saved_style_dna)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, colors_str, fabrics_str, size, skin_tone, budget_range, style_dna))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_all_users() -> list[dict]:
    """Fetch all user profiles from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, skin_tone, size, saved_style_dna FROM user_preferences ORDER BY user_id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int) -> dict:
    """Fetch a single user profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def initialize_database():
    """Create tables and seed inventory only. Users are created dynamically."""
    print("═" * 50)
    print("  Style Engine — Database Initialization")
    print("═" * 50)
    conn = get_connection()
    create_tables(conn)
    print("  ✓ Tables created")
    seed_inventory(conn)
    conn.close()
    print("═" * 50)
    print(f"  Database ready at: {DB_PATH}")
    print("═" * 50)


if __name__ == "__main__":
    initialize_database()


