# DESIGN.md: muhummud.org

Read this before changing anything visual. The site's value is its restraint, and most "improvements" add things it deliberately leaves out.

## Register

A personal page, read quietly, usually on a phone. One visitor in mind. It should feel like a paragraph someone wrote you, not an app.

## Principles

1. **Prose, not dashboard.** Everything is sentences. Live values sit inside the sentences, set darker and slightly heavier than the words around them.
2. **Restraint.** No cards, icons, navigation, headings, badges, dividers, shadows, gradients, rounded containers or emoji. If a change adds a box around something, it is probably wrong.
3. **Fail visible, not blank.** Each data source degrades one sentence at a time ("Prayer times are unavailable right now"), never the whole page.
4. **Correct tense.** The copy changes with the time of day rather than showing a stale sentence.

## Colour

Four tokens, redefined for dark mode. Text contrast must stay at or above WCAG AA (4.5:1) in both modes, at every size the page renders. Check the ratio whenever a grey changes.

| Token | Light | Dark | Use | Contrast |
| --- | --- | --- | --- | --- |
| `--bg` | `#fdfdfb` | `#131311` | Page | n/a |
| `--muted` | `#75756f` | `#80807a` | Prose, footer, source line | 4.55:1 / 4.68:1 |
| `--ink` | `#1a1a18` | `#efefe9` | Live values, verse, translation, current site in the ring | 17.1:1 / 16.1:1 |
| `--rule` | `#d9d9d2` | `#3a3a35` | Dotted underlines only, never text | decorative |

There is no accent colour, and there should not be one.

`--muted` was `#8e8e88` until 2026-09-27. At 3.23:1 it failed AA wherever body text rendered under 24px, which is every phone, and everywhere for the footer and source line.

## Type

- **Latin:** Inter 400 and 500 from Google Fonts, falling back to `"Helvetica Neue", Helvetica, Arial, sans-serif`. Helvetica itself cannot be licensed for the web; the fallback gives real Helvetica on Apple devices.
- **Arabic:** Noto Naskh Arabic 400 and 500, falling back to Scheherazade New, then Amiri. The closest free face to the IndoPak style; Quran.com's own IndoPak font is licensed and not redistributable.
- **Body size:** `clamp(1.35rem, 1.1rem + 1.2vw, 1.8rem)`, line-height 1.5, letter-spacing −0.005em.
- **Weights:** prose 400, live values 500. Never bold beyond 500.
- **Relative sizes:** greeting Arabic 1.15em, verse Arabic 1.5em at line-height 2, source line 0.6em, footer 0.55em.

## Layout

- One column, `max-width: 34em`, centred. Horizontal padding `clamp(1.25rem, 5vw, 2.5rem)`.
- `body` is a flex column with `min-height: 100dvh`; the footer takes `margin-top: auto` so short days don't leave a trailing gap on tall phones.
- Paragraph spacing `margin-bottom: 1.4em`.
- Date and time tokens (`#hijri`, `#clock`, `#sunrise`, `#sunset`) are `white-space: nowrap`, so the Hijri date never breaks at its hyphen.
- The Arabic verse is right-aligned, `direction: rtl`; the translation beneath it is left-aligned.

## Copy

The template, live values in bold:

> As-salamu alaykum ٱلسَّلَامُ عَلَيْكُمْ
>
> It's **Monday, September 14, 2026**, or **3 Rabīʿ al-thānī 1448** on the Hijri calendar. The time in Toronto is **9:31 AM**. Outside it's **15°C, with a high of 19° and a low of 11°**. Sunrise was at **6:56 AM** and sunset will be at **7:29 PM**.
>
> **Fajr** time ended at sunrise. Next is **Dhuhr** at **1:13 PM**, in **3h 42m**.
>
> Today's verse is **Al-Fatihah 1:2**, The Opener (الفاتحة).

Rules:

- Don't repeat "Today" or "Currently" across paragraphs. That's why the wording is what it is.
- Times as `h:mm AM/PM` (US locale). Canadian locale produces `p.m.`, which doubles the full stop at a sentence end.
- The Hijri month keeps its diacritics exactly as Aladhan returns them.
- Sunrise: "is at" before, "was at" after. Sunset: "will be at" before, "was at" after.
- The prayer sentence has four forms: before Fajr, "First up is X at T, in D"; during a prayer, "X began at T. Next is Y at T, in D"; between sunrise and Dhuhr, "Fajr time ended at sunrise. Next is Dhuhr…"; after Isha the next prayer is tomorrow's Fajr.
- Countdown under an hour reads "25 minutes", over an hour "3h 42m".
- The weather low is clamped to the current reading so it never reads above it.

## Footer

Two lines, in this order: data credits, then the site ring.

1. **Credits.** Exactly: "Quran data provided by Quran Foundation. Prayer times from Aladhan. Weather from Open-Meteo." The Quran Foundation wording is a licence condition; do not paraphrase it.
2. **Site ring.** A fixed order across every site in the family, not current-site-first:

   muhummud.org · thatstheworst.com · flemingdon.org · naseema.net · iseentit.com

   The current site carries `aria-current="page"` and renders in `--ink`; the others stay `--muted`. Each link is `white-space: nowrap`.

## Don't

- Add browser storage, cookies, analytics or any tracking.
- Add a build step, framework or bundler. It is one HTML file on purpose.
- Add a second typeface or an accent colour.
- Put account names, secret locations or infrastructure detail in this repo. It is public.
- Change the ring order on one site without changing it on all five.
