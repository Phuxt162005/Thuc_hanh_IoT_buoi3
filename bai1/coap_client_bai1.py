"""GET, gửi nhiều POST, đọc lại giá trị cuối và thử URI không tồn tại."""

import aiocoap

from lab_common import exchange, keyboard, message, parser, run, show_response, uri


async def main(args):
    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    path = "iot/lab/message"

    async def send(code, target=path, text=""):
        print(f"\nSending {code} request...\nURI: {uri(args, target)}")
        if text:
            print("Payload:", text)
        try:
            response = await exchange(context, message(args, code, target, payload=text.encode("utf-8"), content_format=0), args.timeout)
            show_response(response)
            return response
        except Exception as error:
            print(f"Loi giao tiep/timeout ({args.timeout:g}s): {type(error).__name__}: {error}")
            return None

    try:
        if await send(aiocoap.GET) is None:
            return
        if args.missing:
            await send(aiocoap.GET, "iot/lab/not-found")
        name = args.name if args.name is not None else await keyboard("Nhap ho ten sinh vien: ")
        student_id = args.student_id if args.student_id is not None else await keyboard("Nhap ma sinh vien: ")
        if not name or not name.strip() or not student_id or not student_id.strip():
            print("Ho ten va ma sinh vien khong duoc de trong.")
            return
        while True:
            greeting = await keyboard("Noi dung chao mung (Enter: Xin chao tu CoAP Client; EXIT: dung): ")
            if greeting is None or greeting.upper() == "EXIT":
                break
            text = f"{greeting or 'Xin chao tu CoAP Client'} - {student_id.strip()} - {name.strip()}"
            await send(aiocoap.POST, text=text)
            await send(aiocoap.GET)
    finally:
        await context.shutdown()


if __name__ == "__main__":
    options = parser("Bai 1 - GET va nhieu POST; EXIT de dung")
    options.add_argument("--name")
    options.add_argument("--student-id")
    options.add_argument("--missing", action="store_true", help="Thu GET URI khong ton tai (4.04)")
    run(main, options.parse_args())
