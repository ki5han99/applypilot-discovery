import sys, re, requests, sqlite3
from datetime import datetime, timezone

DB = "/Users/sainandakishanedimadakala/.applypilot/applypilot.db"

# Candidate Ashby-hosted companies (board token = url slug in jobs.ashbyhq.com/<slug>).
CANDIDATES = [
    "regard", "vytalize-health", "CodaMetrix", "midnite", "facilityos",
    "relationrx",
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
        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
        try:
            r = requests.get(url, timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        try:
            data = r.json()
        except ValueError:
            continue
        jobs = data.get("jobs", [])
        if not jobs:
            continue
        matched = [j for j in jobs if matches(j.get("title", ""))]
        if not matched:
            continue
        found_companies.append((slug, len(jobs), len(matched)))
        for j in matched:
            job_url = j.get("jobUrl") or j.get("applyUrl")
            title = j.get("title")
            location = j.get("location", "")
            content = re.sub(r"<[^>]+>", " ", j.get("descriptionHtml") or "")
            content = re.sub(r"\s+", " ", content).strip()
            try:
                con.execute(
                    "INSERT INTO jobs (url, title, salary, description, location, site, "
                    "strategy, discovered_at, full_description, application_url, detail_scraped_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (job_url, title, None, content[:500], location, slug,
                     "ashby_api", now, content, job_url, now),
                )
                total_new += 1
            except sqlite3.IntegrityError:
                pass
        con.commit()
    print(f"Companies with matches: {found_companies}")
    print(f"Total new jobs inserted: {total_new}")

if __name__ == "__main__":
    main()
