import pymysql
from config import db_config

def updateUser(email, new_data):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET firstname=%s, lastname=%s, role=%s WHERE email=%s",
        (new_data['firstname'], new_data['lastname'], new_data['role'], email)
    )
    conn.commit()
    cursor.close()
    conn.close()