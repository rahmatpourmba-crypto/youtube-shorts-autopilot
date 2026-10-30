# Quran text & translations (bundled, verbatim)

Used by `quran_branding.py` to burn ayah subtitles. Text is NEVER generated: it is read
verbatim from these files (fallback to none -> subtitles skipped).

| File | Content | Source | License |
|---|---|---|---|
| `quran-simple.txt` | Arabic Quran text, Tanzil "Simple" v1.1 (with diacritics) | https://tanzil.net/download/ | CC BY 3.0, verbatim copy only (Tanzil Project, tanzil.net) |
| `fa.ansarian.txt` | Persian translation, Hussain Ansarian (`fa.ansarian`) | https://tanzil.net/trans/ | Tanzil translations: non-commercial/verbatim, attribution to translator & tanzil.net |
| `en.sahih.txt` | English, Saheeh International (`en.sahih`) | https://tanzil.net/trans/ | as above |
| `surah-names.json` | Surah names (Arabic/translit/English), ayah counts | Tanzil metadata quran-data.xml | as above |

Format: `surah|ayah|text` per line; trailing `#` lines are the original copyright notices
(kept unmodified as required by the Tanzil terms of use). Do not edit these files.
