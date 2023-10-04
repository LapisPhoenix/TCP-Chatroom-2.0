import socket
import random
import threading
import ipaddress
import sys
import json
import utils


class Client:
    def __init__(self):
        self.username = None
        self.id = self.generate_id()
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
        # Send initial packet to the server to announce the client
        payload = self.package_payload({"action": 1, "client_data": {"username": self.username}})
        self.tcp_socket.send(payload)

        # Create separate threads for writing and printing messages
        writing_thread = threading.Thread(target=self.write_messages)
        printing_thread = threading.Thread(target=self.print_messages)

        # Start both threads
        writing_thread.start()
        printing_thread.start()

        # Wait for both threads to finish
        writing_thread.join()
        printing_thread.join()

    def write_messages(self):
        try:
            while True:
                payload = {
                    "action": 3,  # 3: receive_message
                    "username": self.username,
                    "id": self.id
                }
                message = input(f"{self.username}: ")
                payload.update({"message": message})
                payload = self.package_payload(payload)
                self.tcp_socket.send(payload)
        except KeyboardInterrupt:
            print("\nGoodbye!")

    def print_messages(self):
        try:
            while True:
                data = self.tcp_socket.recv(1024)
                if not data:
                    break  # Exit the loop if no data is received, indicating that the connection is closed

                payload_str = data.decode("utf-8")
                if payload_str.strip():  # Check if the received data is not empty or whitespace
                    payload = json.loads(payload_str)
                    sender_username = payload.get("username", "")
                    received_message = payload.get("message", "")
                    print(f"{sender_username}: {received_message}")
        except (socket.error, ConnectionError) as e:
            print(f"Exception: {e}")
        finally:
            # Close the client socket when done
            self.tcp_socket.close()

    @staticmethod
    def package_payload(payload):
        payload = json.dumps(payload).encode("utf-8")
        return payload

    @staticmethod
    def generate_id():
        return random.randint(1, 10000)


if __name__ == "__main__":
    Client()
