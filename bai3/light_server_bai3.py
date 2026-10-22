"""Observe cho light01, fan01, pump01; nhật ký mọi thay đổi trạng thái."""

import asyncio
import json

import aiocoap
import aiocoap.resource as resource

from lab_common import Recorder, device_ids, error_response, json_response, parser, run, timestamp


class LightStatusResource(resource.ObservableResource):
    def __init__(self, device_id, recorder):
        super().__init__()
        self.device_id = device_id
        self.status = "OFF"
        self.changed_at = timestamp()
        self.recorder = recorder
        self.observer_count = 0

    async def render_get(self, request):
        return json_response({"device_id": self.device_id, "status": self.status, "timestamp": self.changed_at})

    async def render_put(self, request):
        if request.opt.content_format != 50:
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_CONTENT_FORMAT, payload=b"Can application/json")
        try:
            data = json.loads(request.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return error_response("Payload JSON khong hop le")
        if not isinstance(data, dict):
            return error_response("Payload phai la JSON object")
        if data.get("device_id") != self.device_id:
            return error_response("device_id khong hop le")
        command = data.get("command")
        if not isinstance(command, str) or command.strip().upper() not in ("ON", "OFF"):
            return error_response("Chi chap nhan lenh ON hoac OFF")
        command = command.strip().upper()
        old_status = self.status
        print(f"\nPUT request received:\nDevice: {self.device_id}\nCommand: {command}")
        if command != old_status:
            changed_at = timestamp()
            try:
                self.recorder.write({"timestamp": changed_at, "device_id": self.device_id,
                                     "old_status": old_status, "status": command})
            except (OSError, ValueError) as error:
                print("Loi ghi nhat ky:", error)
                return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR, payload=b"Khong ghi duoc nhat ky")
            self.status = command
            self.changed_at = changed_at
            print(f"Light state changed: {old_status} -> {command}")
            self.updated_state()
            print(f"Notify observers: {self.device_id} {command}; count={self.observer_count}")
        else:
            print("Light state unchanged:", self.status)
        text = f"Da {'bat' if command == 'ON' else 'tat'} thiet bi {self.device_id}"
        return aiocoap.Message(code=aiocoap.CHANGED, payload=text.encode("utf-8"), content_format=0)

    def update_observation_count(self, count):
        print(f"Observe count: {self.device_id} = {count}")
        if count > self.observer_count:
            print("New Observe registration received:", self.device_id)
        self.observer_count = count


async def main(args):
    recorder = Recorder(args.log, ["timestamp", "device_id", "old_status", "status"])
    site = resource.Site()
    for device in args.devices:
        site.add_resource(["iot", "lab", device, "status"], LightStatusResource(device, recorder))
    context = await aiocoap.Context.create_server_context(site, bind=(args.host, args.port), transports=["simplesocketserver"])
    print(f"CoAP Smart Light Server started on {args.host}:{args.port}")
    for device in args.devices:
        print(f"Resource: /iot/lab/{device}/status; Initial state: OFF")
    print("Nhat ky:", args.log)
    try:
        await asyncio.Future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    options = parser("Bai 3 - Smart Device Server", server=True)
    options.add_argument("--devices", type=device_ids, default=["light01", "fan01", "pump01"])
    options.add_argument("--log", default="outputs/device-events.json", help="Nhat ky .json hoac .csv")
    run(main, options.parse_args())
