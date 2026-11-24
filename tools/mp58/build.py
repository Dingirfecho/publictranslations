"""Build the MP58 reading editions into ../../eight-vidyadharas/
   all/  Tibetan · Wylie · Español · English · Português, segment by segment (numbered as in the source PDF)
   en/ es/ pt/  translation-only reading editions
Run:  cd tools/mp58 && python3 build.py
Source text: data.json (generated from the PDF by parse_pdf.py)."""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'eight-vidyadharas')
IT = {i['n']: i for i in json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))['items']}
e = lambda s: html.escape(s, quote=True)
raw = lambda s: html.escape(s, quote=False)
wyl = lambda s: raw(s.replace('_', ' '))

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400'
 '&amp;family=Inter:wght@300;400;500&amp;family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400'
 '&amp;family=Noto+Serif+Tibetan:wght@300;400;500&amp;display=swap">')

def typo(s):
    """Typographic quotes for translation prose only (never for Wylie)."""
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

# Two parts. 'title' is the item that titles the part; 'opening' an introductory line; 'body' the verse segments; 'colo' the colophon; 'end' the closing Mangalam.
# Item 40 is a bare section mark and is not shown.
PARTS = [dict(n=1, title=1, opening=2, body=list(range(3, 38)), colo=[38], end=39),
         dict(n=2, title=41, opening=None, body=list(range(42, 78)), colo=[78, 79], end=80)]
ROMAN = ['I', 'II']
FOLIO = 'MP58 · 5-43-1a – 5-43-3b'

UI = {
 'en': dict(htmllang='en', short='EN', part='Part', contents='Contents', begin='Begin reading', top='Back to top',
   next='Next part', prev='Previous part', colophon='Colophon', end='End of the text',
   translator='Translation: Lama Fede Andino', footer='A Vajrakula translation · Public translations',
   description='Two supplications from Mipham’s collected works (text MP58): to the Eight Vidyadharas of the Noble Land and to the Eight Great Siddhas of Tibet. Translated by Lama Fede Andino. A scrollable edition for reading on phones.',
   lede='Includes the supplication to the Eight Great Siddhas of Tibet (Part II).', allname='All languages'),
 'es': dict(htmllang='es', short='ES', part='Parte', contents='Índice', begin='Comenzar a leer', top='Volver al inicio',
   next='Parte siguiente', prev='Parte anterior', colophon='Colofón', end='Fin del texto',
   translator='Traducción: Lama Fede Andino', footer='Una traducción de Vajrakula · Traducciones públicas',
   description='Dos súplicas de las obras reunidas de Mipham (texto MP58): a los Ocho Vidyadharas de la Tierra Noble y a los Ocho Grandes Siddhas del Tíbet. Traducidas por el Lama Fede Andino. Edición para leer en el celular.',
   lede='Incluye la súplica a los Ocho Grandes Siddhas del Tíbet (Parte II).', allname='Todas las lenguas'),
 'pt': dict(htmllang='pt', short='PT', part='Parte', contents='Índice', begin='Começar a ler', top='Voltar ao início',
   next='Próxima parte', prev='Parte anterior', colophon='Colofão', end='Fim do texto',
   translator='Tradução: Lama Fede Andino', footer='Uma tradução de Vajrakula · Traduções públicas',
   description='Duas súplicas das obras reunidas de Mipham (texto MP58): aos Oito Vidyadharas da Terra Nobre e aos Oito Grandes Siddhas do Tibete. Traduzidas pelo Lama Fede Andino. Edição para ler no celular.',
   lede='Inclui a súplica aos Oito Grandes Siddhas do Tibete (Parte II).', allname='Todas as línguas'),
}
UI['all'] = dict(UI['en'], short='ALL', htmllang='en',
   description='Two supplications from Mipham’s collected works (text MP58) in Tibetan with Wylie, Español, English and Português, segment by segment. Translated by Lama Fede Andino.',
   lede='Includes the supplication to the Eight Great Siddhas of Tibet (Part II).')
PAGES = ['all', 'en', 'es', 'pt']
vid = lambda n: 'v%02d' % n

def lyr(cls, label, text, lang, prose=False):
    body = typo(text) if prose else (wyl(text) if cls == 'wyl' else raw(text))
    return f'<div class="lyr {cls}" lang="{lang}"><b aria-hidden="true">{label}</b><div><p>{body}</p></div></div>'

