"""Build one accessible page per portfolio slide from reviewed local copy."""
from html import escape
from pathlib import Path
import json

from build_writing import HEADER, FOOTER, ORIGIN

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CASES = json.loads((ROOT / 'content/portfolio/cases.json').read_text())
LISTED_CASES = [case for case in CASES if case.get('listed', True)]
PDF = '/assets/downloads/Nicholas-Roberts-Portfolio.pdf'


def route(case):
    return '/portfolio/' + case['slug'] + '/'


def image_path(case):
    return f'/assets/images/portfolio/slide-{case["slide"]:02}.jpg'


def paragraphs(items):
    return ''.join(f'<p>{escape(item)}</p>' for item in items)


def bullets(items):
    return '<ul>' + ''.join(f'<li>{escape(item)}</li>' for item in items) + '</ul>'


def page(title, description, path, body, case=None):
    url = ORIGIN + path
    header = HEADER.replace('<a href="/#work">Selected work</a>', '<a href="/portfolio/" aria-current="' + ('location' if case else 'page') + '">Portfolio</a>').replace(' aria-current="PAGE_CURRENT"', '')
    image = ORIGIN + (image_path(case) if case else image_path(CASES[0]))
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Article' if case else 'CollectionPage',
        'name': title,
        'description': description,
        'url': url,
        'image': image,
        'author': {'@type': 'Person', 'name': 'Nicholas Roberts', 'url': ORIGIN + '/'},
        'isBasedOn': {'@type': 'DigitalDocument', 'name': 'Nicholas Roberts professional portfolio', 'url': ORIGIN + PDF + (f'#page={case["slide"]}' if case else '')},
    }
    if case:
        schema['headline'] = title
        schema['articleSection'] = case['kind']
    else:
        schema['hasPart'] = [{'@type': 'WebPage', 'name': c['organization'], 'url': ORIGIN + route(c)} for c in LISTED_CASES]
    return f'''<!doctype html>
<html lang="en" data-theme="nord">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#eceff4">
  <title>{escape(title)} — Nicholas Roberts</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="{'article' if case else 'website'}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:alt" content="{escape(case['image_alt'] if case else CASES[0]['image_alt'], quote=True)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg?v=2" type="image/svg+xml">
  <script src="/assets/theme.js?v=2"></script>
  <link rel="stylesheet" href="/assets/daisyui.css?v=12">
  <link rel="stylesheet" href="/assets/styles.css?v=5">
  <link rel="stylesheet" href="/assets/portfolio.css?v=1">
  <script src="/assets/site.js?v=2" defer></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
</head>
<body id="top">
{header}
{body}
{FOOTER}
</body>
</html>
'''


def contact():
    return '''<aside class="portfolio-contact wrap" aria-labelledby="conversation-title">
  <div><p class="eyebrow">LET’S TALK ABOUT YOUR NEXT CHAPTER</p><h2 id="conversation-title">What needs to work better?</h2><p>Tell me about the business, the operating challenge, and the change you want to make.</p></div>
  <div class="flex flex-col items-start gap-5"><a class="link text-lg underline-offset-4" href="mailto:niccolox@devekko.com">niccolox@devekko.com</a><a class="link text-lg underline-offset-4" href="https://www.linkedin.com/in/niccolo/">Connect on LinkedIn <span aria-hidden="true">↗</span></a></div>
</aside>'''


