from core import util

class Params:
    def __init__(self, kabko=None, tanggal=None, sampai=None):
        self.kabko = kabko
        self.tanggal = tanggal
        self.sampai = sampai
        
    def tanggal_after(self, after):
        return util.filter_dates_after(self.tanggal, after)
        
class RawData:
    db_trans = {
        "kabko": "kabko",
        "tanggal": "tanggal",
        "odr": "odr",
        "otg": "otg"
    }
    def __init__(self, kabko, tanggal, odr, otg, odp, pdp, positif):
        self.kabko = kabko
        self.tanggal = tanggal
        if isinstance(tanggal, str):
            self.tanggal = util.parse_date(tanggal)
        self.odr = odr
        self.otg = otg
        self.odp = RawODP(**odp)
        self.pdp = RawPDP(**pdp)
        self.positif = RawPositif(**positif)
        
    def from_db_row(row):
        ret = util.filter_dict_new(row, RawData.db_trans)
        ret["odp"] = util.filter_dict_new(row, RawODP.db_trans)
        ret["pdp"] = util.filter_dict_new(row, RawPDP.db_trans)
        ret["positif"] = util.filter_dict_new(row, RawPositif.db_trans)
        return ret
        
    def to_db_row(self, option=None):
        ret = {k: getattr(self, v) for k, v in RawData.db_trans.items()}
        ret["tanggal"] = util.format_date(self.tanggal)
        ret_odp = RawData._to_db_row_sub(self.odp, self.odp.dipantau, RawODP.db_trans)
        ret_pdp = RawData._to_db_row_sub(self.pdp, self.pdp.dirawat, RawPDP.db_trans)
        ret_positif = RawData._to_db_row_sub(self.positif, self.positif.dirawat, RawPositif.db_trans)
        
        ret = {**ret, **ret_odp, **ret_pdp, **ret_positif}
        
        if option == "max":
            ret["odp_total"] = self.odp.total_max()
            ret["odp_rawat_total"] = self.odp.dipantau.total_max()
            ret["pdp_total"] = self.pdp.total_max()
            ret["pdp_rawat_total"] = self.pdp.dirawat.total_max()
            ret["pos_total"] = self.positif.total_max()
            ret["pos_rawat_total"] = self.positif.dirawat.total_max()
        elif option == "opt":
            ret["odp_total"] = self.odp.total_opt()
            ret["odp_rawat_total"] = self.odp.dipantau.total_opt()
            ret["pdp_total"] = self.pdp.total_opt()
            ret["pdp_rawat_total"] = self.pdp.dirawat.total_opt()
            ret["pos_total"] = self.positif.total_opt()
            ret["pos_rawat_total"] = self.positif.dirawat.total_opt()
            
        return ret
        
    def _to_db_row_sub(obj, obj_rawat, db_trans):
        ret = {k: getattr(obj, v) for k, v in db_trans.items() if "rawat" not in k}
        ret_rawat = {k: getattr(obj_rawat, v) for k, v in db_trans.items() if "rawat" in k}
        return {**ret, **ret_rawat}
        
    def total(self):
        return self.otg + self.odr + self.odp.total + self.pdp.total + self.positif.total
    
    def total_meninggal(self):
        return self.odp.meninggal + self.pdp.meninggal + self.positif.meninggal
    
    def total_exposed(self):
        return self.otg+self.odr
        
    positif_fields = ['total', 'dirawat', 'sembuh', 'meninggal', 'rumah', 'gedung', 'rs']
    
class RawPositif:
    db_trans = {
        "pos_total": "total",
        "pos_sembuh": "sembuh",
        "pos_meninggal": "meninggal",
        "pos_rawat_total": "dirawat",
        "pos_rawat_rumah": "rumah",
        "pos_rawat_gedung": "gedung",
        "pos_rawat_rs": "rs",
    }
    def __init__(self, total, sembuh, meninggal, **dirawat):
        self.total = total
        self.sembuh = sembuh
        self.meninggal = meninggal
        self.dirawat = RawDirawat(**dirawat)
        
    def total_aktif(self):
        return self.dirawat.total
        
    def total_calc(self):
        return self.sembuh+self.meninggal+self.dirawat.total_opt()
        
    def total_opt(self):
        return self.total_calc() or self.total
        
    def total_max(self):
        return max(self.total_calc(), self.total)
    
    
class RawPDP:
    db_trans = {
        "pdp_total": "total",
        "pdp_belum": "belum_diawasi",
        "pdp_sehat": "sehat",
        "pdp_meninggal": "meninggal",
        "pdp_rawat_total": "dirawat",
        "pdp_rawat_rumah": "rumah",
        "pdp_rawat_gedung": "gedung",
        "pdp_rawat_rs": "rs",
    }
    def __init__(self, total, belum_diawasi, sehat, meninggal, **dirawat):
        self.total = total
        self.belum_diawasi = belum_diawasi
        self.sehat = sehat
        self.meninggal = meninggal
        self.dirawat = RawDirawat(**dirawat)
        
    def total_aktif(self):
        return self.dirawat.total
        
    def total_calc(self):
        return self.belum_diawasi+self.sehat+self.meninggal+self.dirawat.total_opt()
        
    def total_opt(self):
        return self.total_calc() or self.total
        
    def total_max(self):
        return max(self.total_calc(), self.total)
        

class RawODP:
    db_trans = {
        "odp_total": "total",
        "odp_belum": "belum_dipantau",
        "odp_selesai": "selesai_dipantau",
        "odp_meninggal": "meninggal",
        "odp_rawat_total": "dirawat",
        "odp_rawat_rumah": "rumah",
        "odp_rawat_gedung": "gedung",
        "odp_rawat_rs": "rs",
    }
    def __init__(self, total, belum_dipantau, selesai_dipantau, meninggal, **dirawat):
        self.total = total
        self.belum_dipantau = belum_dipantau
        self.selesai_dipantau = selesai_dipantau
        self.meninggal = meninggal
        self.dipantau = RawDirawat(**dirawat)
        
    def total_aktif(self):
        return self.dirawat.total
        
    def total_calc(self):
        return self.belum_dipantau+self.selesai_dipantau+self.meninggal+self.dipantau.total_opt()
        
    def total_opt(self):
        return self.total_calc() or self.total
        
    def total_max(self):
        return max(self.total_calc(), self.total)
            
        
class RawDirawat:
    def __init__(self, dirawat, rumah, gedung, rs):
        self.total = dirawat
        self.dirawat = dirawat
        self.rumah = rumah
        self.gedung = gedung
        self.rs = rs
    
    def total_calc(self):
        return self.rumah+self.gedung+self.rs
        
    def total_opt(self):
        return self.total_calc() or self.total
        
    def total_max(self):
        return max(self.total_calc(), self.total)
        