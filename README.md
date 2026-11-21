# Public Translations

Translations of texts from the Vajrakula school, published as mobile-first reading editions in the Vajrakula visual identity (no animation).

## Sūtra of the Lotus Flower of the Wonderful Dharma
Translated by Acharya Vajraprajna. English, Español, Português.

- `lotus-sutra/` — the published site (static; serve with GitHub Pages from the repo root, path `/lotus-sutra/`)
- `tools/content/<lang>/chNN.txt` — source text, one paragraph or verse line per line. Every language file must have the same number of lines as the English one (the build checks this and falls back to English for a chapter that doesn't match).
- `tools/build.py` — regenerates `lotus-sutra/` : `cd tools && python3 build.py`
