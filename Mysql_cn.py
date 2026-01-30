import sqlite3
import pymysql
from tqdm import tqdm

class ConectorDB:#Credenciales BD MySQL
    def __init__(self):
        self.mysql_conf = {
            "host": "localhost",
            "user": "jhojan",
            "password": "Myestrell@1929*",
            "database": "J_Arrendatarios",
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor
        }

    def baseConnect(self):
            return pymysql.connect(**self.mysql_conf)
    
#Migration Funtion SQL to Mysql 
    def migration(self):
        SQLITE_DB = "data/J0BaseDatos.db"
        MYSQL_CONFIG = {
        "host": "localhost",
        "user": "jhojan",
        "password": "Myestrell@1929*",
        "database": "J_Arrendatarios",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor}    
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)

        sqlite_cur = sqlite_conn.cursor()
        mysql_cur = mysql_conn.cursor()

        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

        tables = [t[0] for t in sqlite_cur.fetchall() if t[0] != 'sqlite_sequence']
        for table in tables:
            print(f"Migrating table: {table}")

            sqlite_cur.execute(f"SELECT * FROM {table}")
            filas = sqlite_cur.fetchall()
            if not filas:
                print("  (empty table, skipping)")
            continue

        #Obt valid c  
        mysql_cur.execute(f"DESCRIBE {table}")
        columnas_mysql = [col["Field"] for col in mysql_cur.fetchall()]

        # filter ambas db in tables 
        columnas_comunes = [c for c in filas[0].keys() if c in columnas_mysql]
        columnas_str = ", ".join(columnas_comunes)
        placeholders = ", ".join(["%s"] * len(columnas_comunes))
        insert_sql = f"INSERT INTO {table} ({columnas_str}) VALUES ({placeholders})"

        for fila in tqdm(filas, desc=f"   Insertando {table}", ncols=80):
            valores = [fila[c] for c in columnas_comunes]
            try:
                mysql_cur.execute(insert_sql, valores)
            except Exception as e:
                print(f" Error in row: {dict(fila)}")
                print(f"   Reason: {e}")

        mysql_conn.commit()
        print("\n Data Migration Completed.")

        sqlite_conn.close()
        mysql_conn.close()
