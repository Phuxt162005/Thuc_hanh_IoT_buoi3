"""Polling 3 giây, cảnh báo, xuất dữ liệu và thống kê request."""

import asyncio
import json
import math
import time

import aiocoap

from lab_common import Recorder, exchange, message, parser, run, single_device, timestamp


def warnings(temperature, humidity):
    result = []
    if temperature > 35:
        result.append("CANH BAO: Nhiet do cao")
    if humidity < 40:
        result.append("CANH BAO: Do am thap")
    return result


async def main(args):
    recorder = Recorder(args.output, ["received_at", "device_id", "temperature", "humidity", "timestamp"])
    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    attempts = responses = samples = 0
    total_rtt = 0.0
    print(f"Monitoring CoAP Client started. Device: {args.device}; interval: 3s")
    print("Nhan Ctrl+C de dung Client.")
    loop = asyncio.get_running_loop()
    next_tick = loop.time()
    try:
        while args.count == 0 or attempts < args.count:
            attempts += 1
            started = time.perf_counter()
            try:
                request = message(args, aiocoap.GET, f"iot/lab/{args.device}/data")
                response = await exchange(context, request, args.timeout)
                rtt = time.perf_counter() - started
                responses += 1
                total_rtt += rtt
                received = timestamp()
                if not response.code.is_successful():
                    print(f"[{received}] Server tra loi loi: {response.code}")
                else:
                    if response.opt.content_format != 50:
                        raise ValueError("Content-Format phai la application/json (50)")
                    data = json.loads(response.payload.decode("utf-8"))
                    if not isinstance(data, dict) or data.get("device_id") != args.device:
                        raise ValueError("Sai device_id hoac JSON object")
                    temperature, humidity = data["temperature"], data["humidity"]
                    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
                           for value in (temperature, humidity)):
                        raise ValueError("So do phai la so huu han")
                    if not isinstance(data.get("timestamp"), str):
                        raise ValueError("Thieu timestamp")
                    print(f"\n[{received}] Received sensor data\nDevice: {data['device_id']}")
                    print(f"Temperature: {temperature:.1f} C\nHumidity: {humidity:.1f} %")
                    print("Sensor timestamp:", data["timestamp"])
                    for warning in warnings(temperature, humidity) or ["Trang thai: Binh thuong"]:
                        print(warning)
                    recorder.write({"received_at": received, **{key: data[key] for key in ("device_id", "temperature", "humidity", "timestamp")}})
                    samples += 1
                    print(f"RTT: {rtt * 1000:.2f} ms\n" + "-" * 30)
            except (TimeoutError, ValueError, KeyError, TypeError, UnicodeDecodeError, aiocoap.error.Error) as error:
                print(f"[{timestamp()}] Loi du lieu/giao tiep: {type(error).__name__}: {error}")
            if args.count and attempts >= args.count:
                break
            next_tick += 3
            if next_tick < loop.time():
                next_tick = loop.time() + 3
            await asyncio.sleep(max(0, next_tick - loop.time()))
    finally:
        average = f"{total_rtt / responses * 1000:.2f} ms" if responses else "N/A"
        print(f"\nThong ke: GET={attempts}; responses={responses}; valid_samples={samples}; avg_response={average}")
        await context.shutdown()


if __name__ == "__main__":
    options = parser("Bai 2 - Sensor Monitoring")
    options.add_argument("--device", default="sensor01", type=single_device)
    options.add_argument("--output", help="Luu .csv hoac .json")
    options.add_argument("--count", type=int, default=0, help="So GET; 0 = lien tuc den Ctrl+C")
    arguments = options.parse_args()
    if arguments.count < 0:
        options.error("--count khong duoc am")
    run(main, arguments)
