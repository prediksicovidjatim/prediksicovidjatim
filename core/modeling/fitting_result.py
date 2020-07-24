from sklearn.metrics import explained_variance_score, max_error, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, r2_score, mean_tweedie_deviance, r2_score
from scipy.stats import shapiro, pearsonr, f_oneway, kstest, ks_2samp
import numpy as np
from core import util
from statsmodels.stats.stattools import durbin_watson
from statsmodels.sandbox.stats.runs import runstest_1samp
import math

class BaseScorer:
    def __init__(self, data, pred, dely_conf, dely_pred, nvarys=None, train_mean=None, indexes=None, x=None):
        self.data = util.np_make_2d(data)
        self.pred = util.np_make_2d(pred)
        self.dely_conf = dely_conf
        self.dely_pred = dely_pred
        self.residual = data-pred
        self.row_count = len(self.data)
        self.data_count = len(self.data[0])
        self.nvarys = nvarys
        self.train_mean = train_mean
        if indexes is None:
            self.indexes = [(0, self.data_count)]
        else:
            self.indexes=indexes
        self.x = x
        self.__stats = None
        
    def flatten(self):
        return BaseScorer(
            np.array([self.data.flatten()]), 
            np.array([self.pred.flatten()]), 
            np.array([self.dely_conf.flatten()]),
            np.array([self.dely_pred.flatten()]),
            self.nvarys,
            np.array([np.mean(self.train_mean)]),
            [(self.row_count * i + self.indexes[i][0], self.indexes[i][1]) for i in range(0, len(self.indexes))],
            np.tile(self.x, self.row_count)
        )
        
    def normalize(self, div):
        return BaseScorer(
            self.data/div, 
            self.pred/div,
            self.dely_conf/div,
            self.dely_pred/div,
            self.nvarys,
            self.train_mean/div,
            self.indexes,
            self.x
        )
        
    def data_mean(self):
        return util.np_mean_2d(self.data)
        
    def report(self, train_mean=None):
        stats = self.stats()
        print("Varying Parameters: " + str(self.nvarys))
        print("Residual Mean (~0): " + str(self.residual_mean()))
        print("Residual Median (~0): " + str(self.residual_median()))
        print("Max Error (~0): " + str(self.max_error()))
        print("MAE (~0): " + str(self.mae()))
        print("MSE (~0): " + str(self.mse()))
        print("RMSE (~0): " + str(self.rmse()))
        print("RMSLE (~0): " + str(self.rmsle()))
        print("Explained Variance: " + str(self.explained_variance()))
        print("R2 (~1): " + str(self.r2()))
        print("Adjusted R2 (~1): " + str(self.r2_adj()))
        print("SMAPE (~0): " + str(self.smape()))
        print("MASE (~0): " + str(self.mase()))
        print("Chi Square: " + str(self.chisqr()))
        print("Reduced Chi Square: " + str(self.redchi()))
        print("AIC: " + str(self.aic()))
        print("AICc: " + str(self.aicc()))
        print("BIC: " + str(self.bic()))
        print("Durbin-Watson: " + str(self.dw()))
        print("Residual Normal Test Shapiro p (p>a): " + str(self.residual_normal()))
        print("Residual Runs Test p (p>0.5): " + str(self.residual_runs()))
        #print("Pearson R pred-data p (~1): " + str(self.pearson_data()))
        #print("Pearson R x-residual p (~0):" + str(self.pearson_residual()))
        print("F-Test Overall Significance p (p<a): " + str(self.f_mean(mean=train_mean)))
        print("F-Test pred-data p (p>a): " + str(self.f_data()))
        print("F-Test residual-zero p (p>a): " + str(self.f_residual()))
        print("KS-Test pred-data p (p>a): " + str(self.ks_data()))
        print("KS-Test residual-normal p (p>a): " + str(self.ks_residual()))
        print("Prediction Interval p (p<a): " + str(self.prediction_interval()))
        
    def stats(self, nvarys=None):
        if not self.__stats:
            self.__stats = self.map_residual(self._stats, nvarys=nvarys)
            self.__stats = util.transpose_dict_list(self.__stats)
        return self.__stats
        
    def _stats(self, residual, nvarys=None):
        nvarys = nvarys or self.nvarys
        if nvarys is None:
            raise ValueError("Please specify nvarys, which is the count of varying parameters")
        #taken shamelessly from lmfit
        #nvarys: number of parameters with vary=True
        chisqr = (residual**2).sum()
        ndata = self.data_count
        nfree = ndata - nvarys
        redchi = chisqr / max(1, nfree)
        # this is -2*loglikelihood
        chisqr = max(chisqr, 1.e-250*ndata)
        _neg2_log_likel = ndata * np.log(chisqr / ndata)
        aic = _neg2_log_likel + 2 * nvarys
        bic = _neg2_log_likel + np.log(ndata) * nvarys
        aicc = aic + (2*nvarys*nvarys + 2*nvarys)/(ndata-nvarys-1)
        
        return {
            "chisqr": chisqr,
            "redchi": redchi,
            "aic": aic,
            "aicc": aicc,
            "bic": bic
        }
        
    def chisqr(self):
        return self.stats()["chisqr"]
        
    def chi2(self):
        return self.chisqr()
        
    def redchi(self):
        return self.stats()["redchi"]
        
    def aic(self):
        return self.stats()["aic"]
        
    def aicc(self):
        return self.stats()["aicc"]
        
    def bic(self):
        return self.stats()["bic"]
        
    def map_data_pred(self, f, *args, **kwargs):
        return np.array([f(self.data[i], self.pred[i], *args, **kwargs) for i in range(0, self.row_count)])
        
    def map_residual(self, f, *args, **kwargs):
        return np.array([f(r, *args, **kwargs) for r in self.residual])
        
    def smape(self):
        return self.map_data_pred(self._smape)
        
    def _smape(self, data, pred):
        ret0 = [(d, p, math.fabs(d)+math.fabs(p)) for d, p in zip(data, pred)]
        ret1 = [math.fabs(p-d) / c for d, p, c in ret0 if c != 0]
        #return 2.0 * sum(ret1) / self.data_count
        return sum(ret1) / self.data_count
        
    def mase(self, seasonality=1):
        ret = np.array([np.mean([self._mase(self.data[i][a:b], self.pred[i][a:b], seasonality=seasonality) for a, b in self.indexes]) for i in range(0, self.row_count)])
        return ret
        #return self.map_data_pred(self._mase, seasonality=seasonality)
        
    def _mase(self, data, pred, seasonality=1):
        return mean_absolute_error(data, pred) / mean_absolute_error(data[seasonality:], pred[:-seasonality])
    
    def prediction_interval(self):
        return np.array([self._prediction_interval(self.data[i], self.pred[i], self.dely_pred[i]) for i in range(0, self.row_count)])
        
    def _prediction_interval(self, data, pred, dely_pred):
        pred_low = pred - dely_pred
        pred_high = pred + dely_pred
        
        p_arr = [0 if pl <= d and d <= ph else 1 for pl, d, ph in zip(pred_low, data, pred_high)]
        return 1.0*sum(p_arr)/self.data_count
        
    def residual_mean(self, **kwargs):
        return self.map_residual(np.mean, **kwargs)
        
    def residual_median(self, **kwargs):
        return self.map_residual(np.median, **kwargs)
        
    def residual_normal(self, **kwargs):
        return self.map_residual(self._residual_normal)
        
    def _residual_normal(self, residual, **kwargs):
        stat, p = shapiro(residual, **kwargs)
        return p
        
    def residual_runs(self, **kwargs):
        return self.map_residual(self._residual_runs)
        
    def _residual_runs(self, residual, **kwargs):
        stat, p = runstest_1samp(residual, 0, correction=False, **kwargs)
        #print("Runs: %s, %s" % (str(stat), str(p)))
        return p
        
    def pearson_data(self, **kwargs):
        return self.map_data_pred(self._pearson_data, **kwargs)
        
    def _pearson_data(self, data, pred, **kwargs):
        stat, p = pearsonr(pred, data, **kwargs)
        return p
        
    def pearson_residual(self, **kwargs):
        return self.map_residual(self._pearson_residual, x=self.x, **kwargs)
        
    def _pearson_residual(self, residual, x=None, **kwargs):
        x = x if x is not None else self.x
        if x is None:
            raise("Please provide x")
        #x = x if x is not None else np.linspace(0, self.data_count-1, self.data_count)
        stat, p = pearsonr(x, residual, **kwargs)
        return p
        
    def f_data(self, **kwargs):
        return self.map_data_pred(self._f_data, **kwargs)
        
    def _f_data(self, data, pred, **kwargs):
        stat, p = f_oneway(pred, data, **kwargs)
        return p
        
    def f_residual(self, **kwargs):
        zero = np.zeros(self.data_count)
        return self.map_residual(self._f_residual, zero=zero, **kwargs)
        
    def _f_residual(self, residual, zero=None, **kwargs):
        zero = zero if zero is not None else np.zeros(self.data_count)
        stat, p = f_oneway(residual, zero, **kwargs)
        return p
        
    def f_mean(self, mean=None, **kwargs):
        mean = mean if mean is not None else self.train_mean#[np.mean(d) for d in self.data]
        if mean is None:
            raise ValueError("Please provide mean of the training data")
        return np.array([self._f_mean(self.pred[i], mean[i], **kwargs) for i in range(0, self.row_count)])
        
    def _f_mean(self, pred, mean, **kwargs):
        means = np.full(self.data_count, mean)
        stat, p = f_oneway(pred, means, **kwargs)
        return p
        
    def ks_data(self, **kwargs):
        return self.map_data_pred(self._ks_data, **kwargs)
        
    def _ks_data(self, data, pred, **kwargs):
        stat, p = ks_2samp(pred, data, **kwargs)
        return p
        
    def ks_residual(self, **kwargs):
        return self.map_residual(self._ks_residual, **kwargs)
        
    def _ks_residual(self, residual, **kwargs):
        stat, p = kstest(residual, "norm", **kwargs)
        return p
        
    def dw(self, **kwargs):
        return self.map_residual(durbin_watson, **kwargs)
        
    def mae(self, **kwargs):
        return self.map_data_pred(mean_absolute_error, **kwargs)
    
    def mse(self, **kwargs):
        return self.map_data_pred(mean_squared_error, **kwargs)
    
    def rmse(self, **kwargs):
        return np.sqrt(self.mse(**kwargs))
    
    def msle(self, **kwargs):
        return self.map_data_pred(mean_squared_log_error, **kwargs)
    
    def rmsle(self, **kwargs):
        return np.sqrt(self.msle(**kwargs))
        
    def explained_variance(self, **kwargs):
        return self.map_data_pred(explained_variance_score, **kwargs)
        
    def max_error(self, **kwargs):
        return self.map_data_pred(max_error, **kwargs)
        
    def median_absolute_error(self, **kwargs):
        return self.map_data_pred(median_absolute_error, **kwargs)
    
    def r2(self, **kwargs):
        return self.map_data_pred(r2_score, **kwargs)
        
    def r2_adj(self, nvarys=None, **kwargs):
        return self.map_data_pred(self._r2_adj, nvarys=nvarys, **kwargs)
        
    def _r2_adj(self, data, pred, nvarys=None, **kwargs):
        nvarys = nvarys or self.nvarys
        if nvarys is None:
            raise ValueError("Please specify nvarys, which is the count of varying parameters")
        r2 = r2_score(data, pred, **kwargs)
        ndata = self.data_count
        return 1.0 - (1.0-r2)*(ndata-1)/(ndata-nvarys-1)
    
    def mean_tweedie_deviance(self, power, **kwargs):
        return self.map_data_pred(mean_tweedie_deviance, power=power, **kwargs)
    
    def mean_poisson_deviance(self, **kwargs):
        return self.map_data_pred(mean_tweedie_deviance, power=1, **kwargs)
    
    def mean_gamma_deviance(self, **kwargs):
        return self.map_data_pred(mean_tweedie_deviance, power=2, **kwargs)
        
    def concatenate(scorers):
        data = util.np_concat_2d([r.data for r in scorers])
        pred = util.np_concat_2d([r.pred for r in scorers])
        dely_conf = util.np_concat_2d([r.dely_conf for r in scorers])
        dely_pred = util.np_concat_2d([r.dely_pred for r in scorers])
        nvarys = max([r.nvarys for r in scorers])
        train_mean = util.np_mean_2d(util.transpose_list_list([r.train_mean for r in scorers]))
        indexes = np.concatenate([r.indexes for r in scorers])
        x = np.concatenate([r.x for r in scorers])
        return BaseScorer(data, pred, dely_conf, dely_pred, nvarys, train_mean, indexes, x)
        
    def get_values(self, attrs):
        return [util.get_obj_attr(self, a) for a in attrs]
        
class FittingResult:
    def __init__(self, model, fit_result, datasets, test_scorer, fit_scorer, nvarys, shift=0):
        self.model = model
        self.kabko = model.kabko
        self.fit_result = fit_result
        #self.model_result = model_result
        self.datasets = datasets
        self.test_scorer = test_scorer
        self.fit_scorer = fit_scorer
        self.nvarys = nvarys
        self.outbreak_shift = shift
        
    def predict(self, days):
        params = dict(self.fit_result.values)
        params["days"] += days
        return self.model.model(**params)
        