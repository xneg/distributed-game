# distributed-game
Python simulator of distributed system

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/xneg/distributed-game/main?labpath=%2Fsrc%2Fsandbox_notebook.ipynb)

# Web-version
https://xneg.github.io/distributed-game/

# How to
You need to implement your own algorithm inheriting [class Node](https://github.com/xneg/distributed-game/blob/main/src/engine/node.py).
There are two abstract methods processing read and write requests:
```python
@WebServer.endpoint(message_type=ClientReadRequest)
@abc.abstractmethod
def process_read_request(self, request):
    pass

@WebServer.endpoint(message_type=ClientWriteRequest)
@abc.abstractmethod
def process_write_request(self, request):
    pass
```
You can see examples [here](https://github.com/xneg/distributed-game/tree/main/src/algorithms).

# Engine
![diagram_2](https://user-images.githubusercontent.com/5748886/180388311-e00628d9-0408-4e77-8689-0edc327f0975.jpg)
This diagram shows communication between two `WebServers`.
WebServer contains three main methods:

* send_message(receiver_id, message)

* add_message(message)

* process()

The `send_message(receiver_id, message)` method creates a `Signal` (1) object that contains the "message packet" itself and the ID of the receiving server.
In fact, `Signal` after a certain number of steps will call the `add_message(message)` (2) callback already on the recipient side.

The `add_message(message)` method sends a message to one of the server endpoints (3) with the help of typing, decorators and a bit of "pythonic" magic.
Web servers use signals instead of calling each other's methods directly to mimic the asynchronous nature of network.
The signal can have an arbitrary execution time, moreover, it is possible to make the signal "lost" by simulating network breaks.

![diagram_1](https://user-images.githubusercontent.com/5748886/180388323-8a26f1a4-e4e1-41fe-85a9-c982fe55d46b.jpg)
This diagram shows implemented system. The client only knows about the gateway.
Gateway acts as a proxy between the client and the nodes of the system, it knows about anything. The gateway forwards client requests to nodes via round-robin (the first request comes to the first node, the second - to the second).
Then the nodes exchange messages with each other and send the response back to the gateway, which returns it to the client.
All the arrows on the diagram are, in fact, signals.