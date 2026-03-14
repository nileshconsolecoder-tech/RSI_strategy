# -*- coding: utf-8 -*-
"""
Professional Algorithmic Trading Dashboard — Clean Light Theme
Bold black text, white panels, high contrast
"""

import wx
import wx.grid
import gettext

_ = gettext.gettext

# ─── Color Constants ───
BG_MAIN = wx.Colour(235, 238, 245)       # Soft blue-grey background
BG_PANEL = wx.Colour(255, 255, 255)      # Pure white panels
BG_INPUT = wx.Colour(245, 247, 250)      # Light grey inputs
BG_INPUT_BORDER = wx.Colour(200, 205, 215)
TEXT_BLACK = wx.Colour(10, 10, 10)        # Near-black for all primary text
TEXT_LABEL = wx.Colour(40, 42, 50)        # Dark grey for labels
TEXT_MUTED = wx.Colour(120, 125, 135)     # Muted for secondary info
COLOR_SUCCESS = wx.Colour(22, 163, 120)   # Teal green
COLOR_DANGER = wx.Colour(220, 53, 69)    # Clean red
COLOR_ACCENT = wx.Colour(41, 98, 195)    # Deep blue
COLOR_WARNING = wx.Colour(210, 145, 0)   # Amber
GRID_LINE = wx.Colour(215, 218, 225)
TITLE_BG = wx.Colour(41, 98, 195)        # Blue header
TITLE_FG = wx.Colour(255, 255, 255)


def font_label(size=10, bold=True):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    f = wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, weight)
    f.SetFaceName("Segoe UI")
    return f

def font_mono(size=11, bold=True):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    f = wx.Font(size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, weight)
    f.SetFaceName("Consolas")
    return f

def font_title(size=13):
    f = wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    f.SetFaceName("Segoe UI")
    return f


class DarkLabel(wx.StaticText):
    """Bold black label."""
    def __init__(self, parent, text, size=10, color=TEXT_LABEL, bold=True):
        super().__init__(parent, label=text)
        self.SetForegroundColour(color)
        self.SetFont(font_label(size, bold))


class DataValue(wx.StaticText):
    """Bold black monospace value."""
    def __init__(self, parent, text="0.00", size=11, color=TEXT_BLACK, bold=True):
        super().__init__(parent, label=text)
        self.SetForegroundColour(color)
        self.SetFont(font_mono(size, bold))


