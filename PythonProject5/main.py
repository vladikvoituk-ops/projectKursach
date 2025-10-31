import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os

DB_FILE = 'library.db'

# УБИРАЕМ УДАЛЕНИЕ БАЗЫ ДАННЫХ ПРИ КАЖДОМ ЗАПУСКЕ
# if os.path.exists(DB_FILE):
#     os.remove(DB_FILE)

COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#2d2d2d',
    'bg_light': '#3d3d3d',
    'accent_blue': '#2962ff',
    'accent_green': '#00c853',
    'accent_orange': '#ff6d00',
    'accent_red': '#d50000',
    'text_primary': '#ffffff',
    'text_secondary': '#cccccc',
    'card_bg': '#2d2d2d'
}


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            registration_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(role_id) REFERENCES roles(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            book_type_id INTEGER NOT NULL,
            isbn TEXT UNIQUE,
            genre_id INTEGER,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            available_quantity INTEGER NOT NULL DEFAULT 1,
            description TEXT,
            created_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(book_type_id) REFERENCES book_types(id),
            FOREIGN KEY(genre_id) REFERENCES genres(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rent_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            rent_date DATE NOT NULL,
            expected_return_date DATE NOT NULL,
            actual_return_date DATE,
            status_id INTEGER NOT NULL,
            cost REAL NOT NULL,
            confirmed_by INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(status_id) REFERENCES rent_statuses(id),
            FOREIGN KEY(confirmed_by) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rent_id INTEGER,
            amount REAL NOT NULL,
            payment_date DATE DEFAULT CURRENT_DATE,
            status_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(rent_id) REFERENCES rents(id),
            FOREIGN KEY(status_id) REFERENCES payment_statuses(id)
        )
    ''')

    # ПРОВЕРЯЕМ, НУЖНО ЛИ ЗАПОЛНЯТЬ ДАННЫЕ
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        print("Инициализация базы данных...")
        roles = [
            ('admin', 'Администратор системы'),
            ('librarian', 'Библиотекарь'),
            ('reader', 'Читатель')
        ]
        cursor.executemany("INSERT INTO roles (role_name, description) VALUES (?, ?)", roles)

    cursor.execute("SELECT COUNT(*) FROM genres")
    if cursor.fetchone()[0] == 0:
        genres = [
            ('Роман', 'Художественная проза'),
            ('Антиутопия', 'Жанр научной фантастики'),
            ('Фэнтези', 'Фантастическая литература'),
            ('Философия', 'Философские произведения'),
            ('Детектив', 'Детективная литература'),
            ('Научная литература', 'Научные произведения')
        ]
        cursor.executemany("INSERT INTO genres (genre_name, description) VALUES (?, ?)", genres)

    cursor.execute("SELECT COUNT(*) FROM book_types")
    if cursor.fetchone()[0] == 0:
        book_types = [
            ('physical', 'Физическая книга'),
            ('digital', 'Цифровая книга')
        ]
        cursor.executemany("INSERT INTO book_types (type_name, description) VALUES (?, ?)", book_types)

    cursor.execute("SELECT COUNT(*) FROM rent_statuses")
    if cursor.fetchone()[0] == 0:
        statuses = [
            ('reserved', 'Забронирована'),
            ('active', 'Активна'),
            ('waiting_return', 'Ожидает возврата'),
            ('returned', 'Возвращена'),
            ('overdue', 'Просрочена'),
            ('auto_returned', 'Авто-возврат')
        ]
        cursor.executemany("INSERT INTO rent_statuses (status_name, description) VALUES (?, ?)", statuses)

    cursor.execute("SELECT COUNT(*) FROM payment_statuses")
    if cursor.fetchone()[0] == 0:
        payment_statuses = [
            ('pending', 'Ожидает оплаты'),
            ('completed', 'Оплачено'),
            ('failed', 'Ошибка оплаты'),
            ('refunded', 'Возвращено')
        ]
        cursor.executemany("INSERT INTO payment_statuses (status_name, description) VALUES (?, ?)", payment_statuses)

    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM roles WHERE role_name='admin'")
        admin_role_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM roles WHERE role_name='librarian'")
        librarian_role_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM roles WHERE role_name='reader'")
        reader_role_id = cursor.fetchone()[0]

        users = [
            ('admin', 'admin123', 'admin@library.ru', admin_role_id),
            ('librarian', 'lib123', 'librarian@library.ru', librarian_role_id),
            ('reader', 'read123', 'reader@library.ru', reader_role_id),
            ('user1', 'user123', 'user1@mail.ru', reader_role_id),
            ('user2', 'user123', 'user2@mail.ru', reader_role_id)
        ]
        cursor.executemany("INSERT INTO users (username, password, email, role_id) VALUES (?, ?, ?, ?)", users)

    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM book_types WHERE type_name='physical'")
        physical_type_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM book_types WHERE type_name='digital'")
        digital_type_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM genres WHERE genre_name='Роман'")
        roman_genre_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM genres WHERE genre_name='Антиутопия'")
        antiutopia_genre_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM genres WHERE genre_name='Фэнтези'")
        fantasy_genre_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM genres WHERE genre_name='Философия'")
        philosophy_genre_id = cursor.fetchone()[0]

        sample_books = [
            ('Война и мир', 'Лев Толстой', physical_type_id, '978-5-699-12014-7', roman_genre_id, 50.0, 3, 3,
             'Классика русской литературы'),
            ('1984', 'Джордж Оруэлл', digital_type_id, '978-5-699-80667-2', antiutopia_genre_id, 30.0, 999, 999,
             'Цифровая книга - классика антиутопии'),
            ('Мастер и Маргарита', 'Михаил Булгаков', physical_type_id, '978-5-389-05787-4', fantasy_genre_id, 45.0, 2,
             2,
             'Мистический роман'),
            ('Гарри Поттер и философский камень', 'Джоан Роулинг', digital_type_id, '978-5-389-07435-2',
             fantasy_genre_id, 40.0, 999,
             999, 'Первая книга серии'),
            ('Преступление и наказание', 'Федор Достоевский', physical_type_id, '978-5-17-090675-9', roman_genre_id,
             35.0, 4, 4,
             'Психологический роман'),
            ('Анна Каренина', 'Лев Толстой', physical_type_id, '978-5-389-01234-5', roman_genre_id, 48.0, 2, 2,
             'Трагическая история любви'),
            ('Маленький принц', 'Антуан де Сент-Экзюпери', digital_type_id, '978-5-699-34567-8', philosophy_genre_id,
             25.0, 999, 999,
             'Философская сказка')
        ]
        cursor.executemany('''INSERT INTO books (title, author, book_type_id, isbn, genre_id, price, quantity, available_quantity, description) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_books)

    conn.commit()
    conn.close()


init_db()

current_user = None
cart = []


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_db_connection():
    return sqlite3.connect(DB_FILE)


