
import asyncio
import json
import random

import aiocoap
import aiocoap.resource as resource
from aiocoap.numbers.contentformat import ContentFormat

class SensorResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.data = self.generate_data()

    @staticmethod
    def generate_data():
        return {
            "device_id": "sensor01",
            "temperature": round(random.uniform(20, 40), 1),
            "humidity": round(random.uniform(30, 80), 1)
        }

    async def update_sensor(self):
        while True:
            await asyncio.sleep(3)
            self.data = self.generate_data()
            print("Sensor data updated:", json.dumps(self.data))

    async def render_get(self, request):
        payload = json.dumps(self.data).encode("utf-8")
        print("GET request received: /iot/lab/sensor01/data")

        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=payload,
            content_format=ContentFormat.JSON
        )

async def main():
    root = resource.Site()
    sensor = SensorResource()
    root.add_resource(["iot", "lab", "sensor01", "data"], sensor)
    context = await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    update_task = asyncio.create_task(sensor.update_sensor())

    print("Sensor CoAP Server started on port 5683")
    print("Resource: /iot/lab/sensor01/data")
    print("Nhan Ctrl+C de dung Server.")

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
        await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung Sensor Server.")
