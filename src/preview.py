"""Local preview of the built site, with the same clean URLs as Netlify (/leistungen -> leistungen.html).

Run:  python3 src/preview.py        then open http://localhost:8000
Stop: Ctrl+C
Forms don't send anything locally; test them on the live site.
"""
import http.server, os, pathlib, sys, webbrowser

ROOT = str(pathlib.Path(__file__).resolve().parent.parent / "public")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass

    def send_head(self):
        p = self.path.split("?")[0].split("#")[0]
        fs = os.path.join(ROOT, p.lstrip("/"))
        if p != "/" and not os.path.isfile(fs):
            if os.path.isfile(fs.rstrip("/") + ".html"):
                self.path = p.rstrip("/") + ".html"
            else:
                body = open(os.path.join(ROOT, "404.html"), "rb").read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return None
        return super().send_head()

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Vorschau: Formulare werden lokal nicht gesendet.".encode())


if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print(f"Vorschau läuft: {url}  (beenden mit Ctrl+C)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
