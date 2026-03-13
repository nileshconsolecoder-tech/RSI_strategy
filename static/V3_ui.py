# -*- coding: utf-8 -*-

import wx
import wx.xrc
import wx.grid
import gettext

_ = gettext.gettext

# ─────────────────────────────────────────────
#  DESIGN TOKENS  –  Light theme, semantic colors
# ─────────────────────────────────────────────
C_BG          = wx.Colour(245, 246, 250)   # page background – cool off-white
C_CARD        = wx.Colour(255, 255, 255)   # card / panel white
C_BORDER      = wx.Colour(220, 224, 235)   # subtle borders
C_TEXT_PRI    = wx.Colour(22,  30,  50)    # primary text – deep navy
C_TEXT_SEC    = wx.Colour(100, 110, 135)   # secondary / label text
C_ACCENT      = wx.Colour(67,  97, 238)    # brand blue (buttons, highlights)
C_ACCENT_LITE = wx.Colour(235, 238, 255)   # light tint of accent

# Semantic
C_BUY   = wx.Colour(16,  185, 129)   # green  – positive / save / on
C_SELL  = wx.Colour(239, 68,  68)    # red    – danger / exit / sell
C_WARN  = wx.Colour(245, 158, 11)    # amber  – toggle / caution
C_RSI   = wx.Colour(99,  102, 241)   # indigo – RSI indicators
C_MA    = wx.Colour(20,  184, 166)   # teal   – Moving Average

FONT_FACE = "Segoe UI"   # clean, modern system font


def _font(size=9, bold=False, face=FONT_FACE):
    w = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, w, faceName=face)


class RoundedPanel(wx.Panel):
    """A panel that paints itself with a rounded-rect card look."""
    def __init__(self, parent, bg=C_CARD, radius=10, border=C_BORDER):
        super().__init__(parent, style=wx.NO_BORDER)
        self._bg     = bg
        self._radius = radius
        self._border = border
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _on_paint(self, _):
        dc  = wx.AutoBufferedPaintDC(self)
        gc  = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        if w < 1 or h < 1:
            return
        gc.SetBrush(gc.CreateBrush(wx.Brush(self._bg)))
        gc.SetPen(gc.CreatePen(wx.Pen(self._border, 1)))
        gc.DrawRoundedRectangle(0, 0, w - 1, h - 1, self._radius)


class PillBadge(wx.Panel):
    """Small coloured pill showing a value."""
    def __init__(self, parent, label="00.00", color=C_ACCENT):
        super().__init__(parent, style=wx.NO_BORDER)
        self._color = color
        self._label = label
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.SetMinSize(wx.Size(72, 26))

    def SetValue(self, val):
        self._label = val
        self.Refresh()

    def _on_paint(self, _):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        # pill background
        r = h // 2
        bg = wx.Colour(self._color.Red(), self._color.Green(), self._color.Blue(), 30)
        gc.SetBrush(gc.CreateBrush(wx.Brush(bg)))
        gc.SetPen(gc.CreatePen(wx.Pen(self._color, 1)))
        gc.DrawRoundedRectangle(0, 0, w - 1, h - 1, r)
        # text
        gc.SetFont(gc.CreateFont(_font(9, bold=True), self._color))
        tw, th = gc.GetTextExtent(self._label)
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)


class StyledButton(wx.Panel):
    """Fully custom drawn button with hover effect."""
    def __init__(self, parent, label, bg, fg=wx.WHITE, radius=7):
        super().__init__(parent, style=wx.NO_BORDER)
        self._label   = label
        self._bg      = bg
        self._hover   = wx.Colour(
            min(bg.Red()   + 20, 255),
            min(bg.Green() + 20, 255),
            min(bg.Blue()  + 20, 255))
        self._fg      = fg
        self._radius  = radius
        self._hovered = False
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize(wx.Size(80, 32))
        self.Bind(wx.EVT_PAINT,       self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self._set_hover(True))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set_hover(False))
        self.Bind(wx.EVT_LEFT_UP,      self._fire_click)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def _set_hover(self, val):
        self._hovered = val
        self.Refresh()

    def _fire_click(self, _):
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def _on_paint(self, _):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        col = self._hover if self._hovered else self._bg
        gc.SetBrush(gc.CreateBrush(wx.Brush(col)))
        gc.SetPen(gc.CreatePen(wx.Pen(col, 0)))
        gc.DrawRoundedRectangle(0, 0, w, h, self._radius)
        gc.SetFont(gc.CreateFont(_font(9, bold=True), self._fg))
        tw, th = gc.GetTextExtent(self._label)
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)


