import websocket
import json
import time
from datetime import datetime
from data.ticks import add_tick

SOCKET_URL = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"

def on_message(ws, message):
    try:
        data = json.loads(message)
        trade = data["data"]
        add_tick(symbol=trade["s"],
                 timestamp=datetime.fromtimestamp(trade["T"]/1000),
                 price=float(trade["p"]),
                 qty=float(trade["q"]))
    except Exception as e:
        print("Error processing message:", e)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed:", close_status_code, close_msg)

def on_open(ws):
    print("WebSocket connection opened")

def start_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(SOCKET_URL,
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
        except Exception as e:
            print("WebSocket crashed, reconnecting in 5 seconds...", e)
            time.sleep(5)
