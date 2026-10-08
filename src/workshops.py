"""Kostenlose Online-Workshops: Themenseiten mit Terminbuchung, Karten für /workshops und Themenwahl der Warteliste.

Termine und Texte stehen in content/workshops.json. Dieses Modul baut daraus HTML, das build.py in body.html einsetzt:
  {{WS_CARDS}}  Karten auf /workshops
  {{WS_TOPICS}} Themenwahl im Wartelisten-Formular
  {{WS_PAGES}}  je Thema eine Seite /workshop-<slug>
"""
import datetime, html, json, pathlib

B = pathlib.Path(__file__).parent
DATA = json.load(open(B / "content" / "workshops.json", encoding="utf-8"))
DAUER = DATA["dauer_min"]
SITE = "https://www.selmazuhause.de"
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
TAGE_K = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]


def e(s):
    return html.escape(str(s), quote=True)


def _last_sunday(year, month):
    d = (datetime.date(year + (month == 12), month % 12 + 1, 1) - datetime.timedelta(days=1))
    while d.weekday() != 6:
        d -= datetime.timedelta(days=1)
    return d


def _offset(dt):
    """UTC-Versatz für Berlin (Sommerzeit: letzter Sonntag im März bis letzter Sonntag im Oktober)."""
    begin = datetime.datetime.combine(_last_sunday(dt.year, 3), datetime.time(2))
    end = datetime.datetime.combine(_last_sunday(dt.year, 10), datetime.time(3))
    return "+02:00" if begin <= dt < end else "+01:00"


def _uhr(dt):
    return f"{dt.hour}:{dt.minute:02d}"


def slots(w):
    out = []
    for i, t in enumerate(w["termine"], 1):
        s = datetime.datetime.fromisoformat(t["start"])
        en = s + datetime.timedelta(minutes=DAUER)
        datum_lang = f"{TAGE[s.weekday()]}, {s.day}. {MONATE[s.month - 1]} {s.year}"
        hint = "Vormittags" if s.hour < 12 else ("Abends, auch für berufstätige Angehörige" if s.hour >= 17 else "Nachmittags")
        out.append({
            "i": i,
            "start": s.isoformat(timespec="seconds") + _offset(s),
            "end": en.isoformat(timespec="seconds") + _offset(en),
            "tag": f"{TAGE_K[s.weekday()]}, {s.day}. {MONATE[s.month - 1]}",
            "zeit": f"{_uhr(s)} bis {_uhr(en)} Uhr",
            "kurz": f"{TAGE_K[s.weekday()]}, {s.day}. {MONATE[s.month - 1]}, {_uhr(s)} Uhr",
            "wert": f"{datum_lang}, {_uhr(s)} Uhr",
            "text": f"{datum_lang}, {_uhr(s)} bis {_uhr(en)} Uhr",
            "hint": hint,
            "voll": bool(t.get("voll")),
        })
    return out


def _ld(w, page_url):
    events = []
    for sl in slots(w):
        events.append({
            "@context": "https://schema.org",
            "@type": "Event",
            "name": f"{w['titel']}: kostenloser Online-Workshop",
            "description": w["kurz"],
            "startDate": sl["start"],
            "endDate": sl["end"],
            "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "VirtualLocation", "url": page_url},
            "image": [SITE + "/" + w["bild"]],
            "isAccessibleForFree": True,
            "inLanguage": "de",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR", "url": page_url,
                       "availability": "https://schema.org/SoldOut" if sl["voll"] else "https://schema.org/InStock"},
            "organizer": {"@type": "Organization", "name": "SELMA Zuhause", "url": SITE},
            "performer": {"@type": "Person", "name": "Kathleen Olstedt"},
        })
    return '<script type="application/ld+json">' + json.dumps(events, ensure_ascii=False).replace("</", "<\\/") + "</script>"


UTM = ('<input type="hidden" name="utm_source" value=""><input type="hidden" name="utm_medium" value="">'
       '<input type="hidden" name="utm_campaign" value="">')


