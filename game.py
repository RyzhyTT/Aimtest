import tkinter as tk
from tkinter import messagebox
import random
import os

BEST_FILE = "aimtest_best.txt"


class AimTestApp:
    def __init__(self, root):
        self.root = root
        root.title("AimTest — Tkinter")

        # Параметры
        self.WIDTH = 800
        self.HEIGHT = 600
        self.TARGET_RADIUS = 30
        self.ROUND_SECONDS = 30

        # Состояние игры
        self.time_left = 0
        self.running = False
        self.target_id = None
        self.target_center = (0, 0)
        self.hits = 0
        self.total_clicks = 0

        # Лучший результат (загружаем из файла)
        self.best_score = self.load_best()

        # GUI
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=8, pady=6)

        self.time_label = tk.Label(top_frame, text=f"Время: {self.ROUND_SECONDS}", font=("Arial", 14))
        self.time_label.pack(side=tk.LEFT, padx=8)

        self.score_label = tk.Label(top_frame, text="Очки: 0", font=("Arial", 14))
        self.score_label.pack(side=tk.LEFT, padx=8)

        self.accuracy_label = tk.Label(top_frame, text="Точность: 0%", font=("Arial", 14))
        self.accuracy_label.pack(side=tk.LEFT, padx=8)

        self.best_label = tk.Label(top_frame, text=f"Лучший: {self.best_score}", font=("Arial", 14))
        self.best_label.pack(side=tk.RIGHT, padx=8)

        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self.canvas.pack(padx=8, pady=6)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill=tk.X, padx=8, pady=6)

        self.start_button = tk.Button(bottom_frame, text="Старт", width=12, command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=6)

        self.info_label = tk.Label(bottom_frame, text="Кликайте по красной мишени!", font=("Arial", 12))
        self.info_label.pack(side=tk.LEFT, padx=8)

        # Обработчик кликов по канве
        self.canvas.bind("<Button-1>", self.on_click)

    def load_best(self):
        try:
            if os.path.exists(BEST_FILE):
                with open(BEST_FILE, "r") as f:
                    return int(f.read().strip() or 0)
        except Exception:
            pass
        return 0

    def save_best(self):
        try:
            with open(BEST_FILE, "w") as f:
                f.write(str(self.best_score))
        except Exception:
            pass

    def start_game(self):
        if self.running:
            return
        # Сброс состояния
        self.time_left = self.ROUND_SECONDS
        self.running = True
        self.hits = 0
        self.total_clicks = 0
        self.update_labels()
        self.start_button.config(state=tk.DISABLED)
        # Появление первой мишени и запуск таймера
        self.spawn_target()
        self.countdown()

    def end_game(self):
        self.running = False
        # Удалить мишень
        if self.target_id:
            self.canvas.delete(self.target_id)
            self.target_id = None
        # Сравнить и обновить лучший результат
        if self.hits > self.best_score:
            self.best_score = self.hits
            self.save_best()
            self.best_label.config(text=f"Лучший: {self.best_score}")
            msg = f"Время вышло!\nВаши очки: {self.hits}\nНовый рекорд!"
        else:
            msg = f"Время вышло!\nВаши очки: {self.hits}"
        self.start_button.config(state=tk.NORMAL)
        self.update_labels()
        messagebox.showinfo("Раунд завершён", msg)

    def countdown(self):
        if not self.running:
            return
        self.time_label.config(text=f"Время: {self.time_left}")
        if self.time_left <= 0:
            self.end_game()
            return
        self.time_left -= 1
        # Планируем следующий вызов через 1 секунду
        self.root.after(1000, self.countdown)

    def spawn_target(self):
        # Удаляем старую
        if self.target_id:
            self.canvas.delete(self.target_id)
            self.target_id = None

        r = self.TARGET_RADIUS
        x = random.randint(r + 5, self.WIDTH - r - 5)
        y = random.randint(r + 5, self.HEIGHT - r - 5)
        self.target_center = (x, y)
        x1, y1 = x - r, y - r
        x2, y2 = x + r, y + r
        # Рисуем цель: красный круг с черной окантовкой
        self.target_id = self.canvas.create_oval(x1, y1, x2, y2, fill="red", outline="black", width=2)

    def on_click(self, event):
        if not self.running:
            return
        self.total_clicks += 1
        # Проверка попадания: расстояние до центра <= radius
        cx, cy = self.target_center
        dx = event.x - cx
        dy = event.y - cy
        dist2 = dx * dx + dy * dy
        if dist2 <= self.TARGET_RADIUS * self.TARGET_RADIUS:
            # Попадание
            self.hits += 1
            # Немного "отзывчивости": мигнуть цветом или создать новую
            # Здесь просто создаём новую мишень
            self.spawn_target()
        else:
            # Промах — можно добавить эффект (миг, звуковой сигнал и т.п.)
            pass
        self.update_labels()

    def update_labels(self):
        self.score_label.config(text=f"Очки: {self.hits}")
        acc = 0
        if self.total_clicks > 0:
            acc = int(round(self.hits / self.total_clicks * 100))
        self.accuracy_label.config(text=f"Точность: {acc}%")
        # время обновляем отдельно в countdown

if __name__ == "__main__":
    root = tk.Tk()
    app = AimTestApp(root)
    root.mainloop()
