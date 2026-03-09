# 🔗 LinkedIn Lead Export Automation

> Extract LinkedIn profiles by category, enrich them with verified work emails, and export business-ready lead lists in CSV and Excel formats.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Scraping-green?logo=playwright)](https://playwright.dev)
[![PeopleDataLabs](https://img.shields.io/badge/API-PeopleDataLabs-orange)](https://www.peopledatalabs.com/)
[![AnymailFinder](https://img.shields.io/badge/API-AnymailFinder-purple)](https://newapp.anymailfinder.com)

---

## 🧠 Which Mode Should You Use?

| Use Case | Recommended Mode |
|---|---|
| Quick small list | 🖥️ Browser Mode |
| Large lists (100+) | ⚡ API Mode |
| No LinkedIn login | ⚡ API Mode |
| Advanced filters | ⚡ API Mode |
| Highest speed | ⚡ API Mode |

---

## 📦 Installation & Setup

### 1. Create a virtual environment

```bash
cd /path/to/project
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set up API keys

Create a `.env` file in the project root:

```env
ANYMAIL_API_KEY=your_anymailfinder_api_key_here
PROXYCURL_API_KEY=your_proxycurl_api_key_here
```

> 🔑 Get your keys:
> - **Proxycurl** → [nubela.co/proxycurl](https://nubela.co/proxycurl/)
> - **AnymailFinder** → [newapp.anymailfinder.com/settings/api](https://newapp.anymailfinder.com/settings/api)

---

## 🖥️ Mode 1 — Browser Automation (Playwright)

Uses LinkedIn search pages + browser scraping.

### First-Time Login (One-Time Setup)

Save your LinkedIn session so scripts can reuse it without re-authenticating:

```bash
python browser_login.py
```

**Steps:**
1. A browser window opens
2. Log in to LinkedIn
3. Wait until the home/feed page loads
4. Return to the terminal and press **ENTER**

This creates a session file: `.pw-session.json`

> ⚠️ Install Playwright browsers if not already done:
> ```bash
> playwright install
> ```

---

### 🚀 Generate Leads (Browser Mode)

**Using a preset category:**

```bash
python export_leads.py --category ai_influencers --limit 200
```

**Available preset categories:**

| Category | Description |
|---|---|
| `ai_influencers` | AI thought leaders & influencers |
| `engineering_leaders` | Engineering VPs, Directors, CTOs |
| `architects` | Solution & Software Architects |
| `ld_heads` | Heads of L&D / Learning & Development |

**Using custom keywords:**

```bash
python export_leads.py --category "AI Researcher India" --limit 150
```

---

### ⚙️ Browser Workflow

```
LinkedIn Search → Profile Scraping → Email Enrichment → Lead Export
```

### 📊 Data Fields Captured

| Field | Description |
|---|---|
| Full Name | Candidate's full name |
| Professional Headline | LinkedIn headline |
| Location | City / Region |
| LinkedIn Profile URL | Direct profile link |
| Verified Work Email | Enriched via AnymailFinder |
| Email Verification Status | Confidence of email match |

---

## ⚡ Mode 2 — API Mode (Proxycurl + AnymailFinder)

Uses APIs instead of browser scraping. **5–10x faster, no LinkedIn login required.**

✅ Faster & more scalable  
✅ No LinkedIn login needed  
✅ Richer company & industry data  
✅ Advanced filtering support  

---

### 🚀 Generate Leads (API Mode)

**Using a preset category:**

```bash
python export_leads_api.py --category ai_influencers --limit 200
```

**Using custom keywords:**

```bash
python export_leads_api.py --keywords "AI Healthcare Robotics" --limit 150
```

---

### 🎛️ Filters & Options

#### 🌍 Location Filters
```bash
--country IN
--city Bangalore
```

#### 👔 People Filters
```bash
--seniority director
--job-title "Head of Engineering"
```

#### 🏢 Company Filters
```bash
--industry "Information Technology"
--company-size-min 200
--company-size-max 5000
--revenue-min 1000000
--public-only
```

---

### 🔥 Full Example

```bash
python export_leads_api.py \
  --keywords "AI Platform" \
  --country US \
  --seniority director \
  --industry "Computer Software" \
  --company-size-min 500 \
  --revenue-min 10000000 \
  --limit 300
```

---

### ⚙️ API Workflow

```
Keyword Search → Profile API → Email Enrichment → Lead Export
```

### 📊 API Data Fields Captured

| Field | Description |
|---|---|
| Full Name | Candidate's full name |
| Professional Headline | LinkedIn headline |
| Location (Country) | Country of residence |
| Company | Current employer |
| Industry | Company industry |
| Company Size | Number of employees |
| Revenue | Estimated company revenue |
| LinkedIn Profile URL | Direct profile link |
| Verified Work Email | Enriched via AnymailFinder |
| Email Verification Status | Confidence of email match |

---

## 📁 Output

All exports are saved to the `/data` directory in two formats:

| Format | Description |
|---|---|
| `.csv` | Universal spreadsheet format |
| `.xlsx` | Excel-ready format with formatting |

---

## 🚨 Troubleshooting

| Issue | Fix |
|---|---|
| Missing modules | `source venv/bin/activate && pip install -r requirements.txt` |
| Playwright browser issue | `playwright install` |
| Lost LinkedIn session | `python browser_login.py` |
| API not working | Check `.env` keys and ensure billing is active on the APIs |

---

## 🔒 Security & Best Practices

Add these to your `.gitignore` — **never commit them:**

```gitignore
venv/
.pw-session.json
.env
data/
```

> ℹ️ If LinkedIn updates its UI, browser scraping selectors may need manual updates. API mode is more stable for long-term production use.

---

## ✉️ Email Enrichment

Verified work emails are fetched using the **AnymailFinder API**. Each email result includes a confidence/verification status so you can filter by match quality before outreach.
