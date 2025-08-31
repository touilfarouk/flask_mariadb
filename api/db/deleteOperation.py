import pymysql
from config import db_config

def delete_all_users():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    cursor.close()
    conn.close()