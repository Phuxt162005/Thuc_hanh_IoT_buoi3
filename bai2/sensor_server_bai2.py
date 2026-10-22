"""Ba cảm biến độc lập, cập nhật 3 giây; --seed giúp tái hiện demo."""

import asyncio
import json
import random

import aiocoap
import aiocoap.resource as resource

from lab_common import device_ids, json_response, parser, run, timestamp


class SensorResource(resource.Resource):
    def __init__(self, device_id, generator):
        super().__init__()
        self.device_id = device_id
        self.generator = generator
        self.update()

    def update(self):
        self.data = {"device_id": self.device_id,
                     "temperature": round(self.generator.uniform(20, 40), 1),
                     "humidity": round(self.generator.uniform(30, 80), 1),
                     "timestamp": timestamp()}

    async def render_get(self, request):
        print(f"GET request received: /iot/lab/{self.device_id}/data")
        return json_response(self.data)


async def main(args):
    site = resource.Site()
    generator = random.Random(args.seed)
    sensors = [SensorResource(device, generator) for device in args.devices]
    for sensor in sensors:
        site.add_resource(["iot", "lab", sensor.device_id, "data"], sensor)

    async def update_all():
        while True:
            await asyncio.sleep(3)
            for sensor in sensors:
                sensor.update()
                print("Sensor data updated:", json.dumps(sensor.data))

    context = await aiocoap.Context.create_server_context(site, bind=(args.host, args.port), transports=["simplesocketserver"])
    task = asyncio.create_task(update_all())
    print(f"Sensor CoAP Server started on {args.host}:{args.port}")
    for sensor in sensors:
        print(f"Resource: /iot/lab/{sensor.device_id}/data")
        print("Initial data:", json.dumps(sensor.data))
    try:
        await asyncio.Future()
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await context.shutdown()


if __name__ == "__main__":
    options = parser("Bai 2 - Sensor Server", server=True)
    options.add_argument("--devices", type=device_ids, default=["sensor01", "sensor02", "sensor03"])
    options.add_argument("--seed", type=int, help="Seed ngau nhien tuy chon cho demo lap lai")
    run(main, options.parse_args())
