from unittest import TestCase
import unittest

from matplotlib import pyplot as plt

from core.ant import Ant, Location, Chemicals, DIRECTIONS, N, \
    SearchWithAvoidance, Nest, NW, return_state, gather_state
from experiments.image_search_strategies import plot_chemicals


class TestAnt(TestCase):

    def test_new_ant(self):

        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )
        self.assertEqual(ant.nest, Location(0, 0))
        self.assertEqual(ant.location, Location(0, 0))

    def test_ant_is_onre_step_away(self):

        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )

        ant.tick()

        self.assertIn(
            ant.distance_to_nest,
            (1, 2)
        )

    def test_ant_leaves_behind_search_chemical(self):

        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )
        ant.tick()

        self.assertAlmostEquals(
            0.975,
            ant.chemicals.search[0, 0],
            3
        )

    def test_ant_leaves_behind_found_chemical(self):
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )
        ant.location = Location(10, 10)
        ant.food = 1

        ant.tick()

        self.assertEqual(
            ant.chemicals.search[10, 10],
            0.0
        )
        self.assertAlmostEquals(
            0.975,
            ant.chemicals.found[10, 10],
            3
        )

    def test_ant_moves_home_if_it_has_food(self):
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )
        ant.food = 1
        ant.last_direction = NW
        ant.location = Location(10, 10)
        ant.chemicals.search[9, 9] = 1.0

        ant.tick()

        self.assertEqual(
            Location(9, 9),
            ant.location,
        )

    def test_ants_should_avoid_existing_search_traces(self):
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=Chemicals()
        )
        ant.chemicals.search += 1.0
        ant.chemicals.search[N.x, N.y] = 0.0
        ant.last_direction = N
        ant.search_strategy = SearchWithAvoidance()

        ant.tick()

        self.assertEqual(
            N,
            ant.location
        )

    def test_when_an_ant_encouters_food_pick_up_food(self):
        chemicals = Chemicals()
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=chemicals
        )
        ant.location = Location(1, 1)
        chemicals.food[1, 1] = 1

        ant.tick()

        self.assertTrue(ant.has_food)

    def test_when_an_ant_encouters_food_pick_up_at_most_1_food(self):
        chemicals = Chemicals()
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=chemicals
        )
        ant.x = 1
        ant.y = 1
        chemicals.food[1, 1] = 0.5

        ant.tick()

        self.assertEqual(ant.food, 0.5)

    def test_when_an_ant_encouters_food_pick_up_at_most_1_food_extra(self):
        chemicals = Chemicals()
        ant = Ant(
            nest=Nest(0, 0),
            chemicals=chemicals
        )
        ant.x = 1
        ant.y = 1
        chemicals.food[1, 1] = 1.5

        ant.tick()

        self.assertEqual(ant.food, 1.0)
        self.assertEqual(chemicals.food[1, 1], 0.5)

    def test_when_an_ant_has_food_has_arrives_home_he_drops_off_the_food_in_the_nest(self):
        chemicals = Chemicals()
        nest = Nest(0, 0)

        ant = Ant(
            nest=nest,
            chemicals=chemicals
        )
        ant.food = 1

        ant.tick()

        self.assertEqual(ant.food, 0.0)
        self.assertEqual(nest.food, 1.0)
        self.assertFalse(ant.has_food)

    @unittest.expectedFailure
    def test_if_returning_and_all_search_directions_are_the_same_move_away_from_found(self):
        chemicals = Chemicals()
        nest = Nest(0, 0)

        ant = Ant(
            nest=nest,
            chemicals=chemicals
        )
        ant.food = 1
        ant.last_direction = NW
        ant.location = Location(10, 10)
        chemicals.found[:, :] = 1
        chemicals.found[9, 9] = 0

        ant.tick()

        self.assertEqual(
            Location(9, 9),
            ant.location)

    def test_ants_can_all_get_home(self):
        chemicals = Chemicals(size=(10, 10))
        nest = Nest(0, 0)

        chemicals.search[0, 0] = 3
        chemicals.search[1, 1] = 2
        chemicals.search[2, 2] = 1

        ant_1 = Ant(
            nest=nest,
            chemicals=chemicals
        )
        ant_1.food = 1
        ant_1.last_direction = NW
        ant_1.location = Location(3, 3)

        for _ in range(3):
            ant_1.tick()
            self.assertIs(
                return_state,
                ant_1.strategy
            )

        self.assertEqual(
            Location(0, 0),
            ant_1.location
        )

        ant_2 = Ant(
            nest=nest,
            chemicals=chemicals
        )
        ant_2.food = 1
        ant_2.last_direction = NW
        ant_2.location = Location(3, 3)

        for _ in range(3):
            ant_1.tick()
            ant_2.tick()
            self.assertIs(
                return_state,
                ant_2.strategy
            )
            self.assertIs(
                gather_state,
                ant_1.strategy
            )

        self.assertEqual(
            Location(0, 0),
            ant_2.location
        )

        ant_3 = Ant(
            nest=nest,
            chemicals=chemicals
        )
        ant_3.food = 1
        ant_3.last_direction = NW
        ant_3.location = Location(3, 3)

        for _ in range(3):
            ant_1.tick()
            ant_2.tick()
            ant_3.tick()

        self.assertEqual(
            Location(0, 0),
            ant_3.location
        )

        # fig, axes = plt.subplots(2, 2)
        #
        # plot_chemicals([ant_1, ant_2, ant_3], axes)
        #
        # ant_3.tick()
        # axes[1, 1].plot(nest.food_history)
        # plt.show()

    def test_any_found_signal(self):
        chemicals = Chemicals(size=(10, 10))
        nest = Nest(0, 0)

        chemicals.found[1, 1] = 1

        ant = Ant(
            nest=nest,
            chemicals=chemicals
        )

        self.assertTrue(
            ant.any_found_signal
        )

    def test_(self):
        chemicals = Chemicals(size=(10, 10))
        nest = Nest(0, 0)

        chemicals.found[1, 1] = 1

        ant = Ant(
            nest=nest,
            chemicals=chemicals
        )

        self.assertTrue(
            ant.any_found_signal
        )


class TestChemicals(TestCase):

    def test_setting_a_chemical(self):
        chemicals = Chemicals()
        chemicals.search[9, 9] = 1.0

        self.assertEqual(
            chemicals.search[9, 9],
            1.0
        )

