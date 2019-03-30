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
from pyqubo import OrderEncInteger, OneHotEncInteger, UnaryEncInteger, LogEncInteger, Placeholder
import dimod
from pyqubo import assert_qubo_equal


class TestInteger(unittest.TestCase):

    def test_order_enc_integer(self):
        a = OrderEncInteger("a", 0, 4, strength=Placeholder("s"))
        model = ((a - 3) ** 2).compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        expected_q = {('a[0]', 'a[1]'): -18.0,
                    ('a[0]', 'a[2]'): 2.0,
                    ('a[0]', 'a[3]'): 2.0,
                    ('a[1]', 'a[2]'): -18.0,
                    ('a[1]', 'a[3]'): 2.0,
                    ('a[2]', 'a[3]'): -18.0,
                    ('a[0]', 'a[0]'): -5.0,
                    ('a[1]', 'a[1]'): 15.0,
                    ('a[2]', 'a[2]'): 15.0,
                    ('a[3]', 'a[3]'): 15.0}
        response = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(
            response, topk=1, feed_dict={"s": 10.0})[0]
        self.assertTrue(response["a"][0] == 1)
        self.assertTrue(response["a"][1] == 1)
        self.assertTrue(response["a"][2] == 1)
        self.assertTrue(response["a"][3] == 0)
        self.assertTrue(a.interval == (0, 4))
        assert_qubo_equal(q, expected_q)

    def test_order_enc_integer_more_than(self):
        a = OrderEncInteger("a", 0, 4, strength=5.0)
        b = OrderEncInteger("b", 0, 4, strength=5.0)
        model = ((a - b) ** 2 + (1 - a.more_than(1)) ** 2 + (1 - b.less_than(3)) ** 2).compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(sampleset, topk=1)[0]
        self.assertTrue(response["a"][0] == 1)
        self.assertTrue(response["a"][1] == 1)
        self.assertTrue(response["a"][2] == 0)
        self.assertTrue(response["a"][3] == 0)
        self.assertTrue(response["b"][0] == 1)
        self.assertTrue(response["b"][1] == 1)
        self.assertTrue(response["b"][2] == 0)
        self.assertTrue(response["b"][3] == 0)

    def test_one_hot_enc_integer(self):
        a = OneHotEncInteger("a", 0, 4, strength=Placeholder("s"))
        H = (a - 3) ** 2
        model = H.compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        sampleset = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(
            sampleset, topk=1, feed_dict={"s": 10.0})[0]
        self.assertTrue(response["a"][0] == 0)
        self.assertTrue(response["a"][1] == 0)
        self.assertTrue(response["a"][2] == 0)
        self.assertTrue(response["a"][3] == 1)
        self.assertTrue(response["a"][4] == 0)
        self.assertTrue(a.interval == (0, 4))

        expected_q = {('a[0]', 'a[1]'): 40.0,
             ('a[0]', 'a[2]'): 40.0,
             ('a[0]', 'a[3]'): 40.0,
             ('a[0]', 'a[4]'): 40.0,
             ('a[1]', 'a[2]'): 44.0,
             ('a[1]', 'a[3]'): 46.0,
             ('a[1]', 'a[4]'): 48.0,
             ('a[2]', 'a[3]'): 52.0,
             ('a[2]', 'a[4]'): 56.0,
             ('a[3]', 'a[4]'): 64.0,
             ('a[0]', 'a[0]'): -20.0,
             ('a[1]', 'a[1]'): -25.0,
             ('a[2]', 'a[2]'): -28.0,
             ('a[3]', 'a[3]'): -29.0,
             ('a[4]', 'a[4]'): -28.0}
        assert_qubo_equal(q, expected_q)

    def test_one_hot_enc_integer_equal(self):
        a = OneHotEncInteger("a", 0, 4, strength=Placeholder("s"))
        b = OneHotEncInteger("b", 0, 4, strength=Placeholder("s"))
        M = 2.0
        H = (a + b - 5) ** 2 + M*(a.equal_to(3)-1)**2
        model = H.compile()
        q, offset = model.to_qubo(feed_dict={"s": 10.0})
        sampleset = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(
            sampleset, topk=1, feed_dict={"s": 10.0})[0]
        self.assertTrue(response["a"][0] == 0)
        self.assertTrue(response["a"][1] == 0)
        self.assertTrue(response["a"][2] == 0)
        self.assertTrue(response["a"][3] == 1)
        self.assertTrue(response["a"][4] == 0)

    def test_unary_enc_integer(self):
        a = UnaryEncInteger("a", 0, 3)
        b = UnaryEncInteger("b", 0, 3)
        M = 2.0
        H = (2 * a - b - 1) ** 2 + M * (a + b - 3) ** 2
        model = H.compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(sampleset, topk=1)[0]
        self.assertTrue(sum(response["a"].values()) == 1)
        self.assertTrue(sum(response["b"].values()) == 2)
        self.assertTrue(a.interval == (0, 3))
        self.assertTrue(b.interval == (0, 3))

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

    def test_log_enc_integer(self):
        a = LogEncInteger("a", 0, 4)
        b = LogEncInteger("b", 0, 4)
        M = 2.0
        H = (2 * a - b - 1) ** 2 + M * (a + b - 5) ** 2
        model = H.compile()
        q, offset = model.to_qubo()
        sampleset = dimod.ExactSolver().sample_qubo(q)
        response, broken, e = model.decode_dimod_response(sampleset, topk=1)[0]
        sol_a = sum(2 ** k * v for k, v in response["a"].items())
        sol_b = sum(2 ** k * v for k, v in response["b"].items())
        self.assertTrue(sol_a == 2)
        self.assertTrue(sol_b == 3)
        self.assertTrue(a.interval == (0, 4))
        self.assertTrue(b.interval == (0, 4))

        expected_q = {('a[0]', 'a[1]'): 24.0,
             ('a[0]', 'a[2]'): 48.0,
             ('a[0]', 'b[0]'): 0.0,
             ('a[0]', 'b[1]'): 0.0,
             ('a[0]', 'b[2]'): 0.0,
             ('a[1]', 'a[2]'): 96.0,
             ('a[1]', 'b[0]'): 0.0,
             ('a[1]', 'b[1]'): 0.0,
             ('a[1]', 'b[2]'): 0.0,
             ('a[2]', 'b[0]'): 0.0,
             ('a[2]', 'b[1]'): 0.0,
             ('a[2]', 'b[2]'): 0.0,
             ('b[0]', 'b[1]'): 12.0,
             ('b[0]', 'b[2]'): 24.0,
             ('b[1]', 'b[2]'): 48.0,
             ('a[0]', 'a[0]'): -18.0,
             ('a[1]', 'a[1]'): -24.0,
             ('a[2]', 'a[2]'): 0.0,
             ('b[0]', 'b[0]'): -15.0,
             ('b[1]', 'b[1]'): -24.0,
             ('b[2]', 'b[2]'): -24.0}
        assert_qubo_equal(q, expected_q)
