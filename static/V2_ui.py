# -*- coding: utf-8 -*-

import wx
import wx.xrc
import wx.grid
import gettext

_ = gettext.gettext

# ========================
# Color Palette (Light Professional Theme)
# ========================

COLOR_BG_ROOT       = wx.Colour(245, 247, 250)      # Page background
COLOR_BG_CARD       = wx.Colour(255, 255, 255)      # Card surface
COLOR_BG_CARD2      = wx.Colour(240, 244, 250)      # Card header / input bg
COLOR_BG_INPUT      = wx.Colour(248, 250, 253)      # Input field bg
COLOR_BORDER        = wx.Colour(210, 220, 235)      # Border / divider
COLOR_BORDER_FOCUS  = wx.Colour(41, 128, 255)       # Focus ring

COLOR_ACCENT_BLUE   = wx.Colour(41, 128, 255)       # Primary blue
COLOR_ACCENT_GREEN  = wx.Colour(0, 175, 115)        # Bullish green
COLOR_ACCENT_RED    = wx.Colour(220, 53, 69)        # Bearish red
COLOR_ACCENT_AMBER  = wx.Colour(210, 135, 10)       # RSI / LTP gold

COLOR_TEXT_PRIMARY  = wx.Colour(18, 30, 48)         # Main dark text
COLOR_TEXT_SECONDARY= wx.Colour(80, 105, 140)       # Label / muted text
COLOR_TEXT_VALUE    = wx.Colour(10, 20, 40)         # Value display

COLOR_TITLE_BG      = wx.Colour(18, 40, 80)         # Dark navy title bar
COLOR_TITLE_TEXT    = wx.Colour(230, 240, 255)      # Title bar text

COLOR_TOGGLE_ON     = wx.Colour(0, 175, 115)
COLOR_TOGGLE_OFF    = wx.Colour(140, 160, 190)
COLOR_SAVE_BTN      = wx.Colour(41, 128, 255)
COLOR_EXIT_BTN      = wx.Colour(220, 53, 69)

COLOR_GRID_HEADER   = wx.Colour(230, 237, 248)
COLOR_GRID_ROW      = wx.Colour(255, 255, 255)
COLOR_GRID_LINE     = wx.Colour(210, 220, 235)


def make_bold_font(size=10):
    f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    f.SetPointSize(size)
    f.SetWeight(wx.FONTWEIGHT_BOLD)
    return f

def make_font(size=10):
    f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    f.SetPointSize(size)
    return f

