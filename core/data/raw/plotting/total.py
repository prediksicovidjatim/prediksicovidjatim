import numpy as np
import matplotlib.pyplot as plt

from core.data.raw.plotting import RawDataPlotterBase
from core import util

class RawDataPlotterTotal:
    def __init__(self, data=None):
        self.t = None
        self.data = None
        self.base = RawDataPlotterBase()
        if data is not None:
            self.set_data(data)
            
    def set_data(self, data):
        l = len(data)
        if not self.t or l != len(self.t):
            #self.t = np.linspace(0, l-1, l)
            self.t = np.array([d.tanggal for d in data])
        self.data = data
        
    def post_plot(self, ax):
        util.date_plot(ax)
        util.post_plot(ax)
        
    def plot_main(self):
        data = self.data
        odr = np.array([d.odr for d in data])
        otg = np.array([d.otg for d in data])
        odp = np.array([d.odp.total for d in data])
        pdp = np.array([d.pdp.total for d in data])
        positif = np.array([d.positif.total for d in data])
        meninggal = np.array([d.total_meninggal() for d in data])
        total = np.array([d.total() for d in data])

        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_main(ax, self.t, odr, otg, odp, pdp, positif, meninggal, total)
        
        
        self.post_plot(ax)
        
        ax.title.set_text("Main (Total)")
        
        return fig
        
    def plot_main_lite(self):
        data = self.data
        odp = np.array([d.odp.total for d in data])
        pdp = np.array([d.pdp.total for d in data])
        positif = np.array([d.positif.total for d in data])
        meninggal = np.array([d.total_meninggal() for d in data])

        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_main_lite(ax, self.t, odp, pdp, positif, meninggal)

        self.post_plot(ax)
        
        ax.title.set_text("Main Lite (Total)")
        
        return fig
        
    def plot_odp(self):
        data = self.data
        belum_dipantau = np.array([d.odp.belum_dipantau for d in data])
        dipantau = np.array([d.odp.dipantau.total for d in data])
        selesai_dipantau = np.array([d.odp.selesai_dipantau for d in data])
        meninggal = np.array([d.odp.meninggal for d in data])
        total = np.array([d.odp.total for d in data])
        total_calc = np.array([d.odp.total_calc() for d in data])
        total_opt = np.array([d.odp.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_odp(ax, self.t, belum_dipantau, dipantau, selesai_dipantau, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("ODP (Total)")
        
        return fig
        
    def plot_odp_rawat(self):
        data = self.data
        rumah = np.array([d.odp.dipantau.rumah for d in data])
        gedung = np.array([d.odp.dipantau.gedung for d in data])
        rs = np.array([d.odp.dipantau.rs for d in data])
        total = np.array([d.odp.dipantau.total for d in data])
        total_calc = np.array([d.odp.dipantau.total_calc() for d in data])
        total_opt = np.array([d.odp.dipantau.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("ODP Dipantau (Total)")
        
        return fig
        
    def plot_pdp(self):
        data = self.data
        belum_diawasi = np.array([d.pdp.belum_diawasi for d in data])
        dirawat = np.array([d.pdp.dirawat.total for d in data])
        sehat = np.array([d.pdp.sehat for d in data])
        meninggal = np.array([d.pdp.meninggal for d in data])
        total = np.array([d.pdp.total for d in data])
        total_calc = np.array([d.pdp.total_calc() for d in data])
        total_opt = np.array([d.pdp.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_odp(ax, self.t, belum_diawasi, dirawat, sehat, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("PDP (Total)")
        
        return fig
        
    def plot_pdp_rawat(self):
        data = self.data
        rumah = np.array([d.pdp.dirawat.rumah for d in data])
        gedung = np.array([d.pdp.dirawat.gedung for d in data])
        rs = np.array([d.pdp.dirawat.rs for d in data])
        total = np.array([d.pdp.dirawat.total for d in data])
        total_calc = np.array([d.pdp.dirawat.total_calc() for d in data])
        total_opt = np.array([d.pdp.dirawat.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("PDP Dirawat (Total)")
        
        return fig
        
    def plot_positif(self):
        data = self.data
        dirawat = np.array([d.positif.dirawat.total for d in data])
        sembuh = np.array([d.positif.sembuh for d in data])
        meninggal = np.array([d.positif.meninggal for d in data])
        total = np.array([d.positif.total for d in data])
        total_calc = np.array([d.positif.total_calc() for d in data])
        total_opt = np.array([d.positif.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_positif(ax, self.t, dirawat, sembuh, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("Positif (Total)")
        
        return fig
        
    def plot_positif_rawat(self):
        data = self.data
        rumah = np.array([d.positif.dirawat.rumah for d in data])
        gedung = np.array([d.positif.dirawat.gedung for d in data])
        rs = np.array([d.positif.dirawat.rs for d in data])
        total = np.array([d.positif.dirawat.total for d in data])
        total_calc = np.array([d.positif.dirawat.total_calc() for d in data])
        total_opt = np.array([d.positif.dirawat.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("Positif Dirawat (Total)")
        
        return fig