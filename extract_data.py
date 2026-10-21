import re
import json

kml_file = "soar_hospitals.kml"  # KML export of the Phoenix SOAR hospital map

with open(kml_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract Placemarks
placemarks = re.findall(r'<Placemark>.*?<name>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</name>.*?<coordinates>\s*([^,]+),([^,]+),.*?</coordinates>.*?</Placemark>', content, re.DOTALL)

hospitals = []
for name, lon, lat in placemarks:
    hospitals.append({
        "name": name.strip(),
        "lat": float(lat.strip()),
        "lng": float(lon.strip()),
        "type": "soar_hospital"
    })

# Add some hardcoded ABA verified Burn Centers that are purely medical to test the filtering
aba_centers = [
    { "name": "ABA Certified - Loyola Medicine Burn Center", "lat": 41.8587, "lng": -87.8354, "type": "burn_center" },
    { "name": "ABA Certified - Shriners Children's Texas", "lat": 29.3013, "lng": -94.7977, "type": "burn_center" },
    { "name": "ABA Certified - Harborview Medical Center", "lat": 47.6041, "lng": -122.3242, "type": "burn_center" },
    { "name": "ABA Certified - Vanderbilt Regional Burn Center", "lat": 36.1409, "lng": -86.8016, "type": "burn_center" },
    { "name": "ABA Certified - Weill Cornell Burn Center", "lat": 40.7641, "lng": -73.9535, "type": "burn_center" }
]

hospitals.extend(aba_centers)

output_file = "hospitals.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(hospitals, f, indent=4)

print(f"Successfully extracted {len(hospitals)} hospitals to hospitals.json")
