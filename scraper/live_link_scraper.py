"""
=============================================================
scraper/live_link_scraper.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  This file creates the LiveLinkScraper class.
  It searches Indian fashion websites for real, live product
  links for every clothing item in a recommended outfit.

  It works in this order:
    1. Build a search query from item name + colour + price
    2. Try Myntra → Nykaa → Ajio in order
    3. If all fail, return a Google Shopping fallback URL
    4. Enrich each item in an outfit dict with the link found

HOW TO USE:
  from scraper.live_link_scraper import LiveLinkScraper
  scraper = LiveLinkScraper()
  linked_outfit = scraper.get_outfit_links(outfit_dict)
=============================================================
"""

import time            # built-in: used to add delays between requests
import random          # built-in: used to pick a random User-Agent + random delay
import urllib.parse    # built-in: used to safely encode search queries in URLs

# requests: sends HTTP requests to fetch web pages
# If not installed: pip install requests
try:
    import requests                          # pip install requests
    REQUESTS_AVAILABLE = True                # flag so we know scraping is possible
except ImportError:
    REQUESTS_AVAILABLE = False               # scraping not available — will use fallback only
    print("  ⚠️  requests not installed — shopping links will be Google fallbacks")

# BeautifulSoup: parses HTML pages so we can find product links inside them
# If not installed: pip install beautifulsoup4
try:
    from bs4 import BeautifulSoup            # pip install beautifulsoup4
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("  ⚠️  beautifulsoup4 not installed — shopping links will be Google fallbacks")


