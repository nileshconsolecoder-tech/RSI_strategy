import configparser
import asyncio
import threading
import time
from datetime import datetime
import logging
import os
import inspect
import wx

# from lib.ui_design import MyFrame1
from static.V2_ui import *
from lib.broker import brokerSession
from lib.RSI_Strategy import RSIStrategy
from lib.rsi_logic import RSI
from lib.data_manager import DataManager

from lib.trading_panel import TradingFrame


# ==========================
# Logger
# ==========================

def print_log(*args):

    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except:
        caller_name = "unknown"

    message_str = '[MN] ' + f'[{caller_name}] ' + ' '.join(map(str, args))
    print(message_str)
    logging.info(message_str)


# ==========================
# Logging Setup
# ==========================

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

# ==========================
# Load Config
# ==========================

config = configparser.ConfigParser()
config.read('etc/config.ini')

broker_section = config['broker_config']

config_dict = {
    "api_key": broker_section.get("API_KEY"),
    "api_secret": broker_section.get("API_SECRET_KEY"),
    "client_id": broker_section.get("CLIENT_ID"),
    "password": broker_section.get("password"),
    "totp_key": broker_section.get("totp_key"),
}

# ==========================
# Initialize Core Objects
# ==========================
rsi_strategy = RSIStrategy()


broker = brokerSession(config_dict,rsi_strategy)

data_manager = DataManager(broker)


rsi_logic = RSI(broker, data_manager, rsi_strategy)



# ==========================
# Async Event Loop (global)
# ==========================

loop = None



# ==========================
# Strategy Worker
# ==========================
async def strategy_worker(frame):

    print_log("RSI worker started")

    while True:

        try:

            await rsi_logic.get_RSI()
            wx.CallAfter(frame.update_rsi_display)

        except Exception as e:

            print_log("Strategy error:", e)

        await asyncio.sleep(1)



def start_async_loop():

    global loop

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_forever()


if __name__ == "__main__":

    worker_thread = threading.Thread(target=start_async_loop)
    worker_thread.start()

    app = wx.App(False)

    frame = TradingFrame(
        None,
        broker,
        data_manager,
        rsi_strategy,
        rsi_logic,
        loop
    )
    
    frame.SetTitle("RSI Trading Panel")

    frame.Show(True)

    app.MainLoop()
