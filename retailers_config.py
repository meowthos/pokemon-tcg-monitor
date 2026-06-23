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
    "shopify" — uses the store's built-in JSON API. Very reliable.
    "html"    — reads the HTML page. May need selector updates
                if the site redesigns their pages.

  fallback_urls (Shopify only):
    If the primary search_url returns a 404, the scraper will
    automatically try each URL in this list until one works.
=================================================================
"""

RETAILERS = [

    # ─────────────────────────────────────────────────────────────
    # JB HI-FI  •  Shopify  •  Fixed: added fallback collection paths
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
        ],
        "base_url":   "https://www.jbhifi.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # EB GAMES  •  HTML
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "ebgames",
        "name":       "EB Games",
        "enabled":    True,
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
    # TARGET AUSTRALIA  •  HTML
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "target",
        "name":       "Target Australia",
        "enabled":    True,
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
    # KMART  •  HTML
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "kmart",
        "name":       "Kmart",
        "enabled":    True,
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
    # BIG W  •  HTML  •  Fixed: increased timeout
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "bigw",
        "name":       "Big W",
        "enabled":    True,
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
    # ZING  •  Shopify  •  FIXED: correct domain is zing.com.au
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
        ],
        "base_url":   "https://www.zing.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # TOYMATE  •  Shopify  •  FIXED: added fallback collection paths
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
    # AMAZON AUSTRALIA  •  HTML  •  Already working ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "amazon",
        "name":       "Amazon Australia",
        "enabled":    True,
        "type":       "html",
        "search_url": "https://www.amazon.com.au/s?k=pokemon+trading+card+game&rh=n%3A4851267051",
        "base_url":   "https://www.amazon.com.au",
        "product_container":             "div[data-component-type='s-search-result']",
        "product_name_selector":         "h2 span",
        "product_price_selector":        "span.a-price-whole",
        "product_link_selector":         "h2 a",
        "product_availability_selector": None,
        "timeout":    30,
    },

    # ─────────────────────────────────────────────────────────────
    # HOBBYKITZ  •  Shopify  •  NEW ✅
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
    # --- REGULAR HTML STORE ---
    # {
    #     "id":         "store_id",
    #     "name":       "Store Name",
    #     "enabled":    False,
    #     "type":       "html",
    #     "search_url": "https://example.com.au/search?q=pokemon",
    #     "base_url":   "https://example.com.au",
    #     "product_container":             "CSS selector for each product card",
    #     "product_name_selector":         "CSS selector for product name",
    #     "product_price_selector":        "CSS selector for price",
    #     "product_link_selector":         "a",
    #     "product_availability_selector": None,
    #     "timeout":    30,
    # },

]
