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

from pyqubo import Binary, Spin, AddList, Mul, Add, Num, Placeholder, Constraint


class TestExpressEquality(unittest.TestCase):

    def test_equality_of_add_list(self):
        exp1 = AddList([Binary("a"), Binary("b")])
        exp2 = AddList([Binary("b"), Binary("a")])
        exp3 = AddList([Binary("a"), Binary("a")])
        self.assertTrue(exp1 == exp2)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertFalse(exp1 == exp3)
        self.assertFalse(exp1 == Binary("a"))

    def test_equality_of_add(self):
        exp1 = Add(Binary("a"), Binary("b"))
        exp2 = Add(Binary("b"), Binary("a"))
        exp3 = Add(Binary("a"), Binary("a"))
        exp4 = Add(Binary("a"), Binary("b"))
        exp5 = Add(Binary("a"), 1)
        self.assertTrue(exp1 == exp2)
        self.assertTrue(exp1 == exp4)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertTrue(exp1 != exp3)
        self.assertFalse(exp1 == exp5)
        self.assertFalse(exp1 == Binary("a"))
        self.assertFalse(exp1 == exp3)
        self.assertEqual(repr(exp1), "(Binary(a)+Binary(b))")

    def test_equality_of_mul(self):
        exp1 = Mul(Binary("a"), Binary("b"))
        exp2 = Mul(Binary("b"), Binary("a"))
        exp3 = Mul(Binary("a"), Binary("a"))
        self.assertTrue(exp1 == exp2)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertFalse(exp1 == exp3)
        self.assertTrue(exp1 != Binary("a"))

    def test_equality_of_num(self):
        self.assertTrue(Num(1) == Num(1))
        self.assertFalse(Num(1) == Num(2))
        self.assertFalse(Num(1) == Binary("a"))

    def test_equality_of_placeholder(self):
        p1 = Placeholder("p1")
        p2 = Placeholder("p2")
        p3 = Placeholder("p1")
        self.assertTrue(p1 == p3)
        self.assertTrue(hash(p1) == hash(p3))
        self.assertTrue(p1 != p2)
        self.assertTrue(p1 != Binary("a"))

    def test_equality_of_const(self):
        c1 = Constraint(Binary("a"), label="c1")
        c2 = Constraint(Binary("b"), label="c1")
        c3 = Constraint(Binary("a"), label="c3")
        c4 = Constraint(Binary("a"), label="c1")
        self.assertTrue(c1 == c4)
        self.assertFalse(c1 != c4)
        self.assertTrue(hash(c1) == hash(c4))
        self.assertTrue(c1 != c2)
        self.assertTrue(c1 != c3)
        self.assertTrue(c1 != Binary("a"))

    def test_equality_of_spin(self):
        a, b, c = Spin("a"), Spin("b"), Spin("a")
        self.assertTrue(a == c)
        self.assertFalse(a != c)
        self.assertTrue(hash(a) == hash(c))
        self.assertTrue(a != b)
        self.assertTrue(a != Binary("a"))
        self.assertEqual(repr(a), "Spin(a)")

    def test_equality_of_qbit(self):
        a, b, c = Binary("a"), Binary("b"), Binary("a")
        self.assertTrue(a == c)
        self.assertFalse(a != c)
        self.assertTrue(hash(a) == hash(c))
        self.assertTrue(a != b)
        self.assertTrue(a != Spin("a"))

    def test_equality_of_express(self):
        a, b = Binary("a"), Binary("b")
        exp = a * b + 2*a - 1
        expected_exp = AddList([Mul(a, b), Num(-1.0), Mul(a, 2)])
        self.assertTrue(exp == expected_exp)

    def test_equality_sub(self):
        a, b = Binary("a"), Binary("b")
        exp = 1-a-b
        expected_exp = AddList([Mul(a, -1), Num(1.0), Mul(b, -1)])
        self.assertTrue(exp == expected_exp)
        self.assertTrue(exp - 0.0 == expected_exp)

    def test_equality_sub2(self):
        a, b = Binary("a"), Binary("b")
        exp = a-b-1
        expected_exp = AddList([a, Num(-1.0), Mul(b, -1)])
        self.assertTrue(exp == expected_exp)

    def test_equality_of_express_with_placeholder(self):
        a, b, p = Binary("a"), Binary("b"), Placeholder("p")
        exp = a + b - 1 + a * p
        expected_exp = AddList([a, Num(-1.0), b, Mul(p, a)])
        self.assertTrue(exp == expected_exp)

    def test_equality_of_express_with_const(self):
        a, b = Binary("a"), Spin("b")
        exp = a + b - 1 + Constraint(a * b, label="const")
        expected_exp = AddList([a, Num(-1.0), b, Constraint(Mul(a, b), label="const")])
        self.assertTrue(exp == expected_exp)

    def test_repr(self):
        a, b, p = Binary("a"), Binary("b"), Placeholder("p")
        exp = a + p - 1 + Constraint(a * b, label="const")
        expected = "(Binary(a)+Placeholder(p)+Num(-1)+Const(const, (Binary(a)*Binary(b))))"
        self.assertTrue(repr(exp) == expected)

    def test_express_error(self):
        self.assertRaises(ValueError, lambda: 2 / Binary("a"))
        self.assertRaises(ValueError, lambda: Binary("a") / Binary("a"))
        self.assertRaises(ValueError, lambda: Binary("a") ** 1.5)
        self.assertRaises(ValueError, lambda: Mul(1, Binary("b")))
        self.assertRaises(ValueError, lambda: Add(1, Binary("b")))
