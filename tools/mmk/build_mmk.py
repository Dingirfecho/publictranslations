"""Build the Mūlamadhyamakakārikā reading editions into ../../mulamadhyamakakarika/
   all/  Tibetan · Wylie · Devanagari · IAST · English · Português · Español, verse by verse
   en/ es/ pt/  translation-only reading editions
Run:  cd tools/mmk && python3 build_mmk.py
Source text lives in data.json (generated once from the .docx by parse_docx.py)."""
import json, os, re, html, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'mulamadhyamakakarika')
D = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
PTN = json.load(open(os.path.join(HERE, 'notes_pt.json'), encoding='utf-8'))
e = lambda s: html.escape(s, quote=True)
N = len(D['chapters'])

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400'
 '&amp;family=Inter:wght@300;400;500&amp;family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400'
 '&amp;family=Noto+Serif+Tibetan:wght@300;400;500&amp;family=Tiro+Devanagari+Sanskrit:ital@0;1&amp;display=swap">')

def typo(s):
    """Typographic quotes for translation prose only (never for Wylie / IAST)."""
    s = s.replace("'", "’")
    s = re.sub(r'(^|[\s(—\[])’', lambda m: m.group(1) + '‘', s)
    out = []
    for i, ch in enumerate(s):
        if ch == '"':
            prev = s[i-1] if i else ' '
            out.append('“' if (i == 0 or prev in ' (—[‘') else '”')
        else:
            out.append(ch)
    return html.escape(''.join(out), quote=False)

raw = lambda s: html.escape(s, quote=False)
vid = lambda i: 'v' + i.replace('.', '-')
nid = lambda i: 'n' + i.replace('.', '-')

# ------------------------------------------------------------------ UI strings
SRC = {
 'en': D['source_lines'],
 'es': ["Tibetano: Derge Tengyur D3824, dbu ma, tsa 1b–19a (e-text de Esukhia, versión 1905)",
        "Sánscrito [G]: e-text de GRETIL, ingreso de D. Bachman, revisado por R. Mahoney",
        "Sánscrito [V]: Prasannapadā, ed. P. L. Vaidya, Darbhanga 1960 (ingreso del DSBC, vía GRETIL)"],
 'pt': ["Tibetano: Derge Tengyur D3824, dbu ma, tsa 1b–19a (e-text de Esukhia, versão 1905)",
        "Sânscrito [G]: e-text de GRETIL, digitação de D. Bachman, revisada por R. Mahoney",
        "Sânscrito [V]: Prasannapadā, ed. P. L. Vaidya, Darbhanga 1960 (digitação do DSBC, via GRETIL)"],
}
UI = {
 'en': dict(htmllang='en', short='EN', chapter='Chapter', contents='Contents', begin='Begin reading', top='Back to top',
   next='Next chapter', prev='Previous chapter', about='About this edition', summary='Summary', sources='Sources', sigla='Sigla',
   siglum='Siglum', source='Source', notes='Editorial Notes', n_general='General', n_verses='Notes to verses (†)',
   homage="Translator’s homage (Tibetan only)", chcolo='Chapter colophon', ded='Dedication verses', nodv='no Derge counterpart',
   notnum='not numbered in [G]', dag='† marks a verse with an editorial note at the end of the volume.',
   translator=D['translator_line'], footer='A Vajrakula translation · Public translations', note_colo='Colophon',
   nextc='Next', description='Nāgārjuna’s Root Verses on the Middle Way, called Prajñā (Mūlamadhyamakakārikā), translated by Dr. Federico Andino. A scrollable edition for reading on phones.',
   end='End of the text', dagt='Editorial note'),
 'es': dict(htmllang='es', short='ES', chapter='Capítulo', contents='Índice', begin='Comenzar a leer', top='Volver al inicio',
   next='Capítulo siguiente', prev='Capítulo anterior', about='Acerca de esta edición', summary='Resumen', sources='Fuentes', sigla='Siglas',
   siglum='Sigla', source='Fuente', notes='Notas editoriales', n_general='General', n_verses='Notas a los versos (†)',
   homage='Homenaje del traductor (solo en tibetano)', chcolo='Colofón del capítulo', ded='Versos de dedicatoria', nodv='sin equivalente en Derge',
   notnum='sin número en [G]', dag='† señala un verso con nota editorial al final del volumen.',
   translator='Traducción al inglés, portugués y castellano rioplatense: Dr. Federico Andino', footer='Una traducción de Vajrakula · Traducciones públicas', note_colo='Colofón',
   nextc='Siguiente', description='Los Versos Raíz del Camino del Medio, llamados Prajñā (Mūlamadhyamakakārikā) de Nāgārjuna, traducidos por el Dr. Federico Andino. Edición para leer en el celular.',
   end='Fin del texto', dagt='Nota editorial'),
 'pt': dict(htmllang='pt', short='PT', chapter='Capítulo', contents='Índice', begin='Começar a ler', top='Voltar ao início',
   next='Próximo capítulo', prev='Capítulo anterior', about='Sobre esta edição', summary='Resumo', sources='Fontes', sigla='Siglas',
   siglum='Sigla', source='Fonte', notes='Notas editoriais', n_general='Geral', n_verses='Notas aos versos (†)',
   homage='Homenagem do tradutor (somente em tibetano)', chcolo='Colofão do capítulo', ded='Versos de dedicatória', nodv='sem equivalente em Derge',
   notnum='sem número em [G]', dag='† assinala um verso com nota editorial no fim do volume.',
   translator='Tradução para o inglês, o português e o espanhol rio-platense: Dr. Federico Andino', footer='Uma tradução de Vajrakula · Traduções públicas', note_colo='Colofão',
   nextc='Próximo', description='Os Versos Raiz do Caminho do Meio, chamados Prajñā (Mūlamadhyamakakārikā) de Nāgārjuna, traduzidos pelo Dr. Federico Andino. Edição para ler no celular.',
   end='Fim do texto', dagt='Nota editorial'),
}
UI['all'] = dict(UI['en'], htmllang='en', short='ALL',
   description='Nāgārjuna’s Root Verses on the Middle Way (Mūlamadhyamakakārikā) in Tibetan with Wylie, Sanskrit in Devanagari and IAST, English, Portuguese and Spanish, verse by verse. Translated by Dr. Federico Andino.')
