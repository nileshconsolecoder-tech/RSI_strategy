import configparser
# import lib.UI as UI
# import wx
# import time
# from datetime import datetime, time
import asyncio
import time
from datetime import datetime, timedelta
import logging
import os
from lib.broker import brokerSession
from lib.RSI_Strategy import RSIStrategy


import inspect
from lib.rsi_logic import RSI
from lib.data_manager import DataManager


def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[MN] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    
    print(full_message)
    logging.info(full_message)

today_date = datetime.now().strftime('%Y-%m-%d')
current_time = datetime.now().strftime('%H-%M-%S')
log_directory = os.path.join('logs', today_date)



if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, f'{current_time}.txt')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



config = configparser.ConfigParser()
config.read('etc/config.ini')
broker_section = config['broker_config']


# Build dictionary
# Convert into dict
config_dict = {
    "api_key": broker_section.get("API_KEY"),
    "api_secret": broker_section.get("API_SECRET_KEY"),
    "client_id": broker_section.get("CLIENT_ID"),
    "password": broker_section.get("password"),
    "totp_key": broker_section.get("totp_key"),
    
    }

broker = brokerSession(config_dict)
data_manager = DataManager(broker)
rsi_strategy = RSIStrategy()
rsi_logic = RSI(broker,data_manager,rsi_strategy)



async def start_background_worker():
    asyncio.create_task(rsi_logic.get_RSI())


async def main():
    asyncio.create_task(rsi_logic.get_RSI())

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_log("Bot stopped manually.")


# if __name__ == "__main__":
#     app = wx.App(False)
#     frame = UI.MyFrame1(None)
#     frame.broker = broker
#     frame.SetTitle("Monthly Option Selling")
#     frame.Show(True)
#     frame.boot_loader()
#     app.MainLoop()
