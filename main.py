import pygame
import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

WIDTH = 800
HEIGHT = 600
FPS = 60


class Drone:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.radius = 12
        self.velocity = 0
        self.gravity = 0.5
        self.jump_force = -8
        self.alive = True

    def update(self):
        if self.alive:
            self.velocity += self.gravity
            self.y += self.velocity

    def jump(self):
        if self.alive:
            self.velocity = self.jump_force

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (0, 200, 255),
            (int(self.x), int(self.y)),
            self.radius
        )


class Corridor:
    def __init__(self, gap):
        self.gap = gap
        self.center = HEIGHT // 2
        self.speed = 4
        self.offset = 0

    def update(self):
        self.offset += self.speed
        if self.offset >= WIDTH:
            self.offset = 0

    def draw(self, screen):
        top = self.center - self.gap // 2
        bottom = self.center + self.gap // 2

        pygame.draw.line(screen, (255, 255, 255), (0, top), (WIDTH, top), 4)
        pygame.draw.line(screen, (255, 255, 255), (0, bottom), (WIDTH, bottom), 4)

        segment_width = 40
        spacing = 120

        x = -self.offset
        while x < WIDTH:
            pygame.draw.line(screen, (180, 180, 180), (x, top - 15), (x, top + 15), 3)
            pygame.draw.line(screen, (180, 180, 180), (x, bottom - 15), (x, bottom + 15), 3)
            x += spacing

    def collision(self, drone):
        top = self.center - self.gap // 2
        bottom = self.center + self.gap // 2

        return (
            drone.y - drone.radius <= top or
            drone.y + drone.radius >= bottom
        )


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 90
        self.finished = False

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.finished = True

    def draw(self, screen):

        progress = self.frame / self.max_frames
        radius = int(10 + progress * 50)

        pygame.draw.circle(screen, (255, 120, 0), (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), int(radius * 0.7))
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(radius * 0.35))

        for i in range(8):
            angle = i * (math.pi / 4) + self.frame * 0.1
            spark_x = self.x + math.cos(angle) * radius
            spark_y = self.y + math.sin(angle) * radius
            pygame.draw.circle(screen, (255, 220, 100), (int(spark_x), int(spark_y)), 4)


class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Летящий Дрон")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        menu = ttk.Frame(notebook)
        game = ttk.Frame(notebook)

        notebook.add(menu, text="Главное меню")
        notebook.add(game, text="Игровое поле")

        ttk.Label(menu, text="Ширина безопасного коридора").pack(pady=10)

        self.scale = tk.Scale(
            menu,
            from_=125,
            to=250,
            orient=tk.HORIZONTAL
        )
        self.scale.set(150)
        self.scale.pack()

        ttk.Button(
            menu,
            text="Старт",
            command=self.start_game
        ).pack(pady=20)

        self.root.mainloop()

    def start_game(self):
        pygame.init()

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Летящий Дрон")

        clock = pygame.time.Clock()

        drone = Drone()
        corridor = Corridor(self.scale.get())

        font = pygame.font.SysFont("Arial", 24)
        big_font = pygame.font.SysFont("Arial", 36)

        start_time = time.time()

        running = True
        exploded = False
        explosion = None
        end_time = None

        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and drone.alive:
                        drone.jump()

            if not exploded:
                drone.update()
                corridor.update()

                if corridor.collision(drone):
                    drone.alive = False
                    exploded = True
                    explosion = Explosion(drone.x, drone.y)
                    end_time = int(time.time() - start_time)

            else:
                explosion.update()
                if explosion.finished:
                    pygame.quit()
                    messagebox.showinfo(
                        "Игра окончена",
                        f"Время выживания: {end_time} сек."
                    )
                    return

            screen.fill((30, 30, 30))

            corridor.draw(screen)

            if not exploded:
                drone.draw(screen)
            else:
                explosion.draw(screen)

            timer = font.render(
                f"Время: {int(time.time() - start_time)}",
                True,
                (255, 255, 255)
            )
            screen.blit(timer, (10, 10))

            if exploded:
                text = big_font.render("СТОЛКНОВЕНИЕ!!!!! БУМ!!!!", True, (255, 80, 80))
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    GameApp()