"""Shared site header: daisyUI megamenu built from reviewed content; no network access."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'content/portfolio/cases.json').read_text())
POSTS = [post for post in json.loads((ROOT / 'content/writing/posts.json').read_text()) if 'moved_to' not in post]
MOVED = [post for post in json.loads((ROOT / 'content/writing/posts.json').read_text()) if 'moved_to' in post]

THEME = 'corporate'
THEME_COLOR = '#ffffff'
HTML_THEME = f'data-theme="{THEME}" data-default-theme="{THEME}"'
THEME_CONTROL = '''<label class="theme-switch" title="Switch between light and dark">
  <span class="theme-label-nord">Light</span><span class="theme-label-night">Dark</span>
  <input type="checkbox" class="toggle theme-controller" value="business" aria-label="Dark theme (off uses light)">
</label>'''

CYBER_WORDMARK = '<a class="link cyber-wordmark" href="https://cyberpolycrisis.com/" aria-label="cyberpolycrisis.com"><span class="cyber-brand-cyber" aria-hidden="true">cyber</span><span class="cyber-brand-poly" aria-hidden="true">poly</span><span class="cyber-brand-crisis" aria-hidden="true">crisis</span><span class="cyber-brand-dot" aria-hidden="true">.</span><span class="cyber-brand-com" aria-hidden="true">com</span></a>'
EXTERNAL = ' <span aria-hidden="true">↗</span>'
DOWNLOAD = ' <span aria-hidden="true">↓</span>'


def item(href, label, note='', suffix=''):
    note_html = f'<small>{escape(note)}</small>' if note else ''
    return f'<li><a href="{escape(href, quote=True)}"><span>{escape(label)}{suffix}</span>{note_html}</a></li>'


def column(title, items, wide=False):
    return f'<section class="nav-column{" nav-column-wide" if wide else ""}"><h2>{escape(title)}</h2><ul>{"".join(items)}</ul></section>'


def footer(*links):
    return '<div class="nav-panel-footer">' + ''.join(f'<a href="{escape(h, quote=True)}">{escape(t)}{s}</a>' for h, t, s in links) + '</div>'


def panels():
    case_studies = [c for c in CASES if c['kind'] == 'Case study' and c.get('listed', True) and c['slug'] != 'cyberpolycrisis']
    work = column('Case studies', [item(f'/portfolio/{c["slug"]}/', c['organization'], c['sector']) for c in case_studies], wide=True) + column('Projects', [
        item('/#engineering', 'Engineering in the open', 'AI builder sprint demos and SaaSx2x'),
        item('/portfolio/cyberpolycrisis/', 'Cyberpolycrisis', 'AI-assisted cyber resilience'),
        item('https://devekko.dev/projects', 'Devekko.dev projects', 'Specs and research', EXTERNAL),
    ])
    work += footer(('/portfolio/', 'Portfolio overview', ' <span aria-hidden="true">→</span>'), ('/assets/downloads/Nicholas-Roberts-Portfolio.pdf', 'Portfolio PDF', DOWNLOAD))
    services = column('Commerce migration', [
        item('/services/magento-to-shopify/', 'Magento to Shopify', 'Orders, customers, catalog and redirects'),
        item('/services/woocommerce-to-shopify/', 'WooCommerce to Shopify', 'Products, subscriptions and SEO continuity'),
    ]) + column('Leadership', [
        item('/portfolio/technology-leadership/', 'Technology leadership', 'Commerce, data and digital services'),
        item('/portfolio/work-with-nicholas-roberts/', 'Work with Nicholas', 'VP, CTO and Director roles'),
    ])
    writing = column('Latest writing', [item(f'/writing/{p["slug"]}/', p['title']) for p in POSTS[:4]], wide=True) + column('Cyberpolycrisis research', [
        item(p['moved_to'], p['title'], '', EXTERNAL) for p in MOVED])
    writing += footer(('/writing/', 'All writing', ' <span aria-hidden="true">→</span>'))
    about = column('Background', [
        item('/#experience', 'Experience', 'Twenty-five years of roles'),
        item('/#approach', 'How I work', 'Close to the business and the build'),
        item('/#contact', 'Contact', 'niccolox@devekko.com'),
    ]) + column('Resume', [
        item('/assets/downloads/Nicholas-Roberts-Resume.pdf', 'Resume PDF', '', DOWNLOAD),
        item('/assets/downloads/Nicholas-Roberts-Resume.docx', 'Resume Word', '', DOWNLOAD),
        item('https://www.linkedin.com/in/niccolo/', 'LinkedIn', '', EXTERNAL),
    ])
    return [('work', 'Work', work), ('services', 'Services', services), ('writing', 'Writing', writing), ('about', 'About', about)]


def site_header(current=''):
    """Return the header; `current` names the top-level section to mark."""
    parts = []
    for key, label, content in panels():
        mark = ' class="is-current"' if key == current else ''
        parts.append(f'<button type="button" popovertarget="nav-{key}"{mark}>{label}</button>\n      <div id="nav-{key}" class="nav-panel nav-panel-{key}" popover><div class="nav-panel-grid">{content}</div></div>')
    menu = '\n      '.join(parts)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner wrap">
  <a href="/" class="wordmark" aria-label="Nicholas Roberts home"><span class="monogram">n<span>r</span>.</span><span>NICHOLAS<br>ROBERTS</span></a>
  <nav class="site-nav" aria-label="Main navigation">
    <button class="menu-toggle" type="button" popovertarget="site-megamenu">Menu <span aria-hidden="true">+</span></button>
    <div class="megamenu max-[1100px]:megamenu-vertical site-megamenu" id="site-megamenu" popover>
      <span class="megamenu-active"></span>
      {menu}
    </div>
  </nav>
  <div class="header-actions">{CYBER_WORDMARK}<a class="nav-contact" href="/#contact">Let’s talk <span aria-hidden="true">↗</span></a>
  {THEME_CONTROL}</div>
</div></header>'''

# Bump a version when its shared asset changes; every page reads these.
ASSET_VERSIONS = {'theme.js': 4, 'daisyui.css': 15, 'styles.css': 9, 'site.js': 5}


def asset(name):
    return f'/assets/{name}?v={ASSET_VERSIONS[name]}'
