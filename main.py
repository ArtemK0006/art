import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Optional

# ====================== АВТОСОЗДАНИЕ ФАЙЛОВ ПРИ ОТСУТСТВИИ ======================
def ensure_files_exist():
    """Создаёт файлы с тестовыми данными, если они отсутствуют."""
    files_content = {
        "inputDataUsers.csv": """userID;fio;phone;login;password;type
1;Белов Александр Давидович;89210563128;login1;pass1;Менеджер
2;Харитонова Мария Павловна;89535078985;login2;pass2;Автомеханик
3;Марков Давид Иванович;89210673849;login3;pass3;Автомеханик
4;Громова Анна Семёновна;89990563748;login4;pass4;Оператор
5;Карташова Мария Данииловна;89994563847;login5;pass5;Оператор
6;Касаткин Егор Львович;89219567849;login11;pass11;Заказчик
7;Ильина Тамара Даниловна;89219567841;login12;pass12;Заказчик
8;Елисеева Юлиана Алексеевна;89219567842;login13;pass13;Заказчик
9;Никифорова Алиса Тимофеевна;89219567843;login14;pass14;Заказчик
10;Васильев Али Евгеньевич;89219567844;login15;pass15;Автомеханик""",
        "inputDataRequests.csv": """requestID;startDate;carType;carModel;problemDescryption;requestStatus;completionDate;repairParts;masterID;clientID
1;2023-06-06;Легковая;Hyundai Avante (CN7);Отказали тормоза.;В процессе ремонта;null;;2;7
2;2023-05-05;Легковая;Nissan 180SX ;Отказали тормоза.;В процессе ремонта;null;;3;8
3;2022-07-07;Легковая;Toyota 2000GT ;В салоне пахнет бензином.;Готова к выдаче;2023-01-01;;3;9
4;2023-08-02;Грузовая;Citroen Berlingo (B9);Руль плохо крутится.;Новая заявка;null;;null;8
5;2023-08-02;Грузовая;УАЗ 2360 ;Руль плохо крутится.;Новая заявка;null;;null;9""",
        "inputDataComments.csv": """commentID;message;masterID;requestID
1;Очень странно.;2;1
2;Будем разбираться!;3;2
3;Будем разбираться!;3;3"""
    }

    for filename, content in files_content.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Создан файл: {filename}")

# Вызываем функцию перед загрузкой данных
ensure_files_exist()

# ====================== МОДЕЛИ ДАННЫХ ======================
class User:
    def __init__(self, uid: int, fio: str, phone: str, login: str, password: str, role: str):
        self.id = uid
        self.fio = fio
        self.phone = phone
        self.login = login
        self.password = password
        self.role = role

class Request:
    def __init__(self, rid: int, start_date: str, car_type: str, car_model: str,
                 problem: str, status: str, completion_date: Optional[str],
                 repair_parts: str, master_id: Optional[int], client_id: int):
        self.id = rid
        self.start_date = start_date
        self.car_type = car_type
        self.car_model = car_model
        self.problem = problem
        self.status = status
        self.completion_date = completion_date if completion_date != 'null' else None
        self.repair_parts = repair_parts
        self.master_id = master_id if master_id != 'null' else None
        self.client_id = client_id

class Comment:
    def __init__(self, cid: int, message: str, master_id: int, request_id: int):
        self.id = cid
        self.message = message
        self.master_id = master_id
        self.request_id = request_id

# ====================== ЗАГРУЗКА ДАННЫХ ======================
def load_users(filename: str) -> List[User]:
    users = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            users.append(User(
                uid=int(row['userID']),
                fio=row['fio'],
                phone=row['phone'],
                login=row['login'],
                password=row['password'],
                role=row['type']
            ))
    return users

def load_requests(filename: str) -> List[Request]:
    requests = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            requests.append(Request(
                rid=int(row['requestID']),
                start_date=row['startDate'],
                car_type=row['carType'],
                car_model=row['carModel'],
                problem=row['problemDescryption'],
                status=row['requestStatus'],
                completion_date=row['completionDate'],
                repair_parts=row.get('repairParts', ''),
                master_id=row['masterID'],
                client_id=int(row['clientID'])
            ))
    return requests

def load_comments(filename: str) -> List[Comment]:
    comments = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            comments.append(Comment(
                cid=int(row['commentID']),
                message=row['message'],
                master_id=int(row['masterID']),
                request_id=int(row['requestID'])
            ))
    return comments

