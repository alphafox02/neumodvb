#!/usr/bin/python3
# Neumo dvb (C) 2019-2025 deeptho@gmail.com
# Copyright notice:
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import wx
import wx.grid
import sys
import os
import copy
from collections import namedtuple, OrderedDict
import numbers
import datetime
from dateutil import tz
import regex as re

from neumodvb.util import setup, lastdot
from neumodvb.util import dtdebug, dterror
from neumodvb import neumodbutils
from neumodvb.neumolist import NeumoTable, NeumoGridBase, IconRenderer, MyColLabelRenderer,  GridPopup, screen_if_t
from neumodvb.neumo_dialogs import ShowMessage, ShowOkCancel
from neumodvb.util import find_parent_prop
import pydevdb
import pychdb

class lnbunicable_screen_t(object):
    def __init__(self, parent):
        self.parent = parent

    @property
    def list_size(self):
        return len(self.parent.lnb.unicable_channels)

    def record_at_row(self, rowno):
        assert(rowno>=0)
        if rowno >= self.list_size:
            assert(rowno == self.list_size)
        assert rowno < self.list_size
        return self.parent.lnb.unicable_channels[rowno]

    def update(self, txn):
        return True

    def set_reference(self, rec):
        lnb = self.parent.lnb
        for i in range(len(lnb.unicable_channels)):
            if lnb.unicable_channels[i].has_same_key(rec):
                return i
        return -1

class LnbunicableTable(NeumoTable):
    CD = NeumoTable.CD
    bool_fn = NeumoTable.bool_fn
    all_columns = \
        [CD(key='ch_id',  label='CH id', basic=True),
         CD(key='position',  label='pos.', basic=False),
         CD(key='frequency',  label='freq', basic=False),
         CD(key='enabled',  label='enabled', basic=False, dfn=bool_fn),
         CD(key='pin_code',  label='pin', basic=False),
         CD(key='unicable_version',  label='uc.\nvers.', basic=False),
        ]

    def __init__(self, parent, basic=False, *args, **kwds):
        initial_sorted_column = 'ch_id'
        data_table= pydevdb.unicable_ch
        self.lnb_ = None
        self.changed = False
        super().__init__(*args, parent=parent, basic=basic, db_t=pydevdb, data_table = data_table,
                         record_t=pydevdb.unicable_ch.unicable_ch,
                         screen_getter = self.screen_getter,
                         initial_sorted_column = initial_sorted_column,
                         **kwds)

    @property
    def lnb(self):
        if self.lnb_  is None:
            self.lnb_ = find_parent_prop(self, 'lnb')
        return self.lnb_

    @property
    def unicable_channel(self):
        if hasattr(self.parent, "unicable_channel"):
            return self.parent.unicable_channel
        return None

    @unicable_channel.setter
    def unicable_channel(self, val):
        if hasattr(self.parent, "unicable_channel"):
            self.parent.unicable_channel = val

    def screen_getter(self, txn, sort_field):
        """
        txn is not used; instead we use self.lnb
        """
        self.screen = screen_if_t(lnbunicable_screen_t(self), self.sort_order==2)

    def __save_record__(self, wtxn, record, old_record):

        dtdebug(f'UNICABLE_CHANNELS: {len(self.lnb.unicable_channels)}')
        changed = pydevdb.lnb.add_or_edit_unicable_channel(wtxn, self.lnb, record)
        return record

    def __delete_record__(self, txn, record):
        for i in range(len(self.lnb.unicable_channels)):
            if self.lnb.unicable_channels[i].ch_id == record.ch_id:
                self.lnb.unicable_channels.erase(i)
                self.changed = True
                return
        dtdebug("ERROR: cannot find record to delete")
        self.changed = True

    def __new_record__(self):
        ret=self.record_t()
        return ret

class LnbUnicableChannelGrid(NeumoGridBase):
    def _add_accels(self, items):
        accels=[]
        for a in items:
            randomId = wx.NewId()
            accels.append([a[0], a[1], randomId])
            self.Bind(wx.EVT_MENU, a[2], id=randomId)
        accel_tbl = wx.AcceleratorTable(accels)
        self.SetAcceleratorTable(accel_tbl)

    def __init__(self, basic, readonly, *args, **kwds):
        table = LnbunicableTable(self, basic=basic)
        super().__init__(basic, readonly, table, *args, **kwds)
        self.sort_order = 0
        self.sort_column = None
        self.selected_row = None if self.table.GetNumberRows() == 0 else 0
        #todo: these accellerators should be copied from neumomenu
        self._add_accels([
            (wx.ACCEL_CTRL,  ord('D'), self.OnDelete),
            (wx.ACCEL_CTRL,  ord('N'), self.OnNew),
            (wx.ACCEL_CTRL,  ord('E'), self.OnEditMode)
        ])
        self.EnableEditing(self.app.frame.edit_mode)

    def InitialRecord(self):
        return self.table.unicable_channel

    def OnDone(self, evt):
        #@todo(). When a new record has been inserted and network has been changed, and then user clicks "done"
        #this is not seen as a change, because the editor has not yet saved itself
        self.table.SaveModified() #fake save
        if self.table.changed:
            dtdebug(f"OnDone called changed-{self.table.changed}")

    def OnKeyDown(self, evt):
        """
        After editing, move cursor right
        """
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_RETURN  and not evt.HasAnyModifiers():
            self.MoveCursorRight(False)
            evt.Skip(False)
        else:
            evt.Skip(True)

    def OnNew(self, evt):
        self.app.frame.SetEditMode(True)
        self.EnableEditing(self.app.frame.edit_mode)
        return super().OnNew(evt)

    def CmdNew(self, event):
        dtdebug("CmdNew")
        f = wx.GetApp().frame
        if not f.edit_mode:
            f.SetEditMode(True)
        self.OnNew(event)

    def OnEditMode(self, evt):
        dtdebug(f'old_mode={self.app.frame.edit_mode}')
        self.app.frame.ToggleEditMode()
        self.EnableEditing(self.app.frame.edit_mode)


class BasicLnbUnicableChannelGrid(LnbUnicableChannelGrid):
    def __init__(self, *args, **kwds):
        basic = True
        readonly = True
        super().__init__(basic, readonly, *args, **kwds)
