# CareBot: iGEM Scarring Support Chatbot

CareBot is a chatbot built by an iGEM team for burn survivors recovering from scarring. It gives general information about scar types, healing timelines and coping strategies, and it is clear that it is not a doctor or a therapist.

- **Crisis handoff:** questions about diagnosis, severe pain or infection, self-harm or severe distress get a card linking to the Phoenix Society, the Crisis Text Line and the ABA burn center finder instead of an AI answer.
- **Burn center map:** when someone asks where to find care, CareBot shows a map of ABA-verified burn centers (blue) and Phoenix SOAR peer-support hospitals (orange), zoomed to their region.
- **Conversation memory:** follow-up questions keep the context of the chat.

It runs on Google Gemini, with a FastAPI backend and a plain HTML/JS frontend that uses Leaflet and OpenStreetMap.

## Running it locally

You need Python 3.10 or newer and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your key into .env
python backend/main.py
```

Then open http://127.0.0.1:8000.

To see which Gemini models your key can use, run `python backend/test_models.py`.

## Files

| File | What it is |
| --- | --- |
| `index.html`, `style.css`, `script.js` | The chat page and map |
| `backend/main.py` | The server: serves the page and talks to Gemini |
| `hospitals.json` | Map data: SOAR hospitals and ABA burn centers with coordinates |
| `aba_list.txt` | Source list of ABA-verified burn centers by state/province |
| `fix_hospitals.py` | Rebuilds the ABA entries in `hospitals.json` by geocoding a curated address list |
| `check_coords.py` | Prints the burn center coordinates for checking |
| `extract_data.py`, `geocode_aba.py`, `geocode_aba_v2.py`, `hospitals_updated.json` | Earlier one-off data scripts and output, kept for reference |
