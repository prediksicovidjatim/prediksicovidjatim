from core import util, database
from core.data.map.entities import MapDataReal
from core.data.model.repo import get_kabko_full
from core.data.raw.repo import fetch_kabko, fetch_kabko_dict, get_latest_tanggal, get_oldest_tanggal

def fetch_real_data(kabko, cur=None):
    if cur:
        return _fetch_real_data(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_real_data(kabko, cur)
    
def _fetch_real_data(kabko, cur):
    cur.execute("""
        SELECT 
            k.kabko,
            d.tanggal,
            k.population as populasi,
            d.otg,
            d.odp_rawat_total as odp_aktif,
            d.pdp_rawat_total as pdp_aktif,
            d.pos_rawat_total as pos_aktif,
            d.pos_rawat_rs as pos_rs,
            d.pos_meninggal,
            d.pos_sembuh,
            d.pos_total
        FROM main.kabko k, main.raw_covid_data d
        WHERE k.kabko=%s AND d.kabko=k.kabko
        ORDER BY tanggal
    """, (kabko,))
    
    return [MapDataReal(*args) for args in cur.fetchall()]
    