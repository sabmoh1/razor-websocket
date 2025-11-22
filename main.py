import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

# ضع رابط الويب سوكت الأصلي هنا
ORIGINAL_WS = "wss://srv1014265.hstgr.cloud:8080/30/8/19?co=3163&cu=9472&lg=en&wh=5288&ipm=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1MFwvMTI4NDM4NjIyNSIsInBpZCI6IjEiLCJqdGkiOiJpcG1fNjkxNWQwYmIxMWI5MjMuODgwOTcyNTMiLCJhcHAiOiJOQSIsImlubmVyIjoidHJ1ZSIsIm5iZiI6MTc2MzAzNzM3MSwiaWF0IjoxNzYzMDM3MzcxLCJleHAiOjE3NjMwNDA5NzF9.QB8fI__AxxnvglZYsZ-Qh2p2XT_krEWrTmOhRmloTXQ&tok=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI5OTk5OTk5Iiwicm9sZSI6IlRoYW5vcyIsImlhdCI6MTc2MzAzNzM3MSwiZXhwIjoxNzYzMDM3NDMxfQ.pACEmEtHs3IslxCeq4F-dnXH16X1yfOFh7Db8aW4l6A"


# قائمة بكل الأشخاص المتصلين بسيرفرك
connected_clients = set()


async def connect_to_original():
    """الاتصال بالويب سوكت الأصلي ونقل البيانات للعملاء"""
    while True:
        try:
            logging.info("Connecting to ORIGINAL WebSocket...")
            async with websockets.connect(ORIGINAL_WS) as orig:
                logging.info("Connected to ORIGINAL WebSocket")

                async for message in orig:
                    logging.info(f"ORIGINAL → {message}")

                    # إرسال الرسالة لكل العملاء المتصلين بسيرفرك
                    dead = []
                    for client in connected_clients:
                        try:
                            await client.send(message)
                        except:
                            dead.append(client)

                    # حذف العملاء الذين انفصلوا
                    for d in dead:
                        connected_clients.remove(d)

        except Exception as e:
            logging.error(f"Error: {e}")
            logging.info("Reconnecting in 3 seconds...")
            await asyncio.sleep(3)


async def client_handler(websocket, path):
    """هذا هو WebSocket Server الذي يتصل به المستخدمون"""
    connected_clients.add(websocket)
    logging.info("Client connected")

    try:
        # ننتظر فقط حتى يغلق العميل الاتصال
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        logging.info("Client disconnected")


async def main():
    # شغل السيرفر المحلي الخاص بك
    server = await websockets.serve(client_handler, "0.0.0.0", 8081)
    logging.info("Your WebSocket Server is running on ws://0.0.0.0:8081")

    # شغل الريلاي
    await connect_to_original()


asyncio.run(main())