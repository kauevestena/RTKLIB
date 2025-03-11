from vmf3 import *
import os
import asyncio
import logging

HOST = "127.0.0.1"
PROCESSING_PORT = 5000
CONTROL_PORT = 5001

# Shared control variables and an asyncio lock
control_vars = {}
control_lock = asyncio.Lock()

base_delaypath = '/home/gnss_data/saidas'

async def handle_processing(reader, writer):
    addr = writer.get_extra_info("peername")
    # Optionally: print(f"Processing connection from {addr}")
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            # Safely access shared control variables using an async lock
            async with control_lock:
                station = control_vars.get("CURRENT_STATION")
                proc_scenario = control_vars.get("PROC_SCENARIO")
                delay_path = control_vars.get("CURRENT_DELAYPATH", os.path.join(base_delaypath, proc_scenario))

            message = data.decode("utf-8").strip()
            # Offload the processing to a separate thread if process() is blocking
            response = await asyncio.to_thread(process, message, station, delay_path)
            writer.write(str(response).encode("utf-8"))
            await writer.drain()
    except Exception as e:
        logging.error(f"Error processing connection {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
    # Optionally: print(f"Processing client disconnected: {addr}")

async def handle_control(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Control connection from {addr}")
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            try:
                key, value = data.decode("utf-8").strip().split(":")
                async with control_lock:
                    control_vars[key] = value
                print(f"Updated control variable: {key} = {value}")
            except ValueError:
                logging.error(f"Invalid control message: {data}")
            except Exception as e:
                logging.error(f"Unexpected error: {e} data: {data}")
    finally:
        print(f"Control client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    processing_server = await asyncio.start_server(handle_processing, HOST, PROCESSING_PORT)
    control_server = await asyncio.start_server(handle_control, HOST, CONTROL_PORT)
    print(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
    logging.info(f"Processing service listening on {HOST}:{PROCESSING_PORT}")
    print(f"Control service listening on {HOST}:{CONTROL_PORT}")
    logging.info(f"Control service listening on {HOST}:{CONTROL_PORT}")

    async with processing_server, control_server:
        await asyncio.gather(
            processing_server.serve_forever(),
            control_server.serve_forever()
        )

if __name__ == "__main__":
    asyncio.run(main())
