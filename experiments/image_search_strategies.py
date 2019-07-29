import random

from core.ant import Ant, Chemicals, search_state_no_advoidance, \
    search_state_with_avoidance, search_with_avoidance_and_jumps, Nest
import matplotlib.pyplot as plt
import numpy as np


search_strategies = [
    search_state_no_advoidance,
    search_state_with_avoidance,
    search_with_avoidance_and_jumps
]


chemicals_to_plot = [
    'search',
    'food',
    'found'
]

WIDTH = 500
HALF_WIDTH = int(WIDTH / 2)
SIZE = (WIDTH, WIDTH)

n_ants = 20
n_ticks = 500


def build_ants(
    n_ants,
    size=SIZE,
    search_strategy=None,
    jump_distance=None,
    chemicals=None,
    nest=None,
):
    random.seed = 1
    ants = []
    if nest is None:
        nest = Nest(int(size[0]/2), int(size[1]/2))

    if chemicals is None:
        chemicals = Chemicals(size=size)

    for _ in range(n_ants):
        ant = Ant(
            nest=nest,
            chemicals=chemicals
        )
        if search_strategy:
            ant.search_strategy = search_strategy
        if jump_distance:
            ant.max_jump_distance=jump_distance
        ants.append(ant)

    return ants


def run(n_ticks, ants):
    nest = ants[0].nest
    for t in range(n_ticks):

        ants[0].chemicals.search[nest.x, nest.y] = 20
        ants[0].chemicals.found[nest.x, nest.y] = 0
        for ant in ants:
            ant.tick()
            ant.chemicals.food[16, 16] = 100
        ant.chemicals.tick()
        nest.tick()

        if t % 10 == 0:
            fig, axes = plt.subplots(2, 2)
            plot_chemicals(ants, axes)
            axes[1, 1].plot(nest.food_history)
            plt.savefig('images/{}'.format(t))


def plot_search(ants, ax):
    coverage = plot_chemical(ants, ax, chemical='search')

    first_ant = ants[0]
    ax.set_title(
        '{search_state} '
        'ants={n_ants}, '
        'ticks={n_ticks} '
        'coverage={coverage}'.format(
            search_state=first_ant.strategy.__class__.__name__,
            n_ants=n_ants,
            n_ticks=n_ticks,
            coverage=coverage
    ))


def plot_chemical(ants, ax, chemical='search'):
    first_ant = ants[0]
    chemical_array = getattr(first_ant.chemicals, chemical)
    # chemical_array[first_ant.nest.x, first_ant.nest.y] = 0
    image = ax.imshow(np.log10(chemical_array))
    # image = ax.imshow(chemical_array)
    coverage = np.count_nonzero(chemical_array) / chemical_array.size
    plt.colorbar(image, ax=ax)
    ax.set_title(chemical)
    return coverage


def plot_chemicals(ants, axes):
    for chemical, ax in zip(chemicals_to_plot, axes.flatten()):
        plot_chemical(ants, ax, chemical=chemical)


if __name__ == '__main__':

    fig, axes = plt.subplots(len(search_strategies))

    for strategy, ax in zip(search_strategies, axes):
        ants = build_ants(n_ants, strategy)
        run(n_ticks, ants)
        plot_search(ants, ax)
    plt.show()