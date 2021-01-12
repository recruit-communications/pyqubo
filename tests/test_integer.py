# Copyright 2020 Recruit Communications Co., Ltd.
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
from pyqubo import OneHotEncInteger, OrderEncInteger, Placeholder, LogEncInteger, UnaryEncInteger
import dimod
from pyqubo import assert_qubo_equal


class TestInteger(unittest.TestCase):

    def test_one_hot_enc_integer(self):
        a = OneHotEncInteger("a", (0, 4), strength=Placeholder("s"))
        H = (a - 3) ** 2
        model = H.compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        sampleset = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(
            sampleset, feed_dict={"s": 10.0})
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"]==3)
        self.assertTrue(a.value_range == (0, 4))

        expected_q = {('a[0]', 'a[1]'): 20.0,
             ('a[0]', 'a[2]'): 20.0,
             ('a[0]', 'a[3]'): 20.0,
             ('a[0]', 'a[4]'): 20.0,
             ('a[1]', 'a[2]'): 24.0,
             ('a[1]', 'a[3]'): 26.0,
             ('a[1]', 'a[4]'): 28.0,
             ('a[2]', 'a[3]'): 32.0,
             ('a[2]', 'a[4]'): 36.0,
             ('a[3]', 'a[4]'): 44.0,
             ('a[0]', 'a[0]'): -10.0,
             ('a[1]', 'a[1]'): -15.0,
             ('a[2]', 'a[2]'): -18.0,
             ('a[3]', 'a[3]'): -19.0,
             ('a[4]', 'a[4]'): -18.0}
        expected_offset = 19
        assert_qubo_equal(q, expected_q)
        self.assertTrue(offset == expected_offset)        

    def test_one_hot_enc_integer_equal(self):
        a = OneHotEncInteger("a", (0, 4), strength=Placeholder("s"))
        b = OneHotEncInteger("b", (0, 4), strength=Placeholder("s"))
        M = 2.0
        H = (a + b - 5) ** 2 + M*(a.equal_to(3)-1)**2
        model = H.compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        sampleset = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(
            sampleset, feed_dict={"s": 10.0})
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"]==3)
        self.assertTrue(best.subh["b"]==2)
        self.assertTrue(best.subh["a_const"]==0)
        self.assertTrue(best.subh["b_const"]==0)
        self.assertEqual(len(best.constraints(only_broken=True)), 0)
    
    def test_order_enc_integer(self):
        a = OrderEncInteger("a", (0, 4), strength=Placeholder("s"))
        model = ((a - 3) ** 2).compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        expected_q = {
            ('a[3]', 'a[2]'): -8.0,
            ('a[0]', 'a[1]'): -8.0,
            ('a[3]', 'a[0]'): 2.0,
            ('a[2]', 'a[0]'): 2.0,
            ('a[1]', 'a[1]'): 5.0,
            ('a[3]', 'a[1]'): 2.0,
            ('a[2]', 'a[1]'): -8.0,
            ('a[3]', 'a[3]'): 5.0,
            ('a[0]', 'a[0]'): -5.0,
            ('a[2]', 'a[2]'): 5.0
        }
        response = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(
            response, feed_dict={"s": 10.0})
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"]==3)
        self.assertTrue(a.value_range == (0, 4))
        assert_qubo_equal(q, expected_q)
    
    def test_order_enc_integer_more_than(self):
        a = OrderEncInteger("a", (0, 4), strength=5.0)
        b = OrderEncInteger("b", (0, 4), strength=5.0)
        model = ((a - b) ** 2 + (1 - a.more_than(1)) ** 2 + (1 - b.less_than(3)) ** 2).compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(sampleset)
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"]==2)
        self.assertTrue(best.subh["b"]==2)

    def test_log_enc_integer(self):
        a = LogEncInteger("a", (0, 4))
        b = LogEncInteger("b", (0, 4))
        M = 2.0
        H = (2 * a - b - 1) ** 2 + M * (a + b - 5) ** 2
        model = H.compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(sampleset)
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"] == 2)
        self.assertTrue(best.subh["b"] == 3)
        self.assertTrue(a.value_range == (0, 4))
        self.assertTrue(b.value_range == (0, 4))


    def test_unary_enc_integer(self):
        a = UnaryEncInteger("a", (0, 3))
        b = UnaryEncInteger("b", (0, 3))
        M = 2.0
        H = (2 * a - b - 1) ** 2 + M * (a + b - 3) ** 2
        model = H.compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        decoded = model.decode_sampleset(sampleset)
        best = min(decoded, key=lambda x: x.energy)
        self.assertTrue(best.subh["a"] == 1)
        self.assertTrue(best.subh["b"] == 2)
        self.assertTrue(a.value_range == (0, 3))
        self.assertTrue(b.value_range == (0, 3))

        expected_q = {('a[0]', 'a[1]'): 12.0,
             ('a[0]', 'a[2]'): 12.0,
             ('a[0]', 'b[0]'): 0.0,
             ('a[0]', 'b[1]'): 0.0,
             ('a[0]', 'b[2]'): 0.0,
             ('a[1]', 'a[2]'): 12.0,
             ('a[1]', 'b[0]'): 0.0,
             ('a[1]', 'b[1]'): 0.0,
             ('a[1]', 'b[2]'): 0.0,
             ('a[2]', 'b[0]'): 0.0,
             ('a[2]', 'b[1]'): 0.0,
             ('a[2]', 'b[2]'): 0.0,
             ('b[0]', 'b[1]'): 6.0,
             ('b[0]', 'b[2]'): 6.0,
             ('b[1]', 'b[2]'): 6.0,
             ('a[0]', 'a[0]'): -10.0,
             ('a[1]', 'a[1]'): -10.0,
             ('a[2]', 'a[2]'): -10.0,
             ('b[0]', 'b[0]'): -7.0,
             ('b[1]', 'b[1]'): -7.0,
             ('b[2]', 'b[2]'): -7.0}
        assert_qubo_equal(q, expected_q)

if __name__ == '__main__':
    unittest.main()
