"""REST Inventory Service. Set INVENTORY_DELAY_SECONDS to simulate slowness."""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STOCK = {"book": 10, "pen": 25, "notebook": 8}


class InventoryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/inventory/check":
            return self.send_json(404, {"error": "endpoint not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            item_id, quantity = data.get("item_id"), data.get("quantity")
            if not isinstance(item_id, str) or not item_id or type(quantity) is not int or quantity < 1:
                return self.send_json(400, {"error": "item_id must be text and quantity must be a positive integer"})
        except (ValueError, json.JSONDecodeError):
            return self.send_json(400, {"error": "request body must be valid JSON"})

        delay = float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))
        if delay > 0:
            print(f"Simulating slow inventory response: sleeping {delay:g}s", flush=True)
            time.sleep(delay)

        remaining = STOCK.get(item_id, 0)
        available = remaining >= quantity
        return self.send_json(200 if available else 409, {
            "available": available,
            "item_id": item_id,
            "requested": quantity,
            "remaining": remaining,
            "message": "inventory available" if available else "item or requested quantity unavailable",
        })

    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[REST inventory] {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("INVENTORY_PORT", "8001"))
    print(f"REST Inventory Service listening on http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), InventoryHandler).serve_forever()
