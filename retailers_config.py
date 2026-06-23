"""
=================================================================
  POKEMON TCG RESTOCK MONITOR — RETAILER CONFIGURATION
=================================================================
  This is the ONLY file you need to edit to add/remove retailers.

  ✅ TO ENABLE a retailer  → set "enabled": True
  🚫 TO DISABLE (not delete) → set "enabled": False
  ➕ TO ADD a new retailer  → copy the TEMPLATE block at the bottom
  🗑  TO REMOVE a retailer  → delete its entire { ... } block

  SCRAPER TYPES:
    "shopify" — uses the store's built-in JSON API. Very reliable.
    "html"    — reads the HTML page directly. May need selector
                updates if the site redesigns their pages.
=================================================================
"""

RETAILERS = [

    # ─────────────────────────────────────────────────────────────
    # JB HI-FI  •  Shopify store  •  Very reliable ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "jbhifi",
        "name":       "JB Hi-Fi",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.jbhifi.com.au/collections/pokemon/products.json",
        "base_url":   "https://www.jbhifi.com.au/products/",
        # Only products whose titles contain at least one of these words are tracked
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # EB GAMES  •  HTML scraper
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "ebgames",
        "name":       "EB Games",
        "enabled":    True,
        "type":       "html",
        "search_url": "https://www.ebgames.com.au/search?q=pokemon+trading+card",
        "base_url":   "https://www.ebgames.com.au",
        # CSS selectors — tell the scraper where to find product info on the page
        "product_container":             "li.product-tile",
        "product_name_selector":         ".product-tile__name",
        "product_price_selector":        ".product-tile__price",
        "product_link_selector":         "a",
        "product_availability_selector": ".product-tile__availability",
    },

    # ─────────────────────────────────────────────────────────────
    # TARGET AUSTRALIA  •  HTML scraper
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
    },

    # ─────────────────────────────────────────────────────────────
    # KMART AUSTRALIA  •  HTML scraper
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
    },

    # ─────────────────────────────────────────────────────────────
    # BIG W  •  HTML scraper
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
    },

    # ─────────────────────────────────────────────────────────────
    # ZING  •  Shopify store  •  Very reliable ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "zing",
        "name":       "Zing",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.zinggadgets.com.au/collections/pokemon/products.json",
        "base_url":   "https://www.zinggadgets.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # TOYMATE  •  Shopify store  •  Very reliable ✅
    # ─────────────────────────────────────────────────────────────
    {
        "id":         "toymate",
        "name":       "Toymate",
        "enabled":    True,
        "type":       "shopify",
        "search_url": "https://www.toymate.com.au/collections/pokemon/products.json",
        "base_url":   "https://www.toymate.com.au/products/",
        "keywords":   ["pokemon"],
    },

    # ─────────────────────────────────────────────────────────────
    # AMAZON AUSTRALIA  •  HTML scraper
    # ⚠️  Amazon has strong bot detection. It will work most of
    #     the time with our headers but may occasionally be blocked.
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
    },


    # =================================================================
    # ✏️  TEMPLATE — Copy everything between the triple-quotes below
    #     and paste it above this comment block to add a new retailer.
    # =================================================================
    #
    # --- SHOPIFY STORE TEMPLATE ---
    # {
    #     "id":         "store_id",          # short unique ID, no spaces
    #     "name":       "Store Display Name", # shown in your notification
    #     "enabled":    False,                # change to True to activate
    #     "type":       "shopify",
    #     "search_url": "https://example.com.au/collections/pokemon/products.json",
    #     "base_url":   "https://example.com.au/products/",
    #     "keywords":   ["pokemon"],
    # },
    #
    # --- REGULAR HTML STORE TEMPLATE ---
    # {
    #     "id":         "store_id",
    #     "name":       "Store Display Name",
    #     "enabled":    False,
    #     "type":       "html",
    #     "search_url": "https://example.com.au/search?q=pokemon",
    #     "base_url":   "https://example.com.au",
    #     "product_container":             "CSS selector for each product card",
    #     "product_name_selector":         "CSS selector for the product name",
    #     "product_price_selector":        "CSS selector for the price",
    #     "product_link_selector":         "a",
    #     "product_availability_selector": None,
    # },

]
