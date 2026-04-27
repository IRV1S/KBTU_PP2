import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG

def get_connection():
    """Создаёт и возвращает подключение к БД."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        return None


def init_database():
    """Создаёт таблицы, если их ещё нет."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Таблица игроков
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)

        # Таблица игровых сессий
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
        """)

        conn.commit()
        print("✅ База данных и таблицы инициализированы успешно.")
        return True
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_or_create_player(username: str):
    """Возвращает player_id. Создаёт игрока, если его нет."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()

        # Пытаемся найти игрока
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        result = cur.fetchone()

        if result:
            return result[0]

        # Создаём нового игрока
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        player_id = cur.fetchone()[0]
        conn.commit()
        return player_id
    except Exception as e:
        print(f"Ошибка при работе с игроком: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def save_game_result(username: str, score: int, level_reached: int):
    """Сохраняет результат игры в базу."""
    player_id = get_or_create_player(username)
    if not player_id:
        return False

    conn = get_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO game_sessions (player_id, score, level_reached)
            VALUES (%s, %s, %s)
        """, (player_id, score, level_reached))
        conn.commit()
        print(f"✅ Результат сохранён: {username} — {score} очков (уровень {level_reached})")
        return True
    except Exception as e:
        print(f"Ошибка сохранения результата: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_top_10():
    """Возвращает топ-10 результатов."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("""
            SELECT 
                p.username,
                gs.score,
                gs.level_reached,
                gs.played_at
            FROM game_sessions gs
            JOIN players p ON gs.player_id = p.id
            ORDER BY gs.score DESC, gs.played_at DESC
            LIMIT 10
        """)
        return cur.fetchall()
    except Exception as e:
        print(f"Ошибка получения топ-10: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_personal_best(username: str):
    """Возвращает лучший результат игрока (score, level)."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT gs.score, gs.level_reached
            FROM game_sessions gs
            JOIN players p ON gs.player_id = p.id
            WHERE p.username = %s
            ORDER BY gs.score DESC
            LIMIT 1
        """, (username,))
        result = cur.fetchone()
        return result if result else None
    except Exception as e:
        print(f"Ошибка получения personal best: {e}")
        return None
    finally:
        if conn:
            conn.close()