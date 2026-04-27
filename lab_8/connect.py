# connect.py
import psycopg2
from config import conn

def get_connection():
    try:
        connect = psycopg2.connect(**conn)
        return connect
    except Exception as e:
        print(f"Ошибка подключения к базе: {e}")
        return None