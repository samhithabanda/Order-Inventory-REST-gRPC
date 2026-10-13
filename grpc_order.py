"""gRPC Order Service with a deadline on its Inventory call."""
import os
from concurrent import futures

import grpc
import inventory_pb2
import inventory_pb2_grpc

INVENTORY_ADDRESS = os.getenv("INVENTORY_ADDRESS", "127.0.0.1:50051")
DEADLINE_SECONDS = float(os.getenv("GRPC_DEADLINE_SECONDS", "1.5"))


class Orders(inventory_pb2_grpc.OrderServiceServicer):
    def PlaceOrder(self, request, context):
        if not request.item_id or request.quantity < 1:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "item_id and a positive quantity are required")
        channel = grpc.insecure_channel(INVENTORY_ADDRESS)
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        try:
            result = stub.CheckInventory(
                inventory_pb2.InventoryRequest(item_id=request.item_id, quantity=request.quantity),
                timeout=DEADLINE_SECONDS,
            )
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"Inventory call exceeded {DEADLINE_SECONDS:g}s deadline; Order Service is still running", flush=True)
            context.abort(error.code(), error.details() or "inventory request failed")
        finally:
            channel.close()
        if not result.available:
            context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, result.message)
        return inventory_pb2.OrderReply(message="order accepted", remaining=result.remaining)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_OrderServiceServicer_to_server(Orders(), server)
    port = int(os.getenv("ORDER_PORT", "50052"))
    server.add_insecure_port(f"127.0.0.1:{port}")
    server.start()
    print(f"gRPC Order Service listening on 127.0.0.1:{port}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
