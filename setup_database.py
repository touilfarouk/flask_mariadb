#!/usr/bin/env python3
"""
Database setup script for the Flask MariaDB project.
This script will create the database and tables using the sql.sql file.
"""

import pymysql
import sys
import os

def setup_database():
    """Setup the database using the sql.sql file"""
    
    # Database connection config (without database name for initial setup)
    initial_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "charset": "utf8mb4"
    }
    
    try:
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'api', 'sql.sql')
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        connection = pymysql.connect(**initial_config)
        
        # Split SQL content by statements and execute them
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement.upper().startswith(('CREATE', 'INSERT', 'USE', 'SET', 'START', 'COMMIT')):
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)
            
            connection.commit()
        
        print("Database setup completed successfully!")
        print("Default admin user created:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"SQL file not found: {sql_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    setup_database()
