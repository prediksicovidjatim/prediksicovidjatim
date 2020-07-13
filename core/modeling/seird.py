import numpy as np
from scipy.integrate import odeint
import lmfit
from core import util
from .base_model import BaseModel

class SeirdModel(BaseModel):
    params = ["incubation_period", "recovery_time", "death_chance", "death_time"]
    
    def __init__(self, kabko):
        super().__init__(kabko) 
    
    def deriv(self, y, t, exposed_rate, infectious_rate, recovery_rate, death_rate, death_chance):
        
        population, susceptible, exposed, infectious, recovered, dead = y
        exposed_flow = exposed_rate * susceptible * infectious / population
        infectious_flow = infectious_rate * exposed * 1
        recovery_flow = recovery_rate * infectious * (1-death_chance)
        death_flow = death_rate * infectious * death_chance
        dSdt = -exposed_flow
        dEdt = exposed_flow - infectious_flow
        dIdt = infectious_flow - recovery_flow - death_flow
        dRdt = recovery_flow
        dDdt = death_flow
        dPdt = dSdt + dEdt + dIdt + dRdt + dDdt
        return dPdt, dSdt, dEdt, dIdt, dRdt, dDdt
        
    def model(self, days, r_0, incubation_period,
                    recovery_time,
                    death_chance, death_time, **kwargs):
        
        #load values
        population = self.kabko.population
        
        # this is derived parameter
        infectious_period_opt = recovery_time_normal * (1-death_chance) + death_time * death_chance #this is derived parameter
        infectious_rate = 1.0 / incubation_period # this is derived parameter
        recovery_rate = 1.0 / recovery_time # this is derived parameter
        death_rate = 1.0 / death_time # this is derived parameter

        exposed_rate = r0 / infectious_period_opt

        population_init, susceptible_init, exposed_init, infectious_init, recovered_init, dead_init = population, population-1, 1, 0, 0, 0  # initial conditions: one exposed, rest susceptible
        
        t = np.linspace(0, days-1, days) # days
        y0 = population_init, susceptible_init, exposed_init, infectious_init, recovered_init, dead_init # Initial conditions tuple

        
        # Integrate the SIR equations over the time grid, t.
        ret = odeint(self.deriv, y0, t, args=(
            exposed_rate, infectious_rate, recovery_rate, death_rate, death_chance
        ))
        
        retT = ret.T
        population_2, susceptible, exposed, infectious, recovered, dead = retT
        
        death_chance_val = [0] + [100 * dead[i] / sum(infectious_rate*exposed[:i]) if sum(infectious_rate*exposed[:i])>0 else 0 for i in range(1, len(t))]
        #death_chance_val = np.zeros(days)
        
        infected = np.array(util.sum_respectively([infectious, dead, recovered]))
        
        return t, population_2, susceptible, exposed, infectious, recovered, dead, infected, death_chance_val
    
    def fitter(self, x, days, r_0, incubation_period,
                    recovery_time, 
                    death_chance, death_time, **kwargs):
        #days = self.kabko.data_days(self.kabko.outbreak_shift(incubation_period))
        ret = self.model(days, r_0, incubation_period,
                    recovery_time, 
                    death_chance, death_time,
                    k)
        dead = ret[7]
        return dead[x]
    
    def fit(self):
        mod = lmfit.Model(self.fitter)
        
        self.kabko.apply_params(mod)
        
        outbreak_shift = self.kabko.outbreak_shift(
            self.kabko.params["incubation_period"].init
        )
        
        days = self.kabko.data_days(outbreak_shift)
        
        mod.set_param_hint("days", value=days, vary=False)

        params = mod.make_params()
        
        x_data = np.linspace(0, days - 1, days, dtype=int)
        
        y_data = util.shift_array(
            self.kabko.dead, 
            outbreak_shift
        )

        result = mod.fit(y_data, params, method="least_squares", x=x_data)
        

        #result.plot_fit(datafmt="-");
        
        return result

Model = SeirdModel