import numpy as np
import matplotlib.pyplot as plt

from core.data.raw.plotting import RawDataPlotterBase
from core import util

class RawDataPlotterHarian:
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
        odr = util.delta([d.odr for d in data])
        otg = util.delta([d.otg for d in data])
        odp = util.delta([d.odp.total for d in data])
        pdp = util.delta([d.pdp.total for d in data])
        positif = util.delta([d.positif.total for d in data])
        meninggal = util.delta([d.total_meninggal() for d in data])
        total = util.delta([d.total() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_main(ax, self.t, odr, otg, odp, pdp, positif, meninggal, total)

        self.post_plot(ax)
        
        ax.title.set_text("Main (Harian)")
        
        return fig
        
    def plot_main_lite(self):
        data = self.data
        odp = util.delta([d.odp.total for d in data])
        pdp = util.delta([d.pdp.total for d in data])
        positif = util.delta([d.positif.total for d in data])
        meninggal = util.delta([d.total_meninggal() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_main_lite(ax, self.t, odp, pdp, positif, meninggal)

        self.post_plot(ax)
        
        ax.title.set_text("Main Lite (Harian)")
        
        return fig
        
    def plot_odp(self):
        data = self.data
        belum_dipantau = util.delta([d.odp.belum_dipantau for d in data])
        dipantau = util.delta([d.odp.dipantau.total for d in data])
        selesai_dipantau = util.delta([d.odp.selesai_dipantau for d in data])
        meninggal = util.delta([d.odp.meninggal for d in data])
        total = util.delta([d.odp.total for d in data])
        total_calc = util.delta([d.odp.total_calc() for d in data])
        total_opt = util.delta([d.odp.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_odp(ax, self.t, belum_dipantau, dipantau, selesai_dipantau, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("ODP (Harian)")
        
        return fig
        
    def plot_odp_rawat(self):
        data = self.data
        rumah = util.delta([d.odp.dipantau.rumah for d in data])
        gedung = util.delta([d.odp.dipantau.gedung for d in data])
        rs = util.delta([d.odp.dipantau.rs for d in data])
        total = util.delta([d.odp.dipantau.total for d in data])
        total_calc = util.delta([d.odp.dipantau.total_calc() for d in data])
        total_opt = util.delta([d.odp.dipantau.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("ODP Dipantau (Harian)")
        
        return fig
        
    def plot_pdp(self):
        data = self.data
        belum_diawasi = util.delta([d.pdp.belum_diawasi for d in data])
        dirawat = util.delta([d.pdp.dirawat.total for d in data])
        sehat = util.delta([d.pdp.sehat for d in data])
        meninggal = util.delta([d.pdp.meninggal for d in data])
        total = util.delta([d.pdp.total for d in data])
        total_calc = util.delta([d.pdp.total_calc() for d in data])
        total_opt = util.delta([d.pdp.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_odp(ax, self.t, belum_diawasi, dirawat, sehat, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("PDP (Harian)")
        
        return fig
        
    def plot_pdp_rawat(self):
        data = self.data
        rumah = util.delta([d.pdp.dirawat.rumah for d in data])
        gedung = util.delta([d.pdp.dirawat.gedung for d in data])
        rs = util.delta([d.pdp.dirawat.rs for d in data])
        total = util.delta([d.pdp.dirawat.total for d in data])
        total_calc = util.delta([d.pdp.dirawat.total_calc() for d in data])
        total_opt = util.delta([d.pdp.dirawat.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("PDP Dirawat (Harian)")
        
        return fig
        
    def plot_positif(self):
        data = self.data
        dirawat = util.delta([d.positif.dirawat.total for d in data])
        sembuh = util.delta([d.positif.sembuh for d in data])
        meninggal = util.delta([d.positif.meninggal for d in data])
        total = util.delta([d.positif.total for d in data])
        total_calc = util.delta([d.positif.total_calc() for d in data])
        total_opt = util.delta([d.positif.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_positif(ax, self.t, dirawat, sembuh, meninggal, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("Positif (Harian)")
        
        return fig
        
    def plot_positif_rawat(self):
        data = self.data
        rumah = util.delta([d.positif.dirawat.rumah for d in data])
        gedung = util.delta([d.positif.dirawat.gedung for d in data])
        rs = util.delta([d.positif.dirawat.rs for d in data])
        total = util.delta([d.positif.dirawat.total for d in data])
        total_calc = util.delta([d.positif.dirawat.total_calc() for d in data])
        total_opt = util.delta([d.positif.dirawat.total_opt() for d in data])
        
        fig, ax = plt.subplots(1, 1)
        
        self.base.plot_rawat(ax, self.t, rumah, gedung, rs, total, total_calc, total_opt)

        self.post_plot(ax)
        
        ax.title.set_text("Positif Dirawat (Harian)")
        
        return fig