PAGES = ['all', 'en', 'es', 'pt']
ALLNAME = {'en': 'All languages', 'es': 'Todas las lenguas', 'pt': 'Todas as línguas', 'all': 'All languages'}

def ch_title(c, l): return c['title'][l]
def lines_join(ls): return ' '.join(ls)

# ------------------------------------------------------------------ blocks
def lyr(cls, label, lines, lang, sg=None, prose=False):
    f = typo if prose else raw
    ps = [f(x) for x in lines]
    if sg: ps[-1] += f'<span class="sg">[{sg}]</span>'
    return (f'<div class="lyr {cls}" lang="{lang}"><b aria-hidden="true">{label}</b><div>'
            + ''.join(f'<p>{p}</p>' for p in ps) + '</div></div>')

def poly_pair(b, with_dev=True):
    s = lyr('tib', 'TIB', b['tib'], 'bo') + lyr('wyl', 'WYL', b['wyl'], 'bo-Latn')
    if with_dev and 'dev' in b:
        s += lyr('dev', 'DEV', b['dev'], 'sa') + lyr('skt', 'SKT', b['skt'], 'sa-Latn', b.get('sig'))
    t = lyr('en', 'EN', b['en'], 'en', prose=True) + lyr('pt', 'PT', b['pt'], 'pt', prose=True) + lyr('es', 'ES', b['es'], 'es', prose=True)
    return f'<div class="src">{s}</div><div class="trs">{t}</div>'

def verse_poly(b, L):
    if b['id'] == 'ded':
        head = f'{e(L["ded"])}<span class="dg">Derge 1.1–1.2 · {e(L["notnum"])}</span>'
        idattr = 'id="ded"'; dg = ''
    else:
        if b['derge']: dgl = f'Derge {b["derge"]}'
        else: dgl = L['nodv']
        head = f'<a href="#{vid(b["id"])}">{b["id"]}</a><span class="dg">{e(dgl)}</span>'
        idattr = f'id="{vid(b["id"])}"'
    dag = f'<a class="dag" id="d{b["id"].replace(".","-")}" href="#{nid(b["id"])}" title="{e(L["dagt"])}">†</a>' if b['dagger'] else ''
    return f'<section class="vs" {idattr}><p class="vn">{head}{dag}</p>{poly_pair(b)}</section>'

def verse_single(b, l, L):
    lines = b[l]
    if b['id'] == 'ded':
        top = f'<p class="sub">{e(L["ded"])}</p>'; idattr = 'id="ded"'; num = ''
    else:
        top = ''; idattr = f'id="{vid(b["id"])}"'
        dag = f'<a class="dag" id="d{b["id"].replace(".","-")}" href="#{nid(b["id"])}" title="{e(L["dagt"])}">†</a>' if b['dagger'] else ''
        num = f'<p class="vn"><a href="#{vid(b["id"])}">{b["id"]}</a>{dag}</p>'
    ps = ''.join(f'<p>{typo(x)}</p>' for x in lines)
    return f'{top}<section class="vs" {idattr}>{num}<div class="verse"><div class="stanza">{ps}</div></div></section>'