class ToggleSwitch(wx.Panel):
    """iOS-style toggle switch.  Green = ON, Grey = OFF."""
    def __init__(self, parent):
        super().__init__(parent, style=wx.NO_BORDER)
        self._on = False
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize(wx.Size(56, 28))
        self.Bind(wx.EVT_PAINT,      self._on_paint)
        self.Bind(wx.EVT_LEFT_UP,    self._toggle)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def _toggle(self, _):
        self._on = not self._on
        self.Refresh()
        evt = wx.CommandEvent(wx.EVT_TOGGLEBUTTON.typeId, self.GetId())
        evt.SetInt(int(self._on))
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def GetValue(self):
        return self._on

    def _on_paint(self, _):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()
        track_col = C_BUY if self._on else wx.Colour(200, 204, 215)
        gc.SetBrush(gc.CreateBrush(wx.Brush(track_col)))
        gc.SetPen(gc.CreatePen(wx.Pen(track_col, 0)))
        gc.DrawRoundedRectangle(0, 4, w, h - 8, (h - 8) // 2)
        # knob
        knob_x = w - h + 2 if self._on else 2
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.WHITE)))
        gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(180, 185, 200), 1)))
        gc.DrawEllipse(knob_x, 2, h - 4, h - 4)
        # label
        lbl = "ON" if self._on else "OFF"
        lbl_col = wx.WHITE if self._on else wx.Colour(130, 135, 155)
        gc.SetFont(gc.CreateFont(_font(7, bold=True), lbl_col))
        tw, th = gc.GetTextExtent(lbl)
        tx = 6 if self._on else w - tw - 6
        gc.DrawText(lbl, tx, (h - th) / 2)


class LabeledInput(wx.Panel):
    """Label + TextCtrl combo with floating-label aesthetics."""
    def __init__(self, parent, label, hint=""):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(C_BG)
        vbox = wx.BoxSizer(wx.VERTICAL)

        lbl = wx.StaticText(self, label=label)
        lbl.SetFont(_font(8, bold=True))
        lbl.SetForegroundColour(C_TEXT_SEC)
        vbox.Add(lbl, 0, wx.BOTTOM, 3)

        self.ctrl = wx.TextCtrl(self, style=wx.NO_BORDER)
        self.ctrl.SetHint(hint)
        self.ctrl.SetFont(_font(10))
        self.ctrl.SetForegroundColour(C_TEXT_PRI)
        self.ctrl.SetBackgroundColour(C_CARD)

        # wrap ctrl in a border panel
        border = RoundedPanel(self, bg=C_CARD, radius=7, border=C_BORDER)
        bsizer = wx.BoxSizer()
        bsizer.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 6)
        border.SetSizer(bsizer)
        vbox.Add(border, 0, wx.EXPAND)

        self.SetSizer(vbox)

    def GetValue(self):
        return self.ctrl.GetValue()


