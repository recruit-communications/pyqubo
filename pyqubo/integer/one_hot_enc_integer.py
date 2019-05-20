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
from pyqubo.core import Constraint
from pyqubo.integer import Integer
from pyqubo.core.express import WithPenalty, Placeholder


class OneHotEncInteger(WithPenalty, Integer):
    """One-hot encoded integer. The value that takes :math:`[0, n]` is represented by :math:`\sum_{i=1}^{n}ix_{i}`.
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
        >>> a = OneHotEncInteger("a", 1, 3, strength=5)
        >>> H = (a-2)**2
        >>> model = H.compile()
        >>> q, offset = model.to_qubo()
        >>> sampleset = dimod.ExactSolver().sample_qubo(q)
        >>> solution, broken, e  = model.decode_dimod_response(sampleset, topk=1)[0]
        >>> print("a={}".format(1+sum(k*v for k, v in solution["a"].items())))
        a=2
    """

    def __init__(self, label, lower, upper, strength):
        assert upper > lower, "upper value should be larger than lower value"
        assert isinstance(lower, int)
        assert isinstance(upper, int)
        assert isinstance(strength, int) or isinstance(strength, float) or\
            isinstance(strength, Placeholder)

        self.lower = lower
        self.upper = upper
        self._num_variables = (upper - lower + 1)
        self.array = Array.create(label, shape=self._num_variables, vartype='BINARY')
        self.label = label

        self.constraint = Constraint((sum(self.array)-1)**2, label=self.label+"_const")

        self._express = lower + sum(i*x for i, x in enumerate(self.array))
        self._penalty = self.constraint * strength

    @property
    def express(self):
        return self._express

    @property
    def penalty(self):
        return self._penalty

    @property
    def interval(self):
        return self.lower, self.upper

    def equal_to(self, k):
        """Variable representing whether the value is equal to `k`.
        
        Note:
            You cannot use this method alone. You should use this variable with the entire integer.
    
        Args:
            k (int): Integer value. 
        
        Returns:
            :class:`Express`
        """
        assert isinstance(k, int), "k should be integer"
        assert self.lower <= k <= self.upper, "This value never takes {}".format(k)
        return self.array[k-self.lower]

