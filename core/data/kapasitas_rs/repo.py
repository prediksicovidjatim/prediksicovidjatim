from core import util, database
from core.data.kapasitas_rs.entities import KapasitasRSRaw, KapasitasRSCollection
from core.data.raw.repo import fetch_kabko


def fetch_kapasitas_rs(kabko, cur=None):
    if cur:
        return _fetch_kapasitas_rs(kabko, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_kapasitas_rs(kabko, cur)
            
def _fetch_kapasitas_rs(kabko, cur):
    cur.execute("""
        SELECT 
            kabko,
            tanggal,
            vent,
            tanpa_vent,
            biasa
        FROM main.kapasitas_rs
        WHERE kabko=%s
        ORDER BY tanggal ASC
    """, (kabko,))
    
    return [KapasitasRSRaw(*args) for args in cur.fetchall()]

def fetch_kapasitas_rs_latest(cur=None):
    if cur:
        return _fetch_kapasitas_rs_latest(cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fetch_kapasitas_rs_latest(cur)
            
def _fetch_kapasitas_rs_latest(cur):
    cur.execute("""
        SELECT 
            kabko,
            tanggal,
            vent,
            tanpa_vent,
            biasa
        FROM main.kapasitas_rs_latest
        ORDER BY kabko
    """)
    
    return [KapasitasRSRaw(*args) for args in cur.fetchall()]
    
def insert_kapasitas_rs(data, cur=None):
    if cur:
        return _insert_kapasitas_rs(data, cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _insert_kapasitas_rs(data, cur)
            
def _insert_kapasitas_rs(data, cur):
    if isinstance(data[0], KapasitasRSRaw):
        data = [d.tuple() for d in data]
    columns = ["kabko", "tanggal", "vent", "tanpa_vent", "biasa"]
    columns_str = ", ".join(columns)
    updates = ["%s=EXCLUDED.%s" % (col, col) for col in columns]
    updates_str = ", ".join(updates)
    values_template = util.mogrify_value_template(len(columns))
    with database.get_conn() as conn, conn.cursor() as cur:
        args_str = ','.join(cur.mogrify(values_template, x).decode('utf-8') for x in data)
        
        cur.execute("""
            INSERT INTO main.kapasitas_rs(%s) VALUES %s
            ON CONFLICT (kabko, tanggal) DO UPDATE SET
                %s
        """ % (columns_str, args_str, updates_str))
        
        conn.commit()
        
def save(data):
    with database.get_conn() as conn, conn.cursor() as cur:
        kabko = set(fetch_kabko(cur))
        old_data = {d for d in fetch_kapasitas_rs_latest()}
        new_data = [d for d in data if d.kabko in kabko and d not in old_data]
        if len(new_data) > 0:
            insert_kapasitas_rs(new_data, cur)