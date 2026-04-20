import pygame
import sys
import math

# ====================== ИНИЦИАЛИЗАЦИЯ PYGAME ======================
pygame.init()

# ====================== НАСТРОЙКИ ОКНА И ОБЛАСТИ РИСОВАНИЯ ======================
WIDTH, HEIGHT = 900, 650  # Размер окна программы
DRAW_AREA_TOP = 100  # Отступ сверху для панели инструментов
DRAW_AREA = pygame.Rect(0, DRAW_AREA_TOP, WIDTH, HEIGHT - DRAW_AREA_TOP)

# ====================== ЦВЕТА ======================
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)  # Цвет фона холста
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint - Practice 11 (Новые фигуры)")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont("arial", 22)
font_small = pygame.font.SysFont("arial", 17)

# ====================== ХОЛСТ (ПОЛОТНО ДЛЯ РИСОВАНИЯ) ======================
# Отдельная поверхность, на которой происходит всё рисование
canvas = pygame.Surface((WIDTH, HEIGHT - DRAW_AREA_TOP))
canvas.fill(LIGHT_GRAY)  # Заливаем холст светло-серым цветом

# ====================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ======================
current_color = BLACK  # Текущий цвет рисования
brush_size = 8  # Размер кисти / толщина линий
tool = "brush"  # Текущий инструмент: brush, rect, circle, square, r_triangle, e_triangle, rhombus, eraser

drawing = False  # Флаг: идёт ли сейчас рисование
start_pos = None  # Начальная позиция для фигур (при нажатии мыши)


