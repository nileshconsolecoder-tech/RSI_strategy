
import wx
import asyncio
import inspect
from static.V3_ui import MyFrame1
import logging

def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    
    message_str = '[TP] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    full_message = f'{message_str}'
    
    print(full_message)
    logging.info(full_message)


class TradingFrame(MyFrame1):

    def __init__(self, parent, broker, data_manager, rsi_strategy, rsi_logic, loop):

        super().__init__(parent)

        self.broker = broker
        self.data_manager = data_manager
        self.rsi_strategy = rsi_strategy
        self.rsi_logic = rsi_logic
        self.loop = loop

        self.worker_started = False

        # enable ENTER detection
        self.instrument_name.SetWindowStyleFlag(wx.TE_PROCESS_ENTER)

        # Bind events
        self.instrument_name.Bind(wx.EVT_TEXT_ENTER, self.on_symbol_enter)
        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        self.On_Off.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_strategy)
        # self.m_button4.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.On_Off.SetLabel("OFF")
        self.m_button4.Bind(wx.EVT_BUTTON, self.on_exit_position)
        print_log("UI Ready")


    # ==========================
    # Symbol ENTER
    # ==========================

    def on_symbol_enter(self, event):

        symbol = self.instrument_name.GetValue().upper()

        try:

            token = self.broker.tradingsymbol[symbol]["instrument_token"]
            ltp = self.broker.get_ltp(token)
            self.data_manager.INSTRUMENT_TOKEN = token
            self.rsi_strategy.INSTRUMENT_TOKEN = token


            self.rsi_strategy.ltp = ltp

            self.m_staticText4.SetLabel(f"{ltp:.2f}")

            print_log("Symbol Loaded:", symbol)

            if not self.worker_started:

                asyncio.run_coroutine_threadsafe(
                    self.strategy_worker(), self.loop
                )

                self.worker_started = True

        except Exception as e:

            print_log("Symbol error:", e)


    # ==========================
    # Strategy Worker
    # ==========================

    async def strategy_worker(self):

        while True:

            try:

                await self.rsi_logic.get_RSI()

                self.rsi_strategy.run_strategy()

                wx.CallAfter(self.update_rsi_display)

            except Exception as e:

                print_log("Worker error:", e)

            await asyncio.sleep(1)


    # ==========================
    # Save Quantity
    # ==========================

    def on_save(self, event):

        qty = self.Quantity_input.GetValue()

        if qty == "":
            return

        self.rsi_strategy.quantity = int(qty)

        print_log("Quantity saved:", qty)


    # ==========================
    # Toggle Strategy
    # ==========================

    def toggle_strategy(self, event):

        if self.On_Off.GetValue():

            self.On_Off.SetLabel("ON")
            self.rsi_strategy.rsi_strategy_status = "ON"

            print_log("Strategy ON")

        else:

            self.On_Off.SetLabel("OFF")
            self.rsi_strategy.rsi_strategy_status = "OFF"

            print_log("Strategy OFF")


    # ==========================
    # Update UI
    # ==========================

    def update_rsi_display(self):

        rsi15 = self.rsi_strategy.rsi_15min
        rsi1h = self.rsi_strategy.rsi_1hr
        rsi_ma = self.rsi_strategy.rsi_ma_1hr
        ltp = self.rsi_strategy.ltp

        if rsi15 is not None:
            self.m_staticText7.SetLabel(f"{rsi15:.2f}")

        if rsi1h is not None:
            self.m_staticText9.SetLabel(f"{rsi1h:.2f}")

        if rsi_ma is not None:
            self.m_staticText11.SetLabel(f"{rsi_ma:.2f}")

        if ltp is not None:
            self.m_staticText4.SetLabel(f"{ltp:.2f}")


    # ==========================
    # Close App
    # ==========================

    def on_close(self, event):

        print_log("Closing app")

        try:
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
        except:
            pass

        self.Destroy()

    def on_exit_position(self, event):

        print_log("Manual exit triggered")

        if self.rsi_strategy.status == "active":

            self.rsi_strategy.Manual_EXIT = True

        else:

            print_log("No active position")