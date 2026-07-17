import sys, re, requests, sqlite3
from datetime import datetime, timezone

DB = "/Users/sainandakishanedimadakala/.applypilot/applypilot.db"

# Candidate Greenhouse-hosted companies (board token = url slug).
# Mix of fintech / enterprise / healthcare / gaming-adjacent tech, avoiding known Workday shops.
CANDIDATES = [
    # Fifth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "enova", "audaxgroup", "praxisprecisionmedicines", "cerebrassystems",
    "d2consulting", "grvty", "quberesearchandtechnologies", "greenhouse",
    "iterativehealth", "hopscotchprimarycare", "definitivehc",
    "imaginepediatrics", "hs", "heygen", "circleso", "thenuclearcompany",
    "juullabs", "life360", "blastpoint", "xapo61", "headway", "isccareers",
    "lithic", "karbon", "prolific", "3cloud", "planetlabs", "hasbro",
    "dbtlabsinc", "humaninterest", "branch", "srsacquiom", "exactera",
    "sagent", "livefront", "datakindinc", "cresta", "wonderschool",
    "florencehealthcare",
    # Sixth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "cargomatic", "roadie", "shift5", "kargo22", "innodatainc", "knowbe4",
    "cybersheath", "galaxydigitalservices", "enhesa", "ujet", "lts",
    "thinkingmachines", "10alabs", "midihealth", "alt", "hungryroot",
    "maintainx", "opploans", "correlationone", "fleetio", "warp",
    "airtable", "future", "sandiegocommunitypower", "coupang",
    "ocrolusinc", "eltropyinc", "falconx", "bottomlinetechnologies",
    "rhinofederatedcomputing", "avepoint", "carrotfertility",
    "nscaleoperationsukltd", "gusto", "ionq", "consensys",
    "abnormalsecurity", "manifoldbio", "axle", "spacex", "oura", "natera",
    "lexingtonmedical", "weee", "atlassand", "everagtester",
    "redwoodmaterials", "gofundme", "faire", "perpay", "commercetools",
    "ezcaterinc", "yipitdata", "loop", "fourkites", "sitrepsllc",
    "gatherai", "onenergy", "rocketlab",
    # Seventh batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "climatecabinet", "climateai", "anewclimate", "tomorrow", "onecampaign",
    "muonspace", "energysolutions", "appdirectraas", "dv01", "gympass",
    "hatchcareers", "bringg", "appfire", "dexory", "gram",
    "appliedintuition", "privateer", "edo", "zetaglobal", "valtech",
    "xealth", "pieinsurance", "edgewoodpartnersinsurancecenter",
    "slideinsurance", "youcom", "acrisureinnovation", "insurify", "boxinc",
    "biohub", "flagshippioneeringinc", "precisionmedicinegroup",
    "pedestalhealth", "supplyhouse", "upwork", "turing", "surveymonkey",
    "shipbobinc", "diligentcorporation", "wurljobs", "wppmedia",
    "grafanalabs", "northbeam", "charterschoolgrowthfund", "mixpanel",
    "bevicareers", "torcrobotics", "apptronik", "nimblerobotics",
    "locusrobotics", "zone5technologies", "workstream",
    # Eighth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "eve", "oddball", "ducerapartners", "drivewealth", "coursera", "itd",
    "aclu", "orchard", "dragos", "cultureamp", "betterhelpcom",
    "defenseunicorns", "fireworksai", "mattermost", "dropzoneai",
    "addepar1", "samsungsemiconductor", "canonical", "senseiag",
    "stackadapt", "classpass", "blueskyinnovators", "algolia", "postscript",
    "winhomeinspection", "apartmentiq", "splitero", "k2spacecorporation",
    "kodiak", "faradayfuture", "formic", "bedrockrobotics", "fortrobotics",
    "extend", "houseaccount", "placementsio", "drweng", "upstart",
    "digitalocean98", "legalservicesnyc", "metropolis", "cribl", "federato",
    # Ninth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "newsela", "vynyl", "udacity", "effectual", "mntn", "alma",
    "fanaticscollectibles", "kardfinancialinc", "mitratech", "patientpoint",
    "greenlightconsulting", "postman", "neweratech",
    "hitachidigitalservices", "sesamm", "harrisassociates", "philo",
    "runwayml", "renaissancelearning-nam", "openfarminc", "blockchain",
    "trmlabs", "messari", "breezecash", "predictiveindex", "ref",
    "justworks", "visiersolutionsinc", "remotecom", "calm", "jetsonhome",
    "wheelhousedmg", "cognitiv", "charlesriverassociates", "hightouch",
    "newsbreak", "togetherai", "amplitude", "shopmy", "scowtt",
    "coderoad", "verse", "horizonindustrieslimited",
    # Tenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "cloudbeds", "casago", "lighthouse", "m3", "interval", "fanaticsfbg",
    "swishanalytics", "rushstreetinteractive", "sumup", "cookunity",
    "sweetgreen", "doordashusa", "afresh", "qualtrics", "techietalent",
    "eqtpartners", "fartherfinance", "sezzle", "coast", "abacusinsights",
    "accenturefederalservices", "hotelengine", "oscar", "gomotive",
    "mettel", "skylotechnologies", "alphafmcroles", "lazarusenterprises",
    "lilasciences", "bridgewater89", "recharge", "coherehealth",
    "gravitypayments17",
    # Eleventh batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "accuweather", "usenourish", "point72", "fastspring", "pilothq",
    "focusfinancialpartners", "gridmaticinc", "toast", "labelbox",
    "gradial", "arizeai",
    # Twelfth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "samsara", "krollbondratingagency", "ageoflearninginc", "quanata",
    "remotepeople", "counterpart", "coinbase", "affirm", "garnerhealth",
    "cloudbedsthirdpartyboard", "axios",
    # Thirteenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "roofr", "goatgroup", "thenewyorktimes", "gusto", "forafinancial",
    "ninjatrader", "chime", "missionlane", "wisetack", "paynearmeinc",
    # Fourteenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "careaccess", "sidebycare", "fuzehealth", "capitalrx", "axuall",
    "penninteractive", "scopely", "2k", "azragames",
    "sonyinteractiveentertainmentglobal",
    # Fifteenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "dataiku", "campminder", "fortifyiq", "fieldwire", "alpaca", "figure",
    # Sixteenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "iherb", "keebo", "velir", "latitude", "materialbank", "parloa",
    "chalkinc",
    # Seventeenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "distantjob", "lightspeedhq",
    # Eighteenth batch -- verified via WebSearch of real job-boards.greenhouse.io URLs
    "cribl", "securityscorecard", "vialogic", "scaleai", "twilio", "okta",
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
