
import asyncio
import json
from datetime import datetime

import aiocoap

URI = "coap://127.0.0.1:5683/iot/lab/light01/status"

def display_state(response, initial=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        data = json.loads(response.payload.decode("utf-8"))
        device_id = data["device_id"]
        status = data["status"]

        if initial:
            print(f"\n[{timestamp}] Initial State")
        else:
            print(f"\n[{timestamp}] State Updated")

        print("Device:", device_id)
        print("Status:", status)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"[{timestamp}] Du lieu nhan duoc khong hop le:", error)

async def main():
    protocol = await aiocoap.Context.create_client_context()
    request_message = aiocoap.Message(code=aiocoap.GET, uri=URI)
    request_message.opt.observe = 0
    request = protocol.request(request_message)

    print("Registering CoAP Observe...")
    print("URI:", URI)
    try:
        response = await request.response
        if not response.code.is_successful():
            print("Observe registration failed:", response.code)
            return
        print("Observe registration successful")
        display_state(response, initial=True)

        async for notification in request.observation:
            if notification.code.is_successful():
                display_state(notification)
            else:
                print("Observe notification error:", notification.code)
                break
    except asyncio.CancelledError:
        raise
    except Exception as error:
        print("Loi khi dang ky hoac nhan Observe:", error)
    finally:
        await protocol.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung Monitoring Client.")
