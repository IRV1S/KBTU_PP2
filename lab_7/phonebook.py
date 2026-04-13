# phonebook.py
import psycopg2
from connect import get_connection


def show_menu():
    print("\n=== Телефонная книга ===")
    print("1. Показать все контакты")
    print("2. Добавить контакт")
    print("3. Найти контакт")
    print("4. Обновить контакт")
    print("5. Удалить контакт")
    print("6. Добавить контакты из CSV")
    print("0. Выход")
    return input("Выберите действие: ")


def show_all_contacts():
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM contacts ORDER BY name")
    rows = cur.fetchall() # Получаем все строки результата
    print("\nВсе контакты:")
    for row in rows:
        print(f"ID: {row[0]} | Имя: {row[1]} | Телефон: {row[2]}")
    cur.close()
    conn.close()


def add_contact():
    name = input("Введите имя: ").strip()
    phone = input("Введите телефон: ").strip()

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit() # Сохраняем изменения в базе
        print("Контакт успешно добавлен!")
    except psycopg2.errors.UniqueViolation:
        print("Ошибка: Такой телефон уже существует!")
        conn.rollback() # Отменяем изменения при ошибке
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def search_contact():
    pattern = input("Введите имя или часть телефона для поиска: ").strip()
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
                SELECT id, name, phone
                FROM contacts
                WHERE name ILIKE %s
                   OR phone ILIKE %s
                """, (f'%{pattern}%', f'%{pattern}%'))
    rows = cur.fetchall()
    if rows:
        print("\nНайденные контакты:")
        for row in rows:
            print(f"ID: {row[0]} | Имя: {row[1]} | Телефон: {row[2]}")
    else:
        print("Ничего не найдено.")
    cur.close()
    conn.close()


def update_contact():
    name = input("Введите имя контакта для обновления: ").strip()
    new_phone = input("Введите новый телефон: ").strip()

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("UPDATE contacts SET phone = %s WHERE name = %s", (new_phone, name))
        if cur.rowcount > 0:
            conn.commit()
            print("Контакт обновлён!")
        else:
            print("Контакт с таким именем не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def delete_contact():
    choice = input("Удалить по (1) имени или (2) телефону? ")
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        if choice == '1':
            name = input("Введите имя: ").strip()
            cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        elif choice == '2':
            phone = input("Введите телефон: ").strip()
            cur.execute("DELETE FROM contacts WHERE phone = %s", (phone,))
        else:
            print("Неверный выбор.")
            return

        if cur.rowcount > 0:
            conn.commit()
            print("Контакт удалён!")
        else:
            print("Контакт не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def load_from_csv():
    # Простая версия — можно улучшить
    try:
        with open('contacts.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:]  # пропускаем заголовок
        conn = get_connection()
        cur = conn.cursor()
        for line in lines:
            if line.strip():
                name, phone = line.strip().split(',')
                try:
                    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING",
                                (name.strip(), phone.strip()))
                except:
                    pass
        conn.commit()
        print("Контакты из CSV загружены!")
        cur.close()
        conn.close()
    except FileNotFoundError:
        print("Файл contacts.csv не найден!")


# Главный цикл
if __name__ == "__main__":
    while True:
        choice = show_menu()
        if choice == '1':
            show_all_contacts()
        elif choice == '2':
            add_contact()
        elif choice == '3':
            search_contact()
        elif choice == '4':
            update_contact()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            load_from_csv()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")