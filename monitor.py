#!/usr/bin/env python3
"""
Pokemon TCG Restock Monitor
───────────────────────────
Checks Australian retailers for Pokemon card restocks and pre-orders,
then sends a Telegram push notification to your phone.

Runs automatically on GitHub Actions every 15 minutes.
"""

import os
import json
import time
import random
import logging
import requests
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

from retailers_config import RETAILERS

# ══════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)
logging.getLogger("cloudscraper").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════
# CONFIGURATION  —  loaded from GitHub Secrets
# ══════════════════════════════════════════════════════════════
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE       = "state.json"


# ══════════════════════════════════════════════════════════════
# ANTI-DETECTION  —  rotate user agents + realistic headers
# ══════════════════════════════════════════════════════════════
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

def get_headers() -> dict:
    """Realistic browser headers to avoid bot detection."""
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

def create_session(use_cloudscraper: bool = True):
    """
    Creates the right HTTP session for a retailer.
    - use_cloudscraper=True  → cloudscraper (bypasses CloudFlare)
    - use_cloudscraper=False → plain requests (better for Amazon)
    """
    if use_cloudscraper:
        try:
            return cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )
        except Exception as e:
            log.warning(f"cloudscraper init failed ({e}), falling back to requests.Session()")
    return requests.Session()


# ══════════════════════════════════════════════════════════════
# URL HELPER  —  handles relative, protocol-relative, and full URLs
# ══════════════════════════════════════════════════════════════
def build_url(href: str, base_url: str) -> str:
    """
    Turns any kind of href into a clean, absolute URL.
    Handles: relative paths (/products/...), protocol-relative (//example.com),
    and full URLs (https://...).
    """
    if not href:
        return ""
    href = href.strip()
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    if href.startswith("http"):
        return href
    # Relative path without leading slash
    return base_url.rstrip("/") + "/" + href


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
            log.warning("⚠️  state.json corrupted — starting fresh, no alerts this run.")
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
        log.error("❌ Telegram credentials missing. Check GitHub Secrets.")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id":                  TELEGRAM_CHAT_ID,
                "text":                     message,
                "parse_mode":               "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            log.info("✅ Telegram notification sent!")
            return True
        log.error(f"❌ Telegram error {resp.status_code}: {resp.text}")
    except Exception as e:
        log.error(f"❌ Failed to reach Telegram: {e}")
    return False

def build_notification(event_type: str, retailer_name: str, product: dict) -> str:
    """Format a clean, clickable notification message."""
    icons  = {"new": "🆕", "restock": "✅", "preorder": "📋"}
    labels = {"new": "NEW LISTING", "restock": "BACK IN STOCK", "preorder": "PRE-ORDER OPEN"}
    icon   = icons.get(event_type, "🔔")
    label  = labels.get(event_type, "ALERT")

    # Build the link line — only show if we have a valid URL
    url = (product.get("url") or "").strip()
    link_line = (
        f"🔗 <a href='{url}'>View Product →</a>"
        if url and url.startswith("http")
        else "🔗 Link unavailable"
    )

    return (
        f"{icon} <b>Pokemon TCG Alert!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏪 <b>Retailer:</b> {retailer_name}\n"
        f"📦 <b>Status:</b>   {label}\n"
        f"🃏 <b>Product:</b>  {product['name']}\n"
        f"💰 <b>Price:</b>    {product['price']}\n"
        f"{link_line}"
    )


