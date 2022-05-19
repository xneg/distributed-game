from engine.signal import SignalFactory
from engine.web_server import WebServer


class TestWebServerA(WebServer):
    def __init__(self, server_id, timer):
        super().__init__(server_id, timer)
        self.mailbox = None

    @WebServer.endpoint(message_type=str)
    def process_str_message(self, message):
        self.mailbox = message


class TestWebServerB(WebServer):
    def __init__(self, server_id, timer):
        super().__init__(server_id, timer)
        self.mailbox = None

    @WebServer.endpoint(message_type=str)
    def process_str_message(self, message):
        self.mailbox = message


def test_endpoints_registration(setup):
    SignalFactory.const_time = 1

    simulator_loop, timer, sender, _ = setup
    serverA = TestWebServerA(server_id="A", timer=timer)
    serverB = TestWebServerB(server_id="B", timer=timer)

    simulator_loop.add_object(serverA)
    simulator_loop.add_object(serverB)

    SignalFactory.create_signal(sender=sender, recipient=serverA, message="Hello A!")
    SignalFactory.create_signal(sender=sender, recipient=serverB, message="Hello B!")

    simulator_loop.process()
    simulator_loop.process()

    assert serverA.mailbox == "Hello A!"
    assert serverB.mailbox == "Hello B!"
