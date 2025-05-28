import tkinter as tk
from tkinter import scrolledtext


def show_copyable_message(title, message):
    """
    Создает окно с сообщением, которое можно скопировать.

    :param title: Заголовок окна
    :param message: Текст сообщения
    """
    root = tk.Tk()
    root.title(title)

    # Создаем прокручиваемое текстовое поле
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
    text_area.insert(tk.INSERT, message)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Делаем текстовое поле доступным только для чтения
    text_area.configure(state='disabled')

    # Кнопка для закрытия окна
    close_button = tk.Button(root, text="Закрыть", command=root.destroy)
    close_button.pack(pady=10)

    root.mainloop()


# Пример использования
if __name__ == "__main__":
    show_copyable_message(
        "Ошибка",
        "Произошла критическая ошибка:\n\n" +
        "Traceback (most recent call last):\n" +
        "  File \"example.py\", line 10, in <module>\n" +
        "    result = 10 / 0\n" +
        "ZeroDivisionError: division by zero"
    )