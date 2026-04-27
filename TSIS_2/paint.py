import pygame
import sys
import math
from datetime import datetime
from collections import deque

# ====================== ИНИЦИАЛИЗАЦИЯ PYGAME ======================
pygame.init()

# ====================== НАСТРОЙКИ ОКНА ======================
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 110
DRAW_AREA_TOP = TOOLBAR_HEIGHT
DRAW_AREA = pygame.Rect(0, DRAW_AREA_TOP, WIDTH, HEIGHT - DRAW_AREA_TOP)

# ====================== ЦВЕТА ======================
WHITE      = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
GRAY       = (210, 210, 210)
DARK_GRAY  = (160, 160, 160)
BLACK      = (0, 0, 0)
ACCENT     = (70, 130, 180)

# ====================== ЭКРАН И ХОЛСТ ======================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — TSIS 2")
clock = pygame.time.Clock()

canvas = pygame.Surface((WIDTH, HEIGHT - DRAW_AREA_TOP))
canvas.fill(WHITE)

# ====================== ШРИФТЫ ======================
font       = pygame.font.SysFont("arial", 14)
font_bold  = pygame.font.SysFont("arial", 14, bold=True)
font_text  = pygame.font.SysFont("arial", 20)   # Для текстового инструмента

# ====================== СОСТОЯНИЕ ======================
current_color = BLACK
brush_size    = 5   # 2 / 5 / 10
tool          = "pencil"

drawing    = False
start_pos  = None
prev_pos   = None   # Для карандаша

# Прямая линия
line_start = None

# Текстовый инструмент
text_mode     = False
text_pos      = None    # Позиция на холсте
text_buffer   = ""

# ====================== ИНСТРУМЕНТЫ И КНОПКИ ======================
TOOLS = [
    ("pencil",     "Карандаш",   "P"),
    ("line",       "Линия",      "L"),
    ("rect",       "Прямоуг.",   "R"),
    ("circle",     "Круг",       "O"),
    ("square",     "Квадрат",    "Q"),
    ("r_triangle", "П.треуг",    "T"),
    ("e_triangle", "Р.треуг",    "Y"),
    ("rhombus",    "Ромб",       "H"),
    ("fill",       "Заливка",    "F"),
    ("text",       "Текст",      "X"),
    ("eraser",     "Ластик",     "E"),
]

PALETTE = [
    BLACK, WHITE, (128,128,128), (192,192,192),
    (255,0,0), (0,255,0), (0,0,255),
    (255,255,0), (255,165,0), (255,0,255),
    (0,255,255), (139,69,19),
]

SIZE_PRESETS = [2, 5, 10]

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================

def canvas_pos(mx, my):
    return mx, my - DRAW_AREA_TOP

def in_draw_area(mx, my):
    return DRAW_AREA.collidepoint(mx, my)


# ====================== РИСОВАНИЕ ФИГУР НА ПОВЕРХНОСТИ ======================

def draw_shape(surface, tool, start, end, color, thickness, offset_y=0):
    """Рисует фигуру на surface. offset_y добавляется к y-координатам (для preview на screen)."""
    sx, sy = start[0], start[1] + offset_y
    ex, ey = end[0],   end[1]   + offset_y

    if tool == "rect":
        r = pygame.Rect(min(sx,ex), min(sy,ey), abs(ex-sx), abs(ey-sy))
        pygame.draw.rect(surface, color, r, thickness)

    elif tool == "circle":
        rad = int(math.hypot(ex-sx, ey-sy))
        pygame.draw.circle(surface, color, (sx, sy), rad, thickness)

    elif tool == "square":
        side = max(abs(ex-sx), abs(ey-sy))
        pygame.draw.rect(surface, color, pygame.Rect(sx, sy, side, side), thickness)

    elif tool == "r_triangle":
        pts = [(sx,sy), (ex,sy), (sx,ey)]
        pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "e_triangle":
        dx = ex - sx
        h  = int(abs(dx) * math.sqrt(3) / 2)
        pts = [
            (sx, sy),
            (ex, sy),
            (sx + dx//2, sy + (h if dx > 0 else -h))
        ]
        pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "rhombus":
        mid_x = (sx + ex) // 2
        mid_y = (sy + ey) // 2
        pts = [
            (mid_x, sy),   # верх
            (ex,    mid_y),# право
            (mid_x, ey),   # низ
            (sx,    mid_y),# лево
        ]
        pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "line":
        pygame.draw.line(surface, color, (sx,sy), (ex,ey), thickness)


# ====================== FLOOD FILL ======================

def flood_fill(surface, pos, fill_color):
    """BFS flood-fill по пикселям поверхности."""
    x, y = pos
    w, h = surface.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return

    target_color = surface.get_at((x, y))[:3]
    fc = fill_color[:3]
    if target_color == fc:
        return

    visited = set()
    queue   = deque()
    queue.append((x, y))
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), fill_color)
        for nx, ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
            if (nx, ny) not in visited and 0 <= nx < w and 0 <= ny < h:
                if surface.get_at((nx, ny))[:3] == target_color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


