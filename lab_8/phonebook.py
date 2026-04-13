# phonebook.py
import psycopg2
from connect import get_connection


def show_menu():
    print("\n=== Телефонная книга (Practice 8) ===")
    print("1. Показать все контакты")
    print("2. Показать контакты с пагинацией")
    print("3. Поиск по шаблону")
    print("4. Добавить / обновить контакт (upsert)")
    print("5. Массовое добавление контактов")
    print("6. Удалить контакт")
    print("0. Выход")
    return input("Выберите действие: ")


def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM contacts ORDER BY name")
    rows = cur.fetchall()
    print("\nВсе контакты:")
    for row in rows:
        print(f"ID: {row[0]:<3} | Имя: {row[1]:<20} | Телефон: {row[2]}")
    cur.close()
    conn.close()


def show_paginated():
    limit = int(input("Сколько записей на странице? (по умолчанию 10): ") or 10)
    offset = int(input("Сдвиг (offset): ") or 0)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    print(f"\nКонтакты (лимит={limit}, offset={offset}):")
    for row in rows:
        print(f"ID: {row[0]:<3} | Имя: {row[1]:<20} | Телефон: {row[2]}")
    cur.close()
    conn.close()


def search_by_pattern():
    pattern = input("Введите часть имени или телефона: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    rows = cur.fetchall()
    if rows:
        print("\nРезультаты поиска:")
        for row in rows:
            print(f"ID: {row[0]:<3} | Имя: {row[1]:<20} | Телефон: {row[2]}")
    else:
        print("Ничего не найдено.")
    cur.close()
    conn.close()


def upsert_contact():
    name = input("Введите имя: ").strip()
    phone = input("Введите телефон: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
        print("Операция upsert выполнена успешно.")
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def bulk_insert():
    print("Введите контакты (пустая строка = закончить)")
    names = []
    phones = []
    while True:
        name = input("Имя (или Enter для завершения): ").strip()
        if not name:
            break
        phone = input("Телефон: ").strip()
        names.append(name)
        phones.append(phone)

    if not names:
        print("Ничего не введено.")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL bulk_insert_contacts(%s, %s, NULL)", (names, phones))
        # Получаем OUT параметр (incorrect)
        result = cur.fetchone()
        incorrect = result[0] if result else "Нет данных"
        conn.commit()
        print("\nРезультат массовой вставки:")
        print(incorrect)
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def delete_contact_menu():
    choice = input("Удалить по (1) имени или (2) телефону? ")
    conn = get_connection()
    cur = conn.cursor()
    try:
        if choice == '1':
            name = input("Имя: ").strip()
            cur.execute("CALL delete_contact(%s, NULL)", (name,))
        elif choice == '2':
            phone = input("Телефон: ").strip()
            cur.execute("CALL delete_contact(NULL, %s)", (phone,))
        else:
            print("Неверный выбор")
            return
        conn.commit()
        print("Удаление выполнено.")
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    while True:
        choice = show_menu()
        if choice == '1':
            show_all_contacts()
        elif choice == '2':
            show_paginated()
        elif choice == '3':
            search_by_pattern()
        elif choice == '4':
            upsert_contact()
        elif choice == '5':
            bulk_insert()
        elif choice == '6':
            delete_contact_menu()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор.")