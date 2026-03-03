# ============================================
# АВТОСЕРВИС - ПОЛНАЯ СИСТЕМА УЧЁТА ЗАЯВОК
# Модуль 1 + Модуль 2 (ИСПРАВЛЕННАЯ ВЕРСИЯ)
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import sqlite3
import os

# ============================================
# МОДЕЛИ ДАННЫХ
# ============================================

@dataclass
class User:
    """Модель пользователя"""
    UserID: Optional[int]  # Изменено с user_id на UserID для соответствия БД
    FIO: str
    Phone: str
    Login: str
    Password: str
    Role: str
    CreatedAt: Optional[str] = None
    UpdatedAt: Optional[str] = None

@dataclass
class Request:
    """Модель заявки"""
    RequestID: Optional[int]  # Изменено с request_id на RequestID
    StartDate: str
    CarType: str
    CarModel: str
    ProblemDescription: str
    RequestStatus: str
    CompletionDate: Optional[str] = None
    RepairParts: Optional[str] = None
    MasterID: Optional[int] = None
    ClientID: Optional[int] = None
    CreatedAt: Optional[str] = None
    UpdatedAt: Optional[str] = None
    
    @property
    def days_in_work(self) -> Optional[int]:
        if self.CompletionDate:
            start = datetime.strptime(self.StartDate, '%Y-%m-%d')
            end = datetime.strptime(self.CompletionDate, '%Y-%m-%d')
            return (end - start).days
        return None

@dataclass
class Comment:
    """Модель комментария"""
    CommentID: Optional[int]  # Изменено с comment_id на CommentID
    Message: str
    MasterID: int
    RequestID: int
    CreatedAt: Optional[str] = None

# ============================================
# РАБОТА С БАЗОЙ ДАННЫХ
# ============================================