def render_cards():
    items = []
    for n, w in enumerate(DATA["workshops"]):
        dates = "".join(f'<li data-end="{sl["end"]}">{{{{i:calendar}}}}<span>{e(sl["kurz"])}</span></li>' for sl in slots(w) if not sl["voll"])
        items.append(f"""
        <li class="ansatz-card ws-card rv" style="--d:{n * 120}ms">
          <div class="media rv-img" style="--d:{n * 120}ms"><img src="{w['bild']}" width="500" height="500" alt="" loading="lazy"></div>
          <div>
            <h3>{w['karte_titel_html']}</h3>
            <p>{e(w['kurz'])}</p>
            <ul class="ws-card-dates" aria-label="Termine">{dates}</ul>
            <p class="ws-cta"><a class="btn btn-primary" href="#workshop-{w['slug']}">Termin wählen<span class="btn-ic">{{{{i:arrow}}}}</span></a></p>
          </div>
        </li>""")
    return '<ul class="cards-3 ws-cards">' + "".join(items) + "\n      </ul>"


def render_topics():
    opts = [(w["titel"], w["titel"]) for w in DATA["workshops"]] + [("Alle Themen", "Alle Themen")]
    return "".join(
        f'<label class="slot"><input type="radio" name="workshop" id="wl-t{i}" value="{e(v)}" required data-label="Thema" '
        f'data-msg="Bitte wählen Sie ein Thema."><span class="slot-body"><strong>{e(t)}</strong></span></label>'
        for i, (v, t) in enumerate(opts, 1))


FAQ = [
    ("Was brauche ich zur Teilnahme?",
     "Ein Smartphone, Tablet oder Computer mit Internet. Den Zugangslink schicken wir Ihnen per E-Mail, ein Klick genügt. Eine Kamera ist hilfreich, aber kein Muss."),
    ("Ich bin unsicher mit der Technik. Was kann ich tun?",
     'Rufen Sie uns gern an: <a href="tel:+493037580867"><span class="num">030 3758 0867</span></a>. Wir helfen Ihnen vorab, damit am Workshop-Tag alles klappt.'),
    ("Dürfen Angehörige teilnehmen?",
     "Ja, sehr gern. Sie können gemeinsam vor einem Gerät sitzen oder sich jeweils selbst anmelden."),
    ("Muss ich bei den Übungen mitmachen?",
     "Nein. Sie können zuschauen oder im Sitzen mitmachen, ganz in Ihrem Tempo."),
    ("Was kostet der Workshop?",
     "Nichts. Der Workshop ist kostenlos und unverbindlich."),
]


