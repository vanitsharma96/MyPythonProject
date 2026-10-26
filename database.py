import oracledb
from contextlib import closing
from db_config import USER, PASSWORD, HOST, PORT, SERVICE_NAME

def get_connection():
    dsn = oracledb.makedsn(HOST, PORT, service_name=SERVICE_NAME)
    return oracledb.connect(user=USER, password=PASSWORD, dsn=dsn)

def query_all(sql, params=None):
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or {})
            return cur.fetchall()

def call_procedure(name, args):
    with closing(get_connection()) as conn:
        with conn.cursor() as cur:
            cur.callproc(name, args)
            conn.commit()
