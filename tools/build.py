import json, os, re, html, shutil, sys
from meta import LANGS, COLOPHON, ROMAN
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lotus-sutra')
structure = json.load(open('structure.json'))
N = 28
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&amp;family=Inter:wght@300;400;500&amp;family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400&amp;display=swap">')

def typo(s, lang):
    s = s.replace("'", "’")
    s = re.sub(r'(^|[\s(—\[])’', lambda m: m.group(1) + '‘', s)
    out = []; 
    for i, ch in enumerate(s):
        if ch == '"':
            prev = s[i-1] if i else ' '
            out.append('“' if (i == 0 or prev in ' (—[‘') else '”')
        else: out.append(ch)
    return html.escape(''.join(out), quote=False)

def load(lang, n):
    p = f'content/{lang}/ch{n:02d}.txt'
    if not os.path.exists(p): return None
    lines = open(p, encoding='utf-8').read().rstrip('\n').split('\n')
    if len(lines) != len(structure[str(n)]['types']):
        print(f'WARN {lang} ch{n}: {len(lines)} lines vs {len(structure[str(n)]["types"])} expected -> using English', file=sys.stderr)
        return None
    return lines

def render_body(lines, types, ends, lang):
    out = []; i = 0
    while i < len(lines):
        t = types[i]
        if t == 'v':
            out.append('<div class="verse">'); out.append('<div class="stanza">')
            while i < len(lines) and types[i] == 'v':
                out.append(f'<p>{typo(lines[i], lang)}</p>')
                if ends[i] and i+1 < len(lines) and types[i+1] == 'v':
                    out.append('</div><div class="stanza">')
                i += 1
            out.append('</div></div>')
        elif t == 'sub':
            out.append(f'<h3>{typo(lines[i], lang)}</h3>'); i += 1
        else:
            out.append(f'<p>{typo(lines[i], lang)}</p>'); i += 1
    return '\n'.join(out)

def add_dropcap(body):
    for m in re.finditer(r'<p>(.*?)</p>', body):
        if len(re.sub('<[^>]+>','',m.group(1)).split()) >= 20:
            return body[:m.start()] + '<p class="dc">' + m.group(1) + '</p>' + body[m.end():]
        if m.start() > 3000: break
    return body