def login_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id, u.username, r.role_name, u.password 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE u.username=? AND u.status='active'
    ''', (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_id, db_username, db_role, db_password = user_data

        if role == 'admin' and db_role != 'admin':
            return False
        if role == 'librarian' and db_role not in ['librarian', 'admin']:
            return False

        password_correct = (password == db_password or hash_password(password) == db_password)

        if password_correct:
            global current_user
            current_user = {'id': user_id, 'username': db_username, 'role': db_role}
            return True

    return False


def register_user(username, password, email='', role='reader'):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM roles WHERE role_name=?", (role,))
        role_data = cursor.fetchone()
        if not role_data:
            return False

        role_id = role_data[0]
        hashed_pwd = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, email, role_id) VALUES (?, ?, ?, ?)",
                       (username, hashed_pwd, email, role_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_books(search='', genre='', book_type=''):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT b.id, b.title, b.author, bt.type_name, b.isbn, g.genre_name, 
               b.price, b.quantity, b.available_quantity, b.description
        FROM books b
        LEFT JOIN genres g ON b.genre_id = g.id
        LEFT JOIN book_types bt ON b.book_type_id = bt.id
        WHERE 1=1
    '''
    params = []

    if search:
        query += " AND (b.title LIKE ? OR b.author LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])

    if genre and genre != 'Все жанры':
        query += " AND g.genre_name = ?"
        params.append(genre)

    if book_type and book_type != 'Все типы':
        query += " AND bt.type_name = ?"
        params.append(book_type)

    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()
    return books


def get_genres():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT genre_name FROM genres ORDER BY genre_name")
    genres = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ['Все жанры'] + genres


def get_book_types():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type_name FROM book_types")
    types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ['Все типы'] + types


def add_book(title, author, book_type, isbn, genre, price, quantity, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM book_types WHERE type_name=?", (book_type,))
        type_data = cursor.fetchone()
        if not type_data:
            return False
        book_type_id = type_data[0]

        genre_id = None
        if genre:
            cursor.execute("SELECT id FROM genres WHERE genre_name=?", (genre,))
            genre_data = cursor.fetchone()
            if genre_data:
                genre_id = genre_data[0]

        cursor.execute('''INSERT INTO books (title, author, book_type_id, isbn, genre_id, price, quantity, available_quantity, description) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (title, author, book_type_id, isbn, genre_id, price, quantity, quantity, description))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def update_book(book_id, title, author, book_type, isbn, genre, price, quantity, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM book_types WHERE type_name=?", (book_type,))
        type_data = cursor.fetchone()
        if not type_data:
            return False
        book_type_id = type_data[0]

        genre_id = None
        if genre:
            cursor.execute("SELECT id FROM genres WHERE genre_name=?", (genre,))
            genre_data = cursor.fetchone()
            if genre_data:
                genre_id = genre_data[0]

        cursor.execute('''UPDATE books SET title=?, author=?, book_type_id=?, isbn=?, genre_id=?, price=?, quantity=?, description=?
                       WHERE id=?''',
                       (title, author, book_type_id, isbn, genre_id, price, quantity, description, book_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def reserve_books(user_id, book_ids):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='reserved'")
        reserved_status_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='active'")
        active_status_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM payment_statuses WHERE status_name='completed'")
        completed_status_id = cursor.fetchone()[0]

        total_cost = 0
        for book_id in book_ids:
            cursor.execute('''
                SELECT bt.type_name, b.price, b.available_quantity 
                FROM books b
                JOIN book_types bt ON b.book_type_id = bt.id
                WHERE b.id=?
            ''', (book_id,))
            book_data = cursor.fetchone()

            if book_data and book_data[2] > 0:
                book_type, price, available = book_data
                rent_date = datetime.now().date().isoformat()
                return_date = (datetime.now().date() + timedelta(days=14)).isoformat()
                cost = price * 14
                total_cost += cost

                cursor.execute('''INSERT INTO rents (user_id, book_id, rent_date, expected_return_date, status_id, cost) 
                               VALUES (?, ?, ?, ?, ?, ?)''',
                               (user_id, book_id, rent_date, return_date, reserved_status_id, cost))

                if book_type == 'digital':
                    cursor.execute("UPDATE rents SET status_id=? WHERE id=?", (active_status_id, cursor.lastrowid))

                cursor.execute("UPDATE books SET available_quantity = available_quantity - 1 WHERE id=?", (book_id,))

        if total_cost > 0:
            cursor.execute("INSERT INTO payments (user_id, amount, status_id) VALUES (?, ?, ?)",
                           (user_id, total_cost, completed_status_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def get_user_rents(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, b.title, b.author, bt.type_name, r.rent_date, r.expected_return_date, 
               r.actual_return_date, rs.status_name, r.cost
        FROM rents r 
        JOIN books b ON r.book_id = b.id
        JOIN book_types bt ON b.book_type_id = bt.id
        JOIN rent_statuses rs ON r.status_id = rs.id
        WHERE r.user_id = ?
        ORDER BY r.rent_date DESC
    ''', (user_id,))
    rents = cursor.fetchall()
    conn.close()
    return rents


def get_all_rents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, u.username, b.title, bt.type_name, r.rent_date, r.expected_return_date,
               r.actual_return_date, rs.status_name, r.cost
        FROM rents r 
        JOIN users u ON r.user_id = u.id
        JOIN books b ON r.book_id = b.id
        JOIN book_types bt ON b.book_type_id = bt.id
        JOIN rent_statuses rs ON r.status_id = rs.id
        ORDER BY r.rent_date DESC
    ''')
    rents = cursor.fetchall()
    conn.close()
    return rents


def confirm_pickup(rent_id, librarian_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='active'")
        active_status_id = cursor.fetchone()[0]

        cursor.execute("UPDATE rents SET status_id=?, confirmed_by=? WHERE id=?",
                       (active_status_id, librarian_id, rent_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def confirm_return(rent_id, librarian_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT book_id FROM rents WHERE id=?", (rent_id,))
        book_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='returned'")
        returned_status_id = cursor.fetchone()[0]

        return_date = datetime.now().date().isoformat()

        cursor.execute("UPDATE rents SET status_id=?, actual_return_date=?, confirmed_by=? WHERE id=?",
                       (returned_status_id, return_date, librarian_id, rent_id))
        cursor.execute("UPDATE books SET available_quantity = available_quantity + 1 WHERE id=?", (book_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_pending_actions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM rent_statuses WHERE status_name='reserved'")
    reserved_status_id = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM rents r
        JOIN books b ON r.book_id = b.id
        JOIN book_types bt ON b.book_type_id = bt.id
        WHERE r.status_id=? AND bt.type_name='physical'
    ''', (reserved_status_id,))
    pending_pickups = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM rents 
        WHERE status_id IN (SELECT id FROM rent_statuses WHERE status_name IN ('active', 'reserved')) 
        AND expected_return_date < date('now')
    ''')
    pending_returns = cursor.fetchone()[0]

    conn.close()
    return pending_pickups, pending_returns


def get_library_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_name='reader' AND u.status='active'")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM books")
    books_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM books")
    total_books = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(available_quantity) FROM books")
    available_books = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM rents WHERE status_id IN (SELECT id FROM rent_statuses WHERE status_name IN ('active', 'reserved'))")
    active_rents = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')")
    monthly_revenue = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM payments")
    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT COUNT(*) FROM rents 
        WHERE status_id IN (SELECT id FROM rent_statuses WHERE status_name IN ('active', 'reserved')) 
        AND expected_return_date < date('now')
    ''')
    overdue_rents = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM rents r
        JOIN books b ON r.book_id = b.id
        JOIN book_types bt ON b.book_type_id = bt.id
        WHERE bt.type_name='digital' AND r.status_id IN (SELECT id FROM rent_statuses WHERE status_name='active')
    ''')
    digital_rents = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM rents r
        JOIN books b ON r.book_id = b.id
        JOIN book_types bt ON b.book_type_id = bt.id
        WHERE bt.type_name='physical' AND r.status_id IN (SELECT id FROM rent_statuses WHERE status_name='active')
    ''')
    physical_rents = cursor.fetchone()[0]

    conn.close()

    return {
        'users': users_count,
        'books': books_count,
        'total_books': total_books,
        'available_books': available_books,
        'active_rents': active_rents,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'overdue_rents': overdue_rents,
        'digital_rents': digital_rents,
        'physical_rents': physical_rents
    }


