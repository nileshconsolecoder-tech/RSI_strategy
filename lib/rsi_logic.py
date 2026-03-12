from datetime import datetime, timedelta
import time
import logging
import inspect
import csv
import os
from datetime import date
import asyncio
import csv
import pandas as pd
import talib


base_dir = os.getcwd()

today = date.today().strftime("%Y%m%d")
file_path = os.path.join(base_dir, "etc", f"Close_data_{today}.csv")

os.makedirs(os.path.dirname(file_path), exist_ok=True)


def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[RSI_LG] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    
    print(full_message)
    logging.info(full_message)

class RSI:
    def __init__(self,broker , data_manager, rsi_strategy):
        self.broker = broker
        self.data_manager = data_manager
        self.rsi_strategy = rsi_strategy

    async def get_RSI(self):
        if True:
            self.data_manager.fetch_all()
            price_dict_15min = self.data_manager.fetch_15min_data()
            price_dict_1hr = self.data_manager.fetch_1hr_data()
            raw_rsi_15min = calculate_indicators(price_dict_15min)
            raw_rsi_1hr = calculate_indicators(price_dict_1hr)
            RSI_15min = latest_entries(raw_rsi_15min)
            RSI_1hr = latest_entries(raw_rsi_1hr)
            print_log("RSI_15min --> ",RSI_15min)
            print_log("RSI_1hr  --> " ,RSI_1hr)
            self.rsi_strategy.update_indicators(RSI_15min,RSI_1hr)
            self.rsi_strategy.run_strategy()
            # await asyncio.sleep(6)


def calculate_indicators(data):

    # dict -> dataframe
    df = pd.DataFrame.from_dict(data, orient="index")

    df.reset_index(inplace=True)
    df.rename(columns={"index": "time"}, inplace=True)

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    close = df["close"]

    # indicators
    df["RSI"] = talib.RSI(close, timeperiod=14)
    df["RSI_MA"] = talib.SMA(df["RSI"], timeperiod=14)
    df["MA"] = talib.SMA(close, timeperiod=14)

    # convert time back to string
    df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M")

    # dataframe -> dict
    result = df.set_index("time").to_dict(orient="index")

    return result



def latest_entries(data, n=1):
    latest = list(data.items())[-n:]
    time, values = latest[0]
    output = {"data_time": time, **values}

    return output