import sqlite3, os, random
from faker import Faker

os.makedirs('data', exist_ok=True)
db_path = os.path.join('data', 'synthetic_socialcare2.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop tables if they exist
cursor.executescript("""
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS outcomes;
""")

# Create tables
cursor.executescript("""
CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    postcode TEXT
);
CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    assessment_date TEXT,
    assessment_type TEXT,
    assessor TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
CREATE TABLE services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    service_name TEXT,
    start_date TEXT,
    end_date TEXT,
    provider TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
CREATE TABLE outcomes (
    outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    outcome_date TEXT,
    outcome_type TEXT,
    outcome_value TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
""")

# Populate
fake = Faker("en_GB")
N_CLIENTS = 50
for client_id in range(1, N_CLIENTS + 1):
    cursor.execute("INSERT INTO clients VALUES (?, ?, ?, ?, ?)", 
                   (client_id, fake.name(), random.randint(18, 95),
                    random.choice(["Male", "Female"]), fake.postcode()))
conn.commit()
print("✅ Database created and populated.")
