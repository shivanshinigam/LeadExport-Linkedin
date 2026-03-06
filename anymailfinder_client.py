import time
import requests
from config import ANYMAIL_API_KEY, ENDPOINTS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY


class AnymailFinderClient:

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ANYMAIL_API_KEY
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        self.stats = {
            "requests_made": 0,
            "emails_found": 0,
            "emails_not_found": 0,
            "errors": 0,
        }

    def find_decision_maker(self, domain: str = None, company_name: str = None,
                            categories: list = None) -> list:
        if not domain and not company_name:
            return []
        if not categories:
            categories = ["ceo"]

        results = []
        for category in categories:
            payload = {"decision_maker_category": [category]}
            if domain:
                payload["domain"] = domain
            if company_name:
                payload["company_name"] = company_name

            response = self._make_request("decision_maker", payload)
            if response:
                lead = self._normalize_decision_maker_response(response, domain or company_name, category)
                if lead:
                    results.append(lead)

        return results

    def find_person_email(self, full_name: str = None, first_name: str = None,
                          last_name: str = None, domain: str = None,
                          company_name: str = None) -> dict:
        payload = {}
        if full_name:
            payload["full_name"] = full_name
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if domain:
            payload["domain"] = domain
        if company_name:
            payload["company_name"] = company_name

        has_name = full_name or (first_name and last_name)
        has_company = domain or company_name
        if not has_name or not has_company:
            return None

        response = self._make_request("person", payload)
        if response:
            return self._normalize_person_response(response, domain or company_name)
        return None

    def find_company_emails(self, domain: str = None, company_name: str = None) -> list:
        if not domain and not company_name:
            return []

        payload = {}
        if domain:
            payload["domain"] = domain
        if company_name:
            payload["company_name"] = company_name

        response = self._make_request("company", payload)
        if response and isinstance(response, dict):
            return self._normalize_company_response(response, domain or company_name)
        return []

    def find_email_by_linkedin(self, linkedin_url: str) -> dict:
        if not linkedin_url:
            return None

        payload = {"linkedin_url": linkedin_url}
        response = self._make_request("linkedin_url", payload)
        if response:
            return self._normalize_linkedin_response(response, linkedin_url)
        return None

    def _make_request(self, endpoint_key: str, payload: dict) -> dict:
        url = ENDPOINTS[endpoint_key]

        for attempt in range(MAX_RETRIES + 1):
            try:
                self.stats["requests_made"] += 1
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print(f"    ⚠ Authentication failed. Check your API key.")
                    self.stats["errors"] += 1
                    return None
                elif response.status_code == 422:
                    print(f"    ⚠ Invalid request parameters: {payload}")
                    self.stats["errors"] += 1
                    return None
                elif response.status_code == 429:
                    print(f"    ⚠ Rate limited. Waiting {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    print(f"    ⚠ API returned status {response.status_code}")
                    self.stats["errors"] += 1
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY)
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"    ⚠ Request timed out (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue
                self.stats["errors"] += 1
                return None

            except requests.exceptions.RequestException as e:
                print(f"    ⚠ Request error: {e}")
                self.stats["errors"] += 1
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue
                return None

        return None

    def _normalize_decision_maker_response(self, response: dict, company: str, category: str) -> dict:
        email = response.get("email") or response.get("valid_email")
        email_status = response.get("email_status", "unknown")

        if email:
            self.stats["emails_found"] += 1
        else:
            self.stats["emails_not_found"] += 1

        return {
            "full_name": response.get("person_full_name", ""),
            "job_title": response.get("person_job_title", ""),
            "company": company,
            "email": email or "",
            "email_status": email_status,
            "linkedin_url": response.get("person_linkedin_url", ""),
            "source": "decision_maker",
            "category": category,
        }

    def _normalize_person_response(self, response: dict, company: str) -> dict:
        email = response.get("email") or response.get("valid_email")
        email_status = response.get("email_status", "unknown")

        if email:
            self.stats["emails_found"] += 1
        else:
            self.stats["emails_not_found"] += 1

        return {
            "full_name": response.get("person_full_name", ""),
            "job_title": response.get("person_job_title", ""),
            "company": company,
            "email": email or "",
            "email_status": email_status,
            "linkedin_url": response.get("person_linkedin_url", ""),
            "source": "person",
            "category": "",
        }

    def _normalize_company_response(self, response: dict, company: str) -> list:
        leads = []
        emails_data = response.get("emails", [])

        if isinstance(emails_data, list):
            for entry in emails_data:
                email = entry if isinstance(entry, str) else entry.get("email", "")
                email_status = "valid" if isinstance(entry, str) else entry.get("email_status", "unknown")
                if email:
                    self.stats["emails_found"] += 1
                    leads.append({
                        "full_name": entry.get("person_full_name", "") if isinstance(entry, dict) else "",
                        "job_title": entry.get("person_job_title", "") if isinstance(entry, dict) else "",
                        "company": company,
                        "email": email,
                        "email_status": email_status,
                        "linkedin_url": "",
                        "source": "company",
                        "category": "",
                    })
        elif response.get("email"):
            email = response.get("email")
            self.stats["emails_found"] += 1
            leads.append({
                "full_name": response.get("person_full_name", ""),
                "job_title": response.get("person_job_title", ""),
                "company": company,
                "email": email,
                "email_status": response.get("email_status", "unknown"),
                "linkedin_url": "",
                "source": "company",
                "category": "",
            })

        if not leads:
            self.stats["emails_not_found"] += 1

        return leads

    def _normalize_linkedin_response(self, response: dict, linkedin_url: str) -> dict:
        email = response.get("email") or response.get("valid_email")
        email_status = response.get("email_status", "unknown")

        if email:
            self.stats["emails_found"] += 1
        else:
            self.stats["emails_not_found"] += 1

        return {
            "full_name": response.get("person_full_name", ""),
            "job_title": response.get("person_job_title", ""),
            "company": response.get("person_company_name", ""),
            "email": email or "",
            "email_status": email_status,
            "linkedin_url": linkedin_url,
            "source": "linkedin_url",
            "category": "",
        }

    def get_stats(self) -> dict:
        return self.stats.copy()