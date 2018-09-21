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

from .core import UserDefinedExpress


class Not(UserDefinedExpress):
    """Logical NOT of input.

    Args:
        bit (:class:`Express`): expression to be binary
    
    Examples:
        >>> from pyqubo import Qbit, Not
        >>> a = Qbit('a')
        >>> exp = Not(a)
        >>> model = exp.compile()
        >>> for a in (0, 1):
        ...   print(a, int(model.energy({'a': a}, var_type='binary')))
        0 1
        1 0
    """

    def __init__(self, bit):
        express = 1 - bit
        super(Not, self).__init__(express)


class And(UserDefinedExpress):
    """Logical AND of inputs.

    Args:
        bit_a (:class:`Express`): expression to be binary
        
        bit_b (:class:`Express`): expression to be binary
    
    Examples:
        >>> from pyqubo import Qbit, And
        >>> import itertools
        >>> a, b = Qbit('a'), Qbit('b')
        >>> exp = And(a, b)
        >>> model = exp.compile()
        >>> for a, b in itertools.product(*[(0, 1)] * 2):
        ...   print(a, b, int(model.energy({'a': a, 'b': b}, var_type='binary')))
        0 0 0
        0 1 0
        1 0 0
        1 1 1
    """

    def __init__(self, bit_a, bit_b):
        express = bit_a * bit_b
        super(And, self).__init__(express)


class Or(UserDefinedExpress):
    """Logical OR of inputs.

    Args:
        bit_a (:class:`Express`): expression to be binary
        bit_b (:class:`Express`): expression to be binary
    
    Examples:
        
        >>> from pyqubo import Qbit, Or
        >>> import itertools
        >>> a, b = Qbit('a'), Qbit('b')
        >>> exp = Or(a, b)
        >>> model = exp.compile()
        >>> for a, b in itertools.product(*[(0, 1)] * 2):
        ...   print(a, b, int(model.energy({'a': a, 'b': b}, var_type='binary')))
        0 0 0
        0 1 1
        1 0 1
        1 1 1
    """

    def __init__(self, bit_a, bit_b):
        express = Not(And(Not(bit_a), Not(bit_b)))
        super(Or, self).__init__(express)
