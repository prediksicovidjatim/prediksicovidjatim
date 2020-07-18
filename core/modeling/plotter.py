import matplotlib.pyplot as plt
from core import util

class ModelPlotter:
    def __init__(self, result):
        self.result = result
            
        #config.init_plot()
        
    def plot_r0(self, ax):
        if self.result.r0_normal is not None:
            ax.plot(self.result.t, self.result.r0_normal, 'y', alpha=0.5, linewidth=2, label='R0 normal')
        if self.result.r0_over is not None:
            ax.plot(self.result.t, self.result.r0_over, 'r', alpha=0.5, linewidth=2, label='R0 over')
        if self.result.r0_overall is not None:
            ax.plot(self.result.t, self.result.r0_overall(), 'orange', alpha=0.7, linewidth=2, label='R0 overall')

        ax.title.set_text('R0 over time')
        
    def plot_mortality_rate(self, ax):
        if self.result.mortality_rate is not None:
            util._plot_single(ax, self.result.t, self.result.mortality_rate, title="Mortality Rate over Time", label="Mortality rate", color="orange")
        
    def plot_over(self, ax):
        if self.result.exposed_over is not None:
            ax.plot(self.result.t, self.result.exposed_over, 'blue', alpha=0.7, linewidth=2, label='Exposed by Neglected')
        if self.result.critical_over is not None:
            ax.plot(self.result.t, self.result.critical_over(), 'orange', alpha=0.7, linewidth=2, label="Critical but Neglected")
        if self.result.dead_over is not None:
            ax.plot(self.result.t, self.result.dead_over, 'black', alpha=0.7, linewidth=2, label='Dead by Neglect')
        
        ax.title.set_text('Insufficient Healthcare')
        
    def plot_healthcare(self, ax):
        if self.result.critical_cared is not None:
            ax.plot(self.result.t, self.result.critical_cared(), 'blue', alpha=0.7, linewidth=2, label='Critical cared')
        if self.result.kapasitas_rs is not None:
            ax.plot(self.result.t, self.result.kapasitas_rs, 'orange', alpha=0.7, linewidth=2, label="Healthcare Limit")
        
        ax.title.set_text('Healthcare limit')
        
    def plot(self, f, *args, **kwargs):
        fig, ax = plt.subplots(1, 1)
        f(ax, *args, **kwargs)
        util.post_plot(ax)
        return fig
        
    def plot_main(self, ax):
        self._plot_main(ax, self.result.t, susceptible=self.result.susceptible, exposed=self.result.exposed(), infectious=self.result.infectious, critical=self.result.critical, recovered=self.result.recovered(), dead=self.result.dead(), kapasitas_rs=self.result.kapasitas_rs, population=self.result.population, title="Main (Total)")
        
    def plot_main_lite(self, ax):
        self._plot_main(ax, self.result.t, exposed=self.result.exposed(), infectious=self.result.infectious, critical=self.result.critical, recovered=self.result.recovered(), dead=self.result.dead(), kapasitas_rs=self.result.kapasitas_rs, title="Main (Total, Lite)")
    
    def plot_main_data(self, ax, data, data_length=None):
        self._plot_data(
            ax, 
            self.result.t, 
            **self.result.get_datasets(data.keys()),
            kapasitas_rs=self.result.kapasitas_rs,
            is_data=False
        )
        data_length = data_length or len(list(data.values())[0])
        self._plot_data(
            ax, 
            self.result.t[:data_length], 
            is_data=True,
            **data
        )
        ax.title.set_text("Model-Data Comparison")
        
    def _plot_data(self, ax, t, infectious=None, critical_cared=None, infectious_all=None, recovered=None, dead=None, infected=None, kapasitas_rs=None, is_data=False):
        line_style = "-" if is_data else "-"
        label_suffix = " (data)" if is_data else " (model)"
        alpha = 0.7 if is_data else 0.4
        line_width = 3 if is_data else 2
        if infectious is not None:
            ax.plot(t, infectious, 'blue', alpha=alpha, label='Infectious'+label_suffix, linewidth=line_width, ls=line_style)
        if critical_cared is not None:
            ax.plot(t, critical_cared, 'red', alpha=alpha, label='Positif Rawat RS'+label_suffix, linewidth=line_width, ls=line_style)
        if infectious_all is not None:
            ax.plot(t, infectious_all, 'purple', alpha=alpha, label='Positif Aktif'+label_suffix, linewidth=line_width, ls=line_style)
        if recovered is not None:
            ax.plot(t, recovered, 'green', alpha=alpha, label='Positif Sembuh'+label_suffix, linewidth=line_width, ls=line_style)
        if dead is not None:
            ax.plot(t, dead, 'black', alpha=alpha, label='Positif Meninggal'+label_suffix, linewidth=line_width, ls=line_style)
        if infected is not None:
            ax.plot(t, infected, 'grey', alpha=alpha, label='Positif Total'+label_suffix, linewidth=line_width, ls=line_style)
        if kapasitas_rs is not None:
            ax.plot(t, kapasitas_rs, 'orange', alpha=0.3, label='Kapasitas RS', ls=':')
        
        
    def _plot_main(self, ax, t, susceptible=None, exposed=None, infectious=None, critical=None, recovered=None, dead=None, kapasitas_rs=None, population=None, title="Main", line_style="-"):
        if susceptible is not None:
            ax.plot(t, susceptible, 'b', alpha=0.7, label='Susceptible', ls=line_style)
        if exposed is not None:
            ax.plot(t, exposed, 'y', alpha=0.7, label='Exposed', ls=line_style)
        if infectious is not None:
            ax.plot(t, infectious, 'r', alpha=0.7, label='Infectious', ls=line_style)
        if critical is not None:
            ax.plot(t, critical, 'orange', alpha=0.7, label='Critical', ls=line_style)
        if recovered is not None:
            ax.plot(t, recovered, 'g', alpha=0.7, label='Recovered', ls=line_style)
        if dead is not None:
            ax.plot(t, dead, 'black', alpha=0.7, label='Dead', ls=line_style)
        if kapasitas_rs is not None:
            ax.plot(t, kapasitas_rs, 'red', alpha=0.3, label='Healthcare', ls='dotted')
        if population is not None:
            ax.plot(t, population, 'grey', alpha=0.3, label='Population', ls='dotted')
        
        ax.title.set_text(title)

    def plot_daily(self, ax):
        self._plot_main(ax, self.result.t, susceptible=self.result.daily_susceptible(), exposed=self.result.daily_exposed(), infectious=self.result.daily_infectious(), critical=self.result.daily_critical(), recovered=self.result.daily_recovered(), dead=self.result.daily_dead(), title="Main (Harian)")

    def plot_daily_lite(self, ax):
        self._plot_main(ax, self.result.t, exposed=self.result.daily_exposed(), infectious=self.result.daily_infectious(), critical=self.result.daily_critical(), recovered=self.result.daily_recovered(), dead=self.result.daily_dead(), title="Main (Harian)")
        