# ══════════════════════════════════════════════════════════════
# SHOPIFY SCRAPER
# ══════════════════════════════════════════════════════════════
def find_working_shopify_url(session, retailer: dict) -> str | None:
    """
    Tries the primary search_url, then each fallback_url, and finally
    auto-tries /collections/all as a universal last resort — this works
    on virtually every Shopify store regardless of collection structure.

    Returns the first URL that responds with valid product JSON, or None.
    """
    # Build the full list of URLs to probe (normalised, no query string)
    urls_to_try = []
    for raw in [retailer["search_url"]] + retailer.get("fallback_urls", []):
        base = raw.split("?")[0].replace("/products.json", "")
        if base not in urls_to_try:
            urls_to_try.append(base)

    # Auto-add /collections/all as a universal last resort
    domain = retailer["search_url"].split("/collections/")[0]
    all_url = f"{domain}/collections/all"
    if all_url not in urls_to_try:
        urls_to_try.append(all_url)

    for base in urls_to_try:
        test_url = f"{base}/products.json?limit=1&page=1"
        try:
            resp = session.get(test_url, headers=get_headers(), timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if "products" in data:
                    log.info(f"  ✅ Working URL: ...{base.split('.com.au')[-1]}")
                    return base
            # 404 = collection doesn't exist, try next silently
        except Exception as e:
            log.debug(f"  Probe failed for {base}: {e}")

    return None


def scrape_shopify(retailer: dict) -> dict:
    """
    Scrapes Shopify stores via their public /products.json API.
    Automatically discovers the correct collection URL.
    """
    found    = {}
    keywords = [k.lower() for k in retailer.get("keywords", ["pokemon"])]
    session  = create_session(retailer.get("use_cloudscraper", True))

    base_url = find_working_shopify_url(session, retailer)
    if not base_url:
        log.warning(
            f"  ⚠️  {retailer['name']}: Could not find any working collection URL.\n"
            "     The site may not be a Shopify store, or may be blocking all requests.\n"
            "     Try adding more fallback_urls in retailers_config.py."
        )
        return found

    page = 1
    while True:
        url = f"{base_url}/products.json?limit=250&page={page}"
        try:
            resp = session.get(url, headers=get_headers(), timeout=20)
            if resp.status_code != 200:
                log.warning(f"  ⚠️  {retailer['name']}: HTTP {resp.status_code} on page {page}")
                break

            try:
                page_data = resp.json().get("products", [])
            except Exception:
                log.warning(
                    f"  ⚠️  {retailer['name']}: Response wasn't valid JSON.\n"
                    f"     First 120 chars: {resp.text[:120]}"
                )
                break

            if not page_data:
                break  # no more pages

            for p in page_data:
                title = p.get("title", "")
                if not any(kw in title.lower() for kw in keywords):
                    continue

                variants    = p.get("variants", [])
                in_stock    = any(v.get("available", False) for v in variants)
                tags        = [t.lower() for t in p.get("tags", [])]
                is_preorder = (
                    "pre-order" in title.lower() or "preorder" in title.lower()
                    or "pre-order" in tags       or "preorder"  in tags
                )

                raw_price = variants[0].get("price", "") if variants else ""
                try:
                    price_str = f"${float(raw_price):.2f} AUD"
                except (ValueError, TypeError):
                    price_str = "Price TBA"

                pid    = str(p.get("id"))
                handle = p.get("handle", "")
                found[pid] = {
                    "name":        title,
                    "price":       price_str,
                    "url":         f"{retailer['base_url']}{handle}",
                    "in_stock":    in_stock,
                    "is_preorder": is_preorder,
                }

            page += 1
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            log.error(f"  ❌ {retailer['name']}: Error on page {page} — {e}")
            break

    return found


# ══════════════════════════════════════════════════════════════
# HTML SCRAPER
# ══════════════════════════════════════════════════════════════
def scrape_html(retailer: dict) -> dict:
    """
    Scrapes HTML pages using BeautifulSoup.
    Respects the per-retailer use_cloudscraper flag.
    """
    found   = {}
    timeout = retailer.get("timeout", 30)
    session = create_session(retailer.get("use_cloudscraper", True))

    try:
        resp = session.get(retailer["search_url"], headers=get_headers(), timeout=timeout)

        if resp.status_code == 403:
            log.warning(
                f"  ⚠️  {retailer['name']}: 403 Forbidden — uses advanced bot protection\n"
                "     that cannot be bypassed from GitHub Actions cloud IPs."
            )
            return found

        if resp.status_code != 200:
            log.warning(f"  ⚠️  {retailer['name']}: HTTP {resp.status_code}")
            return found

        soup       = BeautifulSoup(resp.text, "lxml")
        containers = soup.select(retailer["product_container"])

        if not containers:
            log.warning(
                f"  ⚠️  {retailer['name']}: 0 products matched '{retailer['product_container']}'.\n"
                "     The site may render products with JavaScript (not visible to scraper),\n"
                "     or the page layout has changed."
            )
            return found

        for i, card in enumerate(containers):
            try:
                # ── Name ──
                name_el = card.select_one(retailer["product_name_selector"])
                name    = name_el.get_text(strip=True) if name_el else ""
                if not name or "pokemon" not in name.lower():
                    continue

                # ── Price ──
                price_el = card.select_one(retailer["product_price_selector"])
                price    = price_el.get_text(strip=True) if price_el else "Price TBA"

                # ── Link  — try href first, fall back to data-href ──
                link_el  = card.select_one(retailer["product_link_selector"])
                raw_href = ""
                if link_el:
                    raw_href = link_el.get("href") or link_el.get("data-href") or ""
                href = build_url(raw_href, retailer["base_url"])

                # ── Availability ──
                avail_sel = retailer.get("product_availability_selector")
                if avail_sel:
                    av_el    = card.select_one(avail_sel)
                    av_text  = av_el.get_text(strip=True).lower() if av_el else ""
                    in_stock = "out of stock" not in av_text and "sold out" not in av_text
                else:
                    in_stock = True

                is_preorder = "pre-order" in name.lower() or "preorder" in name.lower()

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
    alerts       = []

    if is_first_run:
        log.info(
            "🆕 FIRST RUN — scanning all retailers to build a baseline.\n"
            "   No notifications this run. Alerts start from the NEXT run."
        )

    active = [r for r in RETAILERS if r.get("enabled", True)]
    log.info(f"\n📋 Checking {len(active)} retailer(s)...\n")

    for idx, retailer in enumerate(active):
        log.info(f"[{idx + 1}/{len(active)}] {retailer['name']}")

        # ── Scrape ──
        if retailer["type"] == "shopify":
            current = scrape_shopify(retailer)
        elif retailer["type"] == "html":
            current = scrape_html(retailer)
        else:
            log.error(f"  Unknown type '{retailer['type']}' — skipping.")
            continue

        log.info(f"  Found {len(current)} matching product(s).")
        new_state[retailer["id"]] = current

        # ── Compare with previous state ──
        if not is_first_run:
            previous = old_state.get(retailer["id"], {})

            # If this retailer had 0 products before (failed/new), treat it
            # as a fresh baseline to avoid notification spam
            if len(previous) == 0 and len(current) > 0:
                log.info(
                    f"  📝 First successful scan for {retailer['name']} — "
                    "saving baseline, no alerts this time."
                )
            else:
                for pid, product in current.items():
                    prev = previous.get(pid)

                    if prev is None:
                        # Brand new product
                        event = "preorder" if product["is_preorder"] else "new"
                        alerts.append((retailer["name"], event, product))
                        log.info(f"  🆕 NEW → {product['name']}")

                    elif not prev["in_stock"] and product["in_stock"]:
                        # Was out of stock, now available
                        alerts.append((retailer["name"], "restock", product))
                        log.info(f"  ✅ RESTOCK → {product['name']}")

                    elif not prev.get("is_preorder") and product["is_preorder"]:
                        # Pre-order just opened
                        alerts.append((retailer["name"], "preorder", product))
                        log.info(f"  📋 PRE-ORDER → {product['name']}")

        # ── Polite delay before next retailer ──
        if idx < len(active) - 1:
            delay = random.uniform(4, 9)
            log.info(f"  ⏳ Pausing {delay:.1f}s...\n")
            time.sleep(delay)

    # ── Send notifications ──
    log.info("\n" + "=" * 60)

    if is_first_run:
        log.info("✅ Baseline saved. Alerts start from the next run.")
    elif alerts:
        log.info(f"📣 Sending {len(alerts)} notification(s)...")
        for retailer_name, event_type, product in alerts:
            send_telegram(build_notification(event_type, retailer_name, product))
            time.sleep(1)
    else:
        log.info("😴 No changes detected.")

    save_state(new_state)
    log.info("✅ Run complete.\n")


if __name__ == "__main__":
    main()
