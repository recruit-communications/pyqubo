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

from pyqubo import Binary, Placeholder, Array, SubH, Constraint
from pyqubo import assert_qubo_equal
import numpy as np
import dimod

class TestModel(unittest.TestCase):

    def test_to_qubo(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo()
        assert_qubo_equal(qubo, {("a", "a"): 1.0, ("a", "b"): 1.0, ("b", "b"): 0.0})
        self.assertTrue(offset == -1)
    
    def test_to_qubo_with_index(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        qubo, offset = model.to_qubo(index_label=True)
        assert_qubo_equal(qubo, {(0, 0): 1.0, (0, 1): 1.0, (1, 1): 0.0})
        self.assertTrue(offset == -1)

    def test_to_ising(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising()
        self.assertTrue(linear == {'a': 0.75, 'b': 0.25})
        assert_qubo_equal(quad, {('a', 'b'): 0.25})
        self.assertTrue(offset == -0.25)

    def test_to_ising_with_index(self):
        a, b = Binary("a"), Binary("b")
        exp = 1 + a * b + a - 2
        model = exp.compile()
        linear, quad, offset = model.to_ising(index_label=True)
        self.assertTrue(linear == {0: 0.75, 1: 0.25})
        assert_qubo_equal(quad, {(0, 1): 0.25})
        self.assertTrue(offset == -0.25)
    
    def test_decode_sample(self):
        x = Array.create("x", (2, 2), vartype="BINARY")
        exp = SubH((x[1, 1] + x[0, 1] + x[0, 0] - 1) ** 2, label="const")
        model = exp.compile()

        # type of solution is dict[label, int]

        ## vartype = BINARY
        sample = {'x[0][1]': 1, 'x[1][1]': 1, 'x[0][0]': 0}
        decoded_sample = model.decode_sample(sample, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 0)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 1)

        sample = {'x[0][1]': 1, 'x[1][1]': 0, 'x[0][0]': 0}
        decoded_sample = model.decode_sample(sample, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 0)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 0)

        ## vartype = SPIN
        sample = {'x[0][1]': 1, 'x[1][1]': 1, 'x[0][0]': -1}
        decoded_sample = model.decode_sample(sample, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 1)

        sample = {'x[0][1]': 1, 'x[1][1]': -1, 'x[0][0]': -1}
        decoded_sample = model.decode_sample(sample, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == -1)

        # type of solution is list[int]

        ## vartype = BINARY
        sample = {'x[0][1]': 1, 'x[1][1]': 0, 'x[0][0]': 1}
        list_sample = [sample[v] for v in model.variables]
        decoded_sample = model.decode_sample(list_sample, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 0)

        sample = {'x[0][1]': 1, 'x[1][1]': 0, 'x[0][0]': 0}
        list_sample = [sample[v] for v in model.variables]
        decoded_sample = model.decode_sample(list_sample, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 0)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 0)

        ## vartype = SPIN
        sample = {'x[0][1]': 1, 'x[1][1]': 1, 'x[0][0]': -1}
        list_sample = [sample[v] for v in model.variables]
        decoded_sample = model.decode_sample(list_sample, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 1)

        sample = {'x[0][1]': 1, 'x[1][1]': -1, 'x[0][0]': -1}
        list_sample = [sample[v] for v in model.variables]
        decoded_sample = model.decode_sample(list_sample, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == -1)

        # type of solution is dict[index_label(int), bit]
        ## vartype = BINARY
        sample = {'x[0][1]': 1, 'x[1][1]': 0, 'x[0][0]': 1}
        sample_index = {i: sample[v] for i, v in enumerate(model.variables)}
        decoded_sample = model.decode_sample(sample_index, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 0)

        sample = {'x[0][1]': 1, 'x[1][1]': 0, 'x[0][0]': 0}
        sample_index = {v: sample[v] for v in model.variables}
        decoded_sample = model.decode_sample(sample_index, vartype="BINARY")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == 0)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 0)

        ## vartype = SPIN
        sample = {'x[0][1]': 1, 'x[1][1]': 1, 'x[0][0]': -1}
        sample_index = {v: sample[v] for v in model.variables}
        decoded_sample = model.decode_sample(sample_index, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 1)
        self.assertTrue(decoded_sample.energy == 1)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == 1)

        sample = {'x[0][1]': 1, 'x[1][1]': -1, 'x[0][0]': -1}
        sample_index = {v: sample[v] for v in model.variables}
        decoded_sample = model.decode_sample(sample_index, vartype="SPIN")
        self.assertTrue(decoded_sample.sample == sample)
        self.assertTrue(len([label for label, energy in decoded_sample.subh.items() if energy > 0]) == 0)
        self.assertTrue(decoded_sample.energy == 0)
        self.assertTrue(decoded_sample.array("x", (0, 0)) == -1)
        self.assertTrue(decoded_sample.array("x", (0, 1)) == 1)
        self.assertTrue(decoded_sample.array("x", (1, 1)) == -1)

        # invalid solution
        self.assertRaises(ValueError, lambda: model.decode_sample([1, 1, 1, 1], vartype="BINARY"))
        qubo = model.to_qubo()
        self.assertRaises(ValueError, lambda: model.decode_sample(
            {'x[0][2]': 1, 'x[1][1]': 0, 'x[0][0]': 1}, vartype="BINARY"))
        self.assertRaises(TypeError, lambda: model.decode_sample((1, 1), vartype="BINARY"))
    
    def test_work_with_dimod(self):
        S = Array.create('S', 3, "SPIN")
        H = 0.8 * S[0] * S[1] + S[1] * S[2] + 1.1 * S[2] * S[0] + 0.5 * S[0]
        model = H.compile()

        # with index_label=False
        binary_bqm = model.to_bqm(index_label=False)
        sampler = dimod.ExactSolver()
        sampleset = sampler.sample(binary_bqm)
        decoded_samples = model.decode_sampleset(sampleset)
        best_sample = min(decoded_samples, key=lambda s: s.energy)
        self.assertTrue(best_sample.array("S", 0) == 0)
        self.assertTrue(best_sample.array("S", 1) == 0)
        self.assertTrue(best_sample.array("S", 2) == 1)
        self.assertTrue(np.isclose(best_sample.energy, -1.8))

        # with index_label=True
        binary_bqm = model.to_bqm(index_label=True)
        sampler = dimod.ExactSolver()
        sampleset = sampler.sample(binary_bqm)
        decoded_samples = model.decode_sampleset(sampleset)
        best_sample = min(decoded_samples, key=lambda s: s.energy)
        self.assertTrue(best_sample.array("S", 0) == 0)
        self.assertTrue(best_sample.array("S", 1) == 0)
        self.assertTrue(best_sample.array("S", 2) == 1)
        self.assertTrue(np.isclose(best_sample.energy, -1.8))


    def test_placeholders(self):

        S = Array.create('S', 3, "SPIN")
        p1, p2 = Placeholder("p1"), Placeholder("p2")
        H = p1 * S[0] * S[1] + S[1] * S[2] + p2 * S[2] * S[0] + 0.5 * S[0]
        model = H.compile()
        feed_dict = {"p1": 0.8, "p2": 1.1}
        binary_bqm = model.to_bqm(feed_dict=feed_dict)
        sampler = dimod.ExactSolver()
        sampleset = sampler.sample(binary_bqm)
        decoded_samples = model.decode_sampleset(sampleset, feed_dict=feed_dict)
        best_sample = min(decoded_samples, key=lambda s: s.energy)

        self.assertTrue(best_sample.array("S", 0) == 0)
        self.assertTrue(best_sample.array("S", 1) == 0)
        self.assertTrue(best_sample.array("S", 2) == 1)
        self.assertTrue(np.isclose(best_sample.energy, -1.8))
    
    def test_constraint(self):
        sampler = dimod.ExactSolver()
        x = Array.create('x',shape=(3),vartype="BINARY")
        H = Constraint(x[0]*x[1]*x[2],label="C1")
        model = H.compile()
        bqm = model.to_bqm()
        responses = sampler.sample(bqm)
        solutions = model.decode_sampleset(responses)
        
        for sol in solutions:
            if sol.energy==1.0:
                self.assertEqual(sol.subh['C1'], 1.0)
        
    def test_higher_order(self):
        x = Array.create('x', 5, 'BINARY')
        exp = x[0]*x[1]*x[2]*x[3]
        model = exp.compile(strength=10)

        sample = {'x[0]': 1, 'x[1]': 1, 'x[2]': 1, 'x[3]': 1, '0*1': 1, '2*3': 1}
        e = model.energy(sample, vartype='BINARY')
        self.assertEqual(e, 1.0)

        sample = {'x[0]': 0, 'x[1]': 1, 'x[2]': 1, 'x[3]': 1, '0*1': 0, '2*3': 1}
        e = model.energy(sample, vartype='BINARY')
        self.assertEqual(e, 0.0)
        
        sample = {'x[0]': 1, 'x[1]': 1, 'x[2]': 1, 'x[3]': 1, '0*1': 0, '2*3': 1}
        e = model.energy(sample, vartype='BINARY')
        self.assertEqual(e, 10.0)

if __name__ == '__main__':
    unittest.main()
