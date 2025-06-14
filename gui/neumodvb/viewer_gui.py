#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.1.0b1 on Wed Mar  5 23:21:50 2025
#

import wx

# begin wxGlade: dependencies
import gettext
import wx.grid
# end wxGlade

# begin wxGlade: extracode
from neumodvb.scancommandlist import ScanCommandGrid
from neumodvb.recinfo import RecInfoTextCtrl
from neumodvb.chepginfo import ChEpgInfoTextCtrl
from neumodvb.live import LivePanel
from neumodvb.chepglist import ChEpgGrid
from neumodvb.servicelist_combo import ServiceListComboCtrl
from neumodvb.dishlist import DishGrid
from neumodvb.cablelist import CableGrid
from neumodvb.lnblist import LnbGrid
from neumodvb.dvbt_muxlist import DvbtMuxGrid
from neumodvb.dvbc_muxlist import DvbcMuxGrid
from neumodvb.dvbs_muxlist import DvbsMuxGrid
from neumodvb.muxinfo import MuxInfoTextCtrl
from neumodvb.spectrumlist import SpectrumGrid
from neumodvb.autoreclist import AutoRecGrid
from neumodvb.reclist import RecGrid
from neumodvb.chgmlist import ChgmGrid
from neumodvb.chglist_combo import ChgListComboCtrl
from neumodvb.servicelist import ServiceGrid
from neumodvb.serviceinfo import ServiceInfoTextCtrl
from neumodvb.satlist_combo import SatListComboCtrl
from neumodvb.neumowidgets import DvbTypeChoice
from neumodvb.statuslist import StatusGrid
from neumodvb.streamlist import StreamGrid
from neumodvb.frontendlist import FrontendGrid
from neumodvb.chglist import ChgGrid
from neumodvb.satlist import SatGrid
from neumodvb.satbandlist_combo import SatBandChoice
# end wxGlade


class mainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: mainFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1762, 800))
        self.SetTitle(_("NeumoDVB"))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.satlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.satlist_panel.Hide()
        sizer.Add(self.satlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)

        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7.Add(sizer_13, 0, wx.ALL | wx.EXPAND, 3)

        self.sat_satband_sel = SatBandChoice(self.satlist_panel, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_13.Add(self.sat_satband_sel, 0, 0, 0)

        self.button_5 = wx.Button(self.satlist_panel, wx.ID_ANY, _("All"))
        sizer_13.Add(self.button_5, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT | wx.RIGHT, 3)

        sizer_13.Add((0, 0), 0, 0, 0)

        self.satgrid = SatGrid(self.satlist_panel, wx.ID_ANY)
        sizer_7.Add(self.satgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.chglist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.chglist_panel.Hide()
        sizer.Add(self.chglist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_27 = wx.BoxSizer(wx.HORIZONTAL)

        self.chggrid = ChgGrid(self.chglist_panel, wx.ID_ANY)
        sizer_27.Add(self.chggrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.frontendlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.frontendlist_panel.Hide()
        sizer.Add(self.frontendlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)

        self.frontendgrid = FrontendGrid(self.frontendlist_panel, wx.ID_ANY)
        sizer_10.Add(self.frontendgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.streamlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.streamlist_panel.Hide()
        sizer.Add(self.streamlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_31 = wx.BoxSizer(wx.HORIZONTAL)

        self.streamgrid = StreamGrid(self.streamlist_panel, wx.ID_ANY)
        sizer_31.Add(self.streamgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.statuslist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.statuslist_panel.Hide()
        sizer.Add(self.statuslist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_10b = wx.BoxSizer(wx.HORIZONTAL)

        self.statusgrid = StatusGrid(self.statuslist_panel, wx.ID_ANY)
        sizer_10b.Add(self.statusgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.servicelist_panel = wx.Panel(self, wx.ID_ANY)
        self.servicelist_panel.Hide()
        sizer.Add(self.servicelist_panel, 1, wx.EXPAND, 0)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_1, 0, wx.ALL | wx.EXPAND, 3)

        self.service_dvb_type_choice = DvbTypeChoice(self.servicelist_panel, wx.ID_ANY, choices=[_("choice 1")])
        self.service_dvb_type_choice.SetToolTip(_("Restrict service list to a specific\nDVB type"))
        self.service_dvb_type_choice.SetSelection(0)
        sizer_1.Add(self.service_dvb_type_choice, 0, wx.ALL | wx.EXPAND, 3)

        self.service_sat_sel = SatListComboCtrl(self.servicelist_panel, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.service_sat_sel.SetToolTip(_("Further restrict services list to a specific satellite"))
        sizer_1.Add(self.service_sat_sel, 0, wx.ALL | wx.EXPAND, 3)

        self.serviceinfo_text = ServiceInfoTextCtrl(self.servicelist_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_RICH)
        sizer_1.Add(self.serviceinfo_text, 3, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)

        self.servicegrid = ServiceGrid(self.servicelist_panel, wx.ID_ANY)
        sizer_3.Add(self.servicegrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.chgmlist_panel = wx.Panel(self, wx.ID_ANY)
        self.chgmlist_panel.Hide()
        sizer.Add(self.chgmlist_panel, 1, wx.EXPAND, 0)

        sizer_28 = wx.BoxSizer(wx.VERTICAL)

        sizer_101 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_28.Add(sizer_101, 0, wx.ALL | wx.EXPAND, 3)

        self.chgm_chg_sel = ChgListComboCtrl(self.chgmlist_panel, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_101.Add(self.chgm_chg_sel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)

        self.button_101 = wx.Button(self.chgmlist_panel, wx.ID_ANY, _("All"))
        sizer_101.Add(self.button_101, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT | wx.RIGHT, 3)

        self.chgminfo_text = ServiceInfoTextCtrl(self.chgmlist_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_RICH)
        sizer_101.Add(self.chgminfo_text, 3, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 3)

        self.chgmgrid = ChgmGrid(self.chgmlist_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
        self.chgmgrid.SetFocus()
        sizer_28.Add(self.chgmgrid, 1, wx.EXPAND, 0)

        self.reclist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.reclist_panel.Hide()
        sizer.Add(self.reclist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_63 = wx.BoxSizer(wx.HORIZONTAL)

        self.recgrid = RecGrid(self.reclist_panel, wx.ID_ANY)
        sizer_63.Add(self.recgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_63.Add((0, 0), 0, 0, 0)

        self.autoreclist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.autoreclist_panel.Hide()
        sizer.Add(self.autoreclist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_64 = wx.BoxSizer(wx.HORIZONTAL)

        self.autorecgrid = AutoRecGrid(self.autoreclist_panel, wx.ID_ANY)
        sizer_64.Add(self.autorecgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_64.Add((0, 0), 0, 0, 0)

        self.spectrumlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.spectrumlist_panel.Hide()
        sizer.Add(self.spectrumlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_631 = wx.BoxSizer(wx.HORIZONTAL)

        self.spectrumgrid = SpectrumGrid(self.spectrumlist_panel, wx.ID_ANY)
        sizer_631.Add(self.spectrumgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_631.Add((0, 0), 0, 0, 0)

        self.dvbs_muxlist_panel = wx.Panel(self, wx.ID_ANY)
        self.dvbs_muxlist_panel.Hide()
        sizer.Add(self.dvbs_muxlist_panel, 1, wx.EXPAND, 0)

        sizer_8 = wx.BoxSizer(wx.VERTICAL)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 3)

        self.dvbs_muxlist_sat_sel = SatListComboCtrl(self.dvbs_muxlist_panel, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_4.Add(self.dvbs_muxlist_sat_sel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)

        self.button_4 = wx.Button(self.dvbs_muxlist_panel, wx.ID_ANY, _("All"))
        sizer_4.Add(self.button_4, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT | wx.RIGHT, 3)

        self.dvbs_muxinfo_text = MuxInfoTextCtrl(self.dvbs_muxlist_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_RICH)
        sizer_4.Add(self.dvbs_muxinfo_text, 3, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 3)

        self.dvbs_muxgrid = DvbsMuxGrid(self.dvbs_muxlist_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
        self.dvbs_muxgrid.SetFocus()
        sizer_8.Add(self.dvbs_muxgrid, 1, wx.EXPAND, 0)

        self.dvbc_muxlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.dvbc_muxlist_panel.Hide()
        sizer.Add(self.dvbc_muxlist_panel, 1, wx.EXPAND, 0)

        sizer_dvbc_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_dvbc_1.Add(sizer_11, 0, wx.EXPAND, 0)

        label_1 = wx.StaticText(self.dvbc_muxlist_panel, wx.ID_ANY, _("DVBC Muxes"))
        sizer_11.Add(label_1, 1, 0, 0)

        self.dvbc_muxinfo_text = MuxInfoTextCtrl(self.dvbc_muxlist_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_11.Add(self.dvbc_muxinfo_text, 3, 0, 0)

        self.dvbc_muxgrid = DvbcMuxGrid(self.dvbc_muxlist_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
        sizer_dvbc_1.Add(self.dvbc_muxgrid, 1, wx.EXPAND, 0)

        self.dvbt_muxlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.dvbt_muxlist_panel.Hide()
        sizer.Add(self.dvbt_muxlist_panel, 1, wx.EXPAND, 0)

        sizer_dvbt_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_dvbt_1.Add(sizer_12, 0, wx.EXPAND, 0)

        label_2 = wx.StaticText(self.dvbt_muxlist_panel, wx.ID_ANY, _("DVBT muxes"))
        sizer_12.Add(label_2, 1, 0, 0)

        self.dvbt_muxinfo_text = MuxInfoTextCtrl(self.dvbt_muxlist_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_12.Add(self.dvbt_muxinfo_text, 3, 0, 0)

        self.dvbt_muxgrid = DvbtMuxGrid(self.dvbt_muxlist_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
        sizer_dvbt_1.Add(self.dvbt_muxgrid, 1, wx.EXPAND, 0)

        self.lnblist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.lnblist_panel.Hide()
        sizer.Add(self.lnblist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)

        self.lnbgrid = LnbGrid(self.lnblist_panel, wx.ID_ANY)
        sizer_5.Add(self.lnbgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.cablelist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.cablelist_panel.Hide()
        sizer.Add(self.cablelist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_cable = wx.BoxSizer(wx.HORIZONTAL)

        self.cablegrid = CableGrid(self.cablelist_panel, wx.ID_ANY)
        sizer_cable.Add(self.cablegrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.dishlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.dishlist_panel.Hide()
        sizer.Add(self.dishlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_95 = wx.BoxSizer(wx.HORIZONTAL)

        self.dishgrid = DishGrid(self.dishlist_panel, wx.ID_ANY)
        sizer_95.Add(self.dishgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.lnbnetworklist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.lnbnetworklist_panel.Hide()
        sizer.Add(self.lnbnetworklist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_55 = wx.BoxSizer(wx.HORIZONTAL)

        sizer_55.Add((0, 0), 0, 0, 0)

        self.chepg_panel = wx.Panel(self, wx.ID_ANY)
        self.chepg_panel.Hide()
        sizer.Add(self.chepg_panel, 3, wx.EXPAND, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)

        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_21, 0, wx.ALL | wx.EXPAND, 3)

        self.chepg_service_sel = ServiceListComboCtrl(self.chepg_panel, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        sizer_21.Add(self.chepg_service_sel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)

        self.button_21 = wx.Button(self.chepg_panel, wx.ID_ANY, _("All"))
        sizer_21.Add(self.button_21, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT | wx.RIGHT, 3)

        self.chepggrid = ChEpgGrid(self.chepg_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
        self.chepggrid.SetFocus()
        sizer_6.Add(self.chepggrid, 1, wx.EXPAND, 0)

        self.live_panel = LivePanel(self, wx.ID_ANY)
        self.live_panel.Hide()
        sizer.Add(self.live_panel, 1, wx.EXPAND, 0)

        self.mosaic_panel = wx.Panel(self, wx.ID_ANY)
        sizer.Add(self.mosaic_panel, 1, wx.EXPAND, 0)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)

        self.chepginfo_text = ChEpgInfoTextCtrl(self.mosaic_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.chepginfo_text.Hide()
        sizer_9.Add(self.chepginfo_text, 1, wx.EXPAND | wx.TOP, 0)

        self.recinfo_text = RecInfoTextCtrl(self.mosaic_panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.recinfo_text.Hide()
        sizer_9.Add(self.recinfo_text, 1, wx.EXPAND | wx.TOP, 0)

        self.scancommandlist_panel = wx.Panel(self, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.scancommandlist_panel.Hide()
        sizer.Add(self.scancommandlist_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        sizer_56 = wx.BoxSizer(wx.HORIZONTAL)

        self.scancommandgrid = ScanCommandGrid(self.scancommandlist_panel, wx.ID_ANY)
        sizer_56.Add(self.scancommandgrid, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.scancommandlist_panel.SetSizer(sizer_56)

        self.mosaic_panel.SetSizer(sizer_9)

        self.chepg_panel.SetSizer(sizer_6)

        self.lnbnetworklist_panel.SetSizer(sizer_55)

        self.dishlist_panel.SetSizer(sizer_95)

        self.cablelist_panel.SetSizer(sizer_cable)

        self.lnblist_panel.SetSizer(sizer_5)

        self.dvbt_muxlist_panel.SetSizer(sizer_dvbt_1)

        self.dvbc_muxlist_panel.SetSizer(sizer_dvbc_1)

        self.dvbs_muxlist_panel.SetSizer(sizer_8)

        self.spectrumlist_panel.SetSizer(sizer_631)

        self.autoreclist_panel.SetSizer(sizer_64)

        self.reclist_panel.SetSizer(sizer_63)

        self.chgmlist_panel.SetSizer(sizer_28)

        self.servicelist_panel.SetSizer(sizer_3)

        self.statuslist_panel.SetSizer(sizer_10b)

        self.streamlist_panel.SetSizer(sizer_31)

        self.frontendlist_panel.SetSizer(sizer_10)

        self.chglist_panel.SetSizer(sizer_27)

        self.satlist_panel.SetSizer(sizer_7)

        self.SetSizer(sizer)

        self.Layout()

        self.button_5.Bind(wx.EVT_BUTTON, self.OnGroupShowAll)
        self.service_dvb_type_choice.Bind(wx.EVT_CHOICE, self.OnDvbTypeChoice)
        self.button_101.Bind(wx.EVT_BUTTON, self.OnGroupShowAll)
        self.button_4.Bind(wx.EVT_BUTTON, self.OnGroupShowAll)
        self.button_21.Bind(wx.EVT_BUTTON, self.OnGroupShowAll)
        # end wxGlade

    def OnGroupShowAll(self, event):  # wxGlade: mainFrame.<event_handler>
        print("Event handler 'OnGroupShowAll' not implemented!")
        event.Skip()

    def OnDvbTypeChoice(self, event):  # wxGlade: mainFrame.<event_handler>
        print("Event handler 'OnDvbTypeChoice' not implemented!")
        event.Skip()

# end of class mainFrame

class Neumo_Gui(wx.App):
    def OnInit(self):
        self.main_frame = mainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.main_frame)
        self.main_frame.Show()
        return True

# end of class Neumo_Gui

if __name__ == "__main__":
    gettext.install("neumodvb") # replace with the appropriate catalog name

    neumodvb = Neumo_Gui(0)
    neumodvb.MainLoop()
