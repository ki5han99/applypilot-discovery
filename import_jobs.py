import json, sqlite3, sys
from pathlib import Path

DB = "/Users/sainandakishanedimadakala/.applypilot/applypilot.db"
JOBS_FILE = Path(__file__).parent / "jobs_found.json"

def main():
    jobs = json.loads(JOBS_FILE.read_text())
    con = sqlite3.connect(DB)
    inserted = 0
    for j in jobs:
        try:
            con.execute(
                "INSERT INTO jobs (url, title, salary, description, location, site, "
                "strategy, discovered_at, full_description, application_url, detail_scraped_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (j["url"], j["title"], None, j["full_description"][:500], j["location"],
                 j["site"], j["strategy"], j["discovered_at"], j["full_description"],
                 j["application_url"], j["discovered_at"]),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    con.commit()
    print(f"Imported {inserted} new jobs out of {len(jobs)} in {JOBS_FILE.name}")

if __name__ == "__main__":
    main()
