"""Builds the Ratgeber article pages and category pages from the content exported from selmazuhause.de."""
import json, re
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = str(__import__("pathlib").Path(__file__).parent / "content" / "articles.json")
DATE_ISO, DATE_DE = "2026-09-13", "13. September 2026"

CATS = {
    "medikamente-alltag": "Medikamente & Alltag",
    "grundlagen-leitlinie": "Grundlagen & Leitlinie",
    "hilfsmittel-wohnraum": "Hilfsmittel & Wohnraum",
    "bewegung-training": "Bewegung & Training",
}

# Order as on the live Ratgeber page (featured first, then "Aktuelle Beiträge")
ORDER = [
    "s2k-leitlinie-parkinson-ergotherapie",
    "parkinson-medikamente-nebenwirkungen-alltag",
    "pwr-moves-parkinson-training",
    "freezing-bei-parkinson-hilfsmittel-im-uberblick",
    "lsvt-big",
]

META = {
    "s2k-leitlinie-parkinson-ergotherapie": dict(
        cat="grundlagen-leitlinie", author="Kathleen Olstedt", thumb="blog-leitlinie.webp", tw=1100, th=733,
        hero=(1200, 800), alt="Gedruckte S2k-Leitlinie Parkinson der AWMF auf einem Holztisch",
        excerpt="Die S2k-Leitlinie Parkinson-Krankheit empfiehlt Ergotherapie ausdrücklich als Teil der strukturierten Versorgung. Was das konkret im Alltag bedeutet, und warum Hausbesuche klinisch sinnvoll sind, findet sich in diesem Artikel."),
    "parkinson-medikamente-nebenwirkungen-alltag": dict(
        cat="medikamente-alltag", author="Kathleen Olstedt", thumb="blog-medikamente.webp", tw=900, th=506,
        hero=(1200, 675), alt="Bunte Tabletten und eine umgekippte Medikamentendose auf blauem Grund",
        excerpt="Parkinson-Medikamente wirken. Und sie haben Nebenwirkungen. Was das im Alltag bedeutet und wie Betroffene und Angehörige besser damit umgehen können, wird in diesem Artikel behandelt."),
    "pwr-moves-parkinson-training": dict(
        cat="bewegung-training", author="Kathleen Olstedt", thumb="blog-pwr.webp", tw=900, th=600,
        hero=(1200, 800), alt="Älterer Mann geht mit großem Schritt durch die offene Haustür nach draußen",
        excerpt="PWR!Moves® ist ein evidenzbasiertes Bewegungsprogramm, das gezielt die Fähigkeiten trainiert, die Parkinson am stärksten einschränkt. Hier erfahren Sie, was hinter dem Programm steckt, wie es sich von LSVT BIG® unterscheidet und was Sie selbst täglich tun können."),
    "freezing-bei-parkinson-hilfsmittel-im-uberblick": dict(
        cat="hilfsmittel-wohnraum", author=None, thumb="blog-freezing.webp", tw=900, th=506,
        hero=(1200, 675), alt="Schuhe mit Laser-Aufsatz projizieren grüne Linien auf einen Holzboden",
        excerpt=None),
    "lsvt-big": dict(
        cat="bewegung-training", author=None, thumb="blog-lsvt.webp", tw=900, th=635,
        hero=(1024, 722), alt="Älterer Mann macht im Wohnzimmer einen großen Ausfallschritt mit ausgestreckten Armen",
        excerpt="Wir zeigen, wie LSVT BIG® eingesetzt wird, für wen das Programm laut Forschung am wirksamsten ist und wie es helfen kann, Bewegungsfreiheit, Alltagssicherheit und Selbstständigkeit länger zu erhalten."),
}

INLINE_IMG = {
    "6a259bbc9193bf3937649765_image.png": ("pwr-uebungen.webp", 1200, 800, "wide",
        "Acht Fotos einer älteren Frau bei PWR!Moves®-Übungen: im Sitzen auf dem Stuhl, im Stehen, im Knien und im Liegen auf der Matte"),
    "6a2597992c253b9e5e2f69ba_1.png": ("pwr-uebersicht.webp", 1600, 809, "wide",
        "Übersicht der vier PWR!Moves®: PWR! Up – Aufrichten und größer werden, Beispiel: vom Stuhl aufstehen, ohne nach vorne zu kippen. "
        "PWR! Rock – Gewicht verlagern und Balance verbessern, Beispiel: im Stehen die Hose anziehen oder nach etwas im Schrank greifen. "
        "PWR! Step – den ersten Schritt erleichtern, Beispiel: den ersten Schritt machen, wenn die Füße „festkleben“. "
        "PWR! Twist – Drehen und Rotieren, Beispiel: sich in der Küche umdrehen oder nachts im Bett wenden."),
    "6a12e98eb4c33bf17f4e13d9_LSVT%20Zertifikat.png": ("lsvt-zertifikat.webp", 420, 300, "small", "Siegel: LSVT BIG® Certified"),
}

