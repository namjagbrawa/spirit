from random import randint

from pygame import Vector2

from settings import game_settings


class State(object):

    def __init__(self, name):
        self.name = name

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


class StateMachine(object):

    def __init__(self):
        self.states = {}
        self.active_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def think(self):
        if self.active_state is None:
            return

        self.active_state.do_actions()
        new_state_name = self.active_state.check_conditions()

        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()


HERO_STATES = (
    'exploring',
    'seeking',
    'fighting',
    'delivering',
    'kill'
)


class HeroStateExploring(State):

    def __init__(self, hero):
        State.__init__(self, HERO_STATES[0])
        self.hero = hero

    def random_destination(self):
        w, h = game_settings.SCREEN_SIZE
        self.hero.destination = Vector2(randint(60, w - 60), randint(60, h - 60))

    def do_actions(self):
        if randint(1, 20) == 1:
            self.random_destination()

    def check_conditions(self):
        location = self.hero.location
        world = self.hero.world

        enemy_type = self.hero.get_enemy_type()
        enemy = world.get_close_entity(enemy_type, location, game_settings.DEFAULT_SEARCH_RANGE)

        # exploring --> fighting
        if enemy is not None and location.distance_to(enemy.location) < 100.:
            self.hero.enemy_id = enemy.id
            return HERO_STATES[2]

        energy_stone = world.get_close_energy(self.hero.hero_type, self.hero.location)

        # exploring --> seeking
        if energy_stone is not None:
            self.hero.energy_id = energy_stone.id
            return HERO_STATES[1]

        return None

    def entry_actions(self):
        self.hero.speed = 120. + randint(-30, 30)
        self.random_destination()


class HeroStateSeeking(State):
    def __init__(self, hero):
        State.__init__(self, HERO_STATES[1])
        self.hero = hero
        self.energy_id = None

    def check_conditions(self):
        world = self.hero.world
        location = self.hero.location
        energy_stone = world.get_energy_stone(self.energy_id)

        if energy_stone is None:
            return HERO_STATES[0]

        if location.distance_to(energy_stone.location) < 5.0:
            self.hero.carry(energy_stone.image)
            self.hero.world.remove_energy_stone(energy_stone)
            return HERO_STATES[3]

        self.hero.destination = energy_stone.location
        return None

    def entry_actions(self):
        self.energy_id = self.hero.energy_id
        energy_stone = self.hero.world.get(self.energy_id)
        if energy_stone is not None:
            self.hero.destination = energy_stone.location
            self.hero.speed = 160. + randint(-20, 20)


class HeroStateFighting(State):
    def __init__(self, hero):
        State.__init__(self, HERO_STATES[2])
        self.hero = hero
        self.got_kill = False

    def do_actions(self):
        world = self.hero.world
        enemy = world.get(self.hero.enemy_id)
        if enemy is None:
            return

        self.hero.destination = enemy.location
        offset = self.hero.location.distance_to(enemy.location) < 15.
        random_seed = randint(1, 5) == 1

        if offset and random_seed:
            enemy.bitten()
            if enemy.health <= 0:
                enemy.dead()
                world.remove_entity(enemy)
                self.got_kill = True

    def check_conditions(self):
        if self.got_kill:
            if self.hero.health < game_settings.MAX_HEALTH * 0.8:
                self.hero.add_energy_score(5)
                return HERO_STATES[4]
            else:
                return HERO_STATES[0]

        enemy = self.hero.world.get(self.hero.enemy_id)

        if enemy is None:
            return HERO_STATES[0]

        if self.hero.health < 2 / 3 * game_settings.MAX_HEALTH:
            self.hero.destination = self.hero.get_home_location()
            return HERO_STATES[0]

        return None

    def entry_actions(self):
        self.hero.speed = 160. + randint(0, 50)

    def exit_actions(self):
        self.got_kill = False


class HeroStateDelivering(State):
    def __init__(self, hero):
        State.__init__(self, HERO_STATES[3])
        self.hero = hero

    def check_conditions(self):
        location = self.hero.location
        world = self.hero.world
        home_location = Vector2(*self.hero.get_home_location())
        distance_to_home = home_location.distance_to(location)

        if distance_to_home < game_settings.DROP_RANGE or not self.hero.in_center():
            if randint(1, 10) == 1:
                self.hero.add_energy_score(10)
                self.hero.drop(world.background_layer)
                return HERO_STATES[0]

        return None

    def entry_actions(self):
        home_location = Vector2(*self.hero.get_home_location())
        self.hero.speed = 60.0
        random_offset = Vector2(randint(-20, 20), randint(-20, 20))
        self.hero.destination = home_location + random_offset


class HeroKillPeopleGoHome(State):
    def __init__(self, hero):
        State.__init__(self, HERO_STATES[4])
        self.hero = hero

    def check_conditions(self):
        location = self.hero.location
        home_location = Vector2(*self.hero.get_home_location())
        distance_to_home = home_location.distance_to(location)

        if distance_to_home < game_settings.DROP_RANGE or not self.hero.in_center():
            if randint(1, 10) == 1:
                self.hero.health = game_settings.MAX_HEALTH
                return HERO_STATES[0]

        return None

    def entry_actions(self):
        home_location = Vector2(*self.hero.get_home_location())
        self.hero.speed = 60.0
        random_offset = Vector2(randint(-20, 20), randint(-20, 20))
        self.hero.destination = home_location + random_offset
