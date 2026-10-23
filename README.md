# Nicholas Roberts resume site

A responsive, static resume, portfolio, and writing site for `niccolox/niccolox.github.io`.

## Preview

Run from this directory:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:4173`. No package installation or build is needed.

The checked-in site includes compiled DaisyUI 5 / Tailwind CSS 4 styles. Nord is the default; the theme-controller toggle selects Night and remembers the choice in local storage. Both themes work without JavaScript, but persistence requires it. Styles, scripts, and article images are served locally.

## Publish on GitHub Pages

Push this directory's contents to the `main` branch of `niccolox/niccolox.github.io`. In the repository's **Settings → Pages**, set **Source** to **GitHub Actions**. The included workflow validates the files and deploys only `site/` on each push to `main` or manual workflow run.

The custom address is `https://www.niccolox.com/`, backed by `niccolox/niccolox.github.io`. GitHub Pages uses the custom domain configured through repository settings; this Actions deployment does not require a CNAME file. Cloudflare holds a **proxied** `www` CNAME targeting `niccolox.github.io`; keep proxy protection enabled. The existing apex redirect sends `niccolox.com` visitors to `www`.

Cloudflare's `www portfolio: enforce HTTPS` redirect sends `http://www.niccolox.com/*` to `https://www.niccolox.com/${1}` with status 301 and query preservation. The existing Cloudflare Full TLS mode is unchanged. As of 23 October 2026, browser HTTPS works through Cloudflare, but GitHub has not issued a custom-domain certificate, so its separate `https_enforced` setting is unavailable. Do not enable Full (strict) until GitHub's origin certificate is valid for this domain, and do not disable Cloudflare's proxy to obtain it without the owner's approval.

The writing build preserves the imported blog URLs under `/p/` and the `/posts` index using static redirects. Article canonicals, social metadata and the sitemap use the custom domain. This is not a complete migration of every historical blog post or the old subscription/account system.

GitHub's [custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) describes the Pages configuration.

## Edit

- `site/index.html`: copy, projects, experience, links, and Person structured data.
- `site/services/magento-to-shopify/index.html`: migration services landing page, scope, case study, FAQs, and email enquiry.
- `site/assets/migration.css`: service-page typography and component refinements.
- `site/assets/styles.css`: layout, responsive behavior, color, and print styles.
- `site/assets/site.js`: mobile navigation, current year, and printing.
- `site/assets/theme.js`: saved Nord/Night preference and theme-controller state.
- `site/assets/writing.css`: responsive article and writing-index typography.
- `styles/daisyui.css`: Tailwind entry and official DaisyUI Nord/Night configuration.
- `content/writing/`: reviewed article bodies and source metadata.
- `scripts/build_writing.py`: generates article pages, the writing index, and homepage writing links.
- `site/assets/downloads/`: resume PDF, resume Word document, and source portfolio PDF.
- `site/assets/images/`: the provided blue-jacket portrait and original images extracted from the portfolio.
- `scripts/check_site.py`: local asset, anchor, and metadata checks.
- `content/portfolio/cases.json`: reviewed case-study copy mapped to all 12 slides in the original portfolio PDF.
- `scripts/build_portfolio.py`: generates `/portfolio/` and one page per slide, including source images, PDF links, and previous/next navigation.
- `site/assets/images/portfolio/`: full-slide JPEG renders from the unchanged portfolio PDF.
- `site/assets/portfolio.css`: responsive case-study reading layout using the existing Nord/Night theme.

The content and navigation remain available without JavaScript. Native details elements provide project disclosures and article contents. There are no analytics, external fonts, submission forms, trackers, or backend services.

The migration service enquiry opens a draft in the visitor's email application; it does not submit a form or store leads. Its case study identifies Offset Figure as the historical source platform. The service page uses the official daisyUI Lemonade theme with a separate Lemonade/Night preference, and a data-migration infographic covering orders, customers, products, images, and metadata. It uses existing portfolio evidence and links to Shopify's migration and redirect guidance. Service pages are included in the generated sitemap.

