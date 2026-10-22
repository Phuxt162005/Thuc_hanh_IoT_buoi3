"""Đăng ký Observe một lần; không GET polling."""

import asyncio
import json

import aiocoap

from lab_common import Recorder, message, parser, run, single_device, timestamp


def display_state(response, device, recorder, *, initial=False):
    if not response.code.is_successful():
        raise ValueError(f"Server tra loi {response.code}")
    if response.opt.content_format != 50:
        raise ValueError("Content-Format phai la application/json (50)")
    data = json.loads(response.payload.decode("utf-8"))
    if not isinstance(data, dict) or data.get("device_id") != device or data.get("status") not in ("ON", "OFF"):
        raise ValueError("Payload trang thai khong hop le")
    if not isinstance(data.get("timestamp"), str):
        raise ValueError("Thieu timestamp")
    received = timestamp()
    print(f"\n[{received}] {'Initial State' if initial else 'State Updated'}")
    print(f"Device: {device}\nStatus: {data['status']}\nServer timestamp: {data['timestamp']}")
    recorder.write({"received_at": received, **{key: data[key] for key in ("device_id", "status", "timestamp")}})


async def main(args):
    recorder = Recorder(args.output, ["received_at", "device_id", "status", "timestamp"])
    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    request = context.request(message(args, aiocoap.GET, f"iot/lab/{args.device}/status", observe=True))
    print(f"Registering CoAP Observe: {args.device} ({'NON' if args.non else 'CON'})...")
    try:
        response = await asyncio.wait_for(request.response, args.timeout)
        if not response.code.is_successful() or response.opt.observe is None:
            raise ValueError(f"Observe registration failed: {response.code}; observe={response.opt.observe}")
        print("Observe registration successful")
        display_state(response, args.device, recorder, initial=True)
        async for notification in request.observation:
            display_state(notification, args.device, recorder)
    except asyncio.CancelledError:
        raise
    except (aiocoap.error.Error, TimeoutError, ValueError, KeyError, TypeError, UnicodeDecodeError) as error:
        print(f"Loi Observe: {type(error).__name__}: {error}")
    finally:
        if not request.observation.cancelled:
            request.observation.cancel()
        await context.shutdown()


if __name__ == "__main__":
    options = parser("Bai 3 - Observe Monitoring, Ctrl+C de dung")
    options.add_argument("--device", type=single_device, default="light01")
    options.add_argument("--output", help="Luu notification ra .csv hoac .json")
    run(main, options.parse_args())
