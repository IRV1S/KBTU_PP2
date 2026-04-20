import pygame
import sys

pygame.init()

# ====================== НАСТРОЙКИ ======================
WIDTH, HEIGHT = 900, 650
DRAW_AREA_TOP = 100
DRAW_AREA = pygame.Rect(0, DRAW_AREA_TOP, WIDTH, HEIGHT - DRAW_AREA_TOP)

# Цвета
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint - Practice 10 (Ластик исправлен)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
font_small = pygame.font.SysFont("arial", 18)

# ====================== ХОЛСТ ======================
canvas = pygame.Surface((WIDTH, HEIGHT - DRAW_AREA_TOP))
canvas.fill(LIGHT_GRAY)

# Переменные
current_color = BLACK
brush_size = 12
tool = "brush"  # brush, rect, circle, eraser
drawing = False
start_pos = None


# ====================== ОСНОВНОЙ ЦИКЛ ======================
def main():
    global drawing, start_pos, tool, current_color, brush_size

    while True:
        screen.fill(WHITE)
        screen.blit(canvas, (0, DRAW_AREA_TOP))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            mx, my = pygame.mouse.get_pos()
            canvas_x = mx
            canvas_y = my - DRAW_AREA_TOP
            in_area = DRAW_AREA.collidepoint(mx, my)

            # Нажатие мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and in_area:
                drawing = True
                start_pos = (canvas_x, canvas_y)

            # Отпускание мыши
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                if tool in ["rect", "circle"] and in_area:
                    end_pos = (canvas_x, canvas_y)
                    if tool == "rect":
                        pygame.draw.rect(canvas, current_color,
                                         pygame.Rect(min(start_pos[0], end_pos[0]),
                                                     min(start_pos[1], end_pos[1]),
                                                     abs(start_pos[0] - end_pos[0]),
                                                     abs(start_pos[1] - end_pos[1])),
                                         width=brush_size)
                    elif tool == "circle":
                        radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                        pygame.draw.circle(canvas, current_color, start_pos, radius, width=brush_size)

                drawing = False
                start_pos = None

            # Движение мыши
            if event.type == pygame.MOUSEMOTION and drawing and in_area:
                current_pos = (canvas_x, canvas_y)

                if tool == "brush":
                    pygame.draw.line(canvas, current_color, start_pos, current_pos, brush_size)
                    pygame.draw.circle(canvas, current_color, current_pos, brush_size // 2)
                    start_pos = current_pos

                elif tool == "eraser":
                    pygame.draw.line(canvas, LIGHT_GRAY, start_pos, current_pos, brush_size + 20)
                    pygame.draw.circle(canvas, LIGHT_GRAY, current_pos, (brush_size + 20) // 2)
                    start_pos = current_pos

        # Preview (показ во время рисования)
        mx, my = pygame.mouse.get_pos()
        if drawing and tool in ["rect", "circle"] and DRAW_AREA.collidepoint(mx, my):
            end_pos = (mx, my - DRAW_AREA_TOP)
            if tool == "rect":
                pygame.draw.rect(screen, current_color,
                                 pygame.Rect(min(start_pos[0], end_pos[0]),
                                             min(start_pos[1], end_pos[1]) + DRAW_AREA_TOP,
                                             abs(start_pos[0] - end_pos[0]),
                                             abs(start_pos[1] - end_pos[1])),
                                 width=brush_size)
            elif tool == "circle":
                radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                pygame.draw.circle(screen, current_color,
                                   (start_pos[0], start_pos[1] + DRAW_AREA_TOP),
                                   radius, width=brush_size)

        # ====================== ПАНЕЛЬ ======================
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, DRAW_AREA_TOP))

        tools_list = ["Кисть (1)", "Прямоугольник (2)", "Круг (3)", "Ластик (4)"]
        for i, text in enumerate(tools_list):
            color = BLACK if tool == ["brush", "rect", "circle", "eraser"][i] else WHITE
            txt = font.render(text, True, color)
            screen.blit(txt, (30 + i * 170, 15))

        # Цвета
        colors = [BLACK, (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (255, 0, 255), (255, 165, 0), (0, 255, 255), WHITE]
        for i, c in enumerate(colors):
            pygame.draw.rect(screen, c, (30 + i * 45, 55, 38, 32))
            if c == current_color:
                pygame.draw.rect(screen, BLACK, (27 + i * 45, 52, 44, 38), 4)

        # Размер
        size_txt = font_small.render(f"Размер: {brush_size}", True, BLACK)
        screen.blit(size_txt, (WIDTH - 220, 20))
        pygame.draw.line(screen, BLACK, (WIDTH - 220, 55), (WIDTH - 80, 55), brush_size)

        help_txt = font_small.render("1-4: выбор инструмента | +/- : размер | C: очистить | S: сохранить", True, BLACK)
        screen.blit(help_txt, (20, HEIGHT - 25))

        # ====================== КЛАВИШИ ======================
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: tool = "brush"
        if keys[pygame.K_2]: tool = "rect"
        if keys[pygame.K_3]: tool = "circle"
        if keys[pygame.K_4]: tool = "eraser"

        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            brush_size = min(50, brush_size + 1)
        if keys[pygame.K_MINUS]:
            brush_size = max(3, brush_size - 1)
        if keys[pygame.K_c]:
            canvas.fill(LIGHT_GRAY)
        if keys[pygame.K_s]:
            pygame.image.save(canvas, "my_drawing.png")
            print("✅ Рисунок сохранён как my_drawing.png")

        # Выбор цвета
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if 55 <= my <= 85:
                for i, c in enumerate(colors):
                    if 30 + i * 45 <= mx <= 68 + i * 45:
                        current_color = c

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()