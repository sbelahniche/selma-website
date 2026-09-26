# SELMA Zuhause – Website

Static website for [selmazuhause.de](https://www.selmazuhause.de), hosted on Netlify.

## Structure

| Folder | What it is |
|---|---|
| `public/` | The finished website. Netlify publishes this folder as is. **Don't edit by hand**, it's generated. |
| `src/body.html`, `src/faq.html` | Start, Leistungen, Ratgeber, Kontakt pages, header and footer |
| `src/content/articles.json` | Blog articles (Ratgeber) |
| `src/content/pages.json` | Info pages: AGB, Verträge, Jobs, Impressum, Datenschutz, Verordnung … |
| `src/blog.py`, `src/pages.py` | Turn the content into pages (images, excerpts, authors) |
| `src/style.css`, `src/app-site.js` | Design and behaviour |
| `src/img/`, `src/fonts/`, `src/static/` | Images, self-hosted fonts, favicon, share image, redirects |

## Making a change

```bash
pip3 install beautifulsoup4      # once
python3 src/export.py            # rebuilds public/
git add -A && git commit -m "…" && git push   # Netlify deploys automatically
```

Page addresses are the same as on the old Webflow site (`/leistungen`, `/blog-posts/…`, `/posts-categories/…`).

## Forms

Contact, question and newsletter forms use Netlify Forms (form names: `erstgespraech`, `frage`, `newsletter`).
Submissions appear in Netlify under **Forms**; set up email notifications there.
