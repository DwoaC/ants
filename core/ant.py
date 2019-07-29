import logging
import random
from collections import namedtuple

import numpy as np


logging.basicConfig()
logger = logging.getLogger(__name__)


class Location(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Location(
            self.x + other.x,
            self.y + other.y
        )

    def __sub__(self, other):
        return Location(
            self.x - other.x,
            self.y - other.y
        )

    def __eq__(self, other):
        return (
            self.x == other.x and
            self.y == other.y
        )

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            'x={self.x}, '
            'y={self.y}'
            ')'
        ).format(self=self)

    @property
    def location(self):
        return Location(self.x, self.y)

    @location.setter
    def location(self, location):
        self.x = location.x
        self.y = location.y

    def __hash__(self):
        return hash('{}_{}'.format(self.x, self.y))



N = Location(0, -1)
NE = Location(1, -1)
E = Location(1, 0)
SE = Location(1, 1)
S = Location(0, 1)
SW = Location(-1, 1)
W = Location(-1, 0)
NW = Location(-1, -1)


DIRECTIONS = [
    N, NE, E, SE,
    S, SW, W, NW
]

POSIBLE_DIRECTIONS = {
    N: [NW, N, NE],
    NE: [N, NE, E],
    E: [NE, E, SE],
    SE: [E, SE, S],
    S: [SE, S, SW],
    SW: [S, SW, W],
    W: [SW, W, NW],
    NW: [W, NW, N],
}

OBOSITE_DIRECTIONS = {
    N: S,
    S: N,
    NE: SW,
    SW: NE,
    E: W,
    W: E,
    SE: NW,
    NW: SE,
}

MAX_X = MAX_Y = 500

MAX_FOOD = 1.0
MAX_SEARCH = 200000
MAX_CHEMICAL_TIME = 40
MIN_CHEMICAL = 1 / MAX_CHEMICAL_TIME


class Chemicals(object):

    decay_rate = 0.001

    def __init__(self, size=(MAX_X, MAX_Y)):
        self.search = PeriodicLattice(np.zeros(size))
        self.found = PeriodicLattice(np.zeros(size))
        self.food = PeriodicLattice(np.zeros(size))

    def tick(self):
        self.search *= (1 - self.decay_rate)
        self.found *= (1 - self.decay_rate)

        self.search = np.clip(self.search, a_min=0.01, a_max=MAX_SEARCH)
        self.found = np.clip(self.found, a_min=0.01, a_max=MAX_SEARCH)


class HistoryAttr(object):

    def __init__(self, name):
        self.name = '_{}'.format(name)
        self.history_name = '{}_history'.format(name)

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        try:
            getattr(instance, self.history_name).append(value)
        except AttributeError:
            setattr(instance, self.history_name, [])
            getattr(instance, self.history_name).append(value)
        setattr(instance, self.name, value)


class Nest(Location):

    food = HistoryAttr('food')

    def __init__(self, x, y):
        super().__init__(x, y)
        self.food = 0

    def tick(self):
        self.food += 0


