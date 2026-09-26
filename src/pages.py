"""Builds Verordnung, AGB & Verträge (with its documents), Jobs, Impressum and Datenschutz pages from the exported live content."""
import json, re
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = str(__import__("pathlib").Path(__file__).parent / "content" / "pages.json")
EXT = '<span class="sr-only"> (öffnet in neuem Tab)</span>'

# live path -> page id in the new site (all bare #tokens)
ROUTES = {
    "/verordnung-gkv": "verordnung-gkv",
    "/patienteninformationen": "patienteninformationen",
    "/agb": "agb",
    "/behandlungsvertrag": "behandlungsvertrag",
    "/patienteninformation-datenschutz": "patienteninformation-datenschutz",
    "/einwilligung-anonymisierte-daten": "einwilligung-anonymisierte-daten",
    "/einwilligung-versorgungskoordination": "einwilligung-versorgungskoordination",
    "/videotherapie": "videotherapie",
    "/jobs": "jobs",
    "/jobs-ergotherapie-berlin": "jobs-ergotherapie-berlin",
    "/impressum": "impressum",
    "/datenschutzerklarung": "datenschutzerklarung",
    "/kontakt": "kontakt", "/leistungen": "leistungen", "/ratgeber": "ratgeber", "/": "start",
}
TITLES = {  # browser-tab titles (live titles, harmonised)
    "/verordnung-gkv": "Verordnung (GKV) | SELMA Zuhause",
    "/impressum": "Impressum | SELMA Zuhause",
}
VERORDNUNG_IMG = ("verordnung-beispiel.webp", 1086, 1448,
    "Beispiel einer ausgefüllten Heilmittelverordnung (Muster 13), quer bedruckt mit „Muster“: Ergotherapie angekreuzt, "
    "ICD-10-Code G20.11, Diagnosegruppe EN1, Leitsymptomatik a, Heilmittel „Sensomotorisch-perzeptive Behandlung "
    "(Doppelbehandlung)“ mit 20 Behandlungseinheiten, Hausbesuch „ja“ angekreuzt, Therapiefrequenz 1–2 x wöchentlich.")


def _clean_text(html):
    for ch in ("‍", "​"):
        html = html.replace(ch, "")
    return html.replace("\xa0", " ").replace("&nbsp;", " ")


def _route(href):
    if href in ROUTES: return "#" + ROUTES[href]
    return None


def transform(path, html):
    soup = BeautifulSoup(_clean_text(html), "html.parser")
    for t in soup.find_all(["script", "style"]): t.decompose()
    for d in soup.find_all(["div", "span"]):
        if d.name == "div": d.unwrap()

    if path == "/verordnung-gkv":
        h1 = soup.find("h1")
        if h1: h1.decompose()
        img = soup.find("img")
        name, w, h, alt = VERORDNUNG_IMG
        fig = soup.new_tag("figure", attrs={"class": "fig fig-doc"})
        fig.append(soup.new_tag("img", attrs={"src": "img/" + name, "width": str(w), "height": str(h), "alt": alt, "loading": "lazy"}))
        img.replace_with(fig)
        # "☐ ..." lines -> a real checklist
        for p in soup.find_all("p"):
            if "☐" in p.get_text():
                ul = soup.new_tag("ul", attrs={"class": "checklist"})
                li = soup.new_tag("li")
                for c in list(p.contents):
                    if isinstance(c, Tag) and c.name == "br":
                        if li.get_text().strip(): ul.append(li)
                        li = soup.new_tag("li"); continue
                    if isinstance(c, NavigableString) and "☐" in c:
                        c = NavigableString(c.replace("☐", "").lstrip())
                        if not str(c): continue
                    li.append(c.extract() if hasattr(c, "parent") and c.parent is not None else c)
                if li.get_text().strip(): ul.append(li)
                p.replace_with(ul)

    if path == "/agb":
        h = soup.find(["h5", "h4"])
        if h: h.decompose()  # becomes the page h1

    # Headings: plain text, no trailing breaks
    for hd in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        txt = re.sub(r"\s+", " ", hd.get_text()).strip()
        hd.clear(); hd.string = txt

    # Empty paragraphs; trailing / leading line breaks inside paragraphs
    for p in soup.find_all("p"):
        while p.contents and ((isinstance(p.contents[-1], Tag) and p.contents[-1].name == "br") or (isinstance(p.contents[-1], NavigableString) and not p.contents[-1].strip())):
            p.contents[-1].extract()
        while p.contents and ((isinstance(p.contents[0], Tag) and p.contents[0].name == "br") or (isinstance(p.contents[0], NavigableString) and not p.contents[0].strip())):
            p.contents[0].extract()
        if not p.get_text().strip() and not p.find("img"): p.decompose()

    # Links
    for a in soup.find_all("a"):
        href = a.get("href", "")
        txt = a.get_text().strip()
        r = _route(href)
        if r:
            a["href"] = r
            par = a.find_parent("p")
            only = par is not None and par.get_text().strip() == txt
            if txt.startswith("Zurück zur Übersicht") and only:
                par["class"] = "back-link"
                a.insert(0, BeautifulSoup("{{i:arrowl}}", "html.parser"))
            elif only and (txt.endswith(" lesen") or txt.startswith("Zum ") or txt.startswith("Alle ")):
                par["class"] = "more-link"
                a.append(BeautifulSoup("{{i:arrow}}", "html.parser"))
        elif href.startswith("http"):
            a["target"] = "_blank"; a["rel"] = "noopener"
            a.append(BeautifulSoup(EXT, "html.parser"))

    # Heading levels under the page h1: h2, h3 ... without skipping
    stack = []
    for h in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
        o = int(h.name[1])
        while stack and stack[-1][0] >= o: stack.pop()
        new = stack[-1][1] + 1 if stack else 2
        stack.append((o, new)); h.name = f"h{new}"

    allowed = {"a": {"href", "class", "target", "rel"}, "img": {"src", "alt", "width", "height", "loading"},
               "figure": {"class"}, "p": {"class"}, "ul": {"class"}, "span": {"class"}}
    for t in soup.find_all(True):
        keep = allowed.get(t.name, set())
        for k in list(t.attrs):
            if k not in keep: del t.attrs[k]
    return str(soup).strip()


