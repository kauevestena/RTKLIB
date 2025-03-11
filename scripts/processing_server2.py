from vmf3 import *
import os
import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PROCESSING_PORT = 5000
CONTROL_PORT = 5001

# Shared control variables
control_vars = {}
control_lock = threading.Lock()

base_delaypath = '/home/gnss_data/saidas'

def handle_processing(conn, addr):
    # print(f"Processing connection from {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        # Access shared control variables safely
        with control_lock:
            station = control_vars.get("CURRENT_STATION")
            proc_scenario = control_vars.get("PROC_SCENARIO")
            delay_path = control_vars.get("CURRENT_DELAYPATH", os.path.join(base_delaypath, proc_scenario))

        message = data.decode("utf-8").strip()
        response = process(message, station, delay_path)
        conn.sendall(str(response).encode("utf-8"))
    # print(f"Processing client disconnected: {addr}")
    conn.close()

def handle_control(conn, addr):
    print(f"Control connection from {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        try:
            key, value = data.decode("utf-8").strip().split(":")
            with control_lock:
                control_vars[key] = value
            print(f"Updated control variable: {key} = {value}")
        except ValueError:
            logging.error(f"Received an invalid control message: {data}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e} data: {data}")
    print(f"Control client disconnected: {addr}")
    conn.close()

def processing_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PROCESSING_PORT))
        s.listen()
        print(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
        logging.info(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
        # Create a thread pool with a fixed number of worker threads (tune max_workers as needed)
        with ThreadPoolExecutor(max_workers=32) as executor:
            while True:
                conn, addr = s.accept()
                executor.submit(handle_processing, conn, addr)

def control_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, CONTROL_PORT))
        s.listen()
        print(f"Control service listening on {HOST}:{CONTROL_PORT}")
        logging.info(f"Control service listening on {HOST}:{CONTROL_PORT}")
        # You can also use a thread pool here, though the control channel has much lower load
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_control, args=(conn, addr)).start()

if __name__ == "__main__":
    threading.Thread(target=processing_server, daemon=True).start()
    threading.Thread(target=control_server, daemon=True).start()
    # Prevent main thread from exiting
    threading.Event().wait()
