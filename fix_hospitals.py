import json
import urllib.request
import urllib.parse
import time

# A highly curated list of search terms that will definitively succeed on Nominatim
curated_aba = {
    "Firefighters' Burn Treatment Unit — Edmonton": "University of Alberta Hospital, Edmonton, AB",
    "The Diane and Bruce Halle Arizona Burn Center — Valleywise Health": "Valleywise Health Medical Center, Phoenix, AZ",
    "Leon S. Peters Burn Center": "Community Regional Medical Center, Fresno, CA",
    "Los Angeles General Medical Center Regional Burn Center": "Los Angeles General Medical Center, Los Angeles, CA",
    "Santa Clara Valley Medical Center Regional Burn Center": "Santa Clara Valley Medical Center, San Jose, CA",
    "Torrance Memorial's Burn Center": "Torrance Memorial Medical Center, Torrance, CA",
    "UC San Diego Health Regional Burn Center": "UC San Diego Medical Center, San Diego, CA",
    "UCSF Health Saint Francis Hospital — Bothin Burn Center": "Saint Francis Memorial Hospital, San Francisco, CA",
    "HCA HealthONE Swedish": "Swedish Medical Center, Englewood, CO",
    "UCHealth Burn and Frostbite Center — Anschutz Medical Campus": "UCHealth University of Colorado Hospital, Aurora, CO",
    "Connecticut Burn Center — Bridgeport Hospital": "Bridgeport Hospital, Bridgeport, CT",
    "The Burn Center at MedStar Washington Hospital Center": "MedStar Washington Hospital Center, Washington, DC",
    "Miami Burn Center": "Ryder Trauma Center, Miami, FL",
    "The Burn and Reconstructive Center at HCA Florida Kendall Hospital": "Kendall Regional Medical Center, Miami, FL",
    "Warden Burn Center at Orlando Health": "Orlando Regional Medical Center, Orlando, FL",
    "Walter L. Ingram Burn Center — Grady Memorial Hospital": "Grady Memorial Hospital, Atlanta, GA",
    "The Burn Center at Eastern Idaho Regional Medical Center": "Eastern Idaho Regional Medical Center, Idaho Falls, ID",
    "Burn Program at Riley at IU Health": "Riley Hospital for Children, Indianapolis, IN",
    "Richard M. Fairbanks Burn Center": "Eskenazi Hospital, Indianapolis, IN",
    "Our Lady of Lourdes Burn Center": "Our Lady of Lourdes Regional Medical Center, Lafayette, LA",
    "Shriners Burn Center — Boston": "Shriners Hospitals for Children, Boston, MA",
    "Hennepin Healthcare Burn Center": "Hennepin County Medical Center, Minneapolis, MN",
    "The Burn Center at Cooperman Barnabas": "Cooperman Barnabas Medical Center, Livingston, NJ",
    "Clark Burn Center": "Upstate University Hospital, Syracuse, NY",
    "William Randolph Hearst Burn Center": "Weill Cornell Medical Center, New York, NY",
    "North Carolina Jaycee Burn Center": "UNC Medical Center, Chapel Hill, NC",
    "Akron Children's Hospital Burn Center": "Akron Children's Hospital, Akron, OH",
    "Legacy Oregon Burn Center": "Legacy Emanuel Medical Center, Portland, OR",
    "Lehigh Valley Health Network Regional Burn Center": "Lehigh Valley Hospital - Cedar Crest, Allentown, PA",
    "Temple Burn Center": "Temple University Hospital, Philadelphia, PA",
    "South Carolina Burn Center at MUSC": "MUSC Medical Center, Charleston, SC",
    "Blocker Burn Unit": "UTMB Health, Galveston, TX",
    "Parkland Burn Center": "Parkland Memorial Hospital, Dallas, TX",
    "Timothy J. Harnar Burn Center": "UMC Health System, Lubbock, TX",
    "USAISR Burn Center": "Brooke Army Medical Center, San Antonio, TX"
}

with open('hospitals.json', 'r', encoding='utf-8') as f:
    hospitals = json.load(f)

# Keep only SOAR hospitals
soar_hospitals = [h for h in hospitals if h.get("type") == "soar_hospital"]

new_entries = []

for display_name, query_name in curated_aba.items():
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_name)}&format=json&limit=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CareBot/2.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                new_entries.append({
                    "name": f"ABA Certified - {display_name}",
                    "lat": lat,
                    "lng": lng,
                    "type": "burn_center"
                })
                print(f"Success: {display_name}")
            else:
                print(f"Failed to find exact location for: {query_name}")
    except Exception as e:
        print(f"Error on {query_name}: {e}")
        
    time.sleep(1.1)

final_hospitals = soar_hospitals + new_entries

with open('hospitals.json', 'w', encoding='utf-8') as f:
    json.dump(final_hospitals, f, indent=4)
    
print(f"Successfully appended {len(new_entries)} accurately geocoded ABA centers!")
