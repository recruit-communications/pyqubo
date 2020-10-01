from pyqubo import Array, Constraint, Placeholder
import logging
import time
import argparse

parser = argparse.ArgumentParser()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark_tsp")


def tsp(n_city):
    x = Array.create('c', (n_city, n_city), 'BINARY')

    # Constraint not to visit more than two cities at the same time.
    time_const = 0.0
    for i in range(n_city):
        # If you wrap the hamiltonian by Const(...), this part is recognized as constraint
        time_const += Constraint((sum(x[i, j] for j in range(n_city)) - 1)**2, label="time{}".format(i))

    # Constraint not to visit the same city more than twice.
    city_const = 0.0
    for j in range(n_city):
        city_const += Constraint((sum(x[i, j] for i in range(n_city)) - 1)**2, label="city{}".format(j))
    
    # distance of route
    distance = 0.0
    for i in range(n_city):
        for j in range(n_city):
            for k in range(n_city):
                # we set the constant distance
                d_ij = 10
                distance += d_ij * x[k, i] * x[(k+1)%n_city, j]
    
    # Construct hamiltonian
    A = Placeholder("A")
    H = distance + A * (time_const + city_const)

    # Compile model
    t0 = time.time()
    model = H.compile()
    t1 = time.time()

    qubo, offset = model.to_qubo(index_label=True, feed_dict={"A": 2.0})
    t2 = time.time()

    logger.info("compile time: {}, to_qubo time: {}".format(t1-t0, t2-t1))
    return


if __name__=="__main__":
    parser.add_argument('-n', '--n_city', type=int)
    args = parser.parse_args()
    tsp(args.n_city)
