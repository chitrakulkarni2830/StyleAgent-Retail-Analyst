"""
=============================================================
database/sql_queries.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This file contains 10 expert SQL queries written as Python
  functions. Each function connects to inventory.db, runs a
  query, and returns the results as a list of dictionaries.

  These queries are used for data analysis and Tableau exports.
  You can also run individual functions from the Python shell
  to explore the database.

HOW TO USE:
  from database.sql_queries import top_purchased_colours
  results = top_purchased_colours()
  for row in results:
      print(row)
=============================================================
"""

import sqlite3  # built-in Python library for database queries
import os       # built-in: for building file paths

# ── Path to the SQLite database file ──────────────────────────
THIS_FOLDER  = os.path.dirname(os.path.abspath(__file__))
DB_PATH      = os.path.join(THIS_FOLDER, "inventory.db")


def _get_connection():
    """
    Opens a connection to inventory.db and enables dictionary-style
    row access so you can use row['column_name'] instead of row[0].
    Returns the connection object.
    """
    conn = sqlite3.connect(DB_PATH)      # open (or create) the database file
    conn.row_factory = sqlite3.Row       # allows row["column_name"] access
    return conn


def _run_query(sql_query, params=()):
    """
    Helper function that every query below uses.
    Opens the DB, runs the SQL, returns results as a list of dicts,
    then closes the connection cleanly.

    sql_query: the SQL string to run
    params:    tuple of values to substitute into '?' placeholders
    Returns:   list of dictionaries (one dict per row)
    """
    conn  = _get_connection()            # open connection
    cursor = conn.cursor()               # create cursor ("pen" for the database)
    cursor.execute(sql_query, params)    # run the SQL
    rows  = cursor.fetchall()            # get all matching rows
    conn.close()                         # always close when done!
    return [dict(row) for row in rows]   # convert each Row object to a plain dict


# =============================================================
# QUERY 1: Top 5 Most Purchased Colours
# =============================================================
def top_purchased_colours():
    """
    QUERY 1: Which colours do customers buy the most?
    Groups all purchase_history rows by colour and counts purchases.
    Returns the top 5 most popular colours.

    Useful for: inventory planning, trend validation
    """
    sql = """
        SELECT
            colour,                         -- the item colour
            COUNT(*) AS purchase_count,     -- how many times this colour was bought
            ROUND(AVG(price), 0) AS avg_price  -- average price of this colour's items
        FROM purchase_history
        GROUP BY colour                     -- group rows with the same colour together
        ORDER BY purchase_count DESC        -- most purchased first
        LIMIT 5                             -- only the top 5
    """
    return _run_query(sql)


# =============================================================
# QUERY 2: Average Order Value by Vibe
# =============================================================
def average_spend_by_vibe():
    """
    QUERY 2: How much do customers spend on average for each vibe?
    (Ethnic, Modern, Boho, etc.)

    Useful for: understanding which customer segments spend more,
                pricing new inventory items correctly
    """
    sql = """
        SELECT
            vibe,                                    -- the fashion vibe category
            COUNT(*) AS total_purchases,             -- how many purchases in this vibe
            ROUND(AVG(price), 0) AS avg_spend,       -- average spend per transaction
            ROUND(MIN(price), 0) AS min_price,       -- cheapest item ever bought
            ROUND(MAX(price), 0) AS max_price        -- most expensive item ever bought
        FROM purchase_history
        GROUP BY vibe
        ORDER BY avg_spend DESC                      -- highest spending vibe first
    """
    return _run_query(sql)


# =============================================================
# QUERY 3: Most Popular Occasions by Purchase Count
# =============================================================
def most_popular_occasions():
    """
    QUERY 3: Which occasions do customers shop for the most?
    (wedding, office, festival, date_night, etc.)

    Useful for: seasonal promotions, occasion-specific campaigns
    """
    sql = """
        SELECT
            occasion,                       -- the occasion label
            COUNT(*) AS purchase_count,     -- how many times people shopped for this
            ROUND(AVG(price), 0) AS avg_spend   -- how much they spend per occasion
        FROM purchase_history
        GROUP BY occasion
        ORDER BY purchase_count DESC
        LIMIT 10                            -- show top 10 occasions
    """
    return _run_query(sql)


