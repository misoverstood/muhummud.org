"""
Verse of the day fetcher for GitHub Actions.
Walks the Quran in order, one verse per day (1:1, 1:2, ... 114:6, then wraps),
pulls IndoPak Arabic + English (Mufti Taqi Usmani) from the Quran Foundation Content API,
and writes data/verse.json for the static site.
The previous verse.json is the state: if it is already today's, nothing changes.
"""
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ENV = os.getenv("QF_ENV", "prelive")
CLIENT_ID = os.environ["QF_CLIENT_ID"]
CLIENT_SECRET = os.environ["QF_CLIENT_SECRET"]
TRANSLATION_ID = os.getenv("QF_TRANSLATION_ID")  # optional numeric override
TRANSLATION_MATCH = os.getenv("QF_TRANSLATION_MATCH", "usmani")  # preferred, case-insensitive name/author match (Mufti Taqi Usmani)
TRANSLATION_FALLBACK = os.getenv("QF_TRANSLATION_FALLBACK", "saheeh")   # used if the preferred one is unavailable
OUT = Path(os.getenv("OUT_PATH", "data/verse.json"))

URLS = {
    "prelive": ("https://prelive-oauth2.quran.foundation", "https://apis-prelive.quran.foundation"),
    "production": ("https://oauth2.quran.foundation", "https://apis.quran.foundation"),
}
AUTH_BASE, API_BASE = URLS[ENV]

# Ayah count per surah, 1..114 (sums to 6236)
AYAH_COUNTS = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,
112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,
18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,
40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
TOTAL = sum(AYAH_COUNTS)


def key_to_index(key: str) -> int:
    """'2:255' -> 0-based position in the whole Quran."""
    surah, ayah = (int(x) for x in key.split(":"))
    return sum(AYAH_COUNTS[: surah - 1]) + ayah - 1


def index_to_key(idx: int) -> str:
    idx %= TOTAL
    for surah, count in enumerate(AYAH_COUNTS, start=1):
        if idx < count:
            return f"{surah}:{idx + 1}"
        idx -= count
    raise RuntimeError("unreachable")


def next_verse_key(today: date) -> str | None:
    """Advance one verse from the last run. None means today's verse is already written."""
    if not OUT.exists():
        return index_to_key(int(os.getenv("START_INDEX", "0")))
    prev = json.loads(OUT.read_text(encoding="utf-8"))
    if prev.get("date") == today.isoformat():
        return None
    return index_to_key(key_to_index(prev["verse_key"]) + 1)


def get_token() -> str:
    r = requests.post(
        f"{AUTH_BASE}/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="grant_type=client_credentials&scope=content",
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def api_get(token: str, path: str, params: dict | None = None) -> dict:
    r = requests.get(
        f"{API_BASE}/content/api/v4{path}",
        headers={"x-auth-token": token, "x-client-id": CLIENT_ID},
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def resolve_translation_id(token: str) -> int:
    """Find the translation by name so we don't depend on quran.com's public IDs."""
    if TRANSLATION_ID:
        return int(TRANSLATION_ID)
    items = api_get(token, "/resources/translations", {"language": "en"})["translations"]
    english = [t for t in items if (t.get("language_name") or "").lower() == "english"]
    def find(needle: str) -> int | None:
        for t in english:
            if needle in f"{t.get('name','')} {t.get('author_name','')}".lower():
                return int(t["id"])
        return None

    if (tid := find(TRANSLATION_MATCH)) is not None:
        return tid
    if (tid := find(TRANSLATION_FALLBACK)) is not None:
        print(f"'{TRANSLATION_MATCH}' not available to this app; falling back to '{TRANSLATION_FALLBACK}' (id {tid})")
        return tid
    print(f"Neither '{TRANSLATION_MATCH}' nor '{TRANSLATION_FALLBACK}' matched. Available:")
    for t in english:
        print(f"  {t['id']:>5}  {t.get('name')}  ({t.get('author_name')})")
    raise SystemExit(1)


def clean(html: str) -> str:
    """Drop footnote markers (<sup ...>1</sup>) and any other tags, tidy spaces."""
    text = re.sub(r"<sup\b[^>]*>.*?</sup>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    today = datetime.now(ZoneInfo("America/Toronto")).date()
    key = next_verse_key(today)
    if key is None:
        print("verse.json already current for today")
        return 0
    surah_num = int(key.split(":")[0])

    token = get_token()
    translation_id = resolve_translation_id(token)
    print(f"Using translation id {translation_id}")
    try:
        script = api_get(token, "/quran/verses/indopak", {"verse_key": key})["verses"][0]
        tr_resp = api_get(token, f"/quran/translations/{translation_id}", {"verse_key": key})
        tr = tr_resp["translations"][0]
        chapter = api_get(token, f"/chapters/{surah_num}", {"language": "en"})["chapter"]
    except (KeyError, IndexError) as e:
        print("Unexpected API response shape:", repr(e))
        for name in ("script", "tr_resp", "chapter"):
            if name in locals():
                print(name, "=", json.dumps(locals()[name], ensure_ascii=False)[:1500])
        raise

    source = (tr_resp.get("meta") or {}).get("translation_name") or tr.get("resource_name") or "Mufti Taqi Usmani"
    verse_number = int(key.split(":")[1])

    payload = {
        "date": today.isoformat(),
        "verse_key": key,
        "surah": {
            "number": surah_num,
            "name_arabic": chapter["name_arabic"],
            "name_simple": chapter["name_simple"],
            "translated_name": chapter["translated_name"]["name"],
        },
        "ayah": verse_number,
        "position": key_to_index(key) + 1,
        "total": TOTAL,
        "arabic": script["text_indopak"],
        "script": "indopak",
        "translation": clean(tr["text"]),
        "translation_source": source,
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat(timespec="seconds"),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} for {key} ({payload['surah']['name_simple']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
