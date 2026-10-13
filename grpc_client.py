"""Small command-line client for the gRPC Order Service."""
import sys

import grpc
import inventory_pb2
import inventory_pb2_grpc

item_id = sys.argv[1] if len(sys.argv) > 1 else "book"
quantity = int(sys.argv[2]) if len(sys.argv) > 2 else 2
with grpc.insecure_channel("127.0.0.1:50052") as channel:
    stub = inventory_pb2_grpc.OrderServiceStub(channel)
    try:
        reply = stub.PlaceOrder(inventory_pb2.OrderRequest(item_id=item_id, quantity=quantity), timeout=3)
        print(f"gRPC order response: {reply.message}; remaining={reply.remaining}")
    except grpc.RpcError as error:
        print(f"gRPC error: {error.code().name}: {error.details()}")
