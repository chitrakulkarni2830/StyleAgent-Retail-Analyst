-- ============================================================
-- SQL Templates for the Multi-Agent Style Orchestrator
-- Database: style_engine.db (SQLite)
-- ============================================================
-- 1. Style DNA Calculation: Dominant colors from purchase history
SELECT color,
    COUNT(*) as purchase_count,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM purchase_history
            WHERE user_id = :user_id
        ),
        1
    ) as pct
FROM purchase_history
WHERE user_id = :user_id
GROUP BY color
ORDER BY purchase_count DESC;
-- 2. Style DNA Calculation: Preferred silhouettes
SELECT style_tag,
    COUNT(*) as count,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM purchase_history
            WHERE user_id = :user_id
        ),
        1
    ) as pct
FROM purchase_history
WHERE user_id = :user_id
GROUP BY style_tag
ORDER BY count DESC;
-- 3. Style DNA Calculation: Fabric affinity from browsing + purchases
SELECT ci.fabric,
    SUM(bl.view_count) as total_views,
    COUNT(DISTINCT ph.sku) as purchases
FROM browsing_logs bl
    JOIN current_inventory ci ON bl.sku = ci.sku
    LEFT JOIN purchase_history ph ON bl.sku = ph.sku
    AND ph.user_id = bl.user_id
WHERE bl.user_id = :user_id
GROUP BY ci.fabric
ORDER BY total_views DESC;
-- 4. Inventory Filter: By occasion + trending colors + gender + budget
SELECT *
FROM current_inventory
WHERE occasion_tags LIKE '%' || :occasion || '%'
    AND gender IN (:gender, 'unisex')
    AND price <= :max_budget
    AND stock_status = 'in_stock'
    AND (
        color_family IN (:color1, :color2, :color3)
        OR color_family IN ('Neutral Grey', 'Black', 'White', 'Beige')
    )
ORDER BY price ASC;
-- 5. Inventory Filter: By style_dna silhouette + fabric
SELECT *
FROM current_inventory
WHERE silhouette IN (:silhouette1, :silhouette2)
    AND fabric IN (:fabric1, :fabric2, :fabric3)
    AND gender IN (:gender, 'unisex')
    AND stock_status = 'in_stock'
ORDER BY price ASC;
-- 6. Bridge Logic: Find neutral bases user already likes
SELECT ci.*
FROM current_inventory ci
    JOIN purchase_history ph ON ci.color_family = ph.color
WHERE ph.user_id = :user_id
    AND ci.color_family IN (
        'Neutral Grey',
        'Black',
        'White',
        'Beige',
        'Navy',
        'Ivory'
    )
    AND ci.occasion_tags LIKE '%' || :occasion || '%'
    AND ci.gender IN (:gender, 'unisex')
    AND ci.stock_status = 'in_stock';
-- 7. Accent Piece Query: Trending color items for accent
SELECT *
FROM current_inventory
WHERE color_family = :trending_color
    AND category IN ('Accessory', 'Jewelry', 'Layer')
    AND gender IN (:gender, 'unisex')
    AND price <= :accent_budget
    AND stock_status = 'in_stock';
-- 8. User Preference Lookup
SELECT *
FROM user_preferences
WHERE user_id = :user_id;
-- 9. Full Ensemble Query: All categories for an occasion
SELECT category,
    COUNT(*) as available_count
FROM current_inventory
WHERE occasion_tags LIKE '%' || :occasion || '%'
    AND gender IN (:gender, 'unisex')
    AND stock_status = 'in_stock'
GROUP BY category;
-- 10. Trend Alignment Score: How many trending items are in stock
SELECT COUNT(*) as matching_items
FROM current_inventory
WHERE color_family IN (:trend_color1, :trend_color2, :trend_color3)
    AND fabric IN (:trend_fabric1, :trend_fabric2)
    AND stock_status = 'in_stock';