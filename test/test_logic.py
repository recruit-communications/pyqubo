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
from pyqubo import Qbit, And, Or, Not


class TestLogic(unittest.TestCase):

    def test_and(self):
        a, b = Qbit('a'), Qbit('b')
        exp = And(a, b)
        model = exp.compile()
        for a, b in itertools.product(*[(0, 1)] * 2):
            e = int(model.energy({'a': a, 'b': b}, var_type='binary'))
            self.assertEqual(a*b, e)

    def test_or(self):
        a, b = Qbit('a'), Qbit('b')
        exp = Or(a, b)
        model = exp.compile()
        for a, b in itertools.product(*[(0, 1)] * 2):
            e = int(model.energy({'a': a, 'b': b}, var_type='binary'))
            self.assertEqual(int(a+b > 0), e)

    def test_not(self):
        a = Qbit('a')
        exp = Not(a)
        model = exp.compile()
        for a in [0, 1]:
            e = int(model.energy({'a': a}, var_type='binary'))
            self.assertEqual(1-a, e)

        self.assertEqual(repr(exp), "Not(((Qbit(a)*Num(-1))+Num(1)))")
