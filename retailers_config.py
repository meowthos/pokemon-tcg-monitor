"""
=================================================================
  POKEMON TCG RESTOCK MONITOR — RETAILER CONFIGURATION
=================================================================
  Edit this file to add, remove, or disable retailers.

  ✅ TO ENABLE  → set "enabled": True
  🚫 TO DISABLE → set "enabled": False
  ➕ TO ADD     → copy the TEMPLATE block at the bottom
  🗑  TO REMOVE → delete its entire { ... } block

  SCRAPER TYPES:
    "shopify"   — uses the store's built-in JSON API. Very reliable.
    "html"      — reads the HTML page directly.

  SPECIAL FLAGS:
    "use_cloudscraper": False  — use regular requests instead of cloudscraper
                                 (needed for Amazon, which dislikes cloudscraper)
    "fallback_urls"           — extra collection paths to try if the main one fails
                                 (the scraper also auto-tries /collections/all as a
                                  last resort for any Shopify store)
=================================================================
"""

RETAILERS = [

    # ─────────────────────────────────────────────────────────────
    # JB HI-FI  •  Shopify  ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "jbhifi",
        "name":       "JB Hi-Fi",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.jbhifi.com.au/collections/pokemon/products.json",
        "fallback_urls": [
            "https://www.jbhifi.com.au/collections/trading-card-games/products.json",
            "https://www.jbhifi.com.au/collections/card-games/products.json",
            "https://www.jbhifi.com.au/collections/board-card-games/products.json",
            "https://www.jbhifi.com.au/collections/games/products.json",
            "https://www.jbhifi.com.au/collections/toys-collectables/products.json",
        ],
        "base_url":   "https://www.jbhifi.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # EB GAMES  •  ⛔ DISABLED
    # Reason: Uses Akamai Bot Manager — blocks ALL cloud server IPs.
    # Even cloudscraper cannot bypass this level of protection.
    # To re-enable if a workaround is found: set "enabled": True
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "ebgames",
        "name":       "EB Games",
        "enabled":    False,
        "type":       "html",
        "search_url": "https://www.ebgames.com.au/search?q=pokemon+trading+card",
        "base_url":   "https://www.ebgames.com.au",
        "product_container":             "li.product-tile",
        "product_name_selector":         ".product-tile__name",
        "product_price_selector":        ".product-tile__price",
        "product_link_selector":         "a",
        "product_availability_selector": ".product-tile__availability",
        "timeout":    30,
    },

    # ─────────────────────────────────────────────────────────────
    # TARGET AUSTRALIA  •  ⛔ DISABLED
    # Reason: Uses Akamai Bot Manager — blocks ALL cloud server IPs.
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "target",
        "name":       "Target Australia",
        "enabled":    False,
        "type":       "html",
        "search_url": "https://www.target.com.au/search?SearchTerm=pokemon+trading+card",
        "base_url":   "https://www.target.com.au",
        "product_container":             "article",
        "product_name_selector":         "h3",
        "product_price_selector":        "[class*='price']",
        "product_link_selector":         "a",
        "product_availability_selector": None,
        "timeout":    30,
    },

    # ─────────────────────────────────────────────────────────────
    # KMART  •  ⛔ DISABLED
    # Reason: Uses Akamai Bot Manager — blocks ALL cloud server IPs.
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "kmart",
        "name":       "Kmart",
        "enabled":    False,
        "type":       "html",
        "search_url": "https://www.kmart.com.au/search?q=pokemon",
        "base_url":   "https://www.kmart.com.au",
        "product_container":             "article",
        "product_name_selector":         "h3",
        "product_price_selector":        "[class*='price']",
        "product_link_selector":         "a",
        "product_availability_selector": None,
        "timeout":    30,
    },

    # ─────────────────────────────────────────────────────────────
    # BIG W  •  ⛔ DISABLED
    # Reason: Consistently times out — actively blocks all cloud traffic.
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "bigw",
        "name":       "Big W",
        "enabled":    False,
        "type":       "html",
        "search_url": "https://www.bigw.com.au/search?text=pokemon+trading+card",
        "base_url":   "https://www.bigw.com.au",
        "product_container":             "[class*='ProductTile']",
        "product_name_selector":         "p, h3",
        "product_price_selector":        "[class*='price']",
        "product_link_selector":         "a",
        "product_availability_selector": None,
        "timeout":    45,
    },

    # ─────────────────────────────────────────────────────────────
    # ZING  •  Shopify  ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "zing",
        "name":       "Zing",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.zing.com.au/collections/pokemon/products.json",
        "fallback_urls": [
            "https://www.zing.com.au/collections/trading-card-games/products.json",
            "https://www.zing.com.au/collections/card-games/products.json",
            "https://www.zing.com.au/collections/collectibles/products.json",
            "https://www.zing.com.au/collections/games/products.json",
        ],
        "base_url":   "https://www.zing.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # TOYMATE  •  Shopify  ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "toymate",
        "name":       "Toymate",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.toymate.com.au/collections/pokemon/products.json",
        "fallback_urls": [
            "https://www.toymate.com.au/collections/pokemon-trading-card-game/products.json",
            "https://www.toymate.com.au/collections/pokemon-cards/products.json",
            "https://www.toymate.com.au/collections/trading-card-games/products.json",
            "https://www.toymate.com.au/collections/card-games/products.json",
            "https://www.toymate.com.au/collections/trading-cards/products.json",
        ],
        "base_url":   "https://www.toymate.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # AMAZON AUSTRALIA  •  HTML  ✅
    # NOTE: use_cloudscraper is False — Amazon works better WITHOUT
    # cloudscraper. It was finding 37 products before cloudscraper
    # was introduced and broke it.
    # ─────────────────────────────────────────────────────────────
    {
        "id":               "amazon",
        "name":             "Amazon Australia",
        "enabled":          True,
        "type":             "html",
        "use_cloudscraper": False,
        "search_url":       "https://www.amazon.com.au/s?k=pokemon+trading+card+game&rh=n%3A4851267051",
        "base_url":         "https://www.amazon.com.au",
        "product_container":             "div[data-component-type='s-search-result']",
        "product_name_selector":         "h2 span",
        "product_price_selector":        "span.a-price-whole",
        "product_link_selector":         "h2 a",
        "product_availability_selector": None,
        "timeout":    30,
    },

    # ─────────────────────────────────────────────────────────────
    # HOBBYKITZ  •  Shopify  ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "hobbykitz",
        "name":       "HobbyKitz",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.hobbykitz.com.au/collections/pokemon/products.json",
        "fallback_urls": [
            "https://www.hobbykitz.com.au/collections/pokemon-trading-card-game/products.json",
            "https://www.hobbykitz.com.au/collections/trading-card-games/products.json",
            "https://www.hobbykitz.com.au/collections/pokemon-cards/products.json",
            "https://www.hobbykitz.com.au/collections/card-games/products.json",
            "https://www.hobbykitz.com.au/collections/trading-cards/products.json",
        ],
        "base_url":   "https://www.hobbykitz.com.au/products/",
        "keywords":   ["pokemon"],
    },


    # =================================================================
    # ✏️  TEMPLATE — copy and fill in to add a new retailer
    # =================================================================
    #
    # --- SHOPIFY STORE ---
    # {
    #     "id":         "store_id",
    #     "name":       "Store Name",
    #     "enabled":    False,
    #     "type":       "shopify",
    #     "search_url": "https://example.com.au/collections/pokemon/products.json",
    #     "fallback_urls": [
    #         "https://example.com.au/collections/trading-cards/products.json",
    #     ],
    #     "base_url":   "https://example.com.au/products/",
    #     "keywords":   ["pokemon"],
    # },
    #
    # --- HTML STORE ---
    # {
    #     "id":               "store_id",
    #     "name":             "Store Name",
    #     "enabled":          False,
    #     "type":             "html",
    #     "use_cloudscraper": True,
    #     "search_url":       "https://example.com.au/search?q=pokemon",
    #     "base_url":         "https://example.com.au",
    #     "product_container":             "CSS selector for each product card",
    #     "product_name_selector":         "CSS selector for product name",
    #     "product_price_selector":        "CSS selector for price",
    #     "product_link_selector":         "a",
    #     "product_availability_selector": None,
    #     "timeout":          30,
    # },

]
