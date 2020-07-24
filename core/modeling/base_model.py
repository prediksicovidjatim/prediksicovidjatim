import numpy as np
import lmfit
from core import util
from .fitting_result import FittingResult, BaseScorer
import math

class BaseModel:
    available_datasets = ["infectious", "critical_cared", "infectious_all", "recovered", "dead", "infected"]
    dataset_weights = {
        "infectious": 2,
        "critical_cared": 1.75,
        "infectious_all": 2.125,
        "recovered": 2.125,
        "dead": 2.125
    }
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
        
    def objective(self, params, x, data):
        pred = self.fitter(**params)
        #length = len(data[0])
        #pred = np.array([p[:length] for p in pred])
        pred = np.array([p[x[0]:x[1]] for p in pred])
        obj = data - pred
        weights = np.array([BaseModel.dataset_weights[d] for d in self.datasets])
        obj = util.np_multiply_2d(obj, weights)
        ret = obj.flatten()
        return ret
        
    
    def fit(self, method="leastsq", test_splits=[5,3], unvary=[], outbreak_shift=None, sigma_conf=2, sigma_pred=None):#, **kwargs):
        if len([x for x in test_splits if x <= 1]) > 0:
            raise ValueError("A split must be at least 2")
        if sigma_pred is None:
            sigma_pred=sigma_conf
            
        params = lmfit.Parameters()
        params_f = params.add
        
        #mod = lmfit.Model(self.fitter_flat)
        
        outbreak_shift = outbreak_shift or self.kabko.outbreak_shift(
            1.0/self.kabko.params["infectious_rate"].init
        )
        
        days = self.kabko.data_days(outbreak_shift)
        
        params_f("days", value=days, vary=False)
        
        self.kabko.apply_params(params)
        
        #params = mod.make_params()
        mod = lmfit.Minimizer(self.objective, params, nan_policy='propagate')
        
        y_data_0 = self.kabko.get_datasets_values(self.datasets, outbreak_shift)
        
        set_count = len(self.datasets)
        
        y_data_0_0 = y_data_0[0]
        len_y_0_0 = len(y_data_0_0)
        len_x_0 = len(y_data_0) * len_y_0_0
        #x_data_0_flat = np.linspace(0, len_x_0 - 1, len_x_0, dtype=int)#.reshape(y_data_0.shape)
        x_range_0 = 0, len_y_0_0
        x_data_0 = np.linspace(0, len_y_0_0-1, len_y_0_0)
        
        
        for u in unvary:
            if u in params:
                params[u].vary = False
                
        nvarys = len([1 for p in params.values() if p.vary])
        
        repeated_results = []
        #full_index = np.linspace(0, len_y_0_0 - 1, len_y_0_0, dtype=int)
        #empty_index = np.array([], dtype=int)
        
        
        
        for i in test_splits:
            results = self._fit(mod, y_data_0, params, util.time_series_split(y_data_0_0, i), method=method, sigma_conf=sigma_conf, sigma_pred=sigma_pred, nvarys=nvarys)#, **kwargs)
            
            #just mean the scores?
            #https://medium.com/datadriveninvestor/k-fold-cross-validation-6b8518070833
            
            repeated_results.append(results)
        
        test_scorer = BaseScorer.concatenate(repeated_results) if len(repeated_results) > 0 else None
        
        #fit_result = self.____fit(x_data_0_flat, y_data_0.flatten(), params, days=days, method=method, nvarys=nvarys)#, **kwargs)
        fit_result = self.____fit(mod, x_range_0, y_data_0, params, days=days, method=method)#, **kwargs)
        
        for k, v in fit_result.params.items():
            if v.stderr is None:
                vary = v.vary and not math.isclose(v.min, v.max, abs_tol=1e-13, rel_tol=1e-13)
                if vary:
                    fit_result.params[k].stderr = abs(v.value * 0.1)
                
                else:
                    fit_result.params[k].stderr = 0
                
        
        #model_result = self.model(**fit_result.values)
        pred_data_0 = self.fitter(**fit_result.values)
        #pred_data_0 = util.np_split(fit_result.best_fit, set_count)
        #dely_conf_fit, dely_pred_fit = self._get_dely(fit_result, x_data_0_flat, set_count, sigma_conf=sigma_conf, sigma_pred=sigma_pred)
        try:
            dely_conf_fit, dely_pred_fit = self._get_dely(mod, fit_result.params, fit_result.covar, x_range_0, set_count, sigma_conf=sigma_conf, sigma_pred=sigma_pred)
            print("Error bar true fit")
        except AttributeError:
            #raise Exception("Failed: %s, %s, %s, %s" % (str(len(pred_data_0[0])), str(x_range_0), str(fit_result.errorbars), str(fit_result.message)))
            dely = np.zeros(x_range_0[1]-x_range_0[0])
            dely = np.tile(dely, (set_count, 1))
            dely_conf_fit = dely_pred_fit = dely
        
        fit_scorer=BaseScorer(y_data_0, pred_data_0, dely_conf_fit, dely_pred_fit, nvarys, util.np_mean_2d(y_data_0), x=x_data_0)
        datasets = self.datasets
        
        return FittingResult(self, fit_result, datasets, test_scorer, fit_scorer, nvarys, outbreak_shift)
        
    def _fit(self, mod, y_data_0, params, splits, method="leastsq", sigma_conf=2, sigma_pred=None, nvarys=None):#, **kwargs):
        results = []
        for split in splits:
            result = self.__fit(mod, y_data_0, params, split, method=method, sigma_conf=sigma_conf, sigma_pred=sigma_pred, nvarys=nvarys)#, **kwargs)
            results.append(result)
            
        return BaseScorer.concatenate(results)
        
    def __fit(self, mod, y_data_0, params, split, method="leastsq", sigma_conf=2, sigma_pred=None, nvarys=None):#, **kwargs):
        
        tr_index, ts_index = split
        
        trts_index = np.concatenate((tr_index, ts_index))
        
        y_data_train = np.array([y[tr_index] for y in y_data_0])
        y_data_test = np.array([y[ts_index] for y in y_data_0])
        
        set_count = len(y_data_0)
        days = max(trts_index) + 1
        #len_x_0 = set_count * days
        #x_data_0 = np.linspace(0, len_x_0 - 1, len_x_0, dtype=int).reshape((set_count, days))
        
        #x_data_train = np.array([x[tr_index] for x in x_data_0])
        #x_data_test = np.array([x[ts_index] for x in x_data_0])
        
        #x_data_train_flat = x_data_train.flatten()
        #x_data_test_flat = x_data_test.flatten()
        
        x_range_train = tr_index[0], tr_index[-1]+1
        x_range_test = ts_index[0], ts_index[-1]+1
        
        #fit_result = self.____fit(x_data_train.flatten(), y_data_train.flatten(), params, days=days, method=method)#, **kwargs)
        fit_result = self.____fit(mod, x_range_train, y_data_train, params, days=days, method=method)#, **kwargs)
        
        #test_result = mod.eval(fit_result.params, x=x_data_test_flat)
        #test_result = fit_result.eval(fit_result.params, method=method, x=x_range_test)
        
        #values = {k:v.value for k, v in fit_result.params.items()}
        #pred_data_test = [pred[ts_index] for pred in self.fitter(**fit_result.values)]
        #pred_data_test = util.np_split(test_result, set_count)
        pred_data_test = [pred[x_range_test[0]:x_range_test[1]] for pred in self.fitter(**fit_result.values)]
        
        try:
            dely_conf_test, dely_pred_test = self._get_dely(mod, fit_result.params, fit_result.covar, x_range_test, set_count, sigma_conf=sigma_conf, sigma_pred=sigma_pred)
            print("Error bar true")
        except AttributeError:
            #raise Exception("Failed: %s, %s, %s, %s" % (str(len(fit_result.residual)/4), str(x_range_train), str(fit_result.errorbars), str(fit_result.message)))
            dely = np.zeros(x_range_test[1]-x_range_test[0])
            dely = np.tile(dely, (set_count, 1))
            dely_conf_test = dely_pred_test = dely
            
        
        nvarys = nvarys or len([1 for p in params.values() if p.vary])
        
        return BaseScorer(y_data_test, pred_data_test, dely_conf_test, dely_pred_test, nvarys, util.np_mean_2d(y_data_train), x=ts_index)
        
    '''
    def _get_dely_model(self, fit_result, x_data, set_count, sigma_conf=2, sigma_pred=None):
        if sigma_pred is None:
            sigma_pred=sigma_conf
        dely_conf = fit_result.eval_uncertainty(x=x_data, sigma=sigma_conf)
        dely_pred = fit_result.eval_uncertainty(x=x_data, sigma=sigma_pred, predict=True)
        return util.np_split(dely_conf, set_count), util.np_split(dely_pred, set_count)
    '''
    def _get_dely(self, minimizer, params, covar, x_data, set_count, sigma_conf=2, sigma_pred=None):
        if sigma_pred is None:
            sigma_pred=sigma_conf
        dely_conf = minimizer.eval_uncertainty(params, covar, x=x_data, sigma=sigma_conf)
        dely_pred = minimizer.eval_uncertainty(params, covar, x=x_data, sigma=sigma_pred, predict=True)
        return util.np_split(dely_conf, set_count), util.np_split(dely_pred, set_count)
    
        
    def ____fit(self, mod, x_range, y_data, params, days=None, method="leastsq"):#, **kwargs):
        '''
        if days is None:
            days = len(x_data)
        '''
        if days is not None:
            params["days"].value = days
        
        #x = x_data[0], (len(x_data)/len(y_data))
        #fit_result = mod.fit(y_data, params, method=method, x=x_data, **kwargs)
        kws = {
            "x": x_range,
            "data": y_data
        }
        mod.userkws = kws
        fit_result = mod.minimize(params=params, method=method)#, **kwargs)
        
        #set back params
        for k, v in fit_result.params.items():
            params[k].value = v.value
            
        return fit_result