from engine.contracts import MessagePacket
from engine.signal import SignalFactory
from engine.utils import generator
from engine.web_server import WebServer


class TestWebServer(WebServer):
    def __init__(self, timer, server_id):
        super().__init__(timer, server_id)
        self.message_box = None

    @WebServer.endpoint(message_type=str)
    @generator
    def process_str_message(self, _, sender_id, message):
        self.message_box = (sender_id, message)


def test_process_message(setup):
    SignalFactory.const_time = 1

    simulator_loop, timer, sender, _ = setup

    web_server = TestWebServer(timer=timer, server_id="test")

    simulator_loop.add_object(web_server)

    SignalFactory.create_signal(sender, web_server, MessagePacket(sender=sender, message="Hello!"))
    simulator_loop.process()
    simulator_loop.process()

    assert web_server.message_box == ("Sender", "Hello!")
