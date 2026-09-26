import re, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import blog
import pages
B = pathlib.Path(__file__).parent
OUT = B.parent / "preview" / "index.html"  # single-file preview (not deployed)
LIVE = "https://www.selmazuhause.de"

ICONS = {
 "house": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
 "award": '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
 "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
 "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
 "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
 "arrowl": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
 "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
 "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
 "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "instagram": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
 "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
 "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
 "x": '<path d="M18 6 6 18M6 6l12 12"/>',
 "play": '<path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.5-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5z"/>',
 "pause": '<rect x="6" y="4" width="4.5" height="16" rx="1.2"/><rect x="13.5" y="4" width="4.5" height="16" rx="1.2"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "plus": '<path d="M5 12h14M12 5v14"/>',
 "user": '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
 "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 "alert": '<circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>',
}
sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()) + "</svg>"

def icon(m):
    return f'<svg class="icon" aria-hidden="true"><use href="#i-{m.group(1)}"/></svg>'

def render_body():
    faq = (B / "faq.html").read_text()
    body = (B / "body.html").read_text()
    body = body.replace("{{BLOG}}", blog.render() + "\n" + pages.render())
    body = body.replace("{{FAQ_START}}", faq.replace("{{FAQ_ID}}", "faq-start").replace("{{FAQ_CONTACT}}", "#kontakt").replace("{{FAQ_BG}}", ""))
    body = body.replace("{{FAQ_LEIST}}", faq.replace("{{FAQ_ID}}", "faq").replace("{{FAQ_CONTACT}}", "#kontakt-form").replace("{{FAQ_BG}}", ""))
    body = re.sub(r"\{\{i:([a-z]+)\}\}", icon, body)
    body = body.replace("{{ext}}", '<span class="sr-only"> (öffnet in neuem Tab)</span>').replace("{{LIVE}}", LIVE)
    assert "{{" not in body, re.findall(r"\{\{[^}]+\}\}", body)
    return body


head = """<title>SELMA Zuhause Relaunch</title>
<meta name="description" content="Spezialisierte Ergotherapie für Menschen mit Parkinson zu Hause in Berlin: für mehr Sicherheit, Beweglichkeit und Lebensqualität im Alltag.">
<script>document.documentElement.lang="de";</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;700;800&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:wght@600&display=swap">
"""
if __name__ == "__main__":
    body = render_body()
    css = (B / "style.css").read_text()
    js = (B / "app.js").read_text()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(head + "<style>\n" + css + "\n</style>\n" + sprite + "\n" + body + "\n<script>\n" + js + "\n</script>\n")
    print("wrote", OUT, OUT.stat().st_size, "bytes")
