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

from pyqubo import solve_qubo, solve_ising, Spin


class TestSolver(unittest.TestCase):

    @staticmethod
    def create_number_partition_model():
        s1, s2, s3 = Spin("s1"), Spin("s2"), Spin("s3")
        H = (2 * s1 + 4 * s2 + 6 * s3) ** 2
        return H.compile()

    def test_solve_qubo(self):
        model = TestSolver.create_number_partition_model()
        qubo, offset = model.to_qubo()
        solution = solve_qubo(qubo, num_reads=1, sweeps=10)
        self.assertTrue(solution == {'s1': 0, 's2': 0, 's3': 1} or {'s1': 1, 's2': 1, 's3': 0})

    def test_solve_ising(self):
        model = TestSolver.create_number_partition_model()
        linear, quad, offset = model.to_ising()
        solution = solve_ising(linear, quad, num_reads=1, sweeps=10)
        self.assertTrue(solution == {'s1': -1, 's2': -1, 's3': 1} or {'s1': 1, 's2': 1, 's3': -1})

if __name__ == '__main__':
    unittest.main()
