#!/usr/bin/env python3
"""
Pokemon TCG Restock Monitor
───────────────────────────
Checks Australian retailers for Pokemon card restocks and pre-orders,
then sends a Telegram push notification to your phone.

Runs automatically on GitHub Actions every 15 minutes.
You do NOT need to run this file yourself.
"""

import os
import json
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from retailers_config import RETAILERS

# ══════════════════════════════════════════════════════════════
# LOGGING  —  shows what the script is doing in GitHub Actions
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# CONFIGURATION  —  loaded from GitHub Secrets (never hard-coded)
# ══════════════════════════════════════════════════════════════
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE       = "state.json"   # tracks what we've already seen


# ══════════════════════════════════════════════════════════════
# ANTI-DETECTION  —  rotate user agents + realistic headers
# ══════════════════════════════════════════════════════════════
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

def get_headers() -> dict:
    """
    Returns a set of HTTP headers that look like a real browser.
    A random user agent is chosen each time to avoid patterns.
    """
    return {
        "User-Agent":                random.choice(USER_AGENTS),
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":           "en-AU,en;q=0.9",
        "Accept-Encoding":           "gzip, deflate, br",
        "Referer":                   "https://www.google.com.au/",
        "Connection":                "keep-alive",
        "Cache-Control":             "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "DNT":                       "1",
    }


# ══════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════
def load_state() -> dict:
    """Load previously seen products from state.json."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log.warning("⚠️  state.json is corrupted. Starting fresh — no alerts this run.")
    return {}


def save_state(state: dict) -> None:
    """Save current product snapshot to state.json."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    log.info("💾 State saved.")


