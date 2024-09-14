import os
import sqlite3
import logging


logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, "employee_registration_logs.log"), level=logging.INFO, format=logging_str, filemode="a")

def create_table_if_not_exists():
    conn = sqlite3.connect('employee_registration.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            Employee_Id TEXT PRIMARY KEY,
            Name TEXT,
            Job_position TEXT,
            Department TEXT,
            Email TEXT,
            Phone TEXT,
            Blood_group TEXT,
            Dob TEXT,
            Embedding TEXT
        )
        ''')
        conn.commit()
        logging.info("Table 'employees' created.")
    else:
        logging.info("Table 'employees' already exists.")
    
    conn.close()