FREEZING_H2 = {"Was beim Freezing passiert", "Was es gibt, was es kostet", "Wie SELMA Zuhause unterstützt"}
EXT = '<span class="sr-only"> (öffnet in neuem Tab)</span>'
EXT_PDF = '<span class="sr-only"> (PDF, öffnet in neuem Tab)</span>'


def _segments(p):
    """Split a paragraph's children at <br> tags (whitespace-only strings dropped at the edges)."""
    segs, cur = [], []
    for c in list(p.contents):
        if isinstance(c, Tag) and c.name == "br":
            segs.append(cur); cur = []
        else:
            cur.append(c)
    segs.append(cur)
    clean = []
    for s in segs:
        while s and isinstance(s[0], NavigableString) and not s[0].strip(): s = s[1:]
        while s and isinstance(s[-1], NavigableString) and not s[-1].strip(): s = s[:-1]
        clean.append(s)
    return [s for s in clean if s]


def _p(soup, nodes, cls=None):
    p = soup.new_tag("p")
    if cls: p["class"] = cls
    for n in nodes: p.append(n.extract() if hasattr(n, "extract") else n)
    return p


def transform(slug, html):
    html = html.replace("\u200d", "").replace("\xa0", " ").replace("&nbsp;", " ")
    soup = BeautifulSoup(html, "html.parser")

    # Figures -> clean <figure><img></figure> with real alt text and local files
    for fig in soup.find_all("figure"):
        img = fig.find("img")
        key = img["src"].split("/")[-1]
        name, w, h, size, alt = INLINE_IMG[key]
        new = soup.new_tag("figure", attrs={"class": f"fig fig-{size}"})
        new.append(soup.new_tag("img", attrs={"src": "img/" + name, "width": str(w), "height": str(h), "alt": alt, "loading": "lazy"}))
        fig.replace_with(new)

    # Headings are bold already
    for hd in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
        for s in hd.find_all("strong"): s.unwrap()
        txt = hd.get_text().strip(); hd.clear(); hd.string = txt

    # "____" separators -> <hr>
    for p in soup.find_all("p"):
        if re.fullmatch(r"_{3,}", p.get_text().strip()): p.replace_with(soup.new_tag("hr"))

    # Trailing <br> and empty paragraphs
    for p in soup.find_all("p"):
        while p.contents and ((isinstance(p.contents[-1], Tag) and p.contents[-1].name == "br") or (isinstance(p.contents[-1], NavigableString) and not p.contents[-1].strip())):
            p.contents[-1].extract()
        if not p.get_text().strip() and not p.find("img"): p.decompose()

    if slug == "freezing-bei-parkinson-hilfsmittel-im-uberblick":
        for p in list(soup.find_all("p")):
            segs = _segments(p)
            if not segs or not (len(segs[0]) == 1 and isinstance(segs[0][0], Tag) and segs[0][0].name == "strong"):
                continue
            title = segs[0][0].get_text().strip()
            if title in FREEZING_H2 and len(segs) == 1:
                h = soup.new_tag("h2"); h.string = title; p.replace_with(h)
                nxt = h.find_next_sibling()
                if nxt is not None and nxt.name == "p" and nxt.get_text().strip() == title:
                    nxt.decompose()  # the live page repeats this heading as a plain line
                continue
            h = soup.new_tag("h3"); h.string = title
            new_nodes = [h]
            body = segs[1:]
            price = None
            if body and len(body[-1]) == 1 and isinstance(body[-1][0], Tag) and body[-1][0].name == "em" and body[-1][0].get_text().strip().startswith("Preis"):
                price = body.pop()
            for seg in body: new_nodes.append(_p(soup, seg))
            if price: new_nodes.append(_p(soup, list(price[0].contents), "price"))
            p.replace_with(*new_nodes)
        # Paragraphs that end with a price line (entry whose text sits in its own <p>)
        for p in list(soup.find_all("p")):
            segs = _segments(p)
            if len(segs) > 1 and len(segs[-1]) == 1 and isinstance(segs[-1][0], Tag) and segs[-1][0].name == "em" and segs[-1][0].get_text().strip().startswith("Preis"):
                price = segs.pop()
                nodes = []
                for i, seg in enumerate(segs):
                    nodes.extend(seg)
                p.replace_with(_p(soup, nodes), _p(soup, list(price[0].contents), "price"))

    if slug == "pwr-moves-parkinson-training":
        # Study citations on their own line
        for p in soup.find_all("p"):
            segs = _segments(p)
            if len(segs) > 1 and len(segs[-1]) == 1 and isinstance(segs[-1][0], Tag) and segs[-1][0].name == "em":
                for br in p.find_all("br"): br.decompose()
                segs[-1][0]["class"] = "cite"
        # "A / B / C" lines after "Typische Alltagssituationen:" -> real lists
        for p in list(soup.find_all("p")):
            prev = p.find_previous_sibling()
            if prev is not None and prev.name == "p" and prev.get_text().strip() == "Typische Alltagssituationen:" and " / " in p.get_text():
                ul = soup.new_tag("ul")
                for item in [t.strip() for t in p.get_text().split(" / ") if t.strip()]:
                    li = soup.new_tag("li"); li.string = item; ul.append(li)
                p.replace_with(ul)

    # Source line under the quote; notes and callouts
    for bq in soup.find_all("blockquote"):
        nxt = bq.find_next_sibling()
        if nxt is not None and nxt.name == "p" and nxt.get_text().strip().startswith("Quelle:"):
            nxt["class"] = "source"
    for p in soup.find_all("p"):
        kids = [c for c in p.contents if not (isinstance(c, NavigableString) and not c.strip())]
        if len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name == "em" and len(p.get_text()) > 120:
            kids[0].unwrap(); p["class"] = "note"
        elif len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name == "strong" and len(p.get_text()) > 200:
            kids[0].unwrap(); p["class"] = "callout"

    # Links
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if href == "/kontakt":
            a["href"] = "#kontakt"
            if a.get_text().strip() == "Erstgespräch anfragen":
                a["class"] = "btn btn-primary"
                a.append(BeautifulSoup('<span class="btn-ic">{{i:arrow}}</span>', "html.parser"))
                par = a.find_parent("p")
                if par is not None: par["class"] = "article-cta"
        elif href.startswith("http"):
            a["target"] = "_blank"; a["rel"] = "noopener"
            a.append(BeautifulSoup(EXT_PDF if href.lower().endswith(".pdf") else EXT, "html.parser"))

    # Heading levels: start at h2 under the page h1, never skip a level
    stack = []  # (original level, new level)
    for h in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
        o = int(h.name[1])
        while stack and stack[-1][0] >= o: stack.pop()
        new = stack[-1][1] + 1 if stack else 2
        stack.append((o, new))
        h.name = f"h{new}"

    # Only the attributes we set ourselves survive
    allowed = {"a": {"href", "class", "target", "rel"}, "img": {"src", "alt", "width", "height", "loading"}, "figure": {"class"}, "p": {"class"}, "em": {"class"}, "span": {"class"}}
    for t in soup.find_all(True):
        keep = allowed.get(t.name, set())
        for k in list(t.attrs):
            if k not in keep: del t.attrs[k]
    return str(soup)


