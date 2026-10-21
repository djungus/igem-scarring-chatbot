import json
with open('hospitals.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for h in data:
    if h.get('type') == 'burn_center':
        print(f"{h['name']}: {h['lat']}, {h['lng']}")