# ====================== ОКНО ВХОДА ======================
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, users):
        super().__init__(parent)
        self.title("Вход в систему")
        self.geometry("300x150")
        self.users = users
        self.result = None

        ttk.Label(self, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_login = ttk.Entry(self)
        self.entry_login.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_pass = ttk.Entry(self, show="*")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Войти", command=self.check).grid(row=2, column=0, columnspan=2, pady=10)

    def check(self):
        login = self.entry_login.get()
        pwd = self.entry_pass.get()
        for u in self.users:
            if u.login == login and u.password == pwd:
                self.result = u
                self.destroy()
                return
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

# ====================== ОКНО СПИСКА ЗАЯВОК ======================
class RequestsListWindow(tk.Toplevel):
    def __init__(self, parent, requests, users, comments, role, current_user):
        super().__init__(parent)
        self.title("Список заявок")
        self.geometry("900x500")
        self.requests = requests
        self.users = users
        self.comments = comments
        self.role = role
        self.current_user = current_user

        # Фильтрация в зависимости от роли
        if role == "Заказчик":
            filtered = [r for r in requests if r.client_id == current_user.id]
        elif role == "Автомеханик":
            filtered = [r for r in requests if r.master_id == current_user.id]
        else:
            filtered = requests

        # Таблица
        columns = ("ID", "Дата", "Авто", "Модель", "Проблема", "Статус", "Мастер", "Клиент")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("Проблема", width=200)
        self.tree.column("Модель", width=150)

        for r in filtered:
            master_name = next((u.fio for u in users if u.id == r.master_id), "Не назначен")
            client_name = next((u.fio for u in users if u.id == r.client_id), "")
            self.tree.insert("", "end", values=(r.id, r.start_date, r.car_type, r.car_model,
                                                r.problem, r.status, master_name, client_name))

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопка назад
        ttk.Button(self, text="Назад", command=self.destroy).pack(pady=5)

        # Двойной клик для деталей
        self.tree.bind("<Double-1>", self.open_request_details)

    def open_request_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        req_id = int(self.tree.item(selected[0])['values'][0])
        req = next(r for r in self.requests if r.id == req_id)
        RequestDetailWindow(self, req, self.users, self.comments, self.role, self.current_user)

# ====================== ОКНО ДЕТАЛЕЙ ЗАЯВКИ ======================
class RequestDetailWindow(tk.Toplevel):
    def __init__(self, parent, request, users, comments, role, current_user):
        super().__init__(parent)
        self.request = request
        self.users = users
        self.comments = comments
        self.role = role
        self.current_user = current_user
        self.title(f"Заявка №{request.id}")
        self.geometry("700x600")

        # Основная информация
        main_frame = ttk.LabelFrame(self, text="Информация о заявке", padding=10)
        main_frame.pack(fill="x", padx=10, pady=5)

        data = [
            ("Номер:", request.id),
            ("Дата начала:", request.start_date),
            ("Тип авто:", request.car_type),
            ("Модель:", request.car_model),
            ("Проблема:", request.problem),
            ("Статус:", request.status),
            ("Дата завершения:", request.completion_date if request.completion_date else "—"),
            ("Запчасти:", request.repair_parts if request.repair_parts else "—"),
            ("Мастер:", next((u.fio for u in users if u.id == request.master_id), "Не назначен")),
            ("Клиент:", next((u.fio for u in users if u.id == request.client_id), ""))
        ]

        for i, (label, value) in enumerate(data):
            ttk.Label(main_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Label(main_frame, text=str(value)).grid(row=i, column=1, sticky="w", pady=2, padx=10)

        # Комментарии
        comments_frame = ttk.LabelFrame(self, text="Комментарии механиков", padding=10)
        comments_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.comments_listbox = tk.Listbox(comments_frame, height=8)
        self.comments_listbox.pack(fill="both", expand=True)

        self.refresh_comments()

        # Кнопки действий в зависимости от роли
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)

        if role == "Автомеханик" and request.master_id == current_user.id:
            ttk.Button(btn_frame, text="Добавить комментарий", command=self.add_comment).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Изменить статус", command=self.change_status).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Закрыть", command=self.destroy).pack(side="right", padx=5)

    def refresh_comments(self):
        self.comments_listbox.delete(0, tk.END)
        request_comments = [c for c in self.comments if c.request_id == self.request.id]
        for c in request_comments:
            master_name = next((u.fio for u in self.users if u.id == c.master_id), "")
            self.comments_listbox.insert(tk.END, f"{master_name}: {c.message}")

    def add_comment(self):
        dialog = tk.Toplevel(self)
        dialog.title("Новый комментарий")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Комментарий:").pack(pady=5)
        text = tk.Text(dialog, height=5, width=50)
        text.pack(pady=5)

        def save():
            msg = text.get("1.0", "end-1c").strip()
            if not msg:
                messagebox.showwarning("Внимание", "Комментарий не может быть пустым")
                return
            new_id = max((c.id for c in self.comments), default=0) + 1
            comment = Comment(new_id, msg, self.current_user.id, self.request.id)
            self.comments.append(comment)
            self.refresh_comments()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def change_status(self):
        dialog = tk.Toplevel(self)
        dialog.title("Изменение статуса")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Новый статус:").pack(pady=5)
        status_var = tk.StringVar(value=self.request.status)
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                     values=["Новая заявка", "В процессе ремонта",
                                             "Ожидание автозапчастей", "Готова к выдаче"],
                                     state="readonly")
        status_combo.pack(pady=5)

        def save():
            new_status = status_var.get()
            if new_status == self.request.status:
                dialog.destroy()
                return
            if new_status == "Готова к выдаче" and not self.request.completion_date:
                self.request.completion_date = datetime.now().strftime("%Y-%m-%d")
            self.request.status = new_status
            messagebox.showinfo("Успех", "Статус обновлён")
            dialog.destroy()
            self.focus_set()

        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

