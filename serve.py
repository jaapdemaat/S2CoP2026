#!/usr/bin/env python3
import http.server
import os
os.chdir("/Users/jdemaat/Desktop/CRL2026")
handler = http.server.SimpleHTTPRequestHandler
port = int(os.environ.get("PORT", 8080))
httpd = http.server.HTTPServer(("", port), handler)
print(f"Serving on http://localhost:{port}")
httpd.serve_forever()
