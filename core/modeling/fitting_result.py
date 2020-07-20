from sklearn.metrics import explained_variance_score, max_error, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, r2_score, mean_tweedie_deviance, r2_score
import numpy as np
from core import util


class BaseScorer:
    def __init__(self, data, pred):
        self.data = util.np_make_2d(data)
        self.pred = util.np_make_2d(pred)
        self.row_count = len(self.data)
        '''
        self.residual = data-pred
        '''
        
        
    def residual(self):
        return self.data - self.pred
        
    def flatten(self):
        return BaseScorer(np.array([self.data.flatten()]), np.array([self.pred.flatten()]))
        
    def normalize(self, population):
        return BaseScorer(self.data/population, self.pred/population)
        
    def map_function(self, f, *args, **kwargs):
        return np.array([f(self.data[i], self.pred[i], *args, **kwargs) for i in range(0, self.row_count)])
        
    def mean_absolute_error(self, *args, **kwargs):
        return self.map_function(mean_absolute_error, *args, **kwargs)
    
    def mean_squared_error(self, *args, **kwargs):
        return self.map_function(mean_squared_error, *args, **kwargs)
    
    def root_mean_squared_error(self, *args, **kwargs):
        return np.sqrt(self.mean_squared_error(*args, **kwargs))
    
    def mean_squared_log_error(self, *args, **kwargs):
        return self.map_function(mean_squared_log_error, *args, **kwargs)
    
    def root_mean_squared_log_error(self, *args, **kwargs):
        return np.sqrt(self.mean_squared_log_error(*args, **kwargs))
        
    def explained_variance_score(self, *args, **kwargs):
        return self.map_function(explained_variance_score, *args, **kwargs)
        
    def max_error(self, *args, **kwargs):
        return self.map_function(max_error, *args, **kwargs)
        
    def median_absolute_error(self, *args, **kwargs):
        return self.map_function(median_absolute_error, *args, **kwargs)
    
    def r2_score(self, *args, **kwargs):
        return self.map_function(r2_score, *args, **kwargs)
    
    def mean_tweedie_deviance(self, power, *args, **kwargs):
        return self.map_function(mean_tweedie_deviance, *args, power=power, **kwargs)
    
    def mean_poisson_deviance(self, *args, **kwargs):
        return self.map_function(mean_tweedie_deviance, *args, power=1, **kwargs)
    
    def mean_gamma_deviance(self, *args, **kwargs):
        return self.map_function(mean_tweedie_deviance, *args, power=2, **kwargs)
        
    def concatenate(scorers):
        data = util.np_concat_2d([r.data for r in scorers])
        pred = util.np_concat_2d([r.pred for r in scorers])
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
        