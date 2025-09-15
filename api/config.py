# config.py
import secrets

# Generate a secure secret key
SECRET_KEY = secrets.token_hex(32)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "comptabilite",
    "charset": "utf8mb4"
}
