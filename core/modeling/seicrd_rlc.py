import numpy as np
from scipy.integrate import odeint, solve_ivp
import lmfit
from core import util
from .base_model import BaseModel
import math

class SeicrdRlcModelResult:
    def __init__(self, t, population, susceptible, exposed_normal, exposed_over, infectious, critical, recovered_normal, recovered_critical, dead_normal, dead_over, mortality_rate, r0_normal, kapasitas_rs, r0_over, r0_overall, test_coverage):
        self.t = t
        self.population = population
        self.susceptible = susceptible
        self.exposed_normal = exposed_normal
        self.exposed_over = exposed_over
        self.infectious = infectious
        self.critical = critical
        self.recovered_normal = recovered_normal
        self.recovered_critical = recovered_critical
        self.dead_normal = dead_normal
        self.dead_over = dead_over
        self.mortality_rate = mortality_rate
        self.r0_normal = r0_normal
        self.kapasitas_rs = kapasitas_rs
        self.r0_over = r0_over
        self.r0_overall = r0_overall
        self.test_coverage = test_coverage
        
    def exposed(self):
        return self.exposed_normal + self.exposed_over
        
    def critical_cared(self):
        return SeicrdRlcModel.critical_cared(self.critical, self.kapasitas_rs)
        
    def critical_over(self):
        return SeicrdRlcModel.critical_over(self.critical, self.kapasitas_rs)
        
    def infectious_all(self):
        return self.infectious + self.critical
        
    def recovered(self):
        return self.recovered_normal + self.recovered_critical
        
    def dead(self):
        return self.dead_normal + self.dead_over
        
    def over(self):
        return self.critical_over() + self.dead_over
        
    def infectious_scaled(self):
        return self.test_coverage * (self.infectious + self.critical_over())
        
    def critical_cared_scaled(self):
        return self.critical_cared()
        
    def infectious_all_scaled(self):
        return self.infectious_scaled() + self.critical_cared_scaled()
        
    def recovered_scaled(self):
        return self.test_coverage * self.recovered_normal + self.recovered_critical
        
    def dead_scaled(self):
        return self.test_coverage * self.dead_over + self.dead_normal
        
    def infected_scaled(self):
        return self.infectious_all_scaled() + self.recovered_scaled() + self.dead_scaled()
    
    def daily_susceptible(self):
        return util.delta(self.susceptible)
        
    def daily_exposed_normal(self):
        return util.delta(self.exposed_normal)
        
    def daily_exposed_over(self):
        return util.delta(self.exposed_over)
        
    def daily_exposed(self):
        return util.delta(self.exposed())
        
    def daily_infectious(self):
        return util.delta(self.infectious)
        
    def daily_critical_cared(self):
        return util.delta(self.critical_cared())
        
    def daily_critical_over(self):
        return util.delta(self.critical_over())
        
    def daily_critical(self):
        return util.delta(self.critical)
        
    def daily_infectious_all(self):
        return util.delta(self.infectious_all())
        
    def daily_recovered_normal(self):
        return util.delta(self.recovered_normal)
        
    def daily_recovered_critical(self):
        return util.delta(self.recovered_critical)
        
    def daily_recovered(self):
        return util.delta(self.recovered())
        
    def daily_dead_normal(self):
        return util.delta(self.dead_normal)
        
    def daily_dead_over(self):
        return util.delta(self.dead_over)
        
    def daily_dead(self):
        return util.delta(self.dead())
        
    def daily_over(self):
        return tuil.delta(self.over())
    
    def daily_infectious_scaled(self):
        return util.delta(self.infectious_scaled())
        
    def daily_critical_cared_scaled(self):
        return util.delta(self.critical_cared_scaled())
        
    def daily_infectious_all_scaled(self):
        return util.delta(self.infectious_all_scaled())
        
    def daily_recovered_scaled(self):
        return util.delta(self.recovered_scaled())
        
    def daily_dead_scaled(self):
        return util.delta(self.dead_scaled())
        
    def daily_infected_scaled(self):
        return util.delta(self.infected_scaled())
        
    def get_dataset(self, d, shift=0):
        # TODO
        ret = None
        if d == "infectious":
            ret = self.infectious_scaled()
        elif d == "critical_cared":
            ret = self.critical_cared_scaled()
        elif d == "infectious_all":
            ret = self.infectious_all_scaled()
        elif d == "recovered":
            ret = self.recovered_scaled()
        elif d == "dead":
            ret = self.dead_scaled()
        elif d == "infected":
            ret = self.infected_scaled()
        else:
            raise ValueError("Invalid dataset: " + str(d))
        return np.array(ret) if not shift else util.shift_array(ret, shift)
        
    def get_datasets(self, datasets, shift=0):
        return {k:self.get_dataset(k, shift) for k in datasets}
        
    def get_datasets_values(self, datasets, shift=0):
        return np.array([self.get_dataset(k, shift) for k in datasets])
        