## Rebuild styles and writing

```sh
npm ci
npm run build
npm run check
```

Commit the generated files under `site/` along with the sources. GitHub Pages deploys these static files; visitors do not run a CSS compiler. The full build generates portfolio pages first, then writing and the sitemap, then theme utilities. `npm run build:portfolio` rebuilds the 12 slide pages and portfolio index; `npm run build:writing` refreshes article pages, writing links, and sitemap entries for all existing portfolio pages. `npm run build:theme` rebuilds only the theme. The homepage header uses the same theme control as the article template, so header changes should be kept in sync.

The portfolio contains ten project case studies, an introductory overview, and a contact page, following the PDF's slide order. Citizen Success is retained at its existing URL but marked `listed: false`, which omits its card, incoming portfolio navigation links, collection metadata, and sitemap entry. The index presents the other eleven pages. Each page preserves the original slide as an image and links to its numbered PDF page. Historical screenshots and figures describe the source portfolio; the website does not claim that they represent the organizations' current products. The homepage's selected-work and career links open the corresponding web case studies; the complete PDF remains downloadable.

Eight historical posts were imported with their published body text, original images, and external references. Local article copies can be edited at the author’s request; update their word counts and reviewed text hashes when doing so. The ecommerce post’s Cloudflare-protected email is restored as a normal email link. Publication dates are omitted because the source pages expose only relative ages. Imported articles retain their source provenance and use their new `www.niccolox.com/writing/` addresses as canonicals. The sitemap includes the homepage, writing index, articles, and service pages. The source text hashes in `posts.json` let the checker detect accidental truncation or changes during generation.

## Content sources

The site combines Nicholas Roberts's professional resume and portfolio, [blog](https://www.niccolox.com/), and two public engineering projects:

- [Devekko Multi-Commerce](https://github.com/niccolox/devekko.multi-ecommerce): a commerce platform in active development. The [sidecar documentation](https://github.com/niccolox/devekko.multi-ecommerce/blob/master/python_sidecar/README.md) and [Elixir client](https://github.com/niccolox/devekko.multi-ecommerce/blob/master/apps/platform/lib/platform/ai/sidecar_client.ex) describe the Python integration.
- [Sovereign Source AI](https://github.com/niccolox/sovsrc.saasx2x): a local operations pilot. Its [implementation guide](https://github.com/niccolox/sovsrc.saasx2x/blob/master/docs/internal/portfolio/IMPLEMENTATION.md) describes the working slices and deployment boundaries.

Portfolio screenshots show historical work. Project stage labels distinguish commercial delivery from independent development. The two million orders and $150 million figures refer to historical migration volume and order value. The original portfolio download preserves its original wording.

## Check

```sh
python3 scripts/check_site.py
```

Before publishing substantive changes, also check desktop and mobile layout, menu keyboard behavior, project disclosures, downloads, and browser console errors.

## Original feature articles

The cybersecurity polycrisis article is an original, dated research briefing. Its reviewed source is `content/writing/the-cybersecurity-polycrisis.html`; the feature layout uses `site/assets/polycrisis.css`. The source trail distinguishes original notices, research, editorial analysis, and access limitations. Feature posts are self-canonical, dated in structured data, included in the sitemap, and covered by the same text-integrity check as imported posts. Recheck live advisories before updating time-sensitive claims.

`content/writing/cyberpolycrisis-network-map.html` extends that briefing with the 16-topic network analysis. It uses the feature layout plus `site/assets/network-map.css`, an accessible SVG graph on larger screens, and an equivalent large-text list on mobile. The article links to the six-page issue register and the full analytical model in `site/assets/downloads/`. The two PHP topics are merged, and the partly verified iPhone chain remains outside the 14-theme baseline. Its association counts are not severity or victim counts.
