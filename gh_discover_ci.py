import json, re, requests
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
COMPANIES_FILE = HERE / "companies.txt"
OUT_FILE = HERE / "jobs_found.json"

KEYWORDS = [
    "data engineer", "forward deployed", "analytics engineer",
    "sr. analytics engineer", "senior analytics engineer",
    "senior data engineer", "sr. data engineer", "sr data engineer",
]

def matches(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)

def main():
    candidates = [
        line.strip() for line in COMPANIES_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    now = datetime.now(timezone.utc).isoformat()
    found = []
    summary = []
    for slug in candidates:
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
        try:
            r = requests.get(url, timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        jobs = r.json().get("jobs", [])
        matched = [j for j in jobs if matches(j.get("title", ""))]
        if not matched:
            continue
        summary.append((slug, len(jobs), len(matched)))
        for j in matched:
            content = re.sub(r"<[^>]+>", " ", j.get("content", "") or "")
            content = re.sub(r"\s+", " ", content).strip()
            found.append({
                "url": j.get("absolute_url"),
                "title": j.get("title"),
                "location": (j.get("location") or {}).get("name", ""),
                "site": slug,
                "strategy": "greenhouse_api",
                "discovered_at": now,
                "full_description": content,
                "application_url": j.get("absolute_url"),
            })
    OUT_FILE.write_text(json.dumps(found, indent=2))
    print(f"Companies with matches: {summary}")
    print(f"Total jobs found: {len(found)} -> {OUT_FILE}")

if __name__ == "__main__":
    main()