class SeicrdRlcModel(BaseModel):
    params = ["infectious_rate",
                    "critical_chance", "critical_rate", 
                    "recovery_rate_normal", "recovery_rate_critical",
                    "death_chance_normal", "death_rate_normal",
                    "death_chance_over", "death_rate_over", 
                    "exposed_rate_over", "k", "kapasitas_rs_mul",
                    "test_coverage_0", "test_coverage_increase", "test_coverage_max"]
                    
    def __init__(self, kabko):
        super().__init__(kabko) 
        self.prev_dydt = None
    
    def critical_cared(critical, kapasitas_rs):
        ret = critical[:]
        return np.clip(ret, a_min=None, a_max=kapasitas_rs)
    
    def critical_over(critical, kapasitas_rs):
        ret = critical-kapasitas_rs
        return np.clip(ret, a_min=0, a_max=None)
        
    def deriv(self, y, t, population,
    #def deriv(self, t, y, population,
                    exposed_rate_normal, exposed_rate_over, 
                    infectious_rate, 
                    critical_rate, critical_chance, 
                    recovery_rate_normal, recovery_rate_critical, 
                    death_rate_normal, death_chance_normal, 
                    death_rate_over, death_chance_over, kapasitas_rs):
                    
        population_y, susceptible, exposed_normal, exposed_over, infectious, critical, recovered_normal, recovered_critical, dead_normal, dead_over = y
        y_name = ("population", "susceptible", "exposed_normal", "exposed_over", "infectious", "critical", "recovered_normal", "recovered_critical", "dead_normal", "dead_over")
        population_y, susceptible, exposed_normal, exposed_over, infectious, critical, recovered_normal, recovered_critical, dead_normal, dead_over = [util.sanity_check_init(*args) for args in zip(y_name, y)]
        
        exposed_flow_normal = exposed_rate_normal(t) * susceptible * infectious / population
        
        
        infectious_flow_normal = infectious_rate * exposed_normal * 1
        infectious_flow_over = infectious_rate * exposed_over * 1
        
        recovery_flow_normal = recovery_rate_normal * infectious * (1.0-critical_chance)
        critical_flow = critical_rate * infectious * critical_chance
        
        #tricky part because I must not take y+dy (the flow) into account, because I need dt to do that
        kapasitas_rs_val = kapasitas_rs(t)
        critical_cared = min(kapasitas_rs_val, critical)
        critical_over = max(0, critical-critical_cared)
        
        
        if critical_over > 0 and critical_cared < kapasitas_rs_val:
            raise Exception("There can't be critical_over if critical_cared is below kapasitas_rs_val")
        
        exposed_flow_over = exposed_rate_over * susceptible * critical_over / population
        recovery_flow_critical = recovery_rate_critical * critical_cared * (1.0-death_chance_normal)
        
        
        
        if recovery_flow_normal > infectious:
            raise Exception("There can't be more people recovering than infected people. (%f, %f, %f. %f)" % (recovery_rate_normal, critical_chance, recovery_flow_normal, infectious))
        
        if recovery_flow_critical > critical_cared:
            raise Exception("There can't be more people recovering than being cared")
        
        
        death_flow_normal = death_rate_normal * critical_cared * death_chance_normal
        death_flow_over = death_rate_over * critical_over * death_chance_over
        
        if death_flow_over > 0 and critical_cared < kapasitas_rs_val:
            raise Exception("There can't be death_flow_over if critical_cared is below kapasitas_rs_val")
        
        flow = exposed_flow_normal, exposed_flow_over, infectious_flow_normal, infectious_flow_over, recovery_flow_normal, recovery_flow_critical, death_flow_normal, death_flow_over, critical_flow
        flow_name = ("exposed_flow_normal", "exposed_flow_over", "infectious_flow_normal", "infectious_flow_over", "recovery_flow_normal", "recovery_flow_critical", "death_flow_normal", "death_flow_over", "critical_flow")
        exposed_flow_normal, exposed_flow_over, infectious_flow_normal, infectious_flow_over, recovery_flow_normal, recovery_flow_critical, death_flow_normal, death_flow_over, critical_flow = [util.sanity_check_flow(*args) for args in zip(flow_name, flow)]
        
        dSdt = -exposed_flow_normal - exposed_flow_over
        dENdt = exposed_flow_normal - infectious_flow_normal
        dEOdt = exposed_flow_over - infectious_flow_over
        dIdt = infectious_flow_normal + infectious_flow_over - recovery_flow_normal - critical_flow
        dCdt = critical_flow - recovery_flow_critical - death_flow_normal - death_flow_over
        dRNdt = recovery_flow_normal
        dRCdt = recovery_flow_critical
        dDNdt = death_flow_normal
        dDOdt = death_flow_over
        dPdt = dSdt + dENdt + dEOdt + dIdt + dCdt + dRNdt + dRCdt + dDNdt + dDOdt
        '''
        if dPdt != 0:
            raise Exception("Population must not change: %f" % (dPdt,))
        '''
        dydt = dPdt, dSdt, dENdt, dEOdt, dIdt, dCdt, dRNdt, dRCdt, dDNdt, dDOdt
        
        check_result = [util.sanity_check_y(*args) for args in zip(y_name, y, dydt)]
        
        self.prev_dydt = dict(zip(y_name, dydt))
        
        return dydt
        
    def model(self, days, infectious_rate,
                    critical_chance, critical_rate, 
                    recovery_rate_normal, recovery_rate_critical,
                    death_chance_normal, death_rate_normal,
                    death_chance_over, death_rate_over, 
                    exposed_rate_over, k, kapasitas_rs_mul,
                    test_coverage_0, test_coverage_increase, test_coverage_max,
                    **kwargs):
        days = int(days)
        #unpack rt values
        rt_values = self.kabko.get_kwargs_rt(kwargs)
        rt_delta = self.kabko.get_rt_delta(rt_values)
        r_0 = rt_values[0]
        
        #load values
        population = self.kabko.population
        
        # this is derived parameter
        #infectious_period_opt = recovery_time_normal * (1-critical_chance) + critical_time * critical_chance #this is derived parameter
        infectious_leave_rate_opt = recovery_rate_normal * (1-critical_chance) + critical_rate * critical_chance
        #exposed_rate_over = r_over / death_rate_over
        #infectious_rate = 1.0 / incubation_period # this is derived parameter
        #recovery_rate_normal = 1.0 / recovery_time_normal # this is derived parameter
        #death_rate_normal = 1.0 / death_time_normal # this is derived parameter
        #critical_rate = 1.0 / critical_time # this is derived parameter
        #recovery_rate_critical = 1.0 / recovery_time_critical #this is derived parameter
        #death_rate_over = 1.0/death_time_over # this is a derived parameter
        
        def kapasitas_rs(t):
            kap = self.kabko.kapasitas_rs(t)
            '''
            if kapasitas_rs_mul != 1:
                raise Exception("kapasitas_rs_mul must be 1")
            if kap != 1352:
                raise Exception("kap must be 1352")
            '''
            return kap * kapasitas_rs_mul
        
        def test_coverage(t):
            return min(test_coverage_max, test_coverage_0 + test_coverage_increase * t)
        
        def logistic_rt(t):
            return self.kabko.logistic_rt(r_0, rt_delta, t, k)

        def exposed_rate_normal(t):
            rt = logistic_rt(t)
            #ret = rt * recovery_rate_normal * (1-critical_chance) + rt * critical_rate * critical_chance
            ret = rt * infectious_leave_rate_opt
            #ret = logistic_rt(t) / infectious_period_opt
            return ret
        
        _r0_over = exposed_rate_over / death_rate_over
        def r0_normal(t, infectious):
            return logistic_rt(t) if infectious > 0 else 0
            
        def r0_over(critical_over):
            return _r0_over if critical_over > 0 else 0
            
        def r0_overall(t, infectious, critical_over):
            #return exposed_rate_over / death_rate_over# * critical_chance * (critical_over/population)
            tot = infectious+critical_over
            if tot == 0: 
                return 0
            elif infectious == 0:
                return r0_over(critical_over)
            elif critical_over == 0:
                return r0_normal(t, infectious)
            else:
                nor = exposed_rate_normal(t) / infectious_leave_rate_opt * infectious/tot
                over = exposed_rate_over / death_rate_over * critical_over/tot
                return nor + over
        
        seed = self.kabko.seed
        population_init, susceptible_init, exposed_normal_init, exposed_over_init, infectious_init, critical_init, recovered_normal_init, recovered_critical_init, dead_normal_init, dead_over_init = population, population-seed, seed, 0, 0, 0, 0, 0, 0, 0  # initial conditions: one exposed, rest susceptible
        
        y0 = population_init, susceptible_init, exposed_normal_init, exposed_over_init, infectious_init, critical_init, recovered_normal_init, recovered_critical_init, dead_normal_init, dead_over_init # Initial conditions tuple

        
        # Integrate the SIR equations over the time grid, t.
        t = np.linspace(0, days-1, days) # days
        ret = odeint(self.deriv, y0, t, args=(
            population,
            exposed_rate_normal, exposed_rate_over, 
            infectious_rate, 
            critical_rate, critical_chance, 
            recovery_rate_normal, recovery_rate_critical, 
            death_rate_normal, death_chance_normal, 
            death_rate_over, death_chance_over,
            kapasitas_rs
        ))
        retT = ret.T
        '''
        sol = solve_ivp(self.deriv, (0,days-1), y0, dense_output=True, args=(
            population,
            exposed_rate_normal, exposed_rate_over, 
            infectious_rate, 
            critical_rate, critical_chance, 
            recovery_rate_normal, recovery_rate_critical, 
            death_rate_normal, death_chance_normal, 
            death_rate_over, death_chance_over,
            kapasitas_rs
        ))
        retT = sol.sol(t)
        '''
        population_2, susceptible, exposed_normal, exposed_over, infectious, critical, recovered_normal, recovered_critical,  dead_normal, dead_over = retT
        
        kapasitas_rs_val = util.map_function(t, kapasitas_rs)
        #kapasitas_rs_val = np.zeros(days)
        
        exposed = util.sum_element(exposed_normal, exposed_over)
        dead = util.sum_element(dead_normal, dead_over)
        mortality_rate_val = self.mortality_rate(t, exposed, dead, infectious_rate)
        #mortality_rate_val = np.zeros(days)
        
        test_coverage_val = util.map_function(t, test_coverage)
        r0_normal_val = util.map_function(zip(t, infectious), r0_normal, unpack=True)
        critical_over = SeicrdRlcModel.critical_over(critical, kapasitas_rs_val)
        r0_over_val = util.map_function(critical_over, r0_over)
        r0_overall_val = util.map_function(zip(t, infectious, critical_over), r0_overall, unpack=True)
        #r0_normal_val = np.zeros(days)
        #r0_over_val = np.zeros(days)
        
        return SeicrdRlcModelResult(t, population_2, susceptible, exposed_normal, exposed_over, infectious, critical, recovered_normal, recovered_critical, dead_normal, dead_over, mortality_rate_val, r0_normal_val, kapasitas_rs_val, r0_over_val, r0_overall_val, test_coverage_val)
        
    
    def _fitter(self, ret):
                    
        self.last_result_full = ret
        
            
        results = ret.get_datasets_values(self.datasets)
                
        results = np.array(results)
        self.last_result = results
        return results
    
    def fitter(self, **kwargs):
                    
        #days = self.kabko.data_days(self.kabko.outbreak_shift(incubation_period))
        ret = self.model(**kwargs)
        return self._fitter(ret)
        

Model = SeicrdRlcModel