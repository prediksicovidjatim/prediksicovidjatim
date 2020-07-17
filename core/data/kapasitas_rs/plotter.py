from core import util
import numpy as np

class KapasitasRSPlotter:
    def __init__(self, data=None, kabko=''):
        self.set_data(data, kabko)
        
    def set_data(self, data, kabko=''):
        self.data = data
        self.kabko = ''
        
    def get_data(self, tanggal):
        assert self.data is not None
        high = self.data[0]
        '''
        if tanggal < high.tanggal:
            return None
        '''
        for d in self.data:
            if d.tanggal > high.tanggal:
                if d.tanggal > tanggal:
                    break
                else:
                    high = d
        return high
        
    def date_range(self):
        return util.date_range(
            self.data[0].tanggal, 
            util.days_between(self.data[0].tanggal, self.data[-1].tanggal)+1
        )
        
    def data_thick(self, date_range=None):
        date_range = date_range or self.date_range()
        return [self.get_data(t) for t in date_range]
        
    def plot_total(self):
        assert self.data is not None
        date_range = self.date_range()
        data_thick = self.data_thick(date_range)
        return util.plot_single(
            np.array(np.array(date_range)),
            np.array(np.array([d.total() for d in data_thick])),
            title="Total Kapasitas RS " + self.kabko,
            label="Total kapasitas"
        )