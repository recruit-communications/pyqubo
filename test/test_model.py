# Copyright 2018 Recruit Communications Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from pyqubo import Binary, Constraint, Placeholder, Array
from pyqubo import assert_qubo_equal


class TestModel(unittest.TestCase):

    def test_to_qubo(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo()
        assert_qubo_equal(qubo, {("a", "a"): 1.0, ("a", "b"): 1.0, ("b", "b"): 0.0})
        self.assertTrue(offset == -1)

    def test_to_qubo_with_index(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo(index_label=True)
        assert_qubo_equal(qubo, {(0, 0): 1.0, (0, 1): 1.0, (1, 1): 0.0})
        self.assertTrue(offset == -1)

    def test_to_ising(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising()
        self.assertTrue(linear == {'a': 0.75, 'b': 0.25})
        assert_qubo_equal(quad, {('a', 'b'): 0.25})
        self.assertTrue(offset == -0.25)

    def test_to_ising_with_index(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising(index_label=True)
        self.assertTrue(linear == {0: 0.75, 1: 0.25})
        assert_qubo_equal(quad, {(0, 1): 0.25})
        self.assertTrue(offset == -0.25)

    def test_decode(self):
        x = Array.create("x", (2, 2), vartype="BINARY")
        exp = Constraint((x[1, 1] - x[0, 1]) ** 2, label="const")
        model = exp.compile()

        # check __repr__ of CompiledQubo
        expected_repr = "CompiledQubo({('x[0][1]', 'x[0][1]'): 1.0,\n" \
            " ('x[0][1]', 'x[1][1]'): -2.0,\n" \
            " ('x[1][1]', 'x[1][1]'): 1.0}, offset=0.0)"
        self.assertEqual(repr(model.compiled_qubo), expected_repr)

        # check __repr__ of Model
        expected_repr = "Model(CompiledQubo({('x[0][1]', 'x[0][1]'): 1.0,\n"\
                        " ('x[0][1]', 'x[1][1]'): -2.0,\n"\
                        " ('x[1][1]', 'x[1][1]'): 1.0}, offset=0.0), "\
                        "structure={'x[0][1]': ('x', 0, 1), 'x[1][1]': ('x', 1, 1)})"
        self.assertEqual(repr(model), expected_repr)

        # when the constraint is not broken

        # type of solution is dict[label, bit]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 1.0, 'x[1][1]': 1.0},
                                                            vartype="BINARY")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # type of solution is list[bit]
        decoded_sol, broken, energy = model.decode_solution([1, 1], vartype="BINARY")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # type of solution is dict[index_label(int), bit]
        decoded_sol, broken, energy = model.decode_solution({0: 1.0, 1: 1.0},
                                                            vartype="BINARY")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # when the constraint is broken

        # type of solution is dict[label, bit]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 0.0, 'x[1][1]': 1.0},
                                                            vartype="BINARY")
        self.assertTrue(decoded_sol == {'x': {0: {1: 0}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 1)
        self.assertTrue(energy == 1)

        # invalid solution
        self.assertRaises(ValueError, lambda: model.decode_solution([1, 1, 1], vartype="BINARY"))
        self.assertRaises(ValueError, lambda: model.decode_solution(
            {'x[0][2]': 1.0, 'x[1][1]': 0.0}, vartype="BINARY"))
        self.assertRaises(TypeError, lambda: model.decode_solution((1, 1), vartype="BINARY"))

        # type of solution is dict[label, spin]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 1.0, 'x[1][1]': -1.0},
                                                            vartype="SPIN")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: -1}}})
        self.assertTrue(len(broken) == 1)
        self.assertTrue(energy == 1)

    def test_decode2(self):
        x = Array.create("x", (2, 2), vartype="BINARY")
        exp = Constraint(-(x[1, 1] - x[0, 1]) ** 2, label="const")
        model = exp.compile()
        self.assertRaises(ValueError, lambda: model.decode_solution([1, 0], vartype="BINARY"))

    def test_work_with_dimod(self):
        import numpy as np
        import dimod
        n = 10
        A = [np.random.randint(-50, 50) for _ in range(n)]
        S = Array.create('S', n, "BINARY")
        H = sum(A[i] * S[i] for i in range(n)) ** 2
        model = H.compile()
        binary_bqm = model.to_dimod_bqm()
        sa = dimod.reference.SimulatedAnnealingSampler()
        response = sa.sample(binary_bqm, num_reads=10, num_sweeps=5)
        decoded_solutions = model.decode_dimod_response(response, topk=2)
        for (decoded_solution, broken, energy) in decoded_solutions:
            assert isinstance(decoded_solution, dict)
            assert isinstance(broken, dict)
            assert isinstance(energy, float)

        spin_bqm = binary_bqm.change_vartype(dimod.SPIN)
        response = sa.sample(spin_bqm, num_reads=10, num_sweeps=5)
        decoded_solutions = model.decode_dimod_response(response, topk=2)
        for (decoded_solution, broken, energy) in decoded_solutions:
            assert isinstance(decoded_solution, dict)
            assert isinstance(broken, dict)
            assert isinstance(energy, float)

    def test_placeholders(self):
        a, b, p = Binary("a"), Binary("b"), Placeholder("p")
        feed_dict = {'p': 2.0}
        exp = p * (1 + a * b + a)
        model = exp.compile()
        qubo, offset = model.to_qubo(index_label=False, feed_dict=feed_dict)
        dict_solution = {'a': 1, 'b': 0}
        dict_energy = model.energy(dict_solution, vartype="BINARY", feed_dict=feed_dict)
        list_solution = [1, 0]
        list_energy = model.energy(list_solution, vartype="BINARY", feed_dict=feed_dict)
        assert_qubo_equal(qubo, {('a', 'b'): 2.0, ('a', 'a'): 2.0, ('b', 'b'): 0.0})
        self.assertEqual(offset, 2.0)
        self.assertTrue(dict_energy, 2.0)
        self.assertTrue(list_energy, 2.0)

        # Test that `decode_dimod_response` accepts the `feed_dict` arg
        import numpy as np
        import dimod
        n = 10
        p = Placeholder("p")
        feed_dict = {'p': 2}
        A = [np.random.randint(-50, 50) for _ in range(n)]
        S = Array.create('S', n, "BINARY")
        H = sum(p * A[i] * S[i] for i in range(n)) ** 2
        model = H.compile()
        binary_bqm = model.to_dimod_bqm(feed_dict=feed_dict)
        sa = dimod.reference.SimulatedAnnealingSampler()
        response = sa.sample(binary_bqm, num_reads=10, num_sweeps=5)
        # Confirm that decode_dimod_response() accecpts a feed_dict. Test of accuracy delegated to decode_solution()
        decoded_solutions = model.decode_dimod_response(response, topk=2, feed_dict=feed_dict)
        for (decoded_solution, broken, energy) in decoded_solutions:
            assert isinstance(decoded_solution, dict)
            assert isinstance(broken, dict)
            assert isinstance(energy, float)

    def test_placeholder_in_constraint(self):
        a = Binary("a")
        exp = Constraint(2 * Placeholder("c") + a, "const1")
        m = exp.compile()
        sol, broken, energy = m.decode_solution({"a": 1}, vartype="BINARY", feed_dict={"c": 1})
        self.assertEqual(energy, 3.0)
        self.assertEqual(broken, {'const1': {'result': {'a': 1}, 'penalty': 3.0}})
        self.assertEqual(sol, {'a': 1})

if __name__ == '__main__':
    unittest.main()
