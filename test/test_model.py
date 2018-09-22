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

from pyqubo import Qbit, Matrix, Constraint, Param, Vector
from pyqubo import assert_qubo_equal


class TestModel(unittest.TestCase):

    def test_to_qubo(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo()
        assert_qubo_equal(qubo, {("a", "a"): 1.0, ("a", "b"): 1.0, ("b", "b"): 0.0})
        self.assertTrue(offset == -1)

    def test_to_qubo_with_index(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo(index_label=True)
        assert_qubo_equal(qubo, {(0, 0): 1.0, (0, 1): 1.0, (1, 1): 0.0})
        self.assertTrue(offset == -1)

    def test_to_ising(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising()
        self.assertTrue(linear == {'a': 0.75, 'b': 0.25})
        assert_qubo_equal(quad, {('a', 'b'): 0.25})
        self.assertTrue(offset == -0.25)

    def test_to_ising_with_index(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising(index_label=True)
        self.assertTrue(linear == {0: 0.75, 1: 0.25})
        assert_qubo_equal(quad, {(0, 1): 0.25})
        self.assertTrue(offset == -0.25)

    def test_decode(self):
        x = Matrix("x", n_row=2, n_col=2)
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
                        "structure={'x[0][0]': ('x', 0, 0),\n"\
                        " 'x[0][1]': ('x', 0, 1),\n"\
                        " 'x[1][0]': ('x', 1, 0),\n"\
                        " 'x[1][1]': ('x', 1, 1)})"
        self.assertEqual(repr(model), expected_repr)

        # when the constraint is not broken

        # type of solution is dict[label, bit]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 1.0, 'x[1][1]': 1.0},
                                                            var_type="binary")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # type of solution is list[bit]
        decoded_sol, broken, energy = model.decode_solution([1, 1], var_type="binary")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # type of solution is dict[index_label(int), bit]
        decoded_sol, broken, energy = model.decode_solution({0: 1.0, 1: 1.0},
                                                            var_type="binary")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 0)
        self.assertTrue(energy == 0)

        # when the constraint is broken

        # type of solution is dict[label, bit]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 0.0, 'x[1][1]': 1.0},
                                                            var_type="binary")
        self.assertTrue(decoded_sol == {'x': {0: {1: 0}, 1: {1: 1}}})
        self.assertTrue(len(broken) == 1)
        self.assertTrue(energy == 1)

        # type of solution is dict[label, spin]
        decoded_sol, broken, energy = model.decode_solution({'x[0][1]': 1.0, 'x[1][1]': -1.0},
                                                            var_type="spin")
        self.assertTrue(decoded_sol == {'x': {0: {1: 1}, 1: {1: -1}}})
        self.assertTrue(len(broken) == 1)
        self.assertTrue(energy == 1)

        # invalid solution
        self.assertRaises(ValueError, lambda: model.decode_solution([1, 1, 1], var_type="binary"))
        self.assertRaises(ValueError, lambda: model.decode_solution(
            {'x[0][2]': 1.0, 'x[1][1]': 0.0}, var_type="binary"))
        self.assertRaises(TypeError, lambda: model.decode_solution((1, 1), var_type="binary"))

        # invalid var_type
        self.assertRaises(AssertionError, lambda: model.decode_solution([1, 1], var_type="sp"))

    def test_decode2(self):
        x = Matrix("x", n_row=2, n_col=2)
        exp = Constraint(-(x[1, 1] - x[0, 1]) ** 2, label="const")
        model = exp.compile()
        self.assertRaises(ValueError, lambda: model.decode_solution([1, 0], var_type="binary"))

    def test_work_with_dimod(self):
        import numpy as np
        import dimod
        n = 10
        A = [np.random.randint(-50, 50) for _ in range(n)]
        S = Vector('S', n)
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

    def test_params(self):
        a, b, p = Qbit("a"), Qbit("b"), Param("p")
        params = {'p': 2.0}
        exp = p * (1 + a * b + a)
        model = exp.compile()
        qubo, offset = model.to_qubo(index_label=False, params=params)
        dict_solution = {'a': 1, 'b': 0}
        dict_energy = model.energy(dict_solution, var_type="binary", params=params)
        list_solution = [1, 0]
        list_energy = model.energy(list_solution, var_type="binary", params=params)
        assert_qubo_equal(qubo, {('a', 'b'): 2.0, ('a', 'a'): 2.0, ('b', 'b'): 0.0})
        self.assertEqual(offset, 2.0)
        self.assertTrue(dict_energy, 2.0)
        self.assertTrue(list_energy, 2.0)
