"""Chạy từ repo: python -m bai1.coap_server_bai1."""

import asyncio

import aiocoap
import aiocoap.resource as resource

from lab_common import parser, run, timestamp


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.latest = "Xin chao tu CoAP Server"

    async def render_get(self, request):
        print("GET request received: /iot/lab/message")
        return aiocoap.Message(code=aiocoap.CONTENT, payload=self.latest.encode("utf-8"), content_format=0)

    async def render_post(self, request):
        try:
            text = request.payload.decode("utf-8").strip()
        except UnicodeDecodeError:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Can UTF-8")
        if not text:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Thong diep khong duoc rong")
        self.latest = text
        print(f"\nPOST request received:\nPayload: {text}\nTime: {timestamp()}")
        return aiocoap.Message(code=aiocoap.CHANGED, payload=b"Server da nhan thong diep", content_format=0)


async def main(args):
    site = resource.Site()
    site.add_resource(["iot", "lab", "message"], MessageResource())
    context = await aiocoap.Context.create_server_context(site, bind=(args.host, args.port), transports=["simplesocketserver"])
    print(f"CoAP Server started on {args.host}:{args.port}")
    print("Resource: /iot/lab/message\nNhan Ctrl+C de dung Server.")
    try:
        await asyncio.Future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    run(main, parser("Bai 1 - Message Server", server=True).parse_args())
