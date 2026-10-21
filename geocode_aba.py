import json

# Read existing hospitals
with open('hospitals.json', 'r', encoding='utf-8') as f:
    hospitals = json.load(f)

# The new list to geocode
new_centers = [
    "Firefighters' Burn Treatment Unit - Edmonton, Alberta",
    "The Diane and Bruce Halle Arizona Burn Center - Valleywise Health, Arizona",
    "Firefighters Burn Institute Regional Burn Center - UC Davis, California",
    "Los Angeles General Medical Center Regional Burn Center, California",
    "Santa Clara Valley Medical Center Regional Burn Center, California",
    "Torrance Memorial's Burn Center, California",
    "UC San Diego Health Regional Burn Center, California",
    "UCSF Health Saint Francis Hospital - Bothin Burn Center, California",
    "HCA HealthONE Swedish, Colorado",
    "Connecticut Burn Center - Bridgeport Hospital, Connecticut",
    "Miami Burn Center, Florida",
    "The Burn and Reconstructive Center at HCA Florida Kendall Hospital, Florida",
    "Warden Burn Center at Orlando Health, Florida",
    "Walter L. Ingram Burn Center - Grady Memorial Hospital, Georgia",
    "University of Chicago Burn Center, Illinois",
    "Ascension St. Vincent Burn Center, Indiana",
    "Richard M. Fairbanks Burn Center, Indiana",
    "University of Iowa Health Care Burn Treatment Center, Iowa",
    "The University of Kansas Health System Burnett Burn Center, Kansas",
    "Our Lady of Lourdes Burn Center, Louisiana",
    "Johns Hopkins Adult Burn Center, Maryland",
    "Johns Hopkins Pediatric Burn Center, Maryland",
    "Shriners Burn Center - Boston, Massachusetts",
    "Children's Hospital of Michigan Burn Center, Michigan",
    "Lions Burn Center, Nevada",
    "Clark Burn Center, New York",
    "William Randolph Hearst Burn Center, New York",
    "North Carolina Jaycee Burn Center, North Carolina",
    "Akron Children's Hospital Burn Center, Ohio",
    "Burn Care Center at MetroHealth, Ohio",
    "Shriners Children's Ohio Burn Center, Ohio",
    "The Ohio State Comprehensive Burn Center, Ohio",
    "Hospital for Sick Children Burn Center, Ontario",
    "Ross Tilley Burn Centre, Ontario",
    "Lehigh Valley Health Network Regional Burn Center, Pennsylvania",
    "South Carolina Burn Center at MUSC, South Carolina",
    "Blocker Burn Unit, Texas",
    "Timothy J. Harnar Burn Center, Texas",
    "USAISR Burn Center, Texas",
    "University of Utah Health Burn Center, Utah",
    "Evans-Haynes Burn Center, Virginia",
    "Ascension Columbia St. Mary's Regional Burn Center, Wisconsin",
    "UW Burn and Wound Center, Wisconsin"
]

# We need to geocode these using nominatim API
import urllib.request
import urllib.parse
import time

new_entries = []

for center in new_centers:
    # Build query
    query = urllib.parse.urlencode({'q': center, 'format': 'json'})
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    
    print(f"Geocoding: {center}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CareBot/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                new_entries.append({
                    "name": f"ABA Certified - {center.split(',')[0]}",
                    "lat": lat,
                    "lng": lng,
                    "type": "burn_center"
                })
                print(f"  -> Found: {lat}, {lng}")
            else:
                print("  -> Not found")
    except Exception as e:
        print(f"  -> Error: {e}")
        
    # Rate limiting for Nominatim (1 request per second)
    time.sleep(1.2)

# Remove the old hardcoded ABA centers to avoid duplicates
filtered_hospitals = [h for h in hospitals if h.get("type") == "soar_hospital"]

# Combine
final_hospitals = filtered_hospitals + new_entries

with open('hospitals_updated.json', 'w', encoding='utf-8') as f:
    json.dump(final_hospitals, f, indent=4)
    
print(f"Added {len(new_entries)} new ABA centers.")