# ====================== TOOLBAR ======================

tool_rects  = []
size_rects  = []
color_rects = []

def build_toolbar():
    global tool_rects, size_rects, color_rects
    tool_rects  = []
    size_rects  = []
    color_rects = []

    # --- Инструменты (строка 1, левая часть) ---
    bw, bh = 75, 26
    for i, (key, label, _) in enumerate(TOOLS):
        rx = 5 + i * (bw + 3)
        ry = 5
        tool_rects.append((pygame.Rect(rx, ry, bw, bh), key))

    # --- Размеры кисти ---
    labels = ["S (1)", "M (2)", "L (3)"]
    for i, lbl in enumerate(labels):
        rx = 5 + i * 70
        ry = 37
        size_rects.append((pygame.Rect(rx, ry, 65, 26), SIZE_PRESETS[i]))

    # --- Палитра ---
    for i, c in enumerate(PALETTE):
        rx = 5 + i * 36
        ry = 70
        color_rects.append((pygame.Rect(rx, ry, 32, 32), c))


def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT-1), (WIDTH, TOOLBAR_HEIGHT-1), 2)

    # Инструменты
    for rect, key in tool_rects:
        label = next(l for k,l,_ in TOOLS if k == key)
        active = (key == tool)
        bg = ACCENT if active else (230, 230, 230)
        pygame.draw.rect(screen, bg, rect, border_radius=4)
        pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)
        fc = WHITE if active else BLACK
        txt = font_bold.render(label, True, fc) if active else font.render(label, True, fc)
        screen.blit(txt, txt.get_rect(center=rect.center))

    # Размеры кисти
    labels = ["S (1)", "M (2)", "L (3)"]
    for i, (rect, sz) in enumerate(size_rects):
        active = (sz == brush_size)
        bg = ACCENT if active else (230, 230, 230)
        pygame.draw.rect(screen, bg, rect, border_radius=4)
        pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)
        fc = WHITE if active else BLACK
        txt = font_bold.render(labels[i], True, fc)
        screen.blit(txt, txt.get_rect(center=rect.center))

    # Палитра
    for rect, c in color_rects:
        pygame.draw.rect(screen, c, rect)
        if c == current_color:
            pygame.draw.rect(screen, BLACK, rect, 3)
        else:
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)

    # Текущий цвет — индикатор справа
    ind = pygame.Rect(WIDTH - 55, 8, 48, 48)
    pygame.draw.rect(screen, current_color, ind)
    pygame.draw.rect(screen, BLACK, ind, 2)
    lbl = font.render("Цвет", True, BLACK)
    screen.blit(lbl, (WIDTH - 53, 60))

    # Подсказки
    hints = "Ctrl+S: сохранить | C: очистить | Esc: отмена текста"
    screen.blit(font.render(hints, True, (80,80,80)), (5, TOOLBAR_HEIGHT - 18))


# ====================== ГЛАВНЫЙ ЦИКЛ ======================

