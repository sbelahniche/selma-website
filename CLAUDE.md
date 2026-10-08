# SELMA Zuhause website – instructions for Claude Code

This repo is the static website selmazuhause.de, owned by Kathleen Olstedt (Ergotherapie bei Parkinson). Netlify publishes the `public/` folder automatically on every push to `main`.

Kathleen is not a developer. Talk to her in German, in plain words, briefly. Explain what you changed, not how the code works.

## Workflow for every change

1. **Get the latest version first:** `git pull`
2. **Edit the source files**, never `public/` (it is generated).
3. **Rebuild:** `python3 src/export.py`
4. **Preview:**
   - In the Claude desktop app, start the preview server "selma" (`.claude/launch.json`; it rebuilds first). The site opens in the Browser pane. After further edits, rebuild and reload.
   - In the terminal, start `python3 src/preview.py` and tell Kathleen to open http://localhost:8000.
   - Either way, show Kathleen the changed page and let her check it.
5. **Only after Kathleen says it looks good:** commit with a short German message (`git add -A && git commit -m "…"`). Kathleen pushes with GitHub Desktop ("Push origin"). Push yourself only if she explicitly asks.
6. Netlify deploys in about 1 minute. Live: https://www.selmazuhause.de

### Don't waste deploys
Each push costs 15 of 300 free Netlify credits per month. Collect several small changes, then push once, at most about 10–15 pushes per month. Remind Kathleen of this if she wants to push many tiny changes.

## Where content lives

| What | File |
|---|---|
| Start, Leistungen, Ratgeber, Kontakt pages, header, footer | `src/body.html` |
| FAQ (shown on Start and Leistungen) | `src/faq.html` |
| Ratgeber articles (blog) | `src/content/articles.json` (images: `src/img/art-<slug>.webp`) |
| Info pages: AGB, Verträge, Jobs, Impressum, Datenschutz, Verordnung … | `src/content/pages.json` |
| Workshops: dates, texts, topic pages `/workshop-<slug>` (past dates hide themselves) | `src/content/workshops.json`, rendered by `src/workshops.py` |
| Page titles, meta descriptions, noindex (SEO) | `src/content/seo.json` |
| Design (colors, spacing) | `src/style.css`, documented in `SELMA-Design-System.md` |
| Images | `src/img/` (use `.webp`, about 1600 px max width) |
| Text for AI search engines | `src/static/llms.txt` (update it when services, prices or contact data change) |
| Redirects | `src/static/_redirects` |

## Rules

- **SEO: never change existing URLs** (`/leistungen`, `/blog-posts/<slug>`, `/posts-categories/<slug>` …). If a page must move, add a 301 in `src/static/_redirects`.
- New article: three things are needed.
  1. The text goes in `src/content/articles.json` (`slug`, `title`, `category`, `categoryHref`, `html`, `docTitle`, `metaDesc`).
  2. Its card and image data go in `src/blog.py`: add the slug to `ORDER` (first = featured) and an entry to `META` (category slug, author "Kathleen Olstedt", thumbnail, hero size, alt text, excerpt).
  3. Images go in `src/img/`: `art-<slug>.webp` (hero) and a thumbnail `blog-<name>.webp`.
  Copy an existing article as the pattern, then rebuild.
- **Keep facts consistent everywhere** (pages, FAQ, footer, `llms.txt`):
  - Phone 030 3758 0867
  - info@selmazuhause.de
  - Blockdammweg 63, 10318 Berlin
  - Mo–Fr 9:00–18:00 Uhr
  - Einzugsgebiet: Berlin Südost & Charlottenburg
- Forms (Netlify Forms `erstgespraech`, `frage`, `newsletter`) and the cookie banner (Silktide, `src/tracking.html`) are GDPR-relevant. Don't change them without being asked. Google Analytics must only load after consent.
- When adding a new service or tool that processes personal data, tell Kathleen that the Datenschutzerklärung needs updating.
- Follow `SELMA-Design-System.md`:
  - Atkinson Hyperlegible font, body text at least 18 px, contrast at least 4.5:1.
  - Address readers as "Sie", in a calm and concrete tone.
- Don't add new libraries, frameworks or build tools. The site is plain HTML/CSS/JS built by Python (only dependency: `beautifulsoup4`).
- Check after building: the build prints `built 26 pages` (more if pages were added) with no error.

## If something breaks

- If the build fails with `No module named bs4`, run `python3 -m pip install --user beautifulsoup4`.
- If preview port 8000 is busy, run `python3 src/preview.py 8001`.
- If a push was wrong, fix it and push again, or undo it with `git revert HEAD` and push. Netlify can also roll back under Deploys → choose an older deploy → "Publish deploy".
