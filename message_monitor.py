import asyncio
import websockets
import ssl
import json
from threading import Thread
import winsound


alert_keywords = [
    '*',
    'http'
]
chat_id = 3846231 # found from the network log of the kick.com live stream page if you filter for /chatroom


# Create an SSL context with verification disabled
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE



def play_alert():
    sound_thread = Thread(target=winsound.PlaySound, args=(
        "alert.wav", winsound.SND_FILENAME))
    sound_thread.daemon = True
    sound_thread.start()


async def connect_and_send(chat_id):
    data_to_send = [
        {"event": "pusher:subscribe", "data": {
            "auth": "", "channel": f"chatrooms.{chat_id}.v2"}},
        {"event": "pusher:subscribe", "data": {
            "auth": "", "channel": f"chatrooms.{chat_id}"}},
        {"event": "pusher:subscribe", "data": {
            "auth": "", "channel": f"chatroom_{chat_id}"}}
    ]

    socket_link = 'wss://ws-us2.pusher.com/app/32cbd69e4b950bf97679?protocol=7&client=js&version=8.4.0-rc2&flash=false'
    async with websockets.connect(socket_link, ssl=ssl_context) as websocket:
        for data in data_to_send:
            await websocket.send(json.dumps(data))
            print("Sent", data)

        while True:
            # response = await websocket.recv()
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
            except:
                return
            # print(f"Received from socket: {response}")
            data = json.loads(response).get('data')
            data = json.loads(data)
            if data:
                username = data.get('sender', {}).get('username')
                if username is None:
                    continue
                message = data.get('content')
                print(f"{username}: {message}")
                if any(keyword.lower() in message.lower() for keyword in alert_keywords):
                    play_alert()
                


async def async_thread():
    await asyncio.wait_for(connect_and_send(), timeout=30)


if __name__ == "__main__":
    asyncio.run(connect_and_send(chat_id))
