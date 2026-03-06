# LinkedIn Lead Export Automation

## Overview

This tool extracts LinkedIn profiles by category, enriches them with verified work emails (via AnymailFinder), and exports business-ready lead lists in CSV and Excel formats.

Designed for business and sales teams with simple command-based usage.

---

## 🔐 First-Time Setup (One-Time Login)

You must log into LinkedIn once to save your Playwright session state. This lets the scripts reuse your authenticated session without re-login.

### Step 1 — Save LinkedIn Session

Run the browser login helper which opens a browser window for you to sign in and then saves a session file:

```bash
python browser_login.py
```

A browser window will open. Steps:
- Log in to your LinkedIn account.
- Wait until the LinkedIn home/feed page fully loads.
- Return to the terminal and press ENTER to save the session.

This creates:

- `.pw-session.json`

---

## 🚀 Generate Leads

Using a preset category (recommended):

```bash
python export_leads.py --category ai_influencers --limit 200
```

Available preset categories (keys):
- `ai_influencers`
- `engineering_leaders`
- `architects`
- `ld_heads`

Using custom keywords:

```bash
python export_leads.py --category "AI Researcher India" --limit 150
```

### ⚙️ Workflow
LinkedIn Search → Profile Scraping → Email Enrichment → Lead Export

### 📊 Data Fields Captured
- Full Name
- Professional Headline
- Location
- LinkedIn Profile URL
- Verified Work Email
- Email Verification Status

### 📁 Output Files
- CSV export
- Excel (.xlsx) export

Files are saved in:

```
/data
```

---

## ✉️ Email Enrichment

This project integrates with the AnymailFinder API to fetch verified work emails using LinkedIn profile URLs.

Set your AnymailFinder API key in an environment variable (recommended) or a `.env` file used by `python-dotenv`.

Example `.env`:

```
ANYMAILFINDER_API_KEY=your_anymailfinder_api_key_here
PROXYCURL_API_KEY=your_proxycurl_api_key_here
```

(The project already contains `requirements.txt` listing `python-dotenv` if you want to load a `.env` file.)

---

## Installation & Local Setup

1. Create a Python virtual environment (recommended):

```bash
cd /path/to/leadgen-proxycurl
python3 -m venv venv
source venv/bin/activate
```

2. Upgrade pip and install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. If you plan to run Playwright locally, install browsers once:

```bash
playwright install
```

4. Save your LinkedIn session as described above with `browser_login.py`.

5. Run the exporter:

```bash
python export_leads.py --category ai_influencers --limit 200
```

---

## Notes & Recommendations

- Do NOT commit your `venv/` directory or `.pw-session.json` to git. A `.gitignore` is included to prevent this.
- The repository already includes `requirements.txt`. If you add packages, update that file and re-run `pip install -r requirements.txt`.
- Playwright-based scraping interacts with LinkedIn pages and may break if LinkedIn changes its layout. Tweak selectors in `export_leads.py` if needed.

---

## Troubleshooting

- If the script complains about missing modules, ensure your virtualenv is active and packages are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

- If Playwright cannot open a browser, run:

```bash
playwright install
```

- If you lose `.pw-session.json`, re-run `browser_login.py` to regenerate it.

---
