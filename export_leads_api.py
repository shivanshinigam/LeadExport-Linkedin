import os
import csv
import time
import argparse
from datetime import datetime
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv
from anymailfinder_client import AnymailFinderClient

# SETUP
load_dotenv()

PDL_API_KEY = os.getenv("PDL_API_KEY")
PDL_URL = "https://api.peopledatalabs.com/v5/person/search"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

email_client = AnymailFinderClient()

#  PRESET CATEGORIES 
CATEGORY_MAP = {
    "ai_influencers": 'job_title:("AI" OR "Machine Learning" OR "GenAI" OR "Data Engineering" OR "MLOps")',
    "engineering_leaders": 'job_title:("VP Engineering" OR "Director Engineering" OR "Head Engineering")',
    "architects": 'job_title:("Software Architect" OR "Solutions Architect" OR "Enterprise Architect")',
    "ld_heads": 'job_title:("Head Learning" OR "L&D" OR "Training Head" OR "Talent Development")',
}

#  FILTER BUILDER 

def build_query(args):
    filters = []

    # Keywords
    if args.keywords:
        filters.append(f'job_title:("{args.keywords}")')

    # Location filters
    if args.country:
        filters.append(f'location_country:"{args.country}"')

    if args.city:
        filters.append(f'location_locality:"{args.city}"')

    # Seniority
    if args.seniority:
        filters.append(f'job_seniority:"{args.seniority}"')

    # Company filters
    if args.company:
        filters.append(f'job_company_name:"{args.company}"')

    if args.industry:
        filters.append(f'job_company_industry:"{args.industry}"')

    if args.company_size_min:
        filters.append(f'job_company_size:>={args.company_size_min}')

    if args.company_size_max:
        filters.append(f'job_company_size:<={args.company_size_max}')

    return " AND ".join(filters)

#  SEARCH 

def search_people(args):
    print("\n🔎 Searching via People Data Labs API...")

    query = build_query(args)

    headers = {
        "X-Api-Key": PDL_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "query": {"bool": {"must": [{"query_string": {"query": query}}]}},
        "size": min(args.limit, 100),
    }

    urls = []

    try:
        r = requests.post(PDL_URL, headers=headers, json=payload, timeout=30)
        data = r.json()

        for person in data.get("data", []):
            linkedin = person.get("linkedin_url")
            if linkedin:
                urls.append(linkedin)

    except Exception as e:
        print("⚠ Search failed:", e)

    return list(dict.fromkeys(urls))[: args.limit]

#  PROFILE ENRICH 

def enrich_profile(url):
    profile = {
        "Name": "",
        "Headline": "",
        "Location": "",
        "Company": "",
        "Industry": "",
        "Company Size": "",
        "Profile URL": url,
        "Email": "",
        "Email Status": "",
    }

    # PDL enrichment
    try:
        headers = {"X-Api-Key": PDL_API_KEY}
        r = requests.get(
            "https://api.peopledatalabs.com/v5/person/enrich",
            headers=headers,
            params={"profile": url},
            timeout=30,
        )
        data = r.json()

        profile["Name"] = data.get("full_name", "")
        profile["Headline"] = data.get("job_title", "")
        profile["Location"] = data.get("location_country", "")

        job = data.get("job_company", {})
        profile["Company"] = job.get("name", "")
        profile["Industry"] = job.get("industry", "")
        profile["Company Size"] = job.get("size", "")

    except Exception:
        print("   ⚠ Profile enrich failed")

    # Email enrichment
    try:
        email_data = email_client.find_email_by_linkedin(url)
        if email_data:
            profile["Email"] = email_data.get("email", "")
            profile["Email Status"] = email_data.get("email_status", "")
    except Exception:
        print("   ⚠ Email fetch failed")

    return profile

#  MAIN 

def main():
    parser = argparse.ArgumentParser(description="🚀 LinkedIn Lead Engine — API Only (PDL)")
    parser.add_argument("--category", help="Preset category")
    parser.add_argument("--keywords", help="Custom keywords")
    parser.add_argument("--limit", type=int, default=100)

    # Filters
    parser.add_argument("--country")
    parser.add_argument("--city")
    parser.add_argument("--seniority")
    parser.add_argument("--company")
    parser.add_argument("--industry")
    parser.add_argument("--company-size-min", type=int)
    parser.add_argument("--company-size-max", type=int)

    args = parser.parse_args()

    # Category logic
    if args.category:
        key = args.category.lower()
        if key in CATEGORY_MAP:
            args.keywords = CATEGORY_MAP[key]
            print(f"📂 Using preset category: {key}")

    if not args.keywords:
        print("❌ Provide --keywords or --category")
        return

    # SEARCH
    links = search_people(args)
    print(f"✅ Found {len(links)} profiles")

    # ENRICH
    results = []
    for i, url in enumerate(links, 1):
        print(f"   {i}/{len(links)}")
        results.append(enrich_profile(url))
        time.sleep(0.2)

    # EXPORT
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = DATA_DIR / f"linkedin_leads_api_{ts}.csv"
    xlsx_path = DATA_DIR / f"linkedin_leads_api_{ts}.xlsx"

    headers = list(results[0].keys()) if results else []

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    pd.DataFrame(results).to_excel(xlsx_path, index=False)

    print("\n🎉 Done!")
    print(f"📄 CSV:   {csv_path}")
    print(f"📊 Excel: {xlsx_path}")


if __name__ == "__main__":
    main()
