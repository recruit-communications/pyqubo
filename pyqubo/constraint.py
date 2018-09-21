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

from .core import Constraint, UserDefinedExpress, Qbit


class NotConst(UserDefinedExpress):
    """Constraint: Not(a) = b.

    Args:
        a (:class:`Express`): expression to be binary
        
        b (:class:`Express`): expression to be binary
        
        label (str): label to identify the constraint
    
    Examples:
        In this example, when the binary variables satisfy the constraint,
        the energy is 0.0. On the other hand, when they break the constraint,
        the energy is 1.0 > 0.0.
        
        >>> from pyqubo import NotConst, Qbit
        >>> a, b = Qbit('a'), Qbit('b')
        >>> exp = NotConst(a, b, 'not')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0}, var_type='binary')
        0.0
        >>> model.energy({'a': 1, 'b': 1}, var_type='binary')
        1.0
    """

    def __init__(self, a, b, label):
        express = Constraint(2 * a * b - a - b + 1, label=label)
        super(NotConst, self).__init__(express)


class AndConst(UserDefinedExpress):
    """Constraint: AND(a, b) = c.

    Args:
        a (:class:`Express`): expression to be binary
        
        b (:class:`Express`): expression to be binary
        
        c (:class:`Express`): expression to be binary
        
        label (str): label to identify the constraint
    
    Examples:
        In this example, when the binary variables satisfy the constraint,
        the energy is 0.0. On the other hand, when they break the constraint,
        the energy is 1.0 > 0.0.
        
        >>> from pyqubo import AndConst, Qbit
        >>> a, b, c = Qbit('a'), Qbit('b'), Qbit('c')
        >>> exp = AndConst(a, b, c, 'and')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 0}, var_type='binary')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 1}, var_type='binary')
        1.0
    """

    def __init__(self, a, b, c, label):
        express = Constraint(a * b - 2 * (a + b) * c + 3 * c, label=label)
        super(AndConst, self).__init__(express)


class OrConst(UserDefinedExpress):
    """Constraint: OR(a, b) = c.

    Args:
        a (:class:`Express`): expression to be binary
        
        b (:class:`Express`): expression to be binary
        
        c (:class:`Express`): expression to be binary
        
        label (str): label to identify the constraint
    
    Examples:
        In this example, when the binary variables satisfy the constraint,
        the energy is 0.0. On the other hand, when they break the constraint,
        the energy is 1.0 > 0.0.
        
        >>> from pyqubo import OrConst, Qbit
        >>> a, b, c = Qbit('a'), Qbit('b'), Qbit('c')
        >>> exp = OrConst(a, b, c, 'or')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 1}, var_type='binary')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 0}, var_type='binary')
        1.0
    """

    def __init__(self, a, b, c, label):
        express = Constraint(a * b + (a + b) * (1 - 2 * c) + c, label=label)
        super(OrConst, self).__init__(express)


class XorConst(UserDefinedExpress):
    """Constraint: OR(a, b) = c.

    Args:
        a (:class:`Express`): expression to be binary
        
        b (:class:`Express`): expression to be binary
        
        c (:class:`Express`): expression to be binary
        
        label (str): label to identify the constraint
    
    Examples:
        In this example, when the binary variables satisfy the constraint,
        the energy is 0.0. On the other hand, when they break the constraint,
        the energy is 1.0 > 0.0.
        
        >>> from pyqubo import XorConst, Qbit
        >>> a, b, c = Qbit('a'), Qbit('b'), Qbit('c')
        >>> exp = XorConst(a, b, c, 'xor')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 1, 'aux_xor': 0}, var_type='binary')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 0, 'aux_xor': 0}, var_type='binary')
        1.0
    """

    def __init__(self, a, b, c, label):
        aux = Qbit("aux_"+label)
        express = Constraint(2 * a * b - 2 * (a + b) * c - 4 * (a + b) * aux + 4 * aux * c + a + b + c + 4 * aux, label=label)
        super(XorConst, self).__init__(express)
