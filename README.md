# Verse & Prayer Times (Toronto)

Static one-page site on GitHub Pages. A daily GitHub Action fetches the verse of the day
into `data/verse.json`; prayer times are fetched client-side from Aladhan.

## Setup
1. Request Quran Foundation API access (Backend/server app) to get a client_id + client_secret.
2. Repo Settings > Secrets and variables > Actions:
   - Secrets: `QF_CLIENT_ID`, `QF_CLIENT_SECRET`
   - Variable: `QF_ENV` = `prelive` while testing, `production` once approved
3. Settings > Pages > Source: Deploy from branch, `gh-pages` (default branch), folder `/ (root)`.
4. Actions tab > "Verse of the day" > Run workflow to generate the first `verse.json`.

## Verse order
One verse per day starting at 1:1, advancing through the Quran and wrapping after 114:6. To start elsewhere on first run set `START_INDEX` (0-based). To reset, delete `data/verse.json`.

## Local test
```
$env:QF_CLIENT_ID="..."; $env:QF_CLIENT_SECRET="..."; $env:QF_ENV="prelive"
pip install -r scripts/requirements.txt
python scripts/fetch_verse.py
```
