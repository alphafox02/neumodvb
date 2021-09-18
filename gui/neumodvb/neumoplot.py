#!/usr/bin/python3
# Neumo dvb (C) 2019-2021 deeptho@gmail.com
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
import warnings
import os
import sys
import time
import regex as re
from dateutil import tz

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize, LogNorm
from scipy.interpolate import interpn

import mpl_scatter_density # adds projection='scatter_density'
from matplotlib.colors import LinearSegmentedColormap

import numpy as np

#from sklearn.linear_model import LinearRegression
#import pandas as pd

from neumodvb.util import dtdebug, dterror
from neumodvb.neumodbutils import enum_to_str

import pyspectrum
import pystatdb
import pychdb
import datetime




white_viridis = LinearSegmentedColormap.from_list('white_viridis', [
    (0, '#ffffff00'),
    (1e-20, '#440053'),
    (0.2, '#404388'),
    (0.4, '#2a788e'),
    (0.6, '#21a784'),
    (0.8, '#78d151'),
    (1, '#fde624'),
], N=256)


def density_scatter( x , y, ax = None, sort = True, bins = 20, **kwargs )   :
    """
    Scatter plot colored by 2d histogram
    """
    if ax is None :
        fig , ax = plt.subplots()
    data , x_e, y_e = np.histogram2d( x, y, bins = bins, density = True )
    z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T , method = "splinef2d", bounds_error = False)

    #To be sure to plot all data
    z[np.where(np.isnan(z))] = 0.0

    # Sort the points by density, so that the densest points are plotted last
    if sort :
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

    ax.scatter( x, y, c=z, **kwargs )

    norm = Normalize(vmin = np.min(z), vmax = np.max(z))
    cbar = fig.colorbar(cm.ScalarMappable(norm = norm), ax=ax)
    cbar.ax.set_ylabel('Density')

    return ax


class CustomToolbar(NavigationToolbar):
    """
    toolbar which intercepts the readout cursor (which causes trouble)
    """
    def __init__(self, canvas):

        super().__init__(canvas)

    def mouse_move(self, event):
        self._update_cursor(event)

        if event.inaxes and event.inaxes.get_navigate():

            try:
                s = event.inaxes.format_coord(event.xdata, event.ydata)
            except (ValueError, OverflowError):
                pass
            else:
                s = s.rstrip()
                artists = [a for a in event.inaxes._mouseover_set
                           if a.contains(event)[0] and a.get_visible()]
                if artists:
                    a = cbook._topmost_artist(artists)
                    if a is not event.inaxes.patch:
                        data = a.get_cursor_data(event)
                        if data is not None:
                            data_str = a.format_cursor_data(data).rstrip()
                            if data_str:
                                s = s + '\n' + data_str
                #self.set_message(s)
        else:
            pass #self.set_message(self.mode)

