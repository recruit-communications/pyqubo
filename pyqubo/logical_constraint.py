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

from cpp_pyqubo import SubH, UserDefinedExpress, Binary


class NotConst(SubH):
    """Constraint: Not(a) = b.

    Args:
        a (:class:`Express`): expression to be binary
        
        b (:class:`Express`): expression to be binary
        
        label (str): label to identify the constraint
    
    Examples:
        In this example, when the binary variables satisfy the constraint,
        the energy is 0.0. On the other hand, when they break the constraint,
        the energy is 1.0 > 0.0.
        
        >>> from pyqubo import NotConst, Binary
        >>> a, b = Binary('a'), Binary('b')
        >>> exp = NotConst(a, b, 'not')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0}, vartype='BINARY')
        0.0
        >>> model.energy({'a': 1, 'b': 1}, vartype='BINARY')
        1.0
    """

    def __init__(self, a, b, label):
        express = 2 * a * b - a - b + 1
        super().__init__(express, label)



class AndConst(SubH):
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
        
        >>> from pyqubo import AndConst, Binary
        >>> a, b, c = Binary('a'), Binary('b'), Binary('c')
        >>> exp = AndConst(a, b, c, 'and')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 0}, vartype='BINARY')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 1}, vartype='BINARY')
        1.0
    """

    def __init__(self, a, b, c, label):
        express = a * b - 2 * (a + b) * c + 3 * c
        super().__init__(express, label)
    

class OrConst(SubH):
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
        
        >>> from pyqubo import OrConst, Binary
        >>> a, b, c = Binary('a'), Binary('b'), Binary('c')
        >>> exp = OrConst(a, b, c, 'or')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 1}, vartype='BINARY')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 0}, vartype='BINARY')
        1.0
    """

    def __init__(self, a, b, c, label):
        express = a * b + (a + b) * (1 - 2 * c) + c
        super().__init__(express, label)
    

class XorConst(SubH):
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
        
        >>> from pyqubo import XorConst, Binary
        >>> a, b, c = Binary('a'), Binary('b'), Binary('c')
        >>> exp = XorConst(a, b, c, 'xor')
        >>> model = exp.compile()
        >>> model.energy({'a': 1, 'b': 0, 'c': 1, 'aux_xor': 0}, vartype='BINARY')
        0.0
        >>> model.energy({'a': 0, 'b': 1, 'c': 0, 'aux_xor': 0}, vartype='BINARY')
        1.0
    """

    def __init__(self, a, b, c, label):
        aux = Binary("aux_" + label)
        express = 2 * a * b - 2 * (a + b) * c - 4 * (a + b) * aux +\
                                4 * aux * c + a + b + c + 4 * aux

        super().__init__(express, label)
