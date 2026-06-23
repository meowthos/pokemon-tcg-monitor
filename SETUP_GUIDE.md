# 🃏 Pokemon TCG Restock Monitor — Setup Guide

Follow these steps in order. Takes about 15–20 minutes total.

---

## 📁 Files in This Project

| File | What it does |
|---|---|
| `monitor.py` | The main script — do not edit |
| `retailers_config.py` | Add / remove retailers here |
| `requirements.txt` | Python libraries needed — do not edit |
| `.github/workflows/monitor.yml` | Tells GitHub to run every 15 mins — do not edit |
| `state.json` | Created automatically — tracks what's been seen |

---

## STEP 1 — Create a New GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `pokemon-tcg-monitor`
   - **Visibility:** Private ← important (keeps your bot token safe)
   - Tick **"Add a README file"**
4. Click **"Create repository"**

---

## STEP 2 — Upload the Files

> Do this for each file: `monitor.py`, `retailers_config.py`, `requirements.txt`

1. In your new repo, click **"Add file"** → **"Upload files"**
2. Drag and drop the 3 files above
3. Click **"Commit changes"**

### For the workflow file (special location needed):

The workflow file must live inside a `.github/workflows/` folder.

1. In your repo, click **"Add file"** → **"Create new file"**
2. In the filename box, type exactly: `.github/workflows/monitor.yml`
   - GitHub will automatically create the folders as you type the `/`
3. Open the `monitor.yml` file you downloaded and **copy all its contents**
4. Paste into the text editor on GitHub
5. Click **"Commit changes"** → **"Commit directly to the main branch"** → **"Commit changes"**

---

## STEP 3 — Add Your Telegram Secrets

Your bot token and chat ID are private — we store them as GitHub Secrets so they're never visible in your code.

1. In your repo, click **Settings** (top menu)
2. On the left sidebar: **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add these two secrets:

**Secret 1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: your bot token (e.g. `110201543:AAHdqTcvCH1vGWJxfSeofSs4tDW5jene2Z`)

**Secret 2:**
- Name: `TELEGRAM_CHAT_ID`
- Value: your chat ID number (e.g. `123456789`)

4. Click **"Add secret"** after each one

---

## STEP 4 — Test It Manually

Before waiting 15 minutes for the schedule, trigger a manual run:

1. In your repo, click the **"Actions"** tab
2. On the left, click **"Pokemon TCG Restock Monitor"**
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Wait ~30–60 seconds, then refresh the page
5. Click the run to see the logs

**What you should see in the logs:**
```
🆕 FIRST RUN detected.
   The monitor will scan all retailers and save a baseline.
   No notifications are sent on the first run...
✅ Baseline saved. You'll receive alerts from the next run.
```

If you see ❌ errors, check the "Troubleshooting" section below.

---

## STEP 5 — Sit Back and Wait 🎉

After the first run:
- The schedule kicks in automatically every 15 minutes
- You'll get a Telegram notification whenever something changes
- No PC, no phone, no action needed from you

---

## 🔧 How to Add or Remove a Retailer

1. Open `retailers_config.py` in your GitHub repo (click the file, then the ✏️ pencil icon)
2. To **disable**: find the retailer and change `"enabled": True` to `"enabled": False`
3. To **add new**: copy the TEMPLATE block at the bottom and fill in the details
4. Click **"Commit changes"**

---

## ❗ Troubleshooting

**"No products matched the CSS selector"**
→ The retailer's website uses JavaScript to load products, which our scraper can't see.
  This is normal for Kmart, Target, Big W sometimes. The Shopify stores (JB Hi-Fi, Zing, Toymate) will always work.

**Telegram errors (401 Unauthorized)**
→ Your `TELEGRAM_BOT_TOKEN` secret is wrong. Double-check it in Settings → Secrets.

**Telegram errors (400 Bad Request)**
→ Your `TELEGRAM_CHAT_ID` secret is wrong. Re-follow the getUpdates step.

**No notifications after restocks**
→ The state.json may have been lost. Delete it from the repo and the monitor will rebuild it.

---

## 📊 Reliability Expectations

| Retailer | Method | Reliability |
|---|---|---|
| JB Hi-Fi | Shopify API | ⭐⭐⭐⭐⭐ Excellent |
| Zing | Shopify API | ⭐⭐⭐⭐⭐ Excellent |
| Toymate | Shopify API | ⭐⭐⭐⭐⭐ Excellent |
| EB Games | HTML | ⭐⭐⭐⭐ Good |
| Amazon AU | HTML | ⭐⭐⭐ OK (may get blocked occasionally) |
| Target AU | HTML | ⭐⭐⭐ OK (JS-heavy site) |
| Kmart | HTML | ⭐⭐⭐ OK (JS-heavy site) |
| Big W | HTML | ⭐⭐⭐ OK (JS-heavy site) |
