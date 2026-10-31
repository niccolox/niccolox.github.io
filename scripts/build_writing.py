"""Build articles from reviewed local content; no network access."""
from pathlib import Path
from html import escape
import json
import math
import re
from urllib.parse import urlsplit

from site_nav import HTML_THEME, THEME_COLOR, asset, site_header

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CONTENT = ROOT / 'content' / 'writing'
ENTRIES = json.loads((CONTENT / 'posts.json').read_text())
POSTS = [post for post in ENTRIES if 'moved_to' not in post]
# Articles now published elsewhere keep a redirect at their old address.
MOVED = [post for post in ENTRIES if 'moved_to' in post]
ORIGIN = 'https://www.niccolox.com'


FOOTER = '''<footer class="site-footer"><div class="wrap"><span>© <span id="year">2026</span> Nicholas Roberts</span><span>San Francisco Bay Area · Built with AI</span><a href="#top">Back to top ↑</a></div></footer>'''


def route(post):
    return '/writing/' + post['slug'] + '/'


def page(title, description, path, body, canonical=None, post=None):
    url = ORIGIN + path
    header = site_header('writing')
    schema = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting' if post else 'CollectionPage',
        'headline' if post else 'name': title,
        'description': description,
        'url': url,
        'author': {'@type': 'Person', 'name': 'Nicholas Roberts', 'url': ORIGIN + '/'},
    }
    if post:
        schema.update({'image': ORIGIN + post['image'], 'wordCount': post['word_count']})
        schema['isBasedOn'] = post['source']
    image = f'<meta property="og:image" content="{ORIGIN + post["image"]}">' if post else ''
    return f'''<!doctype html>
<html lang="en" {HTML_THEME}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="{THEME_COLOR}">
  <title>{escape(title)} — Nicholas Roberts</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{escape(canonical or url, quote=True)}">
  <meta property="og:type" content="{'article' if post else 'website'}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{url}">
  {image}
  <meta name="twitter:card" content="{'summary_large_image' if post else 'summary'}">
  <link rel="icon" href="/assets/favicon.svg?v=2" type="image/svg+xml">
  <script src="{asset('theme.js')}"></script>
  <link rel="stylesheet" href="{asset('daisyui.css')}">
  <link rel="stylesheet" href="{asset('styles.css')}">
  <link rel="stylesheet" href="/assets/writing.css?v=1">
  <script src="{asset('site.js')}" defer></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
</head>
<body id="top">
{header}
{body}
{FOOTER}
</body>
</html>
'''


def article(post, position):
    content = (CONTENT / (post['slug'] + '.html')).read_text()
    # Keep links between imported articles inside this site.
    for other in POSTS:
        content = content.replace('href="' + other['source'] + '"', 'href="' + route(other) + '"')
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', content, re.S)
    toc = ''
    if len(headings) > 2:
        items = ''.join(f'<li><a href="#{ident}">{label.strip()}</a></li>' for ident, label in headings)
        toc = f'<details class="article-toc"><summary>In this article <span aria-hidden="true">+</span></summary><ul>{items}</ul></details>'
    next_post = POSTS[(position + 1) % len(POSTS)]
    subtitle = f'<p class="article-subtitle">{escape(post["subtitle"])}</p>' if post['subtitle'] else ''
    caption = f'<figcaption>{escape(post["caption"])}</figcaption>' if post['caption'] else ''
    body = f'''<main id="main" class="article-main">
<article>
  <header class="article-header wrap">
    <a class="article-back" href="/writing/">← All writing</a>
    <p class="eyebrow">{escape(post['category'])}</p>
    <h1>{escape(post['title'])}</h1>
    {subtitle}
    <div class="article-meta"><span>Nicholas (Niccolo) Roberts</span><span>{max(1, math.ceil(post['word_count'] / 220))} min read</span><span>From the niccolox.com archive</span></div>
  </header>
  <figure class="article-image wrap"><img src="{post['image']}" alt="{escape(post['image_alt'], quote=True)}" width="{post['image_width']}" height="{post['image_height']}" fetchpriority="high">{caption}</figure>
  <div class="article-reading">
    {toc}
    <div class="article-prose">{content}</div>
    <div class="article-source"><p>Written by Nicholas Roberts. Preserved from the original niccolox.com blog.</p></div>
  </div>
</article>
<aside class="article-next wrap" aria-label="More writing"><div><p class="eyebrow">KEEP READING</p><a href="{route(next_post)}">{escape(next_post['title'])} <span aria-hidden="true">→</span></a></div><a class="text-link" href="/writing/">Browse all articles →</a></aside>
</main>'''
    return page(post['title'], post['description'], route(post), body, post=post)


