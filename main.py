import asyncio
import websockets
import logging
from websockets.http import Headers

logging.basicConfig(level=logging.INFO)

ORIGINAL_WS = "wss://srv1014265.hstgr.cloud:8080/30/8/19?co=3163&cu=9472&lg=en&wh=5288&ipm=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1MFwvMTI4NDM4NjIyNSIsInBpZCI6IjEiLCJqdGkiOiJpcG1fNjkxNWQwYmIxMWI5MjMuODgwOTcyNTMiLCJhcHAiOiJOQSIsImlubmVyIjoidHJ1ZSIsIm5iZiI6MTc2MzAzNzM3MSwiaWF0IjoxNzYzMDM3MzcxLCJleHAiOjE3NjMwNDA5NzF9.QB8fI__AxxnvglZYsZ-Qh2p2XT_krEWrTmOhRmloTXQ&tok=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI5OTk5OTk5Iiwicm9sZSI6IlRoYW5vcyIsImlhdCI6MTc2MzAzNzM3MSwiZXhwIjoxNzYzMDM3NDMxfQ.pACEmEtHs3IslxCeq4F-dnXH16X1yfOFh7Db8aW4l6A"  # رابط الأصلي

connected_clients = set()

async def connect_original_ws():
    """الاتصال بالأصلي وإرسال البيانات فوراً للعملاء."""
    while True:
        try:
            logging.info("Connecting to ORIGINAL...")
            async with websockets.connect(ORIGINAL_WS) as orig:
                logging.info("Connected to ORIGINAL")

                async for message in orig:
                    # بث الرسالة فوراً دون أي انتظار
                    dead = []
                    for client in connected_clients:
                        try:
                            await client.send(message)
                        except:
                            dead.append(client)

                    for d in dead:
                        connected_clients.remove(d)

        except Exception as e:
            logging.error(f"Original connection error: {e}")
            await asyncio.sleep(2)


async def server_handler(websocket, path):
    """WebSocket clients"""
    connected_clients.add(websocket)
    logging.info("Client connected")

    try:
        await websocket.wait_closed()
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        logging.info("Client disconnected")


async def http_handler(path, request_headers):
    """
    حلّ مشكلة Render/Replit:
    إذا جاء طلب HTTP عادي → نرجع له صفحة HTML صغيرة.
    هذا يمنع الخطأ InvalidMessage.
    """
    if "Upgrade" not in request_headers:
        body = b"<h1>WebSocket Relay Server Running</h1>"
        headers = Headers()
        headers["Content-Type"] = "text/html"
        headers["Content-Length"] = str(len(body))

        return (200, headers, body)

    # السماح لـ WebSocket upgrade
    return None


async def main():
    # تشغيل WebSocket + HTTP معاً
    server = await websockets.serve(
        server_handler,
        "0.0.0.0",
        8081,
        process_request=http_handler   # ← أهم شيء
    )

    logging.info("Your WS is running at ws://0.0.0.0:8081")

    await connect_original_ws()
    await server.wait_closed()


asyncio.run(main())
