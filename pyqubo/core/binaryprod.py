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

from operator import mul, xor
from six.moves import reduce


class BinaryProd(object):
    """A product of binary variables.
    This class is used as a key of dictionary when you represent a polynomial as a dictionary.
    
    For example, a polynomial :math:`2ab + b + 2` is represented as
    
    .. code-block:: python
        
        {BinaryProd({'a', 'b'}): 2.0, BinaryProd({'b'}): 1.0, BinaryProd(set()): 2.0}
    
    This class represents product of binary variables.
    Since :math:`a=a^2=a^3=...` where :math:`a` is binary, a product of binary variables
    can be represented by a set of unique variables.
    For example, :math:`aabbc` can be simplified as :math:`abc`.
    For this reason, this class contains unique binary variables as a set.
    
    Note:
        BinaryProd initialized with empty key corresponds to constant.
    
    Args:
        keys (set[label]): set of variable labels.
    """

    JOINT_SYMBOL = "*"
    CONST_STRING = "const"

    def __init__(self, keys):
        assert isinstance(keys, set)
        self.keys = keys
        if keys:
            self.cached_hash = reduce(xor, [hash(key) for key in self.keys])
            self.string = self.JOINT_SYMBOL.join(sorted(self.keys))

        # When :obj:`keys` is empty set, this object represents constant.
        else:
            self.cached_hash = 0
            self.string = self.CONST_STRING

    def __hash__(self):
        return self.cached_hash

    def __eq__(self, other):
        if not isinstance(other, BinaryProd):
            return False
        else:
            return self.keys == other.keys

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.string

    def is_constant(self):
        """Returns whether this is constant or not.
        
        Returns:
            bool
        """
        if self.string == self.CONST_STRING:
            return True
        else:
            return False

    def calc_product(self, dict_values):
        """Returns the value of the product of binary variables.
        
        Args:
            dict_values (dict[label, float]): value of binary variable. 
        
        Returns:
            float
        """
        if self.is_constant():
            return 1.0
        else:
            return reduce(mul, [dict_values[key] for key in self.keys])

    @staticmethod
    def merge_term_key(term_key1, term_key2):
        return BinaryProd(term_key1.keys | term_key2.keys)
