# -*- coding: utf-8 -*-
"""
trading_panel.py
────────────────────────────────────────────────────────────────────
TradingFrame  —  inherits TradingDashboard and wires it to
                 RSIStrategy + broker + data_manager + rsi_logic.

Architecture
────────────
  TradingFrame(TradingDashboard)
    ├── broker          — symbol lookup, LTP fetch, order placement
    ├── data_manager    — manages INSTRUMENT_TOKEN for tick stream
    ├── rsi_strategy    — RSIStrategy instance (state + logic)
    ├── rsi_logic       — async RSI calculator (get_RSI coroutine)
    └── strategy_worker — asyncio coroutine: get_RSI → run_strategy
                          → wx.CallAfter(update UI)

Flow
────
  1. User types symbol → ENTER/TAB → on_symbol_enter()
       → broker resolves token + ltp
       → data_manager & rsi_strategy get INSTRUMENT_TOKEN
       → strategy_worker coroutine launched (once)

  2. strategy_worker loop (every 1 s):
       → rsi_logic.get_RSI()           [async, from broker candles]
       → rsi_strategy.run_strategy()   [entry / exit / manual exit]
       → wx.CallAfter(update_rsi_display)
       → wx.CallAfter(sync_strategy_state)

  3. ON/OFF toggle  → sets rsi_strategy_status ON / OFF
  4. SAVE button    → pushes qty + RSI bounds into strategy (in-memory)
  5. EXIT button    → Manual_EXIT = True + force_strategy_off()
  6. sync_strategy_state (every cycle):
       → detects backend-driven OFF (e.g. after check_manual_exit)
       → updates trade grid row with open position
       → clears row when position closes

Usage
─────
  from trading_panel import TradingFrame
  frame = TradingFrame(
      parent       = None,
      broker       = my_broker,
      data_manager = my_dm,
      rsi_strategy = RSIStrategy(),
      rsi_logic    = MyRSILogic(),
      loop         = asyncio_event_loop,
  )
  frame.Show()
"""

import wx
import asyncio
import inspect
import datetime
import logging

from static.loveable_ai_light_ui import (
    TradingDashboard,
    COLOR_SUCCESS, COLOR_DANGER,
    COLOR_WARNING, TEXT_MUTED, TEXT_BLACK,
)


# ════════════════════════════════════════════════════════════════
#  Logging helper  (same style as RSI_Strategy.py)
# ════════════════════════════════════════════════════════════════
def print_log(*args):
    try:
        caller_name = inspect.currentframe().f_back.f_code.co_name
    except (AttributeError, TypeError):
        caller_name = "unknown"
    message_str = '[TP] ' + f'\033[94m[{caller_name}]\033[0m ' + ' '.join(map(str, args))
    print(message_str)
    logging.info(message_str)


