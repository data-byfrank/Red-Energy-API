import sqlite3
import json
import logging
from datetime import datetime, timedelta

DB_NAME = "energy_data.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS customer_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_number TEXT UNIQUE,
            timestamp TEXT,
            data TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS property_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_number TEXT UNIQUE,
            timestamp TEXT,
            data TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS usage_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consumer_number TEXT,     
            property_number TEXT,
            usage_date DATE,
            timestamp TEXT,
            data TEXT,
            UNIQUE (consumer_number, property_number, usage_date)
        )""")

        conn.commit()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        conn.close()

def update_customer_data(customer_number, data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        json_data = json.dumps(data)
        cur.execute("""
            INSERT INTO customer_data (customer_number, timestamp, data)
            VALUES (?, ?, ?)
            ON CONFLICT(customer_number) DO UPDATE SET
                timestamp = excluded.timestamp,
                data = excluded.data
        """, (customer_number, timestamp, json_data))
        conn.commit()
        logging.info(f"Customer data updated for customer_number: {customer_number}")
    except Exception as e:
        logging.error(f"Error updating customer data: {e}")
    finally:
        conn.close()

def update_property_data(property_number, data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        json_data = json.dumps(data)
        cur.execute("""
            INSERT INTO property_data (property_number, timestamp, data)
            VALUES (?, ?, ?)
            ON CONFLICT(property_number) DO UPDATE SET
                timestamp = excluded.timestamp,
                data = excluded.data
        """, (property_number, timestamp, json_data))
        conn.commit()
        logging.info(f"Property data updated for property_number: {property_number}")
    except Exception as e:
        logging.error(f"Error updating property data: {e}")
    finally:
        conn.close()

def update_usage_data(consumer_number, property_number, usage_date, data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        json_data = json.dumps(data)
        cur.execute("""
            INSERT INTO usage_data (consumer_number, property_number, usage_date, timestamp, data)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(consumer_number, property_number, usage_date) DO UPDATE SET
                timestamp = excluded.timestamp,
                data = excluded.data
        """, (consumer_number, property_number, usage_date, timestamp, json_data))
        conn.commit()
        logging.debug(f"Usage data updated for consumer_number: {consumer_number}, property_number: {property_number}, usage_date: {usage_date}")
    except Exception as e:
        logging.error(f"Error updating usage data: {e}")
    finally:
        conn.close()

def get_all_usage_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usage_data")
        rows = cur.fetchall()
        usage_data = []
        for row in rows:
            usage_data.append({
                "consumer_number": row[1],
                "property_number": row[2],
                "usage_date": row[3],
                "timestamp": row[4],
                "data": json.loads(row[5])
            })
        logging.info("Fetched all usage data successfully.")
        return usage_data
    except Exception as e:
        logging.error(f"Error fetching usage data: {e}")
        return []
    finally:
        conn.close()