class StyledTextCtrl(wx.TextCtrl):
    def __init__(self, parent, value="", size=wx.DefaultSize):
        super().__init__(parent, value=value, size=size, style=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(BG_INPUT)
        self.SetForegroundColour(TEXT_BLACK)
        self.SetFont(font_mono(10, bold=True))


class StyledButton(wx.Button):
    def __init__(self, parent, label, bg_color, fg_color=TITLE_FG, size=wx.DefaultSize):
        super().__init__(parent, label=label, size=size)
        self.bg_color = bg_color
        self.SetBackgroundColour(bg_color)
        self.SetForegroundColour(fg_color)
        self.SetFont(font_label(10, bold=True))
        self.Bind(wx.EVT_ENTER_WINDOW, self._hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._leave)

    def _hover(self, e):
        r, g, b = [max(c - 25, 0) for c in (self.bg_color.Red(), self.bg_color.Green(), self.bg_color.Blue())]
        self.SetBackgroundColour(wx.Colour(r, g, b))
        self.Refresh()

    def _leave(self, e):
        self.SetBackgroundColour(self.bg_color)
        self.Refresh()


class StyledToggleButton(wx.ToggleButton):
    def __init__(self, parent, size=wx.DefaultSize):
        super().__init__(parent, label="OFF", size=size)
        self.SetFont(font_label(10, bold=True))
        self._update()
        # self.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle)

    def _on_toggle(self, e):
        self._update()
        e.Skip()  

    def _update(self):
        if self.GetValue():
            self.SetLabel("● ON")
            self.SetBackgroundColour(COLOR_SUCCESS)
            self.SetForegroundColour(wx.Colour(255, 255, 255))
        else:
            self.SetLabel("○ OFF")
            self.SetBackgroundColour(wx.Colour(195, 200, 210))
            self.SetForegroundColour(TEXT_BLACK)
        self.Refresh()


class SectionPanel(wx.Panel):
    """White rounded-feel panel with title."""
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.SetBackgroundColour(BG_PANEL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        if title:
            title_lbl = wx.StaticText(self, label=f"  {title}")
            title_lbl.SetFont(font_title(11))
            title_lbl.SetForegroundColour(COLOR_ACCENT)
            self.main_sizer.Add(title_lbl, 0, wx.TOP | wx.LEFT, 12)
            line = wx.StaticLine(self)
            self.main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.content_sizer, 1, wx.EXPAND | wx.ALL, 12)
        self.SetSizer(self.main_sizer)


class TradingDashboard(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent, title="⚡ Algo Trading Dashboard",
            size=wx.Size(800, 620),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )
        self.SetSizeHints(wx.Size(720, 550), wx.DefaultSize)
        self.SetBackgroundColour(BG_MAIN)

        self._ltp_prev = 0.0
        self._ltp_flash_step = 0
        self._ltp_flash_color = None
        self._status_pulse_step = 0
        self._status_pulse_dir = 1

        main = wx.BoxSizer(wx.VERTICAL)

        # ═══ TITLE BAR ═══
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(TITLE_BG)
        ts = wx.BoxSizer(wx.HORIZONTAL)
        tl = wx.StaticText(title_panel, label="  ⚡ ALGO TRADING DASHBOARD")
        tl.SetFont(font_title(15))
        tl.SetForegroundColour(TITLE_FG)
        ts.Add(tl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        ts.AddStretchSpacer()
        self.clock_label = wx.StaticText(title_panel, label="--:--:--  ")
        self.clock_label.SetFont(font_mono(11, bold=True))
        self.clock_label.SetForegroundColour(wx.Colour(200, 220, 255))
        ts.Add(self.clock_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        title_panel.SetSizer(ts)
        main.Add(title_panel, 0, wx.EXPAND)

        # ═══ TOP ROW: Config + Market Data ═══
        top = wx.BoxSizer(wx.HORIZONTAL)

        # ─── Configuration ───
        cfg = SectionPanel(self, "⚙  Configuration")
        grid = wx.FlexGridSizer(4, 2, 10, 15)

        self.instrument_name = self._add_input_row(cfg, grid, "Symbol")
        self.quantity_input = self._add_input_row(cfg, grid, "Quantity")
        self.rsi_upper_input = self._add_input_row(cfg, grid, "RSI Upper Limit")
        self.rsi_lower_input = self._add_input_row(cfg, grid, "RSI Lower Limit")

        cfg.content_sizer.Add(grid, 0, wx.BOTTOM, 12)

        btns = wx.BoxSizer(wx.HORIZONTAL)
        self.save_btn = StyledButton(cfg, "💾  SAVE", COLOR_SUCCESS, TITLE_FG, size=(110, 36))
        self.on_off_btn = StyledToggleButton(cfg, size=(90, 36))
        btns.Add(self.save_btn, 0, wx.RIGHT, 12)
        btns.Add(self.on_off_btn, 0)
        cfg.content_sizer.Add(btns, 0)

        top.Add(cfg, 1, wx.ALL | wx.EXPAND, 6)

        # ─── Live Market Data ───
        mkt = SectionPanel(self, "📊  Live Market Data")
        mg = wx.FlexGridSizer(4, 2, 12, 30)

        self.ltp_value = self._add_data_row(mkt, mg, "LTP", "0.00", size=16)
        self.rsi_15_value = self._add_data_row(mkt, mg, "RSI (15 min)", "0.00")
        self.rsi_1h_value = self._add_data_row(mkt, mg, "RSI (1 hr)", "0.00")
        self.ma_1h_value = self._add_data_row(mkt, mg, "MA (1 hr)", "0.00")

        mkt.content_sizer.Add(mg, 0)
        top.Add(mkt, 1, wx.ALL | wx.EXPAND, 6)

        main.Add(top, 0, wx.EXPAND | wx.TOP, 4)

        # ═══ SYSTEM STATUS ═══
        stat = SectionPanel(self, "🔔  System Status")
        sg = wx.FlexGridSizer(2, 6, 8, 24)

        self.status_val = self._add_status_item(stat, sg, "Status", "OFF", TEXT_MUTED)
        self.action_val = self._add_status_item(stat, sg, "Last Action", "—")
        self.update_val = self._add_status_item(stat, sg, "Last Update", "00:00")
        self.sym_val = self._add_status_item(stat, sg, "Symbol", "None")
        self.qty_val = self._add_status_item(stat, sg, "Quantity", "0")
        self.rsi_range_val = self._add_status_item(stat, sg, "RSI Range", "0 – 0")

        stat.content_sizer.Add(sg, 0, wx.EXPAND)
        main.Add(stat, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 6)

        # ═══ TRADE LOG ═══
        log = SectionPanel(self, "📋  Trade Log")
        log_row = wx.BoxSizer(wx.HORIZONTAL)

        self.trade_grid = wx.grid.Grid(log)
        self.trade_grid.CreateGrid(5, 5)
        self.trade_grid.EnableEditing(False)
        self.trade_grid.SetGridLineColour(GRID_LINE)
        self.trade_grid.SetDefaultCellBackgroundColour(BG_PANEL)
        self.trade_grid.SetDefaultCellTextColour(TEXT_BLACK)
        self.trade_grid.SetDefaultCellFont(font_mono(10, bold=True))
        self.trade_grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.trade_grid.SetLabelBackgroundColour(wx.Colour(230, 235, 245))
        self.trade_grid.SetLabelTextColour(COLOR_ACCENT)
        self.trade_grid.SetLabelFont(font_label(9, bold=True))
        self.trade_grid.SetRowLabelSize(0)
        self.trade_grid.SetColLabelSize(32)

        for i, (lbl, w) in enumerate(zip(
            ["Transaction", "QTY", "AVG", "LTP", "Status"],
            [130, 75, 95, 95, 95]
        )):
            self.trade_grid.SetColLabelValue(i, lbl)
            self.trade_grid.SetColSize(i, w)

        for r, row in enumerate([
            ("BUY", "50", "1245.50", "1248.20", "OPEN"),
            ("SELL", "30", "1250.00", "1248.20", "CLOSED"),
        ]):
            for c, v in enumerate(row):
                self.trade_grid.SetCellValue(r, c, v)
            self.trade_grid.SetCellTextColour(r, 0, COLOR_SUCCESS if row[0] == "BUY" else COLOR_DANGER)
            self.trade_grid.SetCellTextColour(r, 4, COLOR_WARNING if row[4] == "OPEN" else TEXT_MUTED)

        log_row.Add(self.trade_grid, 1, wx.EXPAND | wx.ALL, 4)

        self.exit_btn = StyledButton(log, "✕  EXIT", COLOR_DANGER, TITLE_FG, size=(95, 42))
        # self.exit_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        log_row.Add(self.exit_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)

        log.content_sizer.Add(log_row, 1, wx.EXPAND)
        main.Add(log, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 6)

        self.SetSizer(main)
        self.Layout()
        self.Centre(wx.BOTH)

        # Timers
        self.clock_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._tick_clock, self.clock_timer)
        self.clock_timer.Start(1000)

        self.flash_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._tick_flash, self.flash_timer)

        self.pulse_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._tick_pulse, self.pulse_timer)

        # self.on_off_btn.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle)

    # ─── Helpers ───
    def _add_input_row(self, parent_panel, grid, label):
        lbl = DarkLabel(parent_panel, label, bold=True)
        ctrl = StyledTextCtrl(parent_panel, size=(145, -1))
        grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(ctrl, 0, wx.EXPAND)
        return ctrl

    def _add_data_row(self, parent_panel, grid, label, default, size=12):
        lbl = DarkLabel(parent_panel, label, size=10, color=TEXT_LABEL, bold=True)
        val = DataValue(parent_panel, default, size=size, color=TEXT_BLACK, bold=True)
        grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(val, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        return val

    def _add_status_item(self, parent_panel, grid, label, default, color=TEXT_BLACK):
        lbl = DarkLabel(parent_panel, label + ":", size=9, color=TEXT_MUTED, bold=True)
        val = DataValue(parent_panel, default, size=10, color=color, bold=True)
        grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(val, 0, wx.ALIGN_CENTER_VERTICAL)
        return val

    # ─── Clock ───
    def _tick_clock(self, e):
        import datetime
        self.clock_label.SetLabel(f"  {datetime.datetime.now().strftime('%H:%M:%S')}  ")

    # ─── LTP Flash ───
    def update_ltp(self, new_value):
        old = self._ltp_prev
        self._ltp_prev = new_value
        self.ltp_value.SetLabel(f"{new_value:.2f}")
        if new_value > old:
            self._ltp_flash_color = COLOR_SUCCESS
        elif new_value < old:
            self._ltp_flash_color = COLOR_DANGER
        else:
            return
        self._ltp_flash_step = 6
        self.ltp_value.SetForegroundColour(self._ltp_flash_color)
        self.ltp_value.Refresh()
        self.flash_timer.Start(80)

    def _tick_flash(self, e):
        if self._ltp_flash_step <= 0:
            self.flash_timer.Stop()
            self.ltp_value.SetForegroundColour(TEXT_BLACK)
            self.ltp_value.Refresh()
            return
        self._ltp_flash_step -= 1
        fc = self._ltp_flash_color
        t = self._ltp_flash_step / 6.0
        r = int(fc.Red() * t + TEXT_BLACK.Red() * (1 - t))
        g = int(fc.Green() * t + TEXT_BLACK.Green() * (1 - t))
        b = int(fc.Blue() * t + TEXT_BLACK.Blue() * (1 - t))
        self.ltp_value.SetForegroundColour(wx.Colour(r, g, b))
        self.ltp_value.Refresh()

    # ─── Status Pulse ───
    def _on_toggle(self, e):
        # on_off_btn already updated visuals via its own bind
        # just handle pulse timer here
        if self.on_off_btn.GetValue():
            self.status_val.SetLabel("● ON")
            self.status_val.SetForegroundColour(COLOR_SUCCESS)
            self._status_pulse_step = 0
            self._status_pulse_dir = 1
            self.pulse_timer.Start(80)
        else:
            self.pulse_timer.Stop()
            self.status_val.SetLabel("○ OFF")
            self.status_val.SetForegroundColour(TEXT_MUTED)
        self.status_val.Refresh()
        e.Skip()  

    def _tick_pulse(self, e):
        self._status_pulse_step += self._status_pulse_dir
        if self._status_pulse_step >= 10:
            self._status_pulse_dir = -1
        elif self._status_pulse_step <= 0:
            self._status_pulse_dir = 1
        t = self._status_pulse_step / 10.0
        r = int(COLOR_SUCCESS.Red() * t + 160 * (1 - t))
        g = int(COLOR_SUCCESS.Green() * t + 170 * (1 - t))
        b = int(COLOR_SUCCESS.Blue() * t + 160 * (1 - t))
        self.status_val.SetForegroundColour(wx.Colour(r, g, b))
        self.status_val.Refresh()
        
    def force_strategy_off(self):
        """
        Programmatically stop strategy with full visual reset.
        Safe to call from TradingFrame for EXIT or backend-driven OFF.
        """
        self.pulse_timer.Stop()
        self.on_off_btn.SetValue(False)
        self.on_off_btn._update()
        self.status_val.SetLabel("○ OFF")
        self.status_val.SetForegroundColour(TEXT_MUTED)
        self.status_val.Refresh()


class TradingApp(wx.App):
    def OnInit(self):
        frame = TradingDashboard(None)
        frame.Show()
        self._timer = wx.Timer(frame)
        frame.Bind(wx.EVT_TIMER, self._demo, self._timer)
        self._timer.Start(2000)
        self._frame = frame
        self._val = 1245.50
        return True

    def _demo(self, e):
        import random
        self._val += random.uniform(-3.0, 3.5)
        self._frame.update_ltp(self._val)


if __name__ == "__main__":
    app = TradingApp()
    app.MainLoop()
