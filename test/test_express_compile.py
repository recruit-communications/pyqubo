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

from pyqubo import Qbit, Spin, Param, Constraint, Vector, Matrix, Add, Sum
from pyqubo import assert_qubo_equal


class TestExpressCompile(unittest.TestCase):

    def compile_check(self, exp, expected_qubo, expected_offset, expected_structure,
                      params=None):
        model = exp.compile(strength=5)
        qubo, offset = model.to_qubo(params=params)
        assert_qubo_equal(qubo, expected_qubo)
        self.assertEqual(qubo, expected_qubo)
        self.assertEqual(offset, expected_offset)
        self.assertEqual(model.structure, expected_structure)

    def test_compile(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1 + a*b + a - 2
        expected_qubo = {('a', 'a'): 1.0, ('a', 'b'): 1.0, ('b', 'b'): 0.0}
        expected_offset = -1
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_expand(self):
        a, b = Qbit("a"), Qbit("b")
        exp = (a+b)*(a-b)
        expected_qubo = {('a', 'a'): 1.0, ('a', 'b'): 0.0, ('b', 'b'): -1.0}
        expected_offset = 0.0
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_spin(self):
        a, b = Qbit("a"), Spin("b")
        exp = a * b
        expected_qubo = {('a', 'a'): -1.0, ('a', 'b'): 2.0, ('b', 'b'): 0.0}
        expected_offset = 0.0
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_2nd_order(self):
        a, b = Qbit("a"), Qbit("b")
        exp = (Add(a, b)-3)**2
        expected_qubo = {('a', 'a'): -5.0, ('a', 'b'): 2.0, ('b', 'b'): -5.0}
        expected_offset = 9.0
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_3rd_order(self):
        a, b = Qbit("a"), Qbit("b")
        exp = (a+b-2)**3
        expected_qubo = {('a', 'a'): 7.0, ('a', 'b'): -6.0, ('b', 'b'): 7.0}
        expected_offset = -8.0
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_reduce_degree(self):
        a, b, c, d = Qbit("a"), Qbit("b"), Qbit("c"), Qbit("d")
        exp = a * b * c + b * c * d
        expected_qubo = {
            ('a', 'a'): 0.0,
            ('a', 'b*c'): 1.0,
            ('b', 'b'): 0.0,
            ('b', 'b*c'): -10.0,
            ('b', 'c'): 5.0,
            ('c', 'c'): 0.0,
            ('b*c', 'c'): -10.0,
            ('b*c', 'b*c'): 15.0,
            ('b*c', 'd'): 1.0,
            ('d', 'd'): 0.0}
        expected_offset = 0.0
        expected_structure = {'a': ('a',), 'b': ('b',), 'c': ('c',), 'd': ('d',)}

        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_div(self):
        a, b = Qbit("a"), Qbit("b")
        exp = (a+b-2)/2
        expected_qubo = {('a', 'a'): 0.5, ('b', 'b'): 0.5}
        expected_offset = -1
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_param(self):
        a, b, w, v = Qbit("a"), Qbit("b"), Param("w"), Param("v")
        exp = w*(a+b-2) + v
        expected_qubo = {('a', 'a'): 3.0, ('b', 'b'): 3.0}
        expected_offset = -1
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure,
                           params={"w": 3.0, "v": 5.0})

    def test_compile_param2(self):
        a, b, w, v = Qbit("a"), Qbit("b"), Param("w"), Param("v")
        exp = v*w*(a+b-2) + v
        expected_qubo = {('a', 'a'): 15.0, ('b', 'b'): 15.0}
        expected_offset = -25
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure,
                           params={"w": 3.0, "v": 5.0})

    def test_compile_param3(self):
        a, v = Qbit("a"), Param("v")
        exp = v*v*a + v
        expected_qubo = {('a', 'a'): 25.0}
        expected_offset = 5
        expected_structure = {'a': ('a',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure,
                           params={"v": 5.0})

    def test_compile_const(self):
        a, b, w = Qbit("a"), Qbit("b"), Param("w")
        exp = Constraint(Constraint(w * (a + b - 1), label="const1") + Constraint((a + b - 1) ** 2, label="const2"),
                         label="const_all")
        expected_qubo = {('a', 'a'): 2.0, ('a', 'b'): 2.0, ('b', 'b'): 2.0}
        expected_offset = -2.0
        expected_structure = {'a': ('a',), 'b': ('b',)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure,
                           params={"w": 3.0})

    def test_compile_vector(self):
        x = Vector("x", n_dim=5)
        a = Qbit("a")
        exp = x[1] * (x[0] + 2*a + 1)
        expected_qubo = {
            ('a', 'a'): 0.0,
            ('a', 'x[1]'): 2.0,
            ('x[0]', 'x[0]'): 0.0,
            ('x[0]', 'x[1]'): 1.0,
            ('x[1]', 'x[1]'): 1.0}
        expected_offset = 0.0
        expected_structure = {
             'a': ('a',),
             'x[0]': ('x', 0),
             'x[1]': ('x', 1),
             'x[2]': ('x', 2),
             'x[3]': ('x', 3),
             'x[4]': ('x', 4)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_vector_spin(self):
        x = Vector("x", n_dim=2, spin=True)
        exp = x[1] * x[0] + x[0]
        expected_qubo = {('x[1]', 'x[1]'): -2.0, ('x[0]', 'x[0]'): 0.0, ('x[0]', 'x[1]'): 4.0}
        expected_offset = 0.0
        expected_structure = {
             'x[0]': ('x', 0),
             'x[1]': ('x', 1)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_matrix(self):
        x = Matrix("x", n_row=2, n_col=2)
        a = Qbit("a")
        exp = x[0, 1] * (x[1, 1] + 2*a + 1)
        expected_qubo = {
          ('a', 'a'): 0.0,
          ('a', 'x[0][1]'): 2.0,
          ('x[0][1]', 'x[0][1]'): 1.0,
          ('x[0][1]', 'x[1][1]'): 1.0,
          ('x[1][1]', 'x[1][1]'): 0.0}
        expected_offset = 0.0
        expected_structure = {
             'a': ('a',),
             'x[0][0]': ('x', 0, 0),
             'x[0][1]': ('x', 0, 1),
             'x[1][0]': ('x', 1, 0),
             'x[1][1]': ('x', 1, 1)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_compile_matrix_spin(self):
        x = Matrix("x", 2, 2, spin=True)
        exp = x[1, 1] * x[0, 0] + x[0, 0]
        expected_qubo = {('x[1][1]', 'x[1][1]'): -2.0, ('x[0][0]', 'x[0][0]'): 0.0,
                         ('x[0][0]', 'x[1][1]'): 4.0}
        expected_offset = 0.0
        expected_structure = {
             'x[0][0]': ('x', 0, 0),
             'x[0][1]': ('x', 0, 1),
             'x[1][0]': ('x', 1, 0),
             'x[1][1]': ('x', 1, 1)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)

    def test_index_error_vector(self):
        x = Vector("x", n_dim=2)
        self.assertRaises(IndexError, lambda: x[2])

        x = Matrix("x", 2, 1)
        self.assertRaises(IndexError, lambda: x[2, 2])

    def test_sum(self):
        x = Vector('x', 2)
        exp = (Sum(0, 2, lambda i: x[i]) - 1) ** 2

        expected_qubo = {('x[0]', 'x[0]'): -1.0, ('x[1]', 'x[1]'): -1.0, ('x[0]', 'x[1]'): 2.0}
        expected_offset = 1.0
        expected_structure = {
             'x[0]': ('x', 0),
             'x[1]': ('x', 1)}
        self.compile_check(exp, expected_qubo, expected_offset, expected_structure)