def auto_return_expired_digital_books():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='auto_returned'")
        auto_returned_status_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM rent_statuses WHERE status_name='active'")
        active_status_id = cursor.fetchone()[0]

        cursor.execute('''
            SELECT r.id, r.book_id 
            FROM rents r 
            JOIN books b ON r.book_id = b.id
            JOIN book_types bt ON b.book_type_id = bt.id
            WHERE bt.type_name = 'digital' 
            AND r.status_id = ?
            AND r.expected_return_date <= date('now')
        ''', (active_status_id,))

        expired_rents = cursor.fetchall()

        for rent_id, book_id in expired_rents:
            return_date = datetime.now().date().isoformat()
            cursor.execute("UPDATE rents SET status_id=?, actual_return_date=? WHERE id=?",
                           (auto_returned_status_id, return_date, rent_id))
            cursor.execute("UPDATE books SET available_quantity = available_quantity + 1 WHERE id=?", (book_id,))

        conn.commit()
        return len(expired_rents)
    except Exception as e:
        conn.rollback()
        print(f"Error in auto_return: {e}")
        return 0
    finally:
        conn.close()


def promote_to_librarian(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM roles WHERE role_name='librarian'")
        librarian_role_id = cursor.fetchone()[0]

        cursor.execute("UPDATE users SET role_id=? WHERE id=?", (librarian_role_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.email, r.role_name, u.registration_date, u.status 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE r.role_name != 'admin'
    ''')
    users = cursor.fetchall()
    conn.close()
    return users


def get_remaining_days(rent_date, expected_return_date):
    today = datetime.now().date()
    expected = datetime.strptime(expected_return_date, '%Y-%m-%d').date()
    remaining = (expected - today).days
    return max(0, remaining)


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=35, color=COLORS['accent_blue']):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=COLORS['bg_dark'])
        self.command = command
        self.color = color

        self.rect = self.create_rectangle(2, 2, width - 2, height - 2, fill=color, outline=color, width=2)
        self.text = self.create_text(width // 2, height // 2, text=text, fill=COLORS['text_primary'],
                                     font=('Arial', 9, 'bold'))

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=COLORS['accent_green'])

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)


class BookCard(tk.Frame):
    def __init__(self, parent, book_data, on_reserve=None):
        super().__init__(parent, bg=COLORS['card_bg'], relief='raised', bd=1,
                         highlightbackground=COLORS['accent_blue'], highlightthickness=1)
        self.book_data = book_data
        self.on_reserve = on_reserve
        self.setup_ui()

    def setup_ui(self):
        book_id = self.book_data[0]
        title = self.book_data[1]
        author = self.book_data[2]
        book_type = self.book_data[3]
        isbn = self.book_data[4]
        genre = self.book_data[5]
        price = self.book_data[6]
        quantity = self.book_data[7]
        available = self.book_data[8]
        description = self.book_data[9] if len(self.book_data) > 9 else ""

        type_color = COLORS['accent_green'] if book_type == 'digital' else COLORS['accent_blue']
        type_icon = "💻" if book_type == 'digital' else "📚"

        title_label = tk.Label(self, text=title, font=('Arial', 11, 'bold'),
                               bg=COLORS['card_bg'], fg=COLORS['text_primary'], wraplength=200)
        title_label.pack(pady=(10, 5), padx=10, anchor='w')

        author_label = tk.Label(self, text=f"👤 {author}", font=('Arial', 9),
                                bg=COLORS['card_bg'], fg=COLORS['text_secondary'])
        author_label.pack(pady=2, padx=10, anchor='w')

        type_label = tk.Label(self, text=f"{type_icon} {book_type.upper()}", font=('Arial', 9),
                              bg=COLORS['card_bg'], fg=type_color)
        type_label.pack(pady=2, padx=10, anchor='w')

        info_frame = tk.Frame(self, bg=COLORS['card_bg'])
        info_frame.pack(pady=5, padx=10, fill='x')

        price_label = tk.Label(info_frame, text=f"💵 {price} руб/день",
                               font=('Arial', 9), bg=COLORS['card_bg'], fg=COLORS['accent_orange'])
        price_label.pack(side='left')

        available_label = tk.Label(info_frame, text=f"📖 {available}/{quantity}",
                                   font=('Arial', 9), bg=COLORS['card_bg'],
                                   fg=COLORS['accent_green'] if available > 0 else COLORS['accent_red'])
        available_label.pack(side='right')

        if self.on_reserve and available > 0:
            reserve_btn = ModernButton(self, "📦 Забронировать",
                                       command=lambda: self.on_reserve(self.book_data),
                                       width=140, height=30, color=type_color)
            reserve_btn.pack(pady=10)


root = tk.Tk()
root.title("📚 Гибридная Библиотека")
root.geometry("1200x700")
root.configure(bg=COLORS['bg_dark'])

style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background=COLORS['bg_dark'])
style.configure('TLabel', background=COLORS['bg_dark'], foreground=COLORS['text_primary'])
style.configure('Treeview', background=COLORS['bg_medium'], foreground=COLORS['text_primary'],
                fieldbackground=COLORS['bg_medium'])
style.configure('Treeview.Heading', background=COLORS['accent_blue'], foreground=COLORS['text_primary'])

login_frame = ttk.Frame(root)
reader_frame = ttk.Frame(root)
librarian_frame = ttk.Frame(root)
admin_frame = ttk.Frame(root)


def show_frame(frame):
    login_frame.pack_forget()
    reader_frame.pack_forget()
    librarian_frame.pack_forget()
    admin_frame.pack_forget()
    frame.pack(fill='both', expand=True)


def create_login_screen():
    show_frame(login_frame)
    for widget in login_frame.winfo_children():
        widget.destroy()

    main_container = tk.Frame(login_frame, bg=COLORS['bg_dark'])
    main_container.pack(expand=True, fill='both')

    header_frame = tk.Frame(main_container, bg=COLORS['bg_dark'])
    header_frame.pack(pady=50)

    tk.Label(header_frame, text="📚", font=('Arial', 48), bg=COLORS['bg_dark'], fg=COLORS['accent_blue']).pack()
    tk.Label(header_frame, text="ГИБРИДНАЯ БИБЛИОТЕКА", font=('Arial', 20, 'bold'),
             bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=10)

    button_container = tk.Frame(main_container, bg=COLORS['bg_dark'])
    button_container.pack(pady=30)

    def open_login(role):
        login_win = tk.Toplevel(root)
        login_win.title(f"Вход - {role}")
        login_win.geometry("400x300")  # Увеличил размер окна
        login_win.configure(bg=COLORS['bg_dark'])
        login_win.resizable(False, False)
        login_win.grab_set()

        # Центрирование окна
        login_win.transient(root)
        login_win.geometry("+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 100))

        tk.Label(login_win, text=f"Вход как {role}", font=('Arial', 14, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=25)

        form_frame = tk.Frame(login_win, bg=COLORS['bg_dark'])
        form_frame.pack(pady=20, padx=40, fill='x')

        tk.Label(form_frame, text="Логин:", bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                 font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=12)
        username_entry = ttk.Entry(form_frame, width=25, font=('Arial', 10))
        username_entry.grid(row=0, column=1, pady=12, padx=15, sticky='ew')

        tk.Label(form_frame, text="Пароль:", bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                 font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=12)
        password_entry = ttk.Entry(form_frame, show="*", width=25, font=('Arial', 10))
        password_entry.grid(row=1, column=1, pady=12, padx=15, sticky='ew')

        form_frame.columnconfigure(1, weight=1)

        def do_login():
            if login_user(username_entry.get(), password_entry.get(), role):
                login_win.destroy()
                if current_user['role'] == 'reader':
                    show_reader_interface()
                elif current_user['role'] == 'librarian':
                    show_librarian_interface()
                else:
                    show_admin_interface()
            else:
                messagebox.showerror("Ошибка", "Неверные данные")

        btn_frame = tk.Frame(login_win, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=25)

        ModernButton(btn_frame, "Войти", command=do_login, width=120, height=40).pack(side='left', padx=10)
        ModernButton(btn_frame, "Отмена", command=login_win.destroy, width=120, height=40,
                     color=COLORS['bg_light']).pack(side='left', padx=10)

        username_entry.focus()

        # Обработка нажатия Enter
        def on_enter(event):
            do_login()

        username_entry.bind('<Return>', on_enter)
        password_entry.bind('<Return>', on_enter)

    def open_register():
        reg_win = tk.Toplevel(root)
        reg_win.title("Регистрация читателя")
        reg_win.geometry("400x350")
        reg_win.configure(bg=COLORS['bg_dark'])
        reg_win.resizable(False, False)

        tk.Label(reg_win, text="Регистрация читателя", font=('Arial', 14, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=20)

        form_frame = tk.Frame(reg_win, bg=COLORS['bg_dark'])
        form_frame.pack(pady=20, padx=40, fill='x')

        fields = [("Логин:", "username"), ("Пароль:", "password"), ("Email:", "email")]
        entries = {}

        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                     font=('Arial', 10)).grid(row=i, column=0, sticky='w', pady=12)
            entry = ttk.Entry(form_frame, width=25, font=('Arial', 10),
                              show="*" if field == "password" else "")
            entry.grid(row=i, column=1, pady=12, padx=15, sticky='ew')
            entries[field] = entry

        form_frame.columnconfigure(1, weight=1)

        def do_register():
            username = entries['username'].get()
            password = entries['password'].get()
            email = entries['email'].get()

            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните логин и пароль")
                return

            if register_user(username, password, email, 'reader'):
                messagebox.showinfo("Успех", "Регистрация успешна!")
                reg_win.destroy()
            else:
                messagebox.showerror("Ошибка", "Логин занят")

        btn_frame = tk.Frame(reg_win, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=20)

        ModernButton(btn_frame, "Зарегистрироваться", command=do_register, width=180, height=40).pack()

    roles = [
        ("👤 Читатель", "reader", COLORS['accent_blue']),
        ("📋 Библиотекарь", "librarian", COLORS['accent_green']),
        ("👑 Администратор", "admin", COLORS['accent_orange'])
    ]

    for text, role, color in roles:
        btn_frame = tk.Frame(button_container, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=10)
        ModernButton(btn_frame, text, command=lambda r=role: open_login(r),
                     width=250, height=45, color=color).pack()

    register_frame = tk.Frame(button_container, bg=COLORS['bg_dark'])
    register_frame.pack(pady=20)
    ModernButton(register_frame, "📝 Регистрация читателя", command=open_register,
                 width=250, height=45, color=COLORS['accent_blue']).pack()


def show_reader_interface():
    global cart
    cart = []
    show_frame(reader_frame)

    for widget in reader_frame.winfo_children():
        widget.destroy()

    header = tk.Frame(reader_frame, bg=COLORS['bg_medium'], height=60)
    header.pack(fill='x', pady=5)
    header.pack_propagate(False)

    tk.Label(header, text=f"👤 Читатель: {current_user['username']}", font=('Arial', 14, 'bold'),
             bg=COLORS['bg_medium'], fg=COLORS['text_primary']).pack(side='left', padx=20, pady=20)

    btn_container = tk.Frame(header, bg=COLORS['bg_medium'])
    btn_container.pack(side='right', padx=20, pady=15)

    ModernButton(btn_container, "📊 Мои бронирования", command=show_reader_rents, width=160).pack(side='left', padx=5)
    ModernButton(btn_container, "🚪 Выход", command=logout, width=120, color=COLORS['bg_light']).pack(side='left',
                                                                                                     padx=5)

    search_frame = tk.Frame(reader_frame, bg=COLORS['bg_dark'])
    search_frame.pack(fill='x', pady=15, padx=20)

    tk.Label(search_frame, text="🔍 Поиск:", bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(side='left', padx=5)
    search_entry = ttk.Entry(search_frame, width=25)
    search_entry.pack(side='left', padx=5)

    tk.Label(search_frame, text="Тип:", bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(side='left', padx=10)
    type_combo = ttk.Combobox(search_frame, values=get_book_types(), state='readonly', width=12)
    type_combo.set('Все типы')
    type_combo.pack(side='left', padx=5)

    def do_search():
        refresh_books(search_entry.get(), type_combo.get())

    ModernButton(search_frame, "Найти", command=do_search, width=80).pack(side='left', padx=10)

    cart_frame = tk.Frame(reader_frame, bg=COLORS['bg_medium'], relief='raised', bd=1)
    cart_frame.pack(fill='x', pady=5, padx=20)

    cart_label = tk.Label(cart_frame, text="🛒 Корзина: 0 книг", font=('Arial', 11, 'bold'),
                          bg=COLORS['bg_medium'], fg=COLORS['text_primary'])
    cart_label.pack(side='left', padx=15, pady=8)

    def reserve_from_cart():
        if not cart:
            messagebox.showinfo("Корзина", "Корзина пуста")
            return

        book_ids = [book[0] for book in cart]
        if reserve_books(current_user['id'], book_ids):
            cart.clear()
            cart_label.config(text="🛒 Корзина: 0 книг")
            refresh_books()
            messagebox.showinfo("Успех", f"✅ Забронировано {len(book_ids)} книг!")
        else:
            messagebox.showerror("Ошибка", "Ошибка бронирования")

    ModernButton(cart_frame, "📦 Забронировать все", command=reserve_from_cart, width=160).pack(side='right', padx=15,
                                                                                               pady=5)

    cards_container = tk.Frame(reader_frame, bg=COLORS['bg_dark'])
    cards_container.pack(fill='both', expand=True, padx=20, pady=10)

    canvas = tk.Canvas(cards_container, bg=COLORS['bg_dark'], highlightthickness=0)
    scrollbar = ttk.Scrollbar(cards_container, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_dark'])

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def add_to_cart(book_data):
        if int(book_data[8]) > 0:
            cart.append(book_data)
            cart_label.config(text=f"🛒 Корзина: {len(cart)} книг")
            messagebox.showinfo("Успех", f"✅ Книга добавлена в корзину")
        else:
            messagebox.showerror("Ошибка", "❌ Книга недоступна")

    def refresh_books(search='', book_type=''):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        books = get_books(search, '', book_type)

        if not books:
            no_books_label = tk.Label(scrollable_frame, text="📚 Книги не найдены", font=('Arial', 14),
                                      bg=COLORS['bg_dark'], fg=COLORS['text_secondary'])
            no_books_label.pack(pady=50)
            return

        row_frame = None
        for i, book in enumerate(books):
            if i % 3 == 0:
                row_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_dark'])
                row_frame.pack(fill='x', pady=5)

            card = BookCard(row_frame, book, add_to_cart)
            card.pack(side='left', padx=10, pady=5, fill='y')

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    refresh_books()


def show_reader_rents():
    rents_win = tk.Toplevel(root)
    rents_win.title("Мои бронирования")
    rents_win.geometry("900x550")
    rents_win.configure(bg=COLORS['bg_dark'])

    tk.Label(rents_win, text="📊 Мои бронирования", font=('Arial', 16, 'bold'),
             bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=20)

    table_frame = tk.Frame(rents_win, bg=COLORS['bg_dark'])
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    rents_tree = ttk.Treeview(table_frame,
                              columns=(
                              'id', 'title', 'type', 'rent_date', 'return_date', 'remaining_days', 'status', 'cost'),
                              show='headings', height=15)

    columns = [
        ('id', 'ID', 50),
        ('title', 'Книга', 250),
        ('type', 'Тип', 80),
        ('rent_date', 'Дата брони', 100),
        ('return_date', 'Вернуть до', 100),
        ('remaining_days', 'Осталось дней', 100),
        ('status', 'Статус', 120),
        ('cost', 'Стоимость', 100)
    ]

    for col, heading, width in columns:
        rents_tree.heading(col, text=heading)
        rents_tree.column(col, width=width, anchor='center')

    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=rents_tree.yview)
    rents_tree.configure(yscrollcommand=scrollbar.set)

    rents_tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    def refresh_rents():
        for item in rents_tree.get_children():
            rents_tree.delete(item)
        rents = get_user_rents(current_user['id'])
        for rent in rents:
            rent_id, title, author, book_type, rent_date, exp_return, act_return, status, cost = rent

            status_text = {
                'reserved': '🔄 Забронирована',
                'active': '✅ Активна',
                'waiting_return': '📦 Ожидает возврата',
                'returned': '📚 Возвращена',
                'overdue': '⚠️ Просрочена',
                'auto_returned': '🤖 Авто-возврат'
            }.get(status, status)

            remaining_days = ""
            if status in ['active', 'reserved'] and book_type == 'digital':
                remaining_days = get_remaining_days(rent_date, exp_return)
                remaining_days = f"{remaining_days} дн."

            rents_tree.insert('', 'end', values=(
                rent_id, title, book_type, rent_date, exp_return, remaining_days, status_text, f"{cost} руб"
            ))

    refresh_rents()

    button_frame = tk.Frame(rents_win, bg=COLORS['bg_dark'])
    button_frame.pack(pady=20)

    ModernButton(button_frame, "🔄 Обновить", command=refresh_rents, width=140).pack(side='left', padx=10)
    ModernButton(button_frame, "✖️ Закрыть", command=rents_win.destroy, width=140, color=COLORS['bg_light']).pack(
        side='left', padx=10)


def show_librarian_interface():
    show_frame(librarian_frame)

    for widget in librarian_frame.winfo_children():
        widget.destroy()

    header = tk.Frame(librarian_frame, bg=COLORS['bg_medium'], height=60)
    header.pack(fill='x', pady=5)
    header.pack_propagate(False)

    tk.Label(header, text=f"📋 Библиотекарь: {current_user['username']}", font=('Arial', 14, 'bold'),
             bg=COLORS['bg_medium'], fg=COLORS['text_primary']).pack(side='left', padx=20, pady=20)

    ModernButton(header, "🚪 Выход", command=logout, width=120, height=35,
                 color=COLORS['bg_light']).pack(side='right', padx=20, pady=15)

    notebook = ttk.Notebook(librarian_frame)
    notebook.pack(fill='both', expand=True, pady=10)

    actions_tab = tk.Frame(notebook, bg=COLORS['bg_dark'])
    notebook.add(actions_tab, text='📦 Действия')

    rents_tab = tk.Frame(notebook, bg=COLORS['bg_dark'])
    notebook.add(rents_tab, text='📚 Все аренды')

    pending_pickups, pending_returns = get_pending_actions()

    actions_frame = tk.Frame(actions_tab, bg=COLORS['bg_dark'])
    actions_frame.pack(pady=20, padx=20, fill='both', expand=True)

    pickup_frame = tk.Frame(actions_frame, bg=COLORS['card_bg'], relief='raised', bd=2)
    pickup_frame.pack(fill='x', pady=10, padx=20)

    tk.Label(pickup_frame, text=f"📦 Ожидают выдачи: {pending_pickups}", font=('Arial', 12, 'bold'),
             bg=COLORS['card_bg'], fg=COLORS['text_primary']).pack(pady=15)

    def show_pending_pickups():
        pickups_win = tk.Toplevel(root)
        pickups_win.title("Ожидают выдачи")
        pickups_win.geometry("800x450")
        pickups_win.configure(bg=COLORS['bg_dark'])

        tk.Label(pickups_win, text="📦 Книги ожидающие выдачи", font=('Arial', 14, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=20)

        table_frame = tk.Frame(pickups_win, bg=COLORS['bg_dark'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tree = ttk.Treeview(table_frame, columns=('id', 'user', 'title', 'rent_date'), show='headings', height=12)

        for col, heading, width in [('id', 'ID', 50), ('user', 'Читатель', 120), ('title', 'Книга', 300),
                                    ('rent_date', 'Дата', 100)]:
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor='center')

        def refresh_pickups():
            for item in tree.get_children():
                tree.delete(item)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, u.username, b.title, r.rent_date 
                FROM rents r 
                JOIN users u ON r.user_id = u.id 
                JOIN books b ON r.book_id = b.id 
                JOIN rent_statuses rs ON r.status_id = rs.id
                WHERE rs.status_name='reserved' 
                AND b.book_type_id IN (SELECT id FROM book_types WHERE type_name='physical')
            ''')
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)
            conn.close()

        def confirm_selected_pickup():
            selected = tree.selection()
            if selected:
                rent_id = tree.item(selected[0])['values'][0]
                if confirm_pickup(rent_id, current_user['id']):
                    messagebox.showinfo("Успех", "✅ Выдача подтверждена!")
                    refresh_pickups()
                    show_librarian_interface()
                else:
                    messagebox.showerror("Ошибка", "❌ Ошибка подтверждения")

        refresh_pickups()

        tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        btn_frame = tk.Frame(pickups_win, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=20)

        ModernButton(btn_frame, "✅ Подтвердить выдачу", command=confirm_selected_pickup, width=160).pack(side='left',
                                                                                                         padx=10)
        ModernButton(btn_frame, "🔄 Обновить", command=refresh_pickups, width=140).pack(side='left', padx=10)

    ModernButton(pickup_frame, "📋 Просмотреть список", command=show_pending_pickups, width=180).pack(pady=10)

    return_frame = tk.Frame(actions_frame, bg=COLORS['card_bg'], relief='raised', bd=2)
    return_frame.pack(fill='x', pady=10, padx=20)

    tk.Label(return_frame, text=f"📚 Ожидают возврата: {pending_returns}", font=('Arial', 12, 'bold'),
             bg=COLORS['card_bg'], fg=COLORS['text_primary']).pack(pady=15)

    def show_pending_returns():
        returns_win = tk.Toplevel(root)
        returns_win.title("Ожидают возврата")
        returns_win.geometry("900x500")
        returns_win.configure(bg=COLORS['bg_dark'])

        tk.Label(returns_win, text="📚 Книги ожидающие возврата", font=('Arial', 14, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=20)

        table_frame = tk.Frame(returns_win, bg=COLORS['bg_dark'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tree = ttk.Treeview(table_frame,
                            columns=('id', 'user', 'title', 'type', 'rent_date', 'expected_return', 'remaining_days'),
                            show='headings', height=12)

        columns = [
            ('id', 'ID', 50),
            ('user', 'Читатель', 120),
            ('title', 'Книга', 250),
            ('type', 'Тип', 80),
            ('rent_date', 'Дата аренды', 100),
            ('expected_return', 'Вернуть до', 100),
            ('remaining_days', 'Осталось дней', 100)
        ]

        for col, heading, width in columns:
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor='center')

        def refresh_returns():
            for item in tree.get_children():
                tree.delete(item)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, u.username, b.title, bt.type_name, r.rent_date, r.expected_return_date
                FROM rents r 
                JOIN users u ON r.user_id = u.id 
                JOIN books b ON r.book_id = b.id 
                JOIN book_types bt ON b.book_type_id = bt.id
                JOIN rent_statuses rs ON r.status_id = rs.id
                WHERE rs.status_name IN ('active', 'reserved')
            ''')
            for row in cursor.fetchall():
                rent_id, username, title, book_type, rent_date, exp_return = row
                remaining_days = ""
                if book_type == 'digital':
                    remaining_days = get_remaining_days(rent_date, exp_return)
                    remaining_days = f"{remaining_days} дн."

                tree.insert('', 'end', values=(
                    rent_id, username, title, book_type, rent_date, exp_return, remaining_days
                ))
            conn.close()

        def confirm_selected_return():
            selected = tree.selection()
            if selected:
                rent_id = tree.item(selected[0])['values'][0]
                book_type = tree.item(selected[0])['values'][3]

                if book_type == 'physical':
                    if confirm_return(rent_id, current_user['id']):
                        messagebox.showinfo("Успех", "✅ Возврат подтвержден!")
                        refresh_returns()
                        show_librarian_interface()
                    else:
                        messagebox.showerror("Ошибка", "❌ Ошибка подтверждения")
                else:
                    messagebox.showinfo("Информация", "📖 Цифровые книги возвращаются автоматически по истечении срока")

        refresh_returns()

        tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        btn_frame = tk.Frame(returns_win, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=20)

        ModernButton(btn_frame, "✅ Подтвердить возврат", command=confirm_selected_return, width=160).pack(side='left',
                                                                                                          padx=10)
        ModernButton(btn_frame, "🔄 Обновить", command=refresh_returns, width=140).pack(side='left', padx=10)

    ModernButton(return_frame, "📋 Просмотреть список", command=show_pending_returns, width=180).pack(pady=10)

    def refresh_all_rents():
        for item in rents_tree.get_children():
            rents_tree.delete(item)
        rents = get_all_rents()
        for rent in rents:
            rent_id, username, title, book_type, rent_date, exp_return, act_return, status, cost = rent

            status_text = {
                'reserved': '🔄 Забронирована',
                'active': '✅ Активна',
                'waiting_return': '📦 Ожидает возврата',
                'returned': '📚 Возвращена',
                'overdue': '⚠️ Просрочена',
                'auto_returned': '🤖 Авто-возврат'
            }.get(status, status)

            remaining_days = ""
            if status in ['active', 'reserved'] and book_type == 'digital':
                remaining_days = get_remaining_days(rent_date, exp_return)
                remaining_days = f"{remaining_days} дн."

            rents_tree.insert('', 'end', values=(
                rent_id, username, title, book_type, rent_date, exp_return,
                act_return if act_return else "-", remaining_days, status_text, f"{cost} руб"
            ))

    rents_container = tk.Frame(rents_tab, bg=COLORS['bg_dark'])
    rents_container.pack(fill='both', expand=True, padx=20, pady=10)

    rents_tree = ttk.Treeview(rents_container,
                              columns=(
                                  'id', 'user', 'title', 'type', 'rent_date', 'exp_return', 'act_return',
                                  'remaining_days', 'status',
                                  'cost'),
                              show='headings', height=15)

    rent_columns = [
        ('id', 'ID', 50),
        ('user', 'Читатель', 100),
        ('title', 'Книга', 200),
        ('type', 'Тип', 80),
        ('rent_date', 'Дата аренды', 100),
        ('exp_return', 'Вернуть до', 100),
        ('act_return', 'Факт. возврат', 100),
        ('remaining_days', 'Осталось дней', 100),
        ('status', 'Статус', 120),
        ('cost', 'Стоимость', 100)
    ]

    for col, heading, width in rent_columns:
        rents_tree.heading(col, text=heading)
        rents_tree.column(col, width=width, anchor='center')

    scrollbar = ttk.Scrollbar(rents_container, orient='vertical', command=rents_tree.yview)
    rents_tree.configure(yscrollcommand=scrollbar.set)

    rents_tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    refresh_btn_frame = tk.Frame(rents_tab, bg=COLORS['bg_dark'])
    refresh_btn_frame.pack(pady=15)

    ModernButton(refresh_btn_frame, "🔄 Обновить список", command=refresh_all_rents, width=160).pack()

    refresh_all_rents()


def show_admin_interface():
    show_frame(admin_frame)

    for widget in admin_frame.winfo_children():
        widget.destroy()

    header = tk.Frame(admin_frame, bg=COLORS['bg_medium'], height=60)
    header.pack(fill='x', pady=5)
    header.pack_propagate(False)

    tk.Label(header, text=f"👑 Администратор: {current_user['username']}", font=('Arial', 14, 'bold'),
             bg=COLORS['bg_medium'], fg=COLORS['text_primary']).pack(side='left', padx=20, pady=20)

    ModernButton(header, "🚪 Выход", command=logout, width=120, height=35,
                 color=COLORS['bg_light']).pack(side='right', padx=20, pady=15)

    notebook = ttk.Notebook(admin_frame)
    notebook.pack(fill='both', expand=True, pady=10)

    books_tab = tk.Frame(notebook, bg=COLORS['bg_dark'])
    notebook.add(books_tab, text='📚 Книги')

    stats_tab = tk.Frame(notebook, bg=COLORS['bg_dark'])
    notebook.add(stats_tab, text='📊 Статистика')

    users_tab = tk.Frame(notebook, bg=COLORS['bg_dark'])
    notebook.add(users_tab, text='👥 Пользователи')

    # Вкладка книг
    search_frame = tk.Frame(books_tab, bg=COLORS['bg_dark'])
    search_frame.pack(fill='x', pady=15, padx=20)

    tk.Label(search_frame, text="🔍 Поиск:", bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(side='left', padx=5)
    search_entry = ttk.Entry(search_frame, width=25)
    search_entry.pack(side='left', padx=5)

    def admin_search():
        refresh_admin_books(search_entry.get())

    ModernButton(search_frame, "Найти", command=admin_search, width=80).pack(side='left', padx=10)

    table_container = tk.Frame(books_tab, bg=COLORS['bg_dark'])
    table_container.pack(fill='both', expand=True, padx=20, pady=10)

    books_tree = ttk.Treeview(table_container,
                              columns=(
                                  'id', 'title', 'author', 'type', 'isbn', 'genre', 'price', 'quantity', 'available'),
                              show='headings', height=12)

    admin_columns = [
        ('id', 'ID', 50),
        ('title', 'Название', 200),
        ('author', 'Автор', 150),
        ('type', 'Тип', 80),
        ('isbn', 'ISBN', 120),
        ('genre', 'Жанр', 100),
        ('price', 'Цена', 80),
        ('quantity', 'Всего', 70),
        ('available', 'Доступно', 80)
    ]

    for col, heading, width in admin_columns:
        books_tree.heading(col, text=heading)
        books_tree.column(col, width=width, anchor='center')

    scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=books_tree.yview)
    books_tree.configure(yscrollcommand=scrollbar.set)

    books_tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Кнопки управления книгами
    book_buttons_frame = tk.Frame(books_tab, bg=COLORS['bg_dark'])
    book_buttons_frame.pack(pady=15)

    def edit_selected_book():
        selected = books_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для редактирования")
            return

        book_id = books_tree.item(selected[0])['values'][0]
        show_edit_book_dialog(book_id)

    def delete_selected_book():
        selected = books_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления")
            return

        book_id = books_tree.item(selected[0])['values'][0]
        book_title = books_tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Подтверждение", f"Удалить книгу '{book_title}'?"):
            if delete_book(book_id):
                messagebox.showinfo("Успех", "Книга удалена!")
                refresh_admin_books()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить книгу")

    ModernButton(book_buttons_frame, "✏️ Редактировать", command=edit_selected_book, width=160).pack(side='left',
                                                                                                     padx=10)
    ModernButton(book_buttons_frame, "🗑️ Удалить", command=delete_selected_book, width=160,
                 color=COLORS['accent_red']).pack(side='left', padx=10)

    form_frame = tk.Frame(books_tab, bg=COLORS['bg_medium'], relief='raised', bd=1)
    form_frame.pack(fill='x', pady=15, padx=20)

    tk.Label(form_frame, text="📝 Добавить книгу:", font=('Arial', 12, 'bold'),
             bg=COLORS['bg_medium'], fg=COLORS['text_primary']).pack(anchor='w', padx=15, pady=10)

    form_content = tk.Frame(form_frame, bg=COLORS['bg_medium'])
    form_content.pack(fill='x', padx=15, pady=10)

    fields = [
        ('title', 'Название:', 0, 0),
        ('author', 'Автор:', 0, 2),
        ('type', 'Тип:', 1, 0),
        ('isbn', 'ISBN:', 1, 2),
        ('genre', 'Жанр:', 2, 0),
        ('price', 'Цена:', 2, 2),
        ('quantity', 'Количество:', 3, 0),
        ('description', 'Описание:', 3, 2)
    ]

    entries = {}
    for field, label, row, col in fields:
        tk.Label(form_content, text=label, bg=COLORS['bg_medium'], fg=COLORS['text_primary']).grid(row=row, column=col,
                                                                                                   sticky='w', pady=8,
                                                                                                   padx=5)

        if field == 'type':
            entry = ttk.Combobox(form_content, values=['physical', 'digital'], width=22, state='readonly')
            entry.set('physical')
        elif field == 'quantity':
            entry = ttk.Spinbox(form_content, from_=1, to=1000, width=22)
            entry.delete(0, 'end')
            entry.insert(0, '1')
        elif field == 'description':
            entry = tk.Text(form_content, width=25, height=3)
        else:
            entry = ttk.Entry(form_content, width=25)

        entry.grid(row=row, column=col + 1, pady=8, padx=5, sticky='ew')
        entries[field] = entry

    def add_new_book():
        title = entries['title'].get()
        author = entries['author'].get()
        book_type = entries['type'].get()
        isbn = entries['isbn'].get()
        genre = entries['genre'].get()
        price = entries['price'].get()
        quantity = entries['quantity'].get()
        description = entries['description'].get("1.0", "end-1c") if hasattr(entries['description'], 'get') else \
        entries['description'].get()

        if not title or not author or not price or not quantity:
            messagebox.showerror("Ошибка", "Заполните обязательные поля")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            if add_book(title, author, book_type, isbn, genre, price, quantity, description):
                refresh_admin_books()
                messagebox.showinfo("Успех", "Книга добавлена!")
                # Очистка полей
                for field, entry in entries.items():
                    if field == 'type':
                        entry.set('physical')
                    elif field == 'quantity':
                        entry.delete(0, 'end')
                        entry.insert(0, '1')
                    elif field == 'description':
                        entry.delete("1.0", "end")
                    else:
                        entry.delete(0, 'end')
            else:
                messagebox.showerror("Ошибка", "Ошибка добавления")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена и количество должны быть числами")

    button_frame = tk.Frame(books_tab, bg=COLORS['bg_dark'])
    button_frame.pack(pady=20)

    ModernButton(button_frame, "➕ Добавить книгу", command=add_new_book, width=160).pack()

    def show_edit_book_dialog(book_id):
        edit_win = tk.Toplevel(root)
        edit_win.title("Редактировать книгу")
        edit_win.geometry("600x600")  # Увеличил высоту
        edit_win.configure(bg=COLORS['bg_dark'])
        edit_win.resizable(False, False)

        # Центрирование окна
        edit_win.transient(root)
        edit_win.geometry("+%d+%d" % (root.winfo_rootx() + 200, root.winfo_rooty() + 50))

        # Основной контейнер с прокруткой
        main_container = tk.Frame(edit_win, bg=COLORS['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(main_container, text="✏️ Редактировать книгу", font=('Arial', 16, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_primary']).pack(pady=20)

        # Контейнер для формы с фиксированной высотой
        form_container = tk.Frame(main_container, bg=COLORS['bg_dark'])
        form_container.pack(fill='both', expand=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.id, b.title, b.author, bt.type_name, b.isbn, g.genre_name, 
                   b.price, b.quantity, b.description
            FROM books b
            LEFT JOIN genres g ON b.genre_id = g.id
            LEFT JOIN book_types bt ON b.book_type_id = bt.id
            WHERE b.id=?
        ''', (book_id,))
        book = cursor.fetchone()
        conn.close()

        if not book:
            messagebox.showerror("Ошибка", "Книга не найдена")
            edit_win.destroy()
            return

        form_frame = tk.Frame(form_container, bg=COLORS['bg_dark'])
        form_frame.pack(fill='both', expand=True, pady=10)

        edit_entries = {}

        fields = [
            ('title', 'Название:', book[1]),
            ('author', 'Автор:', book[2]),
            ('type', 'Тип:', book[3]),
            ('isbn', 'ISBN:', book[4]),
            ('genre', 'Жанр:', book[5]),
            ('price', 'Цена:', book[6]),
            ('quantity', 'Количество:', book[7]),
            ('description', 'Описание:', book[8] if len(book) > 8 else "")
        ]

        for i, (field, label, value) in enumerate(fields):
            row_frame = tk.Frame(form_frame, bg=COLORS['bg_dark'])
            row_frame.pack(fill='x', pady=8)

            tk.Label(row_frame, text=label, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                     font=('Arial', 10), width=12, anchor='w').pack(side='left', padx=(0, 10))

            if field == 'type':
                entry = ttk.Combobox(row_frame, values=['physical', 'digital'], width=40, state='readonly')
                entry.set(value if value else 'physical')
            elif field == 'quantity':
                entry = ttk.Spinbox(row_frame, from_=1, to=1000, width=40)
                entry.delete(0, 'end')
                entry.insert(0, str(value))
            elif field == 'description':
                # Для описания создаем отдельный фрейм с меткой и текстовым полем
                desc_frame = tk.Frame(form_frame, bg=COLORS['bg_dark'])
                desc_frame.pack(fill='x', pady=8)

                tk.Label(desc_frame, text=label, bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                         font=('Arial', 10), width=12, anchor='w').pack(side='left', padx=(0, 10), anchor='n')

                entry = tk.Text(desc_frame, width=40, height=6)
                entry.insert("1.0", value if value else "")
                entry.pack(side='left', fill='both', expand=True)
            else:
                entry = ttk.Entry(row_frame, width=40)
                entry.insert(0, str(value) if value else "")
                entry.pack(side='left', fill='x', expand=True)

            if field != 'description':
                entry.pack(side='left', fill='x', expand=True)

            edit_entries[field] = entry

        # Фрейм для кнопок внизу окна
        button_frame = tk.Frame(main_container, bg=COLORS['bg_dark'])
        button_frame.pack(pady=20)

        def save_changes():
            title = edit_entries['title'].get()
            author = edit_entries['author'].get()
            book_type = edit_entries['type'].get()
            isbn = edit_entries['isbn'].get()
            genre = edit_entries['genre'].get()
            price = edit_entries['price'].get()
            quantity = edit_entries['quantity'].get()
            description = edit_entries['description'].get("1.0", "end-1c") if hasattr(edit_entries['description'],
                                                                                      'get') else edit_entries[
                'description'].get()

            if not title or not author or not price or not quantity:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            try:
                price = float(price)
                quantity = int(quantity)
                if update_book(book_id, title, author, book_type, isbn, genre, price, quantity, description):
                    refresh_admin_books()
                    messagebox.showinfo("Успех", "Книга обновлена!")
                    edit_win.destroy()
                else:
                    messagebox.showerror("Ошибка", "Ошибка обновления")
            except ValueError:
                messagebox.showerror("Ошибка", "Цена и количество должны быть числами")

        # Кнопки с достаточным отступом
        ModernButton(button_frame, "💾 Сохранить изменения", command=save_changes,
                     width=180, height=40).pack(side='left', padx=10)
        ModernButton(button_frame, "✖️ Отмена", command=edit_win.destroy,
                     width=120, height=40, color=COLORS['bg_light']).pack(side='left', padx=10)

    def refresh_admin_books(search=''):
        for item in books_tree.get_children():
            books_tree.delete(item)
        books = get_books(search)
        for book in books:
            books_tree.insert('', 'end', values=book)

    refresh_admin_books()

    # Вкладка статистики
    stats_label = tk.Label(stats_tab, text="", font=('Arial', 11), justify='left',
                           bg=COLORS['bg_dark'], fg=COLORS['text_primary'])
    stats_label.pack(pady=20, padx=20)

    def refresh_stats():
        returned_count = auto_return_expired_digital_books()
        stats = get_library_stats()

        stats_text = f"""
📈 СТАТИСТИКА БИБЛИОТЕКИ

👥 Читатели: {stats['users']} активных
📚 Названий книг: {stats['books']}
📖 Всего экземпляров: {stats['total_books']}
📗 Доступно книг: {stats['available_books']}
📕 Активных аренд: {stats['active_rents']}
  ├─ Цифровые: {stats['digital_rents']}
  └─ Физические: {stats['physical_rents']}
⚠️ Просроченные аренды: {stats['overdue_rents']}
💰 Доход за месяц: {stats['monthly_revenue']:.2f} руб
🏦 Общий доход: {stats['total_revenue']:.2f} руб

🤖 Автоматически возвращено цифровых книг: {returned_count}
        """
        stats_label.config(text=stats_text)

    stats_button_frame = tk.Frame(stats_tab, bg=COLORS['bg_dark'])
    stats_button_frame.pack(pady=15)

    ModernButton(stats_button_frame, "🔄 Обновить статистику", command=refresh_stats, width=180).pack()
    refresh_stats()

    # Вкладка пользователей
    users_container = tk.Frame(users_tab, bg=COLORS['bg_dark'])
    users_container.pack(fill='both', expand=True, padx=20, pady=10)

    users_tree = ttk.Treeview(users_container,
                              columns=('id', 'username', 'email', 'role', 'reg_date', 'status'),
                              show='headings', height=12)

    users_columns = [
        ('id', 'ID', 50),
        ('username', 'Логин', 120),
        ('email', 'Email', 150),
        ('role', 'Роль', 100),
        ('reg_date', 'Регистрация', 100),
        ('status', 'Статус', 100)
    ]

    for col, heading, width in users_columns:
        users_tree.heading(col, text=heading)
        users_tree.column(col, width=width, anchor='center')

    scrollbar = ttk.Scrollbar(users_container, orient='vertical', command=users_tree.yview)
    users_tree.configure(yscrollcommand=scrollbar.set)

    users_tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    def refresh_users():
        for item in users_tree.get_children():
            users_tree.delete(item)
        users = get_all_users()
        for user in users:
            users_tree.insert('', 'end', values=user)

    def promote_selected_user():
        selected = users_tree.selection()
        if selected:
            user_id = users_tree.item(selected[0])['values'][0]
            username = users_tree.item(selected[0])['values'][1]

            if messagebox.askyesno("Подтверждение", f"Назначить пользователя '{username}' библиотекарем?"):
                if promote_to_librarian(user_id):
                    messagebox.showinfo("Успех", f"✅ Пользователь '{username}' теперь библиотекарь!")
                    refresh_users()
                else:
                    messagebox.showerror("Ошибка", "❌ Ошибка назначения")

    users_button_frame = tk.Frame(users_tab, bg=COLORS['bg_dark'])
    users_button_frame.pack(pady=15)

    ModernButton(users_button_frame, "📋 Назначить библиотекарем", command=promote_selected_user, width=200).pack(
        side='left', padx=10)
    ModernButton(users_button_frame, "🔄 Обновить список", command=refresh_users, width=160).pack(side='left', padx=10)

    refresh_users()


def logout():
    global current_user, cart
    current_user = None
    cart = []
    create_login_screen()


create_login_screen()
root.mainloop()