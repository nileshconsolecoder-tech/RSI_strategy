# -*- coding: utf-8 -*-
"""
Professional Algorithmic Trading Dashboard
Dark themed wxPython UI with animations
"""

import wx
import wx.grid
import gettext

_ = gettext.gettext

# ─── Color Constants ───
BG_DARK = wx.Colour(30, 30, 36)
BG_PANEL = wx.Colour(43, 43, 54)
BG_INPUT = wx.Colour(55, 55, 68)
TEXT_PRIMARY = wx.Colour(248, 249, 250)
TEXT_SECONDARY = wx.Colour(173, 181, 189)
TEXT_MUTED = wx.Colour(108, 117, 125)
COLOR_SUCCESS = wx.Colour(32, 201, 151)
COLOR_DANGER = wx.Colour(250, 82, 82)
COLOR_ACCENT = wx.Colour(74, 144, 226)
COLOR_WARNING = wx.Colour(255, 193, 7)
GRID_LINE = wx.Colour(60, 60, 75)
BORDER_COLOR = wx.Colour(55, 55, 70)

# ─── Fonts ───
def get_label_font(size=10, bold=False):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    return wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, weight)

def get_mono_font(size=11, bold=False):
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    f = wx.Font(size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, weight)
    f.SetFaceName("Consolas")
    return f

def get_title_font(size=11):
    return wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)


class StyledStaticBox(wx.StaticBox):
    """A dark-themed static box for grouping controls."""
    def __init__(self, parent, label=""):
        super().__init__(parent, label=label)
        self.SetForegroundColour(COLOR_ACCENT)
        self.SetFont(get_title_font(10))


class StyledTextCtrl(wx.TextCtrl):
    """Dark-themed text input."""
    def __init__(self, parent, value="", size=wx.DefaultSize):
        super().__init__(parent, value=value, size=size)
        self.SetBackgroundColour(BG_INPUT)
        self.SetForegroundColour(TEXT_PRIMARY)
        self.SetFont(get_mono_font(10))


class StyledButton(wx.Button):
    """Custom styled button with hover effects."""
    def __init__(self, parent, label, bg_color, fg_color=TEXT_PRIMARY, size=wx.DefaultSize):
        super().__init__(parent, label=label, size=size)
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.SetBackgroundColour(bg_color)
        self.SetForegroundColour(fg_color)
        self.SetFont(get_label_font(10, bold=True))
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)

    def _on_hover(self, event):
        r = min(self.bg_color.Red() + 25, 255)
        g = min(self.bg_color.Green() + 25, 255)
        b = min(self.bg_color.Blue() + 25, 255)
        self.SetBackgroundColour(wx.Colour(r, g, b))
        self.Refresh()

    def _on_leave(self, event):
        self.SetBackgroundColour(self.bg_color)
        self.Refresh()


class StyledToggleButton(wx.ToggleButton):
    """Toggle button that changes color based on state."""
    def __init__(self, parent, label="OFF", size=wx.DefaultSize):
        super().__init__(parent, label=label, size=size)
        self.SetFont(get_label_font(10, bold=True))
        self._update_style()
        self.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle)

    def _on_toggle(self, event):
        self._update_style()

    def _update_style(self):
        if self.GetValue():
            self.SetLabel("ON")
            self.SetBackgroundColour(COLOR_SUCCESS)
            self.SetForegroundColour(wx.Colour(10, 10, 10))
        else:
            self.SetLabel("OFF")
            self.SetBackgroundColour(wx.Colour(80, 80, 95))
            self.SetForegroundColour(TEXT_PRIMARY)
        self.Refresh()


