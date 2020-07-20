from sklearn.metrics import explained_variance_score, max_error, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, r2_score, mean_tweedie_deviance, r2_score
import numpy as np
from core import util


class BaseScorer:
    def __init__(self, data, pred):
        self.data = data
        self.pred = pred
        '''
        self.residual = data-pred
        '''
    def residual(self):
        return self.data - self.pred
        
    def normalize(self, population):
        return BaseScorer(self.data, self.pred)
        
    def mean_absolute_error(self, *args, **kwargs):
        return mean_absolute_error(self.data, self.pred, *args, **kwargs)
    
    def mean_squared_error(self, *args, **kwargs):
        return mean_squared_error(self.data, self.pred, *args, **kwargs)
    
    def mean_squared_log_error(self, *args, **kwargs):
        return mean_squared_log_error(self.data, self.pred, *args, **kwargs)
        
    def explained_variance_score(self, *args, **kwargs):
        return explained_variance_score(self.data, self.pred, *args, **kwargs)
        
    def max_error(self, *args, **kwargs):
        return max_error(self.data, self.pred, *args, **kwargs)
        
    def median_absolute_error(self, *args, **kwargs):
        return mean_squared_log_error(self.data, self.pred, *args, **kwargs)
    
    def r2_score(self, *args, **kwargs):
        return r2_score(self.data, self.pred, *args, **kwargs)
    
    def mean_tweedie_deviance(self, power, *args, **kwargs):
        return mean_tweedie_deviance(self.data, self.pred, power=power, *args, **kwargs)
    
    def mean_poisson_deviance(self, *args, **kwargs):
        return self.mean_tweedie_deviance(power=1, *args, **kwargs)
    
    def mean_gamma_deviance(self, *args, **kwargs):
        return self.mean_tweedie_deviance(power=2, *args, **kwargs)
        
    def concatenate(scorers):
        data = np.concatenate([r.data for r in scorers])
        pred = np.concatenate([r.pred for r in scorers])
        return BaseScorer(data, pred)
        
class FittingResult:
    def __init__(self, model, fit_result, datasets, test_scorer, fit_scorer, shift=0):
        self.model = model
        self.kabko = model.kabko
        self.fit_result = fit_result
        #self.model_result = model_result
        self.datasets = datasets
        self.test_scorer = test_scorer
        self.fit_scorer = fit_scorer
        self.outbreak_shift = shift
        
    def predict(self, days):
        params = dict(self.fit_result.values)
        params["days"] += days
        return self.model.model(**params)
        