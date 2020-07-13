from core import util, database
from itertools import accumulate
import numpy as np
from core.modeling import SeicrdRlcModel, SeicrdRlExtModel, SeicrdRlModel, SeicrdRModel, SeicrdModel, SeirdModel, BaseModel
        
class KabkoData:
    def __init__(self, kabko, text, population, first_positive, data, kapasitas_rs, rt, params):
        self.kabko = kabko
        self.text = text
        self.population = population
        self.first_positive = first_positive
        
        self._params = params
        self.params = {p.parameter:p for p in params}
        self._rt_0 = rt
        self._rt_1 = rt[1:]
        
        self.rt_count = len(self._rt_0)
        
        self.set_data(data)
        self.first_positive_index = self.get_date_index(self.first_positive)
        
        self._kapasitas_rs = [(self.get_date_index(tanggal), kapasitas) for tanggal, kapasitas in kapasitas_rs]
        
        
        self.rt_dates = [d.tanggal for d in self._rt_0]
        self.rt_days = [d.day_index(self.oldest_tanggal) for d in self._rt_0]
        
        self._rt_0_delta = util.rt_delta(self._rt_0, self.oldest_tanggal)
        
    def outbreak_shift(self, incubation_period, extra=0, minimum=None):
        ret = extra-(self.first_positive_index-incubation_period)
        if minimum is not None:
            ret = max(minimum, ret)
        return int(ret)
        
    def data_days(self, outbreak_shift=0):
        ret = self.data_count + outbreak_shift
        return int(ret)
        
    def get_date_index(self, tanggal):
        return int(util.days_between(self.oldest_tanggal, tanggal, True))
        
    def set_data(self, data):
        self.data = data
        self.data_count = len(data)
        self.oldest_tanggal = data[0].tanggal
        self.latest_tanggal = data[-1].tanggal
        self.infected = np.array([d.infected for d in data])
        self.infectious = np.array([d.infectious for d in data])
        self.critical_cared = np.array([d.critical_cared for d in data])
        self.recovered = np.array([d.recovered for d in data])
        self.dead = np.array([d.dead for d in data])
        
    def get_dataset(self, d, shift=0):
        # TODO
        ret = None
        if d == "infectious":
            ret = self.infectious 
        elif d == "critical_cared":
            ret = self.critical_cared
        elif d == "recovered":
            ret = self.recovered
        elif d == "dead":
            ret = self.dead
        elif d == "infected":
            ret = self.infected
        else:
            raise ValueError("Invalid dataset: " + str(d))
        return np.array(ret) if not shift else util.shift_array(ret, shift)
        
    def get_datasets(self, datasets, shift=0):
        return {k:self.get_dataset(k, shift) for k in datasets}
        
    def kapasitas_rs(self, t):
        smallest_day = -1
        ret = float("inf")
        for day, kapasitas in self._kapasitas_rs:
            if smallest_day < day and day <= t:
                smallest_day = day
                ret = kapasitas
            else:
                break
        return ret
        
    def rt(self, rt_data, t):
        smallest_day = -1
        ret = 1
        for day, rt in rt_data:
            if smallest_day < day and day <= t:
                smallest_day = day
                ret = rt
            else:
                break
        return ret
        
    def logistic_rt(self, r0, rt_delta, t, k=None):
        if k is None:
            k = self.params["k"].init
        logs = [ delta / (1 + np.exp(k*(-t+day))) for day, delta in rt_delta]
        rt = r0 + sum(logs)
        return rt
        
    def get_params_needed(option):
        params_needed = None
        if option == "seicrd_rlc":
            params_needed = SeicrdRlcModel.params
        elif option == "seicrd_rl_ext":
            params_needed = SeicrdRlExtModel.params
        elif option == "seicrd_rl":
            params_needed = SeicrdRlModel.params
        elif option == "seicrd_r":
            params_needed = SeicrdRModel.params
        elif option == "seicrd":
            params_needed = SeicrdModel.params
        elif option == "seird":
            params_needed = SeirdModel.params
        else:
            raise ValueError("Invalid option: " + str(option))
        return params_needed
        
    def apply_params(self, mod, option="seicrd_rlc"):
        params_needed = KabkoData.get_params_needed(option)
        
        mod.set_param_hint("population", value=self.population, vary=False)
        
        for p in util.filter_dict(self.params, params_needed).values():
            vary = p.vary and p.min != p.max
            if vary:
                mod.set_param_hint(p.parameter, value=p.init, min=p.min, max=p.max, vary=True, expr=p.expr)
            else:
                mod.set_param_hint(p.parameter, value=p.init, vary=False, expr=p.expr)
            
        mod.set_param_hint("r_0", value=self._rt_0[0].init, min=self._rt_0[0].min, max=self._rt_0[0].max, vary=True)
        
        #test these
        if "_r" in option:
            for i in range(1, len(self._rt_0)):
                cur = self._rt_0[i]
                mod.set_param_hint(
                    'r_%d' % (i,), 
                    value=cur.init,
                    min=cur.min,
                    max=cur.max,
                    vary=True
                )
                '''
                prev = self._rt_0[i-1]
                mod.set_param_hint(
                    'r_%d_min' % (i,), 
                    value=cur.min,
                    vary=False
                )
                mod.set_param_hint(
                    'r_%d_max' % (i,), 
                    value=cur.max,
                    vary=False
                )
                if i % 2 == 1:
                    mod.set_param_hint(
                        'dr_%d' % (i,), 
                        value=-self._rt_0_delta[i-1][1], 
                        min=max(0, prev.min-cur.max),
                        max=max(0, prev.max-cur.min),
                        vary=True
                    )
                    mod.set_param_hint('r_%d' % (i,), expr='min(max(r_%d-dr_%d, r_%d_min), r_%d_max)' % (i-1, i, i, i))
                else:
                    mod.set_param_hint(
                        'dr_%d' % (i,), 
                        value=self._rt_0_delta[i-1][1], 
                        min=max(0, cur.min-prev.max),
                        max=max(0, cur.max-prev.min), 
                        vary=True
                    )
                    mod.set_param_hint('r_%d' % (i,), expr='min(max(r_%d+dr_%d, r_%d_min), r_%d_max)' % (i-1, i, i, i))
                '''
    
class DayData:
    def __init__(self, tanggal, infected, infectious, critical_cared, recovered, dead):
        self.tanggal = tanggal
        self.infected = infected
        self.infectious = infectious
        self.critical_cared = critical_cared
        self.recovered = recovered
        self.dead = dead
        
class RtData:
    def __init__(self, tanggal, init, min=None, max=None):
        self.tanggal = tanggal
        self.init = init
        self.min = min
        self.max = max
        
        """
            pars = Parameters()
            pars.add('r0', value=5, vary=True)
            pars.add('dr1', value=5, min=0, vary=True)
            pars.add('r1', expr='r0-dr1')
        """
        
    def day_index(self, oldest_tanggal):
        return util.days_between(oldest_tanggal, self.tanggal)
        
        
class ParamData:
    def __init__(self, parameter, init, min=None, max=None, vary=True, expr=None):
        self.parameter = parameter
        self.init = init
        self.min = min
        self.max = max
        self.vary = False if vary==0 else True
        self.expr = expr
        