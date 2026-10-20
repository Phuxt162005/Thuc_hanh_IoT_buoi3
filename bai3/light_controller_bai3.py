
import asyncio
import json

import aiocoap
from aiocoap.numbers.contentformat import ContentFormat

URI = "coap://localhost:5683/iot/lab/light01/status"

async def main():
    protocol = await aiocoap.Context.create_client_context()

    print("Light Controller Client started.")
    print("URI:", URI)
    print("Lenh: ON / OFF / STATUS / EXIT")

    try:
        while True:
            command = await asyncio.get_running_loop().run_in_executor(None, lambda: input("\nNhap lenh (ON/OFF/STATUS/EXIT): ").strip().upper())
            if command == "EXIT":
                break
            if command == "STATUS":
                request = aiocoap.Message(code=aiocoap.GET, uri=URI)
                print("\nSending GET request...")
            elif command in ("ON", "OFF"):
                payload = {"device_id": "light01", "command": command}
                request = aiocoap.Message(
                    code=aiocoap.PUT,
                    uri=URI,
                    payload=json.dumps(payload).encode("utf-8"),
                    content_format=ContentFormat.JSON
                )
                print("\nSending PUT request...")

            else:
                print("Lenh khong hop le. Hay nhap ON, OFF, STATUS hoac EXIT.")
                continue
            try:
                response = await protocol.request(request).response
                print("Response Code:", response.code)

                if response.code.is_successful():
                    text = response.payload.decode("utf-8")
                    if command == "STATUS":
                        try:
                            data = json.loads(text)
                            print("Response:")
                            print(json.dumps(data, ensure_ascii=False))
                        except json.JSONDecodeError:
                            print("Payload:", text)
                    else:
                        print(text)
                else:
                    print("Server error:", response.payload.decode("utf-8", errors="replace"))

            except Exception as error:
                print("Loi giao tiep CoAP:", error)
    finally:
        await protocol.shutdown()
        print("Da dong Light Controller Client.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung Controller Client.")
