import json
# Load JSON
with open("../data/trials_10k.json", "r", encoding="utf-8") as f:
    trials = json.load(f)
print(f"Total trials: {len(trials)}")
print(f"\nFirst trial keys:")
for key in trials[0].keys():
    print(f"  - {key}")
print(f"\nSample values from first trial:")
print(f"  nct_id: {trials[0].get('nct_id', 'MISSING')}")
print(f"  title: {trials[0].get('title', 'MISSING')}")
print(f"  status: {trials[0].get('status', 'MISSING')}")