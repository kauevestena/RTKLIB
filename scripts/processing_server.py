from vmf3 import *

import socket
import threading

HOST = "127.0.0.1"
PROCESSING_PORT = 5000
CONTROL_PORT = 5001

# Shared control variables
control_vars = {}
control_lock = threading.Lock()


def handle_processing(conn, addr):
    # print(f"Processing connection from {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        # Access shared control variables safely
        with control_lock:
            # Example: retrieve a control variable
            station = control_vars.get("CURRENT_STATION")
            delay_path = control_vars.get("CURRENT_DELAYPATH")

        # Process data (e.g., echo in uppercase and apply multiplier to a number)
        message = data.decode("utf-8").strip()
        # print(f"Processing data: {message} with multiplier {multiplier}")

        response = process(message, station, delay_path)

        conn.sendall(str(response).encode("utf-8"))
    # print(f"Processing client disconnected: {addr}")


def handle_control(conn, addr):
    print(f"Control connection from {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        # Assume control messages are like: "multiplier:2"
        try:
            key, value = data.decode("utf-8").strip().split(":")
            with control_lock:
                control_vars[key] = value  # assuming value is an integer
            print(f"Updated control variable: {key} = {value}")
        except ValueError:
            logging.error(f"Received an invalid control message: {data}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while executing: {e} data: {data}"
            )
    print(f"Control client disconnected: {addr}")


def processing_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PROCESSING_PORT))
        s.listen()
        print(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
        logging.info(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_processing, args=(conn, addr)).start()


def control_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, CONTROL_PORT))
        s.listen()
        print(f"Control service listening on {HOST}:{CONTROL_PORT}")
        logging.info(f"Control service listening on {HOST}:{CONTROL_PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_control, args=(conn, addr)).start()


if __name__ == "__main__":
    threading.Thread(target=processing_server).start()
    threading.Thread(target=control_server).start()
