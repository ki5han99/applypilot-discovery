import sys, re, requests, sqlite3
from datetime import datetime, timezone

DB = "/Users/sainandakishanedimadakala/.applypilot/applypilot.db"

# Candidate Lever-hosted companies (board token = url slug in jobs.lever.co/<slug>).
CANDIDATES = [
    "neighbor", "BDG", "jobgether", "hhaexchange", "versapay", "aircall",
    "redhorsecorp", "finix",
    # Second batch
    "analyticpartners", "civitech", "loopreturns", "aledade", "regal.ai",
    "metabase", "Coda", "alimentiv-2", "sugarcrm", "wgsn",
    "terawattinfrastructure", "massive-rocket", "windfalldata", "resilinc",
    # Third batch
    "whoop", "pattern",
]

KEYWORDS = [
    "data engineer", "forward deployed", "analytics engineer",
    "sr. analytics engineer", "senior analytics engineer",
    "senior data engineer", "sr. data engineer", "sr data engineer",
    "data platform engineer", "business intelligence engineer",
    "bi engineer", "data infrastructure engineer",
]

def matches(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)

def main():
    con = sqlite3.connect(DB)
    now = datetime.now(timezone.utc).isoformat()
    total_new = 0
    found_companies = []
    for slug in CANDIDATES:
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        try:
            r = requests.get(url, timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        try:
            jobs = r.json()
        except ValueError:
            continue
        if not isinstance(jobs, list) or not jobs:
            continue
        matched = [j for j in jobs if matches(j.get("text", ""))]
        if not matched:
            continue
        found_companies.append((slug, len(jobs), len(matched)))
        for j in matched:
            job_url = j.get("hostedUrl") or j.get("applyUrl")
            title = j.get("text")
            location = (j.get("categories") or {}).get("location", "")
            content = re.sub(r"<[^>]+>", " ", j.get("descriptionPlain") or j.get("description") or "")
            content = re.sub(r"\s+", " ", content).strip()
            try:
                con.execute(
                    "INSERT INTO jobs (url, title, salary, description, location, site, "
                    "strategy, discovered_at, full_description, application_url, detail_scraped_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (job_url, title, None, content[:500], location, slug,
                     "lever_api", now, content, job_url, now),
                )
                total_new += 1
            except sqlite3.IntegrityError:
                pass
        con.commit()
    print(f"Companies with matches: {found_companies}")
    print(f"Total new jobs inserted: {total_new}")

if __name__ == "__main__":
    main()
