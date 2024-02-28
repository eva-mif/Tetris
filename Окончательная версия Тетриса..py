import random
import sys
import pygame
from tkinter import *
import sqlite3

# Устанавливаем соединение с базой данных
conn = sqlite3.connect('tetris_scores.db')
cur = conn.cursor()

# Проверяем наличие таблицы "tetris_scores"
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tetris_scores'")
table_exists = cur.fetchone()

if not table_exists:
    # Создаем таблицу "tetris_scores"
    cur.execute('''CREATE TABLE tetris_scores (
                    id INTEGER PRIMARY KEY,
                    score INTEGER
                )''')


# Функция для подсчета общего количества проигрышей
def get_total_losses():
    cur.execute("SELECT COUNT(*) FROM tetris_scores")
    total_losses = cur.fetchone()[0]
    return total_losses


# Получаем общее количество проигрышей
total_losses = get_total_losses()
print(f"Общее количество проигрышей в игре тетрис: {total_losses}")


# Функция для обновления количества проигрышей в базе данных
def update_losses():
    cur.execute("INSERT INTO tetris_scores (score) VALUES (?)", (1,))
    conn.commit()


# начальное окно с кнопкой "Начать!"
class Main(Frame):
    def __init__(self, root):
        super(Main, self).__init__(root)
        self.root = root
        root.protocol('WM_DELETE_WINDOW', self.exit_game)
        self.startUI()

    def startUI(self):
        self.btn = Button(self.root, text="Начать!", font=("Times New Roman", 15),
                          command=lambda x=1: self.btn_click(x))
        self.btn.place(x=10, y=100, width=120, height=50)

        self.lbl = Label(self.root, text="Начало игры!", bg="#FAF", font=("Times New Roman", 21, "bold"))
        self.lbl.place(x=150, y=25)

    def btn_click(self, x):
        if self.btn:
            # Проверяем наличие записей в таблице tetris_scores
            cur.execute("SELECT * FROM tetris_scores")
            existing_records = cur.fetchall()
            if not existing_records:  # Если таблица пуста, добавляем новую запись
                update_losses()  # Вызываем метод update_losses() при нажатии на кнопку "Начать!"
            self.run = True
        self.start_game()

    # выход из игры
    def exit_game(self):
        sys.exit()

    def start_game(self):
        self.root.destroy()
        self.run_game()

    def run_game(self):
        pygame.init()
        clock = pygame.time.Clock()
        self.Tetromino.show()


if __name__ == '__main__':
    root = Tk()
    root.geometry("500x500+200+200")
    root.title("Тетрис")
    root.resizable(False, False)
    root["bg"] = "#FAF"
    app = Main(root)
    app.pack()
    root.mainloop()

pygame.init()

# инициализация окна игры, размеров и цветов тетромино
win_width = 300
win_height = 600
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Tetris")

