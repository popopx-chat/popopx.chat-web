#!/usr/bin/env python3
"""HMAC-checked deploy receiver. Runs as the unprivileged `webdeploy` user and may
only start popopx-sync.service, which is whitelisted in sudoers:
  webdeploy ALL=(root) NOPASSWD: /usr/bin/systemctl start popopx-sync.service
Secret: /etc/popopx/deploy_secret (0600, root:webdeploy) - same value as the
GitHub secret DEPLOY_WEBHOOK_SECRET. Never log the body before verifying it.
"""
import hmac, hashlib, json, os, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = open("/etc/popopx/deploy_secret", "rb").read().strip()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(n)
        if n > 65536 or len(body) != n:
            self.send_response(413); self.end_headers(); return
        got = self.headers.get("x-popopx-signature", "")
        want = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(got, want):
            self.send_response(403); self.end_headers(); self.wfile.write(b"bad signature\n"); return
        try:
            sha = json.loads(body.decode())["sha"][:12]
        except Exception:
            sha = "unknown"
        rc = subprocess.call(["sudo", "/usr/bin/systemctl", "start", "popopx-sync.service"])
        self.send_response(204 if rc == 0 else 500)
        self.end_headers()
        print("queued sync for %s rc=%d" % (sha, rc), flush=True)

HTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
