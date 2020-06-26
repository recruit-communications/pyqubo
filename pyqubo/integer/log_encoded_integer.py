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

from cpp_pyqubo import SubH
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
        >>> a = LogEncInteger("a", (0, 4))
        >>> b = LogEncInteger("b", (0, 4))
        >>> M=2.0
        >>> H = (2*a-b-1)**2 + M*(a+b-5)**2
        >>> model = H.compile()
        >>> bqm = model.to_bqm()
        >>> import dimod
        >>> sampleset = dimod.ExactSolver().sample(bqm)
        >>> decoded_samples = model.decode_sampleset(sampleset)
        >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
        >>> print(best_sample.subh['a'])
        2.0
        >>> print(best_sample.subh['b'])
        3.0
    """

    def __init__(self, label, value_range):
        lower, upper = value_range
        assert upper > lower, "upper value should be larger than lower value"
        assert isinstance(lower, int)
        assert isinstance(upper, int)

        span = upper - lower
        
        self._num_variables = int(np.log2(span)) + 1
        self.array = Array.create(label, shape=self._num_variables, vartype='BINARY')
        d = self._num_variables - 1
        express = lower + sum(self.array[i] * 2 ** i for i in range(self._num_variables - 1))
        express += (span - (2**d - 1)) * self.array[-1]
        express = SubH(express, label)
        
        super().__init__(
            label=label,
            value_range=value_range,
            express=express)
