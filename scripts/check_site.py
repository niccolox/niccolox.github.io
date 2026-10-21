"""Check deployable assets, local links, anchors, and structured data without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
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
        self.json_text = ''

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

    def handle_data(self, data):
        if self.capture_json:
            self.json_text += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.capture_json = False

errors = []
for path in ROOT.glob('*.html'):
    page = Page()
    page.feed(path.read_text())
    errors.extend(page.errors)
    if page.h1_count != 1:
        errors.append(f'{path.name}: expected one h1')
    if page.json_text:
        try:
            json.loads(page.json_text)
        except json.JSONDecodeError as exc:
            errors.append(f'{path.name}: invalid structured data: {exc}')
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        if not url.path and url.fragment:
            if url.fragment not in page.ids:
                errors.append(f'{path.name}: missing anchor {reference}')
        elif url.path:
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f'{path.name}: missing or invalid local file {reference}')

for required in ('index.html', '.nojekyll', 'robots.txt', 'sitemap.xml'):
    if not (ROOT / required).is_file():
        errors.append('Missing ' + required)
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print('Passed: local links, assets, anchors, headings, image descriptions, and structured data.')
