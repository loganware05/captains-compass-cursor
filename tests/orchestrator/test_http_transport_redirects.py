"""UrllibTransport must refuse redirects (no Authorization hop)."""

from __future__ import annotations

import threading
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

from orchestrator.integrations.transport import UrllibTransport


class _RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(302)
        self.send_header("Location", "http://127.0.0.1:9/stolen")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class UrllibTransportRedirectTests(unittest.TestCase):
    def test_refuses_redirect_and_does_not_soft_return_3xx(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _RedirectHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            transport = UrllibTransport()
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                transport.request(
                    "GET",
                    f"http://127.0.0.1:{port}/start",
                    headers={"Authorization": "Bearer secret-token-not-for-redirect"},
                    timeout=2.0,
                )
            self.assertEqual(ctx.exception.code, 302)
            self.assertIn("redirect refused", str(ctx.exception.reason).lower())
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
