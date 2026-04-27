import json
import csv
import re
from connect import get_connection


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

def show_menu():
    print("\n=== Телефонная книга (TSIS 1) ===")
    print("1.  Показать все контакты")
    print("2.  Навигация по страницам (next/prev)")
    print("3.  Поиск (имя / email / телефон)")
    print("4.  Фильтр по группе")
    print("5.  Добавить контакт")
    print("6.  Добавить номер к контакту")
    print("7.  Переместить в группу")
    print("8.  Удалить контакт")
    print("9.  Экспорт в JSON")
    print("10. Импорт из JSON")
    print("11. Импорт из CSV")
    print("0.  Выход")
    return input("Выберите действие: ").strip()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def print_row(row):
    id_, name, email, birthday, grp, phones = row
    print(f"  ID: {id_:<4} | {name:<22} | {str(email or ''):<28} | "
          f"ДР: {str(birthday or ''):<12} | Группа: {str(grp or ''):<10} | {phones or ''}")


def valid_phone(phone: str) -> bool:
    return bool(re.match(r'^\+?[0-9]{10,15}$', phone.strip()))


# ─────────────────────────────────────────────
#  1. SHOW ALL
# ─────────────────────────────────────────────

def show_all():
    sort_options = {"1": "name", "2": "birthday", "3": "created_at"}
    print("Сортировка: 1-Имя  2-ДР  3-Дата добавления")
    choice = input("Выбор (по умолч. 1): ").strip() or "1"
    sort_by = sort_options.get(choice, "name")

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT c.id, c.name, c.email, c.birthday, g.name, "
        "STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') "
        "FROM contacts c "
        "LEFT JOIN groups g ON g.id = c.group_id "
        "LEFT JOIN phones p ON p.contact_id = c.id "
        "GROUP BY c.id, c.name, c.email, c.birthday, g.name "
        f"ORDER BY c.{sort_by}"
    )
    rows = cur.fetchall()
    print(f"\nВсего контактов: {len(rows)}")
    for row in rows:
        print_row(row)
    cur.close()
    conn.close()


# ─────────────────────────────────────────────
#  2. PAGINATED NAVIGATION
# ─────────────────────────────────────────────

def paginated_navigation():
    limit = int(input("Записей на странице (по умолч. 5): ").strip() or 5)
    sort_options = {"1": "name", "2": "birthday", "3": "created_at"}
    print("Сортировка: 1-Имя  2-ДР  3-Дата добавления")
    choice = input("Выбор (по умолч. 1): ").strip() or "1"
    sort_by = sort_options.get(choice, "name")

    offset = 0
    while True:
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_paginated_full(%s, %s, %s)",
                    (limit, offset, sort_by))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows and offset == 0:
            print("Контактов нет.")
            return

        print(f"\n--- Страница (offset={offset}) ---")
        if rows:
            for row in rows:
                print_row(row)
        else:
            print("  (больше записей нет)")

        cmd = input("\n[next / prev / quit]: ").strip().lower()
        if cmd == "next":
            if len(rows) < limit:
                print("Это последняя страница.")
            else:
                offset += limit
        elif cmd == "prev":
            offset = max(0, offset - limit)
        elif cmd == "quit":
            break


# ─────────────────────────────────────────────
#  3. SEARCH
# ─────────────────────────────────────────────

def search():
    query = input("Поиск (имя / email / телефон): ").strip()
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    print(f"\nНайдено: {len(rows)}")
    for row in rows:
        print_row(row)
    cur.close()
    conn.close()


# ─────────────────────────────────────────────
#  4. FILTER BY GROUP
# ─────────────────────────────────────────────

def filter_by_group():
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cur.fetchall()
    print("\nГруппы:")
    for g in groups:
        print(f"  {g[0]}. {g[1]}")
    gid = input("Введите ID группы: ").strip()
    cur.execute(
        "SELECT c.id, c.name, c.email, c.birthday, g.name, "
        "STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') "
        "FROM contacts c "
        "LEFT JOIN groups g ON g.id = c.group_id "
        "LEFT JOIN phones p ON p.contact_id = c.id "
        "WHERE c.group_id = %s "
        "GROUP BY c.id, c.name, c.email, c.birthday, g.name "
        "ORDER BY c.name",
        (gid,)
    )
    rows = cur.fetchall()
    print(f"\nКонтактов в группе: {len(rows)}")
    for row in rows:
        print_row(row)
    cur.close()
    conn.close()


# ─────────────────────────────────────────────
#  5. ADD CONTACT
# ─────────────────────────────────────────────

