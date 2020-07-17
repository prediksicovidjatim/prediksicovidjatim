from core import util

class KapasitasRSRaw:
    def __init__(self, kabko, tanggal, vent, tanpa_vent, biasa):
        self.kabko = kabko
        self.tanggal = util.parse_date(tanggal.split(" ")[0]) if isinstance(tanggal, str) else tanggal
        self.vent = util.parse_int(vent) if isinstance(vent, str) else vent
        self.tanpa_vent = util.parse_int(tanpa_vent) if isinstance(tanpa_vent, str) else tanpa_vent
        self.biasa = util.parse_int(biasa) if isinstance(biasa, str) else biasa
        
    def tuple(self):
        return self.kabko, self.tanggal, self.vent, self.tanpa_vent, self.biasa
        
    def total(self):
        return self.vent + self.tanpa_vent + self.biasa
        
    def add(self, kap):
        assert self is not kap 
        assert isinstance(kap, KapasitasRSRaw) 
        assert self.kabko == kap.kabko 
        
        self.tanggal = max(self.tanggal, kap.tanggal)    
        self.vent += kap.vent
        self.tanpa_vent += kap.tanpa_vent
        self.biasa += kap.biasa
        
    def __hash__(self):
        return hash(self.kabko)
        
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, KapasitasRSRaw):
            return False
        return self.kabko == other.kabko and self.vent == other.vent and self.tanpa_vent == other.tanpa_vent and self.biasa == other.biasa
        
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