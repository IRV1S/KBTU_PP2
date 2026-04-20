import pygame
import sys
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

# Папка с музыкой
music_folder = "music"
playlist = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
current_track = 0

def play_track(index):
    if playlist:
        pygame.mixer.music.load(os.path.join(music_folder, playlist[index]))
        pygame.mixer.music.play()

if playlist:
    play_track(current_track)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:      # Play
                pygame.mixer.music.unpause()
            elif event.key == pygame.K_s:    # Stop / Pause
                pygame.mixer.music.pause()
            elif event.key == pygame.K_n:    # Next
                current_track = (current_track + 1) % len(playlist)
                play_track(current_track)
            elif event.key == pygame.K_b:    # Back
                current_track = (current_track - 1) % len(playlist)
                play_track(current_track)
            elif event.key == pygame.K_q:    # Quit
                running = False

    screen.fill((30, 30, 30))

    # Заголовок
    title = font.render("Music Player", True, (0, 255, 0))
    screen.blit(title, (WIDTH//2 - 120, 50))

    # Текущий трек
    if playlist:
        track_text = small_font.render(f"Now playing: {playlist[current_track]}", True, (255, 255, 255))
        screen.blit(track_text, (50, 200))
    else:
        track_text = small_font.render("Положи mp3 файлы в папку music/", True, (255, 100, 100))
        screen.blit(track_text, (50, 200))

    # Управление
    controls = [
        "P - Play / Unpause",
        "S - Pause",
        "N - Next track",
        "B - Previous track",
        "Q - Quit"
    ]
    for i, text in enumerate(controls):
        txt = small_font.render(text, True, (200, 200, 200))
        screen.blit(txt, (50, 300 + i*40))

    pygame.display.flip()

pygame.quit()
sys.exit()