"""gRPC Inventory Service. Set INVENTORY_DELAY_SECONDS to simulate slowness."""
import os
import time
from concurrent import futures

import grpc
import inventory_pb2
import inventory_pb2_grpc

STOCK = {"book": 10, "pen": 25, "notebook": 8}


class Inventory(inventory_pb2_grpc.InventoryServiceServicer):
    def CheckInventory(self, request, context):
        delay = float(os.getenv("INVENTORY_DELAY_SECONDS", "0"))
        if delay > 0:
            print(f"Simulating slow gRPC inventory response: sleeping {delay:g}s", flush=True)
            time.sleep(delay)
        remaining = STOCK.get(request.item_id, 0)
        available = request.quantity > 0 and remaining >= request.quantity
        return inventory_pb2.InventoryReply(
            available=available,
            remaining=remaining,
            message="inventory available" if available else "item or requested quantity unavailable",
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(Inventory(), server)
    port = int(os.getenv("INVENTORY_PORT", "50051"))
    server.add_insecure_port(f"127.0.0.1:{port}")
    server.start()
    print(f"gRPC Inventory Service listening on 127.0.0.1:{port}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