def page(lang):
    L = LANGS[lang]; e = html.escape
    toc = ''.join(f'<li><a href="#c{n}"><b>{ROMAN[n-1]}</b><span>{e(L["chapters"][n-1])}</span></a></li>' for n in range(1, N+1))
    langs = ''.join(f'<a href="../{k}/" hreflang="{k}" lang="{k}"{" aria-current=\"page\"" if k==lang else ""}>{v["short"]}</a>' for k, v in LANGS.items())
    secs = []; missing = []
    for n in range(1, N+1):
        lines = load(lang, n); fb = False
        if lines is None: lines = load('en', n); fb = lang != 'en'
        if fb: missing.append(n)
        s = structure[str(n)]
        body = render_body(lines, s['types'], s['end'], lang)
        body = add_dropcap(body)
        notice = f'<p class="notice" lang="{lang}">{e(L["fallback"])}</p>' if fb else ''
        prev = f'<a href="#c{n-1}" rel="prev">&larr; {e(L["prev"])}</a>' if n > 1 else ''
        nxt = f'<a href="#c{n+1}" rel="next">{e(L["next"])} &rarr;</a>' if n < N else f'<a href="#top">{e(L["top"])} &uarr;</a>'
        secs.append(f'''<section class="chapter" id="c{n}" aria-labelledby="h{n}"{' lang="en"' if fb else ''}>
<header><p class="folio">{e(L["chapter"])} {ROMAN[n-1]}</p><hr class="taper"><h2 id="h{n}">{e(L["chapters"][n-1] if not fb else L["chapters"][n-1])}</h2></header>
{notice}
{body}
<div class="end"><span class="dot" role="presentation"></span><nav class="nav" aria-label="{e(L["chapter"])}">{prev}{nxt}</nav></div>
</section>''')
    alt = ''.join(f'<link rel="alternate" hreflang="{k}" href="../{k}/">' for k in LANGS)
    doc = f'''<!DOCTYPE html>
<html lang="{L["htmllang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0E1525">
<meta name="color-scheme" content="dark">
<title>{e(L["title"])}</title>
<meta name="description" content="{e(L["description"])}">
<meta property="og:title" content="{e(L["title"])}"><meta property="og:description" content="{e(L["description"])}"><meta property="og:type" content="book">
<meta property="og:image" content="../assets/cover.jpg">
{alt}
{FONTS}
<link rel="stylesheet" href="../assets/style.css">
</head>
<body id="top">
<a class="skip" href="#c1">{e(L["begin"])}</a>
<div class="bar"><div class="bar-in">
<details><summary>{e(L["contents"])}</summary><nav class="toc" aria-label="{e(L["contents"])}"><ol>{toc}</ol></nav></details>
<nav class="langs" aria-label="Language">{langs}</nav>
</div></div>
<figure class="cover"><img src="../assets/cover.jpg" alt="{e(L["img_alt"])}" width="1400" height="753" decoding="async"></figure>
<header class="title-block">
<p class="kicker">Vajrakula</p>
<h1>{e(L["title"])}</h1>
<p class="label kicker" style="margin:0">{e(L["subtitle"])}</p>
<hr class="taper">
<p class="by">{e(L["translator"])}</p>
<a class="begin" href="#c1">{e(L["begin"])}</a>
</header>
<main id="main">
{chr(10).join(secs)}
<section class="colophon" aria-label="{e(L["colophon_label"])}"><hr class="taper"><p class="folio">{e(L["colophon_label"])}</p><p>{e(COLOPHON[lang])}</p><hr class="taper"><p class="folio" style="margin-top:2rem">{e(L["end"])}</p></section>
</main>
<footer class="footer">{e(L["footer"])}</footer>
<script>
/* keep the chapter when switching language */
(function(){{var a=document.querySelectorAll('.langs a');function s(){{for(var i=0;i<a.length;i++){{a[i].href=a[i].href.split('#')[0]+location.hash}}}}s();window.addEventListener('hashchange',s);
var d=document.querySelector('.bar details');if(d){{d.addEventListener('click',function(ev){{if(ev.target.closest&&ev.target.closest('.toc a')){{d.removeAttribute('open')}}}});}}}})();
</script>
</body>
</html>'''
    os.makedirs(f'{BASE}/{lang}', exist_ok=True)
    open(f'{BASE}/{lang}/index.html', 'w', encoding='utf-8').write(doc)
    return missing

os.makedirs(f'{BASE}/assets', exist_ok=True)
shutil.copy('style.css', f'{BASE}/assets/style.css'); shutil.copy('cover.jpg', f'{BASE}/assets/cover.jpg')
for lang in LANGS:
    m = page(lang); print(lang, 'chapters in English fallback:', len(m))

chooser = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#0E1525"><meta name="color-scheme" content="dark">
<title>Sūtra of the Lotus Flower of the Wonderful Dharma</title>
''' + FONTS + '''
<link rel="stylesheet" href="assets/style.css">
<script>(function(){var l=(navigator.language||'en').slice(0,2).toLowerCase();var m={es:'es',pt:'pt'};var t=m[l]||'en';if(!/[?&]choose/.test(location.search))location.replace(t+'/'+location.hash);})();</script>
</head><body><main class="title-block" style="padding-top:20vh">
<p class="kicker">Vajrakula</p><h1>Sūtra of the Lotus Flower of the Wonderful Dharma</h1><hr class="taper">
<nav class="choose" aria-label="Language"><a href="en/" lang="en">English</a><a href="es/" lang="es">Español</a><a href="pt/" lang="pt">Português</a></nav>
</main></body></html>'''
open(f'{BASE}/index.html', 'w', encoding='utf-8').write(chooser)
