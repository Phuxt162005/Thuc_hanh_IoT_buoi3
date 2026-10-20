
import asyncio
import json

import aiocoap
import aiocoap.resource as resource
from aiocoap.numbers.contentformat import ContentFormat

class LightStatusResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.device_id = "light01"
        self.status = "OFF"
        self.observer_count = 0

    def get_payload(self):
        data = {"device_id": self.device_id, "status": self.status}
        return json.dumps(data).encode("utf-8")

    async def render_get(self, request):
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=self.get_payload(),
            content_format=ContentFormat.JSON
        )

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Payload JSON khong hop le")

        if not isinstance(data, dict):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Payload phai la JSON object")

        if data.get("device_id") != self.device_id:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"device_id khong hop le")

        command = data.get("command")
        if not isinstance(command, str):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Command khong hop le")

        command = command.strip().upper()
        if command not in ("ON", "OFF"):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Chi chap nhan lenh ON hoac OFF")

        print("\nPUT request received:")
        print("Device:", self.device_id)
        print("Command:", command)
        old_status = self.status
        if command != old_status:
            self.status = command
            print(f"Light state changed: {old_status} -> {self.status}")
            self.updated_state()
            print("Notify observers:", self.status)
        else:
            print("Light state unchanged:", self.status)
        message = (
            "Da bat den light01"
            if self.status == "ON"
            else "Da tat den light01"
        )

        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=message.encode("utf-8"),
            content_format=ContentFormat.TEXT
        )

    def update_observation_count(self, count):
        if count > self.observer_count:
            print("\nNew Observe registration received")
        self.observer_count = count

async def main():
    root = resource.Site()
    light = LightStatusResource()
    root.add_resource(["iot", "lab", "light01", "status"], light)
    context = await aiocoap.Context.create_server_context(root)

    print("CoAP Smart Light Server started...")
    print("Resource: /iot/lab/light01/status")
    print("Initial state: OFF")
    print("Nhan Ctrl+C de dung Server.")

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung Smart Light Server.")
