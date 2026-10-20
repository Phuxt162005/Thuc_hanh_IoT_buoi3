import asyncio

import aiocoap 
from aiocoap.numbers.contentformat import ContentFormat

URI = "coap://localhost:5683/iot/lab/message"

async def main():
    protocol = await aiocoap.Context.create_client_context()

    try:
        # Gui yeu cau GET
        print("Sending GET request...")
        print("URI:", URI)

        get_request = aiocoap.Message(code=aiocoap.GET, uri=URI)
        try:
            get_response = await protocol.request(get_request).response
            print("\nResponse:")
            print("Code:", get_response.code)
            print("Payload:", get_response.payload.decode("utf-8"))
        except Exception as error:
            print("GET request failed:", error)
            return

        # Nhap thong tin sinh vien
        full_name = input("\nNhap ho ten sinh vien: ").strip()
        student_id = input("Nhap ma sinh vien: ").strip()
        if not full_name or not student_id:
            print("Ho ten va ma sinh vien khong duoc de trong.")
            return
        message = (f"Xin chao tu CoAP Client - " f"{student_id} - {full_name}")
        # Gui yeu cau POST
        print("\nSending POST request...")
        print("Payload:", message)

        post_request = aiocoap.Message(
            code=aiocoap.POST,
            uri=URI,
            payload=message.encode("utf-8"),
            content_format=ContentFormat.TEXT
        )

        try:
            post_response = await protocol.request(post_request).response
            print("\nResponse:")
            print("Code:", post_response.code)
            print("Payload:", post_response.payload.decode("utf-8"))
        except Exception as error:
            print("POST request failed:", error)

    finally:
        await protocol.shutdown()

if __name__ == "__main__":
    asyncio.run(main())