def poly(n):
    i = IT[n]
    src = lyr('tib', 'TIB', i['tib'], 'bo') + lyr('wyl', 'WYL', i['wyl'], 'bo-Latn')
    trs = lyr('es', 'ES', i['es'], 'es', True) + lyr('en', 'EN', i['en'], 'en', True) + lyr('pt', 'PT', i['pt'], 'pt', True)
    return f'<div class="src">{src}</div><div class="trs">{trs}</div>'

def block_all(n):
    i = IT[n]
    return (f'<section class="vs" id="{vid(n)}"><p class="vn"><a href="#{vid(n)}">{n:02d}</a><span class="dg">{e(i["folio"])}</span></p>'
            f'{poly(n)}</section>')

def part_title(p, page, L):
    t = IT[p['title']]; fl = 'en' if page == 'all' else page
    hdr = f'<header><p class="folio">{e(L["part"])} {ROMAN[p["n"]-1]}</p><hr class="taper">'
    if page == 'all':
        hdr += (f'<h2 id="h{p["n"]}" lang="es">{typo(t["es"])}</h2><p class="alt" lang="en">{typo(t["en"])}</p><p class="alt" lang="pt">{typo(t["pt"])}</p>'
                f'<p class="sacred tib" lang="bo">{raw(t["tib"])}</p><p class="translit" lang="bo-Latn">{wyl(t["wyl"])}</p>')
    else:
        hdr += f'<h2 id="h{p["n"]}">{typo(t[fl])}</h2><p class="sacred tib" lang="bo">{raw(t["tib"])}</p>'
    return hdr + '</header>'

def part(p, page, L):
    fl = 'en' if page == 'all' else page
    k = p['n']
    parts_html = [part_title(p, page, L)]
    if page == 'all':
        if p['opening']: parts_html.append(block_all(p['opening']))
        for n in p['body']: parts_html.append(block_all(n))
        parts_html.append(f'<p class="head">{e(L["colophon"])}</p>')
        for n in p['colo']: parts_html.append(block_all(n))
        parts_html.append(f'<div class="mangalam">{block_all(p["end"])}</div>')
    else:
        if p['opening']:
            parts_html.append(f'<p class="opening" id="{vid(p["opening"])}">{typo(IT[p["opening"]][fl])}</p>')
        stanzas = ''.join(f'<div class="stanza" id="{vid(n)}"><p>{typo(IT[n][fl])}</p></div>' for n in p['body'])
        parts_html.append(f'<div class="verse run">{stanzas}</div>')
        colo = ' '.join(IT[n][fl] for n in p['colo'])
        parts_html.append(f'<p class="colo" id="{vid(p["colo"][0])}">{typo(colo)}</p>')
        parts_html.append(f'<p class="mangalam" id="{vid(p["end"])}">{typo(IT[p["end"]][fl])}</p>')
    prev = f'<a href="#p{k-1}" rel="prev">&larr; {e(L["prev"])}</a>' if k > 1 else ''
    nxt = f'<a href="#p{k+1}" rel="next">{e(L["next"])} &rarr;</a>' if k < len(PARTS) else f'<a href="#top">{e(L["top"])} &uarr;</a>'
    parts_html.append(f'<div class="end"><span class="dot" role="presentation"></span><nav class="nav" aria-label="{e(L["part"])}">{prev}{nxt}</nav></div>')
    return f'<section class="chapter" id="p{k}" aria-labelledby="h{k}">' + '\n'.join(x for x in parts_html if x) + '</section>'

def title_block(page, L):
    t = IT[1]; fl = 'en' if page == 'all' else page
    if page == 'all':
        h1 = (f'<h1 lang="es">{typo(t["es"])}</h1><p class="alt-title" lang="en">{typo(t["en"])}</p>'
              f'<p class="alt-title" lang="pt">{typo(t["pt"])}</p>')
    else:
        h1 = f'<h1>{typo(t[fl])}</h1>'
    return (f'<header class="title-block"><p class="kicker">Vajrakula</p>{h1}<hr class="taper">'
            f'<p class="sacred tib" lang="bo">{raw(t["tib"])}</p><p class="translit" lang="bo-Latn">{wyl(t["wyl"])}</p>'
            f'<p class="author">Mipham</p><p class="by">{e(FOLIO)}</p><p class="by">{e(L["translator"])}</p>'
            f'<p class="lede">{e(L["lede"])}</p>'
            f'<a class="begin" href="#p1">{e(L["begin"])}</a></header>')

