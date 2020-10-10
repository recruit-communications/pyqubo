from pyqubo import Array, Constraint, Placeholder
import logging
import time
import argparse
from timeout_decorator import timeout, TimeoutError
from memory_profiler import memory_usage


parser = argparse.ArgumentParser()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark_tsp")

def tsp_with_timeout(n_city, timeout_sec):

    @timeout(timeout_sec)
    def tsp(n_city):
        t0 = time.time()
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
        t1 = time.time()
        model = H.compile()
        qubo, offset = model.to_qubo(index_label=True, feed_dict={"A": 2.0})
        t2 = time.time()

        return t1-t0, t2-t1
    
    return tsp(n_city)


def measure(step, init_size, max_size, timeout):
    for n_city in range(init_size, max_size+step, step):
        try:
            max_memory, (express_time, compile_time) = memory_usage((tsp_with_timeout, (n_city, timeout)), max_usage=True, retval=True)
            logger.info("Memory usage is {} MB for n_city={}".format(max_memory, n_city))
            logger.info("Elapsed time is {} sec (expression: {} sec, compile: {} sec), for n_city={}".format(
                express_time+compile_time, express_time, compile_time, n_city))

        except TimeoutError as e:
            logger.error("TimeoutError: Elapsed time exceeded {} sec for n_city={}".format(timeout, n_city))
            break


if __name__=="__main__":
    parser.add_argument('-m', '--max_size', type=int)
    parser.add_argument('-i', '--init_size', type=int)
    parser.add_argument('-s', '--step', type=int)
    parser.add_argument('-t', '--timeout', type=int)
    args = parser.parse_args()
    measure(args.step, args.init_size, args.max_size, args.timeout)