class RSIRow(wx.Panel):
    """One indicator row: dot + label + pill."""
    def __init__(self, parent, label, dot_color, value="00.00"):
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetBackgroundColour(C_CARD)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # coloured dot
        dot = wx.Panel(self, size=(10, 10), style=wx.NO_BORDER)
        dot.SetBackgroundColour(dot_color)

        lbl = wx.StaticText(self, label=label)
        lbl.SetFont(_font(9))
        lbl.SetForegroundColour(C_TEXT_SEC)

        self.badge = PillBadge(self, value, dot_color)

        hbox.Add(dot,        0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        hbox.Add(lbl,        1, wx.ALIGN_CENTER_VERTICAL)
        hbox.Add(self.badge, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)


# ─────────────────────────────────────────────────────────────────────────────
class MyFrame1(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent,
            id=wx.ID_ANY,
            title="RSI Strategy Panel",
            pos=wx.DefaultPosition,
            size=wx.Size(560, 440),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )
        self.SetSizeHints(wx.Size(520, 420), wx.DefaultSize)
        self.SetBackgroundColour(C_BG)
        self._build_ui()
        self.Centre(wx.BOTH)

    # ─── UI construction ──────────────────────────────────────────────────
    def _build_ui(self):
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._make_header(),     0, wx.EXPAND | wx.ALL, 12)
        root.Add(self._make_instrument(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        root.Add(self._make_indicators(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        root.Add(self._make_grid_row(),   0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(root)
        self.Layout()

    # ── Header ──────────────────────────────────────────────────────────
    def _make_header(self):
        card = RoundedPanel(self, bg=C_ACCENT, radius=10, border=C_ACCENT)
        card.SetMinSize(wx.Size(-1, 54))

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(card, label="RSI Strategy Panel")
        title.SetFont(_font(13, bold=True))
        title.SetForegroundColour(wx.WHITE)

        subtitle = wx.StaticText(card, label="Automated signal monitor")
        subtitle.SetFont(_font(8))
        subtitle.SetForegroundColour(wx.Colour(200, 210, 255))

        vstack = wx.BoxSizer(wx.VERTICAL)
        vstack.Add(title,    0)
        vstack.Add(subtitle, 0, wx.TOP, 2)

        # LTP chip on right
        ltp_lbl = wx.StaticText(card, label="LTP")
        ltp_lbl.SetFont(_font(7, bold=True))
        ltp_lbl.SetForegroundColour(wx.Colour(180, 195, 255))

        self.ltp_value = wx.StaticText(card, label="00.00")
        self.ltp_value.SetFont(_font(16, bold=True))
        self.ltp_value.SetForegroundColour(wx.WHITE)

        ltp_vstack = wx.BoxSizer(wx.VERTICAL)
        ltp_vstack.Add(ltp_lbl,       0, wx.ALIGN_RIGHT)
        ltp_vstack.Add(self.ltp_value, 0, wx.ALIGN_RIGHT)

        hbox.AddSpacer(14)
        hbox.Add(vstack,    1, wx.ALIGN_CENTER_VERTICAL)
        hbox.Add(ltp_vstack, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 14)

        card.SetSizer(hbox)
        return card

    # ── Instrument + Controls ────────────────────────────────────────────
    def _make_instrument(self):
        card = RoundedPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sec_lbl = wx.StaticText(card, label="INSTRUMENT")
        sec_lbl.SetFont(_font(7, bold=True))
        sec_lbl.SetForegroundColour(C_TEXT_SEC)

        # Inputs row
        self.instrument_name  = LabeledInput(card, "Symbol", "e.g. NIFTY50")
        self.Quantity_input   = LabeledInput(card, "Quantity", "e.g. 50")

        inp_row = wx.BoxSizer(wx.HORIZONTAL)
        inp_row.Add(self.instrument_name, 1, wx.EXPAND | wx.RIGHT, 10)
        inp_row.Add(self.Quantity_input,  1, wx.EXPAND)

        # Controls row
        self.On_Off = ToggleSwitch(card)
        self.save   = StyledButton(card, "SAVE",  C_BUY)
        self.save.SetMinSize(wx.Size(90, 32))

        ctrl_row = wx.BoxSizer(wx.HORIZONTAL)
        ctrl_row.AddStretchSpacer()
        ctrl_row.Add(wx.StaticText(card, label="Strategy"), 0,
                     wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        ctrl_row.Add(self.On_Off, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        ctrl_row.Add(self.save,   0, wx.ALIGN_CENTER_VERTICAL)

        vbox.Add(sec_lbl,  0, wx.BOTTOM, 6)
        vbox.Add(inp_row,  0, wx.EXPAND | wx.BOTTOM, 10)
        vbox.Add(ctrl_row, 0, wx.EXPAND)

        # pad inside card
        outer = wx.BoxSizer()
        outer.Add(vbox, 1, wx.EXPAND | wx.ALL, 14)
        card.SetSizer(outer)
        return card

    # ── RSI Indicators ───────────────────────────────────────────────────
    def _make_indicators(self):
        card = RoundedPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sec_lbl = wx.StaticText(card, label="INDICATORS")
        sec_lbl.SetFont(_font(7, bold=True))
        sec_lbl.SetForegroundColour(C_TEXT_SEC)

        self._rsi15 = RSIRow(card, "RSI  15 min",   C_RSI)
        self._rsi1h = RSIRow(card, "RSI  1 hr",     C_ACCENT)
        self._ma1h  = RSIRow(card, "MA   1 hr",     C_MA)

        # dividers
        def _div():
            ln = wx.StaticLine(card, style=wx.LI_HORIZONTAL)
            ln.SetBackgroundColour(C_BORDER)
            return ln

        vbox.Add(sec_lbl,      0, wx.BOTTOM, 8)
        vbox.Add(self._rsi15,  0, wx.EXPAND | wx.BOTTOM, 6)
        vbox.Add(_div(),       0, wx.EXPAND | wx.BOTTOM, 6)
        vbox.Add(self._rsi1h,  0, wx.EXPAND | wx.BOTTOM, 6)
        vbox.Add(_div(),       0, wx.EXPAND | wx.BOTTOM, 6)
        vbox.Add(self._ma1h,   0, wx.EXPAND)

        outer = wx.BoxSizer()
        outer.Add(vbox, 1, wx.EXPAND | wx.ALL, 14)
        card.SetSizer(outer)
        return card

    # ── Trade Grid + Exit ────────────────────────────────────────────────
    def _make_grid_row(self):
        card = RoundedPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sec_lbl = wx.StaticText(card, label="OPEN POSITION")
        sec_lbl.SetFont(_font(7, bold=True))
        sec_lbl.SetForegroundColour(C_TEXT_SEC)

        self.m_grid1 = wx.grid.Grid(card, style=wx.BORDER_NONE)
        self.m_grid1.CreateGrid(1, 4)
        self.m_grid1.SetDefaultRowSize(30)

        # Grid colours
        self.m_grid1.SetDefaultCellFont(_font(9))
        self.m_grid1.SetDefaultCellTextColour(C_TEXT_PRI)
        self.m_grid1.SetGridLineColour(C_BORDER)
        self.m_grid1.SetCellHighlightColour(C_ACCENT)
        self.m_grid1.SetLabelBackgroundColour(C_ACCENT_LITE)
        self.m_grid1.SetLabelTextColour(C_ACCENT)
        self.m_grid1.GetGridColLabelWindow().SetFont(_font(8, bold=True))

        for i, col in enumerate(["Transaction", "Qty", "Avg Price", "LTP"]):
            self.m_grid1.SetColLabelValue(i, col)

        self.m_grid1.SetRowLabelSize(0)
        self.m_grid1.SetColLabelSize(24)
        self.m_grid1.EnableEditing(False)
        self.m_grid1.DisableDragRowSize()
        self.m_grid1.SetBackgroundColour(C_CARD)

        self.exit_btn = StyledButton(card, "EXIT", C_SELL)
        self.exit_btn.SetMinSize(wx.Size(80, 34))

        hrow = wx.BoxSizer(wx.HORIZONTAL)
        hrow.Add(self.m_grid1, 1, wx.EXPAND | wx.RIGHT, 10)
        hrow.Add(self.exit_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        vbox.Add(sec_lbl, 0, wx.BOTTOM, 8)
        vbox.Add(hrow,    1, wx.EXPAND)

        outer = wx.BoxSizer()
        outer.Add(vbox, 1, wx.EXPAND | wx.ALL, 14)
        card.SetSizer(outer)
        return card

    # ─── Event handlers ───────────────────────────────────────────────────
    def on_save(self, event):
        event.Skip()

    def on_toggle(self, event):
        event.Skip()

    def on_exit(self, event):
        event.Skip()

    def __del__(self):
        pass


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame1(None)

    # wire events
    frame.save.Bind(wx.EVT_BUTTON,       frame.on_save)
    frame.On_Off.Bind(wx.EVT_TOGGLEBUTTON, frame.on_toggle)
    frame.exit_btn.Bind(wx.EVT_BUTTON,   frame.on_exit)

    frame.Show()
    app.MainLoop()