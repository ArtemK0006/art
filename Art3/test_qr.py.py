# ============================================
# ТЕСТ QR-КОДА - САМЫЙ ПРОСТОЙ ВАРИАНТ
# ============================================

import tkinter as tk
from tkinter import messagebox

# Пробуем импортировать библиотеки
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_OK = True
    print("✅ Библиотеки найдены!")
except ImportError as e:
    QR_OK = False
    print(f"❌ Ошибка: {e}")
    print("\n🔧 Установите библиотеки командой:")
    print("pip install qrcode[pil] Pillow")
    input("\nНажмите Enter для выхода...")
    exit()

# Создаём простое окно
root = tk.Tk()
root.title("ТЕСТ QR-КОДА")
root.geometry("400x450")

# Заголовок
tk.Label(root, text="ПРОВЕРКА QR-КОДА", 
         font=('Arial', 16, 'bold')).pack(pady=10)

# Создаём QR-код
try:
    # Самый простой QR-код
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data("https://google.com")
    qr.make(fit=True)
    
    # Создаём картинку
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((250, 250))
    
    # Конвертируем
    photo = ImageTk.PhotoImage(img)
    
    # Показываем
    tk.Label(root, image=photo).pack(pady=10)
    tk.Label(root, text="✅ QR-код создан успешно!", 
             fg='green', font=('Arial', 12)).pack()
    
except Exception as e:
    tk.Label(root, text=f"❌ Ошибка: {e}", 
             fg='red', font=('Arial', 12)).pack()

# Кнопка закрытия
tk.Button(root, text="Закрыть", command=root.destroy,
          bg='#3498db', fg='white', font=('Arial', 11),
          width=15, height=2).pack(pady=20)

root.mainloop()