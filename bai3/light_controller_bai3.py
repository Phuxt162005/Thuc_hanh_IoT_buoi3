"""Controller tương tác: ON/OFF/STATUS/EXIT; NON là tùy chọn."""

import json

import aiocoap

from lab_common import exchange, keyboard, message, parser, run, show_response, single_device


async def main(args):
    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    print(f"Controller: {args.device}; type={'NON' if args.non else 'CON'}")
    print("Lenh: ON / OFF / STATUS / EXIT")
    print("Lenh khac EXIT/STATUS duoc gui PUT de thu server tu choi lenh sai.")
    try:
        while True:
            command = await keyboard("\nNhap lenh (ON/OFF/STATUS/EXIT): ")
            if command is None or command.upper() == "EXIT":
                break
            command = command.upper()
            if not command:
                print("Lenh khong duoc rong.")
                continue
            path = f"iot/lab/{args.device}/status"
            if command == "STATUS":
                request = message(args, aiocoap.GET, path)
            else:
                payload = json.dumps({"device_id": args.device, "command": command}).encode("utf-8")
                request = message(args, aiocoap.PUT, path, payload=payload, content_format=50)
            print("Sending", request.code, "request...")
            try:
                show_response(await exchange(context, request, args.timeout))
            except Exception as error:
                print(f"Loi giao tiep/timeout ({args.timeout:g}s): {type(error).__name__}: {error}")
    finally:
        await context.shutdown()
        print("Da dong Controller.")


if __name__ == "__main__":
    options = parser("Bai 3 - Controller")
    options.add_argument("--device", type=single_device, default="light01")
    run(main, options.parse_args())
