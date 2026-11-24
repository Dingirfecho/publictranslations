"""Extract the MP58 text (Tibetan, Wylie, Español, English, Português) from the source PDF into data.json.
Run:  python3 -I parse_pdf.py path/to/MP58.pdf
Needs PyMuPDF (pip install pymupdf) and pdftotext (poppler).
PyMuPDF gives clean line structure but doubles Tibetan vowel signs; pdftotext keeps the signs but inserts stray spaces.
Each item's Tibetan is checked against the other extraction; where they disagree (item 74, where the PDF itself has a
doubled vowel sign) the pdftotext reading, i.e. the PDF as written, is kept."""
import re, json, sys, subprocess, os
pdf = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
import fitz
doc = fitz.open(pdf)
SRC = '\n'.join(p.get_text() for p in doc).split('\n')
TXT = subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf, '-'], capture_output=True, text=True, check=True).stdout
tib = lambda s: bool(re.search('[ༀ-࿿]', s))
MARK = re.compile('([ཱ-྄ྍ-ྼ])\\1+')
items = []; cur = None; lang = None
for raw in SRC:
    ln = raw.rstrip()
    if re.fullmatch(r'\d\d', ln):
        cur = {'n': int(ln), 'folio': None, 'tib': [], 'wyl': [], 'es': [], 'en': [], 'pt': []}; items.append(cur); lang = 'head'; continue
    if cur is None: continue
    if lang == 'head' and re.fullmatch(r'5-43-\d[ab]', ln):
        cur['folio'] = ln; lang = 'tib'; continue
    if ln == '' or ln.startswith('V A J R A K U L A') or ln.startswith('M P 5 8') or re.fullmatch(r'[IV]+', ln) or ln.startswith('L O S O '):
        continue
    m = re.fullmatch(r'(E S|E N|P T)', ln)
    if m: lang = m.group(1).replace(' ', '').lower(); continue
    if lang in ('tib', 'wyl'):
        if tib(ln): lang = 'tib'; cur['tib'].append(MARK.sub(r'\1', ln))
        else: lang = 'wyl'; cur['wyl'].append(ln)
    elif lang in ('es', 'en', 'pt'):
        cur[lang].append(ln)
def jt(ls):
    out = ''
    for l in ls:
        if out and not out.endswith('་') and not out.endswith(' '): out += ' '
        out += l
    return out
for it in items:
    it['tib'] = jt(it['tib']); it['wyl'] = ' '.join(it['wyl'])
    for l in ('es', 'en', 'pt'): it[l] = ' '.join(it[l])
clean = lambda s: re.sub('([ཱ-྄ྍ-ྼ]) (?=[ༀ-࿿])', r'\1', s)
ptj = re.sub(r'\s+', '', ''.join(clean(l) for l in TXT.split('\n') if tib(l)))
for it in items:
    t = re.sub(r'\s+', '', it['tib'])
    if t not in ptj:
        # keep the PDF's own reading: find the pdftotext line(s) for this item
        words = [l for l in TXT.split('\n') if tib(l)]
        cand = [clean(l) for l in words if re.sub(r'\s+', '', MARK.sub(r'\1', clean(l))) and
                MARK.sub(r'\1', re.sub(r'\s+', '', clean(l))) == t]
        if cand: it['tib'] = cand[0]; print('item', it['n'], 'Tibetan taken from pdftotext reading')
        else: print('WARNING: item', it['n'], 'Tibetan does not match the second extraction')
json.dump({'items': items}, open(os.path.join(HERE, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items), 'items')
