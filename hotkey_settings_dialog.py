import tkinter as tk
from tkinter import ttk

class HotkeySettingsDialog:
    def __init__(self, parent, current_hotkey: str, config_manager):
        """
        Инициализация диалогового окна для настройки комбинации клавиш.

        :param parent: Родительское окно (обычно корневое окно Tk).
        :param current_hotkey: Текущая комбинация клавиш в формате "alt+shift+t".
        :param config_manager: Менеджер конфигурации для сохранения новой комбинации.
        """
        self.parent = parent
        self.config_manager = config_manager
        self.current_hotkey = current_hotkey

        # Разбор текущей комбинации клавиш
        self.keys = self.current_hotkey.split('+') if self.current_hotkey else ["", "", ""]

        # Создание нового окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка комбинации клавиш")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов для выбора комбинации клавиш."""
        # Метка для первого выпадающего списка
        label1 = tk.Label(self.dialog, text="Первая клавиша:")
        label1.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Выпадающий список для первой клавиши
        self.combo1 = ttk.Combobox(self.dialog, values=["alt", "ctrl", "shift", "win"], state="readonly")
        self.combo1.grid(row=0, column=1, padx=10, pady=5)
        self.combo1.set(self.keys[0] if len(self.keys) > 0 else "")

        # Метка для второго выпадающего списка
        label2 = tk.Label(self.dialog, text="Вторая клавиша:")
        label2.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Выпадающий список для второй клавиши
        self.combo2 = ttk.Combobox(self.dialog, values=["alt", "ctrl", "shift", "win"], state="readonly")
        self.combo2.grid(row=1, column=1, padx=10, pady=5)
        self.combo2.set(self.keys[1] if len(self.keys) > 1 else "")

        # Метка для третьего выпадающего списка
        label3 = tk.Label(self.dialog, text="Третья клавиша:")
        label3.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Выпадающий список для третьей клавиши
        self.combo3 = ttk.Combobox(self.dialog, values=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                                                        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
                                   state="readonly")
        self.combo3.grid(row=2, column=1, padx=10, pady=5)
        self.combo3.set(self.keys[2] if len(self.keys) > 2 else "")

        # Кнопка "Сохранить"
        save_button = tk.Button(self.dialog, text="Сохранить", command=self.save_hotkey)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def save_hotkey(self):
        """Сохранение новой комбинации клавиш."""
        key1 = self.combo1.get()
        key2 = self.combo2.get()
        key3 = self.combo3.get()

        if not key1 or not key2 or not key3:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, выберите все три клавиши.")
            return

        new_hotkey = f"{key1}+{key2}+{key3}"
        self.config_manager.set_hotkey(new_hotkey)
        tk.messagebox.showinfo("Успех", f"Новая комбинация клавиш сохранена: {new_hotkey}")
        self.dialog.destroy()
