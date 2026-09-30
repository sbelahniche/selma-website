"""Build the deployable multi-page site into ../public.

Run:  python3 src/export.py
Every page gets its own URL, identical to the old Webflow paths, so Google rankings carry over.
"""
import datetime, hashlib, json, pathlib, re, shutil, sys
from bs4 import BeautifulSoup

SRC = pathlib.Path(__file__).parent
sys.path.insert(0, str(SRC))
import build, blog  # noqa: E402

OUT = SRC.parent / "public"
SITE = "https://www.selmazuhause.de"
TODAY = datetime.date.today().isoformat()

MAIN_PATHS = {"start": "/", "leistungen": "/leistungen", "ratgeber": "/ratgeber", "kontakt": "/kontakt"}
# Page titles, descriptions and noindex flags exactly as on the live Webflow site (SEO continuity)
SEO = json.load(open(SRC / "content" / "seo.json"))
TRACKING = (SRC / "tracking.html").read_text()
RAPIDMAIL_POPUP = '<script src="https://t73717dc4.emailsys1a.net/form/242/2569/6d9213f71f/popup.js?_g=1765439568"></script>'

META = {
    "start": ("SELMA Zuhause | Ergotherapie bei Parkinson zu Hause",
              "Spezialisierte Ergotherapie für Menschen mit Parkinson zu Hause in Berlin: für mehr Sicherheit, Beweglichkeit und Lebensqualität im Alltag."),
    "leistungen": ("Spezialisierte Ergotherapie bei Parkinson zu Hause",
                   "Sturzprävention, Bewegungstraining, Hilfsmittel, Wohnraumanpassung und Angehörigenberatung, spezialisiert auf den Alltag mit Parkinson."),
    "ratgeber": ("Wissen & Tipps rund um Parkinson | SELMA Zuhause",
                 "Praktische Informationen zu Parkinson im Alltag: Bewegung, Wohnraumanpassung und Hilfsmittel. Für Betroffene und Angehörige."),
    "kontakt": ("Kontakt | SELMA Zuhause", None),
}
PAGE_DESC = {p["path"].strip("/"): p.get("metaDesc") or None for p in json.load(open(SRC / "content" / "pages.json"))["pages"]}

FORM_NAMES = (("form-nl", "newsletter"), ("form-frage", "frage"), ("form-erst", "erstgespraech"))

FONTS = """@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:400;font-display:swap;src:url(/assets/fonts/atkinson-next-400.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fonts/atkinson-next-700.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:800;font-display:swap;src:url(/assets/fonts/atkinson-next-800.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Mono";font-style:normal;font-weight:600;font-display:swap;src:url(/assets/fonts/atkinson-mono-600.woff2) format("woff2")}
"""
VT = "\n@media (prefers-reduced-motion:no-preference){@view-transition{navigation:auto}}\n"


def hashed(name, text):
    h = hashlib.sha1(text.encode()).hexdigest()[:8]
    stem, ext = name.rsplit(".", 1)
    fn = f"{stem}.{h}.{ext}"
    (OUT / "assets" / fn).write_text(text)
    return "/assets/" + fn


