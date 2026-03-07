import os
import csv
import time
import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from proxycurl import Proxycurl
from anymailfinder_client import AnymailFinderClient

# ================== SETUP ==================
load_dotenv()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

proxycurl = Proxycurl(api_key=os.getenv("PROXYCURL_API_KEY"))
email_client = AnymailFinderClient()

# ================== PRESET CATEGORIES ==================
CATEGORY_MAP = {
    "ai_influencers": "AI OR Machine Learning OR GenAI OR Data Engineering OR MLOps",
    "engineering_leaders": "VP Engineering OR Director Engineering OR Head Engineering",
    "architects": "Software Architect OR Solutions Architect OR Enterprise Architect",
    "ld_heads": "Head Learning Development OR L&D OR Training Head OR Talent Development",
}

# ================== FILTER ENGINE ==================

def build_search_params(args):
    params = {
        "keyword": args.keywords,
        "page_size": min(args.limit, 100),
        "enrich_profiles": False,
    }

    if args.country:
        params["country"] = args.country.upper()

    if args.city:
        params["city"] = args.city

    if args.seniority:
        params["seniority"] = args.seniority.lower()

    if args.job_title:
        params["job_title"] = args.job_title

    if args.company:
        params["company"] = args.company

    if args.industry:
        params["industry"] = args.industry

    if args.company_size_min or args.company_size_max:
        params["company_size_min"] = args.company_size_min
        params["company_size_max"] = args.company_size_max

    if args.revenue_min or args.revenue_max:
        params["revenue_min"] = args.revenue_min
        params["revenue_max"] = args.revenue_max

    if args.public_only:
        params["public_company_only"] = True

    return params


# ================== SEARCH ==================

def search_people(args):
    print("\n🔎 Searching via Proxycurl API...")
    urls = []

    params = build_search_params(args)

    try:
        resp = proxycurl.linkedin.person.search(**params)
        profiles = resp.get("profiles", [])

        for p in profiles:
            url = p.get("linkedin_profile_url")
            if url:
                urls.append(url)

    except Exception as e:
        print("⚠ Search failed:", e)

    # Deduplicate
    urls = list(dict.fromkeys(urls))
    return urls[: args.limit]


# ================== PROFILE ENRICH ==================

def enrich_profile(url):
    profile = {
        "Name": "",
        "Headline": "",
        "Location": "",
        "Company": "",
        "Industry": "",
        "Company Size": "",
        "Revenue": "",
        "Profile URL": url,
        "Email": "",
        "Email Status": "",
    }

    try:
        data = proxycurl.linkedin.person.get(
            linkedin_profile_url=url,
            use_cache=True,
        )

        profile["Name"] = data.get("full_name", "")
        profile["Headline"] = data.get("occupation", "")
        profile["Location"] = data.get("country_full_name", "")

        if data.get("experiences"):
            exp = data["experiences"][0]
            profile["Company"] = exp.get("company", "")
            profile["Industry"] = exp.get("company_industry", "")
            profile["Company Size"] = exp.get("company_employee_count_range", "")
            profile["Revenue"] = exp.get("company_annual_revenue", "")

    except Exception:
        print("   ⚠ Profile fetch failed")

    # Email enrichment
    try:
        email_data = email_client.find_email_by_linkedin(url)
        if email_data:
            profile["Email"] = email_data.get("email", "")
            profile["Email Status"] = email_data.get("email_status", "")
    except Exception:
        print("   ⚠ Email fetch failed")

    return profile


# ================== MAIN ==================

def main():
    parser = argparse.ArgumentParser(
        description="🚀 LinkedIn Lead Engine — API Only (Advanced Filters)"
    )

    # Core
    parser.add_argument("--category", help="Preset category")
    parser.add_argument("--keywords", help="Custom search keywords")
    parser.add_argument("--limit", type=int, default=100)

    # People filters
    parser.add_argument("--country", help="Country code (IN, US, GB)")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--job-title", help="Job title keyword")
    parser.add_argument("--seniority", help="senior / manager / director / vp / cxo")

    # Company filters
    parser.add_argument("--company", help="Company keyword")
    parser.add_argument("--industry", help="Industry name")
    parser.add_argument("--company-size-min", type=int)
    parser.add_argument("--company-size-max", type=int)
    parser.add_argument("--revenue-min", type=int)
    parser.add_argument("--revenue-max", type=int)
    parser.add_argument("--public-only", action="store_true")

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
    csv_path = DATA_DIR / f"linkedin_leads_{ts}.csv"
    xlsx_path = DATA_DIR / f"linkedin_leads_{ts}.xlsx"

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