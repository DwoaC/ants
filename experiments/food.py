import random

import matplotlib.pyplot as plt
import numpy as np

from core.ant import Chemicals, Nest
from experiments.image_search_strategies import build_ants, run, plot_search, \
    plot_chemical, plot_chemicals



if __name__ == '__main__':
    random.seed = 1
    n_ants = 100
    n_ticks = 1000
    size = (40, 40)

    chemicals = Chemicals(size=size)
    nest = Nest(3, 3)
    # chemicals.search[nest.x, nest.y] = 1
    # chemicals.food[6:16, 6:16] = 1
    chemicals.food[16, 16] = 1
    ants = build_ants(
        n_ants=n_ants,
        size=size,
        chemicals=chemicals,
        nest=nest
    )
    run(n_ticks, ants)

    fig, axes = plt.subplots(2, 2)

    plot_chemicals(ants, axes)

    axes[1, 1].plot(nest.food_history)
    plt.show()
    print('/n'.join(str(a.strategy) for a in ants))