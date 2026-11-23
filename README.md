# Public Translations

Translations of texts from the Vajrakula school, published as mobile-first reading editions in the Vajrakula visual identity (no animation).

## Sūtra of the Lotus Flower of the Wonderful Dharma
Translated by Lama Dorje Sherab (Acharya Vajraprajña). English, Español, Português.

- `lotus-sutra/` — the published site (static; serve with GitHub Pages from the repo root, path `/lotus-sutra/`)
- `tools/content/<lang>/chNN.txt` — source text, one paragraph or verse line per line. Every language file must have the same number of lines as the English one (the build checks this and falls back to English for a chapter that doesn't match).
- `tools/build.py` — regenerates `lotus-sutra/` : `cd tools && python3 build.py`

## Root Verses on the Middle Way, Called Prajñā (Nāgārjuna, *Mūlamadhyamakakārikā*)
Tibetan (Derge D3824) and Sanskrit, translated into English, Português and Español by Lama Fede Andino.

- `mulamadhyamakakarika/` — the published site (static; `/mulamadhyamakakarika/`)
  - `all/` — every layer verse by verse: Tibetan, Wylie, Devanagari, IAST, English, Português, Español
  - `en/`, `es/`, `pt/` — translation-only reading editions
- `tools/mmk/data.json` — the full text, extracted once from the source .docx (Tibetan, Wylie, Devanagari and IAST are copied verbatim, never retyped)
- `tools/mmk/parse_docx.py` — regenerates `data.json` from the .docx: `python3 -I parse_docx.py path/to/file.docx`
- `tools/mmk/notes_pt.json` — Portuguese version of the editorial notes (the .docx has them in English and Spanish only; draft for the translator to review)
- `tools/mmk/build_mmk.py` — regenerates the site: `cd tools/mmk && python3 build_mmk.py` (reuses `tools/style.css` + `tools/mmk/extra.css`)

## Lotus Samādhi Repentance: Liturgy and Practical Guide
Liturgy of Master Zhiyi (Part I) and a practical guide with condensed instructions (Part II), to be practised together with the Sūtra of the Lotus Flower of the Wonderful Dharma. English, Español, Português. English is translated by Lama Dorje Sherab (Acharya Vajraprajña); the Español and Português versions are drafts for the translator to review.

- `lotus-repentance-rite/` — the published site (static; `/lotus-repentance-rite/`), one page per language plus a language chooser
- `tools/rite/content/{en,es,pt}.txt` — source text, one typed line per line (`TYPE|text`; `PT` title, `PS` subtitle, `PC` attribution, `H2`/`H3`/`H4` headings, `P` paragraph, `C` chanted or spoken line, `V`/`VE` verse line / last line of a stanza, `OL`/`UL` list item, `PE` closing line, `CO` dedication; inline `*italic*` and `**bold**`). A `=====` line separates Part I from Part II. Every language file must match the English one line for line and type for type; the build stops with an error otherwise.
- `tools/rite/meta.py` — interface strings per language
- `tools/rite/build.py` — regenerates the site: `python3 tools/rite/build.py` (reuses `tools/style.css` + `tools/rite/extra.css`; cover image `tools/rite/cover.jpg`)