def render_page(w):
    s = w["slug"]
    pid = f"workshop-{s}"
    page_url = f"{SITE}/{pid}"
    sl = slots(w)
    dates = "".join(f'<span class="ws-d" data-end="{x["end"]}">{e(x["kurz"])}</span>' for x in sl if not x["voll"])
    radios = []
    for x in sl:
        dis = " disabled" if x["voll"] else ""
        hint = "Ausgebucht" if x["voll"] else x["hint"]
        radios.append(
            f'<label class="slot{" is-full" if x["voll"] else ""}"><input type="radio" name="termin" id="t-{s}-{x["i"]}" value="{e(x["wert"])}" required{dis} '
            f'data-label="Termin" data-msg="Bitte wählen Sie einen Termin." data-start="{x["start"]}" data-end="{x["end"]}" data-text="{e(x["text"])}">'
            f'<span class="slot-body"><strong>{e(x["tag"])}</strong><span>{e(x["zeit"])}</span><small>{e(hint)}</small></span></label>')
    checks = "".join(f"<li>{{{{i:check}}}}<span>{e(m)}</span></li>" for m in w["mitnehmen"])
    faq = "".join(
        f'<details class="faq-item"><summary>{e(q)}<span class="plus" aria-hidden="true">{{{{i:plus}}}}</span></summary>'
        f'<div class="faq-body"><p>{a}</p></div></details>' for q, a in FAQ)
    others = "".join(
        f'<li><a href="#workshop-{o["slug"]}"><img src="{o["bild"]}" width="72" height="72" alt="" loading="lazy"><span>{e(o["titel"])}</span>{{{{i:arrow}}}}</a></li>'
        for o in DATA["workshops"] if o is not w)
    return f"""
<!-- ======================= WORKSHOP: {e(w['titel'])} (aus src/workshops.py, Termine in content/workshops.json) ======================= -->
<div data-page id="{pid}" data-title="{e(w['titel'])}: kostenloser Online-Workshop · SELMA Zuhause" data-landing data-section="workshops" hidden>
  {_ld(w, page_url)}
  <section class="section ws-hero bg-mint" aria-labelledby="{pid}-title">
    <div class="wrap ws-hero-grid">
      <div class="ws-hero-a">
        <p class="eyebrow">Kostenloser Online-Workshop</p>
        <h1 id="{pid}-title" tabindex="-1">{e(w['h1'])} <span class="accent">{e(w['h1_akzent'])}</span></h1>
        <ul class="ws-facts">
          <li>{{{{i:calendar}}}}<span class="ws-dates">{dates}</span></li>
          <li>{{{{i:clock}}}}<span>{DAUER} Minuten, live per Video, kostenlos</span></li>
          <li>{{{{i:user}}}}<span>Für Menschen mit Parkinson und Angehörige</span></li>
        </ul>
      </div>
      <div class="form-card ws-book" id="anmeldung-{s}">
        <h2 class="ws-book-title">Kostenlos Platz sichern</h2>
        <form id="form-ws-{s}" novalidate data-booking data-done="Vielen Dank! Ihr Platz ist reserviert." data-after="ws-after-{s}">
          <div class="form-summary" hidden tabindex="-1"></div>
          <input type="hidden" name="workshop" value="{e(w['titel'])}">{UTM}
          <fieldset class="field ws-slots">
            <legend>Wählen Sie Ihren Termin</legend>
            {"".join(radios)}
          </fieldset>
          <div class="form-grid">
            <div class="field">
              <label for="ws-{s}-vorname">Vorname</label>
              <input id="ws-{s}-vorname" name="vorname" type="text" autocomplete="given-name" required data-msg="Bitte geben Sie Ihren Vornamen an.">
            </div>
            <div class="field">
              <label for="ws-{s}-nachname">Nachname</label>
              <input id="ws-{s}-nachname" name="nachname" type="text" autocomplete="family-name" required data-msg="Bitte geben Sie Ihren Nachnamen an.">
            </div>
            <div class="field full">
              <label for="ws-{s}-email">E-Mail</label>
              <input id="ws-{s}-email" name="email" type="email" autocomplete="email" inputmode="email" required data-msg="Bitte geben Sie Ihre E-Mail-Adresse an, z. B. name@beispiel.de.">
            </div>
          </div>
          <p class="fineprint ws-privacy">Wir nutzen Ihre Angaben, um Ihnen die Bestätigung und den Zugangslink zu diesem Workshop zu schicken. Ihre Daten geben wir nicht weiter. Mehr in der <a href="#datenschutzerklarung">Datenschutzerklärung</a>.</p>
          <div class="form-foot">
            <button class="btn btn-primary" type="submit">Meinen Platz sichern<span class="btn-ic">{{{{i:arrow}}}}</span></button>
          </div>
          <p class="ws-phone">Lieber telefonisch anmelden? <a href="tel:+493037580867"><span class="num">030 3758 0867</span></a></p>
        </form>
        <div class="ws-after" id="ws-after-{s}" hidden>
          <p class="ws-after-termin" data-fill="termin"></p>
          <p>Sie erhalten von uns eine Bestätigung mit dem Zugangslink per E-Mail.</p>
          <div class="btn-row">
            <button class="btn btn-ghost" type="button" data-ics>In Kalender eintragen<span class="btn-ic">{{{{i:calendar}}}}</span></button>
            <a data-gcal href="https://calendar.google.com/" target="_blank" rel="noopener">In Google Kalender eintragen{{{{ext}}}}</a>
          </div>
          <div class="ws-after-block">
            <p><strong>Möchten Sie auch über weitere Workshops informiert werden?</strong> Dann melden Sie sich gern für unseren Newsletter an. Sie können ihn jederzeit abbestellen.</p>
            <button class="btn btn-ghost rm-open-popup" type="button" aria-haspopup="dialog">Newsletter erhalten<span class="btn-ic">{{{{i:arrow}}}}</span></button>
          </div>
          <div class="ws-after-block">
            <p><strong>Kennen Sie jemanden, für den das hilfreich ist?</strong></p>
            <button class="btn btn-ghost" type="button" data-share>Workshop weitersagen<span class="btn-ic">{{{{i:arrow}}}}</span></button>
          </div>
        </div>
        <div class="ws-noslots" hidden>
          <p>Die Termine dieses Workshops sind vorbei. Neue Termine folgen bald.</p>
          <a class="btn btn-primary" href="#warteliste">Bei neuen Terminen informieren<span class="btn-ic">{{{{i:arrow}}}}</span></a>
        </div>
      </div>
      <div class="ws-hero-b">
        <h2 class="ws-sub">Das nehmen Sie mit</h2>
        <ul class="ws-check">{checks}</ul>
        <div class="ws-host"><img src="img/portrait.webp" width="64" height="64" alt="" loading="lazy"><p><strong>Mit Kathleen Olstedt</strong><span>Ergotherapeutin, spezialisiert auf Parkinson</span></p></div>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="{pid}-was">
    <div class="wrap ws-split">
      <div>
        <p class="eyebrow rv">Das erwartet Sie</p>
        <h2 id="{pid}-was" class="rv-split">{e(w['titel'])}</h2>
        <p class="rv">{e(w['erwartet'])}</p>
        <p class="rv">Der Workshop ist für Menschen mit Parkinson und ihre Angehörigen. Vorkenntnisse brauchen Sie keine. Am Ende ist Zeit für Ihre Fragen.</p>
      </div>
      <div class="media rv-img"><img src="{w['bild']}" width="500" height="500" alt="" loading="lazy"></div>
    </div>
  </section>

  <section class="section founder bg-mist" aria-labelledby="{pid}-leitung">
    <div class="wrap">
      <div class="portrait">
        <div class="pblock" data-par="0.1" aria-hidden="true"></div>
        <div class="pimg rv-img"><img data-par="0.05" src="img/portrait.webp" width="760" height="869" alt="Porträt von Kathleen Olstedt" loading="lazy"></div>
      </div>
      <div>
        <p class="eyebrow rv">Ihre Workshop-Leiterin</p>
        <h2 id="{pid}-leitung" class="rv-split">Kathleen Olstedt</h2>
        <p class="role rv" style="--d:120ms">Leiterin SELMA Zuhause · staatl. anerkannte Ergotherapeutin</p>
        <div class="bio rv" style="--d:200ms">
          <p>SELMA Zuhause ist auf <strong>mobile Ergotherapie bei Parkinson</strong> spezialisiert. Wir begleiten Menschen mit Parkinson direkt in ihrem häuslichen Umfeld, und die Erfahrungen aus dieser täglichen Arbeit fließen in die Workshops ein.</p>
          <p>Zertifiziert in <strong>LSVT BIG®</strong>, <strong>PWR!Moves®</strong>, Wohnraumanpassung (<strong>CAPS</strong>) und Sturzprävention.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section faq" aria-labelledby="{pid}-faq-title">
    <div class="wrap">
      <div class="faq-aside">
        <h2 id="{pid}-faq-title" class="rv-split">Fragen und Antworten</h2>
        <p class="rv" style="--d:120ms">Sie haben eine andere Frage? Rufen Sie uns an: <a href="tel:+493037580867"><span class="num">030 3758 0867</span></a>.</p>
      </div>
      <div class="faq-list">{faq}</div>
    </div>
  </section>

  <section class="section ws-end bg-peach" aria-label="Anmelden und weitere Workshops">
    <div class="wrap">
      <div class="cta-band">
        <p>Live dabei sein, Fragen stellen, Strategien für den Alltag mitnehmen.</p>
        <a class="btn btn-primary" href="#anmeldung-{s}">Meinen Platz sichern<span class="btn-ic">{{{{i:arrow}}}}</span></a>
      </div>
      <div class="ws-more">
        <h2>Weitere kostenlose Workshops</h2>
        <ul>{others}</ul>
      </div>
    </div>
  </section>
</div>
"""


def render_pages():
    return "\n".join(render_page(w) for w in DATA["workshops"])


if __name__ == "__main__":
    for w in DATA["workshops"]:
        for x in slots(w):
            print(w["slug"], x["start"], x["end"], x["text"], x["hint"])