# ══════════════════════════════════════════════════════════════
# TELEGRAM NOTIFICATIONS
# ══════════════════════════════════════════════════════════════
def send_telegram(message: str) -> bool:
    """Send a push notification to your phone via Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log.error("❌ Telegram credentials are missing. Check your GitHub Secrets.")
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(
            api_url,
            json={
                "chat_id":                  TELEGRAM_CHAT_ID,
                "text":                     message,
                "parse_mode":               "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        if response.status_code == 200:
            log.info("✅ Telegram notification sent!")
            return True
        log.error(f"❌ Telegram error {response.status_code}: {response.text}")
    except Exception as e:
        log.error(f"❌ Failed to reach Telegram: {e}")
    return False


def build_notification(event_type: str, retailer_name: str, product: dict) -> str:
    """Format a clean notification message."""
    icons  = {"new": "🆕", "restock": "✅", "preorder": "📋"}
    labels = {"new": "NEW LISTING", "restock": "BACK IN STOCK", "preorder": "PRE-ORDER OPEN"}

    icon  = icons.get(event_type, "🔔")
    label = labels.get(event_type, "ALERT")

    return (
        f"{icon} <b>Pokemon TCG Alert!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏪 <b>Retailer:</b> {retailer_name}\n"
        f"📦 <b>Status:</b>   {label}\n"
        f"🃏 <b>Product:</b>  {product['name']}\n"
        f"💰 <b>Price:</b>    {product['price']}\n"
        f"🔗 <a href='{product['url']}'>View Product →</a>"
    )


# ══════════════════════════════════════════════════════════════
# SCRAPER — SHOPIFY JSON API
# ══════════════════════════════════════════════════════════════
def scrape_shopify(retailer: dict) -> dict:
    """
    Shopify stores expose a public /products.json endpoint.
    This is far more reliable than HTML scraping — it's essentially
    a documented API that Shopify provides for all its stores.

    Returns: dict of { product_id: product_info }
    """
    found    = {}
    keywords = [k.lower() for k in retailer.get("keywords", ["pokemon"])]
    base_url = retailer["search_url"].split("?")[0]   # strip any existing query params
    session  = requests.Session()
    page     = 1

    while True:
        url = f"{base_url}?limit=250&page={page}"
        try:
            resp = session.get(url, headers=get_headers(), timeout=20)

            if resp.status_code == 404:
                log.warning(
                    f"  ⚠️  {retailer['name']}: Collection URL returned 404. "
                    "The URL in retailers_config.py may need updating."
                )
                break

            if resp.status_code != 200:
                log.warning(f"  ⚠️  {retailer['name']}: HTTP {resp.status_code}")
                break

            page_data = resp.json().get("products", [])
            if not page_data:
                break   # no more pages

            for p in page_data:
                title = p.get("title", "")

                # Skip products that don't contain our keywords
                if not any(kw in title.lower() for kw in keywords):
                    continue

                variants    = p.get("variants", [])
                in_stock    = any(v.get("available", False) for v in variants)
                tags        = [t.lower() for t in p.get("tags", [])]
                is_preorder = (
                    "pre-order" in title.lower()
                    or "preorder" in title.lower()
                    or "pre-order" in tags
                    or "preorder" in tags
                )

                # Price from first variant
                raw_price = variants[0].get("price", "") if variants else ""
                try:
                    price_str = f"${float(raw_price):.2f} AUD"
                except (ValueError, TypeError):
                    price_str = "Price TBA"

                product_id = str(p.get("id"))
                handle     = p.get("handle", "")

                found[product_id] = {
                    "name":        title,
                    "price":       price_str,
                    "url":         f"{retailer['base_url']}{handle}",
                    "in_stock":    in_stock,
                    "is_preorder": is_preorder,
                }

            page += 1
            time.sleep(random.uniform(0.5, 1.5))   # polite delay between pages

        except Exception as e:
            log.error(f"  ❌ {retailer['name']}: Error on page {page} — {e}")
            break

    return found


# ══════════════════════════════════════════════════════════════
# SCRAPER — REGULAR HTML PAGE
# ══════════════════════════════════════════════════════════════
def scrape_html(retailer: dict) -> dict:
    """
    Scrapes a regular search results page using BeautifulSoup.
    Uses CSS selectors defined in retailers_config.py to find products.

    NOTE: If a retailer redesigns their website, their CSS class names
    may change and the selectors in retailers_config.py will need updating.

    Returns: dict of { product_id: product_info }
    """
    found   = {}
    session = requests.Session()

    try:
        resp = session.get(
            retailer["search_url"],
            headers=get_headers(),
            timeout=25,
        )

        if resp.status_code != 200:
            log.warning(
                f"  ⚠️  {retailer['name']}: HTTP {resp.status_code}. "
                "May be temporarily blocked — will retry next run."
            )
            return found

        soup       = BeautifulSoup(resp.text, "lxml")
        containers = soup.select(retailer["product_container"])

        if not containers:
            log.warning(
                f"  ⚠️  {retailer['name']}: No products matched the CSS selector "
                f"'{retailer['product_container']}'. "
                "The site may use JavaScript to render products (results hidden from scraper), "
                "or the site layout has changed. Selector may need updating."
            )
            return found

        for i, card in enumerate(containers):
            try:
                # ── Product name ──
                name_el = card.select_one(retailer["product_name_selector"])
                name    = name_el.get_text(strip=True) if name_el else ""

                # Skip if name is blank or not Pokemon-related
                if not name or "pokemon" not in name.lower():
                    continue

                # ── Price ──
                price_el = card.select_one(retailer["product_price_selector"])
                price    = price_el.get_text(strip=True) if price_el else "Price TBA"

                # ── Product link ──
                link_el = card.select_one(retailer["product_link_selector"])
                href    = (link_el.get("href") or "") if link_el else ""
                if href and not href.startswith("http"):
                    href = retailer["base_url"] + href

                # ── Stock availability ──
                avail_sel = retailer.get("product_availability_selector")
                if avail_sel:
                    av_el    = card.select_one(avail_sel)
                    av_text  = av_el.get_text(strip=True).lower() if av_el else ""
                    in_stock = "out of stock" not in av_text and "sold out" not in av_text
                else:
                    # If product appears in search results, we assume it's listable.
                    # Restock detection is based on it re-appearing after being gone.
                    in_stock = True

                # ── Pre-order detection ──
                is_preorder = "pre-order" in name.lower() or "preorder" in name.lower()

                # Use a stable key made from the product name
                slug = "".join(c if c.isalnum() else "_" for c in name.lower())[:60]
                pid  = f"{retailer['id']}_{slug}"

                found[pid] = {
                    "name":        name,
                    "price":       price,
                    "url":         href,
                    "in_stock":    in_stock,
                    "is_preorder": is_preorder,
                }

            except Exception as e:
                log.debug(f"  Skipped card {i}: {e}")

    except Exception as e:
        log.error(f"  ❌ {retailer['name']}: Scrape failed — {e}")

    return found


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    log.info("=" * 60)
    log.info("🃏  Pokemon TCG Restock Monitor")
    log.info(f"🕐  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} (AEST = UTC+10 or +11)")
    log.info("=" * 60)

    old_state    = load_state()
    is_first_run = len(old_state) == 0
    new_state    = {}
    alerts       = []   # list of (retailer_name, event_type, product)

    if is_first_run:
        log.info(
            "🆕 FIRST RUN detected.\n"
            "   The monitor will scan all retailers and save a baseline.\n"
            "   No notifications are sent on the first run to avoid spam.\n"
            "   From the NEXT run onwards, you'll get alerts for any changes."
        )

    active_retailers = [r for r in RETAILERS if r.get("enabled", True)]
    log.info(f"\n📋 Checking {len(active_retailers)} retailer(s)...\n")

    for idx, retailer in enumerate(active_retailers):
        log.info(f"[{idx + 1}/{len(active_retailers)}] {retailer['name']}")

        # ── Run the appropriate scraper ──
        if retailer["type"] == "shopify":
            current_products = scrape_shopify(retailer)
        elif retailer["type"] == "html":
            current_products = scrape_html(retailer)
        else:
            log.error(f"  Unknown type '{retailer['type']}' — skipping.")
            continue

        log.info(f"  Found {len(current_products)} matching product(s).")
        new_state[retailer["id"]] = current_products

        # ── Compare with previous state (skip on first run) ──
        if not is_first_run:
            previous_products = old_state.get(retailer["id"], {})

            for pid, product in current_products.items():
                prev = previous_products.get(pid)

                if prev is None:
                    # Product is brand new (never seen before)
                    event = "preorder" if product["is_preorder"] else "new"
                    alerts.append((retailer["name"], event, product))
                    log.info(f"  🆕 NEW → {product['name']}")

                elif not prev["in_stock"] and product["in_stock"]:
                    # Was out of stock last time, now available
                    alerts.append((retailer["name"], "restock", product))
                    log.info(f"  ✅ RESTOCK → {product['name']}")

                elif not prev.get("is_preorder") and product["is_preorder"]:
                    # Pre-order just opened
                    alerts.append((retailer["name"], "preorder", product))
                    log.info(f"  📋 PRE-ORDER → {product['name']}")

        # ── Polite delay before hitting the next retailer ──
        if idx < len(active_retailers) - 1:
            delay = random.uniform(4, 9)
            log.info(f"  ⏳ Pausing {delay:.1f}s before next retailer (anti-detection)...\n")
            time.sleep(delay)

    # ── Send Telegram notifications ──
    log.info("\n" + "=" * 60)

    if is_first_run:
        log.info("✅ Baseline saved. You'll receive alerts from the next run.")

    elif alerts:
        log.info(f"📣 Sending {len(alerts)} notification(s) to Telegram...")
        for retailer_name, event_type, product in alerts:
            message = build_notification(event_type, retailer_name, product)
            send_telegram(message)
            time.sleep(1)   # small gap so messages arrive in order

    else:
        log.info("😴 No changes detected. Nothing new to report.")

    # ── Save updated state ──
    save_state(new_state)
    log.info("✅ Run complete.\n")


if __name__ == "__main__":
    main()
