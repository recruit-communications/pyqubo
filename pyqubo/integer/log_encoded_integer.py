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

from pyqubo.array import Array
from pyqubo.integer import Integer
import numpy as np


class LogEncInteger(Integer):
    """Log encoded integer. The value that takes :math:`[0, n]` is
    represented by :math:`\\sum_{i=1}^{\\lceil\\log_{2}n\\rceil}2^ix_{i}` without any constraint.

    Args:
        label (str): Label of the integer.

        lower (int): Lower value of the integer.

        upper (int): Upper value of the integer.

    Examples:
        This example finds the value `a`, `b` such that :math:`a+b=5` and :math:`2a-b=1`.
        
        >>> from pyqubo import LogEncInteger
        >>> import dimod
        >>> a = LogEncInteger("a", 0, 4)
        >>> b = LogEncInteger("b", 0, 4)
        >>> M=2.0
        >>> H = (2*a-b-1)**2 + M*(a+b-5)**2
        >>> model = H.compile()
        >>> q, offset = model.to_qubo()
        >>> sampleset = dimod.ExactSolver().sample_qubo(q)
        >>> response, broken, e  = model.decode_dimod_response(sampleset, topk=1)[0]
        >>> sol_a = sum(2**k * v for k, v in response["a"].items())
        >>> sol_b = sum(2**k * v for k, v in response["b"].items())
        >>> print("a={},b={}".format(sol_a, sol_b))
        a=2,b=3
    """

    def __init__(self, label, lower, upper):
        assert upper > lower, "upper value should be larger than lower value"
        assert isinstance(lower, int)
        assert isinstance(upper, int)

        self.lower = lower
        self.upper = upper
        self._num_variables = int(np.log2(upper - lower))+1
        self.array = Array.create(label, shape=self._num_variables, vartype='BINARY')
        self.label = label
        self._express = lower + sum(x*2**i for i, x in enumerate(self.array))

    @property
    def express(self):
        return self._express

    @property
    def interval(self):
        return self.lower, self.upper