import sys, re, requests, sqlite3
from datetime import datetime, timezone

DB = "/Users/sainandakishanedimadakala/.applypilot/applypilot.db"

# Candidate Greenhouse-hosted companies (board token = url slug).
# Mix of fintech / enterprise / healthcare / gaming-adjacent tech, avoiding known Workday shops.
CANDIDATES = [
    # Third batch -- companies not yet tried
    "lyft", "pinterest2", "yelp", "eventbrite", "thumbtack", "nextdoor",
    "patreon", "substack", "medium", "quora", "houseparty", "cameo",
    "whatnot", "faire2", "chewy", "wayfair", "etsy", "poshmark", "stitchfix",
    "grubhub", "postmates", "gopuff", "getir", "flexport2", "shippo",
    "convoy", "samsara2", "motive", "veho", "loadsmart", "flock-safety",
    "verkada", "arlo", "ring", "wyze", "nest", "sonos2", "roku",
    "plex", "trulia", "zillow", "opendoor", "compass", "redfin",
    "carvana", "vroom", "shift", "turo", "getaround", "outdoorsy",
    "workato", "n8n", "make", "tray", "boomi", "celonis", "uipath",
    "automationanywhere", "pega", "appian", "servicenow2", "freshworks",
    "front", "helpscout", "kustomer", "gladly", "assemblyai", "deepgram",
    "speechmatics", "voiceflow", "rasa", "dialpad", "aircall", "gong2",
    "chorus", "clari2", "highspot", "seismic", "mediafly", "showpad",
]

KEYWORDS = [
    "data engineer", "forward deployed", "analytics engineer",
    "sr. analytics engineer", "senior analytics engineer",
    "senior data engineer", "sr. data engineer", "sr data engineer",
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
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
        try:
            r = requests.get(url, timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        data = r.json()
        jobs = data.get("jobs", [])
        if not jobs:
            continue
        matched = [j for j in jobs if matches(j.get("title", ""))]
        if not matched:
            continue
        found_companies.append((slug, len(jobs), len(matched)))
        for j in matched:
            job_url = j.get("absolute_url")
            title = j.get("title")
            location = (j.get("location") or {}).get("name", "")
            content = re.sub(r"<[^>]+>", " ", j.get("content", "") or "")
            content = re.sub(r"\s+", " ", content).strip()
            try:
                con.execute(
                    "INSERT INTO jobs (url, title, salary, description, location, site, "
                    "strategy, discovered_at, full_description, application_url, detail_scraped_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (job_url, title, None, content[:500], location, slug,
                     "greenhouse_api", now, content, job_url, now),
                )
                total_new += 1
            except sqlite3.IntegrityError:
                pass
        con.commit()
    print(f"Companies with matches: {found_companies}")
    print(f"Total new jobs inserted: {total_new}")

if __name__ == "__main__":
    main()