def case_page(case, position):
    number = f'{case["slide"]:02}'
    kind = case['kind']
    metrics = ''.join(f'<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>' for value, label in case['metrics'])
    tags = ''.join(f'<li class="badge badge-outline">{escape(tag)}</li>' for tag in case['tags'])
    note = f'<p class="portfolio-evidence-note">{escape(case["note"])}</p>' if case.get('note') else ''
    previous = next((item for item in reversed(CASES[:position]) if item.get('listed', True)), None)
    following = next((item for item in CASES[position + 1:] if item.get('listed', True)), None)
    prev_url = route(previous) if previous else '/portfolio/'
    prev_title = previous['organization'] if previous else 'All portfolio pages'
    next_url = route(following) if following else '/portfolio/'
    next_title = following['organization'] if following else 'Back to the portfolio'
    first_title = 'The brief' if kind == 'Case study' else ('The work in context' if kind == 'Portfolio overview' else 'Start a conversation')
    evidence_title = 'Delivery and evidence' if kind == 'Case study' else ('What this portfolio shows' if kind == 'Portfolio overview' else 'A useful first conversation')
    method_title = 'How the work was delivered' if kind == 'Case study' else 'Connecting the work'
    body = f'''<main id="main" class="portfolio-page">
<article>
  <header class="portfolio-lead wrap">
    <div class="portfolio-breadcrumb"><a class="link link-hover" href="/">Home</a><span aria-hidden="true">/</span><a class="link link-hover" href="/portfolio/">Portfolio</a><span aria-hidden="true">/</span><span>Slide {number}</span></div>
    <p class="eyebrow">{escape(kind.upper())} <span aria-hidden="true">/</span> {number} OF 12</p>
    <p class="portfolio-organization">{escape(case['organization'])}</p>
    <h1>{escape(case['title'])}</h1>
    <p class="portfolio-deck">{escape(case['summary'])}</p>
    <div class="portfolio-role"><span>{escape(case['role'])}</span><span>{escape(case['sector'])}</span></div>
    <dl class="portfolio-metrics grid grid-cols-1 gap-5 sm:grid-cols-3">{metrics}</dl>
  </header>
  <div class="portfolio-body wrap">
    <aside class="portfolio-sidebar" aria-label="Case study guide">
      <p class="eyebrow">ON THIS PAGE</p>
      <ol><li><a href="#brief">{first_title}</a></li><li><a href="#ownership">What I owned</a></li><li><a href="#delivery">{method_title}</a></li><li><a href="#evidence">{evidence_title}</a></li><li><a href="#source-slide">Original slide</a></li></ol>
      <a class="link underline-offset-4" href="{PDF}#page={case['slide']}">Open slide {number} in the PDF <span aria-hidden="true">↗</span></a>
    </aside>
    <div class="portfolio-story">
      <section id="brief"><p class="portfolio-section-number">01 / CONTEXT</p><h2>{first_title}</h2><p>{escape(case['brief'])}</p></section>
      <section id="ownership"><p class="portfolio-section-number">02 / RESPONSIBILITY</p><h2>What I owned</h2>{bullets(case['ownership'])}</section>
      <section id="delivery"><p class="portfolio-section-number">03 / EXECUTION</p><h2>{method_title}</h2>{paragraphs(case['delivery'])}</section>
      <section id="evidence"><p class="portfolio-section-number">04 / EVIDENCE</p><h2>{evidence_title}</h2>{bullets(case['outcomes'])}{note}</section>
      <aside class="portfolio-takeaway"><p class="eyebrow">THE OPERATING LESSON</p><p>{escape(case['lesson'])}</p></aside>
      <section class="portfolio-toolbox" aria-labelledby="toolbox-title"><h2 id="toolbox-title">Tools &amp; disciplines</h2><ul class="flex flex-wrap gap-2">{tags}</ul></section>
    </div>
  </div>
  <section id="source-slide" class="portfolio-source wrap" aria-labelledby="source-title">
    <div class="portfolio-source-heading"><div><p class="eyebrow">FROM THE ORIGINAL PORTFOLIO</p><h2 id="source-title">Slide {number}. The source material.</h2></div><a class="link underline-offset-4" href="{PDF}#page={case['slide']}">Open the PDF <span aria-hidden="true">↗</span></a></div>
    <figure><a href="{image_path(case)}" aria-label="Enlarge original portfolio slide {number}"><img src="{image_path(case)}" alt="{escape(case['image_alt'], quote=True)}" width="1600" height="900" loading="lazy" decoding="async"></a><figcaption>Original slide {case['slide']} of 12. Select the image to enlarge. The historical slide is preserved; the text above expands its project description for the web.</figcaption></figure>
  </section>
</article>
<div class="portfolio-pagination wrap" role="navigation" aria-label="Portfolio pages">
  <a href="{prev_url}"><span>← {'Previous slide' if previous else 'Portfolio index'}</span><strong>{escape(prev_title)}</strong></a>
  <a href="{next_url}"><span>{'Next slide' if following else 'Portfolio index'} →</span><strong>{escape(next_title)}</strong></a>
</div>
{contact()}
</main>'''
    return page(case['organization'] + ' · ' + case['title'], case['summary'], route(case), body, case)


