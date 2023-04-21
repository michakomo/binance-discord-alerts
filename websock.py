import time
import datetime as dt
import pandas as pd
import pandas_ta as ta
import numpy as np
import websocket
import json
from discord_webhook import DiscordWebhook

from config import WEBHOOK_URL

VOLUME_ARRAY = []
CLOSE_ARRAY = []
cross = False

def on_message(ws, message):
    data = json.loads(message)
    candle = data['k']

    if candle['x']:
        volume = float(candle['v'])
        close = float(candle['c'])
        VOLUME_ARRAY.append(volume)
        CLOSE_ARRAY.append(close)

        # msg = f"{pd.to_datetime(candle['t'], unit='ms')} volume = {volume} ARB"

        print(f"Candle opened at {pd.to_datetime(candle['t'], unit='ms')} has closed.")
        print(f"Volume = {volume}")

        # if len(VOLUME_ARRAY) > 20 or len(CLOSE_ARRAY) > 14:
        #     rvol = volume / np.array(VOLUME_ARRAY)[-20:].mean()
        #     if rvol > 2:
        #         msg = f"{pd.to_datetime(candle['t'], unit='ms')} volume = {volume} ARB, RVOL = {rvol}"
        #         webhook = DiscordWebhook(url=WEBHOOK_URL, content=msg)
        #         response = webhook.execute()

        if len(CLOSE_ARRAY) > 14:
            rsi_val = pd.DataFrame({"close": CLOSE_ARRAY}).ta.rsi().values[-1]
            print(f"RSI = {np.round(rsi_val):.4f}")

            if (rsi_val > 70 or rsi_val < 30) and cross == False:
                cross = True
                msg = f"{pd.to_datetime(candle['t'], unit='ms')}, RSI = {rsi_val}"
                webhook = DiscordWebhook(url=WEBHOOK_URL, content=msg)
                response = webhook.execute()
            if rsi_val >= 30 and rsi_val <= 70:
                cross = False
        
        print("")
        time.sleep(58)


def main() -> int:
    url = "wss://fstream.binance.com/ws/arbusdt@kline_1m"
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()

    return 0


if __name__ == "__main__":
    main()