def main():
    global drawing, start_pos, prev_pos, tool, current_color, brush_size
    global line_start, text_mode, text_pos, text_buffer

    build_toolbar()

    while True:
        screen.fill(WHITE)
        screen.blit(canvas, (0, DRAW_AREA_TOP))

        mx, my = pygame.mouse.get_pos()
        cx, cy = canvas_pos(mx, my)

        # ======== PREVIEW ========
        if drawing and tool not in ("pencil", "eraser", "fill", "text") and in_draw_area(mx, my):
            draw_shape(screen, tool, start_pos, (cx, cy), current_color, brush_size, offset_y=DRAW_AREA_TOP)

        if tool == "line" and line_start and in_draw_area(mx, my):
            lsx, lsy = line_start
            pygame.draw.line(screen, current_color,
                             (lsx, lsy + DRAW_AREA_TOP),
                             (mx, my), brush_size)

        # Preview текста
        if text_mode and text_pos:
            preview = text_buffer + "|"
            surf = font_text.render(preview, True, current_color)
            screen.blit(surf, (text_pos[0], text_pos[1] + DRAW_AREA_TOP))

        # ======== СОБЫТИЯ ========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ---------- KEYDOWN ----------
            if event.type == pygame.KEYDOWN:

                # Текстовый режим
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Зафиксировать текст на холсте
                        if text_buffer and text_pos:
                            surf = font_text.render(text_buffer, True, current_color)
                            canvas.blit(surf, text_pos)
                        text_mode   = False
                        text_pos    = None
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_pos    = None
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode:
                            text_buffer += event.unicode
                    continue  # не обрабатывать горячие клавиши в текстовом режиме

                # Ctrl+S — сохранение
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name = f"canvas_{ts}.png"
                    pygame.image.save(canvas, name)
                    print(f"✅ Сохранено: {name}")
                    continue

                # Очистка
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)

                # Инструменты по горячим клавишам
                key_map = {
                    pygame.K_p: "pencil",
                    pygame.K_l: "line",
                    pygame.K_r: "rect",
                    pygame.K_o: "circle",
                    pygame.K_q: "square",
                    pygame.K_t: "r_triangle",
                    pygame.K_y: "e_triangle",
                    pygame.K_h: "rhombus",
                    pygame.K_f: "fill",
                    pygame.K_x: "text",
                    pygame.K_e: "eraser",
                }
                if event.key in key_map:
                    tool = key_map[event.key]

                # Размер кисти
                if event.key == pygame.K_1: brush_size = 2
                if event.key == pygame.K_2: brush_size = 5
                if event.key == pygame.K_3: brush_size = 10

            # ---------- MOUSEBUTTONDOWN ----------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Клик по тулбару
                if my < TOOLBAR_HEIGHT:
                    for rect, key in tool_rects:
                        if rect.collidepoint(mx, my):
                            tool = key
                    for rect, sz in size_rects:
                        if rect.collidepoint(mx, my):
                            brush_size = sz
                    for rect, c in color_rects:
                        if rect.collidepoint(mx, my):
                            current_color = c
                    continue

                if not in_draw_area(mx, my):
                    continue

                # Клик по холсту
                if tool == "fill":
                    flood_fill(canvas, (cx, cy), current_color)

                elif tool == "text":
                    text_mode   = True
                    text_pos    = (cx, cy)
                    text_buffer = ""

                elif tool == "line":
                    line_start = (cx, cy)

                elif tool in ("pencil", "eraser"):
                    drawing   = True
                    start_pos = (cx, cy)
                    prev_pos  = (cx, cy)

                else:
                    drawing   = True
                    start_pos = (cx, cy)

            # ---------- MOUSEBUTTONUP ----------
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if tool == "line" and line_start:
                    if in_draw_area(mx, my):
                        pygame.draw.line(canvas, current_color, line_start, (cx, cy), brush_size)
                    line_start = None

                elif drawing and tool not in ("pencil", "eraser"):
                    if in_draw_area(mx, my) and start_pos:
                        draw_shape(canvas, tool, start_pos, (cx, cy), current_color, brush_size)
                    drawing   = False
                    start_pos = None

                elif drawing:
                    drawing   = False
                    start_pos = None
                    prev_pos  = None

            # ---------- MOUSEMOTION ----------
            if event.type == pygame.MOUSEMOTION and drawing and in_draw_area(mx, my):
                if tool == "pencil":
                    if prev_pos:
                        pygame.draw.line(canvas, current_color, prev_pos, (cx, cy), brush_size)
                        pygame.draw.circle(canvas, current_color, (cx, cy), brush_size // 2)
                    prev_pos = (cx, cy)

                elif tool == "eraser":
                    er = brush_size * 3
                    if prev_pos:
                        pygame.draw.line(canvas, WHITE, prev_pos, (cx, cy), er)
                        pygame.draw.circle(canvas, WHITE, (cx, cy), er // 2)
                    prev_pos = (cx, cy)

        # ======== ТУЛБАР ========
        draw_toolbar()

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()
