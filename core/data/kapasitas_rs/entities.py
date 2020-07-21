from core import util

class KapasitasRSRaw:
    def __init__(self, kabko, tanggal, kapasitas):
        self.kabko = kabko
        self.tanggal = util.parse_date(tanggal.split(" ")[0]) if isinstance(tanggal, str) else tanggal
        self.kapasitas = util.parse_int(kapasitas) if isinstance(kapasitas, str) else kapasitas
        
    def tuple(self):
        return self.kabko, self.tanggal, self.kapasitas
        
    def add(self, kap):
        assert self is not kap 
        assert isinstance(kap, KapasitasRSRaw) 
        assert self.kabko == kap.kabko 
        
        self.tanggal = max(self.tanggal, kap.tanggal)    
        self.kapasitas += kap.kapasitas
        
    def __hash__(self):
        return hash(self.kabko)
        
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, KapasitasRSRaw):
            return False
        return self.kabko == other.kabko and self.kapasitas==other.kapasitas
        
class KapasitasRSCollection:
    def __init__(self):
        self.dict = {}
        
    def add(self, kap):
        assert isinstance(kap, KapasitasRSRaw)
        if kap.kabko not in self.dict:
            self.dict[kap.kabko] = KapasitasRSRaw(*kap.tuple())
        else:
            self.dict[kap.kabko].add(kap)
            
    def collect(self):
        return list(self.dict.values())