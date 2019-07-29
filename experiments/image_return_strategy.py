import random

from core.ant import Ant, Chemicals, search_state_no_advoidance, \
    search_state_with_avoidance, search_with_avoidance_and_jumps, Nest, Location
import matplotlib.pyplot as plt
import numpy as np

from experiments.food import plot_chemicals
from experiments.image_search_strategies import build_ants, run, plot_search

search_strategies = [
    search_state_no_advoidance,
    search_state_with_avoidance,
    search_with_avoidance_and_jumps
]

WIDTH = 20
HALF_WIDTH = int(WIDTH / 2)
SIZE = (WIDTH, WIDTH)

n_ants = 1
n_ticks = 20

if __name__ == '__main__':

    fig, axes = plt.subplots(2, 2)

    ants = build_ants(n_ants, size=SIZE)
    first_ant = ants[0]
    first_ant.location = Location(15, 15)
    first_ant.food = 1

    run(n_ticks, ants)
    plot_chemicals(ants, axes)
    plt.show()