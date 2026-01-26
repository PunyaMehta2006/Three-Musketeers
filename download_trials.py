import requests
import json
import time
import os

# 1. Define the target conditions based on your Plan [cite: 94-99]
CONDITIONS = [
    "Type 2 Diabetes",
    "Hypertension", 
    "Breast Cancer", 
    "Lung Cancer", 
    "Heart Disease"
]

TARGET_PER_CONDITION = 2000  # Goal: 10,000 total 
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def download_trials():
    all_trials = []
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')

    print(f"🚀 Starting download. Target: {len(CONDITIONS) * TARGET_PER_CONDITION} trials.")

    for condition in CONDITIONS:
        print(f"\n📥 Fetching trials for: {condition}...")
        count = 0
        next_page_token = None
        
        while count < TARGET_PER_CONDITION:
            # 2. Construct Query Parameters [cite: 556]
            params = {
                "query.cond": condition,
                "filter.overallStatus": "RECRUITING", # Only active trials [cite: 108]
                "pageSize": 100, # Max allowed per page
                "format": "json"
            }
            
            # Handle Pagination (ClinicalTrials.gov v2 API uses page tokens)
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                studies = data.get('studies', [])
                if not studies:
                    print(f"   ⚠️ No more studies found for {condition}.")
                    break
                
                # Add to master list
                all_trials.extend(studies)
                count += len(studies)
                print(f"   ✅ Collected {count}/{TARGET_PER_CONDITION}...")
                
                # Check for next page
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Be nice to the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                break
                
    # 3. Save to JSON [cite: 558]
    output_file = "data/trials_10k.json"
    with open(output_file, "w") as f:
        json.dump(all_trials, f, indent=2)
        
    print(f"\n🎉 Success! Downloaded {len(all_trials)} trials to {output_file}")

if __name__ == "__main__":
    download_trials()