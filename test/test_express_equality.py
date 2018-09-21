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

from pyqubo import Qbit, Spin, AddList, Mul, Add, Num, Param, Constraint


class TestExpressEquality(unittest.TestCase):

    def test_equality_of_add_list(self):
        exp1 = AddList([Qbit("a"), Qbit("b")])
        exp2 = AddList([Qbit("b"), Qbit("a")])
        exp3 = AddList([Qbit("a"), Qbit("a")])
        self.assertTrue(exp1 == exp2)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertFalse(exp1 == exp3)
        self.assertFalse(exp1 == Qbit("a"))

    def test_equality_of_add(self):
        exp1 = Add(Qbit("a"), Qbit("b"))
        exp2 = Add(Qbit("b"), Qbit("a"))
        exp3 = Add(Qbit("a"), Qbit("a"))
        exp4 = Add(Qbit("a"), Qbit("b"))
        exp5 = Add(Qbit("a"), 1)
        self.assertTrue(exp1 == exp2)
        self.assertTrue(exp1 == exp4)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertTrue(exp1 != exp3)
        self.assertFalse(exp1 == exp5)
        self.assertFalse(exp1 == Qbit("a"))
        self.assertFalse(exp1 == exp3)
        self.assertEqual(repr(exp1), "(Qbit(a)+Qbit(b))")

    def test_equality_of_mul(self):
        exp1 = Mul(Qbit("a"), Qbit("b"))
        exp2 = Mul(Qbit("b"), Qbit("a"))
        exp3 = Mul(Qbit("a"), Qbit("a"))
        self.assertTrue(exp1 == exp2)
        self.assertTrue(hash(exp1) == hash(exp2))
        self.assertFalse(exp1 == exp3)
        self.assertTrue(exp1 != Qbit("a"))

    def test_equality_of_num(self):
        self.assertTrue(Num(1) == Num(1))
        self.assertFalse(Num(1) == Num(2))
        self.assertFalse(Num(1) == Qbit("a"))

    def test_equality_of_param(self):
        p1 = Param("p1")
        p2 = Param("p2")
        p3 = Param("p1")
        self.assertTrue(p1 == p3)
        self.assertTrue(hash(p1) == hash(p3))
        self.assertTrue(p1 != p2)
        self.assertTrue(p1 != Qbit("a"))

    def test_equality_of_const(self):
        c1 = Constraint(Qbit("a"), label="c1")
        c2 = Constraint(Qbit("b"), label="c1")
        c3 = Constraint(Qbit("a"), label="c3")
        c4 = Constraint(Qbit("a"), label="c1")
        self.assertTrue(c1 == c4)
        self.assertFalse(c1 != c4)
        self.assertTrue(hash(c1) == hash(c4))
        self.assertTrue(c1 != c2)
        self.assertTrue(c1 != c3)
        self.assertTrue(c1 != Qbit("a"))

    def test_equality_of_spin(self):
        a, b, c = Spin("a"), Spin("b"), Spin("a")
        self.assertTrue(a == c)
        self.assertFalse(a != c)
        self.assertTrue(hash(a) == hash(c))
        self.assertTrue(a != b)
        self.assertTrue(a != Qbit("a"))
        self.assertEqual(repr(a), "Spin(a)")

    def test_equality_of_qbit(self):
        a, b, c = Qbit("a"), Qbit("b"), Qbit("a")
        self.assertTrue(a == c)
        self.assertFalse(a != c)
        self.assertTrue(hash(a) == hash(c))
        self.assertTrue(a != b)
        self.assertTrue(a != Spin("a"))

    def test_equality_of_express(self):
        a, b = Qbit("a"), Qbit("b")
        exp = a * b + 2*a - 1
        expected_exp = AddList([Mul(a, b), Num(-1.0), Mul(a, 2)])
        self.assertTrue(exp == expected_exp)

    def test_equality_sub(self):
        a, b = Qbit("a"), Qbit("b")
        exp = 1-a-b
        expected_exp = AddList([Mul(a, -1), Num(1.0), Mul(b, -1)])
        self.assertTrue(exp == expected_exp)
        self.assertTrue(exp - 0.0 == expected_exp)

    def test_equality_sub2(self):
        a, b = Qbit("a"), Qbit("b")
        exp = a-b-1
        expected_exp = AddList([a, Num(-1.0), Mul(b, -1)])
        self.assertTrue(exp == expected_exp)

    def test_equality_of_express_with_param(self):
        a, b, p = Qbit("a"), Qbit("b"), Param("p")
        exp = a + b - 1 + a * p
        expected_exp = AddList([a, Num(-1.0), b, Mul(p, a)])
        self.assertTrue(exp == expected_exp)

    def test_equality_of_express_with_const(self):
        a, b = Qbit("a"), Spin("b")
        exp = a + b - 1 + Constraint(a * b, label="const")
        expected_exp = AddList([a, Num(-1.0), b, Constraint(Mul(a, b), label="const")])
        self.assertTrue(exp == expected_exp)

    def test_repr(self):
        a, b, p = Qbit("a"), Qbit("b"), Param("p")
        exp = a + p - 1 + Constraint(a * b, label="const")
        expected = "(Qbit(a)+Param(p)+Num(-1)+Const(const, (Qbit(a)*Qbit(b))))"
        self.assertTrue(repr(exp) == expected)

    def test_express_error(self):
        self.assertRaises(ValueError, lambda: 2 / Qbit("a"))
        self.assertRaises(ValueError, lambda: Qbit("a") / Qbit("a"))
        self.assertRaises(ValueError, lambda: Qbit("a") ** 1.5)
        self.assertRaises(ValueError, lambda: Mul(1, Qbit("b")))
        self.assertRaises(ValueError, lambda: Add(1, Qbit("b")))