def load():
    data = json.load(open(SRC))
    arts = {a["slug"]: a for a in data["articles"]}
    out = []
    for slug in ORDER:
        a = arts[slug]; m = META[slug]
        out.append(dict(slug=slug, title=a["title"], cat=m["cat"], catname=CATS[m["cat"]], **{k: v for k, v in m.items() if k != "cat"}, body=transform(slug, a["html"])))
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def byline(a):
    parts = []
    if a["author"]: parts.append('<span>{{i:user}}' + a["author"] + '</span>')
    parts.append('<span>{{i:calendar}}<time datetime="' + DATE_ISO + '">' + DATE_DE + '</time></span>')
    return '<p class="byline">' + "".join(parts) + "</p>"


def newsletter(suffix):
    return f'''  <section class="section bg-peach nl" aria-labelledby="nl-title-{suffix}">
    <div class="wrap">
      <div class="intro">
        <h2 id="nl-title-{suffix}" class="rv-split">Auf dem Laufenden Bleiben</h2>
        <p class="rv" style="--d:120ms">Tipps für den Alltag mit Parkinson, kostenlose Online-Workshops und neue Veranstaltungen – gelegentlich und jederzeit abbestellbar.</p>
      </div>
      <div class="rv" style="--d:200ms">
        <!-- Opens the rapidmail sign-up pop-up (double opt-in), same list as everywhere -->
        <button class="btn btn-primary rm-open-popup" type="button" aria-haspopup="dialog">Jetzt anmelden<span class="btn-ic">{{{{i:arrow}}}}</span></button>
        <p class="fineprint" style="margin-top:16px">*Mit der Anmeldung erklären Sie sich einverstanden, per E-Mail Tipps, Workshops und Veranstaltungen von SELMA Zuhause zu erhalten. Jederzeit abbestellbar. Weitere Infos in der <a href="#datenschutzerklarung">Datenschutzerklärung</a>.</p>
      </div>
    </div>
  </section>'''


