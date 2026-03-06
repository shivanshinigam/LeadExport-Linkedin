import asyncio
import csv
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from playwright.async_api import async_playwright
from anymailfinder_client import AnymailFinderClient
from dotenv import load_dotenv

# ================== SETUP ==================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SESSION_FILE = ".pw-session.json"

# 🔐 Load Anymail API
load_dotenv()
email_client = AnymailFinderClient()

# 🎯 Preset categories
CATEGORY_MAP = {
    "ai_influencers": "AI Researcher OR Machine Learning Engineer OR GenAI OR Data Engineering OR MLOps",
    "engineering_leaders": "VP Engineering OR Director of Engineering OR Head of Engineering OR Principal Engineer",
    "architects": "Software Architect OR Solutions Architect OR Enterprise Architect OR Technical Architect",
    "ld_heads": "Head of Learning and Development OR L&D Head OR Training Head OR Talent Development",
}

# ================== HELPERS ==================

async def auto_scroll(page):
    for _ in range(12):
        await page.mouse.wheel(0, 3000)
        await page.wait_for_timeout(1200)


async def collect_profile_links(page, limit):
    anchors = await page.query_selector_all("a")
    links = set()

    for a in anchors:
        href = await a.get_attribute("href")
        if not href:
            continue
        if href.startswith("/"):
            href = "https://www.linkedin.com" + href
        if "/in/" in href:
            href = href.split("?")[0]
            links.add(href)

    return list(links)[:limit]


async def scrape_profile(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
    except:
        print(f"⚠️ Skipping slow profile: {url}")
        return None

    name = ""
    headline = ""
    location = ""

    try:
        h1 = await page.query_selector("h1")
        if h1:
            name = (await h1.text_content() or "").strip()
    except:
        pass

    try:
        h2 = await page.query_selector("h2")
        if h2:
            headline = (await h2.text_content() or "").strip()
    except:
        pass

    try:
        loc = await page.query_selector(
            "span.text-body-small.inline.t-black--light.break-words"
        )
        if loc:
            location = (await loc.text_content() or "").strip()
    except:
        pass

    # ================= EMAIL ENRICHMENT =================
    profile = {
        "Name": name,
        "Headline": headline,
        "Location": location,
        "Profile URL": url,
        "Email": "",
        "Email Status": "",
    }

    try:
        email_data = email_client.find_email_by_linkedin(url)
        if email_data:
            profile["Email"] = email_data.get("email", "")
            profile["Email Status"] = email_data.get("email_status", "")
    except Exception:
        print("      ⚠ Email fetch failed")

    return profile


# ================== MAIN ==================

async def main():
    parser = argparse.ArgumentParser(description="LinkedIn Lead Export Tool")
    parser.add_argument(
        "--category", required=True, help="Preset category key OR custom keywords"
    )
    parser.add_argument(
        "--limit", type=int, default=200, help="Max profiles to export"
    )
    args = parser.parse_args()

    category_key = args.category.lower().strip()
    max_profiles = args.limit

    if category_key in CATEGORY_MAP:
        search_keywords = CATEGORY_MAP[category_key]
        print(f"📂 Using preset category: {category_key}")
    else:
        search_keywords = args.category
        print(f"🔎 Using custom keywords: {search_keywords}")

    search_url = (
        f"https://www.linkedin.com/search/results/people/?keywords={quote(search_keywords)}"
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()

        print("\n🔎 Opening LinkedIn search...")
        await page.goto(search_url)
        await page.wait_for_timeout(3000)

        await auto_scroll(page)
        links = await collect_profile_links(page, max_profiles)

        print(f"✅ Found {len(links)} profiles. Scraping...")

        results = []
        for i, link in enumerate(links, 1):
            print(f"   {i}/{len(links)}")
            profile = await scrape_profile(page, link)
            if profile:
                results.append(profile)

        await browser.close()

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # ================= CSV EXPORT =================
    csv_path = DATA_DIR / f"linkedin_leads_{ts}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Name",
                "Headline",
                "Location",
                "Profile URL",
                "Email",
                "Email Status",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    # ================= EXCEL EXPORT =================
    xlsx_path = DATA_DIR / f"linkedin_leads_{ts}.xlsx"
    df = pd.DataFrame(results)
    df.to_excel(xlsx_path, index=False)

    print(f"\n🎉 Done!")
    print(f"📄 CSV:   {csv_path}")
    print(f"📊 Excel: {xlsx_path}")


if __name__ == "__main__":
    asyncio.run(main())