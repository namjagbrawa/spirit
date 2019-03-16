from random import randint

from pygame import Surface, Vector2
from pytmx.util_pygame import load_pygame

from game_funcs import draw_background_with_tiled_map, load_alpha_image, create_random_heroes, create_random_stones, \
    initial_heroes, render_score_message
from settings import game_settings


class World(object):

    def __init__(self, screen):
        # 全部的精灵对象
        self.entities = {}
        # current entity id
        self.entity_id = 0
        self.hero_nums = {'green': 0, 'red': 0}
        # 能量石对象
        self.energy_stones = {}
        # 加载地图
        self.game_map = load_pygame(game_settings.MAP_DIR)
        self.background_layer = Surface(game_settings.SCREEN_SIZE).convert_alpha()
        self.player_layer = Surface(game_settings.SCREEN_SIZE).convert_alpha()
        self.player_layer.fill((0, 0, 0, 0))
        # initial double-side heroes
        draw_background_with_tiled_map(self.background_layer, self.game_map)
        screen.blit(self.background_layer, (0, 0))

        initial_heroes(self)

    def add_entity(self, entity):
        self.entities[self.entity_id] = entity
        entity.id = self.entity_id
        self.entity_id += 1
        self.hero_nums[entity.hero_type] += 1

    def remove_entity(self, entity):
        self.hero_nums[entity.hero_type] -= 1
        del self.entities[entity.id]

    def get(self, energy_id):
        if energy_id in self.entities:
            return self.entities[energy_id]
        return None

    def process(self, time_passed):
        time_passed_seconds = time_passed / 1000.0
        entities_copy = [entity for entity in self.entities.values()]
        for entity in entities_copy:
            entity.process(time_passed_seconds)

    def render(self, surface):
        surface.fill((255, 255, 255))
        self.player_layer.fill((0, 0, 0, 0))

        # render entities
        for entity in self.entities.values():
            entity.render(self.player_layer)

        for entity in self.energy_stones.values():
            entity.render(self.player_layer)

        render_score_message(self.player_layer)
        surface.blit(self.background_layer, (0, 0))
        surface.blit(self.player_layer, (0, 0))

    def get_close_entity(self, name, location, search_range=100.0):
        location = Vector2(*location)
        for entity in self.entities.values():
            if entity.name == name:
                distance = location.distance_to(entity.location)
                if distance < search_range:
                    return entity
        return None

    def get_close_energy(self, energy_type, location, search_range=100.0):
        location = Vector2(*location)
        for entity in self.energy_stones.values():
            if entity.energy_type == energy_type:
                distance = location.distance_to(entity.location)
                if distance < search_range:
                    return entity
        return None

    def get_energy_stone(self, energy_id):
        if energy_id in self.energy_stones.keys():
            return self.energy_stones[energy_id]
        return None

    def add_energy_stone(self, stone):
        self.energy_stones[self.entity_id] = stone
        stone.id = self.entity_id
        self.entity_id += 1

    def remove_energy_stone(self, stone):
        if stone in self.energy_stones.values():
            del self.energy_stones[stone.id]

    def min_hero_type(self):
        if self.hero_nums['red'] < self.hero_nums['green']:
            return 'red'
        return 'green'

    def random_emit(self):
        create_random_heroes(self)
        create_random_stones(self)
