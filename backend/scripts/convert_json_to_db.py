"""
Convert trials_10k.json to SQLite database
Run this ONCE to populate the database
"""
import json
import sqlite3
import os
# Paths
SCRIPT_DIR = os.path.dirname(__file__)
JSON_FILE = os.path.join(SCRIPT_DIR, "../../data/trials_10k.json")
DB_FILE = os.path.join(SCRIPT_DIR, "../../data/trials.db")
print(f"Converting trials from JSON to SQLite...")
print(f"JSON file: {JSON_FILE}")
print(f"Database: {DB_FILE}")
# Load JSON data
print("\n[1/3] Loading JSON file...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    trials = json.load(f)
print(f"✅ Loaded {len(trials)} trials")
# Create database
print("\n[2/3] Creating database and table...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trials (
        nct_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        brief_summary TEXT,
        status TEXT,
        phase TEXT,
        conditions TEXT,
        eligibility_criteria TEXT,
        minimum_age TEXT,
        maximum_age TEXT,
        gender TEXT,
        locations TEXT,
        sponsor TEXT
    )
""")
print("✅ Table created")
# Insert trials
print("\n[3/3] Inserting trials into database...")
count = 0
for trial in trials:
    # Extract from nested structure
    protocol = trial.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    description = protocol.get("descriptionModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    design_module = protocol.get("designModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    contacts = protocol.get("contactsLocationsModule", {})
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    
    # Get NCT ID and title
    nct_id = identification.get("nctId", "")
    title = identification.get("briefTitle", "")
    
    # Skip if missing required fields
    if not nct_id or not title:
        continue
    
    # Extract other fields
    brief_summary = description.get("briefSummary", "")
    status = status_module.get("overallStatus", "")
    
    # Phase
    phases = design_module.get("phases", [])
    phase = phases[0] if phases else None
    
    # Conditions
    conditions = conditions_module.get("conditions", [])
    
    # Eligibility
    eligibility_criteria = eligibility.get("eligibilityCriteria", "")
    min_age = eligibility.get("minimumAge", "")
    max_age = eligibility.get("maximumAge", "")
    sex = eligibility.get("sex", "ALL")
    
    # Locations
    locations_list = contacts.get("locations", [])
    location_names = []
    for loc in locations_list:
        city = loc.get("city", "")
        country = loc.get("country", "")
        if city and country:
            location_names.append(f"{city}, {country}")
    
    # Sponsor
    lead_sponsor = sponsor_module.get("leadSponsor", {})
    sponsor = lead_sponsor.get("name", "")
    
    # Insert into database
    cursor.execute("""
        INSERT OR REPLACE INTO trials 
        (nct_id, title, brief_summary, status, phase, conditions,
         eligibility_criteria, minimum_age, maximum_age, gender,
         locations, sponsor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nct_id,
        title,
        brief_summary,
        status,
        phase,
        json.dumps(conditions),
        eligibility_criteria,
        min_age,
        max_age,
        sex,
        json.dumps(location_names),
        sponsor
    ))
    
    count += 1
    if count % 1000 == 0:
        print(f"  Inserted {count} trials...")
# Save changes
conn.commit()
conn.close()
print(f"\n SUCCESS! Inserted {count} trials into database")
print(f" Database created at: {DB_FILE}")
print(f" Database size: {os.path.getsize(DB_FILE) / (1024*1024):.1f} MB")