# Order and Inventory: REST and gRPC

This project implements the same Order → Inventory interaction using REST/HTTP and gRPC.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## REST

### Run

Start Inventory Service:

```bash
python rest_inventory.py
```
![img.png](img.png)

Start Order Service in another terminal:

```bash
python rest_order.py
```
![img_1.png](img_1.png)

### Successful Request

```bash
curl -i -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d '{"item_id":"book","quantity":2}'
```

Response:

```text
HTTP/1.0 200 OK
{"status": "accepted", "message": "order accepted", "remaining": 10}
```

![img_2.png](img_2.png)

### REST Timeout

The Inventory Service was temporarily delayed for 4 seconds while the Order Service timeout was 1.5 seconds.

![img_3.png](img_3.png)

```text
HTTP/1.0 504 Gateway Timeout
{"error": "inventory request timed out"}
```
![img_5.png](img_5.png)


Order Service remained running:

```text
Inventory call timed out after 1.5s; Order Service is still running
```
![img_4.png](img_4.png)

## gRPC

### Run

Start Inventory Service:

```bash
python grpc_inventory.py
```
![img_9.png](img_9.png)

Start Order Service in another terminal:

```bash
python grpc_order.py
```
![img_8.png](img_8.png)

Run the client:

```bash
python grpc_client.py
```
![img_7.png](img_7.png)

### Successful Request

```text
gRPC order response: order accepted; remaining=10
```
![img_10.png](img_10.png)

### gRPC Deadline

The Inventory Service was temporarily delayed for 4 seconds while the gRPC deadline was 1.5 seconds.
![img_11.png](img_11.png)

```text
gRPC error: DEADLINE_EXCEEDED: Deadline Exceeded
```
![img_12.png](img_12.png)

Order Service remained running:

```text
Inventory call exceeded 1.5s deadline; Order Service is still running
```
![img_13.png](img_13.png)

## REST vs gRPC

REST uses HTTP and JSON with HTTP status codes, while gRPC uses a `.proto` contract and strongly typed messages. REST was simpler to test manually with curl. gRPC provided built-in status handling such as `DEADLINE_EXCEEDED`. Both implementations handled slow Inventory responses without stopping the Order Service.