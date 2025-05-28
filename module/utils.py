from PIL import Image, ImageDraw
from logging import getLogger
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.font as tkfont
from tkinter import messagebox


logger = getLogger(__name__)


def create_app_icon() -> Image:
    width, height, padding = 64, 64, 10
    image = Image.new("RGB", (width, height), color="blue")
    dc = ImageDraw.Draw(image)
    dc.ellipse((padding, padding, width - padding, height - padding), fill="yellow")
    logger.info("Application icon initialized successfully")
    return image


def get_config_dir() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)

    return config_dir


def show_error_message(title, message) -> None:
    root = tk.Tk()
    root.title(title)
    root.resizable(True, True)  # Разрешаем изменение размера окна
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.96)  # Легкая прозрачность

    # Настройка стилей
    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="black")
    style.map("TButton", background=[('active', '#45a049')])

    # Современный шрифт
    modern_font = tkfont.Font(family="Segoe UI", size=10)
    text_font = tkfont.Font(family="Consolas", size=9)

    # Центрирование окна
    window_width, window_height = 500, 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # Основной контейнер
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Текстовая область с возможностью копирования
    text_area = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,
        font=text_font,
        bg="#f0f0f0",
        relief="flat",
        padx=10,
        pady=10,
        selectbackground="#a6d5fa",
        inactiveselectbackground="#cce8ff"  # Цвет выделения когда окно не в фокусе
    )
    text_area.insert(tk.INSERT, message)
    text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Блокируем редактирование, но разрешаем выделение
    text_area.configure(state='disabled')

    # Добавляем контекстное меню для копирования
    def copy_text():
        try:
            root.clipboard_clear()
            text = text_area.selection_get()
            root.clipboard_append(text)
        except tk.TclError:
            pass  # Если ничего не выделено

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Копировать", command=copy_text, accelerator="Ctrl+C")
    context_menu.add_separator()
    context_menu.add_command(label="Выделить все", command=lambda: text_area.tag_add('sel', '1.0', 'end'))

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    text_area.bind("<Button-3>", show_context_menu)  # ПКМ
    text_area.bind("<Control-c>", lambda e: copy_text())
    text_area.bind("<Control-a>", lambda e: text_area.tag_add('sel', '1.0', 'end'))

    # Панель кнопок
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(5, 0))

    copy_button = ttk.Button(
        button_frame,
        text="Копировать всё",
        command=lambda: [root.clipboard_clear(), root.clipboard_append(message)]
    )
    copy_button.pack(side=tk.LEFT, padx=(0, 10))

    close_button = ttk.Button(
        button_frame,
        text="Закрыть",
        command=root.destroy,
        style="TButton"
    )
    close_button.pack(side=tk.RIGHT)

    # Статус бар
    status_bar = ttk.Label(
        root,
        text="Сообщение об ошибке",
        relief=tk.SUNKEN,
        anchor=tk.W,
        padding=(5, 2)
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()
