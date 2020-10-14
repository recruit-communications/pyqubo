import unittest
from pyqubo import Binary, Spin, Add, Num, Mul, WithPenalty, SubH, Constraint, assert_qubo_equal, Placeholder


class TestExpress(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(Binary("a"), Binary("a"))
        self.assertNotEqual(Binary("a"), Binary("b"))

        exp1 = Binary("a") + 2
        exp2 = Binary("a") + 2
        exp3 = Binary("b") + 2
        self.assertEqual(exp1, exp2)
        self.assertNotEqual(exp1, exp3)

        mul1 = Placeholder("p") * Binary("b")
        mul2 = Placeholder("p") * Binary("b")
        mul3 = Placeholder("p") * Binary("a")
        self.assertEqual(mul1, mul2)
        self.assertNotEqual(mul1, mul3)

        class CustomPenalty(WithPenalty):
            def __init__(self, hamiltonian, penalty, label="label"):
                super().__init__(hamiltonian, penalty, label)
        
        a, b = Binary("a"), Binary("b")
        p1 = 1 + CustomPenalty(a+b, a*b)
        p2 = 1 + CustomPenalty(a+b, a*b)
        p3 = 1 + CustomPenalty(a*b, a+b)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        
        subh1 = SubH(a+b, label="c1")
        subh2 = SubH(a+b, label="c1")
        subh3 = SubH(a+b, label="c2")
        self.assertEqual(subh1, subh2)
        self.assertNotEqual(subh1, subh3)


    def compile_check(self, exp, expected_qubo, expected_offset, feed_dict={}):
        model = exp.compile(strength=5)
        qubo, offset = model.to_qubo(feed_dict=feed_dict)
        assert_qubo_equal(qubo, expected_qubo)
        self.assertEqual(offset, expected_offset)

    def test_compile_binary(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a*b + a - 2
        expected_qubo = {('a', 'a'): 1.0, ('a', 'b'): 1.0, ('b', 'b'): 0.0}
        expected_offset = -1
        self.compile_check(exp, expected_qubo, expected_offset)
    
    def test_compile_spin(self):
        exp = 2*(Spin("a") - Binary("b"))
        expected_qubo = {('a', 'a'): 4.0, ('b', 'b'): -2.0}
        expected_offset = -2.0
        self.compile_check(exp, expected_qubo, expected_offset)
    
    def test_compile_expand_add(self):
        a, b = Binary("a"), Binary("b")
        exp = (a+b)*(a-b)
        expected_qubo = {('a', 'a'): 1.0, ('a', 'b'): 0.0, ('b', 'b'): -1.0}
        expected_offset = 0.0
        self.compile_check(exp, expected_qubo, expected_offset)
    
    def test_compile_div(self):
        a, b = Binary("a"), Binary("b")
        exp = a*b / 2 + 1
        expected_qubo = {('a', 'a'): 0.0, ('a', 'b'): 0.5, ('b', 'b'): 0.0}
        expected_offset = 1.0
        q, offset = exp.compile().to_qubo()
        self.compile_check(exp, expected_qubo, expected_offset)

    def test_compile_power(self):
        a, b = Binary("a"), Binary("b")
        exp = (a+b)**3
        expected_qubo = {('a', 'a'): 1.0, ('a', 'b'): 6.0, ('b', 'b'): 1.0}
        expected_offset = 0.0
        q, offset = exp.compile().to_qubo()
        self.compile_check(exp, expected_qubo, expected_offset)
    
    def test_compile_neg(self):
        exp = -Binary("a")
        expected_qubo = {('a', 'a'): -1.0}
        expected_offset = 0.0
        self.compile_check(exp, expected_qubo, expected_offset)
    
    def test_compile_placeholder(self):
        a, b = Binary("a"), Binary("b")
        p, q, r = Placeholder("p"), Placeholder("q"), Placeholder("r")
        exp = r*(q*p*(a+b)**2 + q)
        expected_qubo = {('a', 'a'): 12.0, ('a', 'b'): 24.0, ('b', 'b'): 12.0}
        expected_offset = 4
        feed_dict={"p": 3, "q": 2, "r": 2}
        q, offset = exp.compile().to_qubo(feed_dict=feed_dict)
        self.compile_check(exp, expected_qubo, expected_offset, feed_dict)
    
    def test_compile_subh(self):
        a, b = Binary("a"), Binary("b")
        p = Placeholder("p")
        exp = p * SubH((a+b-1)**2, label="subh") + a*b
        expected_qubo = {('a', 'a'): -3.0, ('a', 'b'): 7.0, ('b', 'b'): -3.0}
        expected_offset = 3
        feed_dict={"p": 3}
        self.compile_check(exp, expected_qubo, expected_offset, feed_dict)
    
    def test_compile_constraint(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = Constraint(a*b*c, label="constraint")
        expected_qubo = {('a', '0*1'): -10.0, ('b', '0*1'): -10.0, ('0*1', '0*1'): 15.0, ('a', 'a'): 0.0, ('a', 'b'): 5.0, ('c', '0*1'): 1.0, ('b', 'b'): 0.0, ('c', 'c'): 0.0}
        expected_offset = 0
        self.compile_check(exp, expected_qubo, expected_offset, feed_dict={})
        

    def test_compile_with_penalty(self):
        class CustomPenalty(WithPenalty):
            def __init__(self, hamiltonian, penalty, label):
                super().__init__(hamiltonian, penalty, label)

        a, b = Binary("a"), Binary("b")
        p = Placeholder("p")
        custom_penalty = p * CustomPenalty(a+b, a*b, "label")
        expected_qubo = {('a', 'a'): 2.0, ('a', 'b'): 1.0, ('b', 'b'): 2.0}
        expected_offset = 0.0
        feed_dict={"p": 2}
        self.compile_check(custom_penalty, expected_qubo, expected_offset, feed_dict)
    
if __name__ == '__main__':
    unittest.main()
