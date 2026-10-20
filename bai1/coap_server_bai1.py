import asyncio
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap.numbers.contentformat import ContentFormat

class MessageResource(resource.Resource):
    async def render_get(self, request):
        print("GET request received: /iot/lab/message")

        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=b"Xin chao tu CoAP Server",
            content_format=ContentFormat.TEXT
        )

    async def render_post(self, request):
        message = request.payload.decode("utf-8", errors="replace")

        print("\nPOST request received:")
        print("Payload:", message)
        print("Time:", datetime.now().strftime("%H:%M:%S"))

        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=b"Server da nhan thong diep",
            content_format=ContentFormat.TEXT
        )

async def main():
    root = resource.Site()
    root.add_resource(["iot", "lab", "message"], MessageResource())

    context = await aiocoap.Context.create_server_context(root)

    print("CoAP Server started on port 5683")
    print("Resource: /iot/lab/message")
    print("Nhan Ctrl+C de dung Server.")

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDa dung CoAP Server.")