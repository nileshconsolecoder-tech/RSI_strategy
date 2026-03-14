# -*- coding: utf-8 -*-

import wx
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
            size=wx.Size(580, 330),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainSizer = wx.GridBagSizer(5, 5)

        # =========================
        # SYMBOL + QTY INPUT
        # =========================

        inputSizer = wx.GridBagSizer(5, 5)

        self.Symbol = wx.StaticText(self, wx.ID_ANY, "Symbol :")
        inputSizer.Add(self.Symbol, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.instrument_name = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.instrument_name.SetMaxLength(20)
        inputSizer.Add(self.instrument_name, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.Quantity = wx.StaticText(self, wx.ID_ANY, "Quantity :")
        inputSizer.Add(self.Quantity, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.Quantity_input = wx.TextCtrl(self, wx.ID_ANY, "")
        self.Quantity_input.SetMaxLength(10)
        inputSizer.Add(self.Quantity_input, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        mainSizer.Add(inputSizer, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND)

        # =========================
        # RSI SETTINGS
        # =========================

        rsiSizer = wx.GridBagSizer(5, 5)

        self.rsi_upper_limit = wx.StaticText(self, wx.ID_ANY, "RSI Upper Limit")
        rsiSizer.Add(self.rsi_upper_limit, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.rsi_upper_limit_input = wx.TextCtrl(self, wx.ID_ANY, "")
        self.rsi_upper_limit_input.SetMaxLength(10)
        rsiSizer.Add(self.rsi_upper_limit_input, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.rsi_lower_limit = wx.StaticText(self, wx.ID_ANY, "RSI Lower Limit")
        rsiSizer.Add(self.rsi_lower_limit, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.rsi_lower_limit_input = wx.TextCtrl(self, wx.ID_ANY, "")
        self.rsi_lower_limit_input.SetMaxLength(10)
        rsiSizer.Add(self.rsi_lower_limit_input, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.On_Off = wx.ToggleButton(self, wx.ID_ANY, "ON/OFF")
        rsiSizer.Add(self.On_Off, wx.GBPosition(0, 3), wx.GBSpan(1, 1), wx.ALL, 5)

        self.save = wx.Button(self, wx.ID_ANY, "SAVE")
        self.save.SetBackgroundColour(wx.Colour(140, 255, 26))
        rsiSizer.Add(self.save, wx.GBPosition(1, 3), wx.GBSpan(1, 1), wx.ALL, 5)

        mainSizer.Add(rsiSizer, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.EXPAND)

        # =========================
        # MARKET DATA
        # =========================

        marketSizer = wx.GridBagSizer(5, 5)

        marketSizer.Add(wx.StaticText(self, wx.ID_ANY, "LTP :"), wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        self.ltp_value = wx.StaticText(self, wx.ID_ANY, "00.00")
        marketSizer.Add(self.ltp_value, wx.GBPosition(0, 1), wx.GBSpan(1, 1))

        marketSizer.Add(wx.StaticText(self, wx.ID_ANY, "RSI (15m) :"), wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, "00.00")
        marketSizer.Add(self.m_staticText7, wx.GBPosition(1, 1), wx.GBSpan(1, 1))

        marketSizer.Add(wx.StaticText(self, wx.ID_ANY, "RSI (1h) :"), wx.GBPosition(2, 0), wx.GBSpan(1, 1))
        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, "00.00")
        marketSizer.Add(self.m_staticText9, wx.GBPosition(2, 1), wx.GBSpan(1, 1))

        marketSizer.Add(wx.StaticText(self, wx.ID_ANY, "MA (1h) :"), wx.GBPosition(3, 0), wx.GBSpan(1, 1))
        self.m_staticText11 = wx.StaticText(self, wx.ID_ANY, "00.00")
        marketSizer.Add(self.m_staticText11, wx.GBPosition(3, 1), wx.GBSpan(1, 1))

        mainSizer.Add(marketSizer, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.EXPAND)

        # =========================
        # TRADE GRID
        # =========================

        gridSizer = wx.GridBagSizer(5, 5)

        self.m_grid1 = wx.grid.Grid(self)
        self.m_grid1.CreateGrid(1, 5)

        self.m_grid1.SetColLabelValue(0, "Transaction")
        self.m_grid1.SetColLabelValue(1, "QTY")
        self.m_grid1.SetColLabelValue(2, "AVG")
        self.m_grid1.SetColLabelValue(3, "LTP")
        self.m_grid1.SetColLabelValue(4, "Status")

        self.m_grid1.EnableEditing(False)

        gridSizer.Add(self.m_grid1, wx.GBPosition(0, 0), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        self.exit_btn = wx.Button(self, wx.ID_ANY, "EXIT")
        self.exit_btn.SetBackgroundColour(wx.Colour(255, 51, 51))

        gridSizer.Add(self.exit_btn, wx.GBPosition(0, 2), wx.GBSpan(1, 1), wx.ALL, 10)

        mainSizer.Add(gridSizer, wx.GBPosition(2, 0), wx.GBSpan(1, 2), wx.EXPAND)

        # =========================
        # CONFIG DISPLAY PANEL
        # =========================

        configSizer = wx.GridBagSizer(5, 5)

        configSizer.Add(wx.StaticText(self, wx.ID_ANY, "Symbol :"), wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        self.config_symbol_name = wx.StaticText(self, wx.ID_ANY, "None")
        configSizer.Add(self.config_symbol_name, wx.GBPosition(0, 1), wx.GBSpan(1, 1))

        configSizer.Add(wx.StaticText(self, wx.ID_ANY, "Quantity :"), wx.GBPosition(0, 2), wx.GBSpan(1, 1))
        self.config_qty = wx.StaticText(self, wx.ID_ANY, "00")
        configSizer.Add(self.config_qty, wx.GBPosition(0, 3), wx.GBSpan(1, 1))

        configSizer.Add(wx.StaticText(self, wx.ID_ANY, "RSI Upper :"), wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        self.config_rsi_upper = wx.StaticText(self, wx.ID_ANY, "00.00")
        configSizer.Add(self.config_rsi_upper, wx.GBPosition(1, 1), wx.GBSpan(1, 1))

        configSizer.Add(wx.StaticText(self, wx.ID_ANY, "RSI Lower :"), wx.GBPosition(1, 2), wx.GBSpan(1, 1))
        self.config_rsi_lower = wx.StaticText(self, wx.ID_ANY, "00.00")
        configSizer.Add(self.config_rsi_lower, wx.GBPosition(1, 3), wx.GBSpan(1, 1))

        configSizer.Add(wx.StaticText(self, wx.ID_ANY, "Last Update :"), wx.GBPosition(2, 0), wx.GBSpan(1, 1))
        self.config_last_update = wx.StaticText(self, wx.ID_ANY, "00:00")
        configSizer.Add(self.config_last_update, wx.GBPosition(2, 1), wx.GBSpan(1, 1))

        mainSizer.Add(configSizer, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.EXPAND)

        # =========================
        # SOFTWARE STATUS
        # =========================

        statusSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Software_Status = wx.StaticText(self, wx.ID_ANY, "Software Status :")
        self.sodtware_status = wx.StaticText(self, wx.ID_ANY, "ON")

        self.action = wx.StaticText(self, wx.ID_ANY, "Action :")
        self.last_action = wx.StaticText(self, wx.ID_ANY, "Idle")

        statusSizer.Add(self.Software_Status, 0, wx.ALL, 5)
        statusSizer.Add(self.sodtware_status, 0, wx.ALL, 5)
        statusSizer.AddSpacer(20)
        statusSizer.Add(self.action, 0, wx.ALL, 5)
        statusSizer.Add(self.last_action, 0, wx.ALL, 5)

        mainSizer.Add(statusSizer, wx.GBPosition(3, 0), wx.GBSpan(1, 2), wx.EXPAND)

        self.SetSizer(mainSizer)
        self.Layout()
        self.Centre(wx.BOTH)

    def __del__(self):
        pass