class Database:
    """Класс для работы с SQLite"""
    
    def __init__(self, db_file="autoservice.db"):
        self.db_file = db_file
        self.init_database()
    
    def get_connection(self):
        """Получение соединения с БД"""
        return sqlite3.connect(self.db_file)
    
    def init_database(self):
        """Инициализация базы данных"""
        need_data = not os.path.exists(self.db_file) or os.path.getsize(self.db_file) == 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создание таблиц
            cursor.executescript("""
                -- Таблица пользователей
                CREATE TABLE IF NOT EXISTS Users (
                    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                    FIO TEXT NOT NULL,
                    Phone TEXT NOT NULL,
                    Login TEXT NOT NULL UNIQUE,
                    Password TEXT NOT NULL,
                    Role TEXT NOT NULL CHECK(Role IN ('Менеджер', 'Автомеханик', 'Оператор', 'Заказчик')),
                    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Таблица заявок
                CREATE TABLE IF NOT EXISTS Requests (
                    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
                    StartDate DATE NOT NULL,
                    CarType TEXT NOT NULL,
                    CarModel TEXT NOT NULL,
                    ProblemDescription TEXT NOT NULL,
                    RequestStatus TEXT NOT NULL CHECK(RequestStatus IN ('Новая заявка', 'В процессе ремонта', 'Ожидание автозапчастей', 'Готова к выдаче')) DEFAULT 'Новая заявка',
                    CompletionDate DATE,
                    RepairParts TEXT,
                    MasterID INTEGER,
                    ClientID INTEGER NOT NULL,
                    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (MasterID) REFERENCES Users(UserID) ON DELETE SET NULL,
                    FOREIGN KEY (ClientID) REFERENCES Users(UserID) ON DELETE CASCADE
                );
                
                -- Таблица комментариев
                CREATE TABLE IF NOT EXISTS Comments (
                    CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Message TEXT NOT NULL,
                    MasterID INTEGER NOT NULL,
                    RequestID INTEGER NOT NULL,
                    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (MasterID) REFERENCES Users(UserID) ON DELETE CASCADE,
                    FOREIGN KEY (RequestID) REFERENCES Requests(RequestID) ON DELETE CASCADE
                );
            """)
            
            # Если БД только что создана, заполняем тестовыми данными
            if need_data:
                self.insert_test_data(conn)
                print("✅ База данных создана и заполнена тестовыми данными")
            else:
                print("✅ Подключено к существующей базе данных")
    
    def insert_test_data(self, conn):
        """Заполнение тестовыми данными"""
        cursor = conn.cursor()
        
        # Пользователи
        users_data = [
            (1, 'Белов Александр Давидович', '89210563128', 'login1', 'pass1', 'Менеджер'),
            (2, 'Харитонова Мария Павловна', '89535078985', 'login2', 'pass2', 'Автомеханик'),
            (3, 'Марков Давид Иванович', '89210673849', 'login3', 'pass3', 'Автомеханик'),
            (4, 'Громова Анна Семёновна', '89990563748', 'login4', 'pass4', 'Оператор'),
            (5, 'Карташова Мария Данииловна', '89994563847', 'login5', 'pass5', 'Оператор'),
            (6, 'Касаткин Егор Львович', '89219567849', 'login11', 'pass11', 'Заказчик'),
            (7, 'Ильина Тамара Даниловна', '89219567841', 'login12', 'pass12', 'Заказчик'),
            (8, 'Елисеева Юлиана Алексеевна', '89219567842', 'login13', 'pass13', 'Заказчик'),
            (9, 'Никифорова Алиса Тимофеевна', '89219567843', 'login14', 'pass14', 'Заказчик'),
            (10, 'Васильев Али Евгеньевич', '89219567844', 'login15', 'pass15', 'Автомеханик')
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO Users (UserID, FIO, Phone, Login, Password, Role) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, users_data)
        
        # Заявки
        requests_data = [
            (1, '2023-06-06', 'Легковая', 'Hyundai Avante', 'Отказали тормоза. Требуется замена колодок и диагностика.', 'В процессе ремонта', None, '', 2, 7),
            (2, '2023-05-05', 'Легковая', 'Nissan 180SX', 'Отказали тормоза. Педаль проваливается.', 'В процессе ремонта', None, '', 3, 8),
            (3, '2022-07-07', 'Легковая', 'Toyota 2000GT', 'В салоне пахнет бензином. Возможно утечка топлива.', 'Готова к выдаче', '2023-01-01', 'Топливный фильтр, прокладки', 3, 9),
            (4, '2023-08-02', 'Грузовая', 'Citroen Berlingo', 'Руль плохо крутится. Стук в рулевой.', 'Новая заявка', None, '', None, 8),
            (5, '2023-08-02', 'Грузовая', 'УАЗ 2360', 'Руль плохо крутится. Гул при повороте.', 'Новая заявка', None, '', None, 9),
            (6, '2023-08-03', 'Легковая', 'Kia Rio', 'Не заводится. Стартер крутит, но двигатель не схватывает.', 'Новая заявка', None, '', None, 6),
            (7, '2023-08-03', 'Легковая', 'Lada Vesta', 'Стук в подвеске спереди.', 'Ожидание автозапчастей', None, 'Амортизаторы, шаровые', 2, 7)
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO Requests (RequestID, StartDate, CarType, CarModel, ProblemDescription, 
                                            RequestStatus, CompletionDate, RepairParts, MasterID, ClientID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, requests_data)
        
        # Комментарии
        comments_data = [
            (1, 'Очень странно. Нужна полная диагностика тормозной системы.', 2, 1),
            (2, 'Будем разбираться! Записал клиента на завтра.', 3, 2),
            (3, 'Проблема оказалась в топливном насосе.', 3, 3),
            (4, 'Заказал запчасти. Ждём 3 дня.', 2, 7)
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO Comments (CommentID, Message, MasterID, RequestID) 
            VALUES (?, ?, ?, ?)
        """, comments_data)
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """Выполнение SQL-запроса"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch:
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                else:
                    conn.commit()
                    return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Ошибка SQLite: {e}")
            return None
    
    # ===== ПОЛЬЗОВАТЕЛИ =====
    
    def get_user_by_login(self, login: str, password: str) -> Optional[User]:
        """Получение пользователя по логину и паролю"""
        query = "SELECT * FROM Users WHERE Login = ? AND Password = ?"
        result = self.execute_query(query, (login, password), fetch=True)
        
        if result and len(result) > 0:
            return User(**result[0])
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        query = "SELECT * FROM Users WHERE UserID = ?"
        result = self.execute_query(query, (user_id,), fetch=True)
        
        if result and len(result) > 0:
            return User(**result[0])
        return None
    
    def get_users_by_role(self, role: str) -> List[User]:
        """Получение пользователей по роли"""
        query = "SELECT * FROM Users WHERE Role = ? ORDER BY FIO"
        result = self.execute_query(query, (role,), fetch=True)
        
        users = []
        if result:
            for row in result:
                users.append(User(**row))
        return users
    
    def create_user(self, user: User) -> Optional[int]:
        """Создание нового пользователя"""
        query = """
            INSERT INTO Users (FIO, Phone, Login, Password, Role)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            user.FIO, user.Phone, user.Login, user.Password, user.Role
        ))
    
    # ===== ЗАЯВКИ =====
    
    def get_requests(self, user_id: Optional[int] = None, role: Optional[str] = None) -> List[Request]:
        """Получение списка заявок"""
        query = "SELECT * FROM Requests"
        params = []
        
        if role == 'Заказчик' and user_id:
            query += " WHERE ClientID = ?"
            params.append(user_id)
        elif role == 'Автомеханик' and user_id:
            query += " WHERE MasterID = ?"
            params.append(user_id)
        
        query += " ORDER BY StartDate DESC"
        
        result = self.execute_query(query, tuple(params), fetch=True)
        
        requests = []
        if result:
            for row in result:
                requests.append(Request(**row))
        return requests
    
    def get_request_by_id(self, request_id: int) -> Optional[Request]:
        """Получение заявки по ID"""
        query = "SELECT * FROM Requests WHERE RequestID = ?"
        result = self.execute_query(query, (request_id,), fetch=True)
        
        if result and len(result) > 0:
            return Request(**result[0])
        return None
    
    def create_request(self, request: Request) -> Optional[int]:
        """Создание новой заявки"""
        query = """
            INSERT INTO Requests (StartDate, CarType, CarModel, ProblemDescription, 
                                 RequestStatus, ClientID)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (
            request.StartDate,
            request.CarType,
            request.CarModel,
            request.ProblemDescription,
            request.RequestStatus,
            request.ClientID
        ))
    
    def update_request(self, request: Request) -> bool:
        """Обновление заявки"""
        query = """
            UPDATE Requests 
            SET CarType = ?, CarModel = ?, ProblemDescription = ?,
                RequestStatus = ?, CompletionDate = ?, RepairParts = ?,
                MasterID = ?
            WHERE RequestID = ?
        """
        result = self.execute_query(query, (
            request.CarType,
            request.CarModel,
            request.ProblemDescription,
            request.RequestStatus,
            request.CompletionDate,
            request.RepairParts,
            request.MasterID,
            request.RequestID
        ))
        
        return result is not None
    
    def assign_master(self, request_id: int, master_id: int) -> bool:
        """Назначение мастера"""
        query = """
            UPDATE Requests 
            SET MasterID = ?, RequestStatus = 'В процессе ремонта'
            WHERE RequestID = ?
        """
        result = self.execute_query(query, (master_id, request_id))
        return result is not None
    
    def update_status(self, request_id: int, status: str, completion_date: Optional[str] = None) -> bool:
        """Обновление статуса заявки"""
        if completion_date:
            query = "UPDATE Requests SET RequestStatus = ?, CompletionDate = ? WHERE RequestID = ?"
            result = self.execute_query(query, (status, completion_date, request_id))
        else:
            query = "UPDATE Requests SET RequestStatus = ? WHERE RequestID = ?"
            result = self.execute_query(query, (status, request_id))
        return result is not None
    
    # ===== КОММЕНТАРИИ =====
    
    def get_comments_by_request(self, request_id: int) -> List[Comment]:
        """Получение комментариев к заявке"""
        query = "SELECT * FROM Comments WHERE RequestID = ? ORDER BY CreatedAt"
        result = self.execute_query(query, (request_id,), fetch=True)
        
        comments = []
        if result:
            for row in result:
                comments.append(Comment(**row))
        return comments
    
    def add_comment(self, comment: Comment) -> Optional[int]:
        """Добавление комментария"""
        query = """
            INSERT INTO Comments (Message, MasterID, RequestID)
            VALUES (?, ?, ?)
        """
        return self.execute_query(query, (
            comment.Message,
            comment.MasterID,
            comment.RequestID
        ))
    
    # ===== СТАТИСТИКА =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        stats = {}
        
        queries = {
            'total_requests': "SELECT COUNT(*) as count FROM Requests",
            'new_requests': "SELECT COUNT(*) as count FROM Requests WHERE RequestStatus = 'Новая заявка'",
            'in_progress': "SELECT COUNT(*) as count FROM Requests WHERE RequestStatus = 'В процессе ремонта'",
            'waiting_parts': "SELECT COUNT(*) as count FROM Requests WHERE RequestStatus = 'Ожидание автозапчастей'",
            'completed': "SELECT COUNT(*) as count FROM Requests WHERE RequestStatus = 'Готова к выдаче'",
            'mechanics_count': "SELECT COUNT(*) as count FROM Users WHERE Role = 'Автомеханик'",
            'clients_count': "SELECT COUNT(*) as count FROM Users WHERE Role = 'Заказчик'"
        }
        
        for key, query in queries.items():
            result = self.execute_query(query, fetch=True)
            if result and len(result) > 0:
                stats[key] = result[0]['count']
        
        # Среднее время ремонта
        result = self.execute_query("""
            SELECT AVG(julianday(CompletionDate) - julianday(StartDate)) as avg_time 
            FROM Requests 
            WHERE CompletionDate IS NOT NULL
        """, fetch=True)
        
        if result and len(result) > 0:
            stats['avg_repair_time'] = result[0]['avg_time'] or 0
        
        # Статистика по проблемам
        result = self.execute_query("""
            SELECT 
                CASE 
                    WHEN ProblemDescription LIKE '%тормоз%' THEN 'Тормозная система'
                    WHEN ProblemDescription LIKE '%руль%' OR ProblemDescription LIKE '%управл%' THEN 'Рулевое управление'
                    WHEN ProblemDescription LIKE '%бензин%' OR ProblemDescription LIKE '%топлив%' THEN 'Топливная система'
                    WHEN ProblemDescription LIKE '%двигател%' OR ProblemDescription LIKE '%мотор%' THEN 'Двигатель'
                    WHEN ProblemDescription LIKE '%электро%' THEN 'Электрика'
                    WHEN ProblemDescription LIKE '%подвеск%' OR ProblemDescription LIKE '%амортизатор%' THEN 'Подвеска'
                    ELSE 'Прочее'
                END as category,
                COUNT(*) as count
            FROM Requests
            GROUP BY category
            ORDER BY count DESC
        """, fetch=True)
        
        stats['problem_stats'] = {}
        if result:
            for row in result:
                stats['problem_stats'][row['category']] = row['count']
        
        return stats

# ============================================
# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ============================================

class AutoServiceApp:
    """Главный класс приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏢 АВТОСЕРВИС - Учёт заявок на ремонт")
        self.root.geometry("1200x700")
        
        # Подключение к БД
        self.db = Database()
        self.current_user = None
        
        # Настройка стилей
        self.setup_styles()
        
        self.center_window()
        self.show_login()
        self.root.mainloop()
    
    def setup_styles(self):
        """Настройка стилей оформления"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цвета
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Arial', 14, 'bold'), foreground='#34495e')
        
        # Настройка Treeview
        style.configure("Treeview", 
                        background="#f9f9f9",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#f9f9f9")
        style.map('Treeview', background=[('selected', '#3498db')])
    
    def center_window(self):
        """Центрирование окна"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ========== ОКНО ВХОДА ==========
    
    def show_login(self):
        """Показ окна входа"""
        self.clear_window()
        
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(expand=True, fill='both')
        
        # Правая панель с формой входа
        right_frame = ttk.Frame(main_container, padding=50)
        right_frame.pack(expand=True)
        
        # Заголовок
        ttk.Label(right_frame, text="Добро пожаловать!", 
                 style='Title.TLabel').pack(pady=(0, 10))
        ttk.Label(right_frame, text="Войдите в систему учёта заявок",
                 font=('Arial', 12)).pack(pady=(0, 30))
        
        # Форма входа
        login_frame = ttk.Frame(right_frame)
        login_frame.pack(pady=20)
        
        # Логин
        ttk.Label(login_frame, text="Логин:", font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=10)
        self.login_entry = ttk.Entry(login_frame, width=30, font=('Arial', 11))
        self.login_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Пароль
        ttk.Label(login_frame, text="Пароль:", font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=10)
        self.pass_entry = ttk.Entry(login_frame, width=30, font=('Arial', 11), show='*')
        self.pass_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Кнопки
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🔑 Войти", command=self.login, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✖ Выход", command=self.root.destroy, width=15).pack(side='left', padx=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(right_frame, text="📋 Тестовые данные", padding=15)
        info_frame.pack(pady=20, fill='x')
        
        info_text = """
        👑 Менеджер:    login1 / pass1
        🔧 Автомеханик: login2 / pass2
        💻 Оператор:    login4 / pass4
        👤 Заказчик:    login11 / pass11
        """
        ttk.Label(info_frame, text=info_text, font=('Courier', 10), 
                 justify='left').pack()
        
        self.login_entry.focus()
    
    def login(self):
        """Обработка входа"""
        login = self.login_entry.get()
        password = self.pass_entry.get()
        
        if not login or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль")
            return
        
        user = self.db.get_user_by_login(login, password)
        
        if user:
            self.current_user = user
            self.show_main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    # ========== ГЛАВНОЕ МЕНЮ ==========
    
    def show_main_menu(self):
        """Показ главного меню"""
        self.clear_window()
        
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="15")
        top_frame.pack(fill='x')
        
        # Информация о пользователе
        user_info = f"👤 {self.current_user.FIO} | Роль: {self.current_user.Role}"
        ttk.Label(top_frame, text=user_info, font=('Arial', 14, 'bold')).pack(side='left')
        
        ttk.Button(top_frame, text="🚪 Выйти", command=self.logout).pack(side='right')
        
        # Разделитель
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=5)
        
        # Заголовок
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill='x')
        ttk.Label(title_frame, text="ГЛАВНОЕ МЕНЮ", 
                 style='Title.TLabel').pack()
        
        # Панель с кнопками
        menu_frame = ttk.Frame(self.root, padding="30")
        menu_frame.pack(expand=True)
        
        # Определяем кнопки в зависимости от роли
        buttons = []
        
        # Общие для всех
        buttons.append(("📋 МОИ ЗАЯВКИ", self.show_my_requests))
        
        # Для оператора и менеджера
        if self.current_user.Role in ('Оператор', 'Менеджер'):
            buttons.append(("📋 ВСЕ ЗАЯВКИ", self.show_all_requests))
        
        # Для оператора
        if self.current_user.Role == 'Оператор':
            buttons.append(("➕ НОВАЯ ЗАЯВКА", self.add_request))
        
        # Для менеджера
        if self.current_user.Role == 'Менеджер':
            buttons.append(("👨‍🔧 НАЗНАЧИТЬ МАСТЕРА", self.assign_master))
            buttons.append(("📊 СТАТИСТИКА", self.show_statistics))
        
        # Для автомеханика
        if self.current_user.Role == 'Автомеханик':
            buttons.append(("💬 МОИ КОММЕНТАРИИ", self.show_my_comments))
        
        # Создание кнопок в сетке 2x2
        for i, (text, cmd) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = tk.Button(menu_frame, text=text, command=cmd,
                          bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                          width=25, height=3, relief='raised', bd=3)
            btn.grid(row=row, column=col, padx=20, pady=20)
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.show_login()
    
    # ========== РАБОТА С ЗАЯВКАМИ ==========
    
    def show_my_requests(self):
        """Показать мои заявки"""
        requests = self.db.get_requests(self.current_user.UserID, self.current_user.Role)
        self.show_requests_list(requests, f"Мои заявки - {self.current_user.FIO}")
    
    def show_all_requests(self):
        """Показать все заявки"""
        requests = self.db.get_requests()
        self.show_requests_list(requests, "Все заявки")
    
    def show_requests_list(self, requests, title):
        """Отображение списка заявок"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("1200x600")
        window.transient(self.root)
        window.grab_set()
        
        # Верхняя панель с поиском
        top_panel = ttk.Frame(window, padding="10")
        top_panel.pack(fill='x')
        
        ttk.Label(top_panel, text="🔍 Поиск:").pack(side='left')
        search_var = tk.StringVar()
        search_entry = ttk.Entry(top_panel, textvariable=search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        # Таблица
        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Дата', 'Тип', 'Модель', 'Проблема', 'Статус', 'Мастер', 'Клиент')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        col_widths = [50, 90, 80, 130, 300, 150, 150, 150]
        for col, width in zip(columns, col_widths):
            tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, c, False))
            tree.column(col, width=width, anchor='w' if col == 'Проблема' else 'center')
        
        # Скроллбары
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        def update_table(filter_text=''):
            """Обновление таблицы"""
            tree.delete(*tree.get_children())
            for req in requests:
                master = self.db.get_user_by_id(req.MasterID) if req.MasterID else None
                client = self.db.get_user_by_id(req.ClientID)
                
                # Фильтрация
                if filter_text:
                    filter_lower = filter_text.lower()
                    if (filter_lower not in str(req.RequestID).lower() and
                        filter_lower not in req.CarModel.lower() and
                        filter_lower not in req.ProblemDescription.lower()):
                        continue
                
                # Цветовая индикация статуса
                status_colors = {
                    'Новая заявка': '#ffcccc',
                    'В процессе ремонта': '#ffffcc',
                    'Ожидание автозапчастей': '#ffcc99',
                    'Готова к выдаче': '#ccffcc'
                }
                
                values = (
                    req.RequestID,
                    req.StartDate,
                    req.CarType,
                    req.CarModel,
                    req.ProblemDescription[:100] + '...' if len(req.ProblemDescription) > 100 else req.ProblemDescription,
                    req.RequestStatus,
                    master.FIO if master else 'Не назначен',
                    client.FIO if client else ''
                )
                
                item = tree.insert('', 'end', values=values)
                
                # Применение цвета к статусу
                if req.RequestStatus in status_colors:
                    tree.tag_configure(req.RequestStatus, background=status_colors[req.RequestStatus])
                    tree.item(item, tags=(req.RequestStatus,))
        
        update_table()
        
        def on_search(*args):
            update_table(search_var.get().strip().lower())
        
        search_var.trace('w', on_search)
        
        # Нижняя панель с кнопками
        bottom_panel = ttk.Frame(window, padding="10")
        bottom_panel.pack(fill='x')
        
        def open_request():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Внимание", "Выберите заявку")
                return
            
            item = tree.item(selected[0])
            req_id = item['values'][0]
            request = next((r for r in requests if r.RequestID == req_id), None)
            if request:
                self.show_request_details(request, window)
        
        ttk.Button(bottom_panel, text="📋 Открыть заявку", 
                  command=open_request).pack(side='left', padx=5)
        ttk.Button(bottom_panel, text="✖ Закрыть", 
                  command=window.destroy).pack(side='right', padx=5)
        
        tree.bind('<Double-1>', lambda e: open_request())
    
    def sort_treeview(self, tree, col, reverse):
        """Сортировка Treeview"""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))
    
    def show_request_details(self, request: Request, parent):
        """Отображение деталей заявки"""
        window = tk.Toplevel(parent)
        window.title(f"Заявка №{request.RequestID}")
        window.geometry("900x700")
        window.transient(parent)
        window.grab_set()
        
        # Основная информация
        main_frame = ttk.LabelFrame(window, text="📋 Информация о заявке", padding=15)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        master = self.db.get_user_by_id(request.MasterID) if request.MasterID else None
        client = self.db.get_user_by_id(request.ClientID)
        
        data = [
            ("Номер заявки:", f"№{request.RequestID}"),
            ("Дата создания:", request.StartDate),
            ("Тип автомобиля:", request.CarType),
            ("Модель:", request.CarModel),
            ("Проблема:", request.ProblemDescription),
            ("Статус:", request.RequestStatus),
            ("Дата завершения:", request.CompletionDate if request.CompletionDate else "—"),
            ("Запчасти:", request.RepairParts if request.RepairParts else "—"),
            ("Мастер:", master.FIO if master else "Не назначен"),
            ("Клиент:", client.FIO if client else ""),
            ("Телефон клиента:", client.Phone if client else "")
        ]
        
        for i, (label, value) in enumerate(data):
            ttk.Label(main_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=3)
            
            # Для статуса делаем цветной
            if label == "Статус:":
                status_colors = {
                    'Новая заявка': 'red',
                    'В процессе ремонта': 'orange',
                    'Ожидание автозапчастей': 'brown',
                    'Готова к выдаче': 'green'
                }
                color = status_colors.get(request.RequestStatus, 'black')
                ttk.Label(main_frame, text=value, foreground=color, 
                         font=('Arial', 10, 'bold')).grid(row=i, column=1, sticky='w', pady=3, padx=10)
            else:
                ttk.Label(main_frame, text=value, wraplength=500).grid(
                    row=i, column=1, sticky='w', pady=3, padx=10)
        
        # Комментарии
        comments_frame = ttk.LabelFrame(window, text="💬 Комментарии", padding=15)
        comments_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Текст с комментариями
        comments_text = tk.Text(comments_frame, height=10, wrap='word', font=('Arial', 10))
        comments_text.pack(fill='both', expand=True)
        
        comments = self.db.get_comments_by_request(request.RequestID)
        for comment in comments:
            master_comment = self.db.get_user_by_id(comment.MasterID)
            master_name = master_comment.FIO if master_comment else "Неизвестно"
            comments_text.insert('end', f"[{comment.CreatedAt}] {master_name}:\n")
            comments_text.insert('end', f"{comment.Message}\n")
            comments_text.insert('end', "-" * 50 + "\n")
        
        comments_text.config(state='disabled')
        
        # Панель действий
        actions_frame = ttk.Frame(window, padding="10")
        actions_frame.pack(fill='x')
        
        # Для автомеханика
        if self.current_user.Role == 'Автомеханик' and request.MasterID == self.current_user.UserID:
            ttk.Button(actions_frame, text="💬 Добавить комментарий", 
                      command=lambda: self.add_comment(request, window)).pack(side='left', padx=5)
            ttk.Button(actions_frame, text="🔄 Изменить статус", 
                      command=lambda: self.change_status(request, window)).pack(side='left', padx=5)
        
        # Для менеджера
        if self.current_user.Role == 'Менеджер' and not request.MasterID:
            ttk.Button(actions_frame, text="👨‍🔧 Назначить мастера", 
                      command=lambda: self.assign_master_to_request(request, window)).pack(side='left', padx=5)
        
        ttk.Button(actions_frame, text="✖ Закрыть", command=window.destroy).pack(side='right', padx=5)
    
    def add_comment(self, request: Request, parent):
        """Добавление комментария"""
        window = tk.Toplevel(parent)
        window.title("Новый комментарий")
        window.geometry("500x300")
        window.transient(parent)
        window.grab_set()
        
        ttk.Label(window, text="Комментарий:", font=('Arial', 11, 'bold')).pack(pady=10)
        comment_text = tk.Text(window, height=8, width=50)
        comment_text.pack(pady=5, padx=20)
        
        def save():
            msg = comment_text.get('1.0', 'end-1c').strip()
            if not msg:
                messagebox.showwarning("Внимание", "Введите текст комментария")
                return
            
            comment = Comment(
                CommentID=None,
                Message=msg,
                MasterID=self.current_user.UserID,
                RequestID=request.RequestID
            )
            comment_id = self.db.add_comment(comment)
            if comment_id:
                messagebox.showinfo("Успех", "Комментарий добавлен")
                window.destroy()
                # Обновляем окно с деталями
                parent.destroy()
                self.show_request_details(request, parent.master)
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить комментарий")
        
        ttk.Button(window, text="Сохранить", command=save).pack(pady=10)
    
    def change_status(self, request: Request, parent):
        """Изменение статуса заявки"""
        window = tk.Toplevel(parent)
        window.title("Изменение статуса")
        window.geometry("400x200")
        window.transient(parent)
        window.grab_set()
        
        ttk.Label(window, text="Новый статус:", font=('Arial', 11)).pack(pady=10)
        
        status_var = tk.StringVar(value=request.RequestStatus)
        status_combo = ttk.Combobox(window, textvariable=status_var, width=30,
                                    values=['Новая заявка', 'В процессе ремонта', 
                                           'Ожидание автозапчастей', 'Готова к выдаче'])
        status_combo.pack(pady=5)
        
        def save():
            new_status = status_var.get()
            if new_status == request.RequestStatus:
                window.destroy()
                return
            
            completion_date = None
            if new_status == 'Готова к выдаче':
                completion_date = datetime.now().strftime('%Y-%m-%d')
            
            if self.db.update_status(request.RequestID, new_status, completion_date):
                messagebox.showinfo("Успех", "Статус обновлён")
                window.destroy()
                parent.destroy()
                self.show_request_details(request, parent.master)
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить статус")
        
        ttk.Button(window, text="Сохранить", command=save).pack(pady=10)
    
    def assign_master_to_request(self, request: Request, parent):
        """Назначение мастера на заявку"""
        window = tk.Toplevel(parent)
        window.title("Назначение мастера")
        window.geometry("500x250")
        window.transient(parent)
        window.grab_set()
        
        ttk.Label(window, text="Выберите мастера:", font=('Arial', 11)).pack(pady=10)
        
        mechanics = self.db.get_users_by_role('Автомеханик')
        mechanic_names = [f"{m.UserID} - {m.FIO} (тел. {m.Phone})" for m in mechanics]
        
        mechanic_var = tk.StringVar()
        mechanic_combo = ttk.Combobox(window, textvariable=mechanic_var, 
                                     values=mechanic_names, width=50)
        mechanic_combo.pack(pady=5)
        
        def assign():
            if not mechanic_var.get():
                messagebox.showwarning("Внимание", "Выберите мастера")
                return
            
            master_id = int(mechanic_var.get().split(' - ')[0])
            if self.db.assign_master(request.RequestID, master_id):
                messagebox.showinfo("Успех", "Мастер назначен")
                window.destroy()
                parent.destroy()
                self.show_request_details(request, parent.master)
            else:
                messagebox.showerror("Ошибка", "Не удалось назначить мастера")
        
        ttk.Button(window, text="Назначить", command=assign).pack(pady=10)
    
    # ========== ДОБАВЛЕНИЕ ЗАЯВКИ ==========
    
    def add_request(self):
        """Добавление новой заявки"""
        window = tk.Toplevel(self.root)
        window.title("Новая заявка")
        window.geometry("600x600")
        window.transient(self.root)
        window.grab_set()
        
        ttk.Label(window, text="➕ НОВАЯ ЗАЯВКА", style='Title.TLabel').pack(pady=10)
        
        # Форма
        frame = ttk.Frame(window, padding="20")
        frame.pack()
        
        fields = [
            ("Тип автомобиля:", 'car_type'),
            ("Модель:", 'car_model'),
            ("Описание проблемы:", 'problem'),
            ("ФИО клиента:", 'client_fio'),
            ("Телефон клиента:", 'client_phone')
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label, font=('Arial', 11)).grid(row=i, column=0, sticky='w', pady=10)
            entry = ttk.Entry(frame, width=40, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=10, padx=10)
            entries[key] = entry
        
        def save():
            # Проверка заполнения
            if not entries['car_type'].get() or not entries['car_model'].get() or not entries['problem'].get():
                messagebox.showwarning("Внимание", "Заполните обязательные поля")
                return
            
            # Поиск или создание клиента
            fio = entries['client_fio'].get().strip()
            phone = entries['client_phone'].get().strip()
            client_id = None
            
            if fio and phone:
                # Проверяем существующего клиента
                clients = self.db.get_users_by_role('Заказчик')
                for client in clients:
                    if client.FIO.lower() == fio.lower() and client.Phone == phone:
                        client_id = client.UserID
                        break
                
                # Создаём нового клиента
                if not client_id:
                    new_login = f"client{len(clients) + 11}"
                    new_pass = f"pass{len(clients) + 11}"
                    new_client = User(
                        UserID=None,
                        FIO=fio,
                        Phone=phone,
                        Login=new_login,
                        Password=new_pass,
                        Role='Заказчик'
                    )
                    client_id = self.db.create_user(new_client)
                    if client_id:
                        messagebox.showinfo("Информация", f"Создан новый клиент. Логин: {new_login}")
            else:
                # Если клиент не указан, используем первого попавшегося (для теста)
                clients = self.db.get_users_by_role('Заказчик')
                if clients:
                    client_id = clients[0].UserID
                else:
                    messagebox.showerror("Ошибка", "Нет доступных клиентов")
                    return
            
            # Создаём заявку
            new_request = Request(
                RequestID=None,
                StartDate=datetime.now().strftime('%Y-%m-%d'),
                CarType=entries['car_type'].get(),
                CarModel=entries['car_model'].get(),
                ProblemDescription=entries['problem'].get(),
                RequestStatus='Новая заявка',
                CompletionDate=None,
                RepairParts=None,
                MasterID=None,
                ClientID=client_id
            )
            
            request_id = self.db.create_request(new_request)
            if request_id:
                messagebox.showinfo("Успех", f"Заявка №{request_id} создана")
                window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заявку")
        
        ttk.Button(window, text="💾 Сохранить", command=save).pack(pady=20)
    
    # ========== НАЗНАЧЕНИЕ МАСТЕРА ==========
    
    def assign_master(self):
        """Назначение мастера на заявку (менеджер)"""
        # Получаем заявки без мастера
        all_requests = self.db.get_requests()
        unassigned = [r for r in all_requests if r.MasterID is None]
        
        if not unassigned:
            messagebox.showinfo("Информация", "Нет заявок без назначенного мастера")
            return
        
        window = tk.Toplevel(self.root)
        window.title("Назначение мастера")
        window.geometry("800x500")
        window.transient(self.root)
        window.grab_set()
        
        ttk.Label(window, text="👨‍🔧 НАЗНАЧЕНИЕ МАСТЕРА", style='Title.TLabel').pack(pady=10)
        
        # Список заявок
        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Дата', 'Модель', 'Проблема', 'Клиент')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column('ID', width=50)
        tree.column('Дата', width=90)
        tree.column('Модель', width=150)
        tree.column('Проблема', width=300)
        tree.column('Клиент', width=150)
        
        for req in unassigned:
            client = self.db.get_user_by_id(req.ClientID)
            tree.insert('', 'end', values=(
                req.RequestID,
                req.StartDate,
                req.CarModel,
                req.ProblemDescription[:50] + '...',
                client.FIO if client else ''
            ))
        
        tree.pack(side='left', fill='both', expand=True)
        
        # Панель назначения
        assign_frame = ttk.Frame(window, padding="10")
        assign_frame.pack(fill='x')
        
        ttk.Label(assign_frame, text="Выберите мастера:").pack(side='left')
        
        mechanics = self.db.get_users_by_role('Автомеханик')
        mechanic_names = [f"{m.UserID} - {m.FIO}" for m in mechanics]
        
        mechanic_var = tk.StringVar()
        mechanic_combo = ttk.Combobox(assign_frame, textvariable=mechanic_var, 
                                     values=mechanic_names, width=40)
        mechanic_combo.pack(side='left', padx=10)
        
        def do_assign():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Внимание", "Выберите заявку")
                return
            
            if not mechanic_var.get():
                messagebox.showwarning("Внимание", "Выберите мастера")
                return
            
            item = tree.item(selected[0])
            req_id = item['values'][0]
            master_id = int(mechanic_var.get().split(' - ')[0])
            
            if self.db.assign_master(req_id, master_id):
                messagebox.showinfo("Успех", f"Мастер назначен на заявку №{req_id}")
                window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось назначить мастера")
        
        ttk.Button(assign_frame, text="Назначить", command=do_assign).pack(side='left', padx=5)
    
    # ========== КОММЕНТАРИИ ==========
    
    def show_my_comments(self):
        """Показать комментарии текущего механика"""
        if self.current_user.Role != 'Автомеханик':
            return
        
        requests = self.db.get_requests(self.current_user.UserID, self.current_user.Role)
        
        window = tk.Toplevel(self.root)
        window.title("Мои комментарии")
        window.geometry("800x500")
        
        text = tk.Text(window, wrap='word', font=('Arial', 11))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        for req in requests:
            comments = self.db.get_comments_by_request(req.RequestID)
            if comments:
                text.insert('end', f"\n{'='*60}\n")
                text.insert('end', f"Заявка №{req.RequestID} - {req.CarModel}\n")
                text.insert('end', f"{'='*60}\n")
                
                for comment in comments:
                    if comment.MasterID == self.current_user.UserID:
                        text.insert('end', f"[{comment.CreatedAt}]\n")
                        text.insert('end', f"{comment.Message}\n")
                        text.insert('end', f"{'-'*40}\n")
        
        text.config(state='disabled')
        
        ttk.Button(window, text="Закрыть", command=window.destroy).pack(pady=5)
    
    # ========== СТАТИСТИКА ==========
    
    def show_statistics(self):
        """Показать статистику"""
        stats = self.db.get_statistics()
        
        window = tk.Toplevel(self.root)
        window.title("Статистика")
        window.geometry("600x600")
        window.transient(self.root)
        window.grab_set()
        
        # Заголовок
        ttk.Label(window, text="📊 СТАТИСТИКА РАБОТЫ", style='Title.TLabel').pack(pady=10)
        
        # Основная статистика
        main_frame = ttk.LabelFrame(window, text="Общая информация", padding=15)
        main_frame.pack(fill='x', padx=20, pady=5)
        
        stats_text = f"""
        Всего заявок:          {stats.get('total_requests', 0)}
        Новых заявок:          {stats.get('new_requests', 0)}
        В процессе ремонта:    {stats.get('in_progress', 0)}
        Ожидание запчастей:    {stats.get('waiting_parts', 0)}
        Завершено:             {stats.get('completed', 0)}
        
        Среднее время ремонта: {stats.get('avg_repair_time', 0):.1f} дней
        
        Механиков:             {stats.get('mechanics_count', 0)}
        Клиентов:              {stats.get('clients_count', 0)}
        """
        
        ttk.Label(main_frame, text=stats_text, font=('Courier', 11), 
                 justify='left').pack()
        
        # Статистика по проблемам
        problem_frame = ttk.LabelFrame(window, text="По типам проблем", padding=15)
        problem_frame.pack(fill='x', padx=20, pady=5)
        
        problem_text = ""
        for problem, count in stats.get('problem_stats', {}).items():
            problem_text += f"{problem}: {count}\n"
        
        if not problem_text:
            problem_text = "Нет данных"
        
        ttk.Label(problem_frame, text=problem_text, font=('Courier', 11),
                 justify='left').pack()
        
        # Кнопка закрытия
        ttk.Button(window, text="Закрыть", command=window.destroy).pack(pady=20)

# ============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================

if __name__ == "__main__":
    print("="*50)
    print("🏢 АВТОСЕРВИС - Система учёта заявок")
    print("="*50)
    print("\n📦 Используется SQLite (встроенная БД)")
    print("📁 Файл базы данных: autoservice.db")
    print("\n" + "="*50)
    
    app = AutoServiceApp()