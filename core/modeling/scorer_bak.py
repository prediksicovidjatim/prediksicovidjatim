from sklearn.metrics import explained_variance_score, max_error, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, r2_score, mean_tweedie_deviance
import numpy as np
from core import util

class BaseScorer:
    def __init__(self, data, pred, population=None):
        self.population = population
        self.data = 1.0/population*data if population else data
        self.pred = 1.0/population*pred if population else pred
        '''
        self.residual = data-pred
        '''
        
    def normalize(self, population):
        return self if self.population else BaseScorer(self.data, self.pred, population)
        
    def explained_variance_score(self, *args, **kwargs):
        return explained_variance_score(self.data, self.pred, *args, **kwargs)
        
    def max_error(self, *args, **kwargs):
        return max_error(self.data, self.pred, *args, **kwargs)
    
    def mean_absolute_error(self, *args, **kwargs):
        return mean_absolute_error(self.data, self.pred, *args, **kwargs)
    
    def mean_squared_error(self, *args, **kwargs):
        return mean_squared_error(self.data, self.pred, *args, **kwargs)
    
    def mean_squared_log_error(self, *args, **kwargs):
        return mean_squared_log_error(self.data, self.pred, *args, **kwargs)
    
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
        
    def mean_absolute_percentage_error(self):
        return 100 / len(self.data) * (self.data-self.pred)/self.data
        
    def from_2d(result, data, pred):
        return [BaseScorer(data[i], pred[i]) for i in len(data)]
        
class ResultScorer:
    def __init__(self, result, data_train, data_test, pred_train, pred_test):
        self.result = result
        self.data_train = data_train
        self.data_test = data_test
        self.pred_train = pred_train
        self.pred_test = pred_test
        
        self.data = np.concatenate((data_train, data_test))
        self.pred = np.concatenate((pred_train, pred_test))
        '''
        self.residual_train = data_train - pred_train
        self.residual_test = data_test - pred_test
        self.residual = np.concatenate((self.residual_train, self.residual_test))
        '''
        
        self.train_scorer = BaseScorer(self.data_train, self.pred_train)
        self.test_scorer = BaseScorer(self.data_test, self.pred_test)
        self.scorer = BaseScorer(self.data, self.pred)
    
    def stdev(self):
        return util.stdev(self.result.covar)
        
    def from_2d(result, data_train, data_test, pred_train, pred_test):
        return [ResultScorer(result, data_train[i], data_test[i], pred_train[i], pred_test[i]) for i in range(0, len(data_train))]
        
class ResultScorerMany:
    def __init__(self, result, data_train, data_test, pred_train, pred_test):
        self.result = result
        row_count = len(data_train)
        self.row_count = row_count
        self.data_train = data_train
        self.data_test = data_test
        self.pred_train = pred_train
        self.pred_test = pred_test
        
        self.scorers = ResultScorer.from_2d(result, data_train, data_test, pred_train, pred_test)
        
        
        self.data = util.np_concat_2d(data_train, data_test)
        self.pred = util.np_concat_2d(pred_train, pred_test)
        
        '''
        self.residual_train = np.array([data_train-pred_train for i in range(0, row_count)])
        self.residual_test = np.array([data_test-pred_test for i in range(0, row_count)])
        self.residual = np.array([np.concatenate(residual_train[i], residual_test[i]) for i in range(0, row_count)])
        '''
        
        '''
        self.train_scorer = [BaseScorer(self.data_train[i], self.pred_train[i]) for i in range(0, row_count)]
        self.test_scorer = [BaseScorer(self.data_test[i], self.pred_test[i]) for i in range(0, row_count)]
        self.scorer = [BaseScorer(self.data[i], self.pred[i]) for i in range(0, row_count)]
        '''
        
        self.data_train_flat = data_train.flatten()
        self.data_test_flat = data_test.flatten()
        self.pred_train_flat = pred_train.flatten()
        self.pred_test_flat = pred_test.flatten()
        self.data_flat = self.data.flatten()
        self.pred_flat = self.pred.flatten()
        
        self.scorer_flat = ResultScorer(result, self.data_train_flat, self.data_test_flat, self.pred_train_flat, self.pred_test_flat)
    
    def stdev(self):
        return util.stdev(self.result.covar)