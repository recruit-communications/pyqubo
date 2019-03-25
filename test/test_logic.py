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
import itertools
from pyqubo import Binary, And, Or, Not, Xor


class TestLogic(unittest.TestCase):

    def test_and(self):
        a, b = Binary('a'), Binary('b')
        exp = And(a, b)
        model = exp.compile()
        for a, b in itertools.product(*[(0, 1)] * 2):
            e = int(model.energy({'a': a, 'b': b}, vartype='BINARY'))
            self.assertEqual(a*b, e)

    def test_or(self):
        a, b = Binary('a'), Binary('b')
        exp = Or(a, b)
        model = exp.compile()
        for a, b in itertools.product(*[(0, 1)] * 2):
            e = int(model.energy({'a': a, 'b': b}, vartype='BINARY'))
            self.assertEqual(int(a+b > 0), e)

    def test_not(self):
        a = Binary('a')
        exp = Not(a)
        model = exp.compile()
        for a in [0, 1]:
            e = int(model.energy({'a': a}, vartype='BINARY'))
            self.assertEqual(1-a, e)

        self.assertEqual(repr(exp), "Not(((Binary(a)*Num(-1))+Num(1)))")

    def test_xor(self):
        a, b = Binary('a'), Binary('b')
        exp = Xor(a, b)
        model = exp.compile()
        for a, b in itertools.product(*[(0, 1)] * 2):
            e = int(model.energy({'a': a, 'b': b}, vartype='BINARY'))
            if (a == 1 and b == 0) or (a == 0 and b == 1):
                self.assertTrue(e == 1)
            else:
                self.assertTrue(e == 0)
