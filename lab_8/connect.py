# connect.py
import psycopg2
from config import DB_CONFIG

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе: {e}")
        return None