def chapter(c, page, L):
    n = c['n']; l = page
    fl = 'en' if page == 'all' else page
    toc = D['toc'][n]          # toc[0] is the homage row
    if page == 'all':
        hdr = (f'<header><p class="folio">{e(L["chapter"])} {n}</p><hr class="taper">'
               f'<h2 id="h{n}" lang="en">{typo(c["title"]["en"])}</h2>'
               f'<p class="alt" lang="es">{typo(c["title"]["es"])}</p><p class="alt" lang="pt">{typo(c["title"]["pt"])}</p>'
               f'<p class="devt" lang="sa">{raw(c["dev"])}</p><p class="iast" lang="sa-Latn">{raw(c["iast"])}</p>'
               f'<p class="folio" style="margin-top:1.1rem">Derge {e(toc["derge"])} · {e(toc["verses"])}</p></header>')
    else:
        hdr = (f'<header><p class="folio">{e(L["chapter"])} {n}</p><hr class="taper">'
               f'<h2 id="h{n}">{typo(c["title"][l])}</h2><p class="iast" lang="sa-Latn">{raw(c["iast"])}</p></header>')
    body = []
    for b in c['blocks']:
        if b['type'] == 'homage':
            if page == 'all':
                body.append(f'<p class="head">{e(L["homage"])}</p>{poly_pair(b, with_dev=False)}')
            else:
                body.append(f'<p class="sub">{e(L["homage"])}</p><div class="verse homage"><div class="stanza"><p>{typo(lines_join(b[l]))}</p></div></div>')
        elif b['type'] == 'verse':
            body.append(verse_poly(b, L) if page == 'all' else verse_single(b, l, L))
        elif b['type'] == 'colophon':
            if page == 'all':
                body.append(f'<p class="head">{e(L["chcolo"])}</p>{poly_pair(b, with_dev=False)}')
            else:
                body.append(f'<p class="colo">{typo(lines_join(b[l]))}</p>')
    prev = f'<a href="#c{n-1}" rel="prev">&larr; {e(L["prev"])}</a>' if n > 1 else ''
    if n < N: nxt = f'<a href="#c{n+1}" rel="next">{e(L["next"])} &rarr;</a>'
    else: nxt = f'<a href="#tibcol" rel="next">{e(D["tib_colophon"]["title"][fl])} &rarr;</a>'
    return (f'<section class="chapter" id="c{n}" aria-labelledby="h{n}">{hdr}\n' + '\n'.join(body) +
            f'\n<div class="end"><span class="dot" role="presentation"></span><nav class="nav" aria-label="{e(L["chapter"])}">{prev}{nxt}</nav></div></section>')

def tibcol(page, L):
    T = D['tib_colophon']; fl = 'en' if page == 'all' else page
    dag = f'<a class="dag" id="d-colophon" href="#n-colophon" title="{e(L["dagt"])}">†</a>' if T['dagger'] else ''
    hdr = f'<header><p class="folio">{e(T["derge"])}{dag}</p><hr class="taper"><h2 id="htc">{typo(T["title"][fl])}</h2>'
    if page == 'all':
        hdr += f'<p class="alt" lang="es">{typo(T["title"]["es"])}</p><p class="alt" lang="pt">{typo(T["title"]["pt"])}</p>'
    hdr += '</header>'
    if page == 'all':
        body = ''.join(f'<div class="vs">{poly_pair(p, with_dev=False)}</div>' for p in T['parts'])
    else:
        body = ''.join(f'<p>{typo(lines_join(p[fl]))}</p>' for p in T['parts'])
    nav = (f'<a href="#c{N}" rel="prev">&larr; {e(L["chapter"])} {N}</a><a href="#notes" rel="next">{e(L["notes"])} &rarr;</a>')
    return (f'<section class="chapter" id="tibcol" aria-labelledby="htc">{hdr}\n{body}\n'
            f'<div class="end"><span class="dot" role="presentation"></span><nav class="nav">{nav}</nav></div></section>')

def lead(txt):
    m = re.match(r'^([^.]{2,45}\.)\s+(.*)$', txt, re.S)
    return f'<strong>{raw(m.group(1))}</strong> {raw(m.group(2))}' if m else raw(txt)

