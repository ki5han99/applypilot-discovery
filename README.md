# applypilot-discovery

A small script to discover job postings from Greenhouse-hosted company career boards, filtered by role keywords, and load them into an [ApplyPilot](https://github.com/) job-search pipeline database.

Uses Greenhouse's public JSON API (`https://boards-api.greenhouse.io/v1/boards/{company}/jobs`) directly instead of scraping aggregator job boards — faster, more reliable, and avoids CAPTCHA/rate-limit blocks common on sites like Indeed or LinkedIn.

## Usage

Edit `CANDIDATES` (company board slugs) and `KEYWORDS` (role title filters) in `gh_discover.py`, then run:

```bash
python3 gh_discover.py
```

New matching jobs are inserted into the ApplyPilot SQLite database at `~/.applypilot/applypilot.db`.
