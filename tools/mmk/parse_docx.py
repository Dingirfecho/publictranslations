"""Parse the Mūlamadhyamakakārikā root-verses .docx into data.json.
Usage: python3 -I parse_docx.py path/to/Mulamadhyamakakarika_root_verses.docx
Nothing is retyped: Tibetan, Wylie, Devanagari and IAST are copied verbatim from the docx."""
import sys, re, json, os
import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

src = sys.argv[1]
d = docx.Document(src)
items = []
for e in d.element.body:
    if e.tag.endswith('}p'):
        items.append(('p', Paragraph(e, d).text))
    elif e.tag.endswith('}tbl'):
        T = Table(e, d)
        items.append(('t', [[[p.text for p in c.paragraphs] for c in r.cells] for r in T.rows]))

LAB = re.compile(r'^([A-Z]{2,3})\t(.*)$', re.S)
def labelled(paras):
    out = {}
    for p in paras:
        m = LAB.match(p)
        if m: out[m.group(1)] = m.group(2).split('\n')
    return out

def siglum(lines):
    m = re.search(r'\s+\[([GV])\]\s*$', lines[-1])
    if m:
        lines = lines[:-1] + [lines[-1][:m.start()]]
        return lines, m.group(1)
    return lines, None

tables = [v for k, v in items if k == 't']
sigla_t, toc_t = tables[0], tables[1]
verse_tables = tables[2:]

data = {}
data['sigla'] = [[r[0][0], r[1][0]] for r in sigla_t[1:]]
toc = []
for r in toc_t[1:]:
    c = [x[0] for x in r]
    toc.append(dict(n=c[0], en=c[1], es=c[2], pt=c[3], skt=c[4], derge=c[5], verses=c[6]))
data['toc'] = toc

paras = [(i, v) for i, (k, v) in enumerate(items) if k == 'p' and v.strip()]
# ---- front matter
ptxt = [v for _, v in paras]
data['title'] = dict(en=ptxt[0], es=ptxt[1], pt=ptxt[2])
data['title_tib'] = ptxt[3]; data['title_wyl'] = ptxt[4]; data['title_dev'] = ptxt[5]
data['title_iast'] = re.sub(r'\s+\[D\]\s*$', '', ptxt[6]); data['author'] = ptxt[7]
data['source_lines'] = ptxt[8:11]
data['translator_line'] = ptxt[11]
assert ptxt[12] == 'Sigla'
# summaries: after toc footnote, 'Summary' / 'Resumen' / 'Resumo' each followed by paragraphs
def block(start_label, stop_labels):
    idx = ptxt.index(start_label); out = []
    for t in ptxt[idx+1:]:
        if t in stop_labels or t.startswith('Chapter 1:'): break
        out.append(t)
    return out
data['toc_note'] = ptxt[ptxt.index('Karchag · Table of Contents · Tabla de contenidos · Sumário') + 1]
data['summary'] = dict(en=block('Summary', {'Resumen'}), es=block('Resumen', {'Resumo'}), pt=block('Resumo', set()))

# ---- walk body in order
pos = {id(x): i for i, x in enumerate(items)}
chapters = []; cur = None; vt = iter(verse_tables)
i = 0; N = len(items)
def pnext(i):
    while i < N and not (items[i][0] == 'p' and items[i][1].strip()) and items[i][0] != 't': i += 1
    return i
