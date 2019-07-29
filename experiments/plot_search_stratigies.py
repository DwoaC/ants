from experiments.image_search_strategies import search_strategies, build_ants, run
import matplotlib.pyplot as plt
import numpy as np


if __name__ == '__main__':

    n_ants = 2
    n_ticks_list = np.logspace(1, 3, 100)
    fig, ax = plt.subplots(1)

    for strategy in search_strategies:
        coverage_results = []
        for n_ticks in n_ticks_list:
            n_ticks = int(n_ticks)
            ants = build_ants(n_ants, strategy)
            run(n_ticks, ants)

            search = ants[0].chemicals.search
            coverage = np.count_nonzero(search) / search.size
            coverage_results.append(coverage)
        ax.loglog(
            n_ticks_list,
            coverage_results,
            label=strategy.__class__.__name__
        )
    plt.legend()
    plt.show()