def notes(page, L):
    gen_pt = PTN['general']; ver_pt = PTN['verses']
    def gtxt(g, l): return g['en'] if l == 'en' else g['es'] if l == 'es' else gen_pt[str(g['n'])]
    def vtxt(v, l): return v['en'] if l == 'en' else v['es'] if l == 'es' else ver_pt[v['id']]
    langs = ['en', 'es', 'pt'] if page == 'all' else [page]
    gen = []
    for g in D['notes_general']:
        ps = ''.join(f'<p lang="{l}"{" class=\"l2\"" if i else ""}>' + (f'<span class="k">{g["n"]}</span>' if i == 0 else '') + lead(gtxt(g, l)) + '</p>'
                     for i, l in enumerate(langs))
        gen.append(f'<li id="g{g["n"]}">{ps}</li>')
    ver = []
    for v in D['notes_verses']:
        if v['id'] == 'colophon':
            key = '<a class="k" href="#tibcol">' + e(L['note_colo'] if page != 'all' else 'Colophon') + '</a>'; back = '#d-colophon'
        else:
            key = f'<a class="k" href="#{vid(v["id"])}">{v["id"]}</a>'; back = '#d' + v['id'].replace('.', '-')
        ps = ''
        for i, l in enumerate(langs):
            t = vtxt(v, l)
            ps += f'<p lang="{l}"{" class=\"l2\"" if i else ""}>' + (key if i == 0 else '') + raw(t) + (f'<a class="back" href="{back}" title="↩">↩</a>' if i == len(langs) - 1 else '') + '</p>'
        ver.append(f'<li id="{nid(v["id"]) if v["id"] != "colophon" else "n-colophon"}">{ps}</li>')
    return (f'<section class="notes" id="notes" aria-labelledby="hn"><header><hr class="taper"><h2 id="hn">{e(L["notes"])}</h2></header>'
            f'<h3>{e(L["n_general"])}</h3><ol>{"".join(gen)}</ol><h3>{e(L["n_verses"])}</h3><ul>{"".join(ver)}</ul>'
            f'<div class="end"><span class="dot" role="presentation"></span><nav class="nav"><a href="#tibcol" rel="prev">&larr; {e(D["tib_colophon"]["title"]["en" if page=="all" else page])}</a><a href="#top">{e(L["top"])} &uarr;</a></nav></div></section>')

def front(page, L):
    langs = ['en', 'es', 'pt'] if page == 'all' else [page]
    parts = []
    for l in langs:
        lab = UI[l]['summary']
        parts.append(f'<div lang="{l}"><h3>{e(lab)}</h3>' + ''.join(f'<p>{typo(p)}</p>' for p in D['summary'][l]) + '</div>')
    srcs = ''.join(f'<p>{raw(s)}</p>' for s in (SRC['en'] if page in ('all', 'en') else SRC[page]))
    s = (f'<section class="front" id="about" aria-labelledby="ha"><h2 id="ha">{e(L["about"])}</h2>' + ''.join(parts) +
         f'<h3>{e(L["sources"])}</h3><div class="srcs" lang="{"en" if page in ("all","en") else page}">{srcs}'
         f'<p>{e(L["dag"])}</p></div>')
    if page in ('all', 'en'):
        rows = ''.join(f'<dt id="{"sigla" if i == 0 else "s%d" % i}">{raw(a)}</dt><dd lang="en">{raw(b)}</dd>' for i, (a, b) in enumerate(D['sigla']))
        s += f'<h3>{e(L["sigla"])}</h3><dl class="sigla">{rows}</dl>'
    return s + '</section>'

def title_block(page, L):
    if page == 'all':
        h1 = (f'<h1 lang="en">{raw(D["title"]["en"])}</h1><p class="alt-title" lang="es">{raw(D["title"]["es"])}</p>'
              f'<p class="alt-title" lang="pt">{raw(D["title"]["pt"])}</p>')
    else:
        h1 = f'<h1>{raw(D["title"][page])}</h1>'
    return (f'<header class="title-block"><p class="kicker">Vajrakula</p>{h1}<hr class="taper">'
            f'<p class="sacred tib" lang="bo">{raw(D["title_tib"])}</p><p class="translit" lang="bo-Latn">{raw(D["title_wyl"])}</p>'
            f'<p class="sacred dev" lang="sa">{raw(D["title_dev"])}</p><p class="translit" lang="sa-Latn">{raw(D["title_iast"])}</p>'
            f'<p class="author">{raw(D["author"])}</p><p class="by">{raw(L["translator"])}</p>'
            f'<a class="begin" href="#c1">{e(L["begin"])}</a></header>')

