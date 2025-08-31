import pymysql
from config import db_config

def createUser(firstname, lastname, email, hashed_password, role):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (firstname, lastname, email, password, role) VALUES (%s, %s, %s, %s, %s)",
        (firstname, lastname, email, hashed_password, role)
    )
    conn.commit()
    cursor.close()
    conn.close()