# ====================== ОСНОВНАЯ ФУНКЦИЯ ПРОГРАММЫ ======================
def main():
    global drawing, start_pos, tool, current_color, brush_size

    while True:
        # Очистка экрана и отображение холста
        screen.fill(WHITE)
        screen.blit(canvas, (0, DRAW_AREA_TOP))

        # ====================== ОБРАБОТКА СОБЫТИЙ ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            mx, my = pygame.mouse.get_pos()
            canvas_x = mx
            canvas_y = my - DRAW_AREA_TOP
            in_area = DRAW_AREA.collidepoint(mx, my)  # Проверяем, находится ли курсор в области рисования

            # ---------- Нажатие левой кнопки мыши ----------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and in_area:
                drawing = True
                start_pos = (canvas_x, canvas_y)

            # ---------- Отпускание левой кнопки мыши ----------
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing and in_area:
                end_pos = (canvas_x, canvas_y)

                # Рисуем выбранную фигуру на холсте
                if tool in ["rect", "circle", "square", "r_triangle", "e_triangle", "rhombus"]:
                    draw_shape_on_canvas(tool, start_pos, end_pos, current_color, brush_size)

                drawing = False
                start_pos = None

            # ---------- Движение мыши (кисть и ластик) ----------
            if event.type == pygame.MOUSEMOTION and drawing and in_area:
                current_pos = (canvas_x, canvas_y)
                if tool == "brush":
                    # Рисуем линию и кружок для гладкости
                    pygame.draw.line(canvas, current_color, start_pos, current_pos, brush_size)
                    pygame.draw.circle(canvas, current_color, current_pos, brush_size // 2)
                    start_pos = current_pos
                elif tool == "eraser":
                    # Ластик — рисуем светло-серым цветом с большей толщиной
                    pygame.draw.line(canvas, LIGHT_GRAY, start_pos, current_pos, brush_size + 25)
                    pygame.draw.circle(canvas, LIGHT_GRAY, current_pos, (brush_size + 25) // 2)
                    start_pos = current_pos

        # ====================== ПРЕВЬЮ ФИГУР (предпросмотр) ======================
        # Пока пользователь держит кнопку — показываем фигуру в реальном времени
        mx, my = pygame.mouse.get_pos()
        if drawing and tool not in ["brush", "eraser"] and DRAW_AREA.collidepoint(mx, my):
            preview_end = (mx, my - DRAW_AREA_TOP)
            draw_shape_preview(tool, start_pos, preview_end, current_color, brush_size)

        # ====================== ПАНЕЛЬ УПРАВЛЕНИЯ (верхняя панель) ======================
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, DRAW_AREA_TOP))

        # Список инструментов
        tools_list = ["Кисть", "Прямоуг", "Круг", "Квадрат", "Прямоуг.треуг", "Равн.треуг", "Ромб", "Ластик"]
        tool_keys = ["1", "2", "3", "4", "5", "6", "7", "8"]
        current_tools = ["brush", "rect", "circle", "square", "r_triangle", "e_triangle", "rhombus", "eraser"]

        for i, text in enumerate(tools_list):
            color = BLACK if tool == current_tools[i] else WHITE
            txt = font.render(f"{tool_keys[i]} - {text}", True, color)
            screen.blit(txt, (20 + i * 105, 12))

        # Палитра цветов
        colors = [BLACK, (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (255, 0, 255), (255, 165, 0), (0, 255, 255), WHITE]
        for i, c in enumerate(colors):
            pygame.draw.rect(screen, c, (25 + i * 45, 55, 38, 32))
            if c == current_color:
                pygame.draw.rect(screen, BLACK, (22 + i * 45, 52, 44, 38), 4)  # Рамка выделения

        # Отображение текущего размера кисти
        size_txt = font_small.render(f"Размер: {brush_size}", True, BLACK)
        screen.blit(size_txt, (WIDTH - 210, 20))
        pygame.draw.line(screen, BLACK, (WIDTH - 210, 55), (WIDTH - 70, 55), brush_size)

        # Подсказки по управлению
        help_txt = font_small.render("1-8: инструмент | +/- : размер | C: очистить | S: сохранить", True, BLACK)
        screen.blit(help_txt, (20, HEIGHT - 25))

        # ====================== ОБРАБОТКА КЛАВИШ ======================
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: tool = "brush"
        if keys[pygame.K_2]: tool = "rect"
        if keys[pygame.K_3]: tool = "circle"
        if keys[pygame.K_4]: tool = "square"
        if keys[pygame.K_5]: tool = "r_triangle"
        if keys[pygame.K_6]: tool = "e_triangle"
        if keys[pygame.K_7]: tool = "rhombus"
        if keys[pygame.K_8]: tool = "eraser"

        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            brush_size = min(40, brush_size + 1)
        if keys[pygame.K_MINUS]:
            brush_size = max(2, brush_size - 1)
        if keys[pygame.K_c]:
            canvas.fill(LIGHT_GRAY)  # Очистка холста
        if keys[pygame.K_s]:
            pygame.image.save(canvas, "my_drawing.png")
            print("✅ Рисунок сохранён как my_drawing.png")

        # Выбор цвета кликом по палитре
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if 55 <= my <= 87:
                for i, c in enumerate(colors):
                    if 25 + i * 45 <= mx <= 63 + i * 45:
                        current_color = c

        pygame.display.flip()
        clock.tick(120)


# ====================== ФУНКЦИИ РИСОВАНИЯ ФИГУР ======================

def draw_shape_on_canvas(tool, start, end, color, thickness):
    """Рисует выбранную фигуру на основном холсте (при отпускании кнопки мыши)"""
    if tool == "rect":
        pygame.draw.rect(canvas, color,
                         pygame.Rect(min(start[0], end[0]), min(start[1], end[1]),
                                     abs(start[0] - end[0]), abs(start[1] - end[1])), thickness)

    elif tool == "circle":
        radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        pygame.draw.circle(canvas, color, start, radius, thickness)

    elif tool == "square":
        side = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        pygame.draw.rect(canvas, color,
                         pygame.Rect(start[0], start[1], side, side), thickness)

    elif tool == "r_triangle":  # Прямоугольный треугольник
        points = [start, (end[0], start[1]), (start[0], end[1])]
        pygame.draw.polygon(canvas, color, points, thickness)

    elif tool == "e_triangle":  # Равносторонний треугольник
        dx = end[0] - start[0]
        height = int(abs(dx) * math.sqrt(3) / 2)
        points = [
            start,
            (end[0], start[1]),
            (start[0] + dx // 2, start[1] + height if dx > 0 else start[1] - height)
        ]
        pygame.draw.polygon(canvas, color, points, thickness)

    elif tool == "rhombus":  # Ромб
        points = [
            start,
            (end[0], start[1]),
            (end[0] + (start[0] - end[0]), end[1]),
            (start[0], end[1])
        ]
        pygame.draw.polygon(canvas, color, points, thickness)


def draw_shape_preview(tool, start, end, color, thickness):
    """Рисует предпросмотр фигуры на экране (пока кнопка мыши зажата)"""
    if tool == "rect":
        pygame.draw.rect(screen, color,
                         pygame.Rect(min(start[0], end[0]), min(start[1], end[1]) + DRAW_AREA_TOP,
                                     abs(start[0] - end[0]), abs(start[1] - end[1])), thickness)

    elif tool == "circle":
        radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        pygame.draw.circle(screen, color, (start[0], start[1] + DRAW_AREA_TOP), radius, thickness)

    elif tool == "square":
        side = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        pygame.draw.rect(screen, color,
                         pygame.Rect(start[0], start[1] + DRAW_AREA_TOP, side, side), thickness)

    elif tool == "r_triangle":
        points = [(start[0], start[1] + DRAW_AREA_TOP),
                  (end[0], start[1] + DRAW_AREA_TOP),
                  (start[0], end[1] + DRAW_AREA_TOP)]
        pygame.draw.polygon(screen, color, points, thickness)

    elif tool == "e_triangle":
        dx = end[0] - start[0]
        height = int(abs(dx) * math.sqrt(3) / 2)
        points = [
            (start[0], start[1] + DRAW_AREA_TOP),
            (end[0], start[1] + DRAW_AREA_TOP),
            (start[0] + dx // 2, start[1] + DRAW_AREA_TOP + (height if dx > 0 else -height))
        ]
        pygame.draw.polygon(screen, color, points, thickness)

    elif tool == "rhombus":
        points = [
            (start[0], start[1] + DRAW_AREA_TOP),
            (end[0], start[1] + DRAW_AREA_TOP),
            (end[0] + (start[0] - end[0]), end[1] + DRAW_AREA_TOP),
            (start[0], end[1] + DRAW_AREA_TOP)
        ]
        pygame.draw.polygon(screen, color, points, thickness)


# ====================== ЗАПУСК ПРОГРАММЫ ======================
if __name__ == "__main__":
    main()