def title_parts(p):
    """(main, sub) from the live title block; AGB and Verordnung carry their heading in the content."""
    if p["path"] == "/verordnung-gkv": return "Verordnung (GKV)", None
    if p["path"] == "/agb": return "Hinweis zu den AGB", None
    s = BeautifulSoup(_clean_text(p["title"]), "html.parser")
    h1 = s.find("h1")
    sub = h1.find("span")
    sub_txt = re.sub(r"\s+", " ", sub.get_text()).strip() if sub else None
    if sub: sub.decompose()
    main = re.sub(r"\s+", " ", h1.get_text()).strip()
    return main, sub_txt


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def contact_block(sfx):
    return f'''  <section class="section bg-mist ask" aria-labelledby="ask-title-{sfx}">
    <div class="wrap">
      <div class="intro">
        <p class="eyebrow rv">Kontakt</p>
        <h2 id="ask-title-{sfx}" class="rv-split">Sie haben eine Frage?</h2>
        <p class="rv" style="--d:120ms">Wir antworten per E-Mail oder rufen auf Wunsch zurück. Bei Rückrufwunsch bitte Telefonnummer angeben.</p>
      </div>
      <div class="form-card rv" style="--d:160ms">
        <form id="form-frage-{sfx}" novalidate data-done="Vielen Dank! Wir haben Ihre Nachricht erhalten.">
          <div class="form-summary" hidden tabindex="-1"></div>
          <div class="form-grid">
            <div class="field">
              <label for="frage-email-{sfx}">E-Mail <span class="opt">(Pflichtfeld)</span></label>
              <input id="frage-email-{sfx}" name="email" type="email" autocomplete="email" required data-msg="Bitte geben Sie Ihre E-Mail-Adresse an, z. B. name@beispiel.de.">
            </div>
            <div class="field">
              <label for="frage-tel-{sfx}">Telefon <span class="opt">(falls Rückruf erwünscht)</span></label>
              <input id="frage-tel-{sfx}" name="telefon" type="tel" autocomplete="tel">
            </div>
            <div class="field full">
              <label for="frage-msg-{sfx}">Ihre Nachricht <span class="opt">(Pflichtfeld)</span></label>
              <textarea id="frage-msg-{sfx}" name="nachricht" required data-msg="Bitte schreiben Sie uns kurz, worum es geht."></textarea>
            </div>
          </div>
          <div class="form-foot">
            <button class="btn btn-primary" type="submit">Versenden<span class="btn-ic">{{{{i:arrow}}}}</span></button>
            <p class="fineprint">*Mit Absenden der Anfrage erklären Sie sich einverstanden, dass wir Ihre Angaben zur Beantwortung der Anfrage verwenden. Weitere Infos in der <a href="#datenschutzerklarung">Datenschutzerklärung</a>.</p>
          </div>
        </form>
      </div>
    </div>
  </section>'''


def page(p):
    pid = ROUTES[p["path"]]
    main, sub = title_parts(p)
    sub_html = f' <span class="sub">{esc(sub)}</span>' if sub else ""
    doc_title = TITLES.get(p["path"], p["docTitle"] if "|" in p["docTitle"] else p["docTitle"] + " | SELMA Zuhause")
    body = transform(p["path"], p["content"])
    contact = ("\n" + contact_block(pid)) if p["hasContactForm"] else ""
    return f'''
<!-- ======================= SEITE: {pid} ======================= -->
<div data-page id="{pid}" data-title="{esc(doc_title)}" hidden>
  <section class="page-head bg-mint" aria-labelledby="{pid}-title">
    <div class="wrap">
      <h1 id="{pid}-title" class="rv-split doc-title" tabindex="-1">{esc(main)}{sub_html}</h1>
    </div>
  </section>
  <section class="section doc" aria-labelledby="{pid}-title">
    <div class="wrap"><div class="prose doc-prose">
{body}
    </div></div>
  </section>{contact}
</div>'''


def load():
    return json.load(open(SRC))["pages"]


def render():
    return "\n".join(page(p) for p in load())


if __name__ == "__main__":
    for p in load():
        print("=====", p["path"], title_parts(p))
        print(transform(p["path"], p["content"])[:500])
