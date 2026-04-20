import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()

# Шарик
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_radius = 25
ball_speed = 20

WHITE = (255, 255, 255)
RED = (255, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ball_pos[0] -= ball_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ball_pos[0] += ball_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        ball_pos[1] -= ball_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        ball_pos[1] += ball_speed

    # Ограничение по краям
    ball_pos[0] = max(ball_radius, min(WIDTH - ball_radius, ball_pos[0]))
    ball_pos[1] = max(ball_radius, min(HEIGHT - ball_radius, ball_pos[1]))

    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, ball_pos, ball_radius)

    # Инструкция
    font = pygame.font.SysFont("Arial", 24)
    text = font.render("Используй стрелки или WASD", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()