def legacy_redirect(path, destination, title, note='This page is now part of the writing archive.', description='Continue to the writing archive.'):
    """Keep existing blog bookmarks reachable on the static Pages host."""
    body = f'<main id="main" class="writing-index wrap"><h1>{escape(title)}</h1><p>{escape(note)}</p><a class="text-link" href="{escape(destination, quote=True)}">Continue to the article →</a></main>'
    canonical = destination if destination.startswith('https://') else ORIGIN + destination
    html = page(title, description, path, body, canonical=canonical)
    html = html.replace('<head>', f'<head>\n  <meta http-equiv="refresh" content="0; url={destination}">\n  <meta name="robots" content="noindex">', 1)
    target = SITE / path.strip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)


def homepage_row(post):
    return f'''      <a class="writing-row" href="{route(post)}"><span class="writing-category">{post['category']}</span><div><h3>{escape(post['title'])}</h3><p>{escape(post['description'])}</p></div><span class="writing-arrow" aria-hidden="true">→</span></a>'''


def build():
    for position, post in enumerate(POSTS):
        target = SITE / route(post).strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(article(post, position))
        source = urlsplit(post['source'])
        if source.hostname in {'www.niccolox.com', 'niccolox.com'} and source.path.startswith('/p/'):
            legacy_redirect(source.path, route(post), post['title'])
    for post in MOVED:
        legacy_redirect(route(post), post['moved_to'], post['title'], 'This article now lives on cyberpolycrisis.com.', 'Continue to the article on cyberpolycrisis.com.')
    legacy_redirect('/posts', '/writing/', 'Writing by Nicholas Roberts')
    cards = []
    for post in POSTS:
        cards.append(f'''<a class="article-card" href="{route(post)}"><img src="{post['image']}" alt="{escape(post['image_alt'], quote=True)}" width="{post['image_width']}" height="{post['image_height']}" loading="lazy"><div class="article-card-copy"><p class="eyebrow">{post['category']}</p><h2>{escape(post['title'])}</h2><p>{escape(post['description'])}</p><span class="article-card-link">Read article →</span></div></a>''')
    body = '''<main id="main" class="writing-index wrap"><header class="writing-index-header"><p class="eyebrow">NOTES FROM THE WORK</p><h1>Thinking in public.</h1><p>Field notes on AI, commerce, technology leadership, and getting useful work into the world.</p></header><div class="article-grid">''' + '\n'.join(cards) + '''</div></main>'''
    (SITE / 'writing/index.html').write_text(page('Writing', 'Articles by Nicholas Roberts on AI, ecommerce, modernization, customer success, and product delivery.', '/writing/', body))
    homepage = SITE / 'index.html'
    html = homepage.read_text()
    start = html.index('    <section class="writing-section')
    end = html.index('</section>', start) + len('</section>')
    section = '''    <section class="writing-section section-pad" id="writing" aria-labelledby="writing-heading"><div class="wrap"><div class="section-heading"><div><h2 id="writing-heading">Thinking in public.</h2></div><a class="text-link" href="/writing/">All writing <span aria-hidden="true">→</span></a></div><div class="writing-list">\n''' + '\n'.join(homepage_row(post) for post in POSTS) + '\n    </div></div></section>'
    homepage.write_text(html[:start] + section + html[end:])
    sitemap_urls = [ORIGIN + '/', ORIGIN + '/writing/']
    sitemap_urls += [ORIGIN + '/' + str(path.parent.relative_to(SITE)) + '/' for path in sorted((SITE / 'services').rglob('index.html'))]
    unlisted_portfolio = {case['slug'] for case in json.loads((ROOT / 'content/portfolio/cases.json').read_text()) if not case.get('listed', True)}
    sitemap_urls += [ORIGIN + '/' + str(path.parent.relative_to(SITE)) + '/' for path in sorted((SITE / 'portfolio').rglob('index.html')) if path.parent.name not in unlisted_portfolio]
    sitemap_urls += [ORIGIN + route(post) for post in POSTS]
    (SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + escape(url) + '</loc></url>' for url in sitemap_urls) + '</urlset>\n')
    print(f'Built {len(POSTS)} complete articles, writing index, and homepage links.')


if __name__ == '__main__':
    build()