def tooltips(fig):
    def update_annot(ind):

        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))),
                               " ".join([names[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        annot.get_bbox_patch().set_alpha(0.4)


    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    #fig.canvas.mpl_connect("motion_notify_event", hover)


def plot_marks(marks, offset=-55, label='xxx', use_index=True):
    global ret
    n = len(ret[0][:,1])
    f = np.array(range(0,n))
    sig = marks*offset
    plt.plot(f, sig, '+', label=label)
    plt.legend()

def get_renderer(fig):
    try:
        return fig.canvas.get_renderer()
    except AttributeError:
        return fig.canvas.renderer

def get_bboxes(objs, r=None, expand=(1, 1), ax=None, transform=None):
    """

    Parameters
    ----------
    objs : list, or PathCollection
        List of objects to get bboxes from. Also works with mpl PathCollection.
    r : renderer
        Renderer. The default is None, then automatically deduced from ax.
    expand : (float, float), optional
        How much to expand bboxes in (x, y), in fractions. The default is (1, 1).
    ax : Axes, optional
        The default is None, then uses current axes.
    transform : optional
        Transform to apply to the objects, if they don't return they window extent.
        The default is None, then applies the default ax transform.
    Returns
    -------
    list
        List of bboxes.
    """
    ax = ax or plt.gca()
    r = r or get_renderer(ax.get_figure())
    try:
        return [i.get_window_extent(r).expanded(*expand) for i in objs]
    except (AttributeError, TypeError):
        try:
            if all([isinstance(obj, matplotlib.transforms.BboxBase) for obj in objs]):
                return objs
            else:
                raise ValueError("Something is wrong")
        except TypeError:
            return get_bboxes_pathcollection(objs, ax)

class Tp(object):
    def __init__(self, spectrum, freq, symbol_rate):
        self.spectrum = spectrum
        self.freq = freq
        self.symbol_rate = symbol_rate
        self.scan_ok = False
        self.scan_failed = False

    def __str__(self):
        return f'{self.freq:8.3f}{self.spectrum.pol} {self.symbol_rate}kS/s'

def find_nearest(array,value):
    import math
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

def overlaps(a, b):
    """
    assumes that a.xmin < b.xmin
    """
    return b.xmin < a.xmax and (a.ymin <= b.ymin < a.ymax or b.ymin <= a.ymin < b.ymax )

all_rects=[]

def remove_rects():
    global all_rects
    for rect in all_rects:
        rect.remove()
    all_rects = []

def combine_ranges(a, b):
    if a is None and b is None:
        return None
    if a is None or b is None:
        return a if b is None else b
    return (min(a[0], b[0]), max(a[1], b[1]))

class Spectrum(object):
    def __init__(self, parent, spectrum, color):
        self.spectrum = spectrum
        self.parent = parent
        self.figure = self.parent.figure
        self.axes = self.parent.axes
        self.drawn = False
        self.color = color
        sat = pychdb.sat_pos_str(self.spectrum.k.sat_pos)
        date = datetime.datetime.fromtimestamp(self.spectrum.k.start_time , tz=tz.tzlocal()).strftime("%Y-%m-%d %H:%M")
        label = f'{date} {sat} {enum_to_str(self.spectrum.k.pol)} dish {self.spectrum.k.lnb_key.dish_id}'
        self.label = label
        self.annots = []
        self.tps = []
        self.peak_data = None
        self.vlines = None
        self.hlines = None
        self.annot_box = ((0,0))
        self.xlimits = (10700., 12750.)
        self.ylimits = (-60.0, -40.0)

    def __str__(self):
        sat = pychdb.sat_pos_str(self.spectrum.k.sat_pos)
        return f'{sat} {enum_to_str(self.spectrum.k.pol)} dish {self.spectrum.k.lnb_key.dish_id}'

    def tps_to_scan(self) :
        return [ tp for tp in self.tps if not tp.scan_failed and not tp.scan_ok ]

    def clear(self):
        for a in self.annots:
            a.remove()
        self.annots=[]
        if self.spectrum_graph is not None:
            for a in self.spectrum_graph:
                a.remove()
        self.spectrum_graph = None
        for a in self.annots:
            a.remove()
        self.annots = []
        if self.vlines is not None:
            self.vlines.remove()
            self.vlines = None

        if self.hlines is not None:
            self.hlines.remove()
            self.hlines = None

    def annot_for_freq(self, freq):
        found = None
        best = 20000000
        for annot in self.annots:
            delta= abs(annot.tp.freq - freq)
            if delta < best:
                found = annot
                best = delta
        return found, best

    def annot_for_mux(self, mux):
        found = None
        best = 20000000
        for annot in self.annots:
            delta= abs(annot.tp.freq*1000 - mux.frequency)
            if delta < best and annot.tp.spectrum.spectrum.k.pol == mux.pol:
                found = annot
                best = delta
        return found

    def show(self):
        if self.drawn:
            #dtdebug('clearing plot')
            #self.axes.clear()
            self.clear()
        receiver = wx.GetApp().receiver
        path = receiver.get_spectrum_path()
        spectrum_fname = ''.join([path, '/', self.spectrum.filename, "_spectrum.dat"])
        tps_fname = ''.join([path, '/', self.spectrum.filename, "_peaks.dat"])
        pol = self.spectrum.k.pol
        self.process(spectrum_fname, tps_fname)
        self.drawn = True

    def make_tps(self, tpsname):
        #n = len(spec[:,1])
        self.peak_data = np.loadtxt(tpsname)
        if len(self.peak_data) == 0:
            return
        f = self.peak_data[:,0]
        snr = None
        bw =  self.peak_data[:,1]/2000000
        for row in self.peak_data:
            tp = Tp(spectrum=self, freq=row[0], symbol_rate=row[1]*1.6/2000.)
            self.tps.append(tp)

    def plot_spec(self, fname):
        dtdebug(f"loading spectrum {fname}")
        self.spec = np.loadtxt(fname)
        if self.parent.do_detrend:
            self.detrend()
        t = self.spec[:,0]
        a = self.spec[:,1]

        self.spectrum_graph = self.axes.plot(t, a/1000,label=self.label, color=self.color)

    def annot_size(self):
        r = self.figure.canvas.get_renderer()
        t = self.axes.text(-50, 11000, '10841.660V/H \n10841.660V/H ', fontsize=8)
        bb = t.get_window_extent(renderer=r).transformed(self.axes.transData.inverted())
        t.remove()
        dtdebug(f"Box: {bb.width} x {bb.height}")
        return bb

    def detrend(self):
        for idx in np.where(self.spec[:,0]<11700), np.where(self.spec[:,0]>=11700):
            parts = len(idx[0])//16
            if parts == 0:
                continue
            l = parts*16
            t=  self.spec[idx, 1][0,:l].reshape([-1,parts]).min(axis=1)
            f = self.spec[idx, 0][0,:l].reshape([-1,parts])[:,0]
            p = np.polyfit(f, t, 1)
            self.spec[idx,1] -= p[0]*self.spec[idx,0]+p[1]

    def ann_tps(self, tpsk, spec, offset=-64, xoffset=0, yoffset=3):
        self.annots =[]
        if len(tpsk) == 0:
            return
        f = tpsk[:,0]
        #setting this is needed to calibrate coordinate system
        a = np.min(spec[:,1])
        b = np.max(spec[:,1])
        l = np.min(spec[0,0])
        r = np.max(spec[-1,0])
        bb = self.annot_size()
        self.annot_box = (bb.width, bb.height*2/1000)
        xscale = (len(spec[:,0])-1)/(r - l)
        w = xscale*bb.width #in integer units
        h = bb.height *2 #in units of snr

        n = len(spec[:,0])
        w = int(w)
        idxs =  np.searchsorted(spec[:,0], f, side='left')
        offset = h
        self.pol = enum_to_str (self.spectrum.k.pol)
        annoty, lrflag, a, b = pyspectrum.find_annot_locations(spec[:,1], idxs, w, h, offset)
        hlines = []
        yoffset =1.
        for idx, ay, flag, tp in zip(idxs, annoty, lrflag, self.tps):
            pt=[tp.freq, ay/1000.+yoffset]
            xoffset = 0
            annot=self.axes.annotate(f"{tp.freq:8.3f}{self.pol} \n{int(tp.symbol_rate)}kS/s ", \
                                     pt, xytext=(pt[0], pt[1]), \
                                     ha='right' if flag else 'left', fontsize=8)
            annot.tp = tp
            annot.set_picker(True)  # Enable picking on the legend line.
            self.annots.append(annot)
        sig = (spec[idxs,1])/1000. +yoffset
        self.vlines = self.axes.vlines(f, sig, annoty/1000 +yoffset, color='black')
        self.vlines.set_picker(True)  # Enable picking on the legend line.

        bw =  tpsk[:,1]/2000000
        self.hlines = self.axes.hlines(sig, f-bw, f+bw, color=self.color)
        self.hlines.set_picker(True)  # Enable picking on the legend line.

        #self.axes.xaxis.zoom((r-l)/1000)

    def process(self, specname, tpsname):
        self.plot_spec(specname)
        frequency_step = round(1000*(self.spec[1:,0] - self.spec[:-1,0]).mean())
        sig = self.spec[:,1]
        self.make_tps(tpsname)

        #set xlimits prior to annotation to ensure the computation
        #which ensures annotations are not overlapping has the proper coordinate system
        if self.parent.zoom_start_freq is None:
            self.parent.zoom_start_freq = self.spectrum.start_freq/1000.

        xlimits =(self.parent.zoom_start_freq, self.parent.zoom_start_freq+self.parent.zoom_bandwidth)
        ylimits = [np.min(self.spec[:,1]),  np.max(self.spec[:,1])]
        if ylimits[1] != ylimits[0]:
            self.axes.set_ylim(ylimits)
        self.axes.set_xlim(xlimits)

        self.ann_tps(self.peak_data, self.spec)

        #set final limits
        self.xlimits = (self.spec[0,0]-100, self.spec[-1,0]+100)
        self.ylimits = (ylimits[0]/1000, ylimits[1]/1000 +self.annot_box[1])

        xlimits, ylimits = self.parent.get_limits()
        self.axes.set_ylim(ylimits)
        self.axes.set_xlim(xlimits)

def log_transform(im):
    '''returns log(image) scaled to the interval [0,1]'''
    try:
        (min, max) = (im[im > 0].min(), im.max())
        if (max > min) and (max > 0):
            return 255*(np.log(im.clip(min, max)) - np.log(min)) / (np.log(max) - np.log(min))
    except:
        pass
    return im


class ConstellationPlotBase(wx.Panel):
    def __init__(self, parent, figsize, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.xlimits = None
        self.ylimits = None
        self.parent = parent
        #self.constellation = pystatdb.spectrum.spectrum()
        #self.scrollbar.Bind(wx.EVT_COMMAND_SCROLL, self.OnScroll)

        self.figure = mpl.figure.Figure(figsize=figsize)
        self.axes = self.figure.add_subplot(111, projection='scatter_density')
        self.canvas = FigureCanvas(self, -1, self.figure)
        #print(f'BLIT={FigureCanvas.supports_blit}')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, proportion=1,
                        flag=wx.LEFT | wx.TOP | wx.EXPAND)
        #self.sizer.Add(self.scrollbar, proportion=0,
        #                flag=wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.Bind ( wx.EVT_WINDOW_CREATE, self.OnCreateWindow )
        self.Parent.Bind ( wx.EVT_SHOW, self.OnShowHide )
        self.legend  = None
        self.cycle_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.constellation_graphs=[]
        self.min = None
        self.max = None
        self.samples = None

    def OnShowHide(self,event):
        if event.IsShown():
            self.draw()

    def OnCreateWindow(self,event):
        if event.GetWindow() == self:
            #self.start_freq, self.end_freq = self.parent.start_freq, self.parent.end_freq
            self.draw()
        else:
            pass

    def draw(self):
        self.axes.clear()
        self.figure.patch.set_alpha(0.2)
        self.Fit()
        #self.figure.subplots_adjust(left=0.15, bottom=0.15, right=0.95, top=0.95)
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.axes.set_axis_off()
        #self.axes.spines['right'].set_visible(False)
        #self.axes.spines['top'].set_visible(False)
        #self.plot_constellation()
        #self.axes.set_ylabel('dB')
        #self.axes.set_xlabel('Frequency (Mhz)')
        self.axes.set_xlim((-120, 120))
        self.axes.set_ylim((-120, 120))
        self.canvas.draw()

    def clear_data(self):
        self.samples = None

    def show_constellation(self, samples):
        import timeit
        if False:
            maxsize = 32*1024
            if self.samples is not None:
                if self.samples.shape[1] + samples.shape[1] < maxsize:
                    self.samples = np.hstack([self.samples, samples])
                else:
                    self.samples = np.hstack([self.samples[:,samples.shape[1]:], samples])
            else:
                self.samples = samples
        else:
            self.samples = samples
        if len(self.constellation_graphs)>0:
            self.constellation_graphs[0].remove()
            self.constellation_graphs=[]
        #dtdebug(f'constellation: plotting {self.samples.shape} samples')
        start =timeit.timeit()
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
            graph = self.axes.scatter_density(self.samples[0,:], self.samples[1,:], vmin=0, vmax= 10., cmap=white_viridis)

        end =timeit.timeit()

        self.constellation_graphs.append(graph)
        if len(self.constellation_graphs) > 5:
            old = self.constellation_graphs.pop(0)
            old.remove()
        self.axes.set_xlim((-120, 120))
        self.axes.set_ylim((-120, 120))
        self.canvas.draw()
        wx.CallAfter(self.parent.Refresh)

    def clear_constellation(self):
        #dtdebug(f'clearing constellation samples')
        for x in self.constellation_graphs:
            x.remove()
        self.constellation_graphs = []
        self.canvas.draw()
        wx.CallAfter(self.parent.Refresh)

class SmallConstellationPlot(ConstellationPlotBase):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, (1.5,1.5), *args, **kwargs)

class ConstellationPlot(ConstellationPlotBase):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, (2.5,2.5), *args, **kwargs)

class SpectrumPlot(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.xlimits = None
        self.ylimits = None
        self.zoom_start_freq = None
        self.zoom_bandwidth=500 #zoom all graphs to this amount of spectrum, to avpid overlapping annotations
        self.parent = parent
        self.spectrum = pystatdb.spectrum.spectrum()
        self.scrollbar = wx.ScrollBar(self)
        self.scrollbar.SetScrollbar(0, self.zoom_bandwidth, 2100, 200)
        self.scrollbar.Bind(wx.EVT_COMMAND_SCROLL, self.OnScroll)

        self.figure = mpl.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.toolbar_sizer = wx.FlexGridSizer(1, 4, 0, 10)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        self.toolbar_sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.toolbar_sizer, 0, wx.LEFT | wx.EXPAND)

        self.sizer.Add(self.canvas, proportion=1,
                        flag=wx.LEFT | wx.TOP | wx.EXPAND)
        self.sizer.Add(self.scrollbar, proportion=0,
                        flag=wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.Bind ( wx.EVT_WINDOW_CREATE, self.OnCreateWindow )
        self.Parent.Bind ( wx.EVT_SHOW, self.OnShowHide )
        self.count =0
        from collections import OrderedDict
        self.spectra = OrderedDict()
        self.legend  = None
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.cycle_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.current_annot = None #currently selected annot
        self.do_detrend = True
        self.add_detrend_button()

    def on_motion(self, event):
        pass

    def OnShowHide(self,event):
        if event.IsShown():
            self.draw()

    def OnCreateWindow(self,event):
        if event.GetWindow() == self:
            self.start_freq, self.end_freq = self.parent.start_freq, self.parent.end_freq
            self.draw()
        else:
            pass

    def OnSlider(self, event):
        self.offset += 300
        self.pan_spectrum(self.offset)
        self.canvas.draw()

    def OnScroll(self, event):
        pos = event.GetPosition()
        offset =pos
        self.pan_spectrum(offset)

    def OnFix(self, event):
        self.adjust()
        self.canvas.draw()

    def draw(self):
        self.axes.clear()
        self.Fit()
        self.figure.subplots_adjust(left=0.05, bottom=0.1, right=0.98, top=0.92)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['top'].set_visible(False)
        self.axes.set_ylabel('dB')
        self.axes.set_xlabel('Frequency (Mhz)')
        self.axes.set_xlim((self.start_freq/1000., self.end_freq/1000.))
        self.canvas.draw()

    def add_detrend_button(self) :
        panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.toolbar_sizer.Add(panel, 0, wx.LEFT|wx.RIGHT, 10)
        sizer = wx.FlexGridSizer(3, 1, 0)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, size=(16, 16))
        button = wx.BitmapToggleButton(panel, wx.ID_ANY, label=bitmap)
        button.SetValue(self.do_detrend)
        sizer.Add(button, 1, wx.ALIGN_CENTER_VERTICAL, border=0)
        panel.SetSizer(sizer)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleDetrend, button)

    def add_legend_button(self, spectrum, color) :
        panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.toolbar_sizer.Add(panel, 0, wx.LEFT|wx.RIGHT, 10)
        sizer = wx.FlexGridSizer(3, 1, 0)
        static_line = wx.StaticLine(panel, wx.ID_ANY)
        static_line.SetMinSize((20, 2))
        static_line.SetBackgroundColour(wx.Colour(color))
        static_line.SetForegroundColour(wx.Colour(color))

        sizer.Add(static_line, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        button = wx.ToggleButton(panel, wx.ID_ANY, _(spectrum.label))
        sizer.Add(button, 0, 0, 0)
        button.spectrum = spectrum
        button.SetValue(1)

        self.close_button = wx.Button(panel, -1, "", style=wx.BU_NOTEXT)
        self.close_button.SetMinSize((32, -1))
        self.close_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_OTHER, (16, 16)))
        self.close_button.spectrum = spectrum
        sizer.Add(self.close_button, 0, 0, 0)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleAnnots, button)
        self.Bind(wx.EVT_BUTTON, self.OnCloseGraph, self.close_button)
        self.Layout()
        spectrum.legend_panel = panel

    def make_key(self, spectrum):
        sat = pychdb.sat_pos_str(spectrum.k.sat_pos)
        key = spectrum.filename
        return key

    def toggle_spectrum(self, spectrum):
        key = self.make_key(spectrum)
        s = self.spectra.get(key, None)
        if s is None:
            self.show_spectrum(spectrum)
        else:
            self.hide_spectrum(spectrum)

        self.canvas.draw()
        wx.CallAfter(self.parent.Refresh)

        return False

    def show_spectrum(self, spectrum):
        key = self.make_key(spectrum)
        s = self.spectra.get(key, None)
        if s is not None:
            self.hide_spectrum(spectrum)
            is_first = False
        else:
            is_first = len(self.spectra)==0
        s = Spectrum(self, spectrum, color=self.cycle_colors[len(self.spectra)])
        self.spectra[key] = s
        self.add_legend_button(s, s.color)
        s.show()
        if self.legend is not None:
            self.legend.remove()
        #self.pan_spectrum(0)
        self.pan_band(s.spec[0,0])
        self.canvas.draw()
        wx.CallAfter(self.parent.Refresh)

    def pan_spectrum(self, offset):
        xmin, ymin = (10700.+offset, -50)
        xmax, ymax = (10700+self.zoom_bandwidth +offset, -45)
        self.axes.set_xbound((xmin, xmax))
        self.canvas.draw()
        self.parent.Refresh()

    def pan_band(self, start):
        xmin, ymin = start, -50
        xmax, ymax = start + self.zoom_bandwidth, -45
        self.axes.set_xbound((xmin, xmax))
        self.canvas.draw()
        self.parent.Refresh()

    def hide_spectrum(self, spectrum):
        key = self.make_key(spectrum)
        s = self.spectra.get(key, None)
        if s is None:
            return
        s.legend_panel.Destroy()
        self.toolbar_sizer.Layout()
        s.clear()
        del self.spectra[key]
        if self.legend is not None:
            self.legend.remove()

    def get_limits(self):
        if self.spectra is None or len(self.spectra)==0:
            return ((10700., 12750.), (-60.0, -40.0))
        xlimits, ylimits = None, None
        for spectrum in self.spectra.values():
            xlimits = combine_ranges(xlimits, spectrum.xlimits)
            ylimits = combine_ranges(ylimits, spectrum.ylimits)
        return xlimits, ylimits

    def update_matplotlib_legend(self, spectrum):
        self.legend = self.figure.legend(ncol=len(self.spectra))

        for legline, key in zip(self.legend.get_lines(), self.spectra):
            legline.set_picker(True)  # Enable picking on the legend line.
            legline.key = key

    def on_pickSHOWHIDE(self, event):
        """
        show/hide graph by clicking on legend line
        """
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legline = event.artist
        key = legline.key
        dtdebug(f"toggling {key} for {legline}")
        origline = self.spectra[key].spectrum_graph[0]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        self.figure.canvas.draw()

    def set_current_annot(self, annot):
        if annot == self.current_annot:
            return
        if self.current_annot is not None:
            if self.current_annot.tp.scan_ok:
                color = 'green'
            elif self.current_annot.tp.scan_failed:
                color = 'red'
            else:
                color ='black'
            self.current_annot.set_color(color)
        color = 'blue'
        annot.set_color(color)
        self.current_annot = annot
        self.canvas.draw()

    def set_current_annot_status(self, mux, locked):
        if self.current_annot is None:
            return
        spectrum = self.current_annot.tp.spectrum
        if spectrum.annot_for_mux(mux) != self.current_annot:
            return
        self.current_annot.tp.scan_ok = locked
        self.current_annot.tp.scan_failed = not locked
        color = 'green' if locked  else 'red'
        self.current_annot.set_color(color)
        self.canvas.draw()

    def reset_current_annot_status(self, mux):
        if self.current_annot is None:
            return
        spectrum = self.current_annot.tp.spectrum
        if spectrum.annot_for_mux(mux) != self.current_annot:
            return
        self.current_annot.tp.scan_ok = False
        self.current_annot.tp.scan_failed = False
        color = 'blue'
        self.current_annot.set_color(color)
        self.canvas.draw()

    def set_current_tp(self, tp):
        """
        Highlight current tp
        """
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        for annot in tp.spectrum.annots:
            if annot.tp == tp:
                dtdebug(f'set current_tp: spec={tp.spectrum} tp={annot.tp}')
                self.set_current_annot(annot)
                return

    def on_pick(self, event):
        """
        show/hide graph by clicking on legend line
        """
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        what = event.artist
        for key,spectrum  in self.spectra.items():
            if what in spectrum.annots:
                dtdebug(f'Spectrum: pick annot {spectrum} tp={what.tp}')
                #import pdb; pdb.set_trace()
                self.set_current_annot(what)
                wx.CallAfter(self.parent.OnSelectMux, what.tp)
                return
        me = event.mouseevent
        freq  = me.xdata
        best_delta =  20000000
        best_annot = None
        dtdebug(f"Spectrum: pick freq={freq}")
        for key,spectrum  in self.spectra.items():
            if what == spectrum.hlines or what == spectrum.vlines:
                ind = event.ind[0]
                verts = what.get_paths()[ind].vertices
                f = (verts[1, 0] + verts[0, 0])/2
                annot, delta = spectrum.annot_for_freq(freq)
                if delta  < best_delta:
                    best_delta = delta
                    best_annot = annot
        if best_annot is not None:
            dtdebug(f'Spectrum: pick line spectrum={spectrum} tp={best_annot.tp}')
            self.set_current_annot(best_annot)
            wx.CallAfter(self.parent.OnSelectMux, best_annot.tp)
            return

    def OnCloseGraph(self, evt):
        spectrum = evt.GetEventObject().spectrum.spectrum
        self.hide_spectrum(spectrum)
        self.canvas.draw()
        self.parent.Refresh()

    def OnToggleAnnots(self, evt):
        spectrum = evt.GetEventObject().spectrum
        if False:
            if spectrum.spectrum_graph is not None:
                origline = spectrum.spectrum_graph[0]
                visible = not origline.get_visible()
                origline.set_visible(visible)

            if spectrum.hlines is not None:
                visible = not spectrum.hlines.get_visible()
                spectrum.hlines.set_visible(visible)

        if spectrum.vlines is not None:
            visible = not spectrum.vlines.get_visible()
            spectrum.vlines.set_visible(visible)

        for a in spectrum.annots:
            visible = not a.get_visible()
            a.set_visible(visible)


        self.figure.canvas.draw()
        self.parent.Refresh()

    def OnToggleDetrend(self, evt):
        self.do_detrend =  evt.GetEventObject().GetValue()
        spectra = []
        for key,spectrum in self.spectra.items():
            spectra.append(spectrum.spectrum)
        for spectrum in spectra:
            self.hide_spectrum(spectrum)
        for spectrum in spectra:
            self.show_spectrum(spectrum)
        self.figure.canvas.draw()
        self.parent.Refresh()

