"""Build the imported articles from reviewed local content; no network access."""
from pathlib import Path
from html import escape
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CONTENT = ROOT / 'content' / 'writing'
POSTS = json.loads((CONTENT / 'posts.json').read_text())
ORIGIN = 'https://niccolox.github.io'

THEME_CONTROL = '''<label class="theme-switch" title="Switch between Nord and Night">
  <span class="theme-label-nord">Nord</span><span class="theme-label-night">Night</span>
  <input type="checkbox" class="toggle theme-controller" value="night" aria-label="Night theme (off uses Nord)">
</label>'''

HEADER = '''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner wrap">
  <a href="/" class="wordmark" aria-label="Nicholas Roberts home"><span class="monogram">n<span>r</span>.</span><span>NICHOLAS<br>ROBERTS</span></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation">Menu <span aria-hidden="true">+</span></button>
  <nav id="navigation" aria-label="Main navigation"><a href="/#work">Selected work</a><a href="/#experience">Experience</a><a href="/writing/" aria-current="PAGE_CURRENT">Writing</a><a class="nav-contact" href="/#contact">Let’s talk <span aria-hidden="true">↗</span></a></nav>
  THEME_CONTROL
</div></header>'''.replace('THEME_CONTROL', THEME_CONTROL)

FOOTER = '''<footer class="site-footer"><div class="wrap"><span>© <span id="year">2026</span> Nicholas Roberts</span><span>San Francisco Bay Area · Built with AI</span><a href="#top">Back to top ↑</a></div></footer>'''


def route(post):
    return '/writing/' + post['slug'] + '/'


def page(title, description, path, body, canonical=None, post=None):
    url = ORIGIN + path
    schema = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting' if post else 'CollectionPage',
        'headline' if post else 'name': title,
        'description': description,
        'url': url,
        'author': {'@type': 'Person', 'name': 'Nicholas Roberts', 'url': ORIGIN + '/'},
    }
    if post:
        schema.update({'isBasedOn': post['source'], 'image': ORIGIN + post['image'], 'wordCount': post['word_count']})
    image = f'<meta property="og:image" content="{ORIGIN + post["image"]}">' if post else ''
    return f'''<!doctype html>
<html lang="en" data-theme="nord">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#eceff4">
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
  <script src="/assets/theme.js?v=1"></script>
  <link rel="stylesheet" href="/assets/daisyui.css?v=1">
  <link rel="stylesheet" href="/assets/styles.css?v=5">
  <link rel="stylesheet" href="/assets/writing.css?v=1">
  <script src="/assets/site.js?v=2" defer></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
</head>
<body id="top">
{HEADER.replace('PAGE_CURRENT', 'location' if post else 'page')}
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
    <div class="article-meta"><span>Nicholas (Niccolo) Roberts</span><span>{max(1, math.ceil(post['word_count'] / 220))} min read</span><a href="{post['source']}">Originally on niccolox.com ↗</a></div>
  </header>
  <figure class="article-image wrap"><img src="{post['image']}" alt="{escape(post['image_alt'], quote=True)}" width="{post['image_width']}" height="{post['image_height']}" fetchpriority="high">{caption}</figure>
  <div class="article-reading">
    {toc}
    <div class="article-prose">{content}</div>
    <div class="article-source"><p>Written by Nicholas Roberts. <a href="{post['source']}">Read the original on niccolox.com ↗</a></p></div>
  </div>
</article>
<aside class="article-next wrap" aria-label="More writing"><div><p class="eyebrow">KEEP READING</p><a href="{route(next_post)}">{escape(next_post['title'])} <span aria-hidden="true">→</span></a></div><a class="text-link" href="/writing/">Browse all articles →</a></aside>
</main>'''
    return page(post['title'], post['description'], route(post), body, canonical=post['source'], post=post)


def homepage_row(post):
    return f'''      <a class="writing-row" href="{route(post)}"><span class="writing-category">{post['category']}</span><div><h3>{escape(post['title'])}</h3><p>{escape(post['description'])}</p></div><span class="writing-arrow" aria-hidden="true">→</span></a>'''


def build():
    for position, post in enumerate(POSTS):
        target = SITE / route(post).strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(article(post, position))
    cards = []
    for post in POSTS:
        cards.append(f'''<a class="article-card" href="{route(post)}"><img src="{post['image']}" alt="{escape(post['image_alt'], quote=True)}" width="{post['image_width']}" height="{post['image_height']}" loading="lazy"><div class="article-card-copy"><p class="eyebrow">{post['category']}</p><h2>{escape(post['title'])}</h2><p>{escape(post['description'])}</p><span class="article-card-link">Read article →</span></div></a>''')
    body = '''<main id="main" class="writing-index wrap"><header class="writing-index-header"><p class="eyebrow">NOTES FROM THE WORK</p><h1>Thinking in public.</h1><p>Field notes on AI, commerce, technology leadership, and getting useful work into the world.</p></header><div class="article-grid">''' + '\n'.join(cards) + '''</div><div class="writing-archive"><p>More notes and experiments on my original blog.</p><a class="text-link" href="https://www.niccolox.com/posts">Visit niccolox.com ↗</a></div></main>'''
    (SITE / 'writing/index.html').write_text(page('Writing', 'Articles by Nicholas Roberts on AI, ecommerce, modernization, customer success, and product delivery.', '/writing/', body))
    homepage = SITE / 'index.html'
    html = homepage.read_text()
    start = html.index('    <section class="writing-section')
    end = html.index('</section>', start) + len('</section>')
    extra = '''      <a class="writing-row" href="https://www.niccolox.com/p/352-cursor-codegpt-and-deepseek-r1-ollama-gpu-in-docker-on-ubuntu-24"><span class="writing-category">ENGINEERING</span><div><h3>A local AI development workflow</h3><p>Connecting Cursor, CodeGPT, Ollama, and GPU-enabled Docker containers. On niccolox.com.</p></div><span class="writing-arrow" aria-hidden="true">↗</span></a>'''
    section = '''    <section class="writing-section section-pad" id="writing" aria-labelledby="writing-heading"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">03 / NOTES FROM THE WORK</p><h2 id="writing-heading">Thinking in public.</h2></div><a class="text-link" href="/writing/">All writing <span aria-hidden="true">→</span></a></div><div class="writing-list">\n''' + '\n'.join(homepage_row(post) for post in POSTS) + '\n' + extra + '\n    </div></div></section>'
    homepage.write_text(html[:start] + section + html[end:])
    print(f'Built {len(POSTS)} complete articles, writing index, and homepage links.')


if __name__ == '__main__':
    build()