def page_html(page):
    L = UI[page]; fl = 'en' if page == 'all' else page
    toc_items = [f'<li><a href="#about"><b>—</b><span>{e(L["about"])}</span></a></li>']
    for c in D['chapters']:
        sub = f'<small>{e(c["title"]["es"])} · {e(c["title"]["pt"])}</small>' if page == 'all' else ''
        toc_items.append(f'<li><a href="#c{c["n"]}"><b>{c["n"]}</b><span>{e(c["title"][fl])}{sub}</span></a></li>')
    toc_items.append(f'<li><a href="#tibcol"><b>—</b><span>{e(D["tib_colophon"]["title"][fl])}</span></a></li>')
    toc_items.append(f'<li><a href="#notes"><b>—</b><span>{e(L["notes"])}</span></a></li>')
    langs = ''.join(f'<a href="../{k}/"{" aria-current=\"page\"" if k == page else ""}'
                    + (f' hreflang="{k}" lang="{k}"' if k != 'all' else f' aria-label="{e(ALLNAME[fl])}" title="{e(ALLNAME[fl])}"')
                    + f'>{UI[k]["short"]}</a>' for k in ['all', 'en', 'es', 'pt'])
    alt = ''.join(f'<link rel="alternate" hreflang="{k}" href="../{k}/">' for k in ['en', 'es', 'pt'])
    title = D['title'][fl]
    chapters = '\n'.join(chapter(c, page, L) for c in D['chapters'])
    return f'''<!DOCTYPE html>
<html lang="{L["htmllang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0E1525">
<meta name="color-scheme" content="dark">
<title>{e(title)}</title>
<meta name="description" content="{e(L["description"])}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(L["description"])}"><meta property="og:type" content="book">
{alt}
{FONTS}
<link rel="stylesheet" href="../assets/style.css">
</head>
<body id="top"{' class="poly"' if page == 'all' else ''}>
<a class="skip" href="#c1">{e(L["begin"])}</a>
<div class="bar"><div class="bar-in">
<details><summary>{e(L["contents"])}</summary><nav class="toc" aria-label="{e(L["contents"])}"><ol>{"".join(toc_items)}</ol></nav></details>
<nav class="langs" aria-label="Language">{langs}</nav>
</div></div>
{title_block(page, L)}
<main id="main"{' class="poly"' if page == 'all' else ''}>
{front(page, L)}
{chapters}
{tibcol(page, L)}
{notes(page, L)}
</main>
<footer class="footer">{e(L["footer"])}</footer>
<script>
/* keep the chapter or verse when switching language */
(function(){{var a=document.querySelectorAll('.langs a');function s(){{for(var i=0;i<a.length;i++){{a[i].href=a[i].href.split('#')[0]+location.hash}}}}s();window.addEventListener('hashchange',s);
var d=document.querySelector('.bar details');if(d){{d.addEventListener('click',function(ev){{if(ev.target.closest&&ev.target.closest('.toc a')){{d.removeAttribute('open')}}}});}}}})();
</script>
</body>
</html>'''

# ------------------------------------------------------------------ write
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
base_css = open(os.path.join(HERE, '..', 'style.css'), encoding='utf-8').read()
extra_css = open(os.path.join(HERE, 'extra.css'), encoding='utf-8').read()
open(os.path.join(OUT, 'assets', 'style.css'), 'w', encoding='utf-8').write(base_css + '\n' + extra_css)
for p in PAGES:
    os.makedirs(os.path.join(OUT, p), exist_ok=True)
    open(os.path.join(OUT, p, 'index.html'), 'w', encoding='utf-8').write(page_html(p))
    print(p, os.path.getsize(os.path.join(OUT, p, 'index.html')) // 1024, 'KB')

chooser = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#0E1525"><meta name="color-scheme" content="dark">
<title>Root Verses on the Middle Way, Called Prajñā</title>
''' + FONTS + '''
<link rel="stylesheet" href="assets/style.css">
<script>(function(){var l=(navigator.language||'en').slice(0,2).toLowerCase();var m={es:'es',pt:'pt'};var t=m[l]||'en';if(!/[?&]choose/.test(location.search))location.replace(t+'/'+location.hash);})();</script>
</head><body><main class="title-block" style="padding-top:16vh">
<p class="kicker">Vajrakula</p><h1>Root Verses on the Middle Way, Called Prajñā</h1><hr class="taper">
<p class="sacred tib" lang="bo">''' + raw(D['title_tib']) + '''</p><p class="translit" lang="sa-Latn">Nāgārjuna · Mūlamadhyamakakārikā</p>
<nav class="choose" aria-label="Language"><a href="en/" lang="en">English</a><a href="es/" lang="es">Español</a><a href="pt/" lang="pt">Português</a><a href="all/" lang="en">All languages · Todas · Todas</a></nav>
</main></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(chooser)
print('done')
