"""HTML -> plain text (standard library): drops script/style/nav/footer, keeps headings, paragraphs, list items and
table cells on separate lines; also appends JSON-LD articleBody / description and <meta> description when present."""
import html, json, re, sys
from html.parser import HTMLParser

SKIP = {'script', 'style', 'noscript', 'svg', 'nav', 'footer', 'header', 'form', 'iframe'}
BLOCK = {'p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article', 'table', 'dt', 'dd', 'blockquote'}


class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0

    def handle_starttag(self, t, a):
        if t in SKIP: self.skip += 1
        elif t in BLOCK: self.out.append('\n')
        elif t in ('td', 'th'): self.out.append(' | ')

    def handle_endtag(self, t):
        if t in SKIP and self.skip: self.skip -= 1
        elif t in BLOCK: self.out.append('\n')

    def handle_data(self, d):
        if not self.skip: self.out.append(d)


for path in sys.argv[1:]:
    s = open(path, encoding='utf-8', errors='replace').read()
    extra = []
    for m in re.finditer(r'<meta[^>]+(?:name|property)="(?:description|og:description|article:published_time|og:title)"[^>]*>', s):
        c = re.search(r'content="([^"]*)"', m.group(0))
        if c: extra.append('[meta] ' + html.unescape(c.group(1)))
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', s, re.S):
        try:
            j = json.loads(m.group(1))
            for o in (j if isinstance(j, list) else j.get('@graph', [j])):
                for k in ('headline', 'datePublished', 'articleBody'):
                    if isinstance(o, dict) and o.get(k): extra.append('[ld+json %s] %s' % (k, o[k]))
        except Exception:
            pass
    p = P(); p.feed(s)
    t = re.sub(r'[ \t\xa0]+', ' ', ''.join(p.out))
    t = re.sub(r'\s*\n\s*', '\n', t).strip()
    open(re.sub(r'\.html$', '', path) + '.txt', 'w', encoding='utf-8').write('\n'.join(extra) + '\n\n' + t + '\n')
    print(len(t), path)
