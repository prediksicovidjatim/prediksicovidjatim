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
            kapasitas
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
            kapasitas
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
    columns = ["kabko", "tanggal", "kapasitas"]
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
            fix_kapasitas(cur)
            
def fix_kapasitas(cur=None):
    if cur:
        return _fix_kapasitas(cur)
    else:
        with database.get_conn() as conn, conn.cursor() as cur:
            return _fix_kapasitas(cur)
    
def _fix_kapasitas(cur):
    cur.execute("""
        UPDATE main.kapasitas_rs
        SET kapasitas=
            CASE WHEN krs2.max_rs > main.kapasitas_rs.kapasitas
                THEN krs2.max_rs
                ELSE main.kapasitas_rs.kapasitas
            END
        FROM (
            SELECT krs1.kabko, krs0.since_tanggal, krs0.max_rs
            FROM main.kapasitas_rs krs1, (
                SELECT krs.kabko, MAX(krs.tanggal) AS since_tanggal, rcd2.max_rs
                FROM main.kapasitas_rs krs, (
                    SELECT rcd1.kabko, rcd0.max_rs, MIN(rcd1.tanggal) AS min_tanggal
                    FROM main.raw_covid_data rcd1, (
                        SELECT rcd.kabko, MAX(rcd.pos_rawat_rs) AS "max_rs"
                        FROM main.raw_covid_data rcd
                        GROUP BY rcd.kabko
                    ) rcd0
                    WHERE rcd1.kabko=rcd0.kabko AND rcd1.pos_rawat_rs=rcd0.max_rs
                    GROUP BY rcd1.kabko, rcd0.max_rs
                    ORDER BY rcd1.kabko
                ) rcd2
                WHERE krs.kabko=rcd2.kabko AND krs.tanggal <= rcd2.min_tanggal
                GROUP BY krs.kabko, rcd2.max_rs
                ORDER BY krs.kabko
            ) krs0
            WHERE krs1.kabko=krs0.kabko AND krs1.tanggal=krs0.since_tanggal
        ) krs2
        WHERE main.kapasitas_rs.kabko=krs2.kabko AND tanggal>=krs2.since_tanggal
    """)
    cur.execute("""
        DELETE FROM main.kapasitas_rs
        WHERE (kabko, tanggal) IN (
            SELECT krs1.kabko, krs1.tanggal
            FROM main.latest_two_kapasitas_rs krs1, main.latest_two_kapasitas_rs krs2
            WHERE krs1.kabko=krs2.kabko AND krs1.r=1 AND krs2.r=2
                AND krs1.kapasitas=krs2.kapasitas
        )
    """)
    
