import socket
import threading
import ipaddress
import sys
import json
import utils


class Client:
    def __init__(self):
        self.username = None
        self.json_handler = utils.JsonHandler()
        self.tcp_socket = None
        self.connected_ip = None
        self.connected_port = None
        self.start()

    def start(self):
        self.username = input("Username: ")
        self.connected_ip = input("Server IP: ")
        self.connected_port = input("Server Port: ")

        try:
            self.connected_port = int(self.connected_port)
        except TypeError:
            print("Invalid Port. Port can only be a number. Example: 8080")
            sys.exit(1)

        try:
            # Verify IP
            ipaddress.ip_address(self.connected_ip)
        except ValueError:
            print("Invalid IP. Please enter a valid ip. Example: 127.0.0.1")
            sys.exit(1)

        self.tcp_socket = socket.create_connection((self.connected_ip, self.connected_port))
        # Send initial packet to server to announce client
        payload = self.package_payload({"action": 1, "client_data": {"username": self.username}})   # 1: on_connect
        self.tcp_socket.send(payload)
        threading.Thread(target=self.handle_client).start()

    def handle_client(self):
        try:
            while True:
                payload = {
                    "action": 3,  # 3: receive_message
                    "username": self.username
                }
                message = input(f"[{self.username}]  ")
                payload.update({"message": message})
                payload = self.package_payload(payload)
                self.tcp_socket.send(payload)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            self.tcp_socket.close()

    @staticmethod
    def package_payload(payload):
        payload = json.dumps(payload).encode("utf-8")
        return payload


if __name__ == "__main__":
    Client()
