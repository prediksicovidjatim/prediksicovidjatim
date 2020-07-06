from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs
from core import util, database
from core.scraping.entities import RawData


def save_data(data):
    columns = data[0].keys()
    columns_str = ", ".join(columns)
    updates = ["%s=EXCLUDED.%s" % (col, col) for col in columns]
    updates_str = ", ".join(updates)
    values_template = util.mogrify_value_template(len(columns))
    with database.get_conn() as conn, conn.cursor() as cur:
        args_str = ','.join(cur.mogrify(values_template, list(x.values())).decode('utf-8') for x in data)
        cur.execute("""
            INSERT INTO main.raw_covid_data(%s) VALUES %s
            ON CONFLICT (kabko, tanggal) DO UPDATE SET
                %s
        """ % (columns_str, args_str, updates_str))
        
        conn.commit()
    
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
        """)
        
        return [x for x, in cur.fetchall()]
    
def fetch_kabko_dict():
    with database.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM main.kabko
        """)
        
        return {k:v for k, v in cur.fetchall()}
    
def fetch_data(kabko):
    with database.get_conn() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT * FROM main.raw_covid_data
            WHERE kabko=%s
        """, (kabko,))
        
        return [RawData(**RawData.from_db_row(row)) for row in cur.fetchall()]