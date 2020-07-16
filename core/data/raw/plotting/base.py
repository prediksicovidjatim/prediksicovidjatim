import numpy as np
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from core import util

class RawDataPlotterBase:
    def __init__(self):
        pass

    def plot_main(self, ax, t, odr, otg, odp, pdp, positif, meninggal, total):
        ax.plot(t, odr, 'green', alpha=0.7, label='ODR')
        ax.plot(t, otg, 'blue', alpha=0.7, label='OTG')
        self.plot_main_lite(ax, t, odp, pdp, positif, meninggal)
        ax.plot(t, total, 'grey', alpha=0.7, label='Total (Calc)')

    def plot_main_lite(self, ax, t, odp, pdp, positif, meninggal):
        ax.plot(t, odp, 'yellow', alpha=0.7, label='ODP')
        ax.plot(t, pdp, 'orange', alpha=0.7, label='PDP')
        ax.plot(t, positif, 'red', alpha=0.7, label='Positif')
        ax.plot(t, meninggal, 'black', alpha=0.7, label='Meninggal')

        ax.set_xlabel('Time (days)', labelpad=10)
        
    def plot_odp(self, ax, t, belum_dipantau, dipantau, selesai_dipantau, meninggal, total, total_calc, total_opt):
        
        ax.plot(t, belum_dipantau, 'yellow', alpha=0.7, label='Belum Dipantau')
        ax.plot(t, dipantau, 'orange', alpha=0.7, label='Dipantau')
        ax.plot(t, selesai_dipantau, 'red', alpha=0.7, label='Selesai Dipantau')
        ax.plot(t, meninggal, 'black', alpha=0.7, label='Meninggal')
        ax.plot(t, total, 'grey', alpha=0.7, label='Total')
        ax.plot(t, total_calc, 'brown', alpha=0.7, label='Total (Calc)')
        ax.plot(t, total_opt, 'purple', alpha=0.7, label='Total (Opt)')

        ax.set_xlabel('Time (days)', labelpad=10)
        
    def plot_rawat(self, ax, t, rumah, gedung, rs, total, total_calc, total_opt):
        
        ax.plot(t, rumah, 'yellow', alpha=0.7, label='Isolasi Rumah')
        ax.plot(t, gedung, 'orange', alpha=0.7, label='Isolasi Gedung')
        ax.plot(t, rs, 'red', alpha=0.7, label='Isolasi RS')
        ax.plot(t, total, 'grey', alpha=0.7, label='Total')
        ax.plot(t, total_calc, 'brown', alpha=0.7, label='Total (Calc)')
        ax.plot(t, total_opt, 'purple', alpha=0.7, label='Total (Opt)')

        ax.set_xlabel('Time (days)', labelpad=10)
        
    def plot_pdp(self, ax, t, belum_diawasi, dirawat, sehat, meninggal, total, total_calc, total_opt):
        
        ax.plot(t, belum_diawasi, 'yellow', alpha=0.7, label='Belum Diawasi')
        ax.plot(t, dirawat, 'orange', alpha=0.7, label='Dirawat')
        ax.plot(t, sehat, 'red', alpha=0.7, label='Sehat')
        ax.plot(t, meninggal, 'black', alpha=0.7, label='Meninggal')
        ax.plot(t, total, 'grey', alpha=0.7, label='Total')
        ax.plot(t, total_calc, 'brown', alpha=0.7, label='Total (Calc)')
        ax.plot(t, total_opt, 'purple', alpha=0.7, label='Total (Opt)')

        ax.set_xlabel('Time (days)', labelpad=10)
        
    def plot_positif(self, ax, t, dirawat, sembuh, meninggal, total, total_calc, total_opt):
        
        ax.plot(t, dirawat, 'red', alpha=0.7, label='Dirawat')
        ax.plot(t, sembuh, 'green', alpha=0.7, label='Sembuh')
        ax.plot(t, meninggal, 'black', alpha=0.7, label='Meninggal')
        ax.plot(t, total, 'grey', alpha=0.7, label='Total')
        ax.plot(t, total_calc, 'brown', alpha=0.7, label='Total (Calc)')
        ax.plot(t, total_opt, 'purple', alpha=0.7, label='Total (Opt)')

        ax.set_xlabel('Time (days)', labelpad=10)