"""
wardrobe_architect_agent.py — Agent C: The 'Synthesizer'
Receives trend_brief + style_dna, queries inventory, applies bridge logic,
curates a complete ensemble with justification, and formats output.
"""

from __future__ import annotations
import sqlite3
import os
from typing import Optional

from state_schema import StyleState, OutfitItem, FinalRecommendation
from color_engine import (
    get_palette_strategy, get_complementary_colors, get_jewelry_metal,
    suggest_accent_color, validate_rule_of_three, get_color_hex, get_stylists_tip,
)
from indian_fashion_kb import (
    get_occasion_guidance, get_skin_tone_metals, get_style_dna_info,
)
from ollama_client import get_client


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "style_engine.db")


class WardrobeArchitectAgent:
    """
    The Wardrobe Architect synthesizes trends + user identity into a curated outfit:
    1. Queries inventory filtered by style_dna AND trending_colors
    2. Applies the 'Bridge Logic' for trending colors outside user comfort zone
    3. Enforces the Rule of Three (max 3 colors)
    4. Curates a full ensemble: Main Piece, Bottom/Layer, Jewelry, Footwear, Accessory
    5. Generates "The Why" justification
    6. Calculates trend_alignment_score and availability
    """

    def __init__(self):
        self.db_path = DB_PATH
        self.ollama = get_client()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def curate(self, state: StyleState) -> StyleState:
        """
        Execute the Wardrobe Architect pipeline.
        Produces a complete curated outfit in state.final_recommendation.
        """
        state.current_step = "wardrobe_architect"
        print("\n👗 WARDROBE ARCHITECT — Curating your look...")
        print("─" * 50)

        conn = self._get_conn()
        trend_brief = state.trend_brief
        profile = state.user_style_profile

        occasion = state.occasion or "date_night"
        sub_occasion = state.sub_occasion
        gender = state.gender or "female"
        budget = state.budget or 50000
        region = state.region
        color_mood = getattr(state, "color_mood", "Any")
        vibe_pref = getattr(state, "preferred_vibe", "Any")

        # Step 1: Get occasion guidance
        guidance = get_occasion_guidance(occasion, sub_occasion, region, gender)
        print(f"  📖 Occasion: {guidance.get('display_name', occasion)} | Vibe: {vibe_pref}")
        if guidance.get("regional_note"):
            print(f"  🌍 Regional: {guidance['regional_note']}")

        # Step 2: Determine palette strategy
        palette_strategy = get_palette_strategy(occasion, guidance.get("vibe", ""))
        print(f"  🎨 Palette Strategy: {palette_strategy.upper()}")

        # Step 3: Identify target colors (trend + user intersection)
        trending_colors = trend_brief.trending_colors if trend_brief else guidance.get("colors", [])[:3]
        user_colors = profile.dominant_colors if profile else []
        skin_tone = profile.skin_tone if profile else "neutral"
        style_dna = profile.style_dna if profile else "Fusion Explorer"

        overlap_colors = [c for c in trending_colors if c in user_colors]
        accent_colors = [c for c in trending_colors if c not in user_colors]
        user_neutrals = [c for c in user_colors if c in (
            "Black", "White", "Ivory", "Beige", "Neutral Grey", "Navy Blue", "Charcoal"
        )]

        print(f"  🔍 Querying inventory...")
        outfit_items = []
        primary_colors = []
        vibe_hits = 0
        total_items = 0

        # Step 4: Base Layer (Top/Full + Bottom)
        main_piece, matched_vibe = self._find_main_piece(conn, occasion, gender, budget, trending_colors, user_colors, guidance, state.rejected_skus, state.preferred_clothing_type, vibe_pref)
        remaining = budget - (main_piece["price"] if main_piece else 0)
        
        if main_piece:
            total_items += 1
            if matched_vibe: vibe_hits += 1
            item = self._row_to_outfit_item(main_piece, "The Base — Main Piece")
            outfit_items.append(item)
            primary_colors.append(main_piece["color_family"])
            print(f"  ✅ Base: {main_piece['name']} ({main_piece['color_family']}, ₹{main_piece['price']:,.0f})")

        # Complementary Bottom if needed
        if main_piece and main_piece["category"] != "Full":
            target_category = "Top" if main_piece["category"] == "Bottom" else "Bottom"
            sec_colors = get_secondary_colors(main_piece["color_hex"], palette_strategy, color_mood)
            comp_piece, comp_matched_vibe = self._find_piece(conn, target_category, occasion, gender, remaining, sec_colors, state.rejected_skus, guidance, state.preferred_clothing_type, vibe_pref)
            if comp_piece:
                total_items += 1
                if comp_matched_vibe: vibe_hits += 1
                remaining -= comp_piece["price"]
                item = self._row_to_outfit_item(comp_piece, f"The Base — Complementary {target_category}")
                outfit_items.append(item)
                primary_colors.append(comp_piece["color_family"])
                print(f"  ✅ {target_category}: {comp_piece['name']} ({comp_piece['color_family']}, ₹{comp_piece['price']:,.0f})")

        # Step 5: The Layer (Blazer, Cape, Dupatta)
        # Attempt to find a layer if budget permits
        sec_colors = get_secondary_colors(primary_colors[0] if primary_colors else "#808080", palette_strategy, color_mood) if primary_colors else []
        layer_piece, layer_matched_vibe = self._find_layer(conn, occasion, gender, remaining, sec_colors, state.rejected_skus, vibe_pref)
        if layer_piece:
            total_items += 1
            if layer_matched_vibe: vibe_hits += 1
            remaining -= layer_piece["price"]
            item = self._row_to_outfit_item(layer_piece, "The Layer")
            outfit_items.append(item)
            primary_colors.append(layer_piece["color_family"])
            print(f"  ✅ Layer: {layer_piece['name']} ({layer_piece['color_family']}, ₹{layer_piece['price']:,.0f})")

        # Step 6: Jewelry
        jewelry_metal = get_jewelry_metal(skin_tone, occasion)
        jewelry, jew_matched_vibe = self._find_jewelry(conn, occasion, gender, jewelry_metal, remaining, state.rejected_skus, state.preferred_jewelry_type, vibe_pref)
        if jewelry:
            total_items += 1
            if jew_matched_vibe: vibe_hits += 1
            remaining -= jewelry["price"]
            item = self._row_to_outfit_item(jewelry, "The Accents — Jewelry")
            outfit_items.append(item)
            primary_colors.append(jewelry["color_family"])
            print(f"  ✅ Jewelry: {jewelry['name']} ({jewelry['color_family']}, ₹{jewelry['price']:,.0f})")

        # Step 7: Footwear
        footwear, ftw_matched_vibe = self._find_footwear(conn, occasion, gender, remaining, state.rejected_skus, guidance, vibe_pref)
        if footwear:
            total_items += 1
            if ftw_matched_vibe: vibe_hits += 1
            remaining -= footwear["price"]
            item = self._row_to_outfit_item(footwear, "The Finishing Touches — Footwear")
            outfit_items.append(item)
            print(f"  ✅ Footwear: {footwear['name']} ({footwear['color_family']}, ₹{footwear['price']:,.0f})")

        # Step 8: Accessory (Bag/Hero)
        accessory, acc_matched_vibe = self._find_accessory(conn, occasion, gender, remaining, accent_colors, state.rejected_skus, guidance, state.preferred_accessory_type, vibe_pref)
        if accessory:
            total_items += 1
            if acc_matched_vibe: vibe_hits += 1
            remaining -= accessory["price"]
            is_accent = accessory["color_family"] in accent_colors
            role = "The Accents — Hero Accessory" if is_accent else "The Accents — Accessory"
            item = self._row_to_outfit_item(accessory, role)
            outfit_items.append(item)
            if is_accent: primary_colors.append(accessory["color_family"])
            print(f"  ✅ Accessory: {accessory['name']} ({accessory['color_family']}, ₹{accessory['price']:,.0f})")

        # Wrap up stats
        color_validation = validate_rule_of_three(primary_colors)
        total_cost = sum(item.price for item in outfit_items)
        in_budget = total_cost <= budget
        availability = "available" if outfit_items else "out_of_stock"
        
        confidence_score = (vibe_hits / total_items * 100) if total_items > 0 else 0
        trend_score = self._calculate_trend_score(outfit_items, trending_colors, trend_brief)

        print(f"  💰 Total: ₹{total_cost:,.0f} / ₹{budget:,.0f} {'✅' if in_budget else '⚠️ Over budget'}")
        print(f"  🎯 Confidence Score: {confidence_score:.0f}% (Vibe Match)")
        print(f"  📊 Trend Alignment: {trend_score}/10")

        # LLM Justification
        items_for_llm = [
            {"name": i.name, "color": i.color, "fabric": i.fabric, "category": i.category}
            for i in outfit_items
        ]
        the_why = self.ollama.generate_justification(items_for_llm, occasion, style_dna, trending_colors, skin_tone)
        print(f"\n  📝 The Why: {the_why}")

        main_color = primary_colors[0] if primary_colors else "Cobalt Blue"
        stylist_tip = get_stylists_tip(main_color, palette_strategy, occasion)
        color_palette = [get_color_hex(c) for c in primary_colors[:3]]

        accent_info = {}
        if accent_colors and user_neutrals:
            accent_info = suggest_accent_color(user_neutrals[0], accent_colors[0])

        recommendation = FinalRecommendation(
            outfit_items=outfit_items,
            the_why=the_why,
            trend_alignment_score=trend_score,
            confidence_score=confidence_score,
            inventory_availability_status=availability,
            palette_strategy=palette_strategy,
            color_palette=color_palette,
            accessory_suite={
                "jewelry_metal": jewelry_metal,
                "stylist_tip": stylist_tip,
                "accent_bridge": accent_info.get("suggestion", ""),
            },
            occasion=occasion,
            sub_occasion=sub_occasion,
        )

        state.final_recommendation = recommendation
        state.inventory_match = [{"sku": i.sku, "name": i.name, "price": i.price} for i in outfit_items]
        state.current_step = "complete"

        conn.close()
        print("\n" + "─" * 50)
        return state

    # ─── INVENTORY QUERY METHODS ───

    def _execute_vibe_query(self, cursor, query_template, params, vibe_pref):
        """Helper to first attempt strict vibe match, then fallback to any vibe."""
        if vibe_pref != "Any":
            strict_query = query_template + " AND vibe = ?"
            strict_params = params + [vibe_pref]
            cursor.execute(strict_query + " ORDER BY price DESC LIMIT 5", strict_params)
            rows = cursor.fetchall()
            if rows: return rows, True

        cursor.execute(query_template + " ORDER BY price DESC LIMIT 5", params)
        return cursor.fetchall(), False

    def _find_main_piece(self, conn, occasion, gender, budget, trending_colors, user_colors, guidance, rejected, pref_clothing, vibe_pref):
        cursor = conn.cursor()
        color_placeholders = ",".join("?" * len(trending_colors)) if trending_colors else "''"
        
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category IN ('Top', 'Full', 'Bottom')
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND (? = 'Any' OR name LIKE ?)
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [f"%{occasion}%", gender, budget, pref_clothing, f"%{pref_clothing}%"] + list(rejected)
        
        # Try with trending colors
        if trending_colors:
            q_trend = base_query + f" AND color_family IN ({color_placeholders})"
            p_trend = params + trending_colors
            rows, matched_vibe = self._execute_vibe_query(cursor, q_trend, p_trend, vibe_pref)
            if rows: return dict(rows[0]), matched_vibe

        # Fallback to user colors
        if user_colors:
            q_user = base_query + f" AND color_family IN ({','.join('?' * len(user_colors))})"
            p_user = params + user_colors
            rows, matched_vibe = self._execute_vibe_query(cursor, q_user, p_user, vibe_pref)
            if rows: return dict(rows[0]), matched_vibe

        # Fallback to any color
        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    def _find_piece(self, conn, category, occasion, gender, budget, colors_hex, rejected, guidance, pref_clothing, vibe_pref):
        cursor = conn.cursor()
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category = ?
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND (? = 'Any' OR name LIKE ?)
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [category, f"%{occasion}%", gender, budget, pref_clothing, f"%{pref_clothing}%"] + list(rejected)

        if colors_hex:
            color_placeholders = ",".join("?" * len(colors_hex))
            q_color = base_query + f" AND color_hex IN ({color_placeholders})"
            p_color = params + colors_hex
            rows, matched_vibe = self._execute_vibe_query(cursor, q_color, p_color, vibe_pref)
            if rows: return dict(rows[0]), matched_vibe

        # Fallback
        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    def _find_layer(self, conn, occasion, gender, budget, colors_hex, rejected, vibe_pref):
        cursor = conn.cursor()
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category = 'Layer'
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [f"%{occasion}%", gender, budget] + list(rejected)

        if colors_hex:
            q_color = base_query + f" AND color_hex IN ({','.join('?' * len(colors_hex))})"
            p_color = params + colors_hex
            rows, matched_vibe = self._execute_vibe_query(cursor, q_color, p_color, vibe_pref)
            if rows: return dict(rows[0]), matched_vibe

        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    def _find_jewelry(self, conn, occasion, gender, metal, budget, rejected, pref_jewelry, vibe_pref):
        cursor = conn.cursor()
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category = 'Jewelry'
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND (? = 'Any' OR name LIKE ?)
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [f"%{occasion}%", gender, budget, pref_jewelry, f"%{pref_jewelry}%"] + list(rejected)
        
        q_metal = base_query + " AND (fabric LIKE ? OR color_family LIKE ?)"
        p_metal = params + [f"%{metal}%", f"%{metal}%"]
        rows, matched_vibe = self._execute_vibe_query(cursor, q_metal, p_metal, vibe_pref)
        if rows: return dict(rows[0]), matched_vibe
        
        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    def _find_footwear(self, conn, occasion, gender, budget, rejected, guidance, vibe_pref):
        cursor = conn.cursor()
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category = 'Footwear'
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [f"%{occasion}%", gender, budget] + list(rejected)
        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    def _find_accessory(self, conn, occasion, gender, budget, accent_colors, rejected, guidance, pref_accessory, vibe_pref):
        cursor = conn.cursor()
        base_query = f"""
            SELECT * FROM current_inventory
            WHERE category = 'Accessory'
              AND occasion_tags LIKE ?
              AND gender IN (?, 'unisex')
              AND price <= ?
              AND stock_status = 'in_stock'
              AND (? = 'Any' OR name LIKE ?)
              AND sku NOT IN ({','.join('?' * len(rejected))})
        """
        params = [f"%{occasion}%", gender, budget, pref_accessory, f"%{pref_accessory}%"] + list(rejected)

        if accent_colors:
            q_trend = base_query + f" AND color_family IN ({','.join('?' * len(accent_colors))})"
            p_trend = params + accent_colors
            rows, matched_vibe = self._execute_vibe_query(cursor, q_trend, p_trend, vibe_pref)
            if rows: return dict(rows[0]), matched_vibe

        rows, matched_vibe = self._execute_vibe_query(cursor, base_query, params, vibe_pref)
        return (dict(rows[0]), matched_vibe) if rows else (None, False)

    # ─── SCORING & CONVERSION ───

    def _row_to_outfit_item(self, row: dict, role: str) -> OutfitItem:
        """Convert a database row to an OutfitItem."""
        return OutfitItem(
            sku=row["sku"],
            name=row["name"],
            category=row["category"],
            brand=row.get("brand", ""),
            price=row["price"],
            color=row["color_family"],
            color_hex=row.get("color_hex", ""),
            fabric=row.get("fabric", ""),
            image_url=row.get("image_url", ""),
            product_url=row.get("product_url", ""),
            style_match_pct=0.0,  # calculated separately
            role=role,
        )

    def _calculate_trend_score(self, items: list[OutfitItem], trending_colors: list, trend_brief) -> float:
        """Calculate trend alignment score (1-10)."""
        if not items or not trending_colors:
            return 5.0

        score = 5.0  # base

        # Color alignment (up to +3)
        item_colors = {i.color for i in items}
        color_hits = len(item_colors.intersection(set(trending_colors)))
        score += min(color_hits * 1.5, 3.0)

        # Fabric alignment (up to +2)
        if trend_brief:
            item_fabrics = {i.fabric for i in items}
            fabric_hits = len(item_fabrics.intersection(set(trend_brief.key_fabrics)))
            score += min(fabric_hits, 2.0)

        return min(round(score, 1), 10.0)

    # ─── LOOKBOOK OUTPUT ───

    def format_lookbook(self, state: StyleState) -> str:
        """Format the curated outfit as a premium Lookbook Markdown output."""
        rec = state.final_recommendation
        if not rec:
            return "❌ No recommendation available. Run the pipeline first."

        profile = state.user_style_profile
        lines = []
        lines.append("=" * 60)
        lines.append("  ✨ YOUR CURATED LOOKBOOK ✨")
        lines.append("=" * 60)
        lines.append("")

        # Occasion & Context
        lines.append(f"  🎯 Occasion: {rec.occasion.replace('_', ' ').title()}")
        if rec.sub_occasion:
            lines.append(f"     Sub: {rec.sub_occasion.replace('_', ' ').title()}")
        if profile:
            lines.append(f"  🧬 Style DNA: {profile.style_dna}")
        lines.append(f"  🎨 Palette: {rec.palette_strategy.upper()}")
        lines.append(f"  📊 Trend Score: {rec.trend_alignment_score}/10")
        lines.append(f"  📦 Availability: {rec.inventory_availability_status.upper()}")
        lines.append("")

        # Group items by role
        sections = {
            "🧥 THE FOUNDATION": [],
            "✨ THE ACCENTS": [],
            "👠 THE FINISHING TOUCHES": [],
        }

        for item in rec.outfit_items:
            if "Foundation" in item.role:
                sections["🧥 THE FOUNDATION"].append(item)
            elif "Accent" in item.role or "Jewelry" in item.role:
                sections["✨ THE ACCENTS"].append(item)
            else:
                sections["👠 THE FINISHING TOUCHES"].append(item)

        for section_name, items in sections.items():
            if items:
                lines.append(f"  {section_name}")
                lines.append("  " + "─" * 40)
                for item in items:
                    lines.append(f"    • {item.name}")
                    lines.append(f"      Brand: {item.brand} | Color: {item.color}")
                    lines.append(f"      Fabric: {item.fabric} | ₹{item.price:,.0f}")
                    if item.product_url:
                        lines.append(f"      🔗 Shop: {item.product_url}")
                    if "Accent Piece (Trending)" in item.role:
                        lines.append(f"      ⭐ ACCENT: Trending color for this season!")
                    lines.append("")

        # Total cost
        total = sum(item.price for item in rec.outfit_items)
        lines.append(f"  💰 TOTAL: ₹{total:,.0f}")
        lines.append("")

        # The Why
        lines.append("  📝 THE STYLIST'S WHY")
        lines.append("  " + "─" * 40)
        lines.append(f"  \"{rec.the_why}\"")
        lines.append("")

        # Stylist Tip
        if rec.accessory_suite.get("stylist_tip"):
            lines.append(f"  {rec.accessory_suite['stylist_tip']}")
            lines.append("")

        # Bridge Logic note
        if rec.accessory_suite.get("accent_bridge"):
            lines.append("  🔗 ACCENT BRIDGE")
            lines.append(f"  {rec.accessory_suite['accent_bridge']}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)
