from pyqubo import Binary, Add, Num, Mul, Dog, DogAdd, WithPenalty, SubH
#from pyqubo import Binary, Add, Num, Mul
import unittest
import time
#from memory_profiler import profile
#from memory_profiler import memory_usage
import gc
import sys
from copy import copy


class TestExpressEquality(unittest.TestCase):
    
    def test_main3(self):
        t0 = time.time()
        n = 40
        H = Binary("a")
        for i in range(n):
            a = Binary("a")
            for j in range(n):
                b = Binary(f"b_{i}_{j}")
                a = a + b
            H = Add(H, Mul(a, a))
        
        for j in range(n):
            a = Binary("a")
            for i in range(n):
                b = Binary(f"b_{i}_{j}")
                a = a + b
            H = Add(H, Mul(a, a))

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    b1 = Binary(f"b_{i}_{j}")
                    b2 = Binary(f"b_{j}_{k}")
                    H = H + b1*b2

        model = H.compile(1.0)
        t1 = time.time()
        print("compile:", t1-t0)
        qubo, offset = model.to_qubo(False, {})
        #print(qubo, offset)
        t2 = time.time()
        print(t2-t1)
    
    def _test_main2(self):
        class CustomPenalty(WithPenalty):
            def __init__(self):
                WithPenalty.__init__(self)
                self.hamiltonian = Binary("a")
                self.penalty = Binary("b")

        custom_penalty = CustomPenalty()
        print(custom_penalty)
    
    def _test_main1(self):
        pass
        array_index = ArrayIndex("b", "array_name", (2, 2), [0, 0])
        a = Binary("a", array_index)
        array_index2 = ArrayIndex("b", "array_name", [2, 2], [0, 1])
        b = Binary("b", array_index2)
        model = (a+b).compile(1.0)
        print(model)
    
    def _test_main4(self):
        array_index = ArrayIndex("b", "array_name", [2, 2], [0, 0])
        h = Binary("b", array_index)
        subh = SubH(h, "label1")
        H = subh+Binary("a")
        model = H.compile(1)
        print(model)
        sol = model.decode_solutions([{"a": 1, "b": 1}], "BINARY", {})
        array = sol[0].arrays["array_name"]
        print("array.keys()", array.keys())
        print("array[0,0]", array[0, 0])

        class Sample:
            def __init__(self):
                pass
            def __getitem__(self, key):
                print(key)
        s = Sample()
        print(s[0])
        print(s[0:10])
        print(s[0:1,:])

if __name__ == '__main__':
    unittest.main()