class TradingDashboard(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent, id=wx.ID_ANY,
            title="⚡ Algo Trading Dashboard",
            pos=wx.DefaultPosition,
            size=wx.Size(780, 580),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.Size(700, 500), wx.DefaultSize)
        self.SetBackgroundColour(BG_DARK)

        # Animation state
        self._ltp_prev = 0.0
        self._ltp_flash_step = 0
        self._ltp_flash_color = None
        self._status_pulse_step = 0
        self._status_pulse_dir = 1  # 1 = brightening, -1 = dimming

        # ─── Main Layout ───
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title bar
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(BG_PANEL)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_label = wx.StaticText(title_panel, label="  ALGO TRADING DASHBOARD")
        title_label.SetFont(get_title_font(14))
        title_label.SetForegroundColour(TEXT_PRIMARY)
        title_sizer.Add(title_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        title_sizer.AddStretchSpacer()
        self.clock_label = wx.StaticText(title_panel, label="--:--:--  ")
        self.clock_label.SetFont(get_mono_font(10))
        self.clock_label.SetForegroundColour(TEXT_SECONDARY)
        title_sizer.Add(self.clock_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        title_panel.SetSizer(title_sizer)
        main_sizer.Add(title_panel, 0, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        # Top row: Configuration + Live Market Data
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # ─── Configuration Panel ───
        config_box = StyledStaticBox(self, " ⚙  Configuration ")
        config_sizer = wx.StaticBoxSizer(config_box, wx.VERTICAL)
        config_grid = wx.FlexGridSizer(4, 2, 8, 12)

        lbl_symbol = wx.StaticText(self, label="Symbol")
        lbl_symbol.SetForegroundColour(TEXT_SECONDARY)
        lbl_symbol.SetFont(get_label_font(10))
        self.instrument_name = StyledTextCtrl(self, size=(140, -1))

        lbl_qty = wx.StaticText(self, label="Quantity")
        lbl_qty.SetForegroundColour(TEXT_SECONDARY)
        lbl_qty.SetFont(get_label_font(10))
        self.quantity_input = StyledTextCtrl(self, size=(140, -1))

        lbl_rsi_upper = wx.StaticText(self, label="RSI Upper Limit")
        lbl_rsi_upper.SetForegroundColour(TEXT_SECONDARY)
        lbl_rsi_upper.SetFont(get_label_font(10))
        self.rsi_upper_limit_input = StyledTextCtrl(self, size=(140, -1))

        lbl_rsi_lower = wx.StaticText(self, label="RSI Lower Limit")
        lbl_rsi_lower.SetForegroundColour(TEXT_SECONDARY)
        lbl_rsi_lower.SetFont(get_label_font(10))
        self.rsi_lower_limit_input = StyledTextCtrl(self, size=(140, -1))

        for lbl, ctrl in [
            (lbl_symbol, self.instrument_name),
            (lbl_qty, self.quantity_input),
            (lbl_rsi_upper, self.rsi_upper_limit_input),
            (lbl_rsi_lower, self.rsi_lower_limit_input),
        ]:
            config_grid.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            config_grid.Add(ctrl, 0, wx.EXPAND)

        config_sizer.Add(config_grid, 0, wx.ALL, 10)

        # Buttons row
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_btn = StyledButton(self, "💾  SAVE", COLOR_SUCCESS, wx.Colour(10, 10, 10), size=(100, 34))
        self.on_off_btn = StyledToggleButton(self, size=(80, 34))
        btn_sizer.Add(self.save_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.on_off_btn, 0)
        config_sizer.Add(btn_sizer, 0, wx.LEFT | wx.BOTTOM, 10)

        top_sizer.Add(config_sizer, 1, wx.ALL | wx.EXPAND, 8)

        # ─── Live Market Data Panel ───
        market_box = StyledStaticBox(self, " 📊  Live Market Data ")
        market_sizer = wx.StaticBoxSizer(market_box, wx.VERTICAL)
        market_grid = wx.FlexGridSizer(4, 2, 10, 20)

        self.ltp_value = self._make_data_row(market_grid, "LTP", "0.00", bold=True, large=True)
        self.rsi_15_value = self._make_data_row(market_grid, "RSI (15 min)", "0.00")
        self.rsi_1h_value = self._make_data_row(market_grid, "RSI (1 hr)", "0.00")
        self.ma_1h_value = self._make_data_row(market_grid, "MA (1 hr)", "0.00")

        market_sizer.Add(market_grid, 0, wx.ALL, 12)
        top_sizer.Add(market_sizer, 1, wx.ALL | wx.EXPAND, 8)

        main_sizer.Add(top_sizer, 0, wx.EXPAND)

        # ─── System Status Panel ───
        status_box = StyledStaticBox(self, " 🔔  System Status ")
        status_sizer = wx.StaticBoxSizer(status_box, wx.VERTICAL)
        status_grid = wx.FlexGridSizer(2, 6, 6, 20)

        self.software_status_val = self._make_status_item(status_grid, "Status", "OFF", TEXT_MUTED)
        self.last_action_val = self._make_status_item(status_grid, "Last Action", "—", TEXT_SECONDARY)
        self.last_update_val = self._make_status_item(status_grid, "Last Update", "00:00", TEXT_SECONDARY)

        self.config_symbol_val = self._make_status_item(status_grid, "Symbol", "None", TEXT_SECONDARY)
        self.config_qty_val = self._make_status_item(status_grid, "Quantity", "0", TEXT_SECONDARY)
        self.config_rsi_val = self._make_status_item(status_grid, "RSI Range", "0 – 0", TEXT_SECONDARY)

        status_sizer.Add(status_grid, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(status_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        # ─── Trade Grid Panel ───
        grid_box = StyledStaticBox(self, " 📋  Trade Log ")
        grid_sizer = wx.StaticBoxSizer(grid_box, wx.VERTICAL)

        grid_and_btn = wx.BoxSizer(wx.HORIZONTAL)

        self.trade_grid = wx.grid.Grid(self)
        self.trade_grid.CreateGrid(5, 5)
        self.trade_grid.EnableEditing(False)
        self.trade_grid.EnableGridLines(True)
        self.trade_grid.SetGridLineColour(GRID_LINE)
        self.trade_grid.SetDefaultCellBackgroundColour(BG_PANEL)
        self.trade_grid.SetDefaultCellTextColour(TEXT_PRIMARY)
        self.trade_grid.SetDefaultCellFont(get_mono_font(10))
        self.trade_grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.trade_grid.SetLabelBackgroundColour(wx.Colour(38, 38, 50))
        self.trade_grid.SetLabelTextColour(COLOR_ACCENT)
        self.trade_grid.SetLabelFont(get_label_font(9, bold=True))
        self.trade_grid.SetRowLabelSize(0)
        self.trade_grid.SetColLabelSize(30)

        col_labels = ["Transaction", "QTY", "AVG", "LTP", "Status"]
        col_widths = [120, 70, 90, 90, 90]
        for i, (label, width) in enumerate(zip(col_labels, col_widths)):
            self.trade_grid.SetColLabelValue(i, label)
            self.trade_grid.SetColSize(i, width)

        # Sample data
        sample = [
            ("BUY", "50", "1245.50", "1248.20", "OPEN"),
            ("SELL", "30", "1250.00", "1248.20", "CLOSED"),
        ]
        for r, row in enumerate(sample):
            for c, val in enumerate(row):
                self.trade_grid.SetCellValue(r, c, val)
            if row[0] == "BUY":
                self.trade_grid.SetCellTextColour(r, 0, COLOR_SUCCESS)
            else:
                self.trade_grid.SetCellTextColour(r, 0, COLOR_DANGER)
            if row[4] == "OPEN":
                self.trade_grid.SetCellTextColour(r, 4, COLOR_WARNING)
            else:
                self.trade_grid.SetCellTextColour(r, 4, TEXT_MUTED)

        grid_and_btn.Add(self.trade_grid, 1, wx.EXPAND | wx.ALL, 5)

        # Exit button
        self.exit_btn = StyledButton(self, "✕  EXIT", COLOR_DANGER, TEXT_PRIMARY, size=(90, 40))
        self.exit_btn.Bind(wx.EVT_BUTTON, self._on_exit)
        grid_and_btn.Add(self.exit_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)

        grid_sizer.Add(grid_and_btn, 1, wx.EXPAND)
        main_sizer.Add(grid_sizer, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        self.SetSizer(main_sizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # ─── Timers ───
        self.clock_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_clock_tick, self.clock_timer)
        self.clock_timer.Start(1000)

        self.flash_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_flash_tick, self.flash_timer)

        self.pulse_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_pulse_tick, self.pulse_timer)

        # Bind toggle for status animation
        self.on_off_btn.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle_status)

    # ─── Helper: create label + value pair for data display ───
    def _make_data_row(self, grid_sizer, label_text, default_val, bold=False, large=False):
        lbl = wx.StaticText(self, label=label_text)
        lbl.SetForegroundColour(TEXT_SECONDARY)
        lbl.SetFont(get_label_font(10))

        font_size = 14 if large else 11
        val = wx.StaticText(self, label=default_val)
        val.SetForegroundColour(TEXT_PRIMARY)
        val.SetFont(get_mono_font(font_size, bold=bold))

        grid_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(val, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        return val

    def _make_status_item(self, grid_sizer, label_text, default_val, val_color):
        lbl = wx.StaticText(self, label=label_text + ":")
        lbl.SetForegroundColour(TEXT_MUTED)
        lbl.SetFont(get_label_font(9))

        val = wx.StaticText(self, label=default_val)
        val.SetForegroundColour(val_color)
        val.SetFont(get_mono_font(10, bold=True))

        grid_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(val, 0, wx.ALIGN_CENTER_VERTICAL)
        return val

    # ─── Clock ───
    def _on_clock_tick(self, event):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.SetLabel(f"  {now}  ")

    # ─── LTP Flash Animation ───
    def update_ltp(self, new_value):
        """Call this to update LTP — triggers color flash animation."""
        old = self._ltp_prev
        self._ltp_prev = new_value
        self.ltp_value.SetLabel(f"{new_value:.2f}")

        if new_value > old:
            self._ltp_flash_color = COLOR_SUCCESS
        elif new_value < old:
            self._ltp_flash_color = COLOR_DANGER
        else:
            return

        self._ltp_flash_step = 5
        self.ltp_value.SetForegroundColour(self._ltp_flash_color)
        self.ltp_value.Refresh()
        self.flash_timer.Start(100)

    def _on_flash_tick(self, event):
        if self._ltp_flash_step <= 0:
            self.flash_timer.Stop()
            self.ltp_value.SetForegroundColour(TEXT_PRIMARY)
            self.ltp_value.Refresh()
            return
        self._ltp_flash_step -= 1
        # Fade towards white
        fc = self._ltp_flash_color
        t = self._ltp_flash_step / 5.0
        r = int(fc.Red() * t + TEXT_PRIMARY.Red() * (1 - t))
        g = int(fc.Green() * t + TEXT_PRIMARY.Green() * (1 - t))
        b = int(fc.Blue() * t + TEXT_PRIMARY.Blue() * (1 - t))
        self.ltp_value.SetForegroundColour(wx.Colour(r, g, b))
        self.ltp_value.Refresh()

    # ─── Status Pulse Animation ───
    def _on_toggle_status(self, event):
        self.on_off_btn._on_toggle(event)
        if self.on_off_btn.GetValue():
            self.software_status_val.SetLabel("ON")
            self.software_status_val.SetForegroundColour(COLOR_SUCCESS)
            self._status_pulse_step = 0
            self._status_pulse_dir = 1
            self.pulse_timer.Start(80)
        else:
            self.pulse_timer.Stop()
            self.software_status_val.SetLabel("OFF")
            self.software_status_val.SetForegroundColour(TEXT_MUTED)
        self.software_status_val.Refresh()

    def _on_pulse_tick(self, event):
        self._status_pulse_step += self._status_pulse_dir
        if self._status_pulse_step >= 10:
            self._status_pulse_dir = -1
        elif self._status_pulse_step <= 0:
            self._status_pulse_dir = 1
        t = self._status_pulse_step / 10.0
        r = int(COLOR_SUCCESS.Red() * t + 80 * (1 - t))
        g = int(COLOR_SUCCESS.Green() * t + 100 * (1 - t))
        b = int(COLOR_SUCCESS.Blue() * t + 80 * (1 - t))
        self.software_status_val.SetForegroundColour(wx.Colour(r, g, b))
        self.software_status_val.Refresh()

    def _on_exit(self, event):
        self.Close()


class TradingApp(wx.App):
    def OnInit(self):
        frame = TradingDashboard(None)
        frame.Show()

        # Demo: simulate LTP updates
        self._demo_timer = wx.Timer(frame)
        frame.Bind(wx.EVT_TIMER, self._demo_ltp, self._demo_timer)
        self._demo_timer.Start(2000)
        self._demo_frame = frame
        self._demo_val = 1245.50
        return True

    def _demo_ltp(self, event):
        import random
        self._demo_val += random.uniform(-3.0, 3.5)
        self._demo_frame.update_ltp(self._demo_val)


if __name__ == "__main__":
    app = TradingApp()
    app.MainLoop()