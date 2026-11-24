"""Apply the shared header, theme and asset versions to hand-written pages."""
from pathlib import Path
import re

from site_nav import ASSET_VERSIONS, HTML_THEME, THEME_COLOR, author_box, site_header

SITE = Path(__file__).resolve().parents[1] / 'site'
# Hand-written pages and the top-level section each belongs to.
PAGES = {
    'index.html': '',
    'services/magento-to-shopify/index.html': 'services',
    'services/woocommerce-to-shopify/index.html': 'services',
    '404.html': '',
}
AUTHOR = re.compile(r'\s*<aside class="author-box".*?</aside>', re.S)
HEADER = re.compile(r'(?:<a class="skip-link"[^>]*>[^<]*</a>\s*)?<header class="site-header">.*?</header>', re.S)


def apply(path, current):
    html = path.read_text()
    html = re.sub(r'<html lang="en"[^>]*>', f'<html lang="en" {HTML_THEME}>', html, count=1)
    html = re.sub(r'<meta name="theme-color" content="[^"]*">', f'<meta name="theme-color" content="{THEME_COLOR}">', html, count=1)
    for name, version in ASSET_VERSIONS.items():
        html = re.sub(rf'(assets/{re.escape(name)})\?v=\d+', rf'\g<1>?v={version}', html)
    if not HEADER.search(html):
        raise SystemExit(f'{path}: no site header to replace')
    html = HEADER.sub(lambda _: site_header(current), html, count=1)
    # Replace any earlier author box, then place it above the footer (or before </body>).
    html = AUTHOR.sub('', html)
    anchor = '<footer class="site-footer"' if '<footer class="site-footer"' in html else '</body>'
    start = html.rindex(anchor)
    line = html.rfind('\n', 0, start) + 1
    html = html[:line] + author_box() + '\n' + html[line:]
    path.write_text(html)


if __name__ == '__main__':
    for page, current in PAGES.items():
        apply(SITE / page, current)
    print(f'Applied the shared header, author box and theme to {len(PAGES)} hand-written pages.')
