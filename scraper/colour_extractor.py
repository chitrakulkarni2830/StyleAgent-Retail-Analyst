"""
=============================================================
scraper/colour_extractor.py — Style Agent Gold Standard
=============================================================
PURPOSE:
  Extracts the DOMINANT HEX COLOURS from any image file or URL.
  Uses Pillow (PIL) — resizes image, counts pixel colour buckets,
  filters out near-white/black, returns top N HEX codes.
  If Pillow is not installed, returns hardcoded 2026 fallback colours.
=============================================================
"""

import os    # built-in: file paths
import sys   # built-in: module path
import io    # built-in: bytes buffer for URL image downloads

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Try to import Pillow for image processing ─────────────────
try:
    from PIL import Image          # pip install Pillow
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("  ⚠️  Pillow not installed. Run: pip install Pillow")

# ── Try to import requests for URL image downloads ─────────────
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# =============================================================
# CLASS: ColourExtractor
# =============================================================
class ColourExtractor:
    """
    Extracts dominant HEX colours from image files or image URLs.
    Uses a simple pixel-counting approach — no machine learning needed.
    """

    def __init__(self, thumbnail_size=(100, 100)):
        """
        thumbnail_size: resize images to this before counting pixels
                        (smaller = faster, accuracy stays good)
        """
        self.thumbnail_size = thumbnail_size  # e.g. 100x100 pixels

    def _rgb_to_hex(self, rgb_tuple):
        """Converts (R, G, B) integers → '#RRGGBB' string."""
        r, g, b = rgb_tuple[0], rgb_tuple[1], rgb_tuple[2]
        return f"#{r:02X}{g:02X}{b:02X}"

    def _quantise_colour(self, rgb_tuple, step=32):
        """
        Groups similar colours into 'buckets' by rounding to nearest step.
        This reduces 16 million colours to ~512 distinct groups.
        """
        r = (rgb_tuple[0] // step) * step
        g = (rgb_tuple[1] // step) * step
        b = (rgb_tuple[2] // step) * step
        return (r, g, b)

    def _filter_near_white_black(self, colour_counts):
        """Removes near-white and near-black colours (usually backgrounds)."""
        filtered = {}
        for rgb, count in colour_counts.items():
            r, g, b = rgb
            if r > 220 and g > 220 and b > 220:
                continue   # skip near-white
            if r < 30 and g < 30 and b < 30:
                continue   # skip near-black
            filtered[rgb] = count
        return filtered

    def extract_from_image(self, pil_image, num_colours=5):
        """
        Core logic: takes an open Pillow Image → returns list of HEX strings.
        Steps: resize → convert to RGB → count pixels → sort → return top N.
        """
        try:
            image = pil_image.copy()
            image.thumbnail(self.thumbnail_size)         # shrink for speed
            image = image.convert("RGB")                 # ensure RGB (not RGBA)
            all_pixels = list(image.getdata())           # list of (R,G,B) tuples

            colour_count = {}
            for pixel in all_pixels:
                bucket = self._quantise_colour(pixel, step=32)
                colour_count[bucket] = colour_count.get(bucket, 0) + 1

            colour_count = self._filter_near_white_black(colour_count)
            if not colour_count:
                return self._fallback_colours(num_colours)

            sorted_colours = sorted(colour_count, key=colour_count.get, reverse=True)
            return [self._rgb_to_hex(c) for c in sorted_colours[:num_colours]]

        except Exception as error:
            print(f"    ⚠️  extract_from_image error: {error}")
            return self._fallback_colours(num_colours)

    def extract_from_file(self, image_path, num_colours=5):
        """Opens a local image file and returns its dominant HEX colours."""
        if not PILLOW_AVAILABLE:
            return self._fallback_colours(num_colours)
        if not os.path.exists(image_path):
            print(f"    ⚠️  Image not found: {image_path}")
            return self._fallback_colours(num_colours)
        try:
            with Image.open(image_path) as img:
                return self.extract_from_image(img, num_colours)
        except Exception as e:
            print(f"    ⚠️  Could not open {image_path}: {e}")
            return self._fallback_colours(num_colours)

    def extract_from_url(self, image_url, num_colours=5):
        """Downloads an image from a URL and extracts its dominant HEX colours."""
        if not PILLOW_AVAILABLE or not REQUESTS_AVAILABLE:
            return self._fallback_colours(num_colours)
        try:
            response = requests.get(image_url, timeout=5)
            if response.status_code == 200:
                image_bytes = io.BytesIO(response.content)
                with Image.open(image_bytes) as img:
                    return self.extract_from_image(img, num_colours)
            else:
                print(f"    ⚠️  HTTP {response.status_code} for {image_url}")
                return self._fallback_colours(num_colours)
        except Exception as e:
            print(f"    ⚠️  URL download failed: {e}")
            return self._fallback_colours(num_colours)

    def _fallback_colours(self, num_colours=5):
        """Returns hardcoded 2026 trend HEX colours as a safe fallback."""
        fallback = [
            "#C67C5A",   # Terracotta
            "#0047AB",   # Cobalt Blue
            "#B2AC88",   # Sage Green
            "#FFFFF0",   # Ivory
            "#800020",   # Deep Burgundy
        ]
        return fallback[:num_colours]


# ── Convenience wrapper functions ─────────────────────────────

def extract_dominant_colours(image_path, num_colours=5):
    """One-line helper: extract colours from a local image file."""
    return ColourExtractor().extract_from_file(image_path, num_colours)


def extract_from_url(image_url, num_colours=5):
    """One-line helper: extract colours from an image URL."""
    return ColourExtractor().extract_from_url(image_url, num_colours)


# =============================================================
# MAIN — for testing: python scraper/colour_extractor.py
# =============================================================
if __name__ == "__main__":
    print("\n=== Style Agent — Colour Extractor ===")
    extractor = ColourExtractor()
    fallback  = extractor._fallback_colours(5)
    names     = ["Terracotta", "Cobalt Blue", "Sage Green", "Ivory", "Deep Burgundy"]
    print("\nFallback 2026 Trend Colours:")
    for name, hex_code in zip(names, fallback):
        print(f"  • {name:15s}  {hex_code}")

    sample = os.path.join(PROJECT_ROOT, "assets", "sample_trend.jpg")
    if os.path.exists(sample):
        print(f"\nExtracting from: {sample}")
        print(extract_dominant_colours(sample))
    else:
        print("\nNo sample image found in assets/ — place a .jpg there to test.")
    print("\n✅ Colour Extractor ready.\n")
