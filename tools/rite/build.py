"""Build the Lotus Samādhi Repentance reading edition (en/es/pt).

Run from anywhere:  python3 tools/rite/build.py
Reads  tools/rite/content/{en,es,pt}.txt  (typed lines  TYPE|text ; '=====' splits Part I / Part II)
Writes lotus-repentance-rite/{index.html, en|es|pt/index.html, assets/}.
English is the canonical structure; any other language must match it type-for-type.
"""
import os, re, html, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from meta import LANGS

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BASE = os.path.join(ROOT, 'lotus-repentance-rite')
TOOLS = os.path.join(HERE, '..')
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&amp;family=Inter:wght@300;400;500&amp;family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400&amp;display=swap">')
ROMAN = ['I', 'II']


def typo(s):
    s = s.replace("'", "’")
    s = re.sub(r'(^|[\s(—\[*])’', lambda m: m.group(1) + '‘', s)
    out = []
    for i, ch in enumerate(s):
        if ch == '"':
            prev = s[i-1] if i else ' '
            out.append('“' if (i == 0 or prev in ' (—[‘*') else '”')
        else:
            out.append(ch)
    s = html.escape(''.join(out), quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s


def load(lang):
    p = os.path.join(HERE, 'content', f'{lang}.txt')
    items = []
    for n, line in enumerate(open(p, encoding='utf-8').read().rstrip('\n').split('\n'), 1):
        if line == '=====':
            items.append(('SPLIT', '')); continue
        if '|' not in line:
            raise SystemExit(f'{lang}.txt line {n}: no TYPE| prefix')
        t, x = line.split('|', 1)
        items.append((t, x))
    return items


def parse(items):
    """-> list of parts; part = {opener:[(t,x)], sections:[{h2, body:[(t,x)]}], colophon:str|None}"""
    parts = [{'opener': [], 'sections': [], 'colophon': None}]
    for t, x in items:
        part = parts[-1]
        if t == 'SPLIT':
            parts.append({'opener': [], 'sections': [], 'colophon': None}); continue
        if t == 'H2':
            part['sections'].append({'h2': x, 'body': []}); continue
        if t == 'CO':
            part['colophon'] = x; continue
        if not part['sections']:
            part['opener'].append((t, x))
        else:
            part['sections'][-1]['body'].append((t, x))
    return parts


def render_body(body, ids):
    out = []; i = 0
    while i < len(body):
        t, x = body[i]
        if t == 'V':
            out.append('<div class="verse"><div class="stanza">')
            while i < len(body) and body[i][0] in ('V', 'VE'):
                out.append(f'<p>{typo(body[i][1])}</p>')
                if body[i][0] == 'VE' and i + 1 < len(body) and body[i+1][0] in ('V', 'VE'):
                    out.append('</div><div class="stanza">')
                i += 1
            out.append('</div></div>'); continue
        if t in ('OL', 'UL'):
            tag = t.lower()
            out.append(f'<{tag}>')
            while i < len(body) and body[i][0] == t:
                out.append(f'<li>{typo(body[i][1])}</li>'); i += 1
            out.append(f'</{tag}>'); continue
        if t == 'H3':
            out.append(f'<h3 id="{ids.pop(0)}">{typo(x)}</h3>')
        elif t == 'H4':
            out.append(f'<h4>{typo(x)}</h4>')
        elif t == 'C':
            out.append(f'<p class="chant">{typo(x)}</p>')
        elif t == 'PE':
            out.append(f'<p class="endline">{typo(x)}</p>')
        else:
            out.append(f'<p>{typo(x)}</p>')
        i += 1
    return '\n'.join(out)


def add_dropcap(body):
    for m in re.finditer(r'<p>(.*?)</p>', body):
        if len(re.sub('<[^>]+>', '', m.group(1)).split()) >= 20:
            return body[:m.start()] + '<p class="dc">' + m.group(1) + '</p>' + body[m.end():]
        if m.start() > 3000: break
    return body


def page(lang, parts):
    L = LANGS[lang]; e = html.escape
    # 1. build the flat list of sections (part openers + H2 sections) with ids
    flat = []   # dicts: id, kind, title, h3s[(id,title)]
    n = 0
    for pi, part in enumerate(parts):
        n += 1
        title = next(x for t, x in part['opener'] if t == 'PT')
        flat.append({'id': f's{n}', 'kind': 'part', 'title': title, 'pi': pi, 'h3': []})
        for sec in part['sections']:
            n += 1
            h3 = []
            for t, x in sec['body']:
                if t == 'H3':
                    h3.append((f's{n}-{len(h3)+1}', x))
            flat.append({'id': f's{n}', 'kind': 'sec', 'title': sec['h2'], 'pi': pi, 'h3': h3, 'sec': sec})
    # 2. table of contents
    toc = []
    for f in flat:
        if f['kind'] == 'part':
            toc.append(f'<li class="l0"><a href="#{f["id"]}"><b>{e(L["part"])} {ROMAN[f["pi"]]}</b><span>{e(f["title"])}</span></a></li>')
        else:
            toc.append(f'<li class="l1"><a href="#{f["id"]}"><span>{e(f["title"])}</span></a></li>')
            for hid, ht in f['h3']:
                toc.append(f'<li class="l2"><a href="#{hid}"><span>{e(ht)}</span></a></li>')
    langs = ''.join(f'<a href="../{k}/" hreflang="{k}" lang="{k}"{" aria-current=\"page\"" if k == lang else ""}>{v["short"]}</a>' for k, v in LANGS.items())
    # 3. sections
    secs = []
    for idx, f in enumerate(flat):
        prev = f'<a href="#{flat[idx-1]["id"]}" rel="prev">&larr; {e(L["prev"])}</a>' if idx > 0 else ''
        nxt = (f'<a href="#{flat[idx+1]["id"]}" rel="next">{e(L["next"])} &rarr;</a>' if idx < len(flat) - 1
               else f'<a href="#top">{e(L["top"])} &uarr;</a>')
        end = f'<div class="end"><span class="dot" role="presentation"></span><nav class="nav" aria-label="{e(L["nav"])}">{prev}{nxt}</nav></div>'
        if f['kind'] == 'part':
            part = parts[f['pi']]
            subs = ''.join(f'<p class="sub">{typo(x)}</p>' for t, x in part['opener'] if t == 'PS')
            attr = ''.join(f'<p class="attr">{typo(x)}</p>' for t, x in part['opener'] if t == 'PC')
            secs.append(f'''<section class="chapter part" id="{f["id"]}" aria-labelledby="h{f["id"]}">
<header><p class="folio">{e(L["part"])} {ROMAN[f["pi"]]}</p><hr class="taper"><h2 id="h{f["id"]}">{typo(f["title"])}</h2>{subs}</header>
{attr}
{end}
</section>''')
        else:
            sec = f['sec']
            body = add_dropcap(render_body(sec['body'], [h for h, _ in f['h3']]))
            colo = ''
            last_of_part = idx == len(flat) - 1 or flat[idx+1]['kind'] == 'part'
            part = parts[f['pi']]
            if last_of_part and part['colophon']:
                colo = f'<div class="colophon"><hr class="taper"><p class="folio">{e(L["colophon_label"])}</p><p>{typo(part["colophon"])}</p><hr class="taper"></div>'
            secs.append(f'''<section class="chapter" id="{f["id"]}" aria-labelledby="h{f["id"]}">
<header><h2 id="h{f["id"]}">{typo(f["title"])}</h2></header>
{body}
{colo}
{end}
</section>''')
    alt = ''.join(f'<link rel="alternate" hreflang="{k}" href="../{k}/">' for k in LANGS)
    doc = f'''<!DOCTYPE html>
<html lang="{L["htmllang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0E1525">
<meta name="color-scheme" content="dark">
<title>{e(L["title"])}: {e(L["subtitle"])}</title>
<meta name="description" content="{e(L["description"])}">
<meta property="og:title" content="{e(L["title"])}"><meta property="og:description" content="{e(L["description"])}"><meta property="og:type" content="book">
<meta property="og:image" content="../assets/cover.jpg">
{alt}
{FONTS}
<link rel="stylesheet" href="../assets/style.css">
<link rel="stylesheet" href="../assets/extra.css">
</head>
<body id="top">
<a class="skip" href="#s1">{e(L["begin"])}</a>
<div class="bar"><div class="bar-in">
<details><summary>{e(L["contents"])}</summary><nav class="toc" aria-label="{e(L["contents"])}"><ol>{''.join(toc)}</ol></nav></details>
<nav class="langs" aria-label="Language">{langs}</nav>
</div></div>
<figure class="cover"><img src="../assets/cover.jpg" alt="{e(L["img_alt"])}" width="1400" height="755" decoding="async"></figure>
<header class="title-block">
<p class="kicker">Vajrakula</p>
<h1>{e(L["title"])}</h1>
<p class="label kicker" style="margin:0">{e(L["subtitle"])}</p>
<hr class="taper">
<p class="by">{e(L["translator"])}</p>
<p class="by"><a href="{e(L["sutra_link"])}">{e(L["sutra_note"])}</a></p>
<a class="begin" href="#s1">{e(L["begin"])}</a>
</header>
<main id="main">
{chr(10).join(secs)}
<section class="colophon" aria-label="{e(L["end"])}"><hr class="taper"><p class="folio" style="margin-top:2rem">{e(L["end"])}</p></section>
</main>
<footer class="footer">{e(L["footer"])}</footer>
<script>
/* keep the section when switching language */
(function(){{var a=document.querySelectorAll('.langs a');function s(){{for(var i=0;i<a.length;i++){{a[i].href=a[i].href.split('#')[0]+location.hash}}}}s();window.addEventListener('hashchange',s);
var d=document.querySelector('.bar details');if(d){{d.addEventListener('click',function(ev){{if(ev.target.closest&&ev.target.closest('.toc a')){{d.removeAttribute('open')}}}});}}}})();
</script>
</body>
</html>'''
    os.makedirs(os.path.join(BASE, lang), exist_ok=True)
    open(os.path.join(BASE, lang, 'index.html'), 'w', encoding='utf-8').write(doc)


def main():
    en = load('en')
    for lang in LANGS:
        items = load(lang)
        if [t for t, _ in items] != [t for t, _ in en]:
            for i, (a, b) in enumerate(zip(en, items), 1):
                if a[0] != b[0]:
                    raise SystemExit(f'{lang}.txt line {i}: type {b[0]} != English {a[0]}')
            raise SystemExit(f'{lang}.txt: {len(items)} lines vs English {len(en)}')
        page(lang, parse(items))
        print(lang, 'ok', len(items), 'lines')
    os.makedirs(os.path.join(BASE, 'assets'), exist_ok=True)
    shutil.copy(os.path.join(TOOLS, 'style.css'), os.path.join(BASE, 'assets', 'style.css'))
    shutil.copy(os.path.join(HERE, 'extra.css'), os.path.join(BASE, 'assets', 'extra.css'))
    shutil.copy(os.path.join(HERE, 'cover.jpg'), os.path.join(BASE, 'assets', 'cover.jpg'))
    title = LANGS['en']['title'] + ': ' + LANGS['en']['subtitle']
    chooser = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#0E1525"><meta name="color-scheme" content="dark">
<title>''' + html.escape(title) + '''</title>
''' + FONTS + '''
<link rel="stylesheet" href="assets/style.css">
<script>(function(){var l=(navigator.language||'en').slice(0,2).toLowerCase();var m={es:'es',pt:'pt'};var t=m[l]||'en';if(!/[?&]choose/.test(location.search))location.replace(t+'/'+location.hash);})();</script>
</head><body><main class="title-block" style="padding-top:20vh">
<p class="kicker">Vajrakula</p><h1>''' + html.escape(LANGS['en']['title']) + '''</h1><hr class="taper">
<nav class="choose" aria-label="Language"><a href="en/" lang="en">English</a><a href="es/" lang="es">Español</a><a href="pt/" lang="pt">Português</a></nav>
</main></body></html>'''
    open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(chooser)


main()
