from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

class ProxyHandler(BaseHTTPRequestHandler):
    TARGET = "https://jserralheiro.github.io"

    def do_GET(self):
        url = self.TARGET + self.path
        try:
            req = urllib.request.Request(url, headers={"Host": "jserralheiro.github.io"})
            with urllib.request.urlopen(req) as resp:
                body = resp.read()
                self.send_response(resp.status)
                for key, val in resp.headers.items():
                    if key.lower() not in ("transfer-encoding", "content-encoding"):
                        self.send_header(key, val)
                self.end_headers()
                self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, *args):
        pass

print("Proxy a correr em http://localhost:8000/burndownchart/")
HTTPServer(("localhost", 8000), ProxyHandler).serve_forever()