white = (255, 255, 255)
black = (0, 0, 0)
colors = [(255, 255, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
figure_colors = [(0, 255, 255), (255, 0, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

block_size = 30
rows = win_height // block_size
cols = win_width // block_size

# угол поворота тетромино
angle = 0
corner = [0, 90, 180, 270]

# виды тетрамино
tetrominoes = [
    [[1, 1, 1, 1]],
    [[1, 1, 0],
     [0, 1, 1]],
    [[0, 1, 1],
     [1, 1, 0]],
    [[1, 1],
     [1, 1]],
    [[1, 1, 1],
     [0, 1, 0]],
    [[1, 1, 1],
     [0, 0, 1]],
    [[1, 1, 1],
     [1, 0, 0]]
]


class Tetromino:
    def init(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.choice(tetrominoes)
        self.color = random.choice(figure_colors)

    # поворот тетромино
    def rotate(self):
        rotated_shape = list(zip(*self.shape[::-1]))
        if self.x + len(rotated_shape[0]) * block_size > win_width or self.y + len(
                rotated_shape) * block_size > win_height:
            return
        self.shape = rotated_shape
        if self.x + len(self.shape[0]) * block_size > win_width:
            self.x = win_width - len(self.shape[0]) * block_size
        if self.y + len(self.shape) * block_size > win_height:
            self.y = win_height - len(self.shape) * block_size

    # рисование тетромино на поле
    def draw(self):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1:
                    pygame.draw.rect(win, self.color,
                                     (self.x + j * block_size, self.y + i * block_size,
                                      block_size, block_size))

    # движение тетромино вниз
    def move_down(self):
        for i in range(len(self.shape)):
            if (self.y + (len(self.shape) * block_size) >= win_height or
                    grid[self.y // block_size + len(self.shape)][self.x // block_size] != 0):
                for i in range(len(self.shape)):
                    for j in range(len(self.shape[i])):
                        if self.shape[i][j] == 1:
                            grid[self.y // block_size + i][self.x // block_size] = colors.index(self.color)
                clear_lines(check_lines())
                return

        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1 and grid[(self.y // block_size) + i + 1][(self.x // block_size) + j] != 0:
                    for i in range(len(self.shape)):
                        for j in range(len(self.shape[i])):
                            if self.shape[i][j] == 1:
                                grid[self.y // block_size + i][self.x // block_size] = colors.index(self.color)
                    clear_lines(check_lines())
                    return
        self.y += block_size

    # движение тетромино влево
    def move_side(self, direction):
        if direction == "left":
            for i in range(len(self.shape)):
                if self.x - block_size < 0 or grid[self.y // block_size + i][self.x // block_size - 1] != 0:
                    return

            # и вправо
            self.x -= block_size
        elif direction == "right":
            for i in range(len(self.shape)):
                if self.x + (len(self.shape[0]) * block_size) >= win_width or grid[self.y // block_size + i][
                    self.x // block_size + len(self.shape[0])] != 0:
                    return
            self.x += block_size


# проверка заполненности линий
def check_lines():
    global grid
    lines_to_clear = []
    for i in range(rows):
        if all(grid[i]):
            lines_to_clear.append(i)
    return lines_to_clear


# обозначение параметров тетрамино к полю
def draw_grid():
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                pygame.draw.rect(win, colors[grid[i][j]],
                                 (j * block_size, i * block_size, block_size, block_size), 0)
            pygame.draw.rect(win, black, (j * block_size, i * block_size, block_size, block_size), 1)


# очистка линий
def clear_lines(lines_to_clear):
    global grid
    for line in lines_to_clear:
        del grid[line]
        grid.insert(0, [0] * cols)


# проверка поражения
def check_defeat():
    for i in range(3):
        for j in range(cols):
            if grid[i][j] != 0:
                return True
    return False


grid = [[0] * cols for _ in range(rows)]

current_piece = Tetromino()
current_piece.init(3 * block_size, 0)

run = True
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 500
level = 1

# основной цикл игры
while run:
    pygame.init()
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_piece.rotate()
        if check_defeat():
            print("Вы проиграли!")
            run = False

        # используемые клавиши: влево, вправо, вниз, вверх
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            current_piece.move_side("left")
        if keys[pygame.K_RIGHT]:
            current_piece.move_side("right")
        if keys[pygame.K_DOWN]:
            current_piece.move_down()
        if keys[pygame.K_UP]:
            current_piece.rotate()

    win.fill(white)
    draw_grid()
    lines_to_clear = check_lines()

    if lines_to_clear:
        clear_lines(lines_to_clear)
        level += 1
        fall_speed = 500 - (level * 50)

    if pygame.time.get_ticks() - fall_time > fall_speed:
        current_piece.move_down()
        fall_time = pygame.time.get_ticks()

    # параметры фигур
    current_piece.draw()
    if current_piece.y + (len(current_piece.shape) * block_size) >= win_height or \
            grid[current_piece.y // block_size + len(current_piece.shape)][current_piece.x // block_size] != 0:
        for i in range(len(current_piece.shape)):
            for j in range(len(current_piece.shape[i])):
                if current_piece.shape[i][j] == 1:
                    grid[current_piece.y // block_size + i][current_piece.x // block_size + j] = colors.index(
                        current_piece.color)
        current_piece = Tetromino()
        current_piece.init(3 * block_size, 0)
    pygame.display.update()

    clock.tick(30)

    # pygame.quit()
