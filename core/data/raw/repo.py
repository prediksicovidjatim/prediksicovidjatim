from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs
from core import util, database
from core.data.raw.entities import RawData, RawODP, RawPDP, RawPositif


def save_data(data, upsert=False):
    if isinstance(data[0], RawData):
        data = [d.to_db_row() for d in data]
    columns = data[0].keys()
    columns_str = ", ".join(columns)
    updates = ["%s=EXCLUDED.%s" % (col, col) for col in columns]
    updates_str = ", ".join(updates)
    values_template = util.mogrify_value_template(len(columns))
    with database.get_conn() as conn, conn.cursor() as cur:
        args_str = ','.join(cur.mogrify(values_template, list(x.values())).decode('utf-8') for x in data)
        
        if upsert:
            cur.execute("""
                INSERT INTO main.raw_covid_data(%s) VALUES %s
                ON CONFLICT (kabko, tanggal) DO UPDATE SET
                    %s
            """ % (columns_str, args_str, updates_str))
        else:
            cur.execute("""
                INSERT INTO main.raw_covid_data(%s) VALUES %s
                ON CONFLICT (kabko, tanggal) DO NOTHING
            """ % (columns_str, args_str))
        
        
        conn.commit()
        
value_cols = [y for x in (RawData.db_trans.keys(), RawODP.db_trans.keys(), RawPDP.db_trans.keys(), RawPositif.db_trans.keys()) for y in x]
value_cols.remove("tanggal")
value_cols.remove("kabko")
non_zero_filter = " OR ".join(["%s<>0" % col for col in value_cols])
        
def get_oldest_tanggal(kabko):
    global non_zero_filter
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT min(tanggal) FROM main.raw_covid_data
            WHERE kabko=%s AND (%s)
        """ % ("%s", non_zero_filter), (kabko,))
        
        return cur.fetchone()[0]
        
def trim_early_zeros():
    global non_zero_filter
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            DELETE FROM main.raw_covid_data d1
            WHERE d1.tanggal < (
                SELECT d2.tanggal FROM (
                    SELECT d3.kabko, MIN(d3.tanggal) AS tanggal FROM main.raw_covid_data d3
                    WHERE %s
                    GROUP BY d3.kabko
                ) d2 WHERE d2.kabko=d1.kabko
            )
        """ % (non_zero_filter,))
        
        return cur.rowcount
    
def get_latest_tanggal():
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT max(tanggal) FROM main.raw_covid_data
        """)
        
        return cur.fetchone()[0]
    
def fetch_kabko():
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT kabko FROM main.kabko
            ORDER BY kabko
        """)
        
        return [x for x, in cur.fetchall()]
    
def fetch_kabko_dict():
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM main.kabko
            ORDER BY kabko
        """)
        
        return {k:v for k, v in cur.fetchall()}
    
def fetch_data(kabko):
    with database.get_conn() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT * FROM main.raw_covid_data
            WHERE kabko=%s
            ORDER BY tanggal
        """, (kabko,))
        
        return [RawData(**RawData.from_db_row(row)) for row in cur.fetchall()]
        
def get_latest_data(kabko=None):
    with database.get_conn() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
        if kabko:
            cur.execute("""
                SELECT * FROM covid_data_latest
                WHERE kabko=%s
            """, (kabko,))
        else:
            cur.execute("""
                SELECT * FROM main.covid_data_latest
            """)
        
        return [RawData(**RawData.from_db_row(row)) for row in cur.fetchall()]
        

sum_columns = ", ".join(["SUM(%s) AS %s" % (col, col) for col in value_cols])
        
def get_latest_total():
    global sum_columns
    with database.get_conn() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT * FROM main.covid_data_total_latest
        """)
        
        return [RawData(**RawData.from_db_row(row)) for row in cur.fetchall()]
    