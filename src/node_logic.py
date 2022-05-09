from contracts import RequestType, ClientResponse


class NodeLogic:
    def __init__(self, node):
        self._send_response = node.send_response
        self._send_message = node.send_message
        self._requests = node.requests
        self._messages = node.messages
        self._storage = node.storage
        self._is_leader = node.is_leader

    def process(self):
        while self._requests:
            request = self._requests.pop(0)
            self._process_request(request)

        self._messages = []

    def _process_request(self, request):
        if request.type == RequestType.Read:
            value = self._storage.get("x", None)
            self._send_response(ClientResponse(type=RequestType.Read, value=value or "N", id=request.id))
        else:
            self._storage["x"] = request.value
            self._send_response(ClientResponse(type=RequestType.Write, value="SUCCESS", id=request.id))
