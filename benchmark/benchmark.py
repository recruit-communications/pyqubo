from pyqubo import Array, Constraint, Placeholder
import logging
import time
import argparse
import numpy as np
from timeout_decorator import timeout, TimeoutError
from memory_profiler import memory_usage


parser = argparse.ArgumentParser()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark_tsp")


def number_partition_with_timeout(n, timeout_sec):

    @timeout(timeout_sec)
    def number_partition(n):
        t0 = time.time()
        s = Array.create('s', n, 'SPIN')
        numbers = np.random.randint(0, 10, n)
        H = sum([si * ni for si, ni in zip(s, numbers)])**2

        # Compile model
        t1 = time.time()
        model = H.compile()
        t2 = time.time()
        qubo, offset = model.to_qubo(index_label=False)
        t3 = time.time()
        print("len(qubo)", len(qubo))

        return t1-t0, t2-t1, t3-t2
    
    return number_partition(n)

def tsp_with_timeout(n_city, timeout_sec):

    @timeout(timeout_sec)
    def tsp(n_city):
        t0 = time.time()
        x = Array.create('c', (n_city, n_city), 'BINARY')
        use_for_loop=False

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
        feed_dict = {}
        
        if use_for_loop:
            distance = 0.0
            for i in range(n_city):
                for j in range(n_city):
                    for k in range(n_city):
                        # we set the constant distance
                        d_ij = 10
                        distance += d_ij * x[k, i] * x[(k + 1) % n_city, j]
                    
        else:
            distance = []
            for i in range(n_city):
                for j in range(n_city):
                    for k in range(n_city):
                        # we set the constant distance
                        d_ij = 10
                        distance.append(d_ij * x[k, i] * x[(k + 1) % n_city, j])
            distance = sum(distance)

        print("express done")
        
        # Construct hamiltonian
        A = Placeholder("A")
        H = distance

        feed_dict["A"] = 1.0

        # Compile model
        t1 = time.time()
        model = H.compile()
        t2 = time.time()
        qubo, offset = model.to_qubo(index_label=False, feed_dict=feed_dict)
        t3 = time.time()

        print("len(qubo)", len(qubo))

        return t1-t0, t2-t1, t3-t2
    
    return tsp(n_city)

 

def measure(problem, step, init_size, max_size, timeout):
    if problem == "tsp":
        f = tsp_with_timeout
    elif problem == "number_partition":
        f = number_partition_with_timeout
    
    for n in range(init_size, max_size+step, step):
        try:
            max_memory, (express_time, compile_time, to_qubo_time) = memory_usage((f, (n, timeout)), max_usage=True, retval=True)
            logger.info("Memory usage is {} MB for n={}".format(max_memory, n))
            logger.info("Elapsed time is {} sec (expression: {} sec, compile: {} sec, to_qubo {} sec), for n={}".format(
                express_time+compile_time+to_qubo_time, express_time, compile_time, to_qubo_time, n))

        except TimeoutError as e:
            logger.error("TimeoutError: Elapsed time exceeded {} sec for n_city={}".format(timeout, n))
            break


if __name__=="__main__":
    parser.add_argument('-p', '--problem', type=str)
    parser.add_argument('-m', '--max_size', type=int)
    parser.add_argument('-i', '--init_size', type=int)
    parser.add_argument('-s', '--step', type=int)
    parser.add_argument('-t', '--timeout', type=int)
    args = parser.parse_args()
    #number_partition_with_timeout(2000, timeout_sec=10)
    measure(args.problem, args.step, args.init_size, args.max_size, args.timeout)
