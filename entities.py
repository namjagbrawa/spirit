from pygame import Vector2

from game_funcs import display_message
from settings import game_settings
from states import StateMachine, HeroStateExploring, HeroStateSeeking, HeroStateDelivering, HeroStateFighting, \
    HeroKillPeopleGoHome


# todo 加个国际医疗组织，负责给所有人治病

class Entity(object):
    def __init__(self, world, name, image):
        self.id = 0
        self.world = world
        self.name = name
        self.image = image
        self.location = Vector2(game_settings.SCREEN_WIDTH / 2, game_settings.SCREEN_HEIGHT / 2)
        self.destination = Vector2(0, 0)
        self.speed = 0.0
        self.brain = StateMachine()
        self.size = self.image.get_size()

    def render(self, surface):
        x, y = self.location
        w, h = self.size
        surface.blit(self.image, (x - w / 2, y - h / 2))

    def process(self, time_passed):
        self.brain.think()
        # move to destination
        if self.speed > 0.0 and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.length()
            heading = vec_to_destination.normalize()
            travel_distance = min(distance_to_destination, time_passed * self.speed * game_settings.SPEED_PERCENT)
            self.location += travel_distance * heading


class EnergyStone(Entity):

    def __init__(self, world, image, energy_type):
        super(EnergyStone, self).__init__("energy", world, image)
        self.energy_type = energy_type


class Hero(Entity):

    def __init__(self, world, image, dead_image, hero_type):
        super(Hero, self).__init__(world, "hero", image)
        self.dead_image = dead_image
        self.health = game_settings.MAX_HEALTH
        self.carry_energy_stone = None
        self.hero_type = hero_type
        exploring_state = HeroStateExploring(self)
        seeking_state = HeroStateSeeking(self)
        delivering_state = HeroStateDelivering(self)
        fighting = HeroStateFighting(self)
        kill = HeroKillPeopleGoHome(self)
        self.brain.add_state(exploring_state)
        self.brain.add_state(seeking_state)
        self.brain.add_state(delivering_state)
        self.brain.add_state(fighting)
        self.brain.add_state(kill)

    def carry(self, image):
        self.carry_energy_stone = image

    def drop(self, surface):
        if not self.carry_energy_stone:
            return
        self._draw_if_carry_energy(surface)
        self.carry_energy_stone = None

    def bitten(self):
        self.health -= 2
        self.speed = 140.

        if self.health <= 0:
            self.speed = 0.
            self.image = self.dead_image

    def dead(self):
        x, y = self.location
        w, h = self.image.get_size()
        background = self.world.background_layer
        background.blit(self.dead_image, (x - w, y - h / 2))

    def get_enemy_type(self):
        return 'red-hero' if self.hero_type == 'green' else 'green-hero'

    def in_center(self):
        return game_settings.RIGHT_HOME_LOCATION[0] > self.location.x > game_settings.LEFT_HOME_LOCATION[0]

    def get_home_location(self):
        if self.hero_type == 'green':
            return game_settings.LEFT_HOME_LOCATION
        return game_settings.RIGHT_HOME_LOCATION

    def add_energy_score(self, score):
        if self.hero_type == 'green':
            game_settings.left_score += score
        else:
            game_settings.right_score += score

    def render(self, surface):
        if self.health > 0:
            self._draw_health_number(surface)

        self._draw_state_machine(surface)
        Entity.render(self, surface)

        if not self.carry_energy_stone:
            return

        self._draw_if_carry_energy(surface)

    def _draw_if_carry_energy(self, surface):
        x, y = self.location
        w, h = self.carry_energy_stone.get_size()
        surface.blit(self.carry_energy_stone, (x - w, y - h / 2))

    def _draw_health_number(self, surface):
        x, y = self.location
        w, h = self.image.get_size()
        bar_x, bar_y = x - w / 2, y - h / 2 - 6

        surface.fill(game_settings.HEALTH_COLOR, (bar_x, bar_y, game_settings.MAX_HEALTH, 4))
        surface.fill(game_settings.HEALTH_COVER_COLOR, (bar_x, bar_y, self.health, 4))

    def _draw_state_machine(self, surface):
        x, y = self.location
        w, h = self.image.get_size()
        center = (x - w, y - h / 2 - 22)

        display_message(
            text=str(self.brain.active_state),
            color=(0, 0, 0),
            screen=surface,
            rect=center,
            size=22
        )
