import pygame
from pygame import Vector2
import random
from math import pi, tau, sin, cos
from enum import Enum

# Game constants
target_radius = 0.1
reticle_radius = 0.06667
start_color = (0, 128, 0)
end_color = (64, 128, 255)
max_hit_count = 50
min_speed = 1.5
max_speed = 4
min_min_offset = tau / 8
max_min_offset = tau / 4
min_max_offset = tau / 3
max_max_offset = tau / 2
hit_threshold = 0.16


def unit_vect(angle):
    return Vector2(cos(angle), sin(angle))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))


def modulus(x, m):
    return (x % m + m) % m


def angle_diff(a, b):
    return min(modulus(a - b, tau), modulus(b - a, tau))


class State(Enum):
    Start = 1
    Playing = 2
    Win = 3
    Lose = 4


class Game:
    def __init__(self):
        self.state = State.Start
        self.angle = random.uniform(0, tau)
        self.hits = 0
        self.pick_target()

    def dir(self):
        return self.hits % 2 * 2 - 1

    def progress(self):
        return self.hits / max_hit_count

    def pick_target(self):
        min_offset = lerp(max_min_offset, min_min_offset, self.progress())
        max_offset = lerp(max_max_offset, min_max_offset, self.progress())
        offset = random.uniform(min_offset, max_offset)
        self.target = modulus(self.angle + self.dir() * offset, tau)
        # print()
        # print(min_offset)
        # print(max_offset)
        # print(offset)
        # print(self.angle)
        # print(self.target)

    def space(self):
        """Handle space press"""
        match self.state:
            case State.Start | State.Win | State.Lose:
                self.__init__()
                self.state = State.Playing
            case State.Playing:
                print(angle_diff(self.angle, self.target))
                if angle_diff(self.angle, self.target) < hit_threshold:
                    self.hits += 1
                    if self.hits == max_hit_count:
                        self.state = State.Win
                    else:
                        self.pick_target()
                else:
                    self.state = State.Lose

    def render(self):
        """Render the game"""
        match self.state:
            case State.Start:
                screen.fill(start_color)
                screen.blit(text("Pop the Lock!", 64, "white"), (10, 100))
                screen.blit(text("Press SPACE to start", 48, "white"), (10, 300))
            case State.Playing:
                screen.fill(lerp_color(start_color, end_color, self.progress()))
                self.render_board()
                self.render_count()
            case State.Win:
                screen.fill(end_color)
                screen.blit(text("You Win!", 64, "white"), (10, 100))
                screen.blit(text("Press SPACE to play again", 48, "white"), (10, 300))
            case State.Lose:
                screen.fill("#f04040")
                self.render_board()
                self.render_count()
                screen.blit(text("Press SPACE to play again", 48, "white"), (10, 300))

    def render_count(self):
        screen_size = Vector2(screen.get_width(), screen.get_height())
        center = screen_size / 2
        count_text = text(str(self.hits), 64, "white")
        count_size = Vector2(count_text.get_width(), count_text.get_height())
        screen.blit(count_text, center - count_size / 2)

    def render_board(self):
        screen_size = Vector2(screen.get_width(), screen.get_height())
        center = screen_size / 2
        min_radius = min(screen_size.x, screen_size.y) / 2
        radius = min_radius * (1 - max(target_radius, reticle_radius))
        # Draw target
        pygame.draw.circle(
            screen,
            "#f0c020",
            center + unit_vect(self.target) * radius,
            target_radius * min_radius,
        )
        # Draw reticle
        pygame.draw.circle(
            screen,
            "white",
            center + unit_vect(self.angle) * radius,
            reticle_radius * min_radius,
        )

    def update(self, dt):
        if self.state == State.Playing:
            speed = lerp(min_speed, max_speed, self.progress())
            self.angle = modulus(self.angle + self.dir() * speed * dt, tau)


def text(str, size, color):
    """Create a text surface with a cached font"""
    if size not in text_dict:
        text_dict[size] = pygame.font.Font(pygame.font.get_default_font(), size)
    return text_dict[size].render(str, True, color)


text_dict = {}

# Initialization
pygame.init()
pygame.font.init()
pygame.display.set_caption("Pop the Lock")
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
game = Game()


running = True

# Main loop
while running:

    # Handle events
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        game.space()

    # Update
    game.update(clock.tick(60) / 1000)

    # Render
    game.render()
    pygame.display.flip()

pygame.quit()
