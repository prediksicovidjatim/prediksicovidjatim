import numpy as np
import lmfit
from core import util
from .fitting_result import FittingResult, BaseScorer

class BaseModel:
    available_datasets = ["infectious", "critical_cared", "infectious_all", "recovered", "dead", "infected"]
    def __init__(self, kabko):
        self.kabko = kabko
        self.last_result_full = None
        self.last_result = None
        self.last_result_flat = None
        self.datasets = ["infectious", "critical_cared", "recovered", "dead"]
        
    def use_datasets(self, datasets):
        for dataset in datasets:
            if dataset not in BaseModel.available_datasets:
                raise ValueError("Invalid dataset: " + str(dataset))
        self.datasets = datasets
        
    def mortality_rate(self, t, exposed, dead, infectious_rate):
        return np.array([0] + [100 * dead[i] / sum(infectious_rate*exposed[:i]) if sum(infectious_rate*exposed[:i])>0 else 0 for i in range(1, len(t))])
        
    def fitter_flat(self, x, **kwargs):
        results = self.fitter(**kwargs)
        
        results_flat = results.flatten()
        self.last_result_flat = results_flat
        return results_flat[x]
    
    def fit(self, method="leastsq", test_splits=[5,3], unvary=[], outbreak_shift=None):
        if len([x for x in test_splits if x <= 1]) > 0:
            raise ValueError("A split must be at least 2")
        mod = lmfit.Model(self.fitter_flat)
        
        outbreak_shift = outbreak_shift or self.kabko.outbreak_shift(
            1.0/self.kabko.params["infectious_rate"].init
        )
        
        days = self.kabko.data_days(outbreak_shift)
        
        mod.set_param_hint("days", value=days, vary=False)
        
        self.kabko.apply_params(mod)

        params = mod.make_params()
        
        y_data_0 = self.kabko.get_datasets_values(self.datasets, outbreak_shift)
        
        set_count = len(self.datasets)
        
        y_data_0_0 = y_data_0[0]
        len_y_0_0 = len(y_data_0_0)
        len_x_0 = len(y_data_0) * len_y_0_0
        x_data_0_flat = np.linspace(0, len_x_0 - 1, len_x_0, dtype=int)#.reshape(y_data_0.shape)
        
        
        for u in unvary:
            if u in params:
                params[u].vary = False
        
        repeated_results = []
        full_index = np.linspace(0, len_y_0_0 - 1, len_y_0_0, dtype=int)
        empty_index = np.array([], dtype=int)
        
        for i in test_splits:
            results = self._fit(mod, y_data_0, params, util.time_series_split(y_data_0_0, i), method="leastsq")
            
            #just mean the scores?
            #https://medium.com/datadriveninvestor/k-fold-cross-validation-6b8518070833
            
            repeated_results.append(results)
        
        test_scorer = BaseScorer.concatenate(repeated_results) if len(repeated_results) > 0 else None
        
        fit_result = self.___fit(mod, x_data_0_flat, y_data_0.flatten(), params, method="leastsq", days=days)
        #model_result = self.model(**fit_result.values)
        pred_data_0 = self.fitter(**fit_result.values)
        fit_scorer=BaseScorer(y_data_0, pred_data_0)
        datasets = self.datasets
        
        return FittingResult(self, fit_result, datasets, test_scorer, fit_scorer, outbreak_shift)
        
    def _fit(self, mod, y_data_0, params, splits, method="leastsq"):
        results = []
        for split in splits:
            result = self.__fit(mod,  y_data_0, params, split, method=method)
            results.append(result)
            
        return BaseScorer.concatenate(results)
        
        
    def __fit(self, mod, y_data_0, params, split, method="leastsq"):
        
        tr_index, ts_index = split
        
        trts_index = np.concatenate((tr_index, ts_index))
        
        y_data_train = np.array([y[tr_index] for y in y_data_0])
        y_data_test = np.array([y[ts_index] for y in y_data_0])
        
        row_count = len(y_data_0)
        days = max(trts_index) + 1
        len_x_0 = row_count * days
        x_data_0 = np.linspace(0, len_x_0 - 1, len_x_0, dtype=int).reshape((row_count, days))
        
        x_data_train = np.array([x[tr_index] for x in x_data_0])
        x_data_test = np.array([x[ts_index] for x in x_data_0])
        
        
        fit_result = self.___fit(mod, x_data_train.flatten(), y_data_train.flatten(), params, method=method, days=days)
        
        pred_data_test = [pred[ts_index] for pred in self.fitter(**fit_result.values)]
        
        return BaseScorer(y_data_test, pred_data_test)
        
        
    def ___fit(self, mod, x_data, y_data, params, method="leastsq", days=None):
        if days is None:
            days = len(x_data)
        
        params["days"].value = days
        
        fit_result = mod.fit(y_data, params, method=method, x=x_data)
        
        #set back params
        for k, v in fit_result.values.items():
            params[k].value = v
            
        return fit_result