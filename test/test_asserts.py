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
from pyqubo import assert_qubo_equal


class TestAsserts(unittest.TestCase):

    def test_qubo_equal(self):
        qubo1 = {('a', 'b'): 1.0}
        qubo2 = {('b', 'a'): 1.0}
        qubo3 = {('a', 'b'): 2.0}
        qubo4 = {('b', 'a'): 2.0}
        qubo5 = {('c', 'a'): 1.0}

        assert_qubo_equal(qubo1, qubo2)
        self.assertRaises(AssertionError, lambda: assert_qubo_equal(qubo1, qubo3))
        self.assertRaises(AssertionError, lambda: assert_qubo_equal(qubo1, qubo4))
        self.assertRaises(AssertionError, lambda: assert_qubo_equal(qubo1, qubo5))