# ════════════════════════════════════════════════════════════════
#  TradingFrame
# ════════════════════════════════════════════════════════════════
class TradingFrame(TradingDashboard):
    """
    Inherits TradingDashboard (all UI widgets already built by parent).
    This class only adds behaviour — event handlers, async worker,
    and state-sync between RSIStrategy and the UI labels.

    Parameters
    ----------
    parent       : wx.Window | None
    broker       : object with .tradingsymbol dict and .get_ltp(token)
    data_manager : object with .INSTRUMENT_TOKEN attribute
    rsi_strategy : RSIStrategy instance
    rsi_logic    : object with async .get_RSI() coroutine
    loop         : running asyncio event loop (from the broker thread)
    """

    def __init__(self, parent, broker, data_manager, rsi_strategy, rsi_logic, loop):

        super().__init__(parent)

        # ── safety guard — stops wx.CallAfter after window closes ─
        self._is_alive = True

        # ── injected dependencies ─────────────────────────────────
        self.broker       = broker
        self.data_manager = data_manager
        self.rsi_strategy = rsi_strategy
        self.rsi_logic    = rsi_logic
        self.loop         = loop

        # ── internal flags ────────────────────────────────────────
        self.worker_started = False   # strategy_worker launched once per session

        # ── pre-fill RSI defaults from strategy object ────────────
        self.rsi_upper_input.SetValue(str(self.rsi_strategy.rsi_15min_upper))
        self.rsi_lower_input.SetValue(str(self.rsi_strategy.rsi_15min_lower))

        # ── allow ENTER key on symbol field ──────────────────────
        self.instrument_name.SetWindowStyleFlag(wx.TE_PROCESS_ENTER)

        # ── bind all UI events ────────────────────────────────────
        self.instrument_name.Bind(wx.EVT_TEXT_ENTER,    self.on_symbol_enter)
        self.instrument_name.Bind(wx.EVT_KILL_FOCUS,    self.on_symbol_enter)
        self.save_btn.Bind(wx.EVT_BUTTON,               self.on_save)
        self.on_off_btn.Bind(wx.EVT_TOGGLEBUTTON,       self.toggle_strategy)
        self.exit_btn.Bind(wx.EVT_BUTTON,               self.on_exit_position)
        self.Bind(wx.EVT_CLOSE,                         self.on_close)

        print_log("UI Ready")

    # ════════════════════════════════════════════════════════════
    #  Symbol resolution  —  ENTER key / TAB / focus-leave
    # ════════════════════════════════════════════════════════════

    def on_symbol_enter(self, event):
        """
        Resolves symbol → instrument token → fetches LTP.
        Launches strategy_worker coroutine on first valid symbol.
        """
        symbol = self.instrument_name.GetValue().strip().upper()

        if not symbol:
            event.Skip()
            return

        try:
            token = self.broker.tradingsymbol[symbol]["instrument_token"]
            ltp   = self.broker.get_ltp(token)

            # ── push token into data pipeline + strategy ──────────
            self.data_manager.INSTRUMENT_TOKEN = token
            self.rsi_strategy.INSTRUMENT_TOKEN = token
            self.rsi_strategy.ltp              = ltp

            # ── update UI immediately with resolved LTP ───────────
            self.update_ltp(ltp)
            self.sym_val.SetLabel(symbol)

            # ── start async worker once ───────────────────────────
            if not self.worker_started:
                asyncio.run_coroutine_threadsafe(
                    self.strategy_worker(), self.loop
                )
                self.worker_started = True

        except KeyError:
            print_log("Symbol not found:", symbol)
            self.sym_val.SetLabel("NOT FOUND")

        except Exception as e:
            print_log("Symbol error:", e)

        event.Skip()

    # ════════════════════════════════════════════════════════════
    #  Async strategy worker  —  runs in the broker event loop
    # ════════════════════════════════════════════════════════════

    async def strategy_worker(self):
        """
        Infinite async loop:
          1. Fetch fresh RSI values via rsi_logic.get_RSI()
          2. Run strategy logic (entry / exit checks)
          3. Push results back to UI thread via wx.CallAfter (thread-safe)

        Runs every 1 second. Errors are caught and logged so the
        loop never dies silently.
        """
        while True:
            try:
                await self.rsi_logic.get_RSI()
                self.rsi_strategy.run_strategy()

                # ── only touch UI if window is still alive ────────
                if self._is_alive:
                    wx.CallAfter(self.update_rsi_display)
                    wx.CallAfter(self.sync_strategy_state)

            except Exception as e:
                print_log("Worker error:", e)

            await asyncio.sleep(1)

    # ════════════════════════════════════════════════════════════
    #  SAVE button  —  in-memory push to RSIStrategy
    # ════════════════════════════════════════════════════════════

    def on_save(self, event):
        """
        Reads qty + RSI bounds from input fields and pushes them
        directly into the strategy object (no file I/O needed here —
        broker already holds instrument config).
        """
        qty       = self.quantity_input.GetValue().strip()
        rsi_upper = self.rsi_upper_input.GetValue().strip()
        rsi_lower = self.rsi_lower_input.GetValue().strip()

        if not qty:
            print_log("Save ignored — quantity empty")
            return

        self.rsi_strategy.quantity        = int(qty)
        self.rsi_strategy.rsi_15min_upper = int(rsi_upper) if rsi_upper else self.rsi_strategy.rsi_15min_upper
        self.rsi_strategy.rsi_15min_lower = int(rsi_lower) if rsi_lower else self.rsi_strategy.rsi_15min_lower

        self.update_status_bar()
        self.set_last_action(f"Saved  qty:{qty}  RSI:{rsi_lower}–{rsi_upper}")
        print_log(f"Saved — qty:{qty}  RSI:{rsi_lower}–{rsi_upper}")

    # ════════════════════════════════════════════════════════════
    #  ON/OFF toggle
    # ════════════════════════════════════════════════════════════

    def toggle_strategy(self, event):
        """
        Flips rsi_strategy_status ON/OFF and manages the
        pulse animation on the status label.
        """
        if self.on_off_btn.GetValue():
            # ── Strategy ON ──────────────────────────────────────
            self.rsi_strategy.rsi_strategy_status = "ON"
            self.on_off_btn._update()               # repaint button green
            self.status_val.SetLabel("● ON")
            self.status_val.SetForegroundColour(COLOR_SUCCESS)
            self.status_val.Refresh()
            self._status_pulse_step = 0
            self._status_pulse_dir  = 1
            self.pulse_timer.Start(80)
            self.set_last_action("Strategy ON")
            print_log("Strategy ON")

        else:
            # ── Strategy OFF ─────────────────────────────────────
            self.rsi_strategy.rsi_strategy_status = "OFF"
            self.force_strategy_off()               # resets button + pulse
            self.set_last_action("Strategy OFF")
            print_log("Strategy OFF")

    # ════════════════════════════════════════════════════════════
    #  sync_strategy_state  —  called every worker cycle
    # ════════════════════════════════════════════════════════════

    def sync_strategy_state(self):
        """
        Polls RSIStrategy state after each run_strategy() call.

        Handles two scenarios:
          A) Backend turned strategy OFF  (check_manual_exit resets
             rsi_strategy_status to "OFF") — UI must follow.
          B) Active position exists       — trade grid shows it.
             Position closed              — trade grid row cleared.
        """
        backend_status = self.rsi_strategy.rsi_strategy_status   # "ON" / "OFF"
        ui_is_on       = self.on_off_btn.GetValue()               # True / False

        # ── A: backend drove strategy to OFF without UI knowing ──
        if backend_status == "OFF" and ui_is_on:
            self.force_strategy_off()
            self.set_last_action("Strategy OFF")
            print_log("UI synced: strategy went OFF from backend")

        # ── B: active position → show in trade grid ──────────────
        if self.rsi_strategy.status == "active":
            trades = [{
                "transaction" : self.rsi_strategy.position or "—",
                "qty"         : str(self.rsi_strategy.quantity),
                "avg"         : f"{self.rsi_strategy.AVG:.2f}",
                "ltp"         : f"{self.rsi_strategy.ltp:.2f}",
                "status"      : "OPEN",
            }]
            self.update_trade_grid(trades)

            # update last action only once at entry (not every cycle)
            current_action = (
                f"{self.rsi_strategy.position} ENTRY ")
            if self.action_val.GetLabel() != current_action:
                self.set_last_action(current_action)

        elif self.rsi_strategy.status == "inactive":
            # clear the grid row when position is closed
            self._clear_trade_row(0)

            # mark "Position CLOSED" only after an actual trade
            if self.action_val.GetLabel() not in (
                "Strategy OFF", "Strategy ON",
                "Manual EXIT",  "No Position",
                "Position CLOSED", "—",
            ):
                self.set_last_action("Position CLOSED")

    # ════════════════════════════════════════════════════════════
    #  update_rsi_display  —  push indicator values to UI labels
    # ════════════════════════════════════════════════════════════

    def update_rsi_display(self):
        """
        Copies RSI / MA / LTP values from rsi_strategy into the
        Live Market Data panel. Called via wx.CallAfter from worker.
        """
        rsi15  = self.rsi_strategy.rsi_15min
        rsi1h  = self.rsi_strategy.rsi_1hr
        rsi_ma = self.rsi_strategy.rsi_ma_1hr
        ltp    = self.rsi_strategy.ltp

        if rsi15 is not None:
            self.rsi_15_value.SetLabel(f"{rsi15:.2f}")

        if rsi1h is not None:
            self.rsi_1h_value.SetLabel(f"{rsi1h:.2f}")

        if rsi_ma is not None:
            self.ma_1h_value.SetLabel(f"{rsi_ma:.2f}")

        if ltp:
            self.update_ltp(ltp)   # animated green/red flash

        self.update_val.SetLabel(datetime.datetime.now().strftime("%H:%M"))

    # ════════════════════════════════════════════════════════════
    #  update_status_bar  —  push config values to Status section
    # ════════════════════════════════════════════════════════════

    def update_status_bar(self):
        """Syncs Symbol / Qty / RSI Range labels from input fields."""
        qty     = self.quantity_input.GetValue().strip()
        rsi_up  = self.rsi_upper_input.GetValue().strip()
        rsi_low = self.rsi_lower_input.GetValue().strip()
        symbol  = self.instrument_name.GetValue().strip().upper()

        if symbol:
            self.sym_val.SetLabel(symbol)
        if qty:
            self.qty_val.SetLabel(qty)
        if rsi_up and rsi_low:
            self.rsi_range_val.SetLabel(f"{rsi_low} – {rsi_up}")

    # ════════════════════════════════════════════════════════════
    #  update_trade_grid  —  write trade data into grid rows
    # ════════════════════════════════════════════════════════════

    def update_trade_grid(self, trades: list):
        """
        Writes a list of trade dicts into the grid.
        Each dict: {transaction, qty, avg, ltp, status}

        Grid columns (from loveable_ai_light_ui):
          0=Transaction  1=QTY  2=AVG  3=LTP  4=Status
        """
        for r, trade in enumerate(trades):
            if r >= self.trade_grid.GetNumberRows():
                break

            self.trade_grid.SetCellValue(r, 0, trade.get("transaction", ""))
            self.trade_grid.SetCellValue(r, 1, trade.get("qty",         ""))
            self.trade_grid.SetCellValue(r, 2, trade.get("avg",         ""))
            self.trade_grid.SetCellValue(r, 3, trade.get("ltp",         ""))
            self.trade_grid.SetCellValue(r, 4, trade.get("status",      ""))

            txn    = trade.get("transaction", "")
            status = trade.get("status",      "")

            # LONG = green, SHORT = red
            self.trade_grid.SetCellTextColour(
                r, 0, COLOR_SUCCESS if txn == "LONG" else COLOR_DANGER
            )
            # OPEN = amber, CLOSED = muted grey
            self.trade_grid.SetCellTextColour(
                r, 4, COLOR_WARNING if status == "OPEN" else TEXT_MUTED
            )

        self.trade_grid.Refresh()

    # ════════════════════════════════════════════════════════════
    #  _clear_trade_row  —  reset a single grid row to blank
    # ════════════════════════════════════════════════════════════

    def _clear_trade_row(self, row: int):
        """Clears text and colour from a grid row when position closes."""
        if row >= self.trade_grid.GetNumberRows():
            return
        for col in range(self.trade_grid.GetNumberCols()):
            self.trade_grid.SetCellValue(row, col, "")
            self.trade_grid.SetCellTextColour(row, col, TEXT_BLACK)
        self.trade_grid.Refresh()

    # ════════════════════════════════════════════════════════════
    #  set_last_action  —  tiny helper to update action label
    # ════════════════════════════════════════════════════════════

    def set_last_action(self, action: str):
        """Updates the 'Last Action' label in the System Status bar."""
        self.action_val.SetLabel(action)
        self.action_val.Refresh()

    # ════════════════════════════════════════════════════════════
    #  EXIT button  —  manual position exit
    # ════════════════════════════════════════════════════════════

    def on_exit_position(self, event):
        """
        Sets Manual_EXIT flag on strategy and immediately resets the UI.
        The strategy_worker will process check_manual_exit() on next cycle.
        """
        print_log("Manual exit triggered")

        if self.rsi_strategy.status != "active":
            print_log("No active position — EXIT ignored")
            self.set_last_action("No Position")
            return

        self.rsi_strategy.Manual_EXIT         = True
        self.rsi_strategy.rsi_strategy_status = "OFF"
        self.force_strategy_off()
        self.set_last_action("Manual EXIT")
        print_log("Manual EXIT flag set — backend will process next cycle")

    # ════════════════════════════════════════════════════════════
    #  Window close  —  clean async shutdown
    # ════════════════════════════════════════════════════════════

    def on_close(self, event):
        """
        Stops all wx.CallAfter callbacks instantly via _is_alive guard,
        then shuts down the asyncio event loop gracefully.
        """
        print_log("Closing app")

        # stop wx.CallAfter from touching widgets after destroy
        self._is_alive = False

        try:
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass

        self.Destroy()