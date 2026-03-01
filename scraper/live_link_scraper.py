"""
scraper/live_link_scraper.py — Style Agent v5
==============================================
FIX 2 — Google Shopping Links

IMPORTANT CHANGE from previous version:
We no longer try to scrape product pages directly.
Myntra, NYKAA, and Ajio all use JavaScript to load products —
so requests + BeautifulSoup only sees empty HTML and never finds real products.

The new approach: build pre-filtered Google Shopping search URLs.
These ALWAYS work, ALWAYS show real products, and open in the user's
browser showing items from ALL major Indian fashion retailers simultaneously.

No HTTP requests are made — this module only builds URL strings.
It can never fail or time out.
"""

import urllib.parse    # built-in — converts text to safe URL format (spaces → +)
import webbrowser      # built-in — opens URLs in the user's default browser


class LiveLinkScraper:
    """
    Generates relevant Google Shopping URLs for outfit items.
    Each URL opens a filtered Google Shopping page showing real products
    from Myntra, NYKAA, Ajio, Amazon Fashion, and other retailers.

    Why Google Shopping instead of scraping?
    - Myntra/Ajio/Nykaa render products via JavaScript → BeautifulSoup sees blank pages
    - Google Shopping aggregates ALL retailers in one URL
    - URLs always work — no network requests, no timeouts, no bot blocks
    """

    # ── Base URLs ─────────────────────────────────────────────────────────────
    GOOGLE_SHOPPING_BASE = "https://www.google.com/search?tbm=shop&q="  # Google Shopping

    def build_google_shopping_url(self, item_name, colour, gender, max_price, vibe):
        """
        Builds a Google Shopping URL that searches for the exact item.
        The URL includes a price ceiling and India-specific retailer hints.

        item_name:  clothing description e.g. "silk lehenga set"
        colour:     colour name e.g. "cobalt blue"
        gender:     "Women" or "Men"
        max_price:  maximum price in INR e.g. 5000
        vibe:       e.g. "Ethnic" or "Modern"

        Returns: a full HTTPS URL string
        """

        # Build the search query from item properties
        # More specific = better results on Google Shopping
        query_parts = [
            colour,           # colour first — Google weights it highly
            item_name,        # item description
            gender.lower(),   # "women" or "men"
            "India",          # restrict to Indian market
        ]

        # For ethnic items, add retailer hints to get Indian fashion results
        ethnic_vibes = ["ethnic", "indo-western", "classic"]
        if vibe.lower() in ethnic_vibes:
            query_parts.append("myntra OR ajio OR nykaa")

        # Join all parts with a space, then URL-encode (spaces → + etc.)
        query_string  = " ".join(query_parts)
        encoded_query = urllib.parse.quote_plus(query_string)

        # Google Shopping price filter (tbs parameter):
        #   mr:1       = apply multi-range filter
        #   price:1    = enable price filter
        #   ppr_max:X  = max price = X
        #   p_ord:rv   = sort by relevance
        price_filter = f"&tbs=p_ord:rv,mr:1,price:1,ppr_max:{int(max_price)}"

        # Assemble the full URL
        url = self.GOOGLE_SHOPPING_BASE + encoded_query + price_filter

        return url   # e.g. "https://www.google.com/search?tbm=shop&q=cobalt+blue+silk..."

    def build_myntra_search_url(self, item_name, colour, gender):
        """
        Builds a direct Myntra search URL for the item.
        Uses Myntra's /{search-term} URL format.

        item_name:  clothing description
        colour:     colour name
        gender:     "Women" or "Men"
        Returns: Myntra search URL string
        """
        # Myntra uses hyphen-separated search terms in the URL path
        query  = f"{colour} {item_name} {gender.lower()}"
        # URL-encode then replace + with - (Myntra's format)
        encoded = urllib.parse.quote_plus(query).replace("+", "-")
        return f"https://www.myntra.com/{encoded}"

    def build_ajio_search_url(self, item_name, colour, gender):
        """
        Builds an Ajio search URL.

        item_name:  clothing description
        colour:     colour name
        gender:     "Women" or "Men"
        Returns: Ajio search URL string
        """
        query   = f"{colour} {item_name}"
        encoded = urllib.parse.quote_plus(query)
        # Ajio uses ?text= for search queries
        return f"https://www.ajio.com/search/?text={encoded}&gender={gender.upper()}"

    def build_nykaa_search_url(self, item_name, colour):
        """
        Builds a Nykaa Fashion search URL.

        item_name:  clothing description
        colour:     colour name
        Returns: Nykaa Fashion search URL string
        """
        query   = f"{colour} {item_name}"
        encoded = urllib.parse.quote_plus(query)
        return f"https://www.nykaafashion.com/search?q={encoded}"

    def get_all_links_for_item(self, item_name, colour, gender, price, vibe):
        """
        Returns a dict of shopping links for one outfit item.
        Includes Google Shopping (primary) + Myntra + Ajio + Nykaa.

        This function NEVER fails — it always returns valid URLs
        because we are constructing URLs rather than scraping.

        item_name:  item description string
        colour:     colour name string
        gender:     "Women" or "Men"
        price:      price in INR (used for Google price filter)
        vibe:       vibe string e.g. "Ethnic"
        Returns: dict of {site_name: url_string}
        """
        links = {
            # Primary: Google Shopping (shows results from ALL retailers at once)
            "Google Shopping": self.build_google_shopping_url(
                item_name, colour, gender, price, vibe),

            # Direct retailer search links
            "Myntra":  self.build_myntra_search_url(item_name, colour, gender),
            "Ajio":    self.build_ajio_search_url(item_name, colour, gender),
            "Nykaa":   self.build_nykaa_search_url(item_name, colour),
        }
        return links

    def enrich_outfit_with_links(self, outfit_dict, gender, vibe):
        """
        Adds shopping links to every item in an outfit dictionary.
        Called after WardrobeArchitectAgent builds an outfit.

        outfit_dict: the outfit dict with an "items" list of dicts
        gender:      "Women" or "Men"
        vibe:        e.g. "Ethnic" or "Modern"
        Returns: outfit_dict with shopping links added to every item
        """
        items = outfit_dict.get("items", [])   # list of item dicts

        for item in items:
            if not isinstance(item, dict):
                continue   # skip any non-dict entries safely

            # Get links for this item
            item_links = self.get_all_links_for_item(
                item_name = item.get("item_name", ""),
                colour    = item.get("colour", ""),
                gender    = gender,
                price     = item.get("price", 5000),
                vibe      = vibe,
            )

            # Add the primary Google Shopping link and all links to the item
            item["shopping_link"]      = item_links["Google Shopping"]
            item["link_source"]        = "Google Shopping"
            item["all_shopping_links"] = item_links   # full dict for multi-link UI

        return outfit_dict   # return the enriched outfit

    # Keep backward-compatible alias so old code that calls get_outfit_links() still works
    def get_outfit_links(self, outfit_dict, gender="Women", vibe="Modern"):
        """
        Backward-compatible alias for enrich_outfit_with_links().
        Old code that calls scraper.get_outfit_links(outfit) will still work.
        """
        return self.enrich_outfit_with_links(outfit_dict, gender=gender, vibe=vibe)

    def open_link(self, url):
        """
        Opens a shopping link in the user's default web browser.
        url: any valid URL string
        """
        webbrowser.open(url)   # Python's built-in browser launcher
