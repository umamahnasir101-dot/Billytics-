# Billytics — Your Bill Decoder, Pakistan

Team Two Devs — Umamah Nasir & Chaudhary Muhammad Huzaifa Ali

## Files
- `app.py` — the whole app (all 8 features + home page)
- `requirements.txt` — Python packages needed
- `logo.png` — your logo, shown on the home page

## Before you deploy
Open `app.py` and check the section near the top marked
`⚠️ VERIFY BEFORE DEMO ⚠️`. Update the tariff slabs (`IESCO_SLABS`) and the
medicine prices (`MEDICINES`) with current, verified numbers before your
presentation.

## Deploy (see chat for the full step-by-step)
1. Push these 3 files to a GitHub repo.
2. Go to https://share.streamlit.io, connect the repo, set main file to `app.py`.
3. In the app's "Secrets" settings, add:
   ```
   GROQ_API_KEY = "your-key-here"
   ```
4. Deploy. Done.
