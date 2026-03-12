import configparser
import asyncio
import threading
import time
from datetime import datetime
import logging
import os
import inspect
import wx

from lib.ui_design import MyFrame1
from lib.broker import brokerSession
from lib.RSI_Strategy import RSIStrategy
from lib.rsi_logic import RSI
from lib.data_manager import DataManager


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

broker = brokerSession(config_dict)

data_manager = DataManager(broker)

rsi_strategy = RSIStrategy()

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

        await asyncio.sleep(6)


# ==========================
# Async Thread Starter
# ==========================

def start_async_loop():

    global loop

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_forever()


# ==========================
# Trading UI
# ==========================

class TradingFrame(MyFrame1):

    def __init__(self, parent):

        super().__init__(parent)

        self.strategy_enabled = False
        self.worker_started = False
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.rsi_strategy = rsi_strategy
        self.data_manager = data_manager

        print_log("UI initialized")

    # ======================
    # SAVE Button
    # ======================

    def on_save(self, event):

        symbol = self.instrument_name.GetValue()
        qty = self.Quantity_input.GetValue()

        self.data_manager.INSTRUMENT_TOKEN = symbol
        self.rsi_strategy.quantity = int(qty)

        print_log("Saved Instrument:", symbol, "Qty:", qty)

        if not self.worker_started:

            asyncio.run_coroutine_threadsafe(
                strategy_worker(self), loop
            )

            self.worker_started = True

            print_log("Strategy loop started")
    # ======================
    # ON / OFF Toggle
    # ======================

    def on_toggle(self, event):

        self.strategy_enabled = not self.strategy_enabled

        if self.strategy_enabled:
            print_log("Strategy ENABLED")
        else:
            print_log("Strategy DISABLED")

    # ======================
    # EXIT
    # ======================

    def on_close(self, event):

        global loop, running

        print_log("Window close detected")

        running = False

        try:
            if loop and loop.is_running():
                loop.call_soon_threadsafe(loop.stop)
                print_log("Async loop stopped")

        except Exception as e:
            print_log("Error stopping loop:", e)

        self.Destroy()

    def update_rsi_display(self):

        rsi15 = self.rsi_strategy.rsi_15min
        rsi1h = self.rsi_strategy.rsi_1hr
        rsi_ma = self.rsi_strategy.rsi_ma_1hr
        print_log(
        "RSI15:", rsi_strategy.rsi_15min,
        "RSI1H:", rsi_strategy.rsi_1hr,
        "MA:", rsi_strategy.rsi_ma_1hr)
        if rsi15 is not None:
            self.m_staticText7.SetLabel(f"{rsi15:.2f}")

        if rsi1h is not None:
            self.m_staticText9.SetLabel(f"{rsi1h:.2f}")

        if rsi_ma is not None:
            self.m_staticText11.SetLabel(f"{rsi_ma:.2f}")


# ==========================
# Start Application
# ==========================

if __name__ == "__main__":

    # Start asyncio worker thread
    worker_thread = threading.Thread(target=start_async_loop)
    worker_thread.start()

    # Start UI
    app = wx.App(False)

    frame = TradingFrame(None)

    frame.SetTitle("RSI Trading Panel")

    frame.Show(True)

    app.MainLoop()