def index_page():
    cards = []
    for case in LISTED_CASES:
        label = 'Read case study' if case['kind'] == 'Case study' else ('Read overview' if case['kind'] == 'Portfolio overview' else 'Get in touch')
        cards.append(f'''<article class="card bg-base-200 border border-base-300 portfolio-card">
  <figure><a href="{route(case)}" tabindex="-1" aria-hidden="true"><img src="{image_path(case)}" alt="{escape(case['image_alt'], quote=True)}" width="1600" height="900" loading="lazy" decoding="async"></a></figure>
  <div class="card-body"><p class="eyebrow">{case['slide']:02} / {escape(case['kind'].upper())}</p><h2 class="card-title"><a href="{route(case)}">{escape(case['organization'])}</a></h2><p class="portfolio-card-headline">{escape(case['title'])}</p><p>{escape(case['summary'])}</p><div class="card-actions"><a class="link underline-offset-4" href="{route(case)}" aria-label="{escape(label + ': ' + case['organization'], quote=True)}">{label} <span aria-hidden="true">→</span></a></div></div>
</article>''')
    body = '''<main id="main" class="portfolio-page">
<header class="portfolio-lead wrap">
  <div class="portfolio-breadcrumb"><a class="link link-hover" href="/">Home</a><span aria-hidden="true">/</span><span>Portfolio</span></div>
  <p class="eyebrow">SELECTED WORK / THE PORTFOLIO</p>
  <h1>From the brief to<br>the operating reality.</h1>
  <p class="portfolio-deck">Nine project case studies, a career overview, and a way to start a conversation. Explore the people, systems, and delivery work behind selected projects in my professional portfolio.</p>
  <div class="portfolio-index-links"><a class="link text-lg underline-offset-4" href="#all-slides">Explore the portfolio ↓</a><a class="link text-lg underline-offset-4" href="''' + PDF + '''">Download the portfolio PDF ↗</a></div>
  <p class="portfolio-index-note">Historical work, expanded for the web. Every page includes its original slide and a direct link to the PDF.</p>
</header>
<section id="all-slides" class="wrap portfolio-grid-section" aria-labelledby="all-slides-title"><div class="portfolio-index-heading"><h2 id="all-slides-title">The portfolio, slide by slide.</h2><span>''' + str(len(LISTED_CASES)) + ''' pages</span></div><div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">''' + '\n'.join(cards) + '''</div></section>
''' + contact() + '\n</main>'
    return page('Portfolio case studies', 'Explore Nicholas Roberts’s professional portfolio: commerce, data platforms, cloud infrastructure, telecommunications, government, hospitality, and news publishing.', '/portfolio/', body)


def build():
    if [case['slide'] for case in CASES] != list(range(1, 13)):
        raise ValueError('The portfolio requires exactly one entry for each of its 12 source slides.')
    if len({case['slug'] for case in CASES}) != len(CASES):
        raise ValueError('Duplicate portfolio route')
    for position, case in enumerate(CASES):
        target = SITE / route(case).strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(case_page(case, position))
    (SITE / 'portfolio/index.html').write_text(index_page())
    print(f'Built {len(CASES)} portfolio slide pages and their index.')


if __name__ == '__main__':
    build()
