import os
import sqlite3
import streamlit as st

# Path to your database
db_path = os.path.join(os.path.dirname(__file__), "synthetic_socialcare2.db")

st.write("DB exists?", os.path.isfile(db_path))

if os.path.isfile(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients;")
            count = cursor.fetchone()[0]
        st.write("Number of clients in DB:", count)
    except Exception as e:
        st.error(f"Error querying DB: {e}")
else:
    st.error("Database file not found at expected location.")