i = pnext(0)
mode = None
final = {}
while i < N:
    k, v = items[i]
    if k == 'p':
        t = v.strip()
        m = re.match(r'^Chapter (\d+): (.+)$', t)
        if m:
            n = int(m.group(1)); nxt = items[pnext(i+1)][1]
            pt_es = nxt.split(' · ')
            ptm = re.match(r'^Cap[ií]tulo \d+: (.+)$', pt_es[0]); esm = re.match(r'^Cap[ií]tulo \d+: (.+)$', pt_es[1])
            dev = items[pnext(pnext(i+1)+1)][1]; iast = re.sub(r'\s+\[V\]\s*$', '', items[pnext(pnext(pnext(i+1)+1)+1)][1])
            cur = dict(n=n, title=dict(en=m.group(2), pt=ptm.group(1), es=esm.group(1)), dev=dev, iast=iast, blocks=[])
            chapters.append(cur)
            i = pnext(pnext(pnext(pnext(i+1)+1)+1)+1); continue
        if t == "Translator's homage (Tibetan only)":
            L = labelled([items[j][1] for j in range(i+1, i+6)])
            cur['blocks'].append(dict(type='homage', **{x.lower(): L[x] for x in L}))
            i = pnext(i+6); continue
        if t == 'Chapter colophon':
            L = labelled([items[j][1] for j in range(i+1, i+6)])
            cur['blocks'].append(dict(type='colophon', **{x.lower(): L[x] for x in L}))
            i = pnext(i+6); continue
        if t == 'Colophon of the Tibetan Translation':
            ptes = items[pnext(i+1)][1].split(' · ')
            derge = items[pnext(pnext(i+1)+1)][1]
            j = pnext(pnext(pnext(i+1)+1)+1); parts = []
            while items[j][1].startswith(('TIB\t', 'WYL\t', 'EN\t', 'PT\t', 'ES\t')):
                parts.append(items[j][1]); j += 1
                while j < N and not items[j][1].strip(): j += 1
            groups = [labelled(parts[x:x+5]) for x in range(0, len(parts), 5)]
            final['tib_colophon'] = dict(title=dict(en=t, pt=ptes[0], es=ptes[1]), derge=re.sub(r'\s*†\s*$', '', derge).strip(), dagger='†' in derge,
                                         parts=[{x.lower(): g[x] for x in g} for g in groups])
            i = j; continue
        if t == 'Editorial Notes':
            break
    else:
        if cur is None:
            i = pnext(i+1); continue
        T = v
        L, R = T[0]
        head = L[0]
        lm = labelled(L[1:]); rm = labelled(R)
        dag = '†' in head
        h = re.sub(r'\s*†\s*$', '', head).strip()
        if head.startswith('Dedication'):
            vid = 'ded'; num = None; derge = '1.1–1.2'; note = 'not numbered in [G]'
        else:
            mm = re.match(r'^(\d+)\.(\d+)\s+\((?:Derge (\d+\.\d+)|(no Derge counterpart))\)', h)
            vid = f'{mm.group(1)}.{mm.group(2)}'; num = vid; derge = mm.group(3); note = mm.group(4)
        skt, sig = siglum(lm['SKT'])
        cur['blocks'].append(dict(type='verse', id=vid, derge=derge, derge_note=note, dagger=dag,
            tib=lm['TIB'], wyl=lm['WYL'], dev=lm['DEV'], skt=skt, sig=sig, en=rm['EN'], pt=rm['PT'], es=rm['ES']))
    i = pnext(i+1)

data['chapters'] = chapters
data.update(final)

# ---- editorial notes (EN + ES alternate; no PT in the source)
ni = [j for j, (kk, vv) in enumerate(items) if kk == 'p' and vv.strip() == 'Editorial Notes'][0]
rest = [vv.strip() for kk, vv in items[ni+1:] if kk == 'p' and vv.strip()]
g0 = rest.index('General'); g1 = rest.index('Notes to verses (†)')
gen = rest[g0+1:g1]; vs = rest[g1+1:]
general = []
for x in range(0, len(gen), 2):
    m = re.match(r'^(\d+)\. (.*)$', gen[x], re.S)
    en = m.group(2); es = gen[x+1]
    general.append(dict(n=int(m.group(1)), en=en, es=es))
verse_notes = []
for x in range(0, len(vs), 2):
    en, es = vs[x], vs[x+1]
    m = re.match(r'^(\d+\.\d+)\. (.*)$', en, re.S)
    if m: verse_notes.append(dict(id=m.group(1), en=m.group(2), es=es))
    else: verse_notes.append(dict(id='colophon', en=re.sub(r'^colophon\.\s*', '', en), es=es))
data['notes_general'] = general; data['notes_verses'] = verse_notes

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nv = sum(1 for c in chapters for b in c['blocks'] if b['type'] == 'verse')
print('chapters', len(chapters), 'verse blocks', nv, 'general notes', len(general), 'verse notes', len(verse_notes))
