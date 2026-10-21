# Nicholas Roberts resume site

A responsive, dependency-free resume and portfolio site for `niccolox/niccolox.github.io`.

## Preview

Run from this directory:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:4173`. No package installation or build is needed.

## Publish on GitHub Pages

Push this directory's contents to the `main` branch of `niccolox/niccolox.github.io`. In the repository's **Settings → Pages**, set **Source** to **GitHub Actions**. The included workflow validates the files and deploys only `site/` on each push to `main` or manual workflow run.

The intended address is `https://niccolox.github.io/`. No custom domain or DNS changes are included. The existing blog at `www.niccolox.com` stays linked from the site.

GitHub's [custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) describes the Pages configuration.

## Edit

- `site/index.html`: copy, projects, experience, links, and Person structured data.
- `site/assets/styles.css`: layout, responsive behavior, color, and print styles.
- `site/assets/site.js`: mobile navigation, current year, and printing.
- `site/assets/downloads/`: resume PDF, resume Word document, and source portfolio PDF.
- `site/assets/images/`: the provided blue-jacket portrait and original images extracted from the portfolio.
- `scripts/check_site.py`: local asset, anchor, and metadata checks.

The content and navigation remain available without JavaScript. Native details elements provide project and career disclosures. There are no analytics, external fonts, forms, trackers, or backend services.

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
