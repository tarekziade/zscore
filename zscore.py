"""
Right now, raptor cold page load tests are based on running 25 times
the same test and looking at the median value. This big number
will make outliers have a small impact on the final result,
but forces us to run 25 browser cycles, which is time
and resource consuming. If we can reduce that number, it
will have a positive impact by reducing tests duration
(XXX measure how much).

My new proposal is to do only 8 samples and check the zscore
of the results to detect outliers in that series. If we
find outliers, we discard them and replace them with new
measures until we don't have any. If we reach 25 cycles
we just do the usual median on the 25 series.

In order to validate or invalidate this new technique,
we'll add a new metrics in raptor runs that will simply
run the algorithm on existing 25 series and add the new
metrics alonside the old one, so we can compare them
in a span of a few weeks in treeherder.

If the results are following the same trend (the baseline
will be a bit different, but we want to make sure we have
comparable trends) we can drop the 25 cycles and implement that
new technique.

For a first test, I worked on the loadtime value, using a
zscore of 1.7 for the threshold of outliers.
"""
from math import sqrt

s = [
    594,
    507,
    523,
    519,
    400,
    384,
    412,
    385,
    419,
    418,
    403,
    385,
    395,
    421,
    404,
    401,
    422,
    400,
    399,
    450,
    452,
    403,
    389,
    423,
    409,
]

s2 = [
    596,
    218,
    229,
    221,
    226,
    211,
    218,
    223,
    226,
    223,
    222,
    221,
    226,
    223,
    210,
    217,
    210,
    217,
    224,
    219,
    214,
    239,
    208,
    224,
    209,
]


weird = [
    820,
    1527,
    328,
    535,
    408,
    585,
    497,
    509,
    544,
    1612,
    495,
    477,
    474,
    881,
    701,
    582,
    958,
    757,
    748,
    753,
    538,
    925,
    1715,
    4463,
    940,
]

s3 = [
    823,
    1534,
    330,
    571,
    409,
    397,
    352,
    399,
    373,
    423,
    325,
    403,
    448,
    392,
    495,
    430,
    593,
    499,
    3716,
    336,
    309,
    386,
    311,
    321,
    322,
]

s4 = [
    599,
    515,
    519,
    526,
    421,
    388,
    417,
    427,
    431,
    402,
    450,
    408,
    400,
    449,
    435,
    429,
    392,
    409,
    509,
    406,
    385,
    383,
    437,
    398,
    429,
]

all = [s, s2, s3, s4, weird]


def median(series):
    series = sorted(series)
    if len(series) % 2:
        return series[len(series) / 2]
    else:
        middle = len(series) / 2  # the higher of the middle 2, actually
        return 0.5 * (series[middle - 1] + series[middle])


def zscore(series):
    sum_sq = x_bar = 0
    for i, val in enumerate(series):
        x_bar += val
        sum_sq += val * val
    n = 1 + i
    x_bar *= 1.0 / n
    std = sqrt(1.0 / i * sum_sq - (float(n) / i) * x_bar * x_bar)

    def zscore(v):
        res = abs((v - x_bar) / std)
        return res

    return [zscore(v) for v in series]


def progressive(series):
    i = 8
    initial = sorted(series[:i])
    perms = 0

    while True:
        scores = sorted(zip(zscore(initial), initial))
        outliers = []
        for c, score in enumerate(scores):
            z = score[0]
            if z > 1.7:
                # outlier
                outliers.append(score[1])
        if len(outliers) == 0:
            break
        new = []
        for c, v in enumerate(initial):
            if v in outliers:
                perms += 1
                continue
            new.append(v)
        for x in range(len(outliers)):
            if i > len(series) - 1:
                # we reached the end
                print("Failed")
                return median(series)
            new.append(series[i])
            i += 1
        initial = new
    print("permutations %d" % perms)
    return median(initial)


for r in all:
    print("Progressive %d" % progressive(r))
    print("Median %d" % median(r))
    print("")
    print("")