def excerpt(el, n=155):
    for p in el.select(".page-head p, .prose p, p"):
        t = re.sub(r"\s+", " ", p.get_text(" ")).strip()
        t = re.sub(r"\(\s+", "(", re.sub(r"\s+([).,;:!?])", r"\1", t))
        if len(t) > 60:
            if len(t) <= n: return t
            return t[:n].rsplit(" ", 1)[0].rstrip(",;:") + " …"
    return None


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets" / "fonts").mkdir(parents=True)
    shutil.copytree(SRC / "img", OUT / "img")
    for f in (SRC / "fonts").glob("*.woff2"):
        shutil.copy(f, OUT / "assets" / "fonts" / f.name)
    for f in (SRC / "static").iterdir():
        (shutil.copytree if f.is_dir() else shutil.copy)(f, OUT / f.name)

    css_url = hashed("style.css", FONTS + (SRC / "style.css").read_text() + VT)
    js_url = hashed("app.js", (SRC / "app-site.js").read_text())

    soup = BeautifulSoup(build.render_body(), "html.parser")
    pages = soup.select("[data-page]")

    # ---- URL for every page, and which page every in-page anchor lives on
    path = {}
    for p in pages:
        pid = p["id"]
        if pid in MAIN_PATHS: path[pid] = MAIN_PATHS[pid]
        elif pid.startswith("kategorie-"): path[pid] = "/posts-categories/" + pid[len("kategorie-"):]
        elif p.has_attr("data-article"): path[pid] = "/blog-posts/" + pid
        else: path[pid] = "/" + pid
    owner = {}
    for p in pages:
        for el in p.find_all(id=True):
            owner.setdefault(el["id"], p["id"])

    # ---- Search index (full article text, loaded on demand)
    index = [{"u": path[p["id"]], "t": re.sub(r"\s+", " ", p.find("h1").get_text(" ")).strip(), "c": p.get("data-cat", ""),
              "x": re.sub(r"\s+", " ", (p.select_one(".prose") or p).get_text(" ")).strip()} for p in pages if p.has_attr("data-article")]
    search_url = hashed("search.json", json.dumps(index, ensure_ascii=False))

    # ---- Shared chrome
    app = soup.find(id="app")
    skip, header, footer = app.find(class_="skip"), app.find("header"), app.find("footer")
    ck = footer.find(attrs={"data-cookie": True})  # opens the Silktide cookie settings
    if ck:
        del ck["data-cookie"]; ck["data-cookie-settings"] = "open"
    sprite = build.sprite

    def fix_links(root, here):
        for a in root.find_all("a", href=True):
            h = a["href"]
            if not h.startswith("#") or h == "#main": continue
            t = h[1:]
            if t in path: a["href"] = path[t]
            elif t in owner: a["href"] = h if owner[t] == here else path[owner[t]] + h
        for el in root.find_all(["img", "source", "video"]):
            for attr in ("src", "poster"):
                if el.get(attr, "").startswith("img/"): el[attr] = "/" + el[attr]

    def fix_forms(root, here):
        for f in root.find_all("form"):
            if f.get("id") == "rg-search":
                f["data-index"] = search_url; continue
            name = next(n for pre, n in FORM_NAMES if f["id"].startswith(pre))
            f["name"], f["method"], f["data-netlify"], f["netlify-honeypot"] = name, "POST", "true", "bot-field"
            f.insert(0, BeautifulSoup(f'<input type="hidden" name="form-name" value="{name}">'
                                      f'<input type="hidden" name="seite" value="{path[here]}">'
                                      '<p hidden><label>Bitte leer lassen: <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>',
                                      "html.parser"))

    def document(pid, main_html, title, desc, section, og_type="website"):
        hdr = BeautifulSoup(str(header), "html.parser")
        ftr = BeautifulSoup(str(footer), "html.parser")
        for part in (hdr, ftr): fix_links(part, pid)
        for a in hdr.select("[data-nav]"):
            if a["href"] == path.get(section, "#"): a["aria-current"] = "page"
            elif a.has_attr("aria-current"): del a["aria-current"]
        p_url = path.get(pid, "/")
        title = SEO["titles"].get(p_url, title)
        desc = SEO["descriptions"].get(p_url, desc)
        noindex = pid == "404" or p_url in SEO["noindex"]
        url = SITE + (p_url if pid != "404" else "/404")
        meta = f'<meta name="description" content="{esc(desc)}">\n' if desc else ""
        og_desc = f'<meta property="og:description" content="{esc(desc)}">\n' if desc else ""
        canon = (f'<link rel="canonical" href="{url}">\n' if pid != "404" else "") + ('<meta name="robots" content="noindex">\n' if noindex else "")
        return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
{meta}{canon}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="SELMA Zuhause">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{esc(title)}">
{og_desc}<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="576">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#cdeff0">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/atkinson-next-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/atkinson-next-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{css_url}">
{TRACKING}</head>
<body>
{sprite}
<div id="app">
{skip}
{hdr}
<main id="main">
{main_html}
</main>
{ftr}
</div>
<script src="{js_url}" defer></script>
{RAPIDMAIL_POPUP if pid == "start" else ""}
</body>
</html>
"""

    sitemap = []
    for p in pages:
        pid = p["id"]
        fix_links(p, pid); fix_forms(p, pid)
        section = p.get("data-section") or pid
        title = p.get("data-title")
        desc = None
        if pid in META:
            title, desc = META[pid]
        elif p.has_attr("data-article"):
            desc = blog.META.get(pid, {}).get("excerpt")
        elif pid in PAGE_DESC:
            desc = PAGE_DESC[pid]
        if not desc and pid == "kontakt":
            desc = excerpt(p)
        for a in ("hidden", "data-title"):
            if p.has_attr(a): del p[a]
        html = document(pid, str(p), title, desc, section, "article" if p.has_attr("data-article") else "website")
        fn = OUT / ("index.html" if path[pid] == "/" else path[pid].lstrip("/") + ".html")
        fn.parent.mkdir(parents=True, exist_ok=True)
        fn.write_text(html)
        if path[pid] not in SEO["noindex"]:
            sitemap.append(SITE + (path[pid] if path[pid] != "/" else "/"))

    nf = """<div data-page id="nicht-gefunden">
<section aria-labelledby="nf-title" class="page-head bg-mint"><div class="wrap">
<h1 id="nf-title" tabindex="-1">Seite nicht gefunden</h1>
<p class="lead">Diese Seite gibt es leider nicht (mehr). Vielleicht finden Sie das Gesuchte über die Navigation oben.</p>
</div></section>
<section class="section"><div class="wrap"><div class="btn-row">
<a class="btn btn-primary" href="/">Zur Startseite<span class="btn-ic"><svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></span></a>
<a class="btn btn-ghost btn-plain" href="/kontakt">Kontakt</a>
</div></div></section></div>"""
    (OUT / "404.html").write_text(document("404", nf, "Seite nicht gefunden | SELMA Zuhause", None, ""))

    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in sitemap) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"built {len(pages) + 1} pages into {OUT}")


if __name__ == "__main__":
    main()
