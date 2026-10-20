
import asyncio
import json
from datetime import datetime

import aiocoap

URI = "coap://localhost:5683/iot/lab/sensor01/data"

async def main():
    protocol = await aiocoap.Context.create_client_context()

    print("Monitoring CoAP Client started.")
    print("Resource:", URI)
    print("Nhan Ctrl+C de dung Client.")

    try:
        while True:
            receive_time = datetime.now().strftime("%H:%M:%S")
            request = aiocoap.Message(code=aiocoap.GET, uri=URI)
            try:
                response = await protocol.request(request).response
                if not response.code.is_successful():
                    print(f"[{receive_time}] Server tra loi loi: {response.code}")
                    await asyncio.sleep(3)
                    continue
                data = json.loads(response.payload.decode("utf-8"))
                device_id = data["device_id"]
                temperature = float(data["temperature"])
                humidity = float(data["humidity"])

                print(f"\n[{receive_time}] Received sensor data")
                print(f"Device: {device_id}")
                print(f"Temperature: {temperature:.1f} C")
                print(f"Humidity: {humidity:.1f} %")

                has_warning = False
                if temperature > 35:
                    print("CANH BAO: Nhiet do cao")
                    has_warning = True
                if humidity < 40:
                    print("CANH BAO: Do am thap")
                    has_warning = True
                if not has_warning:
                    print("Trang thai: Binh thuong")
                print("-" * 30)

            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                print(f"[{receive_time}] Du lieu khong hop le: {error}")

            except Exception as error:
                print(f"[{receive_time}] Server khong phan hoi hoac loi giao tiep: {error}")

            await asyncio.sleep(3)
    finally:
        await protocol.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung Monitoring Client.")