# ====================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ======================
class MainApp(tk.Tk):
    def __init__(self, users, requests, comments):
        super().__init__()
        self.title("Автосервис: учёт заявок")
        self.geometry("800x600")
        self.users = users
        self.requests = requests
        self.comments = comments
        self.current_user = None
        self.show_login()

    def show_login(self):
        login_win = LoginWindow(self, self.users)
        self.wait_window(login_win)
        self.current_user = login_win.result
        if not self.current_user:
            self.destroy()
            return
        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text=f"Добро пожаловать, {self.current_user.fio}",
                  font=("Arial", 16)).pack(pady=10)

        if self.current_user.role in ("Оператор", "Менеджер", "Заказчик"):
            ttk.Button(self, text="Мои заявки", command=self.show_my_requests).pack(pady=5)
        if self.current_user.role == "Оператор":
            ttk.Button(self, text="Все заявки", command=self.show_all_requests).pack(pady=5)
            ttk.Button(self, text="Новая заявка", command=self.add_request).pack(pady=5)
        if self.current_user.role == "Автомеханик":
            ttk.Button(self, text="Назначенные заявки", command=self.show_assigned).pack(pady=5)
        if self.current_user.role == "Менеджер":
            ttk.Button(self, text="Статистика", command=self.show_statistics).pack(pady=5)
            ttk.Button(self, text="Назначить исполнителя", command=self.assign_master).pack(pady=5)

        ttk.Button(self, text="Выход", command=self.destroy).pack(pady=20)

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ЗАЯВКАМИ ==========
    def show_my_requests(self):
        if self.current_user.role == "Заказчик":
            filtered = [r for r in self.requests if r.client_id == self.current_user.id]
        elif self.current_user.role == "Автомеханик":
            filtered = [r for r in self.requests if r.master_id == self.current_user.id]
        else:
            filtered = self.requests
        RequestsListWindow(self, filtered, self.users, self.comments,
                           self.current_user.role, self.current_user)

    def show_all_requests(self):
        RequestsListWindow(self, self.requests, self.users, self.comments,
                           self.current_user.role, self.current_user)

    def show_assigned(self):
        self.show_my_requests()

    def add_request(self):
        dialog = tk.Toplevel(self)
        dialog.title("Новая заявка")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        fields = ["Тип авто", "Модель", "Описание проблемы", "ФИО клиента", "Телефон клиента"]
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field + ":").grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(dialog, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save():
            if not entries["Тип авто"].get() or not entries["Модель"].get() or not entries["Описание проблемы"].get():
                messagebox.showwarning("Внимание", "Заполните обязательные поля (Тип, Модель, Проблема)")
                return
            fio = entries["ФИО клиента"].get().strip()
            phone = entries["Телефон клиента"].get().strip()
            client = None
            if fio and phone:
                for u in self.users:
                    if u.fio == fio and u.phone == phone:
                        client = u
                        break
            if not client:
                new_id = max((u.id for u in self.users), default=0) + 1
                login = f"client{new_id}"
                password = f"pass{new_id}"
                client = User(new_id, fio, phone, login, password, "Заказчик")
                self.users.append(client)

            new_id = max((r.id for r in self.requests), default=0) + 1
            today = datetime.now().strftime("%Y-%m-%d")
            request = Request(
                rid=new_id,
                start_date=today,
                car_type=entries["Тип авто"].get(),
                car_model=entries["Модель"].get(),
                problem=entries["Описание проблемы"].get(),
                status="Новая заявка",
                completion_date=None,
                repair_parts="",
                master_id=None,
                client_id=client.id
            )
            self.requests.append(request)
            messagebox.showinfo("Успех", f"Заявка №{new_id} создана")
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def assign_master(self):
        unassigned = [r for r in self.requests if r.master_id is None]
        if not unassigned:
            messagebox.showinfo("Информация", "Нет заявок без назначенного мастера")
            return

        win = tk.Toplevel(self)
        win.title("Назначение мастера")
        win.geometry("600x400")
        win.transient(self)
        win.grab_set()

        ttk.Label(win, text="Выберите заявку:").pack(pady=5)
        request_var = tk.StringVar()
        request_combo = ttk.Combobox(win, textvariable=request_var,
                                      values=[f"{r.id} - {r.car_model} ({r.problem[:20]})" for r in unassigned],
                                      state="readonly", width=50)
        request_combo.pack(pady=5)

        ttk.Label(win, text="Выберите мастера:").pack(pady=5)
        masters = [u for u in self.users if u.role == "Автомеханик"]
        master_var = tk.StringVar()
        master_combo = ttk.Combobox(win, textvariable=master_var,
                                     values=[f"{u.id} - {u.fio}" for u in masters],
                                     state="readonly", width=50)
        master_combo.pack(pady=5)

        def assign():
            req_text = request_combo.get()
            master_text = master_combo.get()
            if not req_text or not master_text:
                messagebox.showwarning("Внимание", "Выберите заявку и мастера")
                return
            req_id = int(req_text.split(" - ")[0])
            master_id = int(master_text.split(" - ")[0])
            request = next(r for r in self.requests if r.id == req_id)
            request.master_id = master_id
            request.status = "В процессе ремонта"
            messagebox.showinfo("Успех", f"Мастер назначен на заявку {req_id}")
            win.destroy()

        ttk.Button(win, text="Назначить", command=assign).pack(pady=20)

    def show_statistics(self):
        total = len(self.requests)
        completed = [r for r in self.requests if r.status == "Готова к выдаче" and r.completion_date]
        avg_time = 0
        if completed:
            days = []
            for r in completed:
                try:
                    start = datetime.strptime(r.start_date, "%Y-%m-%d")
                    end = datetime.strptime(r.completion_date, "%Y-%m-%d")
                    days.append((end - start).days)
                except:
                    continue
            avg_time = sum(days) / len(days) if days else 0

        problem_stats = {}
        for r in self.requests:
            prob = r.problem.lower()
            if "тормоз" in prob:
                key = "Тормозная система"
            elif "руль" in prob:
                key = "Рулевое управление"
            elif "бензин" in prob or "топлив" in prob:
                key = "Топливная система"
            else:
                key = "Прочее"
            problem_stats[key] = problem_stats.get(key, 0) + 1

        win = tk.Toplevel(self)
        win.title("Статистика")
        win.geometry("500x400")
        win.transient(self)
        win.grab_set()

        text = f"Всего заявок: {total}\n"
        text += f"Выполнено заявок: {len(completed)}\n"
        text += f"Среднее время ремонта (дней): {avg_time:.1f}\n\n"
        text += "Статистика по неисправностям:\n"
        for k, v in problem_stats.items():
            text += f"  {k}: {v}\n"

        ttk.Label(win, text=text, font=("Arial", 12), justify="left").pack(padx=20, pady=20)
        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    # Файлы уже созданы функцией ensure_files_exist (вызвана в начале)
    users = load_users("inputDataUsers.csv")
    requests = load_requests("inputDataRequests.csv")
    comments = load_comments("inputDataComments.csv")
    app = MainApp(users, requests, comments)
    app.mainloop()