def page_html(page):
    L = UI[page]; fl = 'en' if page == 'all' else page
    toc = []
    for p in PARTS:
        t = IT[p['title']]
        sub = f'<small>{e(t["en"])} · {e(t["pt"])}</small>' if page == 'all' else ''
        toc.append(f'<li><a href="#p{p["n"]}"><b>{e(L["part"])} {ROMAN[p["n"]-1]}</b><span>{e(t["es" if page == "all" else fl])}{sub}</span></a></li>')
    langs = ''.join(f'<a href="../{k}/"{" aria-current=\"page\"" if k == page else ""}'
                    + (f' hreflang="{k}" lang="{k}"' if k != 'all' else f' aria-label="{e(UI[fl]["allname"])}" title="{e(UI[fl]["allname"])}"')
                    + f'>{UI[k]["short"]}</a>' for k in PAGES_ORDER)
    alt = ''.join(f'<link rel="alternate" hreflang="{k}" href="../{k}/">' for k in ['es', 'en', 'pt'])
    title = IT[1]['es' if page == 'all' else fl]
    chapters = '\n'.join(part(p, page, L) for p in PARTS)
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
<a class="skip" href="#p1">{e(L["begin"])}</a>
<div class="bar"><div class="bar-in">
<details><summary>{e(L["contents"])}</summary><nav class="toc" aria-label="{e(L["contents"])}"><ol>{"".join(toc)}</ol></nav></details>
<nav class="langs" aria-label="Language">{langs}</nav>
</div></div>
{title_block(page, L)}
<main id="main"{' class="poly"' if page == 'all' else ''}>
{chapters}
<section class="colophon" aria-label="{e(L["end"])}"><hr class="taper"><p class="folio" style="margin-top:2rem">{e(L["end"])}</p></section>
</main>
<footer class="footer">{e(L["footer"])}</footer>
<script>
/* keep the part or segment when switching language */
(function(){{var a=document.querySelectorAll('.langs a');function s(){{for(var i=0;i<a.length;i++){{a[i].href=a[i].href.split('#')[0]+location.hash}}}}s();window.addEventListener('hashchange',s);
var d=document.querySelector('.bar details');if(d){{d.addEventListener('click',function(ev){{if(ev.target.closest&&ev.target.closest('.toc a')){{d.removeAttribute('open')}}}});}}}})();
</script>
</body>
</html>'''

PAGES_ORDER = ['all', 'es', 'en', 'pt']
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
base_css = open(os.path.join(HERE, '..', 'style.css'), encoding='utf-8').read()
extra_css = open(os.path.join(HERE, 'extra.css'), encoding='utf-8').read()
open(os.path.join(OUT, 'assets', 'style.css'), 'w', encoding='utf-8').write(base_css + '\n' + extra_css)
for p in PAGES:
    os.makedirs(os.path.join(OUT, p), exist_ok=True)
    open(os.path.join(OUT, p, 'index.html'), 'w', encoding='utf-8').write(page_html(p))
    print(p, os.path.getsize(os.path.join(OUT, p, 'index.html')) // 1024, 'KB')

chooser = '''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#0E1525"><meta name="color-scheme" content="dark">
<title>''' + raw(IT[1]['es']) + '''</title>
''' + FONTS + '''
<link rel="stylesheet" href="assets/style.css">
<script>(function(){var l=(navigator.language||'es').slice(0,2).toLowerCase();var m={es:'es',pt:'pt',en:'en'};var t=m[l]||'en';if(!/[?&]choose/.test(location.search))location.replace(t+'/'+location.hash);})();</script>
</head><body><main class="title-block" style="padding-top:16vh">
<p class="kicker">Vajrakula</p><h1>''' + raw(IT[1]['es']) + '''</h1><hr class="taper">
<p class="sacred tib" lang="bo">''' + raw(IT[1]['tib']) + '''</p><p class="translit">Mipham · MP58</p>
<nav class="choose" aria-label="Language"><a href="es/" lang="es">Español</a><a href="en/" lang="en">English</a><a href="pt/" lang="pt">Português</a><a href="all/" lang="en">Tibetan · Wylie · ES · EN · PT</a></nav>
</main></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(chooser)
print('done')