def card(a, delay, chip=True):
    excerpt = f'\n          <p class="excerpt">{esc(a["excerpt"])}</p>' if a["excerpt"] else ""
    chip_html = f'\n          <a class="chip" href="#kategorie-{a["cat"]}">{esc(a["catname"])}</a>' if chip else ""
    return f'''        <li class="post-card rv" style="--d:{delay}ms">
          <div class="media rv-img" style="--d:{delay}ms"><img src="img/{a["thumb"]}" width="{a["tw"]}" height="{a["th"]}" alt="" loading="lazy"></div>{chip_html}
          <h3><a href="#{a["slug"]}">{esc(a["title"])}</a></h3>{excerpt}
          {byline(a)}
        </li>'''


def article_page(a):
    w, h = a["hero"]
    return f'''
<!-- ======================= ARTIKEL: {a["slug"]} ======================= -->
<div data-page data-article data-section="ratgeber" id="{a["slug"]}" data-cat="{esc(a["catname"])}" data-title="{esc(a["title"])} | SELMA Zuhause" hidden>
  <article aria-labelledby="{a["slug"]}-title">
    <header class="article-head bg-mint">
      <div class="wrap">
        <nav class="crumbs" aria-label="Brotkrumen"><ol><li><a href="#ratgeber">Ratgeber</a></li></ol></nav>
        <h1 id="{a["slug"]}-title" class="rv-split" tabindex="-1">{esc(a["title"])}</h1>
        {byline(a)}
      </div>
    </header>
    <div class="wrap article-hero"><div class="media rv-img"><img src="img/art-{a["slug"]}.webp" width="{w}" height="{h}" alt="{esc(a["alt"])}" loading="lazy"></div></div>
    <div class="wrap article-body"><div class="prose">
{a["body"]}
    </div></div>
  </article>
{newsletter(a["slug"])}
</div>'''


def category_page(cat, arts):
    name = CATS[cat]
    items = [a for a in arts if a["cat"] == cat]
    cards = "\n".join(card(a, i * 120, chip=False) for i, a in enumerate(items))
    return f'''
<!-- ======================= KATEGORIE: {cat} ======================= -->
<div data-page data-section="ratgeber" id="kategorie-{cat}" data-title="{esc(name)} | SELMA Zuhause" hidden>
  <section class="page-head bg-mint" aria-labelledby="kategorie-{cat}-title">
    <div class="wrap">
      <nav class="crumbs" aria-label="Brotkrumen"><ol><li><a href="#ratgeber">Ratgeber</a></li><li><span aria-current="page">{esc(name)}</span></li></ol></nav>
      <h1 id="kategorie-{cat}-title" class="rv-split" tabindex="-1">{esc(name)}</h1>
    </div>
  </section>
  <section class="section" aria-label="Beiträge: {esc(name)}">
    <div class="wrap">
      <ul class="cards-3 posts">
{cards}
      </ul>
    </div>
  </section>
{newsletter("k-" + cat)}
</div>'''


def render():
    arts = load()
    return "\n".join([article_page(a) for a in arts] + [category_page(c, arts) for c in CATS])


if __name__ == "__main__":
    for a in load():
        print("=====", a["slug"], len(a["body"]))
        print(a["body"][:600])