"""
solution to layout text boxes (freq,pol,symrate) suhc that they do not overlap with the vertical lines
pointing to spectral peaks, the horizontal lines describing bandwidth, and the curve itself
-boxes are either left aligned and then start at the vertical line, or rigth aligned and then end
 at the vertical line

-step 1 is to compute a baseline version which is above the curve and horizontal lines, has only left aligned text
 but can have overlap between boxes

-step 2 is to compute two overlap-free versions:
--2.a "increasing" version in which all boxes are right aligned and overlapping
  boxes are moved above their left neighbor. This requires a single pass over the data
--2.b "decreasing" version in which all boxes are left aligned and overlapping
  boxes are moved above their right neighbor. This requires a single pass over the data (but starting from the end)

-step 3 is to merge the increasing and decreasing versions as follows:
--start at the left wit the version having the lowest height; call this "current" version
--skip to the next (right) element. when the alternate version would be lower than the current version, attempt to
  switch version as follows (if switching is not possible, simply keep the current version)
  -switching from increasing to decreasing is always allowed as it creates no additional conflict (if the
   left element was increasing, it was right aligned and cannot cause overlap with the right element, which is
   left aligned in this case)
  -switching  from decreasing to increasing is allowed only the the current element will not overlap with  the increasing
   (=left aligned) version of its right neighbor. This means that swicthing will only be allowed between sepearated clusters
   of overlapping elements.


"""