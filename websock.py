import time
import datetime as dt
import pandas as pd
import pandas_ta as ta
import numpy as np
import websocket
import json
from discord_webhook import DiscordWebhook
from config import WEBHOOK_URL

volume_array = []
close_array = []
cross = False


def on_message(ws, message):
    data = json.loads(message)
    candle = data["k"]

    if candle["x"]:
        volume = float(candle["v"])
        close = float(candle["c"])
        volume_array.append(volume)
        close_array.append(close)

        # msg = f"{pd.to_datetime(candle['t'], unit='ms')} volume = {volume} ARB"

        print(f"Candle opened at {pd.to_datetime(candle['t'], unit='ms')} has closed.")
        print(f"Volume = {volume}")

        # if len(volume_array) > 20 or len(close_array) > 14:
        #     rvol = volume / np.array(volume_array)[-20:].mean()
        #     if rvol > 2:
        #         msg = f"{pd.to_datetime(candle['t'], unit='ms')} volume = {volume} ARB, RVOL = {rvol}"
        #         webhook = DiscordWebhook(url=WEBHOOK_URL, content=msg)
        #         response = webhook.execute()

        if len(close_array) > 14:
            rsi_val = pd.DataFrame({"close": close_array}).ta.rsi().values[-1]
            print(f"RSI = {np.round(rsi_val):.4f}")

            if not cross and (rsi_val < 30 or rsi_val > 70):
                cross = True
                msg = f"{pd.to_datetime(candle['t'], unit='ms')}, RSI = {rsi_val}"
                webhook = DiscordWebhook(url=WEBHOOK_URL, content=msg)
                response = webhook.execute()
            if 30 <= rsi_val <= 70:
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
