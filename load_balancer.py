from client import ClientRequest, ClientResponse, RequestType
from constant_object import ConstantObject
from link import Link
from timer import Timer


class LoadBalancer(ConstantObject):
    def __init__(self):
        self._requests = []
        self._responses = []
        self._timer = Timer()
        print(f"LoadBalancer created at {self._timer.current_epoch()}")

    def add_message(self, message):
        if isinstance(message, ClientRequest):
            self._requests.append(message)
        elif isinstance(message, ClientResponse):
            self._responses.append(message)

        print(f"LoadBalancer accepted {message} at {self._timer.current_epoch()}")

    def process(self):
        for request in self._requests:
            self._process_request(request)

        self._requests = []

        for response in self._responses:
            Link(response.client, response)
            # response.client.set_response(response)
        self._responses = []

    def _process_request(self, request):
        Link(self, ClientResponse(request.client, type=RequestType.Read, value=5))

