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
from pyqubo import Coefficient, ParamProd


class TestCoefficient(unittest.TestCase):

    def test_coefficient_exception(self):
        coeff = Coefficient({ParamProd({'a': 1, 'b': 1}): 2.0, ParamProd({}): 2.0})
        self.assertRaises(ValueError, lambda: coeff.eval({}))
        self.assertRaises(ValueError, lambda: coeff.eval({'a': 1.0}))
