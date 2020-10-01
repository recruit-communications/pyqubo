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
from pyqubo.integer import IntegerWithPenalty
from cpp_pyqubo import Placeholder, Constraint, SubH


class OrderEncInteger(IntegerWithPenalty):
    """
    Order encoded integer. This encoding is useful when you want to know
    whether the integer is more than k or not.
    The value that takes :math:`[0, n]` is represented by :math:`\sum_{i=1}^{n}x_{i}`.
    Also we have the penalty function :math:`strength \\times \\left(\sum_{i=1}^{n-1}\
    \\left(x_{i+1}-x_{i}x_{i+1}\\right)\\right)` in the Hamiltonian.
    See the reference [TaTK09]_ for more details.
    
    Args:
        label (str): Label of the integer.
        
        lower (int): Lower value of the integer.
        
        upper (int): Upper value of the integer.
        
        strength (float/Placeholder): Strength of the constraint.
    
    Examples:
        Create an order encoded integer `a` that takes [0, 3] with the strength = 5.0.
        Solution of `a` represents 2 which is the optimal solution of the Hamiltonian.
        
        >>> from pyqubo import OrderEncInteger
        >>> a = OrderEncInteger("a", (0, 3), strength = 5.0)
        >>> model = ((a-2)**2).compile()
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

        self._num_variables = (upper - lower)
        self.array = Array.create(label, shape=self._num_variables, vartype='BINARY')

        self.constraint = 0.0
        for i in range(self._num_variables - 1):
            a = self.array[i]
            b = self.array[i + 1]
            const_label = label + "_order_" + str(i)
            self.constraint += Constraint(b-a*b, const_label, condition=lambda x: x==0)

        express = SubH(lower + sum(self.array), label=label)
        penalty = self.constraint * strength

        super().__init__(
            label=label,
            value_range=value_range,
            express=express,
            penalty=penalty)


    def more_than(self, k):
        """Binary variable that represents whether the value is more than `k`.
        
        Note:
            You cannot use this method alone. You should use this variable with the entire integer.
            See an example below.

        Args:
            k (int): Integer value.
        
        Returns:
             :class:`Express`
        
        Examples:
            This example finds the value of integer `a` and `b` such that
            :math:`a=b` and :math:`a>1` and :math:`b<3`.
            The obtained solution is :math:`a=b=2`.
            
            >>> from pyqubo import OrderEncInteger
            >>> a = OrderEncInteger("a", (0, 4), strength = 5.0)
            >>> b = OrderEncInteger("b", (0, 4), strength = 5.0)
            >>> model = ((a-b)**2 + (1-a.more_than(1))**2 + (1-b.less_than(3))**2).compile()
            >>> bqm = model.to_bqm()
            >>> import dimod
            >>> sampleset = dimod.ExactSolver().sample(bqm)
            >>> decoded_samples = model.decode_sampleset(sampleset)
            >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
            >>> print(best_sample.subh['a'])
            2.0
            >>> print(best_sample.subh['b'])
            2.0
        """
        assert isinstance(k, int), "k should be integer"
        lower, upper = self.value_range
        assert k > lower, "This value is always equal to or more than {}".format(k)
        assert k <= upper, "This value is never more than {}".format(k)
        return self.array[k-lower]

    def less_than(self, k):
        """Binary variable that represents whether the value is less than `k`.

        Note:
            You cannot use this method alone. You should use this variable with the entire integer.
            See an example below.

        Args:
            k (int): Integer value.

        Returns:
             :class:`Express`

        Examples:
            This example finds the value of integer `a` and `b` such that
            :math:`a=b` and :math:`a>1` and :math:`b<3`.
            The obtained solution is :math:`a=b=2`.
            
            >>> from pyqubo import OrderEncInteger
            >>> a = OrderEncInteger("a", (0, 4), strength = 5.0)
            >>> b = OrderEncInteger("b", (0, 4), strength = 5.0)
            >>> model = ((a-b)**2 + (1-a.more_than(1))**2 + (1-b.less_than(3))**2).compile()
            >>> bqm = model.to_bqm()
            >>> import dimod
            >>> sampleset = dimod.ExactSolver().sample(bqm)
            >>> decoded_samples = model.decode_sampleset(sampleset)
            >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
            >>> print(best_sample.subh['a'])
            2.0
            >>> print(best_sample.subh['b'])
            2.0
        """
        assert isinstance(k, int), "k should be integer"
        lower, upper = self.value_range
        assert k >= lower, "This value is always more than {}".format(k)
        assert k < upper, "This value is always more than {}".format(k)
        return 1-self.array[k-lower-1]