# =============================================================
# QUERY 4: Inventory Count by Vibe
# =============================================================
def inventory_by_vibe_count():
    """
    QUERY 4: How many clothing items do we have in stock for each vibe?
    Also shows the price range per vibe.

    Useful for: identifying gaps (e.g. not enough Streetwear items),
                planning what to add to the inventory
    """
    sql = """
        SELECT
            vibe,                              -- the vibe category
            COUNT(*) AS item_count,            -- how many items in this vibe
            SUM(stock_count) AS total_units,   -- total stock units available
            ROUND(MIN(price), 0) AS min_price, -- cheapest item in this vibe
            ROUND(MAX(price), 0) AS max_price  -- most expensive item in this vibe
        FROM current_inventory
        GROUP BY vibe
        ORDER BY item_count DESC
    """
    return _run_query(sql)


# =============================================================
# QUERY 5: Price Distribution by Category
# =============================================================
def budget_range_distribution():
    """
    QUERY 5: What is the price spread for each clothing category?
    (Tops, Bottoms, Dresses, Bags, Footwear, etc.)

    Useful for: helping customers set realistic budgets,
                understanding where the value sits in the catalogue
    """
    sql = """
        SELECT
            category,                           -- e.g. Top, Bottom, Dress, Bag
            COUNT(*) AS item_count,
            ROUND(MIN(price), 0) AS cheapest,   -- lowest priced item in this category
            ROUND(MAX(price), 0) AS most_expensive,
            ROUND(AVG(price), 0) AS average_price,
            -- CASE calculates which "budget tier" most items fall into
            CASE
                WHEN AVG(price) < 3000 THEN 'Budget'
                WHEN AVG(price) < 8000 THEN 'Mid-range'
                ELSE 'Designer'
            END AS typical_tier
        FROM current_inventory
        GROUP BY category
        ORDER BY average_price DESC
    """
    return _run_query(sql)


# =============================================================
# QUERY 6: Top-Rated Purchased Items
# =============================================================
def top_rated_purchases():
    """
    QUERY 6: Which items got the highest ratings from customers after purchase?
    Shows items rated 5 stars, sorted by how many times they were bought.

    Useful for: "bestseller" badges, recommendation engine seeds
    """
    sql = """
        SELECT
            item_name,
            category,
            colour,
            ROUND(AVG(rating_given), 1) AS avg_rating,  -- average star rating
            COUNT(*) AS times_purchased,                 -- how often it was bought
            ROUND(AVG(price), 0) AS price
        FROM purchase_history
        WHERE rating_given >= 4                          -- only well-rated items
        GROUP BY item_name, category, colour
        HAVING times_purchased >= 1                      -- at least bought once
        ORDER BY avg_rating DESC, times_purchased DESC
        LIMIT 10
    """
    return _run_query(sql)


# =============================================================
# QUERY 7: Colours Wishlisted But Never Purchased
# =============================================================
def wishlist_vs_bought_colours():
    """
    QUERY 7: Which colours do customers BROWSE and SAVE but never actually BUY?
    This gap reveals items that are attractive but too expensive, or out of stock.

    Useful for: pricing analysis, understanding the "aspiration vs. reality" gap
    """
    sql = """
        SELECT
            b.colour AS wishlisted_colour,          -- colour saved in wishlist
            COUNT(*) AS times_wishlisted,           -- how many times it was wishlisted
            -- LEFT JOIN: we match wishlist colours to purchases
            -- If the WHERE clause filters out matching purchases, it means they never bought it
            CASE
                WHEN p.colour IS NULL THEN 'Never Purchased'
                ELSE 'Also Purchased'
            END AS purchase_status
        FROM browsing_logs b
        LEFT JOIN purchase_history p
            ON lower(b.colour) = lower(p.colour)    -- match by colour name (case-insensitive)
            AND b.user_id = p.user_id               -- only compare the same user's data
        WHERE b.saved_to_wishlist = 1               -- only items they saved to wishlist
        GROUP BY b.colour, purchase_status
        ORDER BY times_wishlisted DESC
    """
    return _run_query(sql)


