import threading
import json
import socket
import json
import code


class Server:
    def __init__(self, config_file: str):
        self.config_file = config_file
        # AF_INET, Address Family. Specifies the addresses that the socket will comminucate with.
        # AF_INET is typically Internet Protocol 4, IPv4.
        # Also, There's IPv6, AF_INET6
        # See https://stackoverflow.com/questions/1593946/what-is-af-inet-and-why-do-i-need-it#1594039

        # SOCK_STREAM means that it is a TCP socket. (Transmission Control Protocol)
        # SOCK_DGRAM means that it is a UDP socket.  (User Datagram Protocol)

        # A datagram is a basic transfer unit associated with a packet-switched network.
        # Datagrams are typically structured in header and payload sections.
        # Datagrams provide a connectionless communication service across a packet-switched network.
        # The delivery, arrival time, and order of arrival of datagrams need not be guaranteed by the network.
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.settings = self.load_config()

        self.server_address = (self.settings["IP"], self.settings["PORT"])
        self.tcp_socket.bind(self.server_address)
        self.tcp_socket.listen(self.settings["CONNECTIONS"])
        self.message_queue = []

        self.open_connections()

    def load_config(self):
        with open(self.config_file, "r") as config:
            config = json.load(config)

        return config

    def process_client(self, connection, client):
        # This method is used for handling a client in a separate thread
        try:
            self.handle_client(connection, client)
        except Exception as e:
            print(f"Error handling client: {e}")

    def handle_client(self, connection, client):
        try:
            while True:
                data = connection.recv(1024)
                data = data.decode("utf-8")
                data = (client[0], data)
                self.message_queue.append(data)
                self.handle_queue()
                if not data:
                    connection.close()
        finally:
            connection.close()

    def handle_queue(self):
        oldest_message = self.message_queue.pop(0)
        payload = oldest_message[1]
        payload = json.loads(payload)
        username = payload["username"]
        message = payload["message"]
        message = f"{username} :: {message}"

    def open_connections(self):
        c = code.Transcriber().generate_code(self.server_address[0], self.server_address[1])
        print(f"Share this code with your friends: {c}")
        threads = []
        while True:
            connection, client = self.tcp_socket.accept()
            t = threading.Thread(target=self.process_client, args=(connection, client))
            t.start()
            threads.append(t)


if __name__ == "__main__":
    test_server = Server("config1.json")