class Search(object):

    def move(self, ant):
        return self.find_highest_direction(
            ant,
            ant.chemicals.search
        )

    # def chemicals(self, ant):
    #     if ant.chemicals.search[
    #         ant.location.x,
    #         ant.location.y
    #     ] < self.found_chemical_amount(ant):
    #         self._add_search_chemical(ant)

    def chemicals(self, ant):
        self._add_search_chemical(ant)

    def find_highest_direction(self, ant, chemical):
        directions = self._find_highest_direction(ant, chemical)

        if not directions:
            directions = ant.posible_directions
        return random.choice(directions)

        # directions = [ant.location + d for d in ant.posible_directions]
        # return max(
        #     directions,
        #     key=lambda d: chemical[d.x, d.y]
        # ) - ant.location

    def find_lowest_exclude_zero_direction(self, ant, chemical):
        search_directions = self._find_lowest_exclude_zero_direction(
            ant,
            chemical=chemical
        )
        if search_directions:
            return random.choice(search_directions) - ant.location
        else:
            return random.choice(ant.posible_directions)

    def _find_lowest_exclude_zero_direction(self, ant, chemical):
        return self._find_lowest_direction(
            ant,
            chemical,
            filter_func=lambda v: v != 0
        )

    def _find_lowest_direction(self, ant, chemical, filter_func=None):
        directions = [ant.location + d for d in ant.posible_directions]
        values = [
            chemical[d.x, d.y] for
            d in directions
        ]
        if filter_func:
            values = list(filter(filter_func, values))

        if values:
            min_value = min(values)
            directions = [
                d for d in directions
                if chemical[d.x, d.y] == min_value
            ]
            return directions
        else:
            return []

    def _find_highest_direction(self, ant, chemical, filter_func=None):
        directions = [ant.location + d for d in ant.posible_directions]
        values = [
            chemical[d.x, d.y] for
            d in directions
        ]
        if filter_func:
            values = list(filter(filter_func, values))

        if values:
            max_value = max(values)
            directions = [
                d for d in directions
                if chemical[d.x, d.y] == max_value
            ]
            return [d - ant.location for d in directions]
        else:
            return []

    def find_lowest_search_direction(self, ant):
        directions = [ant.location + d for d in ant.posible_directions]
        values = [
            ant.chemicals.search[d.x, d.y] for
            d in directions
        ]
        if values:
            min_value = min(values)
            min_directions = [
                d for d in directions
                if ant.chemicals.search[d.x, d.y] == min_value
            ]
            return random.choice(min_directions) - ant.location
        else:
            return random.choice(ant.posible_directions)

    def _add_found_chemical(self, ant):
        ant.chemicals.found[
            ant.location.x-1:ant.location.x+2,
            ant.location.y-1:ant.location.y+2
        ] += 1.0

    def _remove_chemical_area(self, ant, chemical):
        chemical[
            ant.location.x-1:ant.location.x+2,
            ant.location.y-1:ant.location.y+2
        ] = 0

    def _remove_chemical(self, ant, chemical):
        chemical[
            ant.location.x,
            ant.location.y
        ] -= (MIN_CHEMICAL / 1000000)

    def _add_found_chemical(self, ant):
        ant.chemicals.found[
            ant.location.x,
            ant.location.y
        ] += self.found_chemical_amount(ant)

    def _add_search_chemical_area(self, ant):
        ant.chemicals.search[
            ant.location.x-1:ant.location.x+2,
            ant.location.y-1:ant.location.y+2
        ] += self.search_chemical_amount(ant)

    def _add_search_chemical(self, ant):
        ant.chemicals.search[
            ant.location.x,
            ant.location.y
        ] += self.search_chemical_amount(ant)

    def search_chemical_amount(self, ant):
        if ant.time_since_nest > MAX_CHEMICAL_TIME:
            return MIN_CHEMICAL
        else:
            return 1 - (ant.time_since_nest / MAX_CHEMICAL_TIME)

    def found_chemical_amount(self, ant):
        if ant.time_since_food > MAX_CHEMICAL_TIME:
            return MIN_CHEMICAL
        else:
            return 1 - (ant.time_since_food / MAX_CHEMICAL_TIME)

    def search_erase_amount(self, ant):
        if ant.time_since_food > MAX_CHEMICAL_TIME:
            return MIN_CHEMICAL
        else:
            return 1 - (ant.time_since_food / MAX_CHEMICAL_TIME)


class SearchWithoutAvoidance(Search):

    def move(self, ant):
        return random.choice(ant.posible_directions)


class SearchWithAvoidanceAndJumps(Search):

    def move(self, ant):
        if hasattr(ant, 'jump') and ant.jump > 1:
            # print('performing jump')
            ant.jump -= 1
            return ant.jump_direction
        else:
            dir = self.find_lowest_search_direction(ant)
            if self.should_jump(ant, dir):
                # print('starting jump')
                ant.jump_direction = dir
                ant.jump = ant.max_jump_distance
            return dir

    def should_jump(self, ant, dir):
        return ant.chemicals.search[dir.x, dir.y] >= 1


class SearchWithAvoidance(Search):

    def move(self, ant):
        return self.find_lowest_search_direction(ant)


class ReturnState(Search):

    def move(self, ant):
        if ant.time_since_food > 200000:
            direction = self.find_highest_direction(
                ant,
                ant.chemicals.search - ant.chemicals.found
            )
        else:
            direction = self.find_highest_direction(
                ant,
                ant.chemicals.search
            )
        return direction

    def chemicals(self, ant):
        if ant.time_since_food > 40:
            self._remove_chemical(ant, ant.chemicals.search)
        if ant.time_since_food < 100:

            self._add_found_chemical(ant)
            # self._remove_chemical(ant, ant.chemicals.search)


class GatherState(Search):
    def move(self, ant):
        direction = self.find_highest_direction(
            ant,
            ant.chemicals.found
        )

        return direction

    # def chemicals(self, ant):
    #     pass


search_state_with_avoidance = SearchWithAvoidance()
search_state_no_advoidance = SearchWithoutAvoidance()
search_with_avoidance_and_jumps = SearchWithAvoidanceAndJumps()

return_state = ReturnState()

gather_state = GatherState()


