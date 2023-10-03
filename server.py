import socket
import threading
import json
import sys
import utils  # Local Import


class Server:
    def __init__(self, settings_config: str):
        self.settings_config = settings_config
        self.json_handler = utils.JsonHandler()
        self.settings = self.json_handler.load_json_file(self.settings_config)

        if self.settings == 1:
            # Failed to load
            print("Failed to load settings config. Check the directory.")
            sys.exit(1)

        # Server IP address
        self.IP = self.json_handler.get_element(self.settings, 'IP')
        # Server Port
        self.PORT = self.json_handler.get_element(self.settings, 'PORT')
        # Max # of connections allowed
        self.CONNECTION_LIMIT = self.json_handler.get_element(self.settings, 'CONNECTIONS')

        # List of currently connected clients
        self._connections = list()

        self._actions = {
            1: self.on_connection,    # When a client connects to the server
            2: self.is_connected,     # Ping to see if the client is still connected to the server
            3: self.receive_message,  # When the client sends a message to the server
        }
        self._server_socket = None

        self.start_server()

    def handle_payload(self, connection, payload, action: int):
        """
        Handle payloads from client
        :param payload: dict
        :param connection: connection that send request
        :param action:
        :return:
        """
        if action not in self._actions:
            payload = {
                "status": 400,
                "message": "Invalid Action Code"
            }
            payload = self.package_payload(payload)
            connection.send(payload)
            return

        self._actions[action](connection, payload)

    def on_connection(self, connection, payload):
        client_data = payload.get("client_data")
        self._connections.append((connection, client_data))

        response_payload = {
            "status": 200,
            "message": "Successfully Created Connection"
        }
        connection.send(self.package_payload(response_payload))

    def is_connected(self, connection, payload):
        try:
            connection.send(b'PING')
            data = connection.recv(1024)
            if len(data) == 0:
                # Dead
                self.remove_dead_connection(connection)
        except (socket.error, ConnectionError):
            # Dead 2.0 (real!!!)
            self.remove_dead_connection(connection)

    def remove_dead_connection(self, connection):
        for i, (conn, _) in enumerate(self._connections):
            if conn == connection:
                self._connections.pop(i)
                break

    def receive_message(self, connection, payload):
        message = payload.get("message")
        for conn, _ in self._connections:
            conn.send(self.package_payload({"status": 200, "message": message}))

    def accept_clients(self):
        while True:
            client_socket, client_address = self._server_socket.accept()

            # Start a new thread to handle the client
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            # Put your existing client handling logic here
            # Use self.handle_payload or other methods to interact with the client

            # Example: sending a welcome message
            welcome_message = {
                "status": 200,
                "message": "Welcome to the server!"
            }
            client_socket.send(self.package_payload(welcome_message))

            # Example: handling client requests
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                payload = json.loads(data.decode("utf-8"))
                action = payload.get("action", None)
                if action is not None:
                    self.handle_payload(client_socket, payload, action)

        except (socket.error, ConnectionError) as e:
            # Handle any exceptions that might occur during client interaction
            print(f"Exception: {e}")

        finally:
            # Close the client socket when done
            client_socket.close()

    @staticmethod
    def package_payload(payload):
        payload = json.dumps(payload).encode("utf-8")
        return payload

    def start_server(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self.IP, self.PORT))
        self._server_socket.listen(self.CONNECTION_LIMIT)

        print(f"Server started on {self.IP}:{self.PORT}")
        threading.Thread(target=self.accept_clients).start()


if __name__ == "__main__":
    server = Server("config1.json")
