import numpy as np
import lmfit
from core import util
from .fitting_result import FittingResult, CategoryPack

class BaseModel:
    available_datasets = ["infectious", "critical_cared", "recovered", "dead", "infected"]
    def __init__(self, kabko):
        self.kabko = kabko
        self.last_result_full = None
        self.last_result = None
        self.last_result_flat = None
        self.datasets = ["infectious", "critical_cared", "recovered", "dead", "infected"]
        
    def use_datasets(self, datasets):
        for dataset in datasets:
            if dataset not in BaseModel.available_datasets:
                raise ValueError("Invalid dataset: " + str(dataset))
        self.datasets = datasets
        
    def fitter_flat(self, x, **kwargs):
        results = self.fitter(**kwargs)
        
        results_flat = results.flatten()
        self.last_result_flat = results_flat
        return results_flat[x]
    
    def fit(self, method="leastsq", splits=[5,3,1], unvary=[]):
        mod = lmfit.Model(self.fitter_flat)
        
        outbreak_shift = self.kabko.outbreak_shift(
            self.kabko.params["incubation_period"].init
        )
        
        days = self.kabko.data_days(outbreak_shift)
        
        mod.set_param_hint("days", value=days, vary=False)
        
        self.kabko.apply_params(mod)

        params = mod.make_params()
        
        y_data_0 = []
        for d in self.datasets:
            y_data_0.append(self.kabko.get_dataset(d, outbreak_shift))
            
        y_data_0 = np.array(y_data_0)
        
        set_count = len(self.datasets)
        
        y_data_0_0 = y_data_0[0]
        len_y_0_0 = len(y_data_0_0)
        len_x_0 = len(y_data_0) * len_y_0_0
        x_data_0 = np.linspace(0, len_x_0 - 1, len_x_0, dtype=int).reshape(y_data_0.shape)
        
        
        repeated_results = []
        full_index = np.linspace(0, len_y_0_0 - 1, len_y_0_0, dtype=int)
        empty_index = np.array([], dtype=int)
        
        for u in unvary:
            params[u].vary = False
        
        for i in splits:
            results = self._fit(mod, x_data_0, y_data_0, params, util.time_series_split(y_data_0_0, i), method="leastsq")
            
            #just mean the scores?
            #https://medium.com/datadriveninvestor/k-fold-cross-validation-6b8518070833
            
            repeated_results.append(results)

        #fit_result.plot_fit(datafmt="-");
        
        return repeated_results
        
    def _fit(self, mod, x_data_0, y_data_0, params, splits, method="leastsq"):
        results = []
        for split in splits:
            result = self.__fit(mod, x_data_0, y_data_0, params, split, method=method)
            results.append(result)
        return results
        
    def death_chance(self, t, exposed, dead, infectious_rate):
        return np.array([0] + [100 * dead[i] / sum(infectious_rate*exposed[:i]) if sum(infectious_rate*exposed[:i])>0 else 0 for i in range(1, len(t))])
        
    def __fit(self, mod, x_data_0, y_data_0, params, split, method="leastsq"):
        
        tr_index, ts_index = split
        
        trts_index = np.concatenate((tr_index, ts_index))
        
        y_data = np.array([y[trts_index] for y in y_data_0])
        
        y_data_train = np.array([y[tr_index] for y in y_data_0])
        y_data_test = np.array([y[ts_index] for y in y_data_0])
        
        x_data = np.array([y[trts_index] for y in x_data_0])
        
        x_data_train = np.array([x[tr_index] for x in x_data_0])
        x_data_test = np.array([x[ts_index] for x in x_data_0])
        
        len_ts = len(ts_index)
        params["days"].value = max(trts_index) + 1
        
        
        fit_result = mod.fit(y_data_train.flatten(), params, method=method, x=x_data_train.flatten())
        
        pred_data_0 = self.fitter(**fit_result.values)
        pred_data = np.array([x[trts_index] for x in pred_data_0])
        
        pred_data_train = np.array([x[tr_index] for x in pred_data_0])
        pred_data_test = np.array([x[ts_index] for x in pred_data_0])
        
        #set back params
        for k, v in fit_result.values.items():
            params[k].value = v
            
        return FittingResult(fit_result, 
            CategoryPack(y_data_train, pred_data_train, x_data_train),
            CategoryPack(y_data_test, pred_data_test, x_data_test),
            CategoryPack(y_data, pred_data, x_data)
        )