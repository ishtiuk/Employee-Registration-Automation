import sqlite3
import pandas as pd
import streamlit as st


def get_db_connection():
    conn = sqlite3.connect('employee_registration.db')
    return conn

def insert_records(text_info):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with conn:
            cursor.execute('''
            INSERT INTO employees (Employee_Id, Name, Job_position, Department, Email, Phone, Blood_group, Dob, Embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (
                text_info['ID'],
                text_info['Full Name'],
                text_info['Job Position'],
                text_info['Department'],
                text_info['Email'],
                text_info['Phone'],
                text_info['Blood Group'],
                text_info["DOB"],
                str(text_info['Embedding'])
            ))
            conn.commit()
    except sqlite3.IntegrityError:
        st.error("Employee ID already exists. Duplicate records are not allowed.")
    finally:
        conn.close()

def fetch_record(text_info):
    employee_id = text_info['ID']
    conn = get_db_connection()
    query = "SELECT * FROM employees WHERE Employee_Id = ?"
    df = pd.read_sql(query, conn, params=(employee_id,))
    conn.close()
    return df

def fetch_all_records():
    conn = get_db_connection()
    query = "SELECT * FROM employees"
    df = pd.read_sql(query, conn).iloc[:, :-1]
    conn.close()

    if df.empty:
        return None
    return df

def check_duplicacy(text_info):
    df = fetch_record(text_info)
    return not df.empty
