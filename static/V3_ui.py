# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder
###########################################################################

import wx
import wx.xrc
import wx.grid

import gettext
_ = gettext.gettext


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(510, 311),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        gbSizer1 = wx.GridBagSizer(0, 0)

        # ======================
        # SYMBOL + QTY
        # ======================

        gbSizer7 = wx.GridBagSizer(0, 0)

        self.Symbol = wx.StaticText(self, wx.ID_ANY, _("Symbol :"))
        gbSizer7.Add(self.Symbol, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # Symbol input
        self.instrument_name = wx.TextCtrl(
            self,
            wx.ID_ANY,
            "",
            style=wx.TE_PROCESS_ENTER
        )

        gbSizer7.Add(self.instrument_name, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.Quantity = wx.StaticText(self, wx.ID_ANY, _("Quantity :"))
        gbSizer7.Add(self.Quantity, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # Quantity input (numbers)
        self.Quantity_input = wx.TextCtrl(self, wx.ID_ANY, "")
        gbSizer7.Add(self.Quantity_input, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        gbSizer1.Add(gbSizer7, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # ======================
        # LTP + BUTTONS
        # ======================

        gbSizer8 = wx.GridBagSizer(0, 0)

        self.LTP = wx.StaticText(self, wx.ID_ANY, _("LTP  :"))
        gbSizer8.Add(self.LTP, wx.GBPosition(1, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, _("00.00"))
        gbSizer8.Add(self.m_staticText4, wx.GBPosition(1, 8), wx.GBSpan(1, 1), wx.ALL, 5)

        self.On_Off = wx.ToggleButton(self, wx.ID_ANY, _("ON/OFF"))
        gbSizer8.Add(self.On_Off, wx.GBPosition(0, 15), wx.GBSpan(1, 1), wx.ALL, 5)

        self.save = wx.Button(self, wx.ID_ANY, _("SAVE"))
        self.save.SetBackgroundColour(wx.Colour(140, 255, 26))
        gbSizer8.Add(self.save, wx.GBPosition(1, 15), wx.GBSpan(1, 1), wx.ALL, 5)

        gbSizer1.Add(gbSizer8, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # ======================
        # RSI DATA
        # ======================

        RSI_Entry = wx.GridBagSizer(0, 0)

        self.m_staticText6 = wx.StaticText(self, wx.ID_ANY, _("RSI (15 min)   :"))
        RSI_Entry.Add(self.m_staticText6, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, _("00.00"))
        RSI_Entry.Add(self.m_staticText7, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText8 = wx.StaticText(self, wx.ID_ANY, _("RSI (1 hr)        :"))
        RSI_Entry.Add(self.m_staticText8, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, _("00.00"))
        RSI_Entry.Add(self.m_staticText9, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText10 = wx.StaticText(self, wx.ID_ANY, _("MA (1 hr)       :"))
        RSI_Entry.Add(self.m_staticText10, wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText11 = wx.StaticText(self, wx.ID_ANY, _("00.00"))
        RSI_Entry.Add(self.m_staticText11, wx.GBPosition(2, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        gbSizer1.Add(RSI_Entry, wx.GBPosition(3, 0), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # ======================
        # GRID + EXIT
        # ======================

        gbSizer11 = wx.GridBagSizer(0, 0)

        self.m_grid1 = wx.grid.Grid(self, wx.ID_ANY)

        self.m_grid1.CreateGrid(1, 5)
        self.m_grid1.EnableEditing(False)

        self.m_grid1.SetColLabelValue(0, _("Transaction"))
        self.m_grid1.SetColLabelValue(1, _("QTY"))
        self.m_grid1.SetColLabelValue(2, _("AVG"))
        self.m_grid1.SetColLabelValue(3, _("LTP"))
        self.m_grid1.SetColLabelValue(4, _("Status"))

        self.m_grid1.SetRowLabelSize(0)

        gbSizer11.Add(self.m_grid1, wx.GBPosition(0, 0), wx.GBSpan(2, 2), wx.ALL, 10)

        self.exit_btn = wx.Button(self, wx.ID_ANY, _("EXIT"))
        self.exit_btn.SetBackgroundColour(wx.Colour(255, 51, 51))

        gbSizer11.Add(self.exit_btn, wx.GBPosition(0, 3), wx.GBSpan(2, 1), wx.ALL, 20)

        # FIXED ROW SPAN (was 0 before)
        gbSizer1.Add(gbSizer11, wx.GBPosition(4, 0), wx.GBSpan(1, 3), wx.EXPAND, 5)

        self.SetSizer(gbSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
