import numpy as np
from scipy.integrate import odeint
import lmfit
from core import util
from .base_model import BaseModel


class SeicrdRlExtModel(BaseModel):
    params = ["incubation_period",
                    "critical_chance", "critical_time", 
                    "recovery_time_normal", "recovery_time_critical",
                    "death_chance_normal", "death_time_normal",
                    "death_chance_over", "death_time_over", 
                    "exposed_rate_critical", "k"]
                    
    def __init__(self, kabko):
        super().__init__(kabko) 
    
    def deriv(self, y, t, exposed_rate_normal, exposed_rate_critical, 
                    infectious_rate, 
                    critical_rate, critical_chance, 
                    recovery_rate_normal, recovery_rate_critical, 
                    death_rate_normal, death_chance_normal, 
                    death_rate_over, death_chance_over):
        
        population, susceptible, exposed_normal, exposed_over, infectious, critical_cared, critical_over, recovered, dead_normal, dead_over = y
        
        
        exposed_flow_normal = exposed_rate_normal(t) * susceptible * infectious / population
        exposed_flow_over = exposed_rate_critical * susceptible * critical_over / population
        
        infectious_flow_normal = infectious_rate * exposed_normal * 1
        infectious_flow_over = infectious_rate * exposed_over * 1
        
        recovery_flow_normal = recovery_rate_normal * infectious * (1-critical_chance)
        recovery_flow_critical = recovery_rate_critical * critical_cared * (1-death_chance_normal)
        
        death_flow_normal = death_rate_normal * critical_cared * death_chance_normal
        death_flow_over = death_rate_over * critical_over * death_chance_over
        
        #tricky part because it should be immediate
        
        #recovering or dying people will free up available care
        available_care = self.kabko.kapasitas_rs(t) - critical_cared + recovery_flow_critical + death_flow_normal
        if available_care < 0:
            raise Exception("available_care should never be negative")
        
        #overflow applying for hospital should take precedence
        #well it's not like it will matter in numbers since new critical people will take their place here
        
        critical_over_return = 1 * min(available_care, critical_over) * 1
        
        available_care_2 = available_care - critical_over_return
        if available_care_2 < 0:
            raise Exception("available_care_2 should never be negative")
        
        #next, the new criticals will flow in
        
        critical_flow = critical_rate * infectious * critical_chance
        critical_flow_cared = min(available_care_2, critical_flow)
        
        available_care_3 = available_care_2 - critical_flow_cared
        if available_care_3 < 0:
            raise Exception("available_care_3 should never be negative")
        
        #the remains of that flow will go to over compartment
        critical_flow_over = critical_flow - critical_flow_cared
        
        dSdt = -exposed_flow_normal - exposed_flow_over
        dENdt = exposed_flow_normal - infectious_flow_normal
        dEOdt = exposed_flow_over - infectious_flow_over
        dIdt = infectious_flow_normal + infectious_flow_over - recovery_flow_normal - critical_flow_cared - critical_flow_over
        dCCdt = critical_flow_cared + critical_over_return - recovery_flow_critical - death_flow_normal
        dCOdt = critical_flow_over - death_flow_over - critical_over_return
        dRdt = recovery_flow_normal + recovery_flow_critical
        dDNdt = death_flow_normal
        dDOdt = death_flow_over
        dPdt = dSdt + dENdt + dEOdt + dIdt + dCCdt + dCOdt + dRdt + dDNdt + dDOdt
        
        return dPdt, dSdt, dENdt, dEOdt, dIdt, dCCdt, dCOdt, dRdt, dDNdt, dDOdt
        
    def model(self, days, incubation_period,
                    critical_chance, critical_time, 
                    recovery_time_normal, recovery_time_critical,
                    death_chance_normal, death_time_normal,
                    death_chance_over, death_time_over, 
                    exposed_rate_critical, k,
                    **kwargs):
        
        #unpack rt values
        rt_values = util.get_kwargs_rt(kwargs, self.kabko.rt_count)
        rt_data = list(zip(self.kabko.rt_days, rt_values))
        rt_delta = util.rt_delta(rt_data, self.kabko.oldest_tanggal)
        r_0 = rt_values[0]
        
        #load values
        population = self.kabko.population
        
        # this is derived parameter
        infectious_period_opt = recovery_time_normal * (1-critical_chance) + critical_time * critical_chance #this is derived parameter
        infectious_rate = 1.0 / incubation_period # this is derived parameter
        recovery_rate_normal = 1.0 / recovery_time_normal # this is derived parameter
        death_rate_normal = 1.0 / death_time_normal # this is derived parameter
        critical_rate = 1.0 / critical_time # this is derived parameter
        recovery_rate_critical = 1.0 / recovery_time_critical #this is derived parameter
        death_rate_over = 1.0/death_time_over # this is a derived parameter
        
        def logistic_rt(t):
            return self.kabko.logistic_rt(r_0, rt_delta, t, k)

        def exposed_rate_normal(t):
            ret = logistic_rt(t) / infectious_period_opt
            return ret
        
        def r0_over(critical_over):
            return exposed_rate_critical * death_time_over * critical_chance * (critical_over/population)

        population_init, susceptible_init, exposed_normal_init, exposed_over_init, infectious_init, critical_cared_init, critical_over_init, recovered_init, dead_normal_init, dead_over_init = population, population-1, 1, 0, 0, 0, 0, 0, 0, 0  # initial conditions: one exposed, rest susceptible
        
        t = np.linspace(0, days-1, days) # days
        y0 = population_init, susceptible_init, exposed_normal_init, exposed_over_init, infectious_init, critical_cared_init, critical_over_init, recovered_init, dead_normal_init, dead_over_init # Initial conditions tuple

        
        # Integrate the SIR equations over the time grid, t.
        ret = odeint(self.deriv, y0, t, args=(
            exposed_rate_normal, exposed_rate_critical, 
            infectious_rate, 
            critical_rate, critical_chance, 
            recovery_rate_normal, recovery_rate_critical, 
            death_rate_normal, death_chance_normal, 
            death_rate_over, death_chance_over
        ))
        
        retT = ret.T
        population_2, susceptible, exposed_normal, exposed_over, infectious,  critical_cared, critical_over, recovered,  dead_normal, dead_over = retT
        
        kapasitas_rs_val = util.map_function(t, self.kabko.kapasitas_rs)
        #kapasitas_rs_val = np.zeros(days)
        
        exposed = util.sum_element(exposed_normal, exposed_over)
        dead = util.sum_element(dead_normal, dead_over)
        death_chance_val = [0] + [100 * dead[i] / sum(infectious_rate*exposed[:i]) if sum(infectious_rate*exposed[:i])>0 else 0 for i in range(1, len(t))]
        #death_chance_val = np.zeros(days)
        
        r0_normal_val = util.map_function(t, logistic_rt)
        r0_over_val = util.map_function(critical_over, r0_over)
        #r0_normal_val = np.zeros(days)
        #r0_over_val = np.zeros(days)
        
        exposed = util.sum_element(exposed_normal, exposed_over)
        critical = util.sum_element(critical_cared, critical_over)
        dead = util.sum_element(dead_normal, dead_over) 
        infected = np.array(util.sum_respectively([infectious, critical, dead, recovered]))
        
        return t, population_2, susceptible, exposed_normal, exposed_over, exposed, infectious, critical_cared, critical_over, critical, recovered, dead_normal, dead_over, dead, infected, death_chance_val, r0_normal_val, kapasitas_rs_val, r0_over_val
    
    def fitter(self, **kwargs):
                    
        #days = self.kabko.data_days(self.kabko.outbreak_shift(incubation_period))
        ret = self.model(**kwargs)
                    
        self.last_result_full = ret
        
        t, population, susceptible, exposed_normal, exposed_over, exposed, infectious, critical_cared, critical_over, critical, recovered, dead_normal, dead_over, dead, infected, death_chance_val, r0_normal_val, kapasitas_rs_val, r0_over_val = ret
        
        
        infectious_out = infectious
        critical_out = critical
        recovered_out = recovered
        dead_out = dead
        infected_out = infected
            
        results = []
        for d in self.datasets:
            if d == "infectious":
                results.append(infectious_out)
            elif d == "critical":
                results.append(critical_out)
            elif d == "recovered":
                results.append(recovered_out)
            elif d == "dead":
                results.append(dead_out)
            elif d == "infected":
                results.append(infected_out)
            else:
                raise ValueError("Invalid dataset: " + str(d))
                
        results = np.array(results)
        self.last_result = results
        return results
        

Model = SeicrdRlExtModel