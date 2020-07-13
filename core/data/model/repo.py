from core import util, database
from core.data.model.entities import KabkoData, DayData, ParamData, RtData
from core.data.raw.repo import fetch_kabko, fetch_kabko_dict, get_latest_tanggal, get_oldest_tanggal

def fetch_day_data(kabko, cur=None):
    if cur:
        return _fetch_day_data(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_day_data(kabko, cur)
    
def _fetch_day_data(kabko, cur):
    cur.execute("""
        SELECT 
            tanggal,
            pos_total AS infected,
            (pos_rawat_total-pos_rawat_rs) AS infectious,
            pos_rawat_rs AS critical,
            pos_sembuh AS recovered,
            pos_meninggal AS dead
        FROM main.raw_covid_data
        WHERE kabko=%s
        ORDER BY tanggal
    """, (kabko,))
    
    return [DayData(*args) for args in cur.fetchall()]
        
def fetch_param_data(kabko, cur=None):
    if cur:
        return _fetch_param_data(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_param_data(kabko, cur)
    
def _fetch_param_data(kabko, cur):
    cur.execute("""
        SELECT 
            pk.parameter,
            pk.init,
            pk.min,
            pk.max,
            p.vary,
            p.expr
        FROM main.parameter_kabko pk, main.parameter p
        WHERE pk.parameter=p.parameter AND kabko=%s
        ORDER BY pk.parameter
    """, (kabko,))
    
    return [ParamData(*args) for args in cur.fetchall()]

def fetch_kapasitas_rs(kabko, cur=None):
    if cur:
        return _fetch_kapasitas_rs(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_kapasitas_rs(kabko, cur)
            
def _fetch_kapasitas_rs(kabko, cur):
    cur.execute("""
        SELECT 
            tanggal,
            (vent+tanpa_vent+biasa) AS kapasitas
        FROM main.kapasitas_rs
        WHERE kabko=%s
        ORDER BY tanggal
    """, (kabko,))
    
    return [(*row,) for row in cur.fetchall()]

def fetch_rt_data(kabko, cur=None):
    if cur:
        return _fetch_rt_data(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_rt_data(kabko, cur)
    
def _fetch_rt_data(kabko, cur):
    cur.execute("""
        SELECT 
            tanggal,
            init,
            min,
            max
        FROM main.rt
        WHERE kabko=%s
        ORDER BY tanggal
    """, (kabko,))
    
    return [RtData(*args) for args in cur.fetchall()]
        
def get_kabko(kabko, cur=None):
    if cur:
        return _get_kabko(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _get_kabko(kabko, cur)
    
def _get_kabko(kabko, cur):
    cur.execute("""
        SELECT 
            k.kabko,
            text,
            population,
            tanggal AS first_positive
        FROM main.kabko k, main.first_pos_date fpd
        WHERE k.kabko=fpd.kabko AND k.kabko=%s
    """, (kabko,))
    
    return (*cur.fetchone(),)
        
def get_kabko_full(kabko):
    with database.get_conn() as conn, conn.cursor() as cur:
        return KabkoData(
            *get_kabko(kabko, cur), 
            fetch_day_data(kabko, cur), 
            fetch_kapasitas_rs(kabko, cur), 
            fetch_rt_data(kabko, cur), 
            fetch_param_data(kabko, cur)
        )
    
def update_params_init(kabko, filtered_params, cur=None):
    if cur:
        return _update_params_init(kabko, filtered_params, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            ret = _update_params_init(kabko, filtered_params, cur)
            conn.commit()
            return ret
            
def _update_params_init(kabko, filtered_params, cur):
    cur.execute('''
        PREPARE update_params_init AS 
        UPDATE main.parameter_kabko 
        SET init=$1 
        WHERE "parameter"=$2
            AND kabko=$3
    ''')
    database.execute_batch(
        cur, 
        "EXECUTE update_params_init (%s, %s, %s)",
        [(v, k, kabko) for k, v in filtered_params.items()]
    )
    ret = cur.rowcount
    cur.execute("DEALLOCATE update_params_init")
    return ret
    
def update_rt_init(kabko, rts, cur=None):
    if cur:
        return _update_rt_init(kabko, rts, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _update_rt_init(kabko, rts, cur)
            
def _update_rt_init(kabko, rts, cur):
    cur.execute('''
        PREPARE update_rt_init AS 
        UPDATE main.rt 
        SET init=$1 
        WHERE tanggal=$2
            AND kabko=$3
    ''')
    database.execute_batch(
        cur, 
        "EXECUTE update_rt_init (%s, %s, %s)",
        [(v, k, kabko) for k, v in rts]
    )
    cur.execute("DEALLOCATE update_rt_init")
    
    
def update_params_rt(kabko, params, option="seicrd_rlc"):
    params_needed = KabkoData.get_params_needed(option)
    filtered_params = util.filter_dict(params, params_needed)
    rt_count = kabko.rt_count if "_r" in option else 1
    rts_0 = util.get_kwargs_rt(params, rt_count)
    rts = zip(kabko.rt_dates, rts_0)
    with database.get_conn() as conn, conn.cursor() as cur:
        update_params_init(kabko.kabko, filtered_params, cur)
        update_rt_init(kabko.kabko, rts, cur)
        conn.commit()