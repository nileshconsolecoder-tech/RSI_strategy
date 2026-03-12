# -*- coding: utf-8 -*-

import wx
import wx.xrc
import wx.grid
import gettext

_ = gettext.gettext


class MyFrame1(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="RSI Strategy Panel",
            pos=wx.DefaultPosition,
            size=wx.Size(510, 311),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        gbSizer1 = wx.GridBagSizer(0, 0)

        # ========================
        # Instrument Section
        # ========================

        gbSizer7 = wx.GridBagSizer(0, 0)

        SegmentsChoices = ["NSE", "BSE", "NFO", "BFO", "MCX"]

        self.Segments = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, SegmentsChoices, 0)
        self.Segments.SetSelection(0)

        gbSizer7.Add(self.Segments, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.instrument_name = wx.TextCtrl(self, wx.ID_ANY)
        gbSizer7.Add(self.instrument_name, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.Quantity = wx.StaticText(self, wx.ID_ANY, "Quantity")
        gbSizer7.Add(self.Quantity, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.Quantity_input = wx.TextCtrl(self, wx.ID_ANY)
        gbSizer7.Add(self.Quantity_input, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        gbSizer1.Add(gbSizer7, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # ========================
        # LTP + Controls
        # ========================

        gbSizer8 = wx.GridBagSizer(0, 0)

        self.LTP = wx.StaticText(self, wx.ID_ANY, "LTP :")
        gbSizer8.Add(self.LTP, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, "00.00")
        gbSizer8.Add(self.m_staticText4, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.On_Off = wx.ToggleButton(self, wx.ID_ANY, "ON/OFF")
        gbSizer8.Add(self.On_Off, wx.GBPosition(0, 2), wx.GBSpan(1, 1), wx.ALL, 5)

        self.save = wx.Button(self, wx.ID_ANY, "SAVE")
        self.save.SetBackgroundColour(wx.Colour(140, 255, 26))
        gbSizer8.Add(self.save, wx.GBPosition(0, 3), wx.GBSpan(1, 1), wx.ALL, 5)

        gbSizer1.Add(gbSizer8, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # ========================
        # RSI Indicators
        # ========================

        RSI_Entry = wx.GridBagSizer(0, 0)

        self.rsi15_label = wx.StaticText(self, wx.ID_ANY, "RSI (15 min) :")
        RSI_Entry.Add(self.rsi15_label, wx.GBPosition(0, 0), wx.GBSpan(1,1), wx.ALL, 5)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, "00.00")
        RSI_Entry.Add(self.m_staticText7, wx.GBPosition(0, 1), wx.GBSpan(1,1), wx.ALL, 5)

        self.rsi1h_label = wx.StaticText(self, wx.ID_ANY, "RSI (1 hr) :")
        RSI_Entry.Add(self.rsi1h_label, wx.GBPosition(1, 0), wx.GBSpan(1,1), wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, "00.00")
        RSI_Entry.Add(self.m_staticText9, wx.GBPosition(1, 1), wx.GBSpan(1,1), wx.ALL, 5)

        self.ma_label = wx.StaticText(self, wx.ID_ANY, "MA (1 hr) :")
        RSI_Entry.Add(self.ma_label, wx.GBPosition(2, 0), wx.GBSpan(1,1), wx.ALL, 5)

        self.m_staticText11 = wx.StaticText(self, wx.ID_ANY, "00.00")
        RSI_Entry.Add(self.m_staticText11, wx.GBPosition(2, 1), wx.GBSpan(1,1), wx.ALL, 5)

        gbSizer1.Add(RSI_Entry, wx.GBPosition(2, 0), wx.GBSpan(1, 2), wx.EXPAND, 5)

        # ========================
        # Trade Grid
        # ========================

        gbSizer11 = wx.GridBagSizer(0, 0)

        self.m_grid1 = wx.grid.Grid(self, wx.ID_ANY)
        self.m_grid1.CreateGrid(1, 4)

        self.m_grid1.SetColLabelValue(0, "Transaction")
        self.m_grid1.SetColLabelValue(1, "QTY")
        self.m_grid1.SetColLabelValue(2, "AVG")
        self.m_grid1.SetColLabelValue(3, "LTP")

        self.m_grid1.SetRowLabelSize(0)

        gbSizer11.Add(self.m_grid1, wx.GBPosition(0, 0), wx.GBSpan(1,3), wx.ALL, 10)

        self.exit_btn = wx.Button(self, wx.ID_ANY, "EXIT")
        self.exit_btn.SetBackgroundColour(wx.Colour(255, 51, 51))
        gbSizer11.Add(self.exit_btn, wx.GBPosition(0, 3), wx.GBSpan(1,1), wx.ALL, 10)

        gbSizer1.Add(gbSizer11, wx.GBPosition(3, 0), wx.GBSpan(1, 2), wx.EXPAND, 5)

        self.SetSizer(gbSizer1)
        self.Layout()
        self.Centre(wx.BOTH)

        # ========================
        # Event Bindings
        # ========================

        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        self.On_Off.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)

    # ========================
    # Virtual event handlers
    # ========================

    def on_save(self, event):
        event.Skip()

    def on_toggle(self, event):
        event.Skip()

    def on_exit(self, event):
        event.Skip()

    def __del__(self):
        pass