from core import util
from core.modeling.scorer import BaseScorer, ResultScorer, ResultScorerMany
class DataPack:
    def __init__(self, train, test, all=None):
        self.train = train
        self.test = test
        self.all = all
        if self.all is None:
            if train.ndim == 1:
                self.all = np.concatenate((train, test))
                self.row_count = 1
            else:
                row_count = len(train)
                self.row_count = row_count
                self.all = util.np_concat_2d(train, test)

class CategoryPack:
    def __init__(self, y, pred, x=None):
        self.y = y
        self.pred = pred
        self.x = x
        
    def residual(self):
        return self.y - self.pred
        
    def from_2d(y, pred, x=None):
        row_count = len(y)
        if x:
            return [CategoryPack(y[i], pred[i], x[i]) for i in range(0, row_count)]
        else:
            return [CategoryPack(y[i], pred[i]) for i in range(0, row_count)]
            
    def scorer(self):
        return BaseScorer(self.y, self.pred)

class FittingResult:
    def __init__(self, result, train_pack, test_pack, all_pack=None):
        self.result = result
        self.train_pack = train_pack
        self.test_pack = test_pack
        self._all_pack = all_pack
        self.ndim = train_pack.y.ndim
        self.row_count = 1 if self.ndim==1 else len(train_pack.y)
                
    def all_pack(self):
        if self._all_pack is None:
            if self.ndim == 1:
                x = np.concatenate((self.train_pack.x, self.test_pack.x)) if train_pack.x else None
                self.all_pack = CategoryPack(
                    np.concatenate((self.train_pack.y, self.test_pack.y)),
                    np.concatenate((self.train_pack.pred, self.test_pack.pred)),
                    x
                )
            else:
                x = util.np_concat_2d((self.train_pack.x, self.test_pack.x)) if self.train_pack.x else None
                self.all_pack = CategoryPack.from_2d(
                    util.np_concat_2d((self.train_pack.y, self.test_pack.y)),
                    util.np_concat_2d((self.train_pack.pred, self.test_pack.pred)),
                    x
                )
        return self._all_pack
        
    def scorer(self):
        if self.ndim == 1:
            return ResultScorer(self.result, self.train_pack.y, self.test_pack.y, self.train_pack.pred, self.test_pack.pred)
        else:
            return ResultScorerMany(self.result, self.train_pack.y, self.test_pack.y, self.train_pack.pred, self.test_pack.pred)