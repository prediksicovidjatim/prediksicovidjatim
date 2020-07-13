
class Plotter:
    def __init__(t, **kwargs):
        self.t = t
        
        self.population = util.get_if_exists(kwargs, "population")
        self.susceptible = util.get_if_exists(kwargs, "susceptible")
        self.exposed = util.get_if_exists(kwargs, "exposed")
        self.exposed_normal = util.get_if_exists(kwargs, "exposed_normal")
        self.exposed_over = util.get_if_exists(kwargs, "exposed_over")
        self.infectious = util.get_if_exists(kwargs, "infectious")
        self.critical = util.get_if_exists(kwargs, "critical")
        self.critical_cared = util.get_if_exists(kwargs, "critical_cared")
        self.critical_over = util.get_if_exists(kwargs, "critical_over")
        self.recovered = util.get_if_exists(kwargs, "recovered")
        self.dead = util.get_if_exists(kwargs, "dead")
        self.dead_normal = util.get_if_exists(kwargs, "dead_normal")
        self.dead_over = util.get_if_exists(kwargs, "dead_over")
        self.kapasitas_rs = util.get_if_exists(kwargs, "kapasitas_rs")
        self.death_chance = util.get_if_exists(kwargs, "death_chance")
        self.r0_normal = util.get_if_exists(kwargs, "r0_normal")
        self.r0_over = util.get_if_exists(kwargs, "r0_over")
        
        self.exposed_normal = self.exposed_normal or self.exposed
        self.critical_cared = self.critical_cared or self.critical
        self.dead_normal = self.dead_normal or self.dead
            
        if not self.exposed and self.exposed_normal:
            self.exposed = util.sum_element(self.exposed_normal, self.exposed_over) if self.exposed_over else self.exposed_normal
            
        if not self.critical and self.critical_cared:
            self.critical = util.sum_element(self.critical_cared, self.critical_over) if self.critical_over else self.critical_cared
            
        if not self.dead and self.dead_normal:
            self.dead = util.sum_element(self.dead_normal, self.dead_over) if self.dead_over else self.dead_normal
            
        self.r0_overall = util.sum_element(self.r0_normal, self.r0_over) if self.r0_normal and self.r0_over else None
        
        if self.exposed:
            self.daily_exposed = util.delta(self.exposed)
        if self.infectious:
            self.daily_infectious = util.delta(self.infectious)
        if self.critical:
            self.daily_critical = util.delta(self.critical)
        if self.recovered:
            self.daily_recovered = util.delta(self.recovered)
        if self.dead:
            self.daily_dead = util.delta(self.dead)
            
        self.daily_susceptible = util.delta(self.susceptible) if self.susceptible else None
        self.daily_exposed = util.delta(self.exposed) if self.exposed else None
        self.daily_infectious = util.delta(self.infectious) if self.infectious else None
        self.daily_critical = util.delta(self.critical) if self.critical else None
        self.daily_recovered = util.delta(self.recovered) if self.recovered else None
        self.daily_dead = util.delta(self.dead) if self.dead else None
            
        #config.init_plot()
        
    def plot_r0(self, ax):
        if self.r0_normal:
            ax.plot(self.t, self.r0_normal, 'y', alpha=0.5, linewidth=2, label='R0 normal')
        if self.r0_over:
            ax.plot(self.t, self.r0_over, 'r', alpha=0.5, linewidth=2, label='R0 over')
        if self.r0_overall:
            ax.plot(self.t, self.r0_overall, 'orange', alpha=0.7, linewidth=2, label='R0 overall')

        ax.title.set_text('R0 over time')
        
    def plot_death_chance(self, ax):
        if self.death_chance:
            util._plot_single(ax, self.t, self.death_chance, title="Death Chance over Time", label="Death chance", color="orange")
        
    def plot_over(self, ax):
        if self.exposed_over:
            ax.plot(self.t, self.exposed_over, 'blue', alpha=0.7, linewidth=2, label='Exposed by Neglected')
        if self.critical_over:
            ax.plot(self.t, self.critical_over, 'orange', alpha=0.7, linewidth=2, label="Critical but Neglected")
        if self.dead_over:
            ax.plot(self.t, self.dead_over, 'black', alpha=0.7, linewidth=2, label='Dead by Neglect')
        
        ax.title.set_text('Insufficient Healthcare')
        
    def plot_healthcare(self, ax, t, critical_cared, kapasitas_rs):
        if self.critical_cared:
            ax.plot(self.t, self.critical_cared, 'blue', alpha=0.7, linewidth=2, label='Critical cared')
        if self.kapasitas_rs:
            ax.plot(self.t, self.kapasitas_rs, 'orange', alpha=0.7, linewidth=2, label="Healthcare Limit")
        
        ax.title.set_text('Healthcare limit')
        
    def plot(self, f):
        fig, ax = plt.subplots(1, 1)
        f(ax)
        util.post_plot(ax)
        return fig
        
    def plot_main(self, ax):
        self._plot_main(ax, self.t, susceptible=self.susceptible, exposed=self.exposed, infectious=self.infectious, critical=self.critical, recovered=self.recovered, dead=self.dead, kapasitas_rs=self.kapasitas_rs, population=self.population, title="Main (Total)")
    
    def _plot_main(self, ax, t, susceptible=None, exposed=None, infectious=None, critical=None, recovered=None, dead=None, kapasitas_rs=None, population=None, title="Main"):
        if susceptible:
            ax.plot(t, susceptible, 'b', alpha=0.7, label='Susceptible')
        if exposed:
            ax.plot(t, exposed, 'y', alpha=0.7, label='Exposed')
        if infectious:
            ax.plot(t, infectious, 'r', alpha=0.7, label='Infectious')
        if critical:
            ax.plot(t, critical, 'orange', alpha=0.7, label='Critical')
        if recovered:
            ax.plot(t, recovered, 'g', alpha=0.7, label='Recovered')
        if dead:
            ax.plot(t, dead, 'black', alpha=0.7, label='Dead')
        if kapasitas_rs:
            ax.plot(t, kapasitas_rs, 'red', alpha=0.3, label='Healthcare', ls='dotted')
        if population:
            ax.plot(t, population, 'grey', alpha=0.3, label='Population', ls='dotted')
        
        ax.title.set_text(title)

    def plot_daily(self, ax):
        self._plot_main(ax, self.t, susceptible=self.daily_susceptible, exposed=self.daily_exposed, infectious=self.daily_infectious, critical=self.daily_critical, recovered=self.daily_recovered, dead=self.daily_dead, title="Main (Harian)")
        