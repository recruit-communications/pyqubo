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

from pyqubo import Binary, AndConst, OrConst, XorConst, NotConst


class TestConstraint(unittest.TestCase):

    def test_not(self):
        a, b = Binary("a"), Binary("b")
        exp = NotConst(a, b, label="not")
        model = exp.compile()
        self.assertTrue(model.energy({"a": 1, "b": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 1}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 0, "b": 0}, vartype="BINARY") > 0)

    def test_and(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = AndConst(a, b, c, label="and")
        model = exp.compile()
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 0, "c": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 1, "c": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 0, "c": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 0}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 0, "b": 0, "c": 1}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 1, "b": 0, "c": 1}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 0, "b": 1, "c": 1}, vartype="BINARY") > 0)

    def test_or(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = OrConst(a, b, c, label="or")
        model = exp.compile()
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 0, "c": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 1, "c": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 0, "c": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 0}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 1, "b": 0, "c": 0}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 0, "b": 1, "c": 0}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 0, "b": 0, "c": 1}, vartype="BINARY") > 0)

    def test_xor(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = XorConst(a, b, c, label="xor")
        model = exp.compile()
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 0, "aux_xor": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 0, "c": 1, "aux_xor": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 1, "c": 1, "aux_xor": 0}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 0, "aux_xor": 1}, vartype="BINARY") == 0)
        self.assertTrue(model.energy({"a": 0, "b": 0, "c": 1, "aux_xor": 1}, vartype="BINARY") > 0)
        self.assertTrue(model.energy({"a": 1, "b": 1, "c": 1, "aux_xor": 1}, vartype="BINARY") > 0)

    def test_equality(self):
        xor1 = XorConst(Binary("a"), Binary("b"), Binary("c"), label="xor")
        xor2 = XorConst(Binary("a"), Binary("b"), Binary("c"), label="xor")
        xor3 = XorConst(Binary("b"), Binary("c"), Binary("a"), label="xor")
        or1 = OrConst(Binary("a"), Binary("b"), Binary("c"), label="xor")
        self.assertTrue(xor1 + 1 == xor2 + 1)
        self.assertTrue(xor1 == xor2)
        self.assertFalse(xor1 == or1)
        self.assertFalse(xor1 == xor3)
