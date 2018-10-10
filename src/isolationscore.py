"""
File created by Shashwat Sridhar on 10.10.2018.

This file consists of functions used in the calculation of isolation scores.
"""

import numpy as np
from itertools import combinations
import multiprocessing as mp


def similarity(x, y, lam, d0):
    """
    Calculates the similarity between two waveforms based on the following formula

                     /   /                    \          \
                     | _ | Euclidean Distance | * lambda |
                     |   | between waveforms  |          |
                     | __\____________________/_________ |
    similarity = exp |   /                          \    |
                     |   | Average distance between |    |
                     |   | waveforms in the unit    |    |
                     \   \                          /    /


    The function is used to calculate the value of the similarity
    between the two input waveforms. The Euclidean distance is a
    measure of the distance in n-dimensional space, where n is the
    dimensionality of the vectors x and y.

    Lambda controls how much the distance is "stretched", essentially
    allowing us to decide how much the similarity score should vary
    with small changes in the value of Euclidean distance.

    d0 normalizes the Euclidean distance, allowing for a measure
    that is independent of the units used.

    Input:

        x, y : waveforms of same dimension [list, array, int]
        lam  : value of lambda
        d0   : the d0 value for the unit in consideration

    Output:

        [Float] The value of the similarity between the two waveforms (between 0 and 1)
    """
    return np.exp((-np.linalg.norm(np.subtract(x, y))) * (lam / d0))


def calculate_d0(waves, pool):
    """
    Calculates the average Euclidean distance between waveforms in the given list of waveforms

    Takes a list of waves and calculates the Euclidean distance for
    every pair of waveforms in the list.

    WARNING: Computationally intensive step! For each additional nth
    waveform, n additional steps are added to the calculation.

    Input:

        waves: list of waveforms [list]
        pool: multiprocessing.Pool object to parallelize the job [mp.Pool object]

    Output:

        [Float] Value of d0 for the list of waves
    """
    summed_distance = 0.0
    number_of_pairs = len(waves) * (len(waves) - 1) * 0.5
    result_loop = [pool.apply_async(func=np.linalg.norm, args=(np.subtract(waves[comb[0]], waves[comb[1]]),))
                   for comb in combinations(range(0, len(waves)), 2)]
    summed_distance += np.sum([res.get() for res in result_loop])
    return np.divide(summed_distance, number_of_pairs)


def calculate_d0_loop(waves, pool):
    """
    Calculates the average Euclidean distance between waveforms in the given list of waveforms

    Takes a list of waves and calculates the Euclidean distance for
    every pair of waveforms in the list.

    WARNING: Computationally intensive step! For each additional nth
    waveform, n additional steps are added to the calculation.

    Input:

        waves: list of waveforms [list]
        pool: multiprocessing.Pool object to parallelize the job [mp.Pool object]

    Output:

        [Float] Value of d0 for the list of waves
    """
    number_of_pairs = len(waves) * (len(waves) - 1) * 0.5
    summed_distance = 0.0
    for i in range(len(waves)):
        results_loop = [pool.apply_async(func=np.linalg.norm, args=(np.subtract(waves[i], waves[k]),))
                        for k in range(i + 1, len(waves))]
        summed_distance += np.sum([res.get() for res in results_loop])
    return np.divide(summed_distance, number_of_pairs)


def calculate_isolation_scores(channel_number, block, lambda_value=10, speed=1):
    """
    Calculates the Isolation Scores for all units in the channel using the formula

                                        ________  ________
                                        \         \                similarity(X,Y)
                                         \         \           _______________________
                                1         \         \         ____
                         _______________   \         \        \    /                 \
    Isolation Score   =   | Number of |    /         /         \   | similarity(X,Z) |
                          | spikes in |   /         /          /   |                 |
                          |    unit   |  /         /          /___ \                 /
                                        /________ /_______   Z != X
                                          all X     all Y    (SUM1)
                                                   (SUM2)

    X AND Y LOOP OVER ALL WAVEFORMS IN ONE UNIT, Z IS LOOPED OVER EVERY WAVEFORM IN THE CHANNEL

    This function calculates the isolation score for each unit of a certain
    spike sorted channel (containing at least 2 spike-sorted units). The
    isolation score is a measure of how well separated one spike-sorted
    unit is from the rest of the units (and noise) in the channel. It uses
    the similarity function to determine the separation of the waveforms in
    n-dimensional space, where n is the dimensionality of each waveform
    vector.

    The lambda value controls how sensitive the function is to small
    differences in the waveforms. A lower value of lambda will generally
    result in smaller isolation scores, whereas very high values ( > 20)
    will lead to the isolation scores tending to 1.

    WARNING! The function is computationally very intensive! Use the "speed"
    argument to adjust how fast the function computes the scores (at
    significant loss of accuracy). A higher speed value results in faster
    computation.

    Input:

        **channel_number**: the channel for which the probability score is to be calculated [int]

        **lambda_value**: the value of lambda used in similarity scores [float]

        **block**: the block from which to extract the channel

        **speed**: speed of the function (higher is faster) [int]


    Output:

        list of the probability scores for each unit [list]
    """
    units = [unit for unit in block.channel_indexes[0].units
             if "noise" != unit.description.split()[-1]]  # To avoid the unit of noise

    units_without_unclassified = len([unit for unit in block.channel_indexes[0].units
                                      if "noise" not in unit.description.split() and
                                      "unclassified" not in unit.description.split()])

    if units_without_unclassified < 2:
        print("The selected channel must have at least two spike-sorted",
              "units to obtain a meaningful isolation score. The channel you have",
              "selected has only " + str(units_without_unclassified) + " spike sorted unit.")
        return 0
    else:
        sum_pool = mp.Pool(processes=mp.cpu_count())

        d0_values = np.zeros(len(units))

        for u, unit in enumerate(units):
            if "unclassified" not in unit.description.split():
                waves = [np.transpose(wf) for wf in unit.spiketrains[0].waveforms.magnitude][::speed]
                d0_values[u] = calculate_d0_loop(waves, sum_pool)

        isolation_scores = np.zeros(len(units))

        for u, unit in enumerate(units):
            if "unclassified" not in unit.description.split():
                sum1_all = np.zeros((len(unit.spiketrains[0].waveforms[::speed].magnitude)))
                sum2_all = np.zeros((len(unit.spiketrains[0].waveforms[::speed].magnitude)))

                for s, spike in enumerate(unit.spiketrains[0].waveforms[::speed].magnitude):

                    sum1 = 0.0
                    for vu, v_unit in enumerate(units):
                        results_1 = [
                            sum_pool.apply_async(func=similarity, args=(spike, v_spike, lambda_value, d0_values[u]))
                            for v_spike in v_unit.spiketrains[0].waveforms[::speed].magnitude]
                        sum1 += np.sum([res.get() for res in results_1])
                    sum1_all[s] = sum1 - similarity(spike, spike, lambda_value, d0_values[u])

                    sum2 = 0.0
                    results_2 = [
                        sum_pool.apply_async(func=similarity, args=(spike, w_spike, lambda_value, d0_values[u]))
                        for w_spike in unit.spiketrains[0].waveforms[::speed].magnitude]
                    sum2 += np.sum([res.get() for res in results_2])
                    sum2_all[s] = sum2 - similarity(spike, spike, lambda_value, d0_values[u])

                isolation_scores[u] = np.mean(np.true_divide(sum2_all, sum1_all))
        return isolation_scores