def make_mono_font(size=12):
    f = wx.Font(size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    return f


class SectionPanel(wx.Panel):
    """Card panel with a colored header label strip."""
    def __init__(self, parent, title=""):
        super().__init__(parent, wx.ID_ANY)
        self.SetBackgroundColour(COLOR_BG_CARD)

        outer = wx.BoxSizer(wx.VERTICAL)

        if title:
            header = wx.Panel(self, wx.ID_ANY)
            header.SetBackgroundColour(COLOR_BG_CARD2)
            h_sizer = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(header, wx.ID_ANY, title.upper())
            lbl.SetForegroundColour(COLOR_TEXT_SECONDARY)
            lbl.SetFont(make_bold_font(8))
            h_sizer.Add(lbl, 0, wx.ALL, 7)
            header.SetSizer(h_sizer)
            outer.Add(header, 0, wx.EXPAND)

            # thin accent line under header
            div = wx.Panel(self, size=(-1, 1))
            div.SetBackgroundColour(COLOR_BORDER)
            outer.Add(div, 0, wx.EXPAND)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.content_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(outer)

    def GetContentSizer(self):
        return self.content_sizer


class ValueDisplay(wx.Panel):
    """Label + large monospace value widget."""
    def __init__(self, parent, label, value="00.00", accent=None):
        super().__init__(parent, wx.ID_ANY)
        self.SetBackgroundColour(COLOR_BG_CARD)
        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl = wx.StaticText(self, wx.ID_ANY, label)
        lbl.SetForegroundColour(COLOR_TEXT_SECONDARY)
        lbl.SetFont(make_font(8))

        self.val = wx.StaticText(self, wx.ID_ANY, value)
        self.val.SetForegroundColour(accent or COLOR_TEXT_VALUE)
        self.val.SetFont(make_mono_font(14))

        sizer.Add(lbl, 0)
        sizer.Add(self.val, 0, wx.TOP, 3)
        self.SetSizer(sizer)

    def SetValue(self, v):
        self.val.SetLabel(v)


class MyFrame1(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="RSI Strategy Panel",
            pos=wx.DefaultPosition,
            size=wx.Size(640, 480),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.Size(620, 460), wx.DefaultSize)
        self.SetBackgroundColour(COLOR_BG_ROOT)

        root = wx.BoxSizer(wx.VERTICAL)

        # ── Title Bar ──────────────────────────────────────────────────────
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(COLOR_TITLE_BG)
        title_panel.SetMinSize((-1, 44))
        t_sizer = wx.BoxSizer(wx.HORIZONTAL)

        dot = wx.StaticText(title_panel, label="◆")
        dot.SetForegroundColour(wx.Colour(41, 200, 140))
        dot.SetFont(make_bold_font(9))

        t_lbl = wx.StaticText(title_panel, label="  RSI STRATEGY PANEL")
        t_lbl.SetForegroundColour(COLOR_TITLE_TEXT)
        t_lbl.SetFont(make_bold_font(11))

        v_lbl = wx.StaticText(title_panel, label="v2.0")
        v_lbl.SetForegroundColour(wx.Colour(120, 155, 200))
        v_lbl.SetFont(make_font(8))

        t_sizer.Add(dot,  0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 14)
        t_sizer.Add(t_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        t_sizer.AddStretchSpacer()
        t_sizer.Add(v_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 14)
        title_panel.SetSizer(t_sizer)
        root.Add(title_panel, 0, wx.EXPAND)

        # blue accent bar under title
        accent_bar = wx.Panel(self, size=(-1, 3))
        accent_bar.SetBackgroundColour(COLOR_ACCENT_BLUE)
        root.Add(accent_bar, 0, wx.EXPAND)

        # ── Content ────────────────────────────────────────────────────────
        content = wx.BoxSizer(wx.VERTICAL)

        # Row 1: Instrument + Controls
        row1 = wx.BoxSizer(wx.HORIZONTAL)

        # -- Instrument Card --
        instr_card = SectionPanel(self, "Instrument")

        instr_inner = wx.FlexGridSizer(3, 2, 8, 10)
        instr_inner.AddGrowableCol(1, 1)

        def lbl(text):
            s = wx.StaticText(instr_card, label=text)
            s.SetForegroundColour(COLOR_TEXT_SECONDARY)
            s.SetFont(make_font(9))
            return s

        def styled_input(hint=""):
            t = wx.TextCtrl(instr_card, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
            t.SetBackgroundColour(COLOR_BG_INPUT)
            t.SetForegroundColour(COLOR_TEXT_PRIMARY)
            t.SetFont(make_bold_font(9))
            if hint:
                t.SetHint(hint)
            t.SetMinSize((-1, 28))
            return t

        SegmentsChoices = ["NSE", "BSE", "NFO", "BFO", "MCX"]
        self.Segments = wx.Choice(instr_card, wx.ID_ANY, choices=SegmentsChoices)
        self.Segments.SetSelection(0)
        self.Segments.SetBackgroundColour(COLOR_BG_INPUT)
        self.Segments.SetForegroundColour(COLOR_TEXT_PRIMARY)
        self.Segments.SetFont(make_bold_font(9))
        self.Segments.SetMinSize((-1, 28))

        self.instrument_name = styled_input("e.g. NIFTY50")
        self.Quantity_input   = styled_input("Lots / Units")

        instr_inner.Add(lbl("Segment"),  0, wx.ALIGN_CENTER_VERTICAL)
        instr_inner.Add(self.Segments,   1, wx.EXPAND)
        instr_inner.Add(lbl("Symbol"),   0, wx.ALIGN_CENTER_VERTICAL)
        instr_inner.Add(self.instrument_name, 1, wx.EXPAND)
        instr_inner.Add(lbl("Quantity"), 0, wx.ALIGN_CENTER_VERTICAL)
        instr_inner.Add(self.Quantity_input,  1, wx.EXPAND)

        instr_card.GetContentSizer().Add(instr_inner, 1, wx.EXPAND)
        row1.Add(instr_card, 1, wx.EXPAND | wx.RIGHT, 8)

        # -- Controls Card --
        ctrl_card = SectionPanel(self, "Controls")
        ctrl_inner = wx.BoxSizer(wx.VERTICAL)

        self.ltp_display = ValueDisplay(ctrl_card, "LAST TRADED PRICE", "00.00", COLOR_ACCENT_AMBER)
        ctrl_inner.Add(self.ltp_display, 0, wx.BOTTOM, 14)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)

        self.On_Off = wx.ToggleButton(ctrl_card, wx.ID_ANY, "● ON / OFF")
        self.On_Off.SetBackgroundColour(COLOR_TOGGLE_OFF)
        self.On_Off.SetForegroundColour(wx.Colour(255, 255, 255))
        self.On_Off.SetFont(make_bold_font(9))
        self.On_Off.SetMinSize((105, 32))

        self.save = wx.Button(ctrl_card, wx.ID_ANY, "💾  SAVE")
        self.save.SetBackgroundColour(COLOR_SAVE_BTN)
        self.save.SetForegroundColour(wx.Colour(255, 255, 255))
        self.save.SetFont(make_bold_font(9))
        self.save.SetMinSize((90, 32))

        btn_row.Add(self.On_Off, 0, wx.RIGHT, 8)
        btn_row.Add(self.save, 0)
        ctrl_inner.Add(btn_row, 0)

        ctrl_card.GetContentSizer().Add(ctrl_inner, 1, wx.EXPAND)
        row1.Add(ctrl_card, 1, wx.EXPAND)

        content.Add(row1, 0, wx.EXPAND | wx.BOTTOM, 8)

        # Row 2: Indicators
        rsi_card = SectionPanel(self, "Indicators")
        rsi_inner = wx.BoxSizer(wx.HORIZONTAL)

        self.rsi15_display = ValueDisplay(rsi_card, "RSI · 15 min", "00.00", COLOR_ACCENT_BLUE)
        self.rsi1h_display  = ValueDisplay(rsi_card, "RSI · 1 hour",  "00.00", COLOR_ACCENT_BLUE)
        self.ma1h_display   = ValueDisplay(rsi_card, "MA  · 1 hour",  "00.00", COLOR_ACCENT_AMBER)

        def vdiv(p):
            d = wx.Panel(p, size=(1, -1))
            d.SetBackgroundColour(COLOR_BORDER)
            return d

        rsi_inner.Add(self.rsi15_display, 1, wx.EXPAND | wx.RIGHT, 14)
        rsi_inner.Add(vdiv(rsi_card),     0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        rsi_inner.Add(self.rsi1h_display,  1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        rsi_inner.Add(vdiv(rsi_card),     0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        rsi_inner.Add(self.ma1h_display,   1, wx.EXPAND | wx.LEFT, 14)

        rsi_card.GetContentSizer().Add(rsi_inner, 1, wx.EXPAND)
        content.Add(rsi_card, 0, wx.EXPAND | wx.BOTTOM, 8)

        # Row 3: Trade Grid
        trade_card = SectionPanel(self, "Open Position")
        trade_inner = wx.BoxSizer(wx.HORIZONTAL)

        self.m_grid1 = wx.grid.Grid(trade_card, wx.ID_ANY)
        self.m_grid1.CreateGrid(1, 4)
        self.m_grid1.SetRowLabelSize(0)
        self.m_grid1.SetDefaultRowSize(34)
        self.m_grid1.SetColLabelSize(26)
        self.m_grid1.EnableEditing(False)
        self.m_grid1.EnableGridLines(True)
        self.m_grid1.SetGridLineColour(COLOR_GRID_LINE)

        col_labels = ["Transaction", "QTY", "AVG Price", "LTP"]
        col_widths  = [130, 72, 110, 95]
        for i, (lbl_txt, w) in enumerate(zip(col_labels, col_widths)):
            self.m_grid1.SetColLabelValue(i, lbl_txt)
            self.m_grid1.SetColSize(i, w)

        self.m_grid1.SetDefaultCellBackgroundColour(COLOR_GRID_ROW)
        self.m_grid1.SetDefaultCellTextColour(COLOR_TEXT_PRIMARY)
        self.m_grid1.SetDefaultCellFont(make_mono_font(10))
        self.m_grid1.SetLabelBackgroundColour(COLOR_GRID_HEADER)
        self.m_grid1.SetLabelTextColour(COLOR_TEXT_SECONDARY)
        self.m_grid1.SetLabelFont(make_bold_font(9))
        self.m_grid1.SetBackgroundColour(COLOR_BG_CARD)
        self.m_grid1.SetCellValue(0, 0, "—")
        self.m_grid1.SetCellAlignment(0, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        trade_inner.Add(self.m_grid1, 1, wx.EXPAND | wx.RIGHT, 10)

        self.exit_btn = wx.Button(trade_card, wx.ID_ANY, "EXIT\nPOSITION")
        self.exit_btn.SetBackgroundColour(COLOR_EXIT_BTN)
        self.exit_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.exit_btn.SetFont(make_bold_font(9))
        self.exit_btn.SetMinSize((90, 60))

        trade_inner.Add(self.exit_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        trade_card.GetContentSizer().Add(trade_inner, 1, wx.EXPAND)
        content.Add(trade_card, 1, wx.EXPAND)

        # ── Status Bar ────────────────────────────────────────────────────
        status_panel = wx.Panel(self)
        status_panel.SetBackgroundColour(COLOR_BG_CARD2)
        status_panel.SetMinSize((-1, 28))

        # top divider
        st_div = wx.Panel(self, size=(-1, 1))
        st_div.SetBackgroundColour(COLOR_BORDER)

        st_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status_dot = wx.StaticText(status_panel, label="●")
        self.status_dot.SetForegroundColour(COLOR_TEXT_SECONDARY)
        self.status_dot.SetFont(make_bold_font(9))

        self.status_lbl = wx.StaticText(status_panel, label="  Strategy inactive — configure and press ON/OFF")
        self.status_lbl.SetForegroundColour(COLOR_TEXT_SECONDARY)
        self.status_lbl.SetFont(make_font(8))

        st_sizer.Add(self.status_dot, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        st_sizer.Add(self.status_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        status_panel.SetSizer(st_sizer)

        root.Add(content, 1, wx.EXPAND | wx.ALL, 10)
        root.Add(st_div, 0, wx.EXPAND)
        root.Add(status_panel, 0, wx.EXPAND)

        self.SetSizer(root)
        self.Layout()
        self.Centre(wx.BOTH)

        # ── Bindings ──────────────────────────────────────────────────────
        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        self.On_Off.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)

        for btn, h_col, n_col in [
            (self.save,     wx.Colour(20, 100, 220),  COLOR_SAVE_BTN),
            (self.exit_btn, wx.Colour(180, 30, 45),    COLOR_EXIT_BTN),
        ]:
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn, c=h_col:  b.SetBackgroundColour(c) or b.Refresh())
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn, c=n_col:  b.SetBackgroundColour(c) or b.Refresh())

    # ── Event Handlers ────────────────────────────────────────────────────

    def on_save(self, event):
        self.status_dot.SetForegroundColour(COLOR_ACCENT_GREEN)
        self.status_lbl.SetLabel("  ✔  Settings saved successfully")
        self.status_lbl.SetForegroundColour(COLOR_ACCENT_GREEN)
        event.Skip()

    def on_toggle(self, event):
        if self.On_Off.GetValue():
            self.On_Off.SetBackgroundColour(COLOR_TOGGLE_ON)
            self.On_Off.SetLabel("● ACTIVE")
            self.status_dot.SetForegroundColour(COLOR_ACCENT_GREEN)
            self.status_lbl.SetForegroundColour(COLOR_ACCENT_GREEN)
            self.status_lbl.SetLabel("  Strategy is LIVE — monitoring signals")
        else:
            self.On_Off.SetBackgroundColour(COLOR_TOGGLE_OFF)
            self.On_Off.SetLabel("● ON / OFF")
            self.status_dot.SetForegroundColour(COLOR_TEXT_SECONDARY)
            self.status_lbl.SetForegroundColour(COLOR_TEXT_SECONDARY)
            self.status_lbl.SetLabel("  Strategy inactive — configure and press ON/OFF")
        self.On_Off.Refresh()
        event.Skip()

    def on_exit(self, event):
        self.status_dot.SetForegroundColour(COLOR_ACCENT_RED)
        self.status_lbl.SetForegroundColour(COLOR_ACCENT_RED)
        self.status_lbl.SetLabel("  ⚠  Exit order triggered")
        event.Skip()

    def __del__(self):
        pass


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame1(None)
        frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()