"""Build articles from reviewed local content; no network access."""
from pathlib import Path
from html import escape
import datetime
import json
import math
import re
from urllib.parse import quote, urlsplit

from site_nav import HTML_THEME, THEME_COLOR, asset, author_box, author_card, site_header

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CONTENT = ROOT / 'content' / 'writing'
ENTRIES = json.loads((CONTENT / 'posts.json').read_text())
POSTS = [post for post in ENTRIES if 'moved_to' not in post]
# Articles now published elsewhere keep a redirect at their old address.
MOVED = [post for post in ENTRIES if 'moved_to' in post]
ORIGIN = 'https://www.niccolox.com'
CTAS = json.loads((CONTENT / 'ctas.json').read_text())
EMAIL = 'niccolox@devekko.com'
# Prefilled emails. The subject names the article so replies show their source.
MAILTO = {
    'leadership': ('Leadership role conversation', "Hi Nicholas,\n\nI'd like to talk about a technology leadership role.\n\nCompany: \nRole and level: \nLocation or remote: \nWhat the role needs to change in the first year: \n"),
    'shopify': ('Shopify migration enquiry', "Hi Nicholas,\n\nI'd like to discuss moving our store to Shopify.\n\nStore URL: \nCurrent platform and version: \nCatalog size and order volume: \nKey integrations: \nTarget launch date: \n"),
}


def cta_href(target, post):
    if 'href' in target:
        return target['href']
    subject, body = MAILTO[target['action']]
    return f"mailto:{EMAIL}?subject={quote(subject + ' (re: ' + post['title'] + ')')}&body={quote(body)}"


def cta_link(target, post, css):
    external = target.get('href', '').startswith('https://')
    arrow = '↗' if external or 'action' in target else '→'
    return f'<a class="{css}" href="{escape(cta_href(target, post), quote=True)}">{escape(target["text"])} <span aria-hidden="true">{arrow}</span></a>'


def cta_inline(post):
    cta = CTAS[post['cta']]
    if 'inline' not in cta:
        return ''
    return f'<aside class="article-cta article-cta-inline" aria-label="Work with Nicholas"><p>{escape(cta["inline"])} {cta_link(cta["inline_link"], post, "article-cta-link")}</p></aside>'


def cta_panel(post):
    cta = CTAS[post['cta']]
    return f'''<aside class="article-cta article-cta-panel" aria-labelledby="cta-heading"><p class="eyebrow">{escape(cta['eyebrow'])}</p><h2 id="cta-heading">{escape(cta['heading'])}</h2><p>{escape(cta['body'])}</p><div class="article-cta-actions">{cta_link(cta['primary'], post, 'button primary')}{cta_link(cta['secondary'], post, 'text-link')}</div></aside>'''


FOOTER = author_box() + '''
<footer class="site-footer"><div class="wrap"><span>© <span id="year">2026</span> Nicholas Roberts</span><span>San Francisco Bay Area · Built with AI</span><a href="#top">Back to top ↑</a></div></footer>'''


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
        if 'source' in post:
            schema['isBasedOn'] = post['source']
        if 'published' in post:
            schema['datePublished'] = post['published']
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
  <link rel="stylesheet" href="/assets/writing.css?v=6">
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
    for other in (p for p in POSTS if 'source' in p):
        content = content.replace('href="' + other['source'] + '"', 'href="' + route(other) + '"')
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', content, re.S)
    # Put a short call to action before the middle section of long articles.
    if len(headings) >= 4:
        middle = '<h2 id="' + headings[len(headings) // 2][0] + '">'
        content = content.replace(middle, cta_inline(post) + middle, 1)
    toc = ''
    if len(headings) > 2:
        items = ''.join(f'<li><a href="#{ident}">{label.strip()}</a></li>' for ident, label in headings)
        toc = f'<details class="article-toc"><summary>In this article <span aria-hidden="true">+</span></summary><ul>{items}</ul></details>'
    next_post = POSTS[(position + 1) % len(POSTS)]
    subtitle = f'<p class="article-subtitle">{escape(post["subtitle"])}</p>' if post['subtitle'] else ''
    caption = f'<figcaption>{escape(post["caption"])}</figcaption>' if post['caption'] else ''
    # New posts carry a publication date; imported posts come from the old blog.
    if 'published' in post:
        date = datetime.date.fromisoformat(post['published'])
        origin = f'<time datetime="{post["published"]}">{date.day} {date:%B %Y}</time>'
        source_note = ''
    else:
        origin = 'From the niccolox.com archive'
        source_note = 'Preserved from the original niccolox.com blog.'
    body = f'''<main id="main" class="article-main">
<article>
  <header class="article-header article-header-author wrap">
    <div class="article-header-copy">
    <a class="article-back" href="/writing/">← All writing</a>
    <p class="eyebrow">{escape(post['category'])}</p>
    <h1>{escape(post['title'])}</h1>
    {subtitle}
    <div class="article-meta"><span>{max(1, math.ceil(post['word_count'] / 220))} min read</span><span>{origin}</span></div>
    </div>
    {author_card(escape(cta_href({"action": "leadership"}, post), quote=True))}
  </header>
  <figure class="article-image wrap"><img src="{post['image']}" alt="{escape(post['image_alt'], quote=True)}" width="{post['image_width']}" height="{post['image_height']}" fetchpriority="high">{caption}</figure>
  <div class="article-reading">
    {toc}
    <div class="article-prose">{content}</div>
    {cta_panel(post)}
    {f'<div class="article-source"><p>{source_note}</p></div>' if source_note else ''}
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
        source = urlsplit(post.get('source', ''))
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
