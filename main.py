import pygame
import sys
import time
from typing import Sequence

from levels import Level


SCREEN_WIDTH: int = 1366
SCREEN_HEIGHT: int = 768
SPRITE_SIZE: int = 32
GREEN = (95, 133, 117)
RED = (255, 69, 0)


def show_message(text: str, text_color: Sequence[int] = GREEN) -> None:
    """
    Show a black screen with text of the specified color in the center.

    :param text: text to display on the screen
    :param text_color: text color
    """
    pygame.font.init()
    my_font = pygame.font.SysFont("arial", 30)
    text_surface = my_font.render(text, True, text_color)
    screen.fill((0, 0, 0))
    text_center_coordinates = (
        SCREEN_WIDTH / 2 - text_surface.get_width() / 2,
        SCREEN_HEIGHT / 2 - text_surface.get_height() / 2
    )
    screen.blit(text_surface, text_center_coordinates)
    pygame.display.flip()
    time.sleep(1)


def play(level: Level) -> bool:
    """
    Run main loop for the level. Check win and loose conditions.

    :param level: instance of class Level
    :return: return 'True' if the level is completed and 'False' if the player is dead.
    """
    show_message(level.name, GREEN)
    time.sleep(1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Check win conditions
        if pygame.sprite.spritecollideany(level.player, level.exits):
            show_message(f"You've completed {level.name}.")
            return True

        # Check loose conditions
        if pygame.sprite.spritecollideany(level.player, level.traps):
            show_message("GAME OVER", RED)
            return False

        # Clear the screen
        screen.fill((0, 0, 0))
        # Draw all objects on the screen
        for entity in level.all_objects:
            screen.blit(entity.surf, entity.rect)

        pressed_keys = pygame.key.get_pressed()
        level.update(pressed_keys)

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=True)
    clock = pygame.time.Clock()

    # Files with level maps
    levels = ["maps/level1.txt", "maps/level2.txt"]
    # Load and play every level
    for i, file_name in enumerate(levels, start=1):
        # Move to the next level only if the current one is completed successfully.
        win = False
        while not win:
            current_level = Level(f"Level {i}", file_name, SPRITE_SIZE)
            win = play(current_level)

    # All levels are complete
    show_message("VICTORY! You've finished the game.")
    time.sleep(1)
    pygame.quit()
    sys.exit()
