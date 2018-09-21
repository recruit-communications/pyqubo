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
import copy


class ParamProd(object):
    """A product of parameter variables.
    This class is used as a key of dictionary when you represent a polynomial as a dictionary.

    For example, a polynomial :math:`2a^2 b + 2` is represented as
    
    .. code-block:: python
        
        {ParamProd({'a': 2, 'b': 1}): 2.0, ParamProd({}): 2.0}

    Note:
        ParamProd initialized with empty key corresponds to constant.

    Args:
        keys (dict[label, int]):
            dictionary with a key being label, a int value being order of power.
    """

    JOINT_SYMBOL = "*"
    CONST_STRING = "const"

    def __init__(self, keys):
        assert isinstance(keys, dict)
        self.keys = keys
        if keys:
            self.cached_hash = reduce(xor, [hash(k) ^ hash(v) for k, v in self.keys.items()])
            self.is_const = False

        # When :obj:`keys` is empty dict, this object represents constant.
        else:
            self.cached_hash = 0
            self.is_const = True

    def __hash__(self):
        return self.cached_hash

    def __eq__(self, other):
        if not isinstance(other, ParamProd):
            return False
        else:
            return self.keys == other.keys

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.is_constant():
            return self.CONST_STRING
        else:
            return self.JOINT_SYMBOL.join(sorted(["{}^{}".format(k, v)
                                                  for k, v in self.keys.items()]))

    def is_constant(self):
        """Returns whether this is constant or not.

        Returns:
            bool
        """
        return self.is_const

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
            return reduce(mul, [dict_values[k] ** v for k, v in self.keys.items()])

    @staticmethod
    def merge_term_key(term_key1, term_key2):
        term_key1_copy = copy.copy(term_key1.keys)
        for k, v in term_key2.keys.items():
            if k in term_key1_copy:
                term_key1_copy[k] += v
            else:
                term_key1_copy[k] = v
        return ParamProd(term_key1_copy)
