import pygame

from settings import game_settings
from world import World


def game_looper():
    game_exit = False

    pygame.init()
    game_screen = pygame.display.set_mode(game_settings.SCREEN_SIZE)

    game_world = World(game_screen)
    # random_create(game_world)
    clock = pygame.time.Clock()

    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True

        # game_world.render(game_screen)
        time_passed = clock.tick(100)

        game_world.random_emit()
        game_world.process(time_passed)
        game_world.render(game_screen)
        pygame.display.update()


if __name__ == '__main__':
    game_looper()