class Ant(Location):

    def __init__(self, nest, chemicals=None):
        super().__init__(nest.x, nest.y)
        self.nest = nest
        self.chemicals = chemicals
        self.food = 0
        self.search_strategy = search_state_with_avoidance
        self.return_strategy = return_state
        self.gather_strategy = gather_state
        self.max_jump_distance = 5
        self.previous_location = self.location
        self.last_direction = SE
        self.time_since_nest = 0
        self.time_since_food = 0

    @property
    def posible_directions(self):
        return POSIBLE_DIRECTIONS[self.last_direction]

    @property
    def strategy(self):
        if self.has_food:
            self.time_since_food += 1
            return self.return_strategy
        else:
            self.time_since_food = 0
            if self.any_found_signal:
                return self.gather_strategy
            else:
                return self.search_strategy

    @property
    def any_found_signal(self):
        result = 0
        for direction in self.posible_directions:
            result += self.chemicals.found[direction.x, direction.y]
        return bool(result)

    def tick(self):
        # if self.is_at_home:
        #     print('{}_{}'.format(self.is_at_home, self.has_food))
        if self.is_at_home and self.has_food:
            # print('drop food')
            self._drop_food()
            self.time_since_nest = 0
        else:
            self.time_since_nest += 1
            if not self.has_food:
                self._gather_food()
        self.strategy.chemicals(self)

        self.last_direction = self.strategy.move(self)

        self.location = self.location + self.last_direction

    @property
    def is_at_home(self):
        # return self.location == self.nest.location
        return self.distance_to_nest < 2

    def _drop_food(self):
        self.nest.food += self.food
        self.food = 0
        self.last_direction = OBOSITE_DIRECTIONS[self.last_direction]

    @property
    def has_food(self):
        return self.food > 0

    def _gather_food(self):

        food = self.chemicals.food[self.x, self.y]
        if food > 0:
            if food < MAX_FOOD:
                self.food = food
                self.chemicals.food[self.x, self.y] = 0
            else:
                self.food = MAX_FOOD
                self.chemicals.food[self.x, self.y] -= MAX_FOOD
            self.last_direction = OBOSITE_DIRECTIONS[self.last_direction]

    @property
    def distance_to_nest(self):
        return (
            abs(self.nest.x - self.location.x) +
            abs(self.nest.y - self.location.y)
        )

    def __repr__(self):
        return ''




class PeriodicLattice(np.ndarray):
    """Creates an n-dimensional ring that joins on boundaries w/ numpy

    Required Inputs
        array :: np.array :: n-dim numpy array to use wrap with

    Only currently supports single point selections wrapped around the boundary
    """
    def __new__(cls, input_array, lattice_spacing=None):
        """__new__ is called by numpy when and explicit constructor is used:
        obj = MySubClass(params) otherwise we must rely on __array_finalize
         """
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)

        # add the new attribute to the created instance
        obj.lattice_shape = input_array.shape
        obj.lattice_dim = len(input_array.shape)
        obj.lattice_spacing = lattice_spacing

        # Finally, we must return the newly created object:
        return obj

    def __getitem__(self, index):
        index = self.latticeWrapIdx(index)
        return super(PeriodicLattice, self).__getitem__(index)

    def __setitem__(self, index, item):
        index = self.latticeWrapIdx(index)
        return super(PeriodicLattice, self).__setitem__(index, item)

    def __array_finalize__(self, obj):
        """ ndarray.__new__ passes __array_finalize__ the new object,
        of our own class (self) as well as the object from which the view has been taken (obj).
        See
        http://docs.scipy.org/doc/numpy/user/basics.subclassing.html#simple-example-adding-an-extra-attribute-to-ndarray
        for more info
        """
        # ``self`` is a new object resulting from
        # ndarray.__new__(Periodic_Lattice, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. Periodic_Lattice():
        #   1. obj is None
        #       (we're in the middle of the Periodic_Lattice.__new__
        #       constructor, and self.info will be set when we return to
        #       Periodic_Lattice.__new__)
        if obj is None: return
        #   2. From view casting - e.g arr.view(Periodic_Lattice):
        #       obj is arr
        #       (type(obj) can be Periodic_Lattice)
        #   3. From new-from-template - e.g lattice[:3]
        #       type(obj) is Periodic_Lattice
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'spacing', because this
        # method sees all creation of default objects - with the
        # Periodic_Lattice.__new__ constructor, but also with
        # arr.view(Periodic_Lattice).
        #
        # These are in effect the default values from these operations
        self.lattice_shape = getattr(obj, 'lattice_shape', obj.shape)
        self.lattice_dim = getattr(obj, 'lattice_dim', len(obj.shape))
        self.lattice_spacing = getattr(obj, 'lattice_spacing', None)
        pass

    def latticeWrapIdx(self, index):
        """returns periodic lattice index
        for a given iterable index

        Required Inputs:
            index :: iterable :: one integer for each axis

        This is NOT compatible with slicing
        """
        if not hasattr(index, '__iter__'): return index         # handle integer slices
        if len(index) != len(self.lattice_shape): return index  # must reference a scalar
        if any(type(i) == slice for i in index): return index   # slices not supported
        if len(index) == len(self.lattice_shape):               # periodic indexing of scalars
            mod_index = tuple(( (i%s + s)%s for i,s in zip(index, self.lattice_shape)))
            return mod_index
        raise ValueError('Unexpected index: {}'.format(index))