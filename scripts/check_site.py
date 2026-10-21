"""Check every page, local link, imported article, and asset without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1] / 'site'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []
        self.errors = []
        self.h1_count = 0
        self.capture_json = False
        self.json_blocks = []
        self.body_depth = 0
        self.body_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:
                self.errors.append('Duplicate id: ' + a['id'])
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'img' and not a.get('alt'):
            self.errors.append('Image requires meaningful alt text')
        for key in ('src', 'href'):
            if key in a:
                self.references.append(a[key])
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.capture_json = True
            self.json_blocks.append('')
        if tag == 'div' and (self.body_depth or 'article-prose' in a.get('class', '').split()):
            self.body_depth += 1
        if self.body_depth and (tag in {'script','iframe','form','object','embed'} or any(k.startswith('on') for k in a)):
            self.errors.append('Active content in imported article')

    def handle_data(self, data):
        if self.capture_json:
            self.json_blocks[-1] += data
        if self.body_depth:
            self.body_text.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.capture_json = False
        if tag == 'div' and self.body_depth:
            self.body_depth -= 1

errors = []
pages = {}
for path in ROOT.rglob('*.html'):
    page = Page()
    page.feed(path.read_text())
    pages[path.resolve()] = page
    name = str(path.relative_to(ROOT))
    errors.extend(name + ': ' + error for error in page.errors)
    if page.h1_count != 1:
        errors.append(f'{name}: expected one h1')
    for block in page.json_blocks:
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f'{name}: invalid structured data: {exc}')

for path, page in pages.items():
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            if url.scheme.lower() in {'javascript','data'}:
                errors.append(f'{path.name}: unsafe URL {reference}')
            continue
        if not url.path:
            target = path
        else:
            target = ((ROOT / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (path.parent / unquote(url.path))).resolve()
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_relative_to(ROOT) or not target.is_file():
            errors.append(f'{path.relative_to(ROOT)}: missing or invalid local file {reference}')
        elif url.fragment and target.suffix == '.html' and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{path.relative_to(ROOT)}: missing anchor {reference}')

posts_file = ROOT.parent / 'content/writing/posts.json'
if posts_file.exists():
    posts = json.loads(posts_file.read_text())
    for post in posts:
        path = ROOT / 'writing' / post['slug'] / 'index.html'
        page = pages.get(path)
        if not page:
            errors.append('Missing imported article: ' + post['slug'])
            continue
        body = ' '.join(' '.join(page.body_text).split())
        if hashlib.sha256(body.encode()).hexdigest() != post['body_text_sha256']:
            errors.append('Imported article text differs from reviewed source: ' + post['slug'])

for required in ('index.html', '.nojekyll', 'robots.txt', 'sitemap.xml', 'assets/daisyui.css'):
    if not (ROOT / required).is_file():
        errors.append('Missing ' + required)
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Passed: {len(pages)} pages; local links, assets, anchors, headings, image descriptions, structured data, and complete imported article text.')
