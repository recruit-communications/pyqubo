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

from pyqubo import Array, SubH, Constraint
from pyqubo.integer.integer import IntegerWithPenalty
from pyqubo import WithPenalty, Placeholder


class OneHotEncInteger(IntegerWithPenalty):
    """One-hot encoded integer. The value that takes :math:`[1, n]` is represented by :math:`\sum_{i=1}^{n}ix_{i}`.
    Also we have the penalty function :math:`strength \\times (\sum_{i=1}^{n}x_{i}-1)^2` in the Hamiltonian.
    
    Args:
        label (str): Label of the integer.
        
        lower (int): Lower value of the integer.
        
        upper (int): Upper value of the integer.
        
        strength (float/Placeholder): Strength of the constraint.
    
    Examples:
        This example is equivalent to the following Hamiltonian.
        
        .. math::
        
            H = \\left(\\left(\sum_{i=1}^{3}ia_{i}+1\\right) - 2\\right)^2 + strength \\times \\left(\sum_{i=1}^{3}a_{i}-1\\right)^2
        
        >>> from pyqubo import OneHotEncInteger
        >>> a = OneHotEncInteger("a", (1, 3), strength=5)
        >>> H = (a-2)**2
        >>> model = H.compile()
        >>> bqm = model.to_bqm()
        >>> import dimod
        >>> sampleset = dimod.ExactSolver().sample(bqm)
        >>> decoded_samples = model.decode_sampleset(sampleset)
        >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
        >>> print(best_sample.subh['a'])
        2.0
    """

    def __init__(self, label, value_range, strength):
        lower, upper = value_range
        assert upper > lower, "upper value should be larger than lower value"
        assert isinstance(lower, int)
        assert isinstance(upper, int)
        assert isinstance(strength, int) or isinstance(strength, float) or\
            isinstance(strength, Placeholder)

        self._num_variables = (upper - lower + 1)
        self.array = Array.create(label, shape=self._num_variables, vartype='BINARY')
        self.constraint = Constraint((sum(self.array)-1)**2, label=label+"_const", condition=lambda x: x==0)

        express = SubH(lower + sum(i*x for i, x in enumerate(self.array)), label=label)
        penalty = self.constraint * strength

        super().__init__(
            label=label,
            value_range=value_range,
            express=express,
            penalty=penalty)

    def equal_to(self, k):
        """Variable representing whether the value is equal to `k`.
        
        Note:
            You cannot use this method alone. You should use this variable with the entire integer.
    
        Args:
            k (int): Integer value. 
        
        Returns:
            :class:`Express`
        """
        lower, upper = self.value_range
        assert isinstance(k, int), "k should be integer"
        assert lower <= k <= upper, "This value never takes {}".format(k)
        return self.array[k-lower]

