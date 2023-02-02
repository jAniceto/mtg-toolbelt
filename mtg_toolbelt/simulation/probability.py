import math


def hypergeom_prob(pop, succ_pop, sample, succ_sample):
    return math.comb(succ_pop, succ_sample) * math.comb(pop - succ_pop, sample - succ_sample) / math.comb(pop, sample)


def cum_hypergeom_prob(pop, succ_pop, sample, succ_sample):
    cum_prob = 0
    for succ in range(0, succ_sample + 1):
        cum_prob += math.comb(succ_pop, succ) * math.comb(pop - succ_pop, sample - succ) / math.comb(pop, sample)
    return cum_prob


if __name__ == '__main__':
    # Tests
    [pop, succ_pop, sample, succ_sample] = [60, 18, 7, 2]

    # Hypergeometric probability
    prob = hypergeom_prob(pop, succ_pop, sample, succ_sample)
    print(f"P(x = k) = {prob:.4f}")

    # Cumulative hypergeometric probability
    prob = cum_hypergeom_prob(pop, succ_pop, sample, succ_sample)
    print(f"P(x <= k) = {prob:.4f}")

    prob = 1 - cum_hypergeom_prob(pop, succ_pop, sample, succ_sample - 1)
    print(f"P(x >= k) = {prob:.4f}")