def add_contact():
    name = input("Имя: ").strip()
    phone = input("Телефон: ").strip()
    ptype = input("Тип телефона (home/work/mobile, по умолч. mobile): ").strip() or "mobile"
    email = input("Email (необяз.): ").strip() or None
    birthday = input("День рождения (YYYY-MM-DD, необяз.): ").strip() or None

    if not valid_phone(phone):
        print("Ошибка: неверный формат телефона.")
        return

    # Show groups
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cur.fetchall()
    print("\nГруппы:")
    for g in groups:
        print(f"  {g[0]}. {g[1]}")
    gid = input("ID группы (необяз.): ").strip() or None

    try:
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, email, birthday, gid)
        )
        contact_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
            (contact_id, phone, ptype)
        )
        conn.commit()
        print(f"Контакт '{name}' добавлен.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  6. ADD PHONE TO CONTACT
# ─────────────────────────────────────────────

def add_phone():
    name = input("Имя контакта: ").strip()
    phone = input("Новый телефон: ").strip()
    ptype = input("Тип (home/work/mobile, по умолч. mobile): ").strip() or "mobile"

    if not valid_phone(phone):
        print("Ошибка: неверный формат телефона.")
        return

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("Телефон добавлен.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  7. MOVE TO GROUP
# ─────────────────────────────────────────────

def move_to_group():
    name = input("Имя контакта: ").strip()
    group = input("Название группы: ").strip()
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"Контакт '{name}' перемещён в группу '{group}'.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  8. DELETE CONTACT
# ─────────────────────────────────────────────

def delete_contact():
    choice = input("Удалить по (1) имени или (2) телефону? ").strip()
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        if choice == "1":
            name = input("Имя: ").strip()
            cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        elif choice == "2":
            phone = input("Телефон: ").strip()
            cur.execute("DELETE FROM phones WHERE phone = %s", (phone,))
        else:
            print("Неверный выбор.")
            return
        conn.commit()
        print("Удалено.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  9. EXPORT TO JSON
# ─────────────────────────────────────────────

def export_json():
    filename = input("Имя файла (по умолч. contacts.json): ").strip() or "contacts.json"
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT c.id, c.name, c.email, c.birthday::TEXT, g.name AS grp "
        "FROM contacts c LEFT JOIN groups g ON g.id = c.group_id ORDER BY c.name"
    )
    contacts = cur.fetchall()
    result = []
    for c in contacts:
        cid, name, email, birthday, grp = c
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]
        result.append({
            "name": name,
            "email": email,
            "birthday": birthday,
            "group": grp,
            "phones": phones
        })
    cur.close()
    conn.close()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Экспортировано {len(result)} контактов в '{filename}'.")


# ─────────────────────────────────────────────
#  10. IMPORT FROM JSON
# ─────────────────────────────────────────────

def import_json():
    filename = input("Имя файла (по умолч. contacts.json): ").strip() or "contacts.json"
    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()

    for item in data:
        name = item.get("name")
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            choice = input(f"Контакт '{name}' уже существует. Перезаписать? (y/n): ").strip().lower()
            if choice != "y":
                continue
            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s WHERE name=%s",
                (item.get("email"), item.get("birthday"), name)
            )
            contact_id = existing[0]
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        else:
            # Get or create group
            grp = item.get("group")
            gid = None
            if grp:
                cur.execute("SELECT id FROM groups WHERE name = %s", (grp,))
                row = cur.fetchone()
                if row:
                    gid = row[0]
                else:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (grp,))
                    gid = cur.fetchone()[0]

            cur.execute(
                "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                (name, item.get("email"), item.get("birthday"), gid)
            )
            contact_id = cur.fetchone()[0]

        for p in item.get("phones", []):
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (contact_id, p["phone"], p.get("type", "mobile"))
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Импорт завершён: {len(data)} записей обработано.")


# ─────────────────────────────────────────────
#  11. IMPORT FROM CSV
# ─────────────────────────────────────────────

def import_csv():
    filename = input("Имя CSV файла (по умолч. contacts.csv): ").strip() or "contacts.csv"
    try:
        with open(filename, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return

    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    added, skipped = 0, 0

    for row in rows:
        name  = row.get("name", "").strip()
        phone = row.get("phone", "").strip()
        ptype = row.get("type", "mobile").strip()
        email = row.get("email", "").strip() or None
        bday  = row.get("birthday", "").strip() or None
        grp   = row.get("group", "").strip() or None

        if not name or not valid_phone(phone):
            print(f"Пропущено (невалидно): {name} / {phone}")
            skipped += 1
            continue

        # Get/create group
        gid = None
        if grp:
            cur.execute("SELECT id FROM groups WHERE name = %s", (grp,))
            r = cur.fetchone()
            if r:
                gid = r[0]
            else:
                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (grp,))
                gid = cur.fetchone()[0]

        try:
            cur.execute(
                "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (name) DO UPDATE SET email=EXCLUDED.email, birthday=EXCLUDED.birthday "
                "RETURNING id",
                (name, email, bday, gid)
            )
            contact_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (contact_id, phone, ptype)
            )
            added += 1
        except Exception as e:
            print(f"Ошибка для '{name}': {e}")
            conn.rollback()
            skipped += 1
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"CSV импорт: добавлено {added}, пропущено {skipped}.")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    while True:
        choice = show_menu()
        if   choice == "1":  show_all()
        elif choice == "2":  paginated_navigation()
        elif choice == "3":  search()
        elif choice == "4":  filter_by_group()
        elif choice == "5":  add_contact()
        elif choice == "6":  add_phone()
        elif choice == "7":  move_to_group()
        elif choice == "8":  delete_contact()
        elif choice == "9":  export_json()
        elif choice == "10": import_json()
        elif choice == "11": import_csv()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неверный выбор.")