# =============================================================
# QUERY 8: Jewellery Count by Skin Undertone Suitability
# =============================================================
def jewellery_by_skin_undertone():
    """
    QUERY 8: How many jewellery pieces do we have for each skin undertone?
    (warm, cool, neutral, all)

    Useful for: making sure we have enough jewellery for every skin tone,
                identifying gaps in our jewellery catalogue
    """
    sql = """
        SELECT
            skin_undertone_fit AS suitable_for,    -- warm / cool / neutral / all
            jewellery_type,                        -- Earrings / Necklace / Bangles etc.
            COUNT(*) AS piece_count,               -- how many pieces of this type
            ROUND(MIN(price), 0) AS min_price,
            ROUND(MAX(price), 0) AS max_price,
            ROUND(AVG(price), 0) AS avg_price
        FROM jewellery_inventory
        GROUP BY skin_undertone_fit, jewellery_type
        ORDER BY suitable_for, jewellery_type
    """
    return _run_query(sql)


# =============================================================
# QUERY 9: Outfit History — Most Common Occasions
# =============================================================
def outfit_history_by_occasion():
    """
    QUERY 9: Which occasions have been used most when generating outfits?
    Reads from the outfit_history table (filled when users click 'Save This Look').

    Useful for: understanding what occasions users care about most
    """
    sql = """
        SELECT
            occasion,
            COUNT(*) AS times_generated,          -- how many times outfits were created for this
            SUM(CASE WHEN saved = 1 THEN 1 ELSE 0 END) AS times_saved,  -- how many were saved
            ROUND(AVG(user_rating), 1) AS avg_rating  -- average user satisfaction
        FROM outfit_history
        GROUP BY occasion
        ORDER BY times_generated DESC
        LIMIT 10
    """
    # If outfit_history is empty (no outfits saved yet), return a friendly message
    results = _run_query(sql)
    if not results:
        return [{"message": "No outfits have been saved yet. Generate and save an outfit to see this data."}]
    return results


# =============================================================
# QUERY 10: Low Stock Alert
# =============================================================
def low_stock_alert():
    """
    QUERY 10: Which inventory items are running low on stock?
    Shows items where stock_count is below 5 units.

    Useful for: restocking decisions, removing sold-out items from recommendations
    """
    sql = """
        SELECT
            item_id,
            item_name,
            category,
            colour,
            vibe,
            price,
            stock_count,                         -- how many units remain
            -- Visual urgency label based on stock level
            CASE
                WHEN stock_count = 0 THEN '🔴 OUT OF STOCK'
                WHEN stock_count <= 2 THEN '🟠 CRITICAL — Restock NOW'
                WHEN stock_count <= 5 THEN '🟡 LOW — Restock Soon'
                ELSE '🟢 OK'
            END AS stock_status
        FROM current_inventory
        WHERE stock_count < 5                    -- only items needing attention
        ORDER BY stock_count ASC                 -- most urgent (lowest stock) first
    """
    return _run_query(sql)


# =============================================================
# MAIN — run all 10 queries and print results
# =============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Style Agent — SQL Analytics Report")
    print("=" * 60)

    # Dictionary of all 10 query functions with display labels
    queries = {
        "Q1: Top Purchased Colours":       top_purchased_colours,
        "Q2: Average Spend by Vibe":        average_spend_by_vibe,
        "Q3: Popular Occasions":            most_popular_occasions,
        "Q4: Inventory Count by Vibe":      inventory_by_vibe_count,
        "Q5: Price Distribution by Cat.":   budget_range_distribution,
        "Q6: Top-Rated Purchases":          top_rated_purchases,
        "Q7: Wishlisted But Not Bought":    wishlist_vs_bought_colours,
        "Q8: Jewellery by Undertone":       jewellery_by_skin_undertone,
        "Q9: Outfit History Occasions":     outfit_history_by_occasion,
        "Q10: Low Stock Alert":             low_stock_alert,
    }

    for label, query_func in queries.items():
        print(f"\n{'─' * 60}")
        print(f"  {label}")
        print("─" * 60)
        try:
            rows = query_func()   # run the query
            if not rows:
                print("  (no results)")
            for row in rows[:5]:  # show at most 5 rows per query
                print(f"  {dict(row)}")
        except Exception as e:
            print(f"  ⚠️  Query failed: {e}")

    print("\n" + "=" * 60)
    print("  ✅ All 10 SQL queries complete.\n")