# =============================================================
# USER AGENT ROTATION LIST
# =============================================================
# Web servers can detect and block bots by looking at the "User-Agent"
# header in every HTTP request. By rotating through real browser
# User-Agents, we look like a regular human visiting the site.
USER_AGENTS = [
    # Chrome on Windows — most common browser fingerprint
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    # Safari on Mac — Apple's default browser
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/604.1",

    # Chrome on Linux — common developer environment
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# Request timeout: every request must complete within 8 seconds
# If a site is slow or unreachable, we give up after 8s and try the next
REQUEST_TIMEOUT = 8   # seconds

# Minimum and maximum delay between requests, to avoid being rate-limited
DELAY_MIN = 1.0   # seconds — always wait at least 1 second
DELAY_MAX = 2.5   # seconds — never wait more than 2.5 seconds


# =============================================================
# CLASS: LiveLinkScraper
# =============================================================
class LiveLinkScraper:
    """
    Searches Indian fashion e-commerce sites for real product links.
    Tries Myntra, Nykaa, and Ajio in order.
    Falls back to Google Shopping if all three fail.
    """

    def _random_headers(self):
        """
        Returns a dictionary of HTTP headers with a randomly chosen User-Agent.
        Headers tell the server who is making the request.
        Rotating them reduces the chance of being blocked.
        """
        return {
            # Pick a random browser identity from our rotation list
            "User-Agent": random.choice(USER_AGENTS),

            # Tell the server we accept HTML pages
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

            # Tell the server we accept English responses
            "Accept-Language": "en-US,en;q=0.9",

            # Tell the server the connection can stay open (faster)
            "Connection": "keep-alive",
        }

    def _build_query(self, item_name, colour, max_price):
        """
        Creates a clean search query string from the item's details.
        Example: "powder blue silk kurta under 1500"

        item_name:  the clothing item description from the database
        colour:     the colour of the item
        max_price:  the maximum price the user wants to spend
        """
        # Combine name + colour + price into a single readable search phrase
        # We strip extra spaces from item_name to keep it clean
        query = f"{colour} {item_name.strip()} under {int(max_price)}"
        return query   # e.g. "powder blue silk-georgette kurta under 4500"

    def _safe_request(self, url):
        """
        Makes a single HTTP GET request with all anti-blocking measures:
        - Random User-Agent header
        - 8-second timeout
        - Returns the response object, or None if anything fails

        url: the full URL to fetch
        """
        # If requests module is missing, we can't make HTTP calls at all
        if not REQUESTS_AVAILABLE:
            return None

        try:
            # Add a small random pause BEFORE each request
            # This mimics human browsing rhythm and avoids rate limiting
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            # Make the actual HTTP GET request
            # timeout=REQUEST_TIMEOUT: give up after 8 seconds
            # allow_redirects=True: follow any redirects the site sends
            response = requests.get(
                url,
                headers=self._random_headers(),  # randomised headers
                timeout=REQUEST_TIMEOUT,          # never hang forever
                allow_redirects=True,             # follow redirects
            )

            # HTTP 200 means success — anything else means something went wrong
            if response.status_code == 200:
                return response   # success — return the response object
            else:
                # The server returned an error code (403 = blocked, 404 = not found, etc.)
                return None

        except requests.exceptions.Timeout:
            # The request took longer than 8 seconds — server is too slow
            return None
        except requests.exceptions.ConnectionError:
            # Could not reach the server (no internet, DNS failure, etc.)
            return None
        except Exception:
            # Catch any other unexpected error — never crash the app
            return None

    def _google_fallback(self, query):
        """
        Builds a Google Shopping search URL as a guaranteed fallback.
        Google Shopping always works — it shows real products from many stores.

        query: the search phrase to look up
        """
        # urllib.parse.quote_plus safely encodes spaces as '+' and special chars
        # so the URL is always valid
        encoded_query = urllib.parse.quote_plus(query)  # e.g. "blue+kurta+under+3000"
        return f"https://www.google.com/search?q={encoded_query}&tbm=shop"

    # ─────────────────────────────────────────────────────────
    # SITE-SPECIFIC METHODS
    # Each method searches one site and returns a URL or None
    # ─────────────────────────────────────────────────────────

    def search_myntra(self, item_name, colour, max_price):
        """
        Searches Myntra for a product matching the item details.
        Returns the direct search results URL (Myntra doesn't allow
        direct product links without JavaScript, so we return the search page).

        item_name:  clothing item description
        colour:     item colour
        max_price:  maximum price
        """
        try:
            # Build the search query
            query = self._build_query(item_name, colour, max_price)

            # Myntra's search URL format: myntra.com/{url-encoded-search-term}
            # The search term goes directly in the path, not as a query parameter
            search_term = urllib.parse.quote_plus(
                f"{colour} {item_name}".lower().strip()
            )
            url = f"https://www.myntra.com/{search_term}"

            # Try to fetch the page
            response = self._safe_request(url)

            if response and BS4_AVAILABLE:
                # Parse the HTML to find a product link
                soup = BeautifulSoup(response.text, "html.parser")

                # Myntra typically wraps products in anchor tags with class 'product-base'
                # Look for the first product link on the search results page
                product_link = soup.find("a", {"class": "product-base"})

                if product_link and product_link.get("href"):
                    # Build the full URL (Myntra uses relative paths in href)
                    href = product_link["href"]
                    if href.startswith("/"):
                        return f"https://www.myntra.com{href}"   # add domain prefix
                    return href   # already a full URL

            # If we got the page but couldn't find a product, return the search page URL
            # The user can still browse results from this page
            if response:
                return url

            return None   # request failed — caller will try next site

        except Exception:
            # Never let a scraping failure crash the app
            return None

    def search_nykaa(self, item_name, colour, max_price):
        """
        Searches Nykaa Fashion for a product matching the item details.
        Returns the search results URL or the first product URL found.

        item_name:  clothing item description
        colour:     item colour
        max_price:  maximum price
        """
        try:
            # Build the search query phrase
            query = self._build_query(item_name, colour, max_price)

            # Nykaa Fashion's search URL format: nykaafashion.com/search?q={query}
            encoded_query = urllib.parse.quote_plus(f"{colour} {item_name}")
            url = f"https://www.nykaafashion.com/search?q={encoded_query}"

            # Fetch the search results page
            response = self._safe_request(url)

            if response and BS4_AVAILABLE:
                soup = BeautifulSoup(response.text, "html.parser")

                # Nykaa wraps product cards in anchor tags — look for the first one
                # that links to a product page (usually contains /p/ in the path)
                for anchor in soup.find_all("a", href=True):
                    href = anchor["href"]
                    # Nykaa product pages have '/p/' in their URL
                    if "/p/" in href:
                        if href.startswith("/"):
                            return f"https://www.nykaafashion.com{href}"
                        if href.startswith("http"):
                            return href

            # Return the search page URL if no specific product found
            if response:
                return url

            return None   # failed — try next site

        except Exception:
            return None

    def search_ajio(self, item_name, colour, max_price):
        """
        Searches Ajio for a product matching the item details.
        Returns the search results URL or first product link found.

        item_name:  clothing item description
        colour:     item colour
        max_price:  maximum price
        """
        try:
            # Ajio's search URL format: ajio.com/search/?text={query}
            encoded_query = urllib.parse.quote_plus(f"{colour} {item_name}")
            url = f"https://www.ajio.com/search/?text={encoded_query}"

            # Fetch the search results page
            response = self._safe_request(url)

            if response and BS4_AVAILABLE:
                soup = BeautifulSoup(response.text, "html.parser")

                # Ajio product links typically contain '/p/' in the path
                for anchor in soup.find_all("a", href=True):
                    href = anchor["href"]
                    if "/p/" in href:
                        if href.startswith("/"):
                            return f"https://www.ajio.com{href}"
                        if href.startswith("http"):
                            return href

            # Return search page URL as useful fallback
            if response:
                return url

            return None   # request failed

        except Exception:
            return None

    def get_best_link(self, item_name, colour, max_price):
        """
        Master method: tries all 3 shopping sites in priority order.
        Returns the first successful URL found.
        Falls back to Google Shopping if all 3 fail.

        item_name:  the item name from the database
        colour:     the item colour
        max_price:  the maximum price

        Returns: (url_string, source_name_string)
          e.g. ("https://www.myntra.com/...", "Myntra")
        """
        # Build the search query once (it's the same for all sites)
        query = self._build_query(item_name, colour, max_price)

        # ── Priority 1: Try Myntra ─────────────────────────
        print(f"    🔍 Searching Myntra for: {item_name[:40]}...")
        myntra_url = self.search_myntra(item_name, colour, max_price)
        if myntra_url:
            print(f"    ✅ Myntra link found")
            return myntra_url, "Myntra"   # success — return immediately

        # ── Priority 2: Try Nykaa Fashion ─────────────────
        print(f"    🔍 Searching Nykaa for: {item_name[:40]}...")
        nykaa_url = self.search_nykaa(item_name, colour, max_price)
        if nykaa_url:
            print(f"    ✅ Nykaa link found")
            return nykaa_url, "Nykaa Fashion"

        # ── Priority 3: Try Ajio ───────────────────────────
        print(f"    🔍 Searching Ajio for: {item_name[:40]}...")
        ajio_url = self.search_ajio(item_name, colour, max_price)
        if ajio_url:
            print(f"    ✅ Ajio link found")
            return ajio_url, "Ajio"

        # ── Fallback: Google Shopping ──────────────────────
        # Always returns a useful URL — guaranteed to have results
        print(f"    ↩  All sites blocked — using Google Shopping fallback")
        fallback_url = self._google_fallback(query)
        return fallback_url, "Google Shopping"

    def get_outfit_links(self, outfit_dict):
        """
        Loops through every item slot in an outfit dict and calls
        get_best_link() for each piece that exists.
        Returns a COPY of the outfit dict with shopping_link and
        link_source added to each item.

        outfit_dict: one outfit dict from WardrobeArchitectAgent
        Returns: the same outfit dict with links added to each item
        """
        # Work on a copy so we don't accidentally mutate the original
        import copy
        enriched_outfit = copy.deepcopy(outfit_dict)   # make a deep copy

        # Get the items sub-dict (keys: dress, top, bottom, outerwear, footwear, bag)
        items = enriched_outfit.get("items", {})

        # Loop through each clothing slot
        for slot_name, item_data in items.items():
            # Skip empty slots (e.g. if no dress was found, the value is None)
            if item_data is None:
                continue

            # Extract fields needed for the search
            item_name = item_data.get("name", "")    # e.g. "Powder blue silk kurta"
            colour    = item_data.get("colour", "")  # e.g. "Powder Blue"

            # Parse the price — it is stored as "₹4,500" (a string), convert to number
            price_str = str(item_data.get("price", "0"))
            # Remove the ₹ sign and commas, then convert to float
            price_clean = price_str.replace("₹", "").replace(",", "").strip()
            try:
                max_price = float(price_clean)   # numeric price for the query
            except ValueError:
                max_price = 5000   # default if price string is malformed

            # Skip items with no name (shouldn't happen, but defensive check)
            if not item_name:
                continue

            # Search for a real link using all 3 sites
            link_url, link_source = self.get_best_link(item_name, colour, max_price)

            # Add the link fields to the item dict
            item_data["shopping_link"] = link_url      # the clickable URL
            item_data["link_source"]   = link_source   # site name e.g. "Myntra"

        # Return the enriched outfit dict (same structure, links added)
        return enriched_outfit

    # ===========================================================
    # UPGRADE 3 — Outfit image fetching (Myntra product images)
    # ===========================================================

    def get_item_image_url(self, item_name, colour, category):
        """
        Searches Myntra for the item and returns the first product image URL.
        Used to show real outfit images inside each result card.

        item_name: clothing description e.g. "navy silk kurta"
        colour:    item colour e.g. "navy blue"
        category:  clothing category e.g. "top", "lehenga"

        Returns: image URL string, or a placeholder URL if nothing found.
        """
        # Build search term combining colour and item name
        search_term = urllib.parse.quote_plus(f"{colour} {item_name}".lower().strip())

        # Myntra search URL
        search_url = f"https://www.myntra.com/{search_term}"

        try:
            response = self._safe_request(search_url)   # fetch Myntra search page

            if response and BS4_AVAILABLE:
                soup = BeautifulSoup(response.content, "html.parser")

                # Method 1: look for Myntra product images (class img-responsive)
                img = soup.find("img", {"class": "img-responsive"})
                if img and img.get("src"):
                    return img["src"]   # return direct image URL

                # Method 2: scan all images for Myntra CDN URLs
                for img in soup.find_all("img", src=True):
                    src = img["src"]
                    # Myntra product images are hosted on myntassets.com CDN
                    if "myntassets" in src:
                        return src

        except Exception:
            pass   # silently handle any scraping error

        # Fallback: Unsplash returns a relevant fashion image for the search term
        # (royalty-free, reliable, fashion-themed)
        fallback_query = urllib.parse.quote_plus(f"{colour} {category} fashion indian")
        return f"https://source.unsplash.com/130x155/?{fallback_query}"

    def get_outfit_with_images(self, outfit_dict):
        """
        Adds image_url to every item in the outfit dict.
        Fetches all images simultaneously using a thread pool for speed.

        outfit_dict: one outfit dict from WardrobeArchitectAgent

        Returns: outfit_dict with 'image_url' added to every item,
                 and 'item_image_urls' list added at the top level.
        """
        import copy
        import concurrent.futures   # for parallel image fetching

        # Work on a copy so we never mutate the original outfit data
        enriched = copy.deepcopy(outfit_dict)

        def fetch_for_item(slot_item_pair):
            """Fetch image for a single item. Runs in parallel for each item."""
            slot_name, item_data = slot_item_pair
            if not item_data or not isinstance(item_data, dict):
                return slot_name, item_data   # skip empty slots

            name     = item_data.get("name", "")
            colour   = item_data.get("colour", "")
            category = slot_name   # slot key is the category (top, bottom, etc.)

            # Fetch image URL for this item
            image_url = self.get_item_image_url(name, colour, category)
            item_data["image_url"] = image_url   # add to item dict
            return slot_name, item_data

        items = enriched.get("items", {})

        # Fetch all item images in parallel (max 5 threads)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(fetch_for_item, items.items()))

        # Put updated items back into the outfit dict
        enriched["items"] = dict(results)

        # Also build a convenient top-level list of all image URLs
        enriched["item_image_urls"] = [
            v.get("image_url", "")
            for v in enriched["items"].values()
            if isinstance(v, dict) and v.get("image_url")
        ]

        return enriched
