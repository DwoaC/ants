from collections import defaultdict

from core.ant import search_with_avoidance_and_jumps
from experiments.image_search_strategies import build_ants, run
import matplotlib.pyplot as plt
import numpy as np


def calc_coverage(jump_distance, size):
    ants = build_ants(
        n_ants=n_ants,
        size=size,
        search_strategy=search_with_avoidance_and_jumps,
        jump_distance=jump_distance
    )
    run(n_ticks, ants)
    search = ants[0].chemicals.search
    coverage = np.count_nonzero(search) / search.size
    return coverage


def plot_averages(jump_results, coverage_results):
    averages = defaultdict(int)
    for j, c in zip(jump_results, coverage_results):
        averages[j] += c
    jump_results = []
    coverage_results = []
    for j, c in averages.items():
        jump_results.append(j)
        coverage_results.append(c / repeats)
    ax.plot(
        jump_results,
        coverage_results
    )


if __name__ == '__main__':

    n_ants = 20
    jump_distances = range(1, 6, 1)
    fig, ax = plt.subplots(1)
    n_ticks = 20
    repeats = 10000
    size = (20, 20)

    coverage_results = []
    jump_results = []
    for jump_distance in jump_distances:
        for _ in range(repeats):
            coverage = calc_coverage(jump_distance, size=size)
            coverage_results.append(coverage)
            jump_results.append(jump_distance)

    # results = defaultdict(list)
    # for j, c in zip(jump_results, coverage_results):
    #     results[j].append(c)
    # ax.boxplot(list(results.values()))

    # ax.plot(
    #     jump_results,
    #     coverage_results,
    #     '*'
    # )
    plot_averages(jump_results, coverage_results)
    plt.show()