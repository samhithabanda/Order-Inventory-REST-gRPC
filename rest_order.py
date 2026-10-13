"""REST Order Service. Each order call has a short timeout to Inventory."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://127.0.0.1:8001/inventory/check")
TIMEOUT_SECONDS = float(os.getenv("REST_TIMEOUT_SECONDS", "1.5"))


class OrderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/orders":
            return self.send_json(404, {"error": "endpoint not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            item_id, quantity = data.get("item_id"), data.get("quantity")
            if not isinstance(item_id, str) or not item_id or type(quantity) is not int or quantity < 1:
                return self.send_json(400, {"error": "item_id must be text and quantity must be a positive integer"})
        except (ValueError, json.JSONDecodeError):
            return self.send_json(400, {"error": "request body must be valid JSON"})

        request = Request(INVENTORY_URL, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                inventory = json.loads(response.read())
                return self.send_json(200, {"status": "accepted", "message": "order accepted", "remaining": inventory["remaining"]})
        except HTTPError as error:
            if error.code == 409:
                return self.send_json(409, {"status": "rejected", "message": "item or requested quantity unavailable"})
            return self.send_json(502, {"error": f"inventory returned HTTP {error.code}"})
        except (TimeoutError, URLError) as error:
            reason = getattr(error, "reason", error)
            if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
                print(f"Inventory call timed out after {TIMEOUT_SECONDS:g}s; Order Service is still running", flush=True)
                return self.send_json(504, {"error": "inventory request timed out"})
            return self.send_json(503, {"error": f"inventory service unavailable: {reason}"})

    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[REST order] {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("ORDER_PORT", "8000"))
    print(f"REST Order Service listening on http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), OrderHandler).serve_forever()
