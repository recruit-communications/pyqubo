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

from .array import Array
from .core import Constraint
from .constrained_integer import ConstrainedInteger


class OrderEncInteger(ConstrainedInteger):
    """
    Order encoding integer.
    """

    def __init__(self, label, lower_value, upper_value):
        assert upper_value > lower_value, "upper value should be larger than lower value"
        self.lower_value = lower_value
        self.upper_value = upper_value
        self._num_bits = (upper_value - lower_value)
        self.bits = Array.create(label, shape=self._num_bits, vartype='BINARY')
        self.label = label

        self._constraint = 0.0
        for i in range(self._num_bits - 1):
            a = self.bits[i]
            b = self.bits[i+1]
            label = self.label + "_order_" + str(i)
            self._constraint += Constraint(b-a*b, label)

        self._value = lower_value + sum(self.bits)

    @property
    def constraint(self):
        return self._constraint

    @property
    def value(self):
        return self._value

    @property
    def num_bits(self):
        return self._num_bits

    @property
    def interval(self):
        return self.lower_value, self.upper_value

    def __repr__(self):
        string = "OrderEncInteger(label={label}, interval=({lower_value}, {upper_value}))"\
            .format(label=self.label, lower_value=self.lower_value, upper_value=self